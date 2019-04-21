import app
import argparse
import json
import asyncio
import os


def parse_args():
    parser = argparse.ArgumentParser(description='Film Library telegram bot')
    parser.add_argument('--config', '-c',
                        help='path to your config.json file (README)')
    parser.add_argument('--debug', '-d', action='store_true',
                        help='debug mode')
    parser.add_argument('--local', '-l', action='store_true',
                        help='DEBUG ONLY, use it for testing')
    return parser.parse_args()


def load_config_file(config_path):
    with open(config_path, 'r') as f:
        s = json.load(f)
        return s


def load_config_environ():
    return {
        'token': os.environ.get('TOKEN'),
        'apikey': os.environ.get('APIKEY'),
        'db_url': os.environ.get('DATABASE_URL')
    }


async def start():
    await app.bot.loop()


async def stop():
    app.bot.stop()


def main():
    args = parse_args()
    try:
        if args.config:
            configs = load_config_file(args.config)
        else:
            configs = load_config_environ()
    except Exception:
        print('Failed to load config')
        return
    app.init(configs)
    if args.local:
        print(app.omdb.get_film('Avatar'))
        return
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
