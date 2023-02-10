from .replay_buffer import replay_buffer
from .net import ATNetwork, Discriminator
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import pickle
import yaml
import random
import os
import setproctitle
from tqdm import tqdm, trange

class gail(object):
    def __init__(self, env, file, config_path='gan/config/config.yaml', eval=False):
        f = open(config_path)
        self.config = yaml.load(f)

        self.env = env
        self.episode = self.config['episode']
        self.capacity = self.config['capacity']
        self.gamma = self.config['gamma']
        self.lam = self.config['lam']
        self.value_learning_rate = self.config['value_learning_rate']
        self.policy_learning_rate = self.config['policy_learning_rate']
        self.discriminator_learning_rate = self.config['discriminator_learning_rate']
        self.batch_size = self.config['batch_size']
        self.policy_iter = self.config['policy_iter']
        self.disc_iter = self.config['disc_iter']
        self.value_iter = self.config['value_iter']
        self.epsilon = self.config['epsilon']
        self.entropy_weight = self.config['entropy_weight']
        self.train_iter = self.config['train_iter']
        self.clip_grad = self.config['clip_grad']
        self.file = file
        self.action_dim = 9

        self.total_locations = self.config['total_locations']
        self.time_scale = self.config['time_scale']
        self.loc_embedding_dim = self.config['loc_embedding_dim']
        self.tim_embedding_dim = self.config['tim_embedding_dim']
        self.embedding_net = self.config['embedding_net']
        self.embedding_dim = self.loc_embedding_dim + self.tim_embedding_dim
        self.hidden_dim = self.config['hidden_dim']
        self.bidirectional = self.config['bidirectional']
        self.linear_dim = self.hidden_dim * 2 if self.bidirectional else self.hidden_dim
        self.device = 1
        self.data = self.config['data']
        self.starting_sample = self.config['starting_sample']
        self.starting_dist = self.config['starting_dist']

        self.act_embedding_dim = self.config['act_embedding_dim']
        self.recover_cnn_reward_ratio = self.config['recover_cnn_reward_ratio']
        self.recover_cnn_learning_rate = self.config['recover_cnn_learning_rate']

        self.model_save_interval = self.config['model_save_interval']
        self.eval = eval
        self.test_data_path = self.config['test_data_path']
        self.test_data = np.load(self.test_data_path)

        self.policy_net = ATNetwork(
            self.total_locations,
            self.time_scale,
            self.embedding_net,
            self.loc_embedding_dim,
            self.tim_embedding_dim,
            self.hidden_dim,
            self.bidirectional,
            self.data,
            self.device,
            self.starting_sample,
            self.starting_dist,
            return_prob=True
        ).to(self.device)

        self.value_net = ATNetwork(
            self.total_locations,
            self.time_scale,
            self.embedding_net,
            self.loc_embedding_dim,
            self.tim_embedding_dim,
            self.hidden_dim,
            self.bidirectional,
            self.data,
            self.device,
            self.starting_sample,
            self.starting_dist,
            return_prob=False
        ).to(self.device)

        self.discriminator = Discriminator(
            self.total_locations,
            self.time_scale,
            self.loc_embedding_dim,
            self.tim_embedding_dim,
            self.act_embedding_dim,
            self.hidden_dim,
        ).to(self.device)


        self.buffer = replay_buffer(self.capacity, self.gamma, self.lam)
        self.policy_optimizer = torch.optim.Adam(self.policy_net.parameters(), lr=0.001, weight_decay=0.00001)
        self.policy_pretrain_optimizer = torch.optim.Adam(self.policy_net.parameters(), lr=0.001)
        self.value_optimizer = torch.optim.Adam(self.value_net.parameters(), lr=self.value_learning_rate)
        self.discriminator_optimizer = torch.optim.Adam(self.discriminator.parameters(), lr=self.discriminator_learning_rate)
        #loss
        self.disc_loss_func = nn.BCELoss() 
        self.weight_custom_reward = None

        os.makedirs('gan/models/', exist_ok=True)
        os.makedirs('gan/eval/', exist_ok=True)

        if self.eval:
            self.policy_net.load_state_dict(torch.load('gan/models/policy_net.pkl'))
            self.value_net.load_state_dict(torch.load('gan/models/value_net.pkl'))
            self.discriminator.load_state_dict(torch.load('gan/models/discriminator.pkl'))

    def sample_real_data(self, start_index=None):
        #print(self.file.shape[1])
        total_track_num = self.file.shape[0] * (self.file.shape[1] - 1)
        if start_index is None:
            sample_index = list(np.random.choice(total_track_num, self.batch_size))
            sample_index = [(x // (self.file.shape[1] - 1), x % (self.file.shape[1] - 1)) for x in sample_index]
        else:
            sample_index = list(range(start_index, start_index + self.batch_size))
            sample_index = [x % total_track_num for x in sample_index]
            sample_index = [(x // (self.file.shape[1] - 1) , x % (self.file.shape[1] - 1)) for x in list(range(start_index, start_index + self.batch_size))]
        time = [index[1] for index in sample_index]
        #print(time)
        pos = [self.file[index] for index in sample_index]
        next_pos = [self.file[index[0], index[1]+1] for index in sample_index]
        action = []
        gps = np.loadtxt('gps')
        for i in range(self.batch_size):
            if next_pos[i] == pos[i]:
                action.append(0)
            elif (int(gps[int(next_pos[i]),0])-int(gps[int(pos[i]),0]))>0.9 and (int(gps[int(next_pos[i]),1])-int(gps[int(pos[i]),1]))>=0.9:
                action.append(1)
            elif (int(gps[int(next_pos[i]),0])-int(gps[int(pos[i]),0]))>0.9 and (int(gps[int(next_pos[i]),1])-int(gps[int(pos[i]),1]))<0.9 and (int(gps[int(next_pos[i]),1])-int(gps[int(pos[i]),1]))>-0.9:
                action.append(2)
            elif (int(gps[int(next_pos[i]),0])-int(gps[int(pos[i]),0]))>0.9 and (int(gps[int(next_pos[i]),1])-int(gps[int(pos[i]),1]))<0.9 and (int(gps[int(next_pos[i]),1])-int(gps[int(pos[i]),1]))<-0.9:
                action.append(3)
            elif (int(gps[int(next_pos[i]),0])-int(gps[int(pos[i]),0]))>-0.9 and (int(gps[int(next_pos[i]),0])-int(gps[int(pos[i]),0]))<0.9 and (int(gps[int(next_pos[i]),1])-int(gps[int(pos[i]),1]))>0.9:
                action.append(4)
            elif (int(gps[int(next_pos[i]),0])-int(gps[int(pos[i]),0]))>-0.9 and (int(gps[int(next_pos[i]),0])-int(gps[int(pos[i]),0]))<0.9 and (int(gps[int(next_pos[i]),1])-int(gps[int(pos[i]),1]))<-0.9:
                action.append(5)
            elif (int(gps[int(next_pos[i]),0])-int(gps[int(pos[i]),0]))<-0.9 and (int(gps[int(next_pos[i]),1])-int(gps[int(pos[i]),1]))>0.9:
                action.append(6)
            elif (int(gps[int(next_pos[i]),0])-int(gps[int(pos[i]),0]))<-0.9 and (int(gps[int(next_pos[i]),1])-int(gps[int(pos[i]),1]))<0.9 and (int(gps[int(next_pos[i]),1])-int(gps[int(pos[i]),1]))>-0.9:
                action.append(7)
            else:
                action.append(8)
        print(action)
        return list(zip(pos, time)), action

    def ppo_pretrain(self, start_index):
        expert_batch = self.sample_real_data(start_index)
        expert_observations, expert_actions= expert_batch[0], expert_batch[1]
        expert_observations = np.vstack(expert_observations)
        expert_observations = torch.LongTensor(expert_observations).to(self.device)
        expert_actions_index = torch.LongTensor(expert_actions).unsqueeze(1).to(self.device)
        expert_trajs = torch.cat([expert_observations], 1)
        probs = self.policy_net.forward(expert_trajs[:, 0], expert_trajs[:, 1])
        #print(probs)

        loss = F.nll_loss(probs, expert_actions_index.squeeze())
        self.policy_optimizer.zero_grad()
        loss.backward()
        self.policy_pretrain_optimizer.step()

    
    def ppo_train(self):
        pos, times, actions, returns, advantages = self.buffer.sample(self.batch_size)
        pos = torch.LongTensor(pos).to(self.device)
        times = torch.LongTensor(times).to(self.device)  
        advantages = torch.FloatTensor(advantages).unsqueeze(1).to(self.device)
        advantages = (advantages - advantages.mean()) / advantages.std()
        advantages = advantages.detach()
        returns = torch.FloatTensor(returns).to(self.device).unsqueeze(1).detach()

        for _ in range(self.value_iter):
            values = self.value_net.forward(pos, times)
            value_loss = (returns - values).pow(2).mean()
            self.value_optimizer.zero_grad()
            value_loss.backward()
            self.value_optimizer.step()

        actions_d = torch.LongTensor(actions).unsqueeze(1).to(self.device)
        old_probs = self.policy_net.forward(pos, times)
        old_probs = old_probs.gather(1, actions_d)
        dist = torch.distributions.Categorical(old_probs)
        entropy = dist.entropy().unsqueeze(1)
        for _ in range(self.policy_iter):
            probs = self.policy_net.forward(pos, times)
            probs = probs.gather(1, actions_d)
            ratio = probs / old_probs.detach()
            surr1 = ratio * advantages
            surr2 = torch.clamp(ratio, 1. - self.epsilon, 1. + self.epsilon) * advantages
            policy_loss = - torch.min(surr1, surr2) - self.entropy_weight * entropy
            policy_loss = policy_loss.mean()
            self.policy_optimizer.zero_grad()
            policy_loss.backward(retain_graph=True)
            torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), self.clip_grad)
            self.policy_optimizer.step()

    def discriminator_train(self):
        expert_batch = self.sample_real_data()
        expert_observations, expert_actions = expert_batch[0], expert_batch[1]
        expert_observations = np.vstack(expert_observations)
        expert_observations = torch.LongTensor(expert_observations).to(self.device)
        expert_actions_index = torch.LongTensor(expert_actions).unsqueeze(1).to(self.device)

       
        expert_trajs = torch.cat([expert_observations, expert_actions_index], 1)
        expert_labels = torch.FloatTensor(self.batch_size, 1).fill_(0.0).to(self.device)

        pos, times, actions, _, _ = self.buffer.sample(self.batch_size)
        pos = torch.LongTensor(pos).view(-1, 1).to(self.device)
        times = torch.LongTensor(times).view(-1, 1).to(self.device)
        observations = torch.cat([pos, times], dim=-1).to(self.device)

        actions_index = torch.LongTensor(actions).unsqueeze(1).to(self.device)

        trajs = torch.cat([observations, actions_index], 1)

        labels = torch.FloatTensor(self.batch_size, 1).fill_(1.0).to(self.device)

        for _ in range(self.disc_iter):

            # * optimize discriminator
            expert_reward = self.discriminator.forward(expert_trajs[:, 0], expert_trajs[:, 1], expert_trajs[:, 2])
            current_reward = self.discriminator.forward(trajs[:, 0], trajs[:, 1], trajs[:, 2])
            expert_loss = self.disc_loss_func(expert_reward, expert_labels)
            current_loss = self.disc_loss_func(current_reward, labels)

            loss = (expert_loss + current_loss) / 2
            self.discriminator_optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.discriminator.parameters(), self.clip_grad)
            self.discriminator_optimizer.step()

    def get_reward(self, pos, time, action):
        pos = torch.LongTensor([pos]).to(self.device)
        time = torch.LongTensor([time]).to(self.device)
        action = torch.LongTensor([action]).to(self.device)
        d_reward = self.discriminator.forward(pos, time, action)
        reward = d_reward
        log_reward = - reward.log()
        return log_reward.detach().item()

    def eval_test(self, index):
        result = np.zeros_like(self.test_data)
        for i in trange(len(self.test_data)):
            t = 0
            pos = self.test_data[i][t]
            self.env.set_state(pos=int(pos), t=int(t))
            result[i][t] = pos
            while True:
                action = self.policy_net.act(torch.LongTensor(np.expand_dims(pos, 0)).to(self.device), torch.LongTensor(np.expand_dims(t, 0)).to(self.device))
                #print(action)
                next_pos, next_t, done = self.env.step(action)
                result[i][next_t] = next_pos
                pos = next_pos
                t = next_t
                if done:
                    break
        return result.astype(np.int)
        #np.save('./eval/eval_{}.npy'.format(index), result.astype(np.int))

    def generator_pretrain_run(self, max_epoch):
        epoch = 0
        start_index = 0
        while epoch <= max_epoch:
            self.ppo_pretrain(start_index)
            start_index += 1
            epoch += 1
            start_index = start_index % (self.file.shape[0] * (self.file.shape[1] - 1))
            if start_index > (self.file.shape[0] * (self.file.shape[1] - 1) - self.batch_size):
                start_index = 0

    def run(self):
        print(self) 
        #self.generator_pretrain_run(20000)
        #print('generator')
        for i in range(self.episode):
            if (i + 1) % self.model_save_interval == 0:
                self.eval_test((i + 1) // self.model_save_interval)
