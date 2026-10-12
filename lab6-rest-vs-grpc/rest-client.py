#!/usr/bin/env python3
import json
import requests
from benchmark import arguments, measure, payload


def main():
    args = arguments('REST', 5000)
    data, expected = payload(args)
    address = f'http://{args.host}:{args.port}/api/'
    if args.cmd == 'add':
        url = address + f'add/{data["a"]}/{data["b"]}'
        body, headers = b'', {}
    elif args.cmd == 'rawimage':
        url = address + args.cmd
        body, headers = data, {'Content-Type': 'image/jpeg'}
    else:
        url = address + args.cmd
        body = json.dumps(data).encode('utf8')
        headers = {'Content-Type': 'application/json'}

    def call():
        # A fresh Session per call matches the assignment's REST connection model.
        with requests.Session() as session:
            session.trust_env = False
            response = session.post(url, data=body, headers=headers, timeout=args.timeout)
            response.raise_for_status()
            return response.json()

    measure(args, 'REST', call, expected, len(body))


if __name__ == '__main__':
    main()
