import app
import argparse
import json
import asyncio


def parse_args():
    parser = argparse.ArgumentParser(description='Film Library telegram bot')
    parser.add_argument('--config', '-c', default='config.json',
                        help='path to your config.json file (README)')
    parser.add_argument('--debug', '-d', action='store_true',
                        help='debug mode')
    return parser.parse_args()


def load_config(config_path):
    with open(config_path, 'r') as f:
        s = json.load(f)
        return s


async def start():
    await app.bot.loop()


async def stop():
    app.bot.stop()


def main():
    args = parse_args()
    configs = load_config(args.config)
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
