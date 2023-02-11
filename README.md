# Disease Simulation in Airport Scenario Based on Individual Mobility Model

## Introduction

This repo is the code for paper Disease Simulation in Airport Scenario Based on Individual Mobility Model. Note: we cannot provide the full simulation data of the target airport. Instead, we provide sample files to demosntrate the data format in ```./data```.


## System Requirement

### Example System Information
Operating System: Ubuntu 18.04.5 LTS
CPU: Intel(R) Xeon(R) CPU E5-2650 v4
Memory: 128G DDR4 Memory
GPU: Titan Xp



### Installation Guide
Typically, a morden computer with fast internet can complete the installation within 10 mins.

1. Download Anaconda according to [Official Website](https://www.anaconda.com/products/distribution), which can be done by the fillowing command (newer version of anaconda should also works)
``` bash
wget -c https://repo.anaconda.com/archive/Anaconda3-2022.10-Linux-x86_64.sh
```
2. Install Anaconda through the commandline guide. Permit conda init when asked.
``` bash
./Anaconda3-2022.10-Linux-x86_64.sh
```
3. Quit current terminal window and open a new one. You should able to see (base) before your command line. 

4. Use the following command to create environment. 
``` bash
conda create -n diseasesim python=3.7
conda activate diseasesim
pip install ipython pandas==1.1.5 pillow==8.1.0 matplotlib==3.3.3 setproctitle networkx==2.5 scikit-learn==0.24.1 scipy==1.4.1 tqdm GPUtil jupyterlab notebook h5py statsmodels dgl-cu101==0.5.3 toml Flask==1.1.2 flask-cors==3.0.10 shapely
```

5. Download Pytorch from the following location.
``` bash
wget -c https://download.pytorch.org/whl/cu101/torch-1.5.0%2Bcu101-cp37-cp37m-linux_x86_64.whl
wget -c https://download.pytorch.org/whl/cu101/torchvision-0.6.0%2Bcu101-cp37-cp37m-linux_x86_64.whl
pip install torch-1.5.0+cu101-cp37-cp37m-linux_x86_64.whl
pip install torchvision-0.6.0+cu101-cp37-cp37m-linux_x86_64.whl
```

6. Download and install cuda 10.1 and cudnn-10.1 v7.6.5.32. 

(Optional) If you need to exit the environment for other project, use the following command.

``` bash
conda deactivate 
```

## Run the code
### Start backend
First, you need to check the backend IP and port for the simulation.

``` bash
cd backend_src
vim ./main.sh
```

If the IP setup and port is valid, you can start the backend to wait for frontend request.
``` bash
bash ./main.sh
```


### Start frontend
First, you need to check the frontend IP and port for the simulation.

For the communication between frontend and backend:
``` bash
vim ./frontend_src/src/api/restful.js
```
For the frontend web UI:
``` bash
vim./frontend_src/package.json
```

Install frontend dependencies
``` bash
cd frontend
sudo npm config set registry https://registry.npm.taobao.org
yarn config set registry https://registry.npm.taobao.org
sudo yarn config delete proxy
sudo npm config rm proxy
sudo npm config rm https-proxy
sudo apt install -y nodejs nodejs-legacy npm  
sudo npm install n -g
sudo n stable  
npm install --global yarn
```

Start the front end
``` bash
export PATH=/usr/local/bin:$PATH
yarn install
yarn start
```

Then you can start the web browser to open the front end.
