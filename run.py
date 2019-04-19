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
    app.init_bot(configs['telegram_token'])
    app.init_omdb(configs['omdb_apikey'])


if __name__ == '__main__':
    main()
