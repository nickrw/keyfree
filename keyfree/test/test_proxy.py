import json

import boto3
import httpretty
import pytest

from .. import proxy, auth
from ..proxy import app
from .util import assert_aws4auth_in_headers, downcase_keys


def mock_response_gen(req, uri, headers):
    """An httpretty response callback returning json request headers"""
    return (200, headers, json.dumps(dict(req.headers)))


@pytest.fixture(scope="class")
def client():
    return app.test_client()


@pytest.mark.httpretty
class TestProxy(object):

    @pytest.fixture(autouse=True)
    def setup_env(self, monkeypatch):
        monkeypatch.setenv('AWS_ACCESS_KEY_ID', 'TESTKEY')
        monkeypatch.setenv('AWS_SECRET_ACCESS_KEY', 'TESTSECRET')
        monkeypatch.setenv('AWS_DEFAULT_REGION', 'eu-west-1')
        monkeypatch.setenv('ENDPOINT', 'example.com')
        monkeypatch.setattr(auth, 'session', boto3.session.Session())
        monkeypatch.setattr(auth, 'creds', auth.session.get_credentials())
        proxy.setup()
        httpretty.register_uri(
            httpretty.GET,
            'https://example.com/',
            body=mock_response_gen,
            streaming=True,
        )

    def test_config(self):
        assert proxy.config.get('endpoint') == 'example.com'

    def test_auth_headers_present(self, client):
        res = client.get('/')
        request_headers = json.loads(res.data.decode('utf8'))
        assert_aws4auth_in_headers(request_headers)

    def test_content_type_request_header(self, client):
        res = client.get('/', headers={'Content-Type': 'application/json'})
        request_headers = downcase_keys(json.loads(res.data.decode('utf8')))
        assert request_headers.get('content-type') == 'application/json'

    def test_custom_request_header_not_passed_through(self, client):
        res = client.get('/', headers={'X-Test-Header': 'foo'})
        request_headers = downcase_keys(json.loads(res.data.decode('utf8')))
        assert 'x-test-header' not in request_headers

    def test_response_headers_passed_through(self, client):
        def resp(req, uri, headers):
            return (200, {'x-header-test': 'pass'}, 'Header test')
        httpretty.register_uri(
            httpretty.GET,
            'https://example.com/custom_headers',
            body=resp,
            streaming=True,
        )
        res = client.get('/custom_headers')
        assert res.headers.get('x-header-test') == 'pass'

    @pytest.mark.parametrize("response_code", (200, 201, 404, 500))
    def test_response_code_passed_through(self, client, response_code):
        def resp(req, uri, headers):
            return (response_code, headers, 'Test {}'.format(response_code))
        httpretty.register_uri(
            httpretty.GET,
            'https://example.com/{}'.format(response_code),
            body=resp,
            streaming=True,
        )
        res = client.get('/{}'.format(response_code))
        assert res.status_code == response_code
        assert res.data.decode('utf8') == 'Test {}'.format(response_code)
