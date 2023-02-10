import numpy as np
import time
import pandas as pd
import json 
import random
import math
from scipy import spatial
from scipy.spatial.distance import pdist, squareform
import os
from datetime import datetime, timedelta
import ast
import matplotlib.pyplot as plt
import setproctitle
from tqdm import tqdm, trange
import torch
import torch.nn.functional as F
from math import ceil, floor
import copy
import itertools
from multiprocessing import Pool, Manager
from functools import reduce
from scipy.stats import multivariate_normal
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "1"
#DEVICE = 'cuda:1'
setproctitle.setproctitle("risk_sim")
MULTI_PROCESSING = 8

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
def file_path():
    data_path = {}
    data_path['label_rest'] = '/data4/shaoerzhuo/airport/data/labels/rest.json'
    data_path['label_seat'] = '/data4/shaoerzhuo/airport/data/labels/seat.json'
    data_path['label_security_ck'] = '/data4/shaoerzhuo/airport/data/labels/security_ck.json'
    data_path['label_shop'] = '/data4/shaoerzhuo/airport/data/labels/shop.json'
    return data_path
class Risksim:
    def __init__(self, trace, infect_ID, infect_new, initial, final, control):
        self.infect_ID=infect_ID
        self.initial = initial
        self.final = final
        self.infect_new=infect_new
        self.control = control
        print(control)
        if 'more_susceptible' in self.control:
            self.age_distrib=[0.1,0.2,0.3,0.2,0.1,0.05,0.05] #年龄分布[0~20岁，20~30岁，30~40岁，40~50岁，50~60岁，60~70岁，70~80岁]
        else:
            self.age_distrib=[0.01,0.04,0.05,0.05,0.05,0.4,0.4]
        if 'mask_on' in control:
            print(control)
            self.base_inf_possibility = 0.3
        else:
            print(control)
            self.base_inf_possibility = 1
        if 'more_disinfection' in self.control:
            self.disinfect_time=5 * 60 #消毒时间点list
        else:
            self.disinfect_time=30 * 60

        self.gender_distrib=0.4 #男性比例
        self.contact_radius=1.8 #传播社交距离
        self.solid_possi=0.7 #衡量固体接触传播可能性大小，固体被传染者接触一次时留下感染源的概率是solid_possi
        self.length=822 #室内场景图片大小为length*width
        self.width=902
        data_path = file_path()
        self.label_path=[data_path['label_seat'],data_path['label_shop'],data_path['label_rest'],data_path['label_security_ck']]
        
        self.trace,self.state = self.preprocess_trace(trace) #输入的pysocialforce生成个体轨迹
        self.init_ID=self.get_init_id(infect_ID)
        self.trail=self.update_trace()
        self.tr=self.new_tra()
        self.gauss_c,self.gauss_q,self.gauss_s=self.generate_core()
        self.inf,self.p_q,self.mat=self.get_para()
        self.state['begin_exposed'],self.state['end_exposed'],self.state['infect_time']=self.get_new_state()
    def subprocess_eval(self,i,trace,result_dict):
        begin = i * int(floor(len(trace)/MULTI_PROCESSING))
        if (i + 1) == MULTI_PROCESSING:
            end = len(trace)
        else:
            end = (i+1) * int(floor(len(trace)/MULTI_PROCESSING))
        result_dict[i] = [ast.literal_eval(trace[str(j)]) for j in range(begin,end)]
    def preprocess_trace(self,trace): #预处理pysocialforce信息
        N = len(trace)
        begin_time_abc = datetime.now()
        # m = Manager()
        # result_dict = m.dict()
        # p = Pool(MULTI_PROCESSING)
        # result = [p.apply_async(self.subprocess_eval, args=(i, trace, result_dict)) for i in range(MULTI_PROCESSING)]
        # for i in result:
        #     i.get()
        # evaled_trace_list = []
        # for v in result_dict.values():
        #     evaled_trace_list += v
        evaled_trace_list = trace
        
        init_time = np.zeros(N)  # 每个乘客进入机场时间
        end_time = np.zeros(N)   # 每个乘客离开机场时间
        for i in range(len(evaled_trace_list)):
            init_time[i] = evaled_trace_list[i]['state']['start_time']
            end_time[i] = init_time[i] + len(evaled_trace_list[i]['trajectory']) - 1 
        end_time_abc = datetime.now()
        print("Complete in "+ str((end_time_abc- begin_time_abc).total_seconds() / 60) + " mins" + '\n')
        age = [np.random.randint(i*10,(i+1)*10,size=int(ceil(self.age_distrib[i-1] * N))) for i in range(1,len(self.age_distrib)+1)]
        age = np.random.permutation(np.concatenate(age,axis=0))[:N]
        gender = np.random.binomial(n=1,p=self.gender_distrib,size=N)
        infection_rate={}
        for i in range(N):
            infection_rate[i]=0
        for i in range(len(age)):
            if (age[i]>=0) & (age[i]<20):
                if gender[i]==Gender.MALE:
                    infection_rate[i]=0.000036
                else:
                    infection_rate[i]=0.000018
            else:
                if gender[i]==Gender.MALE:
                    infection_rate[i]=math.pow(2750,(age[i]-20)/60)*0.000036
                else:
                    infection_rate[i]=math.pow(2750,(age[i]-20)/60)*0.000018
        state_dict = {'age':age, 'gender':gender, 'init_time':init_time, 'end_time':end_time,'infection_rate':infection_rate}
        return evaled_trace_list, state_dict
    def get_new_state(self):
        self.state['end_exposed']={}
        self.state['begin_exposed']={}
        self.state['infect_time']={}
        for i in range(len(self.state['end_time'])):
            self.state['begin_exposed'][i]=[]
            self.state['end_exposed'][i]=[]
            if i in self.init_ID:
                self.state['infect_time'][i]=0
            else:
                self.state['infect_time'][i]=self.inf

        return self.state['begin_exposed'],self.state['end_exposed'],self.state['infect_time']
    def point_inside_polygon(self,x,y,poly):
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
        area_state=np.zeros((self.length,self.width),dtype = np.int)
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
    def solid_mat(self): #固体传播状态矩阵mat_s
        mat_s=self.get_area() 
        mat_s=torch.FloatTensor(mat_s).to('cuda:0')
        return mat_s
    def get_data(self):
        return self.trail,self.state,self.tr
    def process_state(self):
        trace_dict = {}
        for key in range(len(self.trace)):
            self.trace[key]['state']['age'] = int(self.state['age'][int(key)])
            self.trace[key]['state']['gender'] = int(self.state['gender'][int(key)])
            self.trace[key]['state']['init_time'] = self.state['init_time'][int(key)]
            self.trace[key]['state']['begin_exposed'] = list(np.array(self.state['begin_exposed'][int(key)])+self.initial)
            self.trace[key]['state']['end_exposed'] = list(np.array(self.state['end_exposed'][int(key)])+self.initial)
            self.trace[key]['state']['infection_time'] = self.state['infect_time'][int(key)]+self.initial
            if self.trace[key]['state']['infection_time']>self.final:
                self.trace[key]['state']['infection_time']=-1
            trace_dict[str(key)] = self.trace[key]
        for i in range(len(self.trace)):
            if len(self.trace[i]['state']['end_exposed'])!=0:
                if self.trace[i]['state']['end_exposed'][-1]<self.trace[i]['state']['begin_exposed'][-1]:
                    self.trace[i]['state']['end_exposed'].append(int(self.state['end_time'][i]))
            else:
                if len(self.trace[i]['state']['end_exposed'])!=0:
                    self.trace[i]['state']['end_exposed'].append(int(self.state['end_time'][i]))  
        for key in range(len(self.trace)):
            if self.trace[key]['state']['infection_time']!=-1 and len(self.trace[key]['state']['begin_exposed'])==0:
                self.trace[key]['state']['begin_exposed'].append(self.trace[key]['state']['infection_time'])
                self.trace[key]['state']['end_exposed'].append(int(self.state['end_time'][key]))
        
        
        
        return trace_dict
    def generate_core(self):
        y = np.linspace(0, 2, 3)
        x = np.linspace(0, 2, 3)
        X, Y = np.meshgrid(x, y)
        gauss_c=torch.FloatTensor(multivariate_normal.pdf(np.dstack([X, Y]), mean=[1, 1], cov=[2,2])).to('cuda:0')
        gauss_q=torch.FloatTensor(multivariate_normal.pdf(np.dstack([X, Y]), mean=[1, 1], cov=[1,1])).to('cuda:0')
        gauss_s=torch.FloatTensor(multivariate_normal.pdf(np.dstack([X, Y]), mean=[1, 1], cov=[0.5,0.5])).to('cuda:0')
        return gauss_c,gauss_q,gauss_s
    def update_trace(self):
        tra={}
        for i in range(len(self.trace)):
            if self.state['end_time'][i]<=self.final:
                tra[i]=self.trace[i]
        return tra
    def new_tra(self):
        tr={}
        for i in range(len(self.trace)):
            if self.state['end_time'][i]<=self.final:
                tr[i]=self.trace[i]
        for i in list(self.init_ID):
            del tr[i]
        return tr
   
    def get_init_id(self,infect_ID):
        init_ID={}
        for i in infect_ID:
            if self.state['end_time'][i]<=self.final:
                init_ID[i]=i
        return init_ID
    def get_para(self):
        inf=self.final+100
        p_q=torch.zeros([822,902]).to('cuda:0')
        mat = torch.zeros([822,902]).to('cuda:0')
        return inf,p_q,mat
    def connect_mat(self,t):
        tra_1={}
        for i in self.infect_new:
            u=int(t+self.initial-self.state['init_time'][i]-1)
            tra_1[i]={}
            tra_1[i]['trajectory']=torch.FloatTensor(self.trail[i]['trajectory'][u]).unsqueeze(0).tolist()
        tra2 = reduce(lambda x,y : x + y, [tra_1[id]['trajectory'] for id in tra_1])
        tra2 = np.array(list(tra2))
        self.mat[tra2[:,1],tra2[:,0]] = 1
        return self.mat 
    def update_id(self,t):
        for i in list(self.init_ID):
            if self.state['init_time'][i]-self.initial<=t and self.state['end_time'][i]-self.initial>=t:
                if i not in self.infect_new:
                    self.infect_new[i]=i
        for i in list(self.infect_new):
            if self.state['end_time'][i]-self.initial<t:
                del self.infect_new[i]
        return self.infect_new
    def infection_sim(self,mat_s):
        for t in trange(0,self.final-self.initial):
            self.infect_new=self.update_id(t)
            mat_c=self.connect_mat(t)
            p_c=torch.conv2d(mat_c.unsqueeze(0).unsqueeze(0),self.gauss_c.unsqueeze(0).unsqueeze(0),bias=None,stride=[1,1],padding=[1,1])
            self.p_q=torch.add(self.p_q,torch.conv2d(mat_c.unsqueeze(0).unsqueeze(0),self.gauss_q.unsqueeze(0).unsqueeze(0),bias=None,stride=[1,1],padding=[1,1]))
            if t % self.disinfect_time != 0:
                p_s=torch.conv2d(mat_s.unsqueeze(0).unsqueeze(0),self.gauss_s.unsqueeze(0).unsqueeze(0),bias=None,stride=[1,1],padding=[1,1])
            else:
                p_s=torch.zeros(mat_c.shape).to('cuda:0')
            for i in list(self.tr):
                if self.state['init_time'][i]<=t+self.initial<=self.state['end_time'][i]:
                    j=t+self.initial-self.state['init_time'][i]
                    j=int(j)
                    x=int(self.trail[i]['trajectory'][j][1])
                    y=int(self.trail[i]['trajectory'][j][0])
                    r=self.state['infection_rate'][i]
                    q1=torch.sub(1,torch.mul(r,p_c))
                    q2=torch.sub(1,torch.mul(r,self.p_q))
                    q3=torch.sub(1,torch.mul(r,p_s))
                    m1=torch.mul(q1,q2)
                    m2=torch.mul(m1,q3)
                    tmp_p=torch.sub(1,m2)
                    tmp_p=tmp_p.reshape(822,902)
                    u=tmp_p[x,y]
                    if 0.1<u<self.base_inf_possibility:
                        if len(self.state['begin_exposed'][i])!=0 and len(self.state['end_exposed'][i])!=0:
                            if self.state['begin_exposed'][i][-1]<self.state['end_exposed'][i][-1]:
                                self.state['begin_exposed'][i].append(t)
                        elif len(self.state['begin_exposed'][i])==0:
                             self.state['begin_exposed'][i].append(t)  
                    elif u<=0.1:
                        if len(self.state['begin_exposed'][i])!=0 and len(self.state['end_exposed'][i])!=0:
                            if t>self.state['begin_exposed'][i][-1] and self.state['begin_exposed'][i][-1]>self.state['end_exposed'][i][-1]:
                                self.state['end_exposed'][i].append(t)
                        elif len(self.state['begin_exposed'][i])!=0 and len(self.state['end_exposed'][i])==0:
                            if t>self.state['begin_exposed'][i][-1]:
                                self.state['end_exposed'][i].append(t)
                    elif u>=self.base_inf_possibility:
                        self.state['infect_time'][i]=t
                        self.infect_new[i]=i
                        del self.tr[i]
        return self.process_state()
