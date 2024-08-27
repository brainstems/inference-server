import torch

import src.cuda_utils


def test_device_enable_returns_valid_device():
    device = src.cuda_utils.cuda_device_enable()
    assert str(device) == "cpu" or str(device) == "cuda"


def test_device_enable_returns_expected_device():
    expected_device_enable_device = src.cuda_utils.cuda_device_enable()
    device_enable_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("device_enable_device", device_enable_device)
    assert expected_device_enable_device == device_enable_device
