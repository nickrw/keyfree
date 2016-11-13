import argparse
import os
import logging

from flask import Flask, Response, request
import requests
from werkzeug.routing import Rule

from .auth import AutoAWS4Auth

logger = logging.getLogger(__name__)

blacklist_response_headers = (
    "connection",
    "content-length",
    "content-encoding"
)
whitelist_request_headers = (
    "content-type"
)

app = Flask(__name__)

config = {}

# Manually add rules with no method, so we will handle all methods
# Additionally, route allow both / and /* to proxy()
app.url_map.add(Rule('/', defaults={'path': ''}, endpoint='proxy'))
app.url_map.add(Rule('/<path:path>', endpoint='proxy'))


@app.endpoint('proxy')
def proxy(path):
    url = 'https://{endpoint}/{path}?{qs}'.format(
        endpoint=config['endpoint'],
        path=path,
        qs=request.query_string.decode('utf-8'),
    )
    logger.debug('Request URL {}'.format(url))
    request_headers = {}
    for header_name, header_value in request.headers.items():
        if header_name.lower() in whitelist_request_headers:
            request_headers[header_name] = header_value
    logger.debug('Request headers {}'.format(request_headers))
    upstream_response = requests.request(
        request.method,
        url,
        auth=AutoAWS4Auth('es'),
        headers=request_headers,
        data=request.data,
        stream=True,
    )
    response_headers = {}
    for header_name, header_value in upstream_response.headers.items():
        if header_name.lower() not in blacklist_response_headers:
            response_headers[header_name] = header_value
    logger.debug('Response Status {}'.format(upstream_response.status_code))
    logger.debug('Response Headers {}'.format(response_headers))

    response_generator = (
        upstream_response.iter_content(chunk_size=config['chunk_size'])
    )
    proxy_response = Response(
        response=response_generator,
        status=upstream_response.status_code,
        headers=response_headers,
        direct_passthrough=True,
    )
    return proxy_response


@app.before_first_request
def check_credentials(*args, **kwargs):
    AutoAWS4Auth('es')


def setup(**kwargs):
    def_chunk_size = 1024 * 1024
    try:
        env_chunk_size = os.getenv('CHUNK_SIZE', def_chunk_size)
        def_chunk_size = int(env_chunk_size)
    except (TypeError, ValueError):
        pass
    defaults = {
        'endpoint': os.getenv('ENDPOINT', ''),
        'chunk_size': def_chunk_size,
    }
    defaults.update(kwargs)
    if defaults['chunk_size'] == 0:
        defaults['chunk_size'] = None
    config.update(defaults)

setup()


def main():
    parser = argparse.ArgumentParser(description='AWS ESS proxy')
    parser.add_argument('--bind-host', default='127.0.0.1')
    parser.add_argument('--bind-port', type=int, default=9200)
    parser.add_argument('--endpoint', required=True)
    parser.add_argument('--chunk-size', type=int, default=1024*1024)
    args = parser.parse_args()
    setup(**vars(args))
    app.run(host=args.bind_host, port=args.bind_port, debug=True)


if __name__ == '__main__':
    main()
