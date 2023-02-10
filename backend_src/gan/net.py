import torch
import torch.nn as nn
import numpy as np
import torch.nn.functional as F
from torch.distributions import Categorical, Normal
import math
import numpy as np


def gen_gaussian_dist(sigma=10):
    """Return a single-sided gaussian distribution weight array and its index.
    """
    u = 0
    x = np.linspace(0, 1, 100)
    y = np.exp(-(x - u) ** 2 / (2 * sigma ** 2)) / \
        (math.sqrt(2 * math.pi) * sigma)
    return x, y


class ATNetwork(nn.Module):
    """Basic Generator.
    """
    def __init__(
            self,
            total_locations=9100,
            time_scale=300,
            embedding_net=None,
            loc_embedding_dim=32,
            tim_embedding_dim=10,
            hidden_dim=64,
            bidirectional=False,
            data='geolife',
            device=None,
            starting_sample='zero',
            starting_dist=None,
            return_prob=True):
        """

        :param total_locations:
        :param embedding_net:
        :param embedding_dim:
        :param hidden_dim:
        :param bidirectional:
        :param cuda:
        :param starting_sample:
        :param starting_dist:
        """
        super(ATNetwork, self).__init__()
        self.total_locations = total_locations
        self.time_scale = time_scale
        self.loc_embedding_dim = loc_embedding_dim
        self.embedding_dim = loc_embedding_dim + tim_embedding_dim
        self.hidden_dim = hidden_dim
        self.bidirectional = bidirectional
        self.linear_dim = hidden_dim * 2 if bidirectional else hidden_dim
        self.device = device
        self.data = data
        self.starting_sample = starting_sample
        self.return_prob = return_prob

        if self.starting_sample == 'real':
            self.starting_dist = torch.tensor(starting_dist).float()

        if embedding_net:
            self.embedding = embedding_net
        else:
            self.loc_embedding = nn.Embedding(
                num_embeddings=self.total_locations, embedding_dim=self.loc_embedding_dim)
            self.tim_embedding = nn.Embedding(
                num_embeddings=self.time_scale, embedding_dim=10)

        self.attn = nn.MultiheadAttention(self.hidden_dim, 8)
        self.Q = nn.Linear(self.embedding_dim, self.hidden_dim)
        self.V = nn.Linear(self.embedding_dim, self.hidden_dim)
        self.K = nn.Linear(self.embedding_dim, self.hidden_dim)

        self.linear = nn.Linear(self.linear_dim, self.total_locations)
        if self.return_prob:
            self.output_layer = nn.Linear(self.total_locations, 9)
        else:
            self.output_layer = nn.Linear(self.total_locations, 1)

        self.init_params()

    def init_params(self):
        for param in self.parameters():
            param.data.uniform_(-0.01, 0.01)

    def init_hidden(self, batch_size):
        h = torch.LongTensor(torch.zeros(
            (2 if self.bidirectional else 1, batch_size, self.hidden_dim)))
        c = torch.LongTensor(torch.zeros(
            (2 if self.bidirectional else 1, batch_size, self.hidden_dim)))
        if self.device:
            h, c = h.to(self.device), c.to(self.device)
        return h, c

    def forward(self, x_l, x_t):
        """
        :param x: (batch_size, seq_len), sequence of locations
        :return:
            (batch_size * seq_len, total_locations), prediction of next stage of all locations
        """
        locs = x_l.contiguous().view(-1).detach().cpu().numpy()

        lemb = self.loc_embedding(x_l)
        temb = self.tim_embedding(x_t)       
        x = torch.cat([lemb, temb], dim=-1)

        Query = self.Q(x)
        Query = F.relu(Query)
        Query = Query.unsqueeze(0)

        Value = self.V(x)
        Value = F.relu(Value)
        Value = Value.unsqueeze(0)

        Key = self.K(x)
        Key = F.relu(Key)
        Key = Key.unsqueeze(0)

        x, _ = self.attn(Query, Key, Value)
        pred = self.linear(
            x.contiguous().view(-1, self.linear_dim))

        pred = pred 
        pred = self.output_layer(F.relu(pred))
        if self.return_prob:
            pred = F.softmax(pred, -1)
        return pred

    def act(self, x_l, x_t):
        prob = self.forward(x_l, x_t)
        dist = torch.distributions.Categorical(prob)
        action = dist.sample()
        return action.cpu().item()


class Discriminator(nn.Module):
    def __init__(
        self,
        total_locations=9100,
        time_scale=300,
        embedding_net=None,
        loc_embedding_dim=32,
        tim_embedding_dim=10,
        act_embedding_dim=9,
        hidden_dim=64
    ):
        super(Discriminator, self).__init__()
        self.total_locations = total_locations
        self.time_scale = time_scale
        self.loc_embedding_dim = loc_embedding_dim
        self.tim_embedding_dim = tim_embedding_dim
        self.act_embedding_dim = act_embedding_dim
        self.hidden_dim = hidden_dim
        self.embedding_dim = loc_embedding_dim + tim_embedding_dim + act_embedding_dim

        self.loc_embedding = nn.Embedding(
            num_embeddings=self.total_locations, embedding_dim=self.loc_embedding_dim)
        self.tim_embedding = nn.Embedding(
            num_embeddings=self.time_scale, embedding_dim=self.tim_embedding_dim)
        self.act_embedding = nn.Embedding(
            num_embeddings=9, embedding_dim=self.act_embedding_dim)
        self.mlp_layer = nn.Sequential(
            nn.Linear(self.embedding_dim, self.hidden_dim),
            nn.ReLU(),
            nn.Linear(self.hidden_dim, self.hidden_dim),
            nn.ReLU(),
            nn.Linear(self.hidden_dim, self.hidden_dim),
            nn.ReLU(),
            nn.Linear(self.hidden_dim, self.hidden_dim),
            nn.ReLU(),
            nn.Linear(self.hidden_dim, 1),
            nn.Sigmoid()
        )

    def forward(self, x_l, x_t, x_a):
        lemb = self.loc_embedding(x_l)
        temb = self.tim_embedding(x_t)
        aemb = self.act_embedding(x_a)    

        x = torch.cat([lemb, temb, aemb], dim=-1)
        reward = self.mlp_layer(x)
        return reward
