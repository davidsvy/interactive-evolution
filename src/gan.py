import torch


def get_model(model='PGAN', dataset='celebAHQ-512', use_gpu=True):
    all_models = ['PGAN', 'DCGAN']
    if not model in all_models:
        raise KeyError(
            f"'model' should be in {all_models}."
        )

    pgan_datasets = ['celebAHQ-256', 'celebAHQ-512', 'DTD', 'celeba']
    if model == 'PGAN' and not dataset in pgan_datasets:
        raise KeyError(
            f"If model == 'PGAN', dataset should be in {pgan_datasets}"
        )

    model = torch.hub.load('facebookresearch/pytorch_GAN_zoo:hub', model,
                           model_name=dataset, pretrained=True, useGPU=use_gpu)

    return model
