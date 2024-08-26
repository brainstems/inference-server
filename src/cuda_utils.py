import torch


def cuda_device_enable():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")
