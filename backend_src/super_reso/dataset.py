import numpy as np
import torch
from PIL import Image
from torchvision import transforms


class MapDataset(torch.utils.data.Dataset):
    def __init__(self, train_path: str, gt_path: str, size, normalize_factor=None):
        super(MapDataset, self).__init__()
        self.train_path = train_path
        self.gt_path = gt_path

        self.train = np.load(self.train_path)
        self.gt = np.load(self.gt_path)

        if normalize_factor:
            self.train_max, self.gt_max = normalize_factor
        else:
            self.train_max = np.max(self.train)
            self.gt_max = np.max(self.gt)

        # Normalize data
        self.train = self.train / self.train_max
        self.gt = self.gt / self.gt_max

        self.pad = transforms.Pad((0, 0, 2, 2))  # left, top, right and bottom
        self.resize = transforms.Resize(size)
        self.to_tensor = transforms.ToTensor()

    def __len__(self):
        return self.train.shape[0]

    def __getitem__(self, idx):
        img_train = Image.fromarray(self.train[idx])
        img_train = self.resize(self.pad(img_train))

        img_gt = Image.fromarray(self.gt[idx])
        img_gt = self.pad(img_gt)

        data = {
            "pop_lr": self.to_tensor(np.array(img_train)),
            "pop_sr": self.to_tensor(np.array(img_gt)),
        }

        return data

    def normalize_factor(self):
        return self.train_max, self.gt_max


class MapDatasetPro(torch.utils.data.Dataset):
    """
    for production
    """

    def __init__(self, data, size, normalize_factor):
        super(MapDatasetPro, self).__init__()

        self.data = data

        self.train_max, self.gt_max = normalize_factor

        # Normalize data
        self.data = self.data / self.train_max

        self.pad = transforms.Pad((0, 0, 2, 2))  # left, top, right and bottom
        self.resize = transforms.Resize(size)
        self.to_tensor = transforms.ToTensor()

    def __len__(self):
        return self.data.shape[0]

    def __getitem__(self, idx):
        img = Image.fromarray(self.data[idx])
        img = self.resize(self.pad(img))

        data = {
            "pop_lr": self.to_tensor(np.array(img)).unsqueeze(0),
        }

        return data
