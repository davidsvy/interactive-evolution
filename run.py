import argparse
import os
from src.ea import Evolutionary_algorithm
import yaml


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--config', '-c', default='configs/config.yaml',
        help='Path to the config file')

    args = parser.parse_args()

    with open(args.config, 'r') as file:
        try:
            config = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            print(exc)

    img_size = (config['gui_args']['img_width'],
                config['gui_args']['img_height'])

    config['gui_args'].pop('img_width', None)
    config['gui_args'].pop('img_height', None)
    config['gui_args']['img_size'] = img_size

    try:
        import google.colab
        colab = True
    except:
        colab = False

    config['gui_args']['colab'] = colab
    if colab:
        config['ea_args']['use_gui'] = False

    return config


def main():
    config = parse_args()
    ea = Evolutionary_algorithm(
        gan_args=config['gan_args'],
        gui_args=config['gui_args'],
        **config['ea_args'])
    ea.run()


if __name__ == '__main__':
    main()
