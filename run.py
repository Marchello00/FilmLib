import app
import argparse
import json
import asyncio
import os


def parse_args():
    parser = argparse.ArgumentParser(description='Film Library telegram bot')
    parser.add_argument('--config', '-c', default='config.json',
                        help='path to your config.json file (README)')
    parser.add_argument('--debug', '-d', action='store_true',
                        help='debug mode')
    return parser.parse_args()


def load_config_file(config_path):
    with open(config_path, 'r') as f:
        s = json.load(f)
        return s


def load_config_environ():
    return {
        'telegram_token': os.environ.get('TOKEN'),
        'omdb_apikey': os.environ.get('APIKEY')
    }


async def start():
    await app.bot.loop()


async def stop():
    app.bot.stop()


def main():
    args = parse_args()
    # configs = load_config(args.config)
    configs = load_config_environ()
    app.init(token=configs['telegram_token'], apikey=configs['omdb_apikey'])
    if args.debug:
        app.bot.run(debug=True)
    else:
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(start())
        except KeyboardInterrupt:
            pass
        finally:
            loop.run_until_complete(stop())


if __name__ == '__main__':
    main()
