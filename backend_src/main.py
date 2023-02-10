import torch, json, pickle, importlib, math, random, os, yaml
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from utils.unix_time import *
from utils.file_path import file_path
data_path = file_path('../data')
from configparser import ConfigParser
from flask import Flask, request, json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def GPU_max_free_memory():
    import pynvml  
    pynvml.nvmlInit()
    free_list = []
    for iter in range(pynvml.nvmlDeviceGetCount()):
        handle = pynvml.nvmlDeviceGetHandleByIndex(iter)
        meminfo = pynvml.nvmlDeviceGetMemoryInfo(handle)
        free_list.append(meminfo.free)
    return np.argmax(free_list)

class AirportSimulator:
    def data_completion(
        self,
        method="gaussian_offline",
        begin_time=1474214400,
        end_time=1474300800,
        period=10 * 60,
    ):
        """
        完成数据补全，从稀疏人口分布中恢复出全局细粒度人口分布
        params: method: 数据补全方法，默认为gcn_lstm_deconf, 还可以选择二维高斯补全;
                begin_time: 补全开始时间戳(unixtime)，默认为2016-09-19 00:00:00;
                end_time: 补全结束时间戳(unixtime)，默认为2016-09-20 00:00:00;
                period: 补全时间间隔，默认为10分钟;
        return: numpy矩阵，第一维度为时间，第二、三维度与机场区域尺度相同，每个元素为对应区域的人口补全结果
        """
        from utils.unix_time import local_time, unix_time
        from utils.file_path import file_path

        if method == "gaussian_offline":
            data_begin_time = 1473505200
            if begin_time < data_begin_time:
                raise Exception("开始时间过小")
            begin_idx = np.floor((begin_time - data_begin_time) / 600).astype(int)
            end_idx = np.ceil((end_time - data_begin_time) / 600).astype(int)

            # 读取预处理好的文件
            # 该文件位于/data4/liyuze/airport_simulator/data
            gaussian_map = np.load(data_path["distribution"])
            return gaussian_map[begin_idx:end_idx]

        elif method == "gaussian_online":
            from scipy.stats import multivariate_normal

            data = pd.read_csv(data_path["map_ap_data"], converters={"PassengerCountMean": eval})
            wifimap_df = pd.read_csv(
                data_path["map_ap_location"],
                index_col=0,
                converters={"loc": eval},
            )

            begin_time_local = local_time(begin_time)
            end_time_local = local_time(end_time)

            data_selected = data[
                (data["Time"] >= begin_time_local) & (data["Time"] <= end_time_local)
            ]

            result = []

            data_time = data_selected.groupby("Time")

            def gauss_fun(X, Y, sv, sm):
                d = np.dstack([X, Y])
                z = None
                for i in range(len(sv)):
                    mean = sm[i]
                    # Extract covariance matrix
                    cov = [100, 100]
                    gaussian = multivariate_normal(mean=mean, cov=cov)
                    z_ret = gaussian.pdf(d) * sv[i]
                    if z is None:
                        z = z_ret
                    else:
                        z += z_ret
                return z

            y = np.linspace(0, 822, 822)
            x = np.linspace(0, 902, 902)

            for time, data_slice in data_time:

                tmp = pd.merge(data_slice, wifimap_df, on="WIFIAPTag")
                sv = tmp["PassengerCountMean"].to_numpy()
                sm = tmp["loc"].to_numpy()
                X, Y = np.meshgrid(x, y)
                Z = gauss_fun(X, Y, sv, sm)
                result.append(Z)
            result = np.array(result)
            result[result < 0] =0
            return result

        elif method == "super_reso":
            from super_reso.SuperReso import SuperReso
            wifiap_path = data_path["map_ap_data"]  # 设置路径
            location_path = data_path["map_ap_location"]  # 设置路径
            dominate_map_path = data_path["map_dominate"]
            weight_path = data_path["weight_super_reso"]

            begin_time_local = local_time(begin_time)
            end_time_local = local_time(end_time)

            data = pd.read_csv(
                wifiap_path,
                converters={"PassengerCountMean": eval},
            )
            data_selected = data[
                (data["Time"] >= begin_time_local) & (data["Time"] <= end_time_local)
            ]

            sr = SuperReso()
            sr.init_model()
            sr.load_weight(weight_path)
            data_map = sr.preprecess_map(data_selected, dominate_map_path, location_path)
            result = sr.complete_data(data_map)
            return result

        
    def gen_individual_traces(
        self,
        scenario='airport',
        method="social_force",
        control=None,
        begin_time=1473638400,
        end_time=1473652800,
        period=1,
        folder_path='../data',
        heatmap=None):
        import numpy as np
        if method == 'social_force':
            from social_force.SocialForceSimulator import SocialForceSimulator
            import social_force.Engine as Engine
            import toml
            """
            params: 
                methods: 'social_force' or 'gan'; 
                control: ['social_distancing', 'more_security_ck', 'speed_up', 'reduce_explore']
                begin_time: unixtime
                end_time: unixtime
                period: int, default 1
            return: json
            {id:{'trajectory': [[x0, y0], [x1, y1], ...], 'state': {}}}
            """
            if type(control) == type(None):
                control = []
            else:
                control.sort()
            file_name = '{0}/{1}/trace/{2}-{3}-{4}-{5}-{6}.json'.format(
                folder_path, scenario, method, begin_time, end_time, '-'.join(control), period)
            
            ##### Processing Control Method #####
            config = toml.load('social_force/default.toml')
            
            if 'speed_up' in control:
                print('Pedestrians speed up')
                config['Pedestrian']['max_speed_multiplier'] *= 1.5
            if 'social_distancing' in control:
                print('Applying Social Distancing')
                config['PedRepulsiveForce'] = config['PedRepulsiveForceSocialDistancing']
            if 'reduce_explore' in control:
                print('Explore Reduced')
            if 'more_security_ck' in control:
                print('Open More Security Check')

            config['more_security_ck'] = ('more_security_ck' in control)
            print(config)
            
            if os.path.exists(file_name):
                print('Loading existing trace file: {}'.format(file_name))
                with open(file_name, 'r') as f:
                    d = json.load(f)
                return d
            
            def timestamp2str(timestamp):
                return datetime.strftime(datetime.fromtimestamp(timestamp), "%Y/%m/%d %H:%M:%S")
            
            def str2timestamp(string):
                return int(datetime.strptime(string, "%Y/%m/%d %H:%M:%S").timestamp())

            data_path = file_path(folder_path)
            if type(heatmap) == type(None):
                heatmap = np.load(data_path['distribution'])
            str_begin, str_end = timestamp2str(begin_time), timestamp2str(end_time)
            obstacles = np.array(Engine.load_airport_lines(data_path, more_security_ck=config['more_security_ck'], vertical_flip=True))
            
            df = Engine.init_by_day(data_path, start=str_begin, end=str_end)
            df = Engine.relay_policy(data_path, df, 'reduce_explore' in control, config['more_security_ck'], heatmap[:, ::-1], start=str_begin, end=str_end)
            df = Engine.vertical_flip(df)
            df = df.join(pd.DataFrame({
                'id' : df.index,
                'start_time' : df['checkin_time'],
                'init_velocity' : np.ones([len(df.index), 2]).tolist(), 
                'arrive_distance_threshold' : 2 * np.ones([len(df.index)]),
                'max_speed' : config['Pedestrian']['max_speed_multiplier'] * np.ones([len(df.index)]),
                'infect_state' : np.zeros(df.shape[0]).tolist()
            }))

            s = SocialForceSimulator(config, df, obstacles, start_time=begin_time, device=torch.device('cuda:0'))

            bar = tqdm(np.arange(end_time - begin_time), ncols=60)
            for iter in bar:
                bar.set_description('ActivePeds:{0}'.format(len(s.ped.active_peds)))
                s.step()

            d = s.ped.to_dict()
            with open(file_name, 'w') as f:
                json.dump(d, f)
                print('Trajectory file saved in {0}'.format(file_name))
            return d
        
        elif method == 'gan':
            from gan.gail import gail
            from gan.env import timegeo_env
            
            sf_trace = self.gen_individual_traces(
                scenario, 'social_force', control, begin_time, end_time, period, 
                heatmap=heatmap)
            
            sf_trace = {eval(key):eval(sf_trace[key]) for key in sf_trace}
            
            airport_map = np.load('gan/airport_map_9x.npy')
            x_max = airport_map.shape[0]
            y_max = airport_map.shape[1]
            all_points = []
            
            for k, v in tqdm(sf_trace.items()):
                indiv = v
                traj = np.array(indiv['trajectory'])#轨迹
                traj_x = np.around(traj[:,0]).astype(int)
                traj_y = np.around(traj[:,1]).astype(int)
                points = traj_x * y_max + traj_y
                all_points.append(points)
            
            env = timegeo_env('gan/config/test.yaml')
            file = np.load('gan/raw_data/geolife/real.npy')
            test = gail(
                env=env,
                file=file[:2],
                config_path='gan/config/test.yaml',
                eval=True)
            simp_trace = test.run()
            
            
            import numpy as np
            m=np.loadtxt('gan/gps')
            recovered_trace={}
            for i in range(simp_trace.shape[0]):
                recovered_trace[i]={}
                recovered_trace[i]['trajectory']=[]
                recovered_trace[i]['state']={}
                recovered_trace[i]['state']['start_time']=0
                for j in simp_trace[i]:
                    j=int(j)
                    p=[]
                    p.append(m[j][0])
                    p.append(m[j][1])
                    recovered_trace[i]['trajectory'].append(p)
                    
            for i in recovered_trace:
                for j in range(len(recovered_trace[i]['trajectory'])):
                    recovered_trace[i]['trajectory'][j][1]=np.around(tra[i]['trajectory'][j][1]*822/91)
                    recovered_trace[i]['trajectory'][j][0]=np.around(tra[i]['trajectory'][j][0]*902/100)
                    
            recovered_trace = {str(key):str(recovered_trace[key]) for key in recovered_trace}
            return recovered_trace

    def crowd_risk_evaluation(self, tra, control=None, initial=1473638400, final=1473638400 + 7200):
        import risk_sim.Risksim as Risksim
        sim = Risksim.Risksim(tra, initial, final)
        crowd = sim.congestion_sim()
        return crowd
    
    def infection_risk_evaluation(self, trace, control=None, initial=1473638400, final=1473638400 + 7200):
        trace = {int(key):eval(trace[key]) for key in trace}
        use_fake = False
        if use_fake:
            # 伪传染，感染状态与时间完全随机
            import risk_sim.RiskSimFake as Risksim
            risk_sim = Risksim.Risksim(trace)
            trace = risk_sim.infection_sim_fake()
            return trace
        else:
            import risk_sim.RiskSimTorch as Risksim
            """
            基于个体移动轨迹评估传染风险
            return: 附带带有感染模拟结果的轨迹
            """
            #infect_ID = list(np.load("/data4/masiran/Risksim/infect_ID.npy"))
            infect_ID = list(trace.keys())
            np.random.shuffle(infect_ID)
            infect_ID = infect_ID[:int(len(infect_ID) * 0.1)]
            infect_new = {}
            risk_sim = Risksim.Risksim(trace, infect_ID, infect_new, initial, final, control)
            trace = risk_sim.infection_sim(risk_sim.solid_mat())
            return trace
    
AS = AirportSimulator()
#################### data_completion ####################
#http://localhost:2000/group_completion?scenario=airport&method=gaussian_offline&begin_time=1474214400&end_time=1474215600&period=600
@app.route('/group_completion', methods=['GET', 'POST'])
def return_data_completion():
    scenario = request.args.get('scenario', default='airport')
    method = request.args.get('method', default='gaussian_offline')
    begin_time = request.args.get('begin_time', default=1474214400, type=int)
    end_time = request.args.get('end_time', default=1474300800, type=int)
    period = request.args.get('period', default=60*10, type=int)
    
    assert(method in ['gaussian_offline', 'gaussian_online', 'gcn_lstm_deconf', 'super_reso'])
    
    print(' '.join([str(iter) for iter in [
        'Completing Group Data:', method, scenario, begin_time, end_time, period]]))
    data = AS.data_completion(method=method, begin_time=begin_time, end_time=end_time, period=period)
    #return str(data.shape)
    return json.jsonify(data.tolist())
    
#################### gen_individual_traces ####################
#http://localhost:2000/individual_traces?scenario=airport&method=social_force&trace_control=None&begin_time=1473638400&end_time=1473652800&period=1
@app.route('/individual_traces', methods=['GET', 'POST'])
def return_individual_traces():
    scenario = request.args.get('scenario', default='airport')
    method = request.args.get('method', default='social_force')
    trace_control = eval(request.args.get('trace_control', default='None', type=str))
    begin_time = request.args.get('begin_time', default=1473638400, type=int)
    end_time = request.args.get('end_time', default=1473652800, type=int)
    period = request.args.get('period', default=1, type=int)
    print(' '.join([str(iter) for iter in [
        "Generating Individual Traces:", method, begin_time, end_time, period, trace_control]]))
    trace = AS.gen_individual_traces(
        scenario, 'social_force', trace_control, begin_time, end_time, period, 
        heatmap=AS.data_completion(
            method='super_reso', begin_time=begin_time, end_time=end_time, period=600))
    return json.jsonify(trace)

#################### risk_evaluation ####################
@app.route('/risk_evaluation', methods=['GET', 'POST'])
#http://localhost:2000/risk_evaluation?scenario=airport&risk=congestion&method=social_force&trace_control=None&risk_control=None&begin_time=1473638400&end_time=1473652800&period=1
def return_risk_evaluation():
    scenario = request.args.get('scenario', default='airport', type=str)
    risk = request.args.get('risk', default='congestion', type=str)
    method = request.args.get('method', default='social_force', type=str)
    trace_control = eval(request.args.get('trace_control', default='None', type=str))
    risk_control = eval(request.args.get('risk_control', default='None', type=str))
    begin_time = request.args.get('begin_time', default=1473638400, type=int)
    end_time = request.args.get('end_time', default=1473652800, type=int)
    period = request.args.get('period', default=1, type=int)
    assert(risk in ['congestion', 'epidemic'])
    
    trace = AS.gen_individual_traces(
        scenario, method, trace_control, begin_time, end_time, period)
    if risk == 'congestion':
        print(' '.join([str(iter) for iter in [
            "Estimating congestion risk:", method, begin_time, end_time, period, trace_control]]))
        risk = AS.crowd_risk_evaluation(
            trace, control=risk_control, initial=begin_time, final=end_time)
    else:
        print(' '.join([str(iter) for iter in [
            "Estimating epidemic risk:", method, begin_time, end_time, period, trace_control]]))
        risk = AS.infection_risk_evaluation(
            trace, control=risk_control, initial=begin_time, final=end_time)
    return json.jsonify({str(key):str(risk[key]) for key in risk})
