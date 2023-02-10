from gail import gail
from env import timegeo_env
import yaml
import numpy as np


if __name__ == '__main__':
    env = timegeo_env()
    file = np.load('./raw_data/geolife/real.npy')
    test = gail(
        env=env,
        file=file
    )
    test.run()
