#!/usr/bin/env python3
import argparse
from service.server import create_app
import uvicorn

def parse_args():
    parser = argparse.ArgumentParser(description='AI Automation System')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind the server to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind the server to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    return parser.parse_args()

def main():
    args = parse_args()
    app = create_app()
    uvicorn.run(app, host=args.host, port=args.port)

if __name__ == '__main__':
    main()
