import numpy as np
import random
import yaml
import collections

class timegeo_env(object):
    def __init__(self, config_path='gan/config/config.yaml'):
        f = open(config_path)
        self.config = yaml.load(f)
        self.track_data = np.load(self.config['track_path']).astype(int)
        self.count = 0
        self.start_pos = list(self.track_data[:, :-1])
        self.traj_length = self.config['traj_length']
        self.reset()

    def reset(self):
        self.t = self.count % (self.traj_length - 1)
        self.current_pos = self.start_pos[self.count // (self.traj_length - 1)][self.t]
        stay_time = 0
        return self.current_pos, self.t

    def step(self, action):
        gps = np.loadtxt('gan/gps')
        air = np.load('gan/airport_map_9x.npy')
        self.t += 1
        done = (self.t >= self.traj_length - 1)
        #print(self.current_pos)
        #print(action)
        #print(int(gps[2,0]))
        #print((int(gps[int(self.current_pos),0]+1)))
        #print((int(gps[int(self.current_pos),1]+1)))
        #print(len(gps))
        if done:
            if self.count % (np.prod(self.track_data.shape) - self.track_data.shape[0] - 1) == 0 and self.count != 0:
                self.count = -1
            else:
                pass
            self.count += 1
        a = gps[int(self.current_pos),0]
        b = gps[int(self.current_pos),1]
        if action == 0:
            self.current_pos=self.current_pos
            # * action == 0: stay
            pass
        elif action == 1:
            # * action == 1: explore
            if int(air[int(b+1)][91-int(a+1)])==int(1):
                for i in range(len(gps)):
                    if (gps[i,0]==(a+1) and gps[i,1]==(b+1)):
                        self.current_pos=i
                        break
            else:
                self.current_pos=self.current_pos
                
        elif action == 2:
            # * action == 1: explore
            if int(air[int(b)][91-int(a+1)])==int(1):
                for i in range(len(gps)):
                    if (gps[i,0]==(a+1) and gps[i,1]==b):
                        self.current_pos=i
                        break
            else:
                self.current_pos=self.current_pos
                
        elif action == 3:
            # * action == 1: explore
            if int(air[int(b-1)][91-int(a+1)])==int(1):
                for i in range(len(gps)):
                    if (gps[i,0]==(a+1) and gps[i,1]==(b-1)):
                        self.current_pos=i
                        break
            else:
                self.current_pos=self.current_pos
                
        elif action == 4:
            if int(air[int(b+1)][91-int(a)])==int(1):
                for i in range(len(gps)):
                    if (gps[i,0]==a and gps[i,1]==(b+1)):
                        self.current_pos=i
                        break
            else:
                self.current_pos=self.current_pos
                
        elif action == 5:
            if int(air[int(b-1)][91-int(a)])==int(1):
                for i in range(len(gps)):
                    if (gps[i,0]==a and gps[i,1]==(b-1)):
                        self.current_pos=i
                        break
            else:
                self.current_pos=self.current_pos
                
        elif action == 6:
            if int(air[int(b+1)][91-int(a-1)])==int(1):
                for i in range(len(gps)):
                    if (gps[i,0]==(a-1) and gps[i,1]==(b+1)):
                        self.current_pos=i
                        break
            else:
                self.current_pos=self.current_pos
                    
        elif action == 7:
            if int(air[int(b)][91-int(a-1)])==int(1):
                for i in range(len(gps)):
                    if (gps[i,0]==(a-1) and gps[i,1]==(b)):
                        self.current_pos=i
                        break
            else:
                self.current_pos=self.current_pos                    
        else:
            if int(air[int(b-1)][91-int(a-1)])==int(1):
                for i in range(len(gps)):
                    if (gps[i,0]==(a-1) and gps[i,1]==(b-1)):
                        self.current_pos=i
                        break
            else:
                self.current_pos=self.current_pos

        return self.current_pos, self.t, done
    
    def set_state(self, pos=None, t=None):
        self.current_pos = pos if pos is not None else self.current_pos
        self.t = t if t is not None else self.t

        
#env = timegeo_env()

