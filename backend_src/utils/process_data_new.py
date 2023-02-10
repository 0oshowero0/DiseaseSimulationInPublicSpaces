from pathlib import Path
import numpy as np
from numpy.ma.core import left_shift
from numpy.random import default_rng
import sys 
import matplotlib.pyplot as plt
from PIL import ImageFilter
from PIL import Image
import json
import pickle
import pandas as pd
from datetime import datetime
from shapely.geometry import Polygon,Point  
from tqdm import tqdm
#from skimage.transform import resize
#--project_root_dir
#       |-- src
#       |      |-- simulator.py
#       |      |-- social_force.py
#       |      |-- gcn_lstm_deconv.py
#       |      |-- GAN.py
#       |      |-- risk_sim.py
#       |      |-- utils
#       |      
#       |-- data
#               |-- maps
#               |-- labels 
#               |-- population_dist
#               |-- aux_data


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
    end1y = rng.uniform(822-78,822-65,size=int(number/2))
    end2x = rng.uniform(728,866,size=int(number/2))
    end2y = rng.uniform(822-80,822-60,size=int(number/2))

    endx = np.concatenate((end1x,end2x),axis=0)
    endy = np.concatenate((end1y,end2y),axis=0)

    state = []
    for i in range(number):
        state.append([locx[i],locy[i],vx[i],vy[i],endx[i],endy[i]])
    return np.array(state)



def file_path(dir='../data'):
    data_path = {}
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
    return data_path




def load_airport_lines(data_path):
    with open(data_path['map_outlines'], 'r') as f:
         lines_dict = json.load(f)
    # lines_dict中，两个数字分别为y坐标与x坐标。
    # 这个模型是普通直角坐标系，因此需要转换一下坐标原点。图尺寸为(822, 902),令坐标原点为左下角。

    # list of linear obstacles given in the form of (x_min, x_max, y_min, y_max)
    airport_obstacles = []
    for _,line in lines_dict.items():
        airport_obstacles.append([line['first'][1],line['second'][1],822-line['first'][0],822-line['second'][0]])

    return airport_obstacles



def init_by_day(data_path,date='2016/9/12'):
    """
    根据某天各个旅客进入机场的时间以及对应的登机口位置，构建用于模拟的时间表。
    return: csv文件，包含 checkin_time BGATE_ID  init_x  init_y  final_x  final_y
    """
    # 读取各个旅客进入机场的时刻，并为每个旅客匹配航班号的登机口信息以及登机口位置
    departure = pd.read_csv(data_path['departure_data'])
    flight = pd.read_csv(data_path['flight_data'])
    #departure = pd.read_csv(r"C:\Users\dell\Desktop\PySocialForce-master\data\original_datas\airport_gz_departure_chusai_2ndround.csv")
    #flight = pd.read_csv(r"C:\Users\dell\Desktop\PySocialForce-master\data\original_datas\airport_gz_flights_chusai_2ndround.csv")

    # 筛选对应日期的记录
    departure_select = departure[departure['checkin_time'].str.contains(date)].sort_values(by=['checkin_time'], ascending=True)
    flight_select = flight[flight['scheduled_flt_time'].str.contains(date)].sort_values(by=['scheduled_flt_time'], ascending=True)

    # 合并表格
    ckin_with_BGATE = departure_select.merge(flight_select,left_on = ['flight_ID'],right_on = ['flight_ID'],how='inner').drop(['passenger_ID2','flight_ID','flight_time','scheduled_flt_time','actual_flt_time'],axis = 1)
    # 将日期时间变成时间差分
    ckin_with_BGATE['checkin_time'] = ckin_with_BGATE['checkin_time'].apply(lambda x: (datetime.strptime(x, "%Y/%m/%d %H:%M:%S")-datetime.strptime(date+' 00:00:00', "%Y/%m/%d %H:%M:%S")).total_seconds())
    # 至此，生成了一个进入模拟器的时间(秒数)-登机口映射表

    #######################################################################################################################
    # 初始化个体起始位置 位于T1航站楼中下部
    rng = default_rng()
    locx = rng.uniform(417,528,size=ckin_with_BGATE.shape[0])  # 即图像的宽方向，依然是左上角为原点
    locy = rng.uniform(434,462,size=ckin_with_BGATE.shape[0])  # 即图像的高方向，依然是左上角为原点
    tmp = {'init_x':locx.astype(int),'init_y':locy.astype(int)}
    init_loc = pd.DataFrame(tmp)

    ckin_with_BGATE_init_loc = ckin_with_BGATE.join(init_loc)   # 两个表格简单横向拼接

    #######################################################################################################################
    # 初始化个体目标位置 根据登机口
    # 读取登机口标记位置
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

    ckin_with_BGATE_init_loc = ckin_with_BGATE_init_loc.merge(label_BGATE,left_on=['BGATE_ID'],right_on = ['BGATE'],how='inner').drop(['down_left','down_right','top_left','top_right','BGATE'],axis=1)
    locx_all= []
    locy_all = []

    bgates = ckin_with_BGATE_init_loc['BGATE_ID'].drop_duplicates()
    for gate in bgates:
        # 根据登机口位置，为每个人在登机口区域内随机初始化一个终点
        tmp = label_BGATE[label_BGATE['BGATE']==gate]
        down_left = tmp['down_left'].iloc[0]
        down_right= tmp['down_right'].iloc[0]
        top_left = tmp['top_left'].iloc[0]
        top_right = tmp['top_right'].iloc[0]

        y_max = np.max((down_left[0],down_right[0],top_left[0],top_right[0]))   # 即图像的高方向，依然是左上角为原点
        y_min = np.min((down_left[0],down_right[0],top_left[0],top_right[0]))   

        x_max = np.max((down_left[1],down_right[1],top_left[1],top_right[1]))   # 即图像的宽方向，依然是左上角为原点
        x_min = np.min((down_left[1],down_right[1],top_left[1],top_right[1]))

        point_in_polygon = False
        point_in_airport = False
        poly = Polygon([down_left,down_right,top_left,top_right])
        while not (point_in_polygon and point_in_airport):
            locx = int(rng.uniform(x_min,x_max,size=1))  # 即图像的宽方向，依然是左上角为原点
            locy = int(rng.uniform(y_min,y_max,size=1))  # 即图像的高方向，依然是左上角为原点
            point = Point([locy,locx])
            point_in_polygon = poly.contains(point)
            point_in_airport = airport.contains(point)
        
        locx_all.append(locx)
        locy_all.append(locy)

    tmp = {'BGATE_ID':bgates,'final_x':locx_all, 'final_y':locy_all}
    final_loc = pd.DataFrame(tmp)

    ckin_with_BGATE_init_loc_fin_loc = ckin_with_BGATE_init_loc.merge(final_loc,left_on=['BGATE_ID'],right_on = ['BGATE_ID'],how='inner')

    # for gate in ckin_with_BGATE_init_loc['BGATE_ID']:
    #     # 根据登机口位置，为每个人在登机口区域内随机初始化一个终点
    #     tmp = label_BGATE[label_BGATE['BGATE']==gate]
    #     down_left = tmp['down_left'].iloc[0]
    #     down_right= tmp['down_right'].iloc[0]
    #     top_left = tmp['top_left'].iloc[0]
    #     top_right = tmp['top_right'].iloc[0]

    #     y_max = np.max((down_left[0],down_right[0],top_left[0],top_right[0]))   # 即图像的高方向，依然是左上角为原点
    #     y_min = np.min((down_left[0],down_right[0],top_left[0],top_right[0]))   

    #     x_max = np.max((down_left[1],down_right[1],top_left[1],top_right[1]))   # 即图像的宽方向，依然是左上角为原点
    #     x_min = np.min((down_left[1],down_right[1],top_left[1],top_right[1]))

    #     point_in_polygon = False
    #     point_in_airport = False
    #     poly = Polygon([down_left,down_right,top_left,top_right])
    #     while not (point_in_polygon and point_in_airport):
    #         locx = int(rng.uniform(x_min,x_max,size=1))  # 即图像的宽方向，依然是左上角为原点
    #         locy = int(rng.uniform(y_min,y_max,size=1))  # 即图像的高方向，依然是左上角为原点
    #         point = Point([locy,locx])
    #         point_in_polygon = poly.contains(point)
    #         point_in_airport = airport.contains(point)
        
    #     locx_all.append(locx)
    #     locy_all.append(locy)
    
    # tmp = {'final_x':locx_all, 'final_y':locy_all}
    # final_loc = pd.DataFrame(tmp)

    # ckin_with_BGATE_init_loc_fin_loc = ckin_with_BGATE_init_loc.join(final_loc)   # 两个表格简单横向拼接

    return ckin_with_BGATE_init_loc_fin_loc

def gen_GAN_base_map():
    data_path = file_path()
    image = np.load(data_path['map_npy'])
    image_resized = resize(image, (image.shape[0] // 9, image.shape[1] // 9),anti_aliasing=True)
    for i in range(image_resized.shape[0]):
        for j in range(image_resized.shape[1]):
            if image_resized[i,j]!=0:
                image_resized[i,j]=1
    airport_map=image_resized 
    x = []
    y = []
    for i in range(airport_map.shape[0]):
        for j in range(airport_map.shape[1]):
            x.append(i)
            y.append(j)
    data = {'x':x,'y':y}
    results = pd.DataFrame(data)
    results.to_csv('./data/GAN/base_map',sep='\t',index=False, header=False)

def process_socialForce_traces_for_GAN(social_force_traces_loc='state0-24.json'):
    data_path = file_path()
    airport_map = np.load(data_path['map_npy'])
    x_max = airport_map.shape[0]
    y_max = airport_map.shape[1]

    with open(social_force_traces_loc,'r') as f:
        social_force = json.load(f)
    
    # # 先插值 再查找
    # max_len = 0
    # for k,v in tqdm(social_force.items()):
    #     indiv = eval(v)
    #     a = indiv['trajectory']
    #     if len(a) > max_len:
    #         max_len = len(a)
    # print(max_len)
    # max_len = 32940
    trace={}
    for k,v in tqdm(social_force.items()):
        trace[k]={}
        v1=eval(v)
        trace[k]['trajectory']=[]
        for i in range(len(v1['trajectory'])):
            u=[]
            a1=np.around(v1['trajectory'][i][0]*822/(902*9))
            a2=np.around(v1['trajectory'][i][1]*822/(902*9))
            u.append(a1)
            u.append(a2)
            trace[k]['trajectory'].append(u)
        trace[k]=str(trace[k])
    social_force=trace
    tmp = []
    for k,v in tqdm(social_force.items()):
        indiv = eval(v)
        a = indiv['trajectory']
        tmp.append(len(a))
    tmp = np.array(tmp)
    print(tmp.mean())
    print(tmp.std())
    max_len = int(tmp.mean() + tmp.std() * 3)
    with open('../data/GAN-trace','w') as f:
        all_points = []
        for k,v in tqdm(social_force.items()):
            indiv = eval(v)
            traj = np.array(indiv['trajectory'])
            origin_x = np.linspace(0, traj.shape[0], num=traj.shape[0],endpoint=False)
            resample_x = np.linspace(0, max_len, num=max_len,endpoint=False)
            traj_x = np.around(np.interp(resample_x,origin_x,traj[:,0])).astype(int)
            traj_y = np.around(np.interp(resample_x,origin_x,traj[:,1])).astype(int)
            points = traj_x * x_max + traj_y
            tmp = points.astype(str).tolist()
            str_to_write = " ".join(tmp)
            f.write(str_to_write+'\n')