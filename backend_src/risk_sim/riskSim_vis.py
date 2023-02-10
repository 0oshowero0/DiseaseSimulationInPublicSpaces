import datetime
from datetime import timedelta
from contextlib import contextmanager
import pytest, json
import numpy as np
from numpy.random import normal
import matplotlib.pyplot as plt
import matplotlib.animation as mpl_animation
from tqdm import tqdm
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
'''
使用示例见test_example.py
'''
class riskSim_vis():
    def __init__(self,
                 trace,
                 label_open,
                 label_color,
                 label_style,
                 start_date_timestamp,
                 start,
                 end,
                 output_path,
                 data_path=file_path()):
        self.states=trace
        self.output_path=output_path
        self.label_open=label_open
        self.label_color=label_color
        self.label_style=label_style
        self.data_path=data_path
        self.start_date_timestamp = start_date_timestamp
        self.WHITE = [1,1,1]
        self.BLACK = [0,0,0]
        self.BLUE = [0, 0.4470, 0.7410]
        self.RED = [0.8500, 0.3250, 0.0980]
        self.YELLOW = [0.9290, 0.6940, 0.1250]
        self.PURPLE = [0.494, 0.184, 0.556]
        self.SUSCEPTIBLE=0
        self.EXPOSED=1
        self.INFECTED=2
        self.writer='ffmpeg'
        self.start, self.end = start + self.start_date_timestamp, end + self.start_date_timestamp
        self.id_list = [[] for iter in range(self.end - self.start)]
        for j in tqdm(trace):
            start = trace[j]['state']['start_time'] - self.start
            end = trace[j]['state']['start_time'] - self.start + len(trace[j]['trajectory'])
            for t in np.arange(start, end):
                if t < len(self.id_list):
                    self.id_list[int(t)].append(j)
        def get_space(data_path,label_open):#获取机场的轮廓数据和相关label的轮廓数据
            space={}
            with open(data_path['map_outlines'], 'r') as f:
                         lines_dict = json.load(f)
            space['map_outlines']=[]
            for _,line in lines_dict.items():#机场轮廓数据
                space['map_outlines'].append([line['first'][1],line['second'][1],822-line['first'][0],822-line['second'][0]])
            for label,display in label_open.items():#label的轮廓数据
                if display:
                    space[label]=[]
                    with open(data_path[label],'r') as f1:
                         label_dict = json.load(f1)
                    for i in label_dict:
                        space[label].append([label_dict[i]['down_left'][1],label_dict[i]['down_right'][1],
                                      822-label_dict[i]['down_left'][0],822-label_dict[i]['down_right'][0]])
                        space[label].append([label_dict[i]['top_left'][1],label_dict[i]['top_right'][1],
                                      822-label_dict[i]['top_left'][0],822-label_dict[i]['top_right'][0]])
                        space[label].append([label_dict[i]['down_right'][1],label_dict[i]['top_right'][1],
                                      822-label_dict[i]['down_right'][0],822-label_dict[i]['top_right'][0]])
            return space
        self.space=get_space(data_path,label_open)
    @contextmanager
    def animation(self,start,end):
        fig = plt.figure(figsize=(20,10))#构建画布
        fig.set_tight_layout(True)
        ax = fig.add_subplot(111)
        ax.set_aspect(1.0, 'datalim')
        plt.axis('off')
        a,b,c=self.get_num(0)
        ax.text(-400, 799, "易感态人数:%s"%a, size = 20,family = "SimHei")
        ax.text(-400, 765, "暴露态人数:%s"%b, size = 20,family = "SimHei")
        ax.text(-400, 730, "感染态人数:%s"%c, size = 20,family = "SimHei")
        context = {'ax': ax,'update_function': None}
        yield context
        ani = mpl_animation.FuncAnimation(fig, context['update_function'],range(end-start))#在给定演示的开始和结束时间后生成动画
        ani.save(self.output_path, writer=self.writer)
        fig.show()
        plt.close(fig)
    def get_num(self,t):#获取当前时间三种状态的人口数量
        a=b=c=0
        t=t+self.start_date_timestamp
        for j in self.states:
            if self.states[j]['state']['start_time']+len(self.states[j]['state']['infec_state'])>t:
                if t>=self.states[j]['state']['start_time']:
                    if int(self.states[j]['state']['infec_state'][t-self.states[j]['state']['start_time']])==0:
                        a=a+1
                    if int(self.states[j]['state']['infec_state'][t-self.states[j]['state']['start_time']])==1:
                        b=b+1
                    if int(self.states[j]['state']['infec_state'][t-self.states[j]['state']['start_time']])==2:
                        c=c+1
        return a,b,c
    @contextmanager   
    def generate(self,start,end):
        facecolor_dict = {self.SUSCEPTIBLE : self.WHITE, self.EXPOSED : self.WHITE, self.INFECTED : self.RED}
        edgecolor_dict = {self.SUSCEPTIBLE : self.BLUE, self.EXPOSED : self.PURPLE, self.INFECTED : self.RED}
        with self.animation(start,end) as context:
            ax = context['ax']
            ax.set_xlabel('x [m]')
            ax.set_ylabel('y [m]')
            yield ax
            for label,label_obstacle in self.space.items():#基于得到的轮廓数据可视化，表现方式和颜色由输入决定
                for u,iter in enumerate(label_obstacle):
                    if u<1:#防止图例重复，让它只显示一次
                        ax.plot(np.array(iter).reshape([-1, 2])[0], np.array(iter).reshape([-1, 2])[1], '-o', 
                            color=self.label_color[label], markersize=1, linewidth=3,linestyle=self.label_style[label],label=label)
                    else:
                        ax.plot(np.array(iter).reshape([-1, 2])[0], np.array(iter).reshape([-1, 2])[1], '-o', 
                            color=self.label_color[label], markersize=1, linewidth=3,linestyle=self.label_style[label])
            ax.legend()
            human_actors = []        
            for ped in np.arange(max(map(lambda x:len(x), self.id_list))):
                radius = 1
                if ped < len(self.id_list[0]):
                    p = plt.Circle(self.states[self.id_list[0][ped]]['trajectory'][0], radius=radius)
                else:
                    p = plt.Circle(self.states[self.id_list[0][-1]]['trajectory'][0], radius=radius)
                human_actors.append(p)
                ax.add_patch(p)
            def update(i):#动画的更新函数，包括点的坐标更新与三种状态人数的更新
                if len(self.id_list[i]) > 0:
                    for ped, p in enumerate(human_actors):
                        if ped >= len(self.id_list[i]):
                            ped = -1
                        t = int(self.start + i - self.states[self.id_list[i][ped]]['state']['start_time'])
                        id = self.id_list[i][ped]
                        p.center = self.states[id]['trajectory'][t]
                        if 'infec_state' in self.states[id]['state']:
                            p.set_facecolor(facecolor_dict[self.states[id]['state']['infec_state'][t]])
                            p.set_edgecolor(edgecolor_dict[self.states[id]['state']['infec_state'][t]])
                        else:
                            p.set_facecolor(facecolor_dict[self.SUSCEPTIBLE])
                            p.set_edgecolor(edgecolor_dict[self.SUSCEPTIBLE])
                ax.text(-400, 799, "暴露态人数:%s"%10000, size = 20,family = "SimHei", color = "w", style = "italic", weight = "light",bbox = dict(facecolor = "w", alpha = 1))
                ax.text(-400, 765, "暴露态人数:%s"%10000, size = 20,family = "SimHei", color = "w", style = "italic", weight = "light",bbox = dict(facecolor = "w", alpha = 1))
                ax.text(-400, 730, "感染态人数:%s"%10000, size = 20,family = "SimHei", color = "w", style = "italic", weight = "light",bbox = dict(facecolor = "w", alpha = 1))
                a,b,c=self.get_num(i)
                ax.text(-400, 799, "易感态人数:%s"%a, size = 20,family = "SimHei")
                ax.text(-400, 765, "暴露态人数:%s"%b, size = 20,family = "SimHei")
                ax.text(-400, 730, "感染态人数:%s"%c, size = 20,family = "SimHei")
                print('=', end='')
            context['update_function'] = update         
    def visualize(self,start,end):#此处的start和end是演示的开始和结束时间
        with self.generate(start,end) as _:
            pass  
