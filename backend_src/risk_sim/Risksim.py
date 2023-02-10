import numpy as np
import pandas as pd
#import jsonpath
import json 
from numpy.random import default_rng
import random
import math
from scipy import spatial
from scipy.spatial.distance import pdist, squareform
import os
from datetime import datetime, timedelta
import ast

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

class InfectMode:
    SUSCEPTIBLE = 0
    EXPOSED = 1
    INFECTED = 2

class Gender:
    MALE=0
    FEMALE=1

class AREA:
    NONE = 0
    CLEAN = 1
    POLLUTED = 2

class Risksim:
    '''
    def __init__(self,conf_path,trace):
        #初始化类内参数
        self.conf_path = conf_path
        self.conf = ConfigParser()
        self.conf.read(conf_path)

        # 读取example.conf，根据example.conf中的值进行初始化示例
        self.contact_radius = self.conf.get('RISKSIM settings','contact_radius')
        self.age_distrib = self.conf.get('RISKSIM settings','age_distrib')
        self.trace=trace
    '''
    #调试暂用参数设置
    def __init__(self, trace, initial, final):
        self.trace = trace #输入的pysocialforce生成个体轨迹
        self.initial = initial
        self.final = final
        data_path = file_path()
        #self.initial=1473638400 #模拟起始时间时间戳
        #self.final=1473639000 #模拟结束时间时间戳
        self.age_distrib=[0.05,0.05,0.1,0.2,0.2,0.3,0.1] #年龄分布[0~20岁，20~30岁，30~40岁，40~50岁，50~60岁，60~70岁，70~80岁]
        self.gender_distrib=[0.5,0.5] #性别分布[男，女]
        self.contact_radius=2 #气溶胶传播社交距离
        self.solid_possi=0.3 #衡量固体接触传播可能性大小，固体每被传染者接触一次，固体传染率增加solid_possi
        self.length=822 #室内场景图片大小为length*width
        self.width=902
        self.label_path=[data_path['label_seat'],data_path['label_shop'] ,data_path['label_rest']]#可能产生固体接触传播的区域标记json路径
        self.crowd_radius=4 #拥挤风险评估时周围人数统计半径

    def pretreat(self):
        #数据预处理与补全函数
        #根据性别、年龄比例随机分配信息，根据不同年龄组传染风险，补全传染率
        #返回N：trace中整个过程包含总人数 timeLen：trace中整个过程总时长(模拟时长可根据self.initial,self.final自行调整)
        #返回trail:N维非等长list 存储所有人个体轨迹(注意每个人个体轨迹包含坐标数量不同，由起始时间、结束时间决定)
        #返回individual_info:dataframe(存储passenger_ID2,velocity,start_time,end_time,infect_time,expose_time,age,gender,infect_rate)
        
        trail=[]
        ID=[]
        velocity=[]
        start_time=[]
        end_time=[]
        infect_time=[]
        for key,value in self.trace.items():
            tmp=ast.literal_eval(value)
            if max(tmp['state']['start_time'], self.initial) < min((tmp['state']['start_time']+len(tmp['trajectory'])), self.final):
                trail.append(tmp['trajectory'])
                ID.append(tmp['state']['passenger_ID2'])
                velocity.append(tmp['state']['max_speed'])
                start_time.append(tmp['state']['start_time'])

        initial_time=min(start_time)
        for i in range(len(trail)):
            start_time[i]=start_time[i]-initial_time #认为第一个人出发时刻为0时刻
            end_time.append(len(trail[i])+start_time[i]-1)

        N=len(trail)
        timeLen=max(end_time)-min(start_time)

        INF=timeLen+100
        for i in range(N):
            if 0.1 > random.random(): #进入机场旅客为无症状感染者的概率为0.1
                infect_time.append(start_time[i])
            else:
                infect_time.append(INF)
        expose_time=infect_time

        #从trace中提取个人信息暂存为individual_info_dict
        individual_info_dict={"ID":ID,"velocity":velocity,"start_time":start_time,"end_time":end_time,"infect_time":infect_time,"expose_time":expose_time}

        #根据年龄分布随机分配年龄,暂存为age_dict
        rng = default_rng()
        age0_20 = rng.uniform(0,20,size=int(self.age_distrib[0]*N))  
        age20_30= rng.uniform(20,30,size=int(self.age_distrib[1]*N))
        age30_40= rng.uniform(30,40,size=int(self.age_distrib[2]*N))
        age40_50= rng.uniform(40,50,size=int(self.age_distrib[3]*N))
        age50_60= rng.uniform(50,60,size=int(self.age_distrib[4]*N))
        age60_70= rng.uniform(60,70,size=int(self.age_distrib[5]*N))
        age70_80= rng.uniform(70,80,size=(N-len(age0_20)-len(age20_30)-len(age30_40)-len(age40_50)-len(age50_60)-len(age60_70)))
        
        age=np.concatenate((age0_20,age20_30,age30_40,age40_50,age50_60,age60_70,age70_80),axis=0).astype(int)
        age=np.random.permutation(age)
        age_dict={'age':age}

        #根据性别比例分配性别，暂存为gender_dict
        gender_M = [Gender.MALE for i in range(int(self.gender_distrib[0]*N))]
        gender_F = [Gender.FEMALE for i in range(N-len(gender_M))]
        gender=np.concatenate((gender_F,gender_M),axis=0).astype(int)
        gender_dict={'gender':gender}

        #根据年龄、性别设置个体感染率(服从同增长速率指数分布，男性为女性2倍)
        infection_rate=np.zeros(N,dtype=float)
        for i in range(len(age)):
            if (age[i]>=0) & (age[i]<20):
                if gender[i]==Gender.MALE:
                    infection_rate[i]=0.00036
                else:
                    infection_rate[i]=0.00018
            else:
                if gender[i]==Gender.MALE:
                    infection_rate[i]=math.pow(2750,(age[i]-20)/60)*0.00036
                else:
                    infection_rate[i]=math.pow(2750,(age[i]-20)/60)*0.00018
        infection_rate_dict={'infection_rate':infection_rate}

        #连接以上所有dict并转换为dataframe
        #individual_info包括：ID,velocity,start_time,end_time,infect_time,expose_time,age,gender,infect_rate)
        individual_info=pd.DataFrame.from_dict({**individual_info_dict,**age_dict,**gender_dict,**infection_rate_dict}) 

        return N,timeLen,trail,individual_info

    def point_inside_polygon(self,x,y,poly):
        #判断坐标点是否在给定顶点的多边形内
        #场景固体接触传播状态矩阵生成时调用

        n = len(poly)
        inside =False
        p1x,p1y = poly[0]
        for i in range(n+1):
            p2x,p2y = poly[i % n]
            if y > min(p1y,p2y):
                if y <= max(p1y,p2y):
                    if x <= max(p1x,p2x):
                        if p1y != p2y:
                            xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x,p1y = p2x,p2y
        return inside

    def get_area(self):
        #生成场景固体接触传播状态矩阵，该矩阵大小与场景二值化图片大小相同，用于记录各位置是否可能进行固体接触传播，是否已经被感染者“污染”
        #AREA类中NONE代表该位置不能进行固体接触传播，CLEAN代表该位置可以进行固体接触传播但尚且安全，POLLUTED代表该位置可以进行固体接触传播且已被“污染”

        area_state=np.zeros((self.length,self.width), dtype = np.int)

        for i in range(len(self.label_path)):
            with open(self.label_path[i],'r') as f:
                area=json.load(f)
            for key,value in area.items():
                poly=[value['down_left'],value['down_right'],value['top_right'],value['top_left']]
                x_list=[value['down_left'][0],value['down_right'][0],value['top_right'][0],value['top_left'][0]]
                y_list=[value['down_left'][1],value['down_right'][1],value['top_right'][1],value['top_left'][1]]
                x_min=min(x_list)
                x_max=max(x_list)
                y_min=min(y_list)
                y_max=max(y_list)
                for i in range(x_min,x_max+1):
                    for j in range(y_min,y_max+1):
                        if self.point_inside_polygon(i,j,poly):
                            area_state[i][j]=AREA.CLEAN
        
        return area_state

    def infection_sim(self):
        #感染风险控制（与评估）函数
        #根据预处理self.pretreat()得到的轨迹坐标、个人信息重新计算感染情况
        #实现控制：
        #1.改变传播范围contact_radius 对每个时刻计算机场现有人群间距离，在传播半径之内的感染者-非感染者传染
        #2.根据个体年龄设置不同感染率infection_rate
        #返回intervene_info：包含ID、infect_state（控制更新后）、trail的dataframe

        N,timeLen,trail,info=self.pretreat()
        area_state=self.get_area()

        for moment in range(0,self.final-self.initial):
            present = info[(info['start_time']<=moment)&(info['end_time']>=moment)].index.tolist() #确定已到场且未离开的所有人的index
            for i in present:
                it = moment-info.loc[i,'start_time']-1 #it为查找坐标indice，个体起始时刻并不一定是零时刻
                if trail[i][it][0] >= self.length or trail[i][it][1] >= self.width: #筛除错误越界轨迹
                    continue
                #如果i为感染者
                if info.loc[i,'infect_time'] <= moment:
                    #气溶胶传染情况：遍历在场所有人
                    for j in present: 
                        jt = moment-info.loc[j,'start_time']-1
                        if (i != j)&(info.loc[j,'infect_time'] > moment)&(((trail[i][it][0]-trail[j][jt][0])**2+(trail[i][it][1]-trail[j][jt][1])**2) <= self.contact_radius): #j非感染者且ij距离过近
                            if info.loc[j,'infection_rate'] > random.random():
                                info.loc[j,'infect_time'] = moment #j产生感染，感染时间变为当前时刻
                                if info.loc[j,'expose_time'] > timeLen: #如果j第一次接触感染者就发生感染
                                    info.loc[j,'expose_time'] = moment #暴露时刻与感染时刻相同
                            else:
                                info.loc[j,'expose_time']=moment #j接触但未感染，暴露时间为当前时刻
                    #固体传播情况：遍历所有标记区域
                    if area_state[int(trail[i][it][1])][int(trail[i][it][0])] != AREA.NONE: #如果所处位置可能进行固体接触传播，提升该位置固体传播风险等级
                        area_state[int(trail[i][it][1])-1:int(trail[i][it][1])+1][int(trail[i][it][0])-1:int(trail[i][it][0])+1] += 1 
                #如果i非感染者，还需查看是否处于感染区
                else:
                    if area_state[int(trail[i][it][1])][int(trail[i][it][0])] >=AREA.POLLUTED: #产生固体传播
                        if max(self.solid_possi*area_state[trail[i][it][1]][trail[i][it][0]],1) > random.random():
                            info.loc[i,'infect_time'] = moment #j产生感染，感染时间变为当前时刻
                            area_state[trail[i][it][1]][trail[i][it][0]]=AREA.POLLUTED
                            if info.loc[i,'expose_time'] > timeLen: #如果j第一次接触就发生感染
                                info.loc[i,'expose_time'] = moment #暴露时刻与感染时刻相同
        
        '''
        #统计总暴露人数、总感染人数、总健康人数
        infect_num=0
        expose_num=0
        susceptible_num=0
        for i in range(N):
            if info.loc[i,'infect_time']<=info.loc[i,'end_time']:
                infect_num=infect_num+1
            else:
                if info.loc[i,'expose_time']<=info.loc[i,'end_time']:
                    expose_num=expose_num+1
                else:
                    susceptible_num=susceptible_num+1
        print(infect_num,expose_num,susceptible_num)
        '''
        
        #此时individual_info中infect_time,expose_time已被更新，据此还原infect_state，便于可视化模块生成视频
        infect_state=[[]for i in range(N)]
        for i in range(N):
            if info.loc[i,'expose_time']>timeLen:
                infect_state[i].extend([InfectMode.SUSCEPTIBLE for i in range(info.loc[i,'start_time'],info.loc[i,'start_time']+len(trail[i]))])
            else:
                infect_state[i].extend([InfectMode.SUSCEPTIBLE for i in range(info.loc[i,'start_time'],info.loc[i,'expose_time'])])
                if info.loc[i,'infect_time']>timeLen:
                    infect_state[i].extend([InfectMode.EXPOSED for i in range(info.loc[i,'expose_time'],info.loc[i,'start_time']+len(trail[i]))])
                else:
                    infect_state[i].extend([InfectMode.EXPOSED for i in range(info.loc[i,'expose_time'],info.loc[i,'infect_time'])])
                    infect_state[i].extend([InfectMode.INFECTED for i in range(info.loc[i,'infect_time'],info.loc[i,'start_time']+len(trail[i]))])
        tmp={'infect_state':infect_state}
        state=pd.DataFrame.from_dict(tmp)

        tmp={'trail':trail}
        trail=pd.DataFrame(tmp)

        intervene_info=info[['ID','start_time']].join(state)
        intervene_info=intervene_info.join(trail)

        #返回intervene_info包含ID、start_time、infect_state、trail的dataframe
        tra={}
        for i in range(len(intervene_info)):
            j=intervene_info['ID'][i]
            tra[j]={}
            tra[j]['trajectory']=intervene_info['trail'][i]
            tra[j]['state']={}
            tra[j]['state']['start_time']=intervene_info['start_time'][i]
            tra[j]['state']['infec_state']=intervene_info['infect_state'][i]
        return tra  
    
    def congestion_sim(self):
        #拥挤风险评估函数
        #根据预处理self.pretreat()得到的轨迹坐标、个人信息评估拥挤情况
        #实现控制：
        #1.计算周围给定半径（crowd_radius）区域内人流密度中半径可调
        #2.根据个体年龄、性别、个体最大行走速度，评估拥挤风险
        #返回intervene_info：包含ID,start_time,crowd_state（拥挤量化值）,trail的dataframe

        N,timeLen,trail,info=self.pretreat()

        crowd_dense=[[]for i in range(N)]
        for moment in range(0,self.final-self.initial):
            present = info[(info['start_time']<=moment)&(info['end_time']>=moment)].index.tolist() #确定已到场且未离开的所有人的index
            for i in present:
                it=moment-info.loc[i,'start_time']-1 #it为查找坐标indice，坐标起始时刻并不一定是零时刻
                dense=0
                for j in present:
                    jt=moment-info.loc[j,'start_time']-1
                    if (i!=j) & (((trail[i][it][0]-trail[j][jt][0])**2+(trail[i][it][1]-trail[j][jt][1])**2)<=self.crowd_radius): #周围一定半径内总人数
                        dense+=1
                crowd_dense[i].append(dense)
        #得到crowd N维非定长list 描述每人每时刻周围以crowd_radius为半径圆形区域内人流密度

        #根据age、velocity、gender量化拥挤风险
        congestion_index=[[]for i in range(N)]
        for i in range(N):
            for t in range(len(crowd_dense[i])):
                if info.loc[i,'gender']==Gender.MALE:
                    if (info.loc[i,'age']<=15) or (info.loc[i,'age']>=65):
                        congestion_index[i].append(crowd_dense[i][t]*info.loc[i,'velocity']*8)
                    else:
                        congestion_index[i].append(crowd_dense[i][t]*info.loc[i,'velocity']*3)
                elif info.loc[i,'gender']==Gender.FEMALE:
                    if (info.loc[i,'age']<=15) or (info.loc[i,'age']>=65):
                        congestion_index[i].append(crowd_dense[i][t]*info.loc[i,'velocity']*9)
                    else:
                        congestion_index[i].append(crowd_dense[i][t]*info.loc[i,'velocity']*4)
        
        #归一化，认为场景内最大拥挤风险量化值为1
        max_index=max(max(row) for row in congestion_index)
        for i in range(N):
            for t in range(len(crowd_dense[i])):
                congestion_index[i][t]=congestion_index[i][t]/max_index
        tmp={"congestion_index":congestion_index}
        evaluation=pd.DataFrame(tmp)
        tmp={'trail':trail}
        trail=pd.DataFrame(tmp)
        evaluate_info=info[['ID','start_time']].join(evaluation)
        evaluate_info=evaluate_info.join(trail)
        #返回evaluate_info包含ID,start_time,congestion_index,trail的dataframe
        return evaluate_info