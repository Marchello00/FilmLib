import app
import argparse
import json


def parse_args():
    parser = argparse.ArgumentParser(description='Film Library telegram bot')
    parser.add_argument('--config', '-c', default='config.json',
                        help="path to your config.json file (README)")
    return parser.parse_args()


def load_config(config_path):
    with open(config_path, 'r') as f:
        s = json.load(f)
        return s


def main():
    args = parse_args()
    configs = load_config(args.config)
    app.init(token=configs['telegram_token'], apikey=configs['omdb_apikey'])
    app.converter.get_russian('Аватар')


if __name__ == '__main__':
    main()
