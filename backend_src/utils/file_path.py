def file_path(dir="../data"):
    data_path = {}
    data_path["departure_data"] = "/aux_data/departure_info.csv"
    data_path["flight_data"] = "/aux_data/flights_info.csv"
    data_path["security_ck_data"] = "/aux_data/security_ck_info.csv"
    
    data_path["gates"] = "/aux_data/gates_info.csv"
    data_path["distribution"] = "/st_completion/labels.npy"

    data_path["map_npy"] = "/maps/airport_map.npy"
    data_path["map_outlines"] = "/maps/airport_map_255_processed.json"
    data_path["map_dominate"] = "/maps/dominate_map.json"
    data_path["map_ap_data"] = "/population_dist/WIFITAPTag_Mean_All.csv"
    
    data_path["map_ap_location"] = "/labels/WIFITag_location.csv"
    data_path["label_checkin"] = "/labels/checkin.json"
    data_path["label_departure"] = "/labels/departure.json"
    data_path["label_rest"] = "/labels/rest.json"
    data_path["label_seat"] = "/labels/seat.json"
    data_path["label_security_ck"] = "/labels/security_ck.json"
    data_path["label_shop"] = "/labels/shop.json"
    data_path["label_region"] = "/labels/regions.json"

    data_path["weight_super_reso"] = "/st_completion/weight_production.pth"
    
    for key in data_path:
        data_path[key] = dir + data_path[key]
    return data_path

def GPU_max_free_memory():
    import pynvml  
    pynvml.nvmlInit()
    free_list = []
    for iter in range(pynvml.nvmlDeviceGetCount()):
        handle = pynvml.nvmlDeviceGetHandleByIndex(iter)
        meminfo = pynvml.nvmlDeviceGetMemoryInfo(handle)
        free_list.append(meminfo.free)
    return np.argmax(free_list)