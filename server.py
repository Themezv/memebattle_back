# aiohttp_example.py
import argparse
from aiohttp import web
from app.gunicorn import app


parser = argparse.ArgumentParser(description="aiohttp server example")
parser.add_argument('--path')
parser.add_argument('--port')


if __name__ == '__main__':

    args = parser.parse_args()
    web.run_app(app, path=args.path, port=args.port)