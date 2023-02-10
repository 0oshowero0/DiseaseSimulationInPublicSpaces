import torch
import torch.nn as nn
from torchvision.transforms import *
import math


class ConvBlock(torch.nn.Module):
    def __init__(
        self,
        input_size,
        output_size,
        kernel_size=3,
        stride=1,
        padding=1,
        bias=True,
        activation="prelu",
        norm=None,
    ):
        super(ConvBlock, self).__init__()
        self.conv = torch.nn.Conv2d(
            input_size, output_size, kernel_size, stride, padding, bias=bias
        )

        self.norm = norm
        if self.norm == "batch":
            self.bn = torch.nn.BatchNorm2d(output_size)
        elif self.norm == "instance":
            self.bn = torch.nn.InstanceNorm2d(output_size)

        self.activation = activation
        if self.activation == "relu":
            self.act = torch.nn.ReLU(True)
        elif self.activation == "prelu":
            self.act = torch.nn.PReLU()
        elif self.activation == "lrelu":
            self.act = torch.nn.LeakyReLU(0.2, True)
        elif self.activation == "tanh":
            self.act = torch.nn.Tanh()
        elif self.activation == "sigmoid":
            self.act = torch.nn.Sigmoid()

    def forward(self, x):
        if self.norm is not None:
            out = self.bn(self.conv(x))
        else:
            out = self.conv(x)

        if self.activation is not None:
            return self.act(out)
        else:
            return out


class DeconvBlock(torch.nn.Module):
    def __init__(
        self,
        input_size,
        output_size,
        kernel_size=4,
        stride=2,
        padding=1,
        bias=True,
        activation="prelu",
        norm=None,
    ):
        super(DeconvBlock, self).__init__()
        self.deconv = torch.nn.ConvTranspose2d(
            input_size, output_size, kernel_size, stride, padding, bias=bias
        )

        self.norm = norm
        if self.norm == "batch":
            self.bn = torch.nn.BatchNorm2d(output_size)
        elif self.norm == "instance":
            self.bn = torch.nn.InstanceNorm2d(output_size)

        self.activation = activation
        if self.activation == "relu":
            self.act = torch.nn.ReLU(True)
        elif self.activation == "prelu":
            self.act = torch.nn.PReLU()
        elif self.activation == "lrelu":
            self.act = torch.nn.LeakyReLU(0.2, True)
        elif self.activation == "tanh":
            self.act = torch.nn.Tanh()
        elif self.activation == "sigmoid":
            self.act = torch.nn.Sigmoid()

    def forward(self, x):
        if self.norm is not None:
            out = self.bn(self.deconv(x))
        else:
            out = self.deconv(x)

        if self.activation is not None:
            return self.act(out)
        else:
            return out


class UpBlock(torch.nn.Module):
    def __init__(
        self,
        num_filter,
        kernel_size=8,
        stride=4,
        padding=2,
        bias=True,
        activation="prelu",
        norm=None,
    ):
        super(UpBlock, self).__init__()
        self.up_conv1 = DeconvBlock(
            num_filter, num_filter, kernel_size, stride, padding, activation, norm=None
        )
        self.up_conv2 = ConvBlock(
            num_filter, num_filter, kernel_size, stride, padding, activation, norm=None
        )
        self.up_conv3 = DeconvBlock(
            num_filter, num_filter, kernel_size, stride, padding, activation, norm=None
        )

    def forward(self, x):
        h0 = self.up_conv1(x)
        l0 = self.up_conv2(h0)
        h1 = self.up_conv3(l0 - x)
        return h1 + h0


class D_UpBlock(torch.nn.Module):
    def __init__(
        self,
        num_filter,
        kernel_size=8,
        stride=4,
        padding=2,
        num_stages=1,
        bias=True,
        activation="prelu",
        norm=None,
    ):
        super(D_UpBlock, self).__init__()
        self.conv = ConvBlock(
            num_filter * num_stages, num_filter, 1, 1, 0, activation, norm=None
        )
        self.up_conv1 = DeconvBlock(
            num_filter, num_filter, kernel_size, stride, padding, activation, norm=None
        )
        self.up_conv2 = ConvBlock(
            num_filter, num_filter, kernel_size, stride, padding, activation, norm=None
        )
        self.up_conv3 = DeconvBlock(
            num_filter, num_filter, kernel_size, stride, padding, activation, norm=None
        )

    def forward(self, x):
        x = self.conv(x)
        h0 = self.up_conv1(x)
        l0 = self.up_conv2(h0)
        h1 = self.up_conv3(l0 - x)
        return h1 + h0


class DownBlock(torch.nn.Module):
    def __init__(
        self,
        num_filter,
        kernel_size=8,
        stride=4,
        padding=2,
        bias=True,
        activation="prelu",
        norm=None,
    ):
        super(DownBlock, self).__init__()
        self.down_conv1 = ConvBlock(
            num_filter, num_filter, kernel_size, stride, padding, activation, norm=None
        )
        self.down_conv2 = DeconvBlock(
            num_filter, num_filter, kernel_size, stride, padding, activation, norm=None
        )
        self.down_conv3 = ConvBlock(
            num_filter, num_filter, kernel_size, stride, padding, activation, norm=None
        )

    def forward(self, x):
        l0 = self.down_conv1(x)
        h0 = self.down_conv2(l0)
        l1 = self.down_conv3(h0 - x)
        return l1 + l0


class D_DownBlock(torch.nn.Module):
    def __init__(
        self,
        num_filter,
        kernel_size=8,
        stride=4,
        padding=2,
        num_stages=1,
        bias=True,
        activation="prelu",
        norm=None,
    ):
        super(D_DownBlock, self).__init__()
        self.conv = ConvBlock(
            num_filter * num_stages, num_filter, 1, 1, 0, activation, norm=None
        )
        self.down_conv1 = ConvBlock(
            num_filter, num_filter, kernel_size, stride, padding, activation, norm=None
        )
        self.down_conv2 = DeconvBlock(
            num_filter, num_filter, kernel_size, stride, padding, activation, norm=None
        )
        self.down_conv3 = ConvBlock(
            num_filter, num_filter, kernel_size, stride, padding, activation, norm=None
        )

    def forward(self, x):
        x = self.conv(x)
        l0 = self.down_conv1(x)
        h0 = self.down_conv2(l0)
        l1 = self.down_conv3(h0 - x)
        return l1 + l0


class Upsampler(torch.nn.Module):
    def __init__(self, scale, n_feat, bn=False, act="prelu", bias=True):
        super(Upsampler, self).__init__()
        modules = []
        for _ in range(int(math.log(scale, 2))):
            modules.append(
                ConvBlock(n_feat, 4 * n_feat, 3, 1, 1, bias, activation=None, norm=None)
            )
            modules.append(torch.nn.PixelShuffle(2))
            if bn:
                modules.append(torch.nn.BatchNorm2d(n_feat))
            # modules.append(torch.nn.PReLU())
        self.up = torch.nn.Sequential(*modules)

        self.activation = act
        if self.activation == "relu":
            self.act = torch.nn.ReLU(True)
        elif self.activation == "prelu":
            self.act = torch.nn.PReLU()
        elif self.activation == "lrelu":
            self.act = torch.nn.LeakyReLU(0.2, True)
        elif self.activation == "tanh":
            self.act = torch.nn.Tanh()
        elif self.activation == "sigmoid":
            self.act = torch.nn.Sigmoid()

    def forward(self, x):
        out = self.up(x)
        if self.activation is not None:
            out = self.act(out)
        return out


class DBPN2(nn.Module):
    name = "DBPN2"

    def __init__(self, config):
        super(DBPN2, self).__init__()
        """
        default_config = {'input_channel' : 1, 'cuda_num' : 0,
        'base_filter' : 64, 'feat' : 256, 'kernel' : 6, 'stride' : 2, 'padding' : 2, 'num_stages' : 7}
        """
        self.config = config

        input_channel = self.config["input_channel"]
        output_channel = self.config["output_channel"]

        base_filter = self.config["base_filter"]
        feat = self.config["feat"]

        self.upscale_factor = self.config["upscale_factor"]
        if self.upscale_factor == 2:
            kernel, stride, padding = 6, 2, 2
        elif self.upscale_factor == 4:
            kernel, stride, padding = 8, 4, 2
        elif self.upscale_factor == 8:
            kernel, stride, padding = 12, 8, 2

        # Initial Feature Extraction
        self.feat0 = ConvBlock(
            input_channel, feat, 3, 1, 1, activation="prelu", norm=None
        )
        self.feat1 = ConvBlock(
            feat, base_filter, 1, 1, 0, activation="prelu", norm=None
        )
        # Back-projection stages
        self.up1 = UpBlock(base_filter, kernel, stride, padding)
        self.down1 = DownBlock(base_filter, kernel, stride, padding)
        self.up2 = UpBlock(base_filter, kernel, stride, padding)
        self.down2 = D_DownBlock(base_filter, kernel, stride, padding, 2)
        self.up3 = D_UpBlock(base_filter, kernel, stride, padding, 2)

        self.output_conv = ConvBlock(
            3 * base_filter, output_channel, 3, 1, 1, activation=None, norm=None
        )

        self.criterion = None
        self.optimizer = None

        for m in self.modules():
            classname = m.__class__.__name__
            if classname.find("Conv2d") != -1:
                # torch.nn.init.kaiming_normal_(m.weight)
                torch.nn.init.normal_(m.weight.data, 0.0, 0.02)
                # if m.bias is not None:
                #    m.bias.data.zero_()
            elif classname.find("ConvTranspose2d") != -1:
                # torch.nn.init.kaiming_normal_(m.weight)
                torch.nn.init.normal_(m.weight.data, 0.0, 0.02)
                # if m.bias is not None:
                #    m.bias.data.zero_()
            elif classname.find("BatchNorm") != -1:
                torch.nn.init.normal_(m.weight.data, 1.0, 0.02)
                torch.nn.init.constant_(m.bias.data, 0.0)

    def assign_cuda(self, cuda_num):
        self.config["cuda_num"] = cuda_num

    def forward(self, batch):
        pop_lr = batch["pop_lr"].cuda(self.config["cuda_num"])
        x = self.feat0(pop_lr)
        x = self.feat1(x)

        h1 = self.up1(x)
        l1 = self.down1(h1)
        h2 = self.up2(l1)

        concat_h = torch.cat((h2, h1), 1)
        l = self.down2(concat_h)
        concat_l = torch.cat((l, l1), 1)
        h = self.up3(concat_l)
        concat_h = torch.cat((h, concat_h), 1)

        x = self.output_conv(concat_h)
        return x