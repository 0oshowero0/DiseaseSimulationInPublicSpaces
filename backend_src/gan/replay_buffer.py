import numpy as np
import random
from collections import deque


class replay_buffer(object):
    def __init__(self, capacity, gamma, lam):
        self.capacity = capacity
        self.gamma = gamma
        self.lam = lam
        self.memory = deque(maxlen=self.capacity)

    def store(self, pos, time, action, reward, done, value):
        pos = np.expand_dims(pos, 0)
        time = np.expand_dims(time, 0)
        #history_pos = np.expand_dims(history_pos, 0)
        self.memory.append([pos, time, action, reward, done, value])

    def sample(self, batch_size):
        batch = random.sample(self.memory, batch_size)
        pos, times, actions, rewards, dones, values, returns, advantages = zip(* batch)
        return np.concatenate(pos, 0), np.concatenate(times, 0), actions, returns, advantages

    def process(self):
        R = 0
        Adv = 0
        Value_previous = 0
        for traj in reversed(list(self.memory)):
            R = self.gamma * R * (1 - traj[4]) + traj[5]
            traj.append(R)
            # * the generalized advantage estimator(GAE)
            delta = Value_previous * self.gamma * (1 - traj[4]) - traj[5]
            Adv = delta + (1 - traj[4]) * Adv * self.gamma * self.lam
            traj.append(Adv)
            Value_previous = traj[5]

    def __len__(self):
        return len(self.memory)

    def clear(self):
        self.memory.clear()
