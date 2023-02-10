import json
import pandas as pd


def precess_location(file_path, save_path):
    """
    处理wifiAP的位置信息
    """

    locations = json.load(open(file_path))

    loc_tag = {}
    for loc in locations.values():
        loc_tag.update(loc)

    loc_tag = pd.DataFrame(pd.Series(loc_tag, name="WIFIAPTag")).reset_index()
    loc_tag.columns = ["WIFIAPTag", "loc"]

    loc_tag.to_csv(save_path)
