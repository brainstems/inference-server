import torch


def cuda_device_enable():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def cuda_is_available():
    return torch.cuda.is_available()
