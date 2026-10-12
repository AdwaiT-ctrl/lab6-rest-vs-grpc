#!/usr/bin/env python3
import argparse
import logging
from flask import Flask, jsonify, request
from werkzeug.exceptions import BadRequest, UnsupportedMediaType
from operations import decode_image, dot_product, image_dimensions

app = Flask(__name__)


@app.errorhandler(ValueError)
@app.errorhandler(BadRequest)
@app.errorhandler(UnsupportedMediaType)
def invalid_request(error):
    return jsonify(error=str(error)), 400


def json_object():
    body = request.get_json()
    if not isinstance(body, dict):
        raise ValueError("payload must be a JSON object")
    return body


@app.route('/api/add/<int(signed=True):a>/<int(signed=True):b>', methods=['GET', 'POST'])
def add(a, b):
    return jsonify(sum=a + b)


@app.route('/api/rawimage', methods=['POST'])
def rawimage():
    return jsonify(image_dimensions(request.get_data()))


@app.route('/api/dotproduct', methods=['POST'])
def dotproduct():
    body = json_object()
    return jsonify(dotproduct=dot_product(body.get('a'), body.get('b')))


@app.route('/api/jsonimage', methods=['POST'])
def jsonimage():
    return jsonify(image_dimensions(decode_image(json_object().get('image'))))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Lab 6 REST server')
    parser.add_argument('-p', '--port', type=int, default=5000)
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('-d', '--debug', action='store_true')
    args = parser.parse_args()
    logging.getLogger('werkzeug').setLevel(logging.INFO if args.debug else logging.ERROR)
    app.run(host=args.host, port=args.port, threaded=True, use_reloader=False)
