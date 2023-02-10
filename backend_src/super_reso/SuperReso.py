import torch
import numpy as np
from tqdm import tqdm
from .model import DBPN2
from .dataset import MapDatasetPro
from .data_process import build_map
import toml
import pandas as pd


def GPU_max_free_memory():
    import pynvml
    pynvml.nvmlInit()
    free_list = []
    for iter in range(pynvml.nvmlDeviceGetCount()):
        handle = pynvml.nvmlDeviceGetHandleByIndex(iter)
        meminfo = pynvml.nvmlDeviceGetMemoryInfo(handle)
        free_list.append(meminfo.free)
    return np.argmax(free_list)


class SuperReso:
    def __init__(self):
        super(SuperReso, self).__init__()

    def init_model(self):
        conf = toml.load("super_reso/conf.toml")
        self.conf = conf
        cuda_num = GPU_max_free_memory()
        self.device = "cuda:" + str(cuda_num)

        config = {
            "input_channel": conf["model"]["input_channel"],
            "output_channel": conf["model"]["output_channel"],
            "upscale_factor": conf["model"]["upscale_factor"],
            "cuda_num": cuda_num,
            "base_filter": conf["model"]["base_filter"],
            "feat": conf["model"]["feat"],
            "kernel": conf["model"]["kernel"],
            "stride": conf["model"]["stride"],
            "padding": conf["model"]["padding"],
            "num_stages": conf["model"]["num_stages"],
        }

        self.model = DBPN2(config).to(self.device)

    def load_weight(self, path):
        self.model.load_state_dict(torch.load(path))

    def complete_data(self, data):
        result = []
        dataset = MapDatasetPro(
            data,
            [int(904 / 4), int(824 / 4)],
            (self.conf["model"]["input_max"], self.conf["model"]["gt_max"]),
        )
        for t in tqdm(dataset):
            r = self.model(t)
            result.append(r.squeeze().cpu().detach().numpy())

        return (np.array(result) * self.conf["model"]["gt_max"]).transpose(0, 2, 1)[
            :, :-2, :-2
        ]

    def preprecess_map(self, data, dominate_map_path, AP_location_path):
        return build_map(data, dominate_map_path, AP_location_path)


if __name__ == "__main__":
    sup = SuperReso()
    sup.init_model()
    sup.load_weight("../../airport_simulator/data/weight/epoch_500.pth")
    data = pd.read_csv(
        "../../airport_simulator/data/WIFITAPTag_Mean_All.csv",
        converters={"PassengerCountMean": eval},
    )
    data = data[
        (data["Time"] >= "2016-09-13 00:00:00")
        & (data["Time"] <= "2016-09-13 23:59:59")
    ]
    map = sup.preprecess_map(
        data,
        "../../airport_simulator/data/dominate_map.json",
        "../../airport_simulator/data/WIFITag_location.csv",
    )
    result = sup.complete_data(map)
    pass