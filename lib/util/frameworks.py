import torch


def get_device(force_cpu=False):
    device = torch.device('cuda' if torch.cuda.is_available() and not force_cpu else 'cpu')
    print(f'Using {device} device. (Notice: {torch.cuda.device_count()} cuda device available.)')
    return device
