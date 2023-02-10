import json, pickle, importlib, math, random
from pathlib import Path
import numpy as np
from numpy.ma.core import left_shift
import matplotlib.pyplot as plt
from PIL import ImageFilter
from PIL import Image
import pandas as pd
from datetime import datetime
from shapely.geometry import Polygon,Point
from tqdm import tqdm


vertival_size = 822

def GPU_max_free_memory():
    import pynvml  
    pynvml.nvmlInit()
    free_list = []
    for iter in range(pynvml.nvmlDeviceGetCount()):
        handle = pynvml.nvmlDeviceGetHandleByIndex(iter)
        meminfo = pynvml.nvmlDeviceGetMemoryInfo(handle)
        free_list.append(meminfo.free)
    return np.argmax(free_list)


def vertical_flip(df):
    df2 = df.copy(deep=True)
    for i in tqdm(range(df2.shape[0])): 
        df2['init_coordinate'][i][1] = vertival_size - df2['init_coordinate'][i][1]
        temp = np.array(df2['waypoint'][i])
        temp[:, 1] = vertival_size - temp[:, 1]
        df2['waypoint'][i] = temp.tolist()
    return df2

def region_filter(lines, region):
    return list(filter(lambda x:(x[0] > region[0]) and (x[1] < region[1]) and (x[2] < region[2]) and (x[3] > region[3]), lines))


def load_checkin_lines(data_path, vertical_flip=False):
    import functools
    with open(data_path['label_checkin'], 'r') as f:
        checkin = json.load(f)
        checkin = {key1:[checkin[key1][key2] for key2 in ['down_left', 'down_right', 'top_right', 'top_left']] for key1 in checkin if key1 != 'CK010'}

        for key, value in checkin.items():
            value.append(value[0])
            if vertical_flip:
                checkin[key] = [[value[iter][1], value[iter+1][1], vertival_size-value[iter][0], vertival_size-value[iter+1][0]] for iter in range(4)]
            else:
                checkin[key] = [[value[iter][1], value[iter+1][1], value[iter][0], value[iter+1][0]] for iter in range(4)]
        checkin = list(functools.reduce((lambda a, b: a + b), checkin.values()))
    return checkin


def load_airport_lines(data_path, more_security_ck, vertical_flip=False):
    with open(data_path['map_outlines'], 'r') as f:
        lines_dict = json.load(f)
    if more_security_ck:
        security = [
            [330, 330, 370, 383], [330, 330, 387, 388], [330, 330, 392, 393], [330, 330, 397, 410], 
            [570, 570, 370, 383], [570, 570, 387, 388], [570, 570, 392, 393], [570, 570, 397, 410], 
        ]
    else:
        security = [
            [330, 330, 370, 388], [330, 330, 392, 410], 
            [570, 570, 370, 388], [570, 570, 392, 410]]
    if vertical_flip:
        security = [[iter[0], iter[1], vertival_size-iter[2], vertival_size-iter[3]]for iter in security]
    airport_obstacles = security
    for _, line in lines_dict.items():
        if vertical_flip:
            airport_obstacles.append([line['first'][1], line['second'][1], vertival_size - line['first'][0], vertival_size - line['second'][0]])
        else:
            airport_obstacles.append([line['first'][1], line['second'][1], line['first'][0], line['second'][0]])
    return airport_obstacles

def process_map(file_path = './airport_map.npy'):
    airport_map = np.load(file_path)

    airport_map_pl = Image.fromarray(airport_map*255)
    airport_map_pl.save('airport_map_255.png','PNG')   #保存0，255可直接观测的图片
    airport_map_pl = Image.fromarray(airport_map)
    airport_map_pl.save('airport_map.png','PNG')       #保存0，1图片
    edge_filter= ImageFilter.Kernel((3,3),[0,-1,0,-1,4,-1,0,-1,0],scale=1)   #手动设计一个边缘提取滤波器
    airport_map_pl_edge = airport_map_pl.filter(edge_filter)
    airport_map_edge = np.array(airport_map_pl_edge)
    airport_map_edge = np.where(airport_map_edge>=1,1,0).astype('uint8')
    airport_map_pl_edge = Image.fromarray(airport_map_edge)
    airport_map_pl_edge.save('airport_map_edge.png','PNG')   #保存0，1边缘图片


def pre_process_json(file_path = './airport_map_255.json'):
    with open(file_path,'r') as f:
        preprocess_json = json.load(f)

    last_end = 0
    new_lines = {}
    i=0
    for line in preprocess_json["shapes"]:   # 遍历是有序的，可以不用看label
        if line["label"] == "1":
            tmp = np.array(line["points"]).astype(int)   # labelme标记的直线，第一个数字是x，第二个数字是y；是从左上角开始的；本函数只是将顺序倒过来了，并令前后点能够接上
            first = [int(tmp[0,1]),int(tmp[0,0])]    # json不能处理numpy数据，必须转换为python原生数据结构
            second = [int(tmp[1,1]),int(tmp[1,0])]
            last_end = second
            new_line = {"label":line["label"],"first":first,"second":second}
            new_lines[line["label"]]= new_line
            i+=1
        else:
            tmp = np.array(line["points"]).astype(int)
            first = last_end
            second = [int(tmp[1,1]),int(tmp[1,0])]
            new_line = {"label":line["label"],"first":first,"second":second}
            new_lines[line["label"]]= new_line
            i+=1
            last_end = second
    
    with open('./airport_map_255_processed.pkl', 'wb') as f:
        pickle.dump(new_lines,f)

    with open('./airport_map_255_processed.json', 'w') as f:
        json.dump(new_lines,f,indent=4)


def gen_pop(number=100):
    rng = default_rng()

    #生成速度
    speed = rng.normal(loc=1.34,scale=0.37,size=number)
    vx = rng.uniform(-1,1,size=number)
    tmp = speed**2-vx**2
    tmp[tmp<0] = 0
    vy = np.sqrt(tmp)
    direction_y = np.where(rng.uniform(0,1,size=number)>0.5,1,-1)
    vy *= direction_y

    # 初始位置位于(360,822-338) (543,822-462)之间  （x,y）
    locx = rng.uniform(360,543,size=number)
    locy = rng.uniform(822-462,822-338,size=number)

    # 终点1位置位于(43,822-65) (172,822-78)之间  （x,y）
    # 终点2位置位于(728,822-60) (866,822-80)之间  （x,y）
    end1x = rng.uniform(43,172,size=int(number/2))
    end1y = rng.uniform(vertival_size - 78, vertival_size - 65, size=int(number/2))
    end2x = rng.uniform(728,866,size = int(number/2))
    end2y = rng.uniform(vertival_size - 80, vertival_size - 60, size=int(number/2))

    endx = np.concatenate((end1x,end2x),axis=0)
    endy = np.concatenate((end1y,end2y),axis=0)

    state = []
    for i in range(number):
        state.append([locx[i],locy[i],vx[i],vy[i],endx[i],endy[i]])
    return np.array(state)

def file_path(dir='../data'):
    data_path = {}
    '''
    data_path['departure_data'] = dir+'/original_datas/airport_gz_departure_chusai_2ndround.csv'
    data_path['flight_data'] = dir+'/original_datas/airport_gz_flights_chusai_2ndround.csv'
    data_path['security_ck_data'] = dir+'/original_datas/airport_gz_security_check_chusai_2ndround.csv'
    data_path['gates'] = dir+'/original_datas/airport_gz_gates.csv'
    data_path['distribution'] = '/data4/liyuze/airport_simulator/data/labels.npy'
    
    data_path['map_npy'] = dir+'/maps/airport_map.npy'
    data_path['map_outlines'] = dir+'/maps/airport_map_255_processed.json'

    data_path['label_checkin'] = dir+'/labels/checkin.json'
    data_path['label_departure'] = dir+'/labels/departure.json'
    data_path['label_rest'] = dir+'/labels/rest.json'
    data_path['label_seat'] = dir+'/labels/seat.json'
    data_path['label_security_ck'] = dir+'/labels/security_ck.json'
    data_path['label_shop'] = dir+'/labels/shop.json'
    data_path['label_region'] = dir+'/labels/regions.json'
    '''
    return data_path

import datetime
def str2timestamp(string):
    return int(datetime.datetime.strptime(string, "%Y/%m/%d %H:%M:%S").timestamp())

def init_by_day(data_path, start, end, seed=0):
    np.random.seed(seed)
    if type(start) == str:
        start = str2timestamp(start)
    if type(end) == str:
        end = str2timestamp(end)

    departure = pd.read_csv(data_path['departure_data'])
    flight = pd.read_csv(data_path['flight_data'])
    flight_BGATE_ID_dict = dict(zip(flight['flight_ID'], flight['BGATE_ID']))
    
    departure = departure[
        departure['checkin_time'].str.contains(' ') & \
        departure['flight_time'].str.contains(' ')]
    departure['checkin_time'] = departure['checkin_time'].apply(str2timestamp)
    departure['flight_time'] = departure['flight_time'].apply(str2timestamp)
    departure = departure[
        (departure['checkin_time'] >= start) & \
        (departure['checkin_time'] < end) & \
        (departure['checkin_time'] < departure['flight_time'])
    ]
    departure = pd.concat([
        departure, 
        pd.DataFrame({
            'interval_time' : (departure['flight_time'] - departure['checkin_time']), 
            'BGATE_ID':departure['flight_ID'].map(flight_BGATE_ID_dict)})
    ], axis=1, join='inner')

    df = departure.sort_values(by=['checkin_time'], ascending=True)
    #df = df[df['BGATE_ID'].apply(str) != 'nan']
    
    #init_x = np.random.uniform(417, 528, size=df.shape[0]).astype(int)
    #init_y = np.random.uniform(434, 462, size=df.shape[0]).astype(int)
    
    with open(data_path['label_departure'],'r') as f:
    #with open(r"C:\Users\dell\Desktop\PySocialForce-master\data\labels\departure.json",'r') as f:
        departure_loc = json.load(f)
    # 整理为dataframe格式
    down_left = []
    down_right = []
    top_left = []
    top_right = []
    BGATE = []
    for k,v in departure_loc.items():
        BGATE.append(v['ID'])
        down_left.append(v['down_left'])
        down_right.append(v['down_right'])
        top_left.append(v['top_left'])
        top_right.append(v['top_right'])
    tmp = {'BGATE':BGATE, 'down_left':down_left, 'down_right':down_right, 'top_left':top_left,'top_right':top_right}
    label_BGATE = pd.DataFrame(tmp)
    
    # 读取整个机场区域
    with open(data_path['map_outlines'], 'r') as f:
         lines_dict = json.load(f)
    # lines_dict中，两个数字分别为y坐标与x坐标。
    airport_border = []
    for _,line in lines_dict.items():
        airport_border.append([line['first'][0],line['first'][1]])
    airport = Polygon(airport_border)

    df = df.merge(label_BGATE, left_on=['BGATE_ID'], right_on=['BGATE'],how='inner').\
        drop(['down_left','down_right','top_left','top_right','BGATE'],axis=1)
    locx_all= []
    locy_all = []

    bgates = df['BGATE_ID'].drop_duplicates()
    for gate in bgates:
        # 根据登机口位置，为每个人在登机口区域内随机初始化一个终点
        tmp = label_BGATE[label_BGATE['BGATE']==gate]
        down_left = tmp['down_left'].iloc[0]
        down_right= tmp['down_right'].iloc[0]
        top_left = tmp['top_left'].iloc[0]
        top_right = tmp['top_right'].iloc[0]

        y_max = np.max((down_left[0],down_right[0],top_left[0],top_right[0]))
        y_min = np.min((down_left[0],down_right[0],top_left[0],top_right[0]))   

        x_max = np.max((down_left[1],down_right[1],top_left[1],top_right[1]))
        x_min = np.min((down_left[1],down_right[1],top_left[1],top_right[1]))

        point_in_polygon = False
        point_in_airport = False
        poly = Polygon([down_left,down_right,top_left,top_right])
        while not (point_in_polygon and point_in_airport):
            locx = int(np.random.uniform(x_min,x_max,size=1))  # 即图像的宽方向，依然是左上角为原点
            locy = int(np.random.uniform(y_min,y_max,size=1))  # 即图像的高方向，依然是左上角为原点
            point = Point([locy,locx])
            point_in_polygon = poly.contains(point)
            point_in_airport = airport.contains(point)
        
        locx_all.append(locx)
        locy_all.append(locy)

    tmp = {'BGATE_ID':bgates,'final_x':locx_all, 'final_y':locy_all}
    final_loc = pd.DataFrame(tmp)

    df = df.merge(final_loc, left_on=['BGATE_ID'], right_on=['BGATE_ID'], how='inner')
    df['ID'] = [i for i in range(df.shape[0])]
    
    df['interval_time'] = df['interval_time'].astype(int)
    df['flight_time'] = df['flight_time'].astype(int)
    return df
    

def relay_policy(data_path, df, reduce_explore, more_security_ck, heatmap, start, end):
    from itertools import product
    np.random.seed(0)
    if type(start) == str:
        start = str2timestamp(start)
    if type(end) == str:
        end = str2timestamp(end)
    
    init_x = np.random.uniform(417, 528, size=df.shape[0]).astype(int)
    init_y = np.random.uniform(434, 462, size=df.shape[0]).astype(int)
    BGATE_ID = df['BGATE_ID']
    exp_lambda = 60
    time_scale = 60
    distribution_interval = 60 * 10
    distribution_start = np.floor(start // distribution_interval).astype(int)
    distribution = heatmap * (1 - np.load(data_path['map_npy']))[np.newaxis]
    distribution = distribution.transpose([0,2,1])
    distribution[distribution < 0] = 0
    
    from PIL import Image, ImageDraw
    def polygon2mask(p):
        temp = Image.new('1', (distribution.shape[2], distribution.shape[1]), 0)
        ImageDraw.Draw(temp).polygon([(iter[1], iter[0]) for iter in p], outline=1, fill=1)
        return np.array(temp)
    with open(data_path['label_region'], 'r') as f:
        regions = json.load(f)['shapes']
        mask_dict = {iter['label'] : polygon2mask(iter['points']) for iter in regions}
    
    region_dict = {}
    loc = list(product(range(distribution.shape[1]), range(distribution.shape[2])))
    for region in mask_dict:
        region_dict[region] = {}
        for t in np.arange(start // distribution_interval, end // distribution_interval).astype(int):
            region_dict[region][t] = (distribution[t - distribution_start] * mask_dict[region]).flatten() + 1e-8
            region_dict[region][t] /= np.sum(region_dict[region][t])
    
    relay = []
    def turbulent(r = 5):
        return np.clip(np.random.normal(0, r / 2), -r, r)
    def leftexit(more_security_ck=more_security_ck):
        if more_security_ck:
            coor1 = [[330, 385], [330, 390], [330, 395]][np.random.choice(3)]
        else:
            coor1 = [330, 390]
        waypoint = [
            [coor1[0] + turbulent(1), coor1[1] + turbulent(1), 1], 
            [262 + turbulent(20), 393 + turbulent(20), 1]]
        return waypoint
    def rightexit(more_security_ck=more_security_ck):
        if more_security_ck:
            coor1 = [[570, 385], [570, 390], [570, 395]][np.random.choice(3)]
        else:
            coor1 = [570, 390]
        waypoint = [
            [coor1[0] + turbulent(1), coor1[1] + turbulent(1), 1], 
            [641 + turbulent(20), 389 + turbulent(20), 1]]
        return waypoint
    
    def park(start, end, region):
        if reduce_explore:
            return []
        else:
            waypoint = []
            length = (end - start) / time_scale
            waypoint_length = 0
            for iter in range(2):
            #while length > waypoint_length:
                frame = int((start + waypoint_length) // distribution_interval)
                if frame in region:
                    loc_id = np.random.choice(len(loc), p=region[int((start + waypoint_length) // distribution_interval)])
                    t = np.random.exponential(exp_lambda)
                    x, y = loc[loc_id]
                    waypoint.append([x, y, t])
                    waypoint_length += t
                else:
                    break
            return waypoint
        
    LU = [[210, 69, 1], [180, 69, 1]]
    LM = [[230, 341, 1], [215, 345, 1]]
    LD = [[282, 607, 1], [272, 610, 1]]
    
    RU = [[692, 67, 1], [719, 67, 1]]
    RM = [[668, 342, 1], [685, 344, 1]]
    RD = [[614, 606, 1], [631, 610, 1]]

    with open(data_path['label_checkin'],'r') as f:
        checkin_loc = json.load(f)
        checkin_loc = {int(key[-1]):np.array(list(checkin_loc[key].values())[1:])[:, [1,0]] for key in checkin_loc}
    with open(data_path['label_departure'],'r') as f:
        departure_loc = json.load(f)
        departure_loc = {key:np.array(list(departure_loc[key].values())[1:])[:, [1,0]] for key in departure_loc}
    entrance1 = {key:[0,1] for key in 
        ['A{}'.format(id) for id in range(109, 113)] + 
        ['A{}'.format(id) for id in range(119, 124)] + 
        ['A{}'.format(id) for id in range(130, 134)] + 
        ['B{}'.format(id) for id in range(207, 214)] + 
        ['B{}'.format(id) for id in range(220, 224)] + 
        ['B{}'.format(id) for id in range(231, 236)]}
    entrance2 = {key:[2,3] for key in 
        ['A{}'.format(id) for id in range(101, 106)] + 
        ['A{}'.format(id) for id in range(113, 118)] + 
        ['A{}'.format(id) for id in range(124, 129)] + 
        ['B{}'.format(id) for id in range(201, 206)] + 
        ['B{}'.format(id) for id in range(214, 218)] + 
        ['B{}'.format(id) for id in range(224, 229)]}
    entrance3 = {key:[1, 3] for key in ['B230', 'B229', 'B219', 'B218', 'B206']}
    entrance4 = {key:[0, 2] for key in ['A129', 'A118', 'A108', 'A107', 'A106']}

    entrance = dict(list(entrance1.items()) + list(entrance2.items()) + list(entrance3.items()) + list(entrance4.items()))

    for key in entrance:
        entrance[key] = departure_loc[key][entrance[key]].mean(0)

    for i in tqdm(range(df.index.size)):
        temp_relay = [[init_x[i], init_y[i], 1]]
        temp_start, temp_end = df['checkin_time'][i], df['flight_time'][i]
        temp_t = temp_end - temp_start
        
        checkin_num = np.random.randint(1, 10)
        if checkin_num in range(5):
            temp_checkin = checkin_loc[checkin_num][:2].mean(0)
        else:
            temp_checkin = checkin_loc[checkin_num][2:].mean(0)
        temp_checkin[0] += np.random.randint(-5, 6)
        temp_relay.append([*temp_checkin, 5])
        
        if BGATE_ID[i] in ['B' + str(iter) for iter in range(224, 236)]:
            temp_relay += park(
                temp_start, temp_start + temp_t * 0.25, region_dict['Center'])
            temp_relay += leftexit()
            temp_relay += park(
                temp_start + temp_t * 0.25, temp_start + temp_t * 0.75, region_dict['LU_park'])
            temp_relay += LU
            temp_relay += park(
                temp_start + temp_t * 0.75, temp_start + temp_t * 1.25, region_dict['LU_Departure'])
        elif BGATE_ID[i] in ['B' + str(iter) for iter in range(214, 224)]:
            temp_relay += park(
                temp_start, temp_start + temp_t * 0.25, region_dict['Center'])
            temp_relay += leftexit()
            temp_relay += park(
                temp_start + temp_t * 0.25, temp_start + temp_t * 0.75, region_dict['LM_park'])
            temp_relay += LM
            temp_relay += park(
                temp_start + temp_t * 0.75, temp_start + temp_t * 1.25, region_dict['LM_Departure'])
        elif BGATE_ID[i] in ['B' + str(iter) for iter in range(201, 214)]:
            temp_relay += park(
                temp_start, temp_start + temp_t * 0.25, region_dict['Center'])
            temp_relay += leftexit()
            temp_relay += park(
                temp_start + temp_t * 0.25, temp_start + temp_t * 0.75, region_dict['LD_park'])
            temp_relay += LD
            temp_relay += park(
                temp_start + temp_t * 0.75, temp_start + temp_t * 1.25, region_dict['LD_Departure'])
        elif BGATE_ID[i] in ['A' + str(iter) for iter in range(124, 134)]:
            temp_relay += park(
                temp_start, temp_start + temp_t * 0.25, region_dict['Center'])
            temp_relay += rightexit()
            temp_relay += park(
                temp_start + temp_t * 0.25, temp_start + temp_t * 0.75, region_dict['RU_park'])
            temp_relay += RU
            temp_relay += park(
                temp_start + temp_t * 0.75, temp_start + temp_t * 1.25, region_dict['RU_Departure'])
        elif BGATE_ID[i] in ['A' + str(iter) for iter in range(113, 124)]:
            temp_relay += park(
                temp_start, temp_start + temp_t * 0.25, region_dict['Center'])
            temp_relay += rightexit()
            temp_relay += park(
                temp_start + temp_t * 0.25, temp_start + temp_t * 0.75, region_dict['RM_park'])
            temp_relay += RM
            temp_relay += park(
                temp_start + temp_t * 0.75, temp_start + temp_t * 1.25, region_dict['RM_Departure'])
        elif BGATE_ID[i] in ['A' + str(iter) for iter in range(101, 113)]:
            temp_relay += park(
                temp_start, temp_start + temp_t * 0.25, region_dict['Center'])
            temp_relay += rightexit()
            temp_relay += park(
                temp_start + temp_t * 0.25, temp_start + temp_t * 0.75, region_dict['RD_park'])
            temp_relay += RD
            temp_relay += park(
                temp_start + temp_t * 0.75, temp_start + temp_t * 1.25, region_dict['RD_Departure'])
        temp_relay.append([*entrance[BGATE_ID[i]], 1])
        temp_relay.append([*departure_loc[BGATE_ID[i]].mean(0), 1])
        relay.append(temp_relay)
    df = df.join(pd.DataFrame({'waypoint':relay, 'init_coordinate':[list(iter) for iter in zip(init_x, init_y)]}))
    return df


def states2DataFrame(states):
    time, x_loc, y_loc, x_speed, y_speed, infection_state, final_x, final_y, relay_x, relay_y = [], [], [], [], [], [], [], [], [], []
    for i, time_stemp in enumerate(states):
        time += [i for person in time_stemp]
        x_loc += [person[0] for person in time_stemp]
        y_loc += [person[1] for person in time_stemp]
        x_speed += [person[2] for person in time_stemp]
        y_speed += [person[3] for person in time_stemp]
        infection_state += [person[4] for person in time_stemp]
        relay_x += [[point[0] for point in person[5]] for person in time_stemp]
        relay_y += [[point[1] for point in person[5]] for person in time_stemp]
        final_x += [person[5][-1][0] for person in time_stemp]
        final_y += [person[5][-1][1] for person in time_stemp]

    data = {
        'time_stamp':time,
        'init_x':x_loc,'init_y':y_loc,
        'x_speed':x_speed,'y_speed':y_speed,
        'infection_state':infection_state,
        'relay_x':relay_x, 'relay_y':relay_y,
        'final_x':final_x, 'final_y':final_y, 
    }
    return pd.DataFrame(data)