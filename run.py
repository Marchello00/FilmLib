import typing as tp
import os
import json
import argparse
import app
import app.strings as strings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Film Library telegram bot')
    parser.add_argument('--config', '-c',
                        help='path to your config.json file (README)')
    parser.add_argument('--debug', '-d', action='store_true',
                        help='debug mode')
    parser.add_argument('--local', '-l', action='store_true',
                        help='DEBUG ONLY, use it for testing')
    return parser.parse_args()


def load_config_file(config_path: str) -> tp.Dict[str, str]:
    with open(config_path, 'r') as config_file:
        return json.load(config_file)


def _not_none(arg: tp.Optional[str]) -> str:
    if arg is None:
        raise RuntimeError('config variable is missing')
    return arg


def load_config_environ(debug: bool = False) -> tp.Dict[str, str]:
    config: tp.Dict[str, str] = {
        strings.TOKEN_CONFIG: _not_none(os.environ.get(strings.TOKEN_ENVIRON)),
        strings.APIKEY_CONFIG: _not_none(
            os.environ.get(strings.APIKEY_ENVIRON)),
        strings.DATABASE_URL_CONFIG: _not_none(os.environ.get(
            strings.DATABASE_URL_ENVIRON))
    }
    if debug:
        if os.environ.get(strings.TOKEN_ENVIRON_DEBUG):
            config[strings.TOKEN_CONFIG] = _not_none(os.environ.get(
                strings.TOKEN_ENVIRON_DEBUG))
        if os.environ.get(strings.APIKEY_ENVIRON_DEBUG):
            config[strings.APIKEY_CONFIG] = _not_none(os.environ.get(
                strings.APIKEY_ENVIRON_DEBUG))
        if os.environ.get(strings.DATABASE_URL_ENVIRON_DEBUG):
            config[strings.DATABASE_URL_CONFIG] = _not_none(os.environ.get(
                strings.DATABASE_URL_ENVIRON_DEBUG))
    return config


def main() -> None:
    args = parse_args()
    try:
        if args.config:
            configs = load_config_file(args.config)
        else:
            configs = load_config_environ(args.debug)
    except Exception:
        print(strings.FAILED_TO_LOAD_CONFIG)
        return
    app.init(configs, debug=args.debug)
    app.run()


if __name__ == '__main__':
    main()
