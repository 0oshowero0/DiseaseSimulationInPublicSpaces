import numpy as np
import pandas as pd
import torch
from torch import FloatTensor, LongTensor
from copy import deepcopy
import json

def normalize(tensor): # [N, 2]
    distance = torch.norm(tensor, dim=-1)
    direction = tensor / (distance.unsqueeze(-1) + 1e-8)
    return direction, distance # [N, 2], [N]

def angle(tensor): # [N, 2]
    return torch.atan2(tensor[..., 1], tensor[..., 0]) # [N]

def distance(coordinate1, coordinate2): # [N, 2], [N, 2]
    assert coordinate1.shape[0] == coordinate2.shape[0]
    difference = coordinate2 - coordinate1
    direction, distance = normalize(difference)
    return distance, direction, difference # [N], [N, 2], [N, 2]

def cross_distance(coordinate1, coordinate2): # [N1, 2], [N2, 2]
    difference = coordinate1.unsqueeze(1) - coordinate2.unsqueeze(0)
    direction, distance = normalize(difference)
    return distance, direction, difference # [N1, N2], [N1, N2, 2], [N1, N2, 2]

def cap(tensor, max_tensor):
    norm = torch.norm(tensor, dim=-1, keepdim=True)
    factor = max_tensor / (norm + 1e-6)
    factor[factor > 1] = 1.0
    return tensor * factor


class FieldOfView(object):
    """
    Compute field of view prefactors.
    The field of view angle twophi is given in degrees.
    out_of_view_factor is C in the paper.
    """

    def __init__(self, phi, out_of_view_factor):
        self.cosphi = np.cos(phi / 180.0 * np.pi)
        self.out_of_view_factor = out_of_view_factor

    def __call__(self, desired_dir, forces_dir):
        """Weighting factor for field of view.

        desired_direction : e, rank 2 and normalized in the last index.
        forces_direction : f, rank 3 tensor.
        """
        in_sight = (
            torch.einsum("aj, abj->ab", desired_dir, forces_dir) > torch.norm(forces_dir, dim=-1) * self.cosphi
        )
        out = self.out_of_view_factor * torch.ones_like(in_sight, device=in_sight.device)
        out[in_sight] = 1.0
        out[np.arange(out.shape[0]), np.arange(out.shape[1])] = 0.0
        return out


class PedPedPotential(object):
    def __init__(self, delta_t, v0, sigma):
        """
        Ped-ped interaction potential.
        v0 is in m^2 / s^2.
        sigma is in m.
        """
        self.delta_t = delta_t
        self.v0 = v0
        self.sigma = sigma

    def b(self, r_ab, speed, direction):
        """
        Calculate b.
        b denotes the semi-minor axis of the ellipse and is given by
        e: desired direction
        2b=sqrt((r_ab+(r_ab-v*delta_t*e_b))
        """
        speed_b = speed.unsqueeze(0)
        speed_b_abc = speed_b.unsqueeze(2)  # abc = alpha, beta, coordinates
        e_b = direction.unsqueeze(0)
        in_sqrt = (torch.norm(r_ab, dim=-1) + torch.norm(r_ab - self.delta_t * speed_b_abc * e_b, dim=-1)) ** 2 - (self.delta_t * speed_b) ** 2
        in_sqrt[np.arange(in_sqrt.shape[0]), np.arange(in_sqrt.shape[0])] = 0.0
        return 0.5 * in_sqrt.clamp(0, 1e9).sqrt()

    def value_r_ab(self, r_ab, speed, direction):
        """Value of potential explicitly parametrized with r_ab."""
        b = self.b(r_ab, speed, direction)
        v = self.v0 * torch.exp(-b / self.sigma)
        return v
    
    def grad_r_ab(self, ped, delta=1e-3):
        """Compute gradient wrt r_ab using finite difference differentiation."""
        r_ab = ped._pedped_coor_diff
        speed, direction = ped._speed, ped._direction
        
        v = self.value_r_ab(r_ab, speed, direction)
        
        dx = FloatTensor(np.array([[[delta, 0.0]]])).to(ped.device)
        dy = FloatTensor(np.array([[[0.0, delta]]])).to(ped.device)
        
        dvdx = (self.value_r_ab(r_ab + dx, speed, direction) - v) / delta
        dvdy = (self.value_r_ab(r_ab + dy, speed, direction) - v) / delta
        
        dvdx[np.arange(dvdx.shape[0]), np.arange(dvdx.shape[0])] = 0.0
        dvdy[np.arange(dvdy.shape[0]), np.arange(dvdy.shape[0])] = 0.0
        return torch.stack([dvdx, dvdy], dim=-1)

class Force:
    def __init__(self, sim, config):
        self.sim = sim
        self.config = config
        self.device = sim.device
        
class PedRepulsiveForce(Force):
    def get_force(self):
        ped = self.sim.ped
        
        potential_func = PedPedPotential(self.sim.config['step_width'], v0=self.config["v0"], sigma=self.config["sigma"])
        f_ab = -1.0 * potential_func.grad_r_ab(ped)
        fov = FieldOfView(phi=self.config["fov_phi"], out_of_view_factor=self.config["fov_factor"])
        w = fov(ped._next_dir, -f_ab).unsqueeze(-1)
        F_ab = w * f_ab
        force = torch.sum(F_ab, dim=1)
        return self.config["factor"] * force
    
class DesiredForce(Force):
    def get_force(self):
        ped = self.sim.ped
        force = ped._next_dir * ped._max_speed - ped._velocity
        #print('{0}-{1}-{2}'.format(ped._next_dir.shape, ped._max_speed.shape, ped._velocity.shape))
        return self.config["factor"] * force 
    
class ObstacleForce(Force):
    def get_force(self):
        ped = self.sim.ped
        env = self.sim.env
        sigma = self.config["sigma"]
        threshold = self.config["threshold"]
        force = torch.zeros([len(ped.active_peds), 2]).to(self.device)
        if env.obstacles.shape[0] == 0:
            return force
        
        pedenv_dist, pedenv_dir, pedenv_diff = cross_distance(ped._coor, env.obstacles)
        pedenv_dist = pedenv_dist.unsqueeze(-1) - 0.35#ped.get_stacked_attr('agent').unsqueeze(-1)
        pedenv_dir *= torch.exp(-pedenv_dist / sigma)
        force = (pedenv_dir * (pedenv_dist < threshold)).sum(dim=1)
        return self.config["factor"] * force

class SocialForce(Force):
    def get_force(self):
        ped = self.sim.ped
        
        gamma = self.config['gamma']
        lambda_importance = self.config['lambda_importance']
        n = self.config['n']
        n_prime = self.config['n_prime']

        # compute interaction direction t_ij
        interaction_dist, interaction_dir, interaction_diff = distance(ped._pedped_coor_dir, lambda_importance * ped._pedped_vel_diff)

        # compute angle theta (between interaction and position difference vector)
        theta = angle(interaction_dir) - angle(ped._pedped_coor_dir)
        # compute model parameter B = gamma * ||D||
        B = gamma * interaction_dist
        left_normal = torch.stack([-interaction_dir[..., 1], interaction_dir[..., 0]], dim=-1)
        
        force_velocity_amount = torch.exp(-1.0 * ped._pedped_coor_dist / (B + 1e-8) - (n_prime * B * theta).sqrt())
        force_angle_amount = -torch.sign(theta) * torch.exp(-1.0 * ped._pedped_coor_dist / (B + 1e-8) - (n * B * theta)**2)
        force_velocity = force_velocity_amount.unsqueeze(-1) * interaction_dir
        force_angle = force_angle_amount.unsqueeze(-1) * left_normal

        force = force_velocity + force_angle
        force[torch.isnan(force)] = 0
        force = force.sum(dim=1)
        return self.config['factor'] * force


class Ped:
    def __init__(self, config, device=torch.device('cpu')):
        self.config = dict(config)
        self.device = device
        
        # Volatile Properties 
        self.coordinate = FloatTensor(self.config['init_coordinate']).to(self.device)
        self.velocity = FloatTensor(self.config['init_velocity']).to(self.device)
        self.waypoint = deepcopy(self.config['waypoint'])
        if len(self.waypoint) > 0:
            self.waypoint[0] = FloatTensor(self.waypoint[0]).to(self.device)
        self.config['trajectory'] = [] if 'trajectory' not in self.config else self.config['trajectory']
        
        # Fixed Properties
        self.start_time = self.config['start_time']
        self.arrive_distance_threshold = FloatTensor([self.config['arrive_distance_threshold']]).to(self.device)
        self.max_speed = FloatTensor([self.config['max_speed']]).to(self.device)
        self.update()
        
    def update(self):
        '''
        Verify whether ped arrives the first waypoint,
        and update coordinate into ped's trajectory.
        '''
        if distance(self.waypoint[0][:2], self.coordinate)[0] <= self.config['arrive_distance_threshold']:
            if self.waypoint[0][2] > 0:
                self.waypoint[0][2] -= 1
            else:
                self.waypoint = self.waypoint[1:]
                if len(self.waypoint) > 0:
                    self.waypoint[0] = FloatTensor(self.waypoint[0]).to(self.device)
        self.config['trajectory'].append(self.coordinate.cpu().numpy().tolist())
        
        
def dummy_pedstrian_init(num_peds, seed=0):
    np.random.seed(seed)
    waypoint = [[(100*np.sin(iter), 100*np.cos(iter), 1), (100*np.sin(iter + 1.57), 100*np.cos(iter + 1.57), 1)] for iter in np.linspace(0, 2*np.pi, num_peds)]
    
    return pd.DataFrame({
        'id' : [int(iter) for iter in np.arange(num_peds)],
        'start_time' : [int(iter) for iter in (np.arange(num_peds) // 10).astype(int).tolist()],
        'init_coordinate' : ((np.random.rand(num_peds, 2) - 0.5) * 10).tolist(), 
        'init_velocity' : ((np.random.rand(num_peds, 2) * 0)).tolist(), 
        'arrive_distance_threshold' : (np.ones([num_peds]) * 1).astype(float).tolist(), 
        'max_speed' : 1.3,
        'waypoint' : waypoint,
    })

class PedState:
    def __init__(self, start_time, config=dummy_pedstrian_init(1000), device=torch.device('cpu')):
        '''
        config: the dataframe contains the settings of all peds,
            each columns contains one property and all properties used in class Ped
            have to be included.
        device : torch.device
        '''
        self.peds = {}
        self.active_peds = []
        self.t = start_time
        self.max_ped = 4000
        self.device = device
        self.join(config)

    def size(self):
        return len(self.active_peds)
        
    def join(self, config):
        for row in config.iloc:
            self.peds[row['id']] = Ped(row, device=self.device)
        self.update_active_peds()
        self.update_cache()
        
    def to_dict(self):
        state_dict = {str(id):str({'trajectory':self.peds[id].config.pop('trajectory'), 'state':self.peds[id].config}) for id in self.peds}
        return state_dict
    
    def get_stacked_attr(self, attr): # -> torch.FloatTensor [self.size(), X]
        return torch.stack([getattr(self.peds[id], attr) for id in self.active_peds], dim=0)
    
    def set_stacked_attr(self, attr, x):
        assert x.shape[0] == len(self.active_peds)
        assert len(x.shape) <= 2
        for row, id in enumerate(self.active_peds):
            setattr(self.peds[id], attr, x[row])
            
    def check_ped(self, ped):
        if ped.config['start_time'] + len(ped.config['trajectory']) == self.t:
            return True # Simulating
        if ped.config['start_time'] + len(ped.config['trajectory']) < self.t:
            if len(ped.waypoint) == 0:
                return True # Simulation finished
        return False
            
    def next_waypoint(self):
        # Return coordinates of the final waypoints.
        return torch.stack([self.peds[id].waypoint[0][:2] for id in self.active_peds], dim=0)
    
    def velocity(self, norm=False):
        if norm:
            vel = self.velocity(norm=False)
            speed = torch.norm(vel, dim=1)
            direction = vel / (speed.unsqueeze(-1) + 1e-6)
            return speed, direction
        else:
            return self.get_stacked_attr('velocity')
    
    def update_cache(self):
        # Called before calculating InfectSimulator.get_force, InfectSimulator.infect and PedState.step
        self._coor = self.get_stacked_attr('coordinate')
        self._next_coor = self.next_waypoint()
        
        self._velocity = self.velocity(norm=False)
        self._speed, self._direction = self.velocity(norm=True)
        
        self._next_dist, self._next_dir, self._next_diff = distance(self._coor, self._next_coor) # [N], [N, 2], [N, 2]
        
        self._pedped_coor_dist, self._pedped_coor_dir, self._pedped_coor_diff = cross_distance(self._coor, self._coor)   # [N, N], [N, N, 2], [N, N, 2]
        self._pedped_vel_dist, self._pedped_vel_dir, self._pedped_vel_diff = cross_distance(self._velocity, self._velocity)     # [N, N], [N, N, 2], [N, N, 2]
        
        self._threshold_distance = self.get_stacked_attr('arrive_distance_threshold')
        self._max_speed = self.get_stacked_attr('max_speed')
        
    def update_active_peds(self):
        # More than 1 target in waypoint(list) and t > start_time.
        self.active_peds = list(filter(lambda id : (len(self.peds[id].waypoint) > 0) & (self.peds[id].start_time <= self.t), self.peds))[:self.max_ped]
        
    def step(self, force, step_width=1):
        if len(self.active_peds) > 0:
            ##### Update Coordinate and velocity of each agent. #####
            self._velocity = cap(self._velocity + step_width * force, step_width * self._max_speed)
            self._coor = self._coor + self._velocity * step_width
            #print('{0}-{1}-{2}'.format(self._velocity.shape, self._coor.shape, self._next_coor.shape))
            self.set_stacked_attr('velocity', self._velocity)
            self.set_stacked_attr('coordinate', self._coor)
            
            ##### Update waypoint, trajectory and cache of each agent. #####
            for id in self.active_peds:
                self.peds[id].update()
                
            ##### Confirm activate agents and their cache. #####
        self.update_active_peds()
        if len(self.active_peds) > 0:
            self.update_cache()
            
class EnvState:
    """State of the environment obstacles"""

    def __init__(self, obstacles, resolution, device=torch.device('cpu')):
        self.device = device
        self.resolution = resolution
        self.obstacles = obstacles # A Coor Instance

    @property
    def obstacles(self):
        """obstacles is a list of np.ndarray"""
        return self._obstacles

    @obstacles.setter
    def obstacles(self, obstacles):
        """Input an list of (startx, endx, starty, endy) as start and end of a line"""
        if obstacles is None:
            self._obstacles = FloatTensor(np.zeros([0,2])).to(device=self.device)
        else:
            self._obstacles = []
            for startx, endx, starty, endy in obstacles:
                samples = int(np.linalg.norm((startx - endx, starty - endy)) * self.resolution)
                line = FloatTensor(list(zip(np.linspace(startx, endx, samples), np.linspace(starty, endy, samples))))
                self._obstacles.append(line)
            self._obstacles = torch.cat(self._obstacles, dim=0).to(device=self.device)
            
            
class SocialForceSimulator:
    import toml
    def __init__(self, config, ped_configs, obstacles, start_time=0, device=torch.device('cpu')):
        self.device = device
        
        import toml
        self.config = config
        
        #self.ped = PedState(ped_configs, self.config['Pedestrian'])
        self.ped = PedState(start_time, config=ped_configs, device=self.device)
        #assert np.all([self.ped.check_ped(self.ped.peds[id]) for id in self.ped.peds])
        self.env = EnvState(obstacles, self.config['resolution'], device=self.device)
        
        self.forces = [
            DesiredForce(self, self.config['DesiredForce']),
            ObstacleForce(self, self.config['ObstacleForce']),
            PedRepulsiveForce(self, self.config['PedRepulsiveForce']),
        ]

    def compute_forces(self):
        if len(self.ped.active_peds) > 0:
            forces = list(map(lambda x: x.get_force(), self.forces))
            return sum(forces)
        else:
            return None
    
    def step(self):
        self.ped.step(self.compute_forces())
        self.ped.t += 1