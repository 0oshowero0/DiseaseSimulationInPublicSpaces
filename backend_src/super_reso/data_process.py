import numpy as np
import pandas as pd
import math
import json


def build_map(data, dominate_map_path, AP_location_path):
    """
    data: DataFrame
    """
    location = pd.read_csv(
        AP_location_path,
        index_col=0,
        converters={"loc": eval},
    )

    dominate = json.load(open(dominate_map_path, "r"))

    # build map
    data.sort_values("Time")

    result = []

    data_time = data.groupby("Time")
    for _, data_slice in data_time:
        tmp = pd.merge(data_slice, location, on="WIFIAPTag")
        wifi_data = dict(
            zip(tmp["WIFIAPTag"].to_list(), tmp["PassengerCountMean"].to_list())
        )
        map_ = np.zeros([902, 822])
        for wifi in wifi_data.keys():
            count = wifi_data[wifi]
            range_ = dominate[wifi]
            num = len(range_)
            value = count / num
            for point in range_:
                map_[point[0], point[1]] = value

        result.append(map_)

    result = np.array(result)

    return result


def cal_dominate(airport_map_path, AP_location_path):
    a_map = np.load(airport_map_path).transpose(1, 0)

    x = np.arange(902)
    y = np.arange(822)
    points = np.array(np.meshgrid(x, y)).T.reshape(-1, 2).tolist()

    points_in_apt = []
    for point in points:
        if not a_map[point[0], point[1]]:
            points_in_apt.append(point)

    location = pd.read_csv(
        AP_location_path,
        index_col=0,
        converters={"loc": eval},
    )
    wifi_map = dict(zip(location["WIFIAPTag"].to_list(), location["loc"].to_list()))

    dominate = wifi_map.copy()
    for k in dominate.keys():
        dominate[k] = [dominate[k]]

    for point in points_in_apt:
        tag = ""
        min_dist = 9999
        for wifi, loc in wifi_map.items():
            dist = math.hypot(point[0] - loc[0], point[1] - loc[1])
            if dist < min_dist:
                min_dist = dist
                tag = wifi

        dominate[tag].append(point)


# if __name__ == "__main__":
#     data = pd.read_csv(
#         "../../airport_simulator/data/WIFITAPTag_Mean_All.csv",
#         converters={"PassengerCountMean": eval},
#     )
#     data = data[
#         (data["Time"] >= "2016-09-13 00:00:00")
#         & (data["Time"] <= "2016-09-13 23:59:59")
#     ]
#     result = build_map(
#         data,
#         "../../airport_simulator/data/dominate_map.json",
#         "../../airport_simulator/data/WIFITag_location.csv",
#     )
