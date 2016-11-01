import argparse
import os

import boto3
from flask import Flask, Response, request
import requests
from requests_aws4auth import AWS4Auth
from werkzeug.routing import Rule

session = boto3.session.Session()
creds = session.get_credentials()


def auth_handler():
    frozen = creds.get_frozen_credentials()
    return AWS4Auth(
        frozen.access_key,
        frozen.secret_key,
        session.region_name,
        'es',
        session_token=frozen.token,
    )

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
    request_headers = {}
    for header_name, header_value in request.headers.items():
        if header_name.lower() in whitelist_request_headers:
            request_headers[header_name] = header_value
    upstream_response = requests.request(
        request.method,
        url,
        auth=auth_handler(),
        headers=request_headers,
        data=request.data,
        stream=True,
    )
    response_headers = {}
    for header_name, header_value in upstream_response.headers.items():
        if header_name.lower() not in blacklist_response_headers:
            response_headers[header_name] = header_value

    proxy_response = Response(
        response=upstream_response.iter_content(chunk_size=None),
        status=upstream_response.status_code,
        headers=response_headers,
    )
    return proxy_response


def setup(**kwargs):
    defaults = {
        'endpoint': os.getenv('ENDPOINT', ''),
    }
    defaults.update(kwargs)
    config.update(defaults)

setup()


def main():
    parser = argparse.ArgumentParser(description='AWS ESS proxy')
    parser.add_argument('--bind-host', default='127.0.0.1')
    parser.add_argument('--bind-port', type=int, default=9200)
    parser.add_argument('--endpoint', required=True)
    args = parser.parse_args()
    setup(**vars(args))
    app.run(host=args.bind_host, port=args.bind_port, debug=True)


if __name__ == '__main__':
    main()
