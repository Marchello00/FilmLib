import app
import argparse
import json
import asyncio
import os
import app.strings as strings


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


def load_config_environ(debug=False):
    config = {
        strings.TOKEN_CONFIG: os.environ.get(strings.TOKEN_ENVIRON),
        strings.APIKEY_CONFIG: os.environ.get(strings.APIKEY_ENVIRON),
        strings.DATABASE_URL_CONFIG: os.environ.get(
            strings.DATABASE_URL_ENVIRON)
    }
    if debug:
        if os.environ.get(strings.TOKEN_ENVIRON_DEBUG):
            config[strings.TOKEN_CONFIG] = os.environ.get(
                strings.TOKEN_ENVIRON_DEBUG)
        if os.environ.get(strings.APIKEY_ENVIRON_DEBUG):
            config[strings.APIKEY_CONFIG] = os.environ.get(
                strings.APIKEY_ENVIRON_DEBUG)
        if os.environ.get(strings.DATABASE_URL_ENVIRON_DEBUG):
            config[strings.DATABASE_URL_CONFIG] = os.environ.get(
                strings.DATABASE_URL_ENVIRON_DEBUG)
    return config


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
        print(strings.FAILED_TO_LOAD_CONFIG)
        return
    app.init(configs)
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
