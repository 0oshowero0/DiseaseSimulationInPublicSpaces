import torch
import numpy as np
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
import torch.nn as nn
import torch.optim as optim
from model import DBPN2
from dataset import MapDataset
import time
from tqdm import tqdm
import toml

conf = toml.load("super_reso/conf.toml")


def GPU_max_free_memory():
    import pynvml

    pynvml.nvmlInit()
    free_list = []
    for iter in range(pynvml.nvmlDeviceGetCount()):
        handle = pynvml.nvmlDeviceGetHandleByIndex(iter)
        meminfo = pynvml.nvmlDeviceGetMemoryInfo(handle)
        free_list.append(meminfo.free)
    return np.argmax(free_list)


cuda_num = GPU_max_free_memory()
device = "cuda:" + str(cuda_num)
max_epoch = conf["train"]["max_epoch"]
lr = conf["train"]["lr"]
test_freq = conf["train"]["test_freq"]
checkpoint_freq = conf["train"]["checkpoint_freq"]


def show_img(map_: np.ndarray):
    plt.imshow(1 - map_, cmap="gray")
    plt.savefig("airport_plot.png")


def train(model, optimizer, criterion, dataloader, epoch):
    epoch_loss = 0
    model.train()
    for iteration, batch in enumerate(dataloader):
        optimizer.zero_grad()
        t0 = time.time()

        prediction = model(batch)
        loss = criterion(prediction, batch["pop_sr"].transpose(3, 2).to(device))

        t1 = time.time()
        epoch_loss += loss.data * 1000
        loss.backward()
        optimizer.step()

        print(
            "===> Epoch[{}]({}/{}): Loss: {:.4f} || Timer: {:.4f} sec.".format(
                epoch, iteration + 1, len(dataloader), loss.data * 1000, (t1 - t0)
            )
        )

    print(
        "===> Epoch {} Complete: Avg. Loss: {:.4f}".format(
            epoch, epoch_loss / len(dataloader)
        )
    )


def test(model, criterion, dataloader):
    test_loss = 0
    model.eval()
    print("===> Running test...")
    with torch.no_grad():
        for batch in tqdm(dataloader):

            prediction = model(batch)
            loss = criterion(prediction, batch["pop_sr"].transpose(3, 2).to(device))

            test_loss += loss.data * 1000

    print("===> Test Complete: Avg. Loss: {:.4f}".format(test_loss / len(dataloader)))


def print_network(net):
    num_params = 0
    for param in net.parameters():
        num_params += param.numel()
    print(net)
    print("Total number of parameters: %d" % num_params)


def checkpoint(epoch, model):
    model_out_path = "data/weight/" + "epoch_{}.pth".format(epoch)
    torch.save(model.state_dict(), model_out_path)
    print("Checkpoint saved to {}".format(model_out_path))


print("===> Loading datasets")
dataset = MapDataset(
    "data/rebuild_map_small.npy",
    "data/label_1day.npy",
    size=[int(904 / 4), int(824 / 4)],
)
dataloader = DataLoader(dataset, batch_size=2)
test_dataset = MapDataset(
    "data/rebuild_map_small_test.npy",
    "data/label_day2.npy",
    [int(904 / 4), int(824 / 4)],
    dataset.normalize_factor(),
)
test_dataloader = DataLoader(test_dataset, batch_size=2)

print("===> Building model ")
config = {
    "input_channel": conf["model"]["input_channel"],
    "output_channel": conf["model"]["output_channel"],
    "upscale_factor": conf["model"]["upscale_factor"],
    "cuda_num": cuda_num,
    "base_filter": conf["model"]["base_filter"],
    "feat": conf["model"]["feat"],
    "kernel": conf["model"]["kernel"],
    "stride": conf["model"]["stride"],
    "padding": conf["model"]["padding"],
    "num_stages": conf["model"]["num_stages"],
}
model = DBPN2(config).to(device)
criterion = nn.L1Loss().to(device)

print("---------- Networks architecture -------------")
print_network(model)
print("----------------------------------------------")

optimizer = optim.Adam(model.parameters(), lr=lr, betas=(0.9, 0.999), eps=1e-8)

for epoch in range(max_epoch):
    train(model, optimizer, criterion, dataloader, epoch)

    # learning rate is decayed by a factor of 10 every half of total epochs
    if (epoch + 1) % (max_epoch / 2) == 0:
        for param_group in optimizer.param_groups:
            param_group["lr"] /= 10.0
        print("Learning rate decay: lr={}".format(optimizer.param_groups[0]["lr"]))

    # plot map
    plot_data = (
        model({"pop_lr": dataset[3]["pop_lr"].unsqueeze(0)})
        .to("cpu")
        .detach()
        .numpy()
        .squeeze()
    )
    show_img(plot_data)

    # run test
    if epoch % test_freq == 0:
        test(model, criterion, test_dataloader)

    if epoch % checkpoint_freq == 0:
        checkpoint(epoch, model)
