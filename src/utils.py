import numpy as np
from PIL import Image
import random
import torch


def set_seed(seed_val):
    """Sets seed for reproducibility.
    Args:
        seed_val (int): Seed for rng.
    """
    random.seed(seed_val)
    np.random.seed(seed_val)
    torch.manual_seed(seed_val)
    torch.cuda.manual_seed_all(seed_val)


def torch_to_pil(images):
    """Transforms the unnormalized output of a gan into a list of PIL images.

    Args:
        images (torch.tensor): unnormalized output of a gan

    Returns:
        (list of PIL.Image)
    """
    images_tr = ((images.clamp(min=-1, max=1) + 1) / 2).permute(0, 2, 3, 1)
    images_np = (images_tr.cpu().detach().numpy() * 255).astype(np.uint8)
    images_pil = [Image.fromarray(img, 'RGB') for img in images_np]

    return images_pil


def torch_to_np(images):
    """Transforms the unnormalized output of a gan into a numpy array
    Args:
        images (torch.tensor): unnormalized output of a gan

    Returns:
        (numpy.array)
    """
    return ((images.clamp(min=-1, max=1) + 1) / 2).permute(0, 2, 3, 1).cpu().detach().numpy()
