
import boto3
import httpretty
import pytest
import requests

from .. import auth
from .util import assert_aws4auth_in_headers


@pytest.fixture(autouse=True)
def setup(monkeypatch):
    monkeypatch.setenv('AWS_ACCESS_KEY_ID', 'TESTKEY')
    monkeypatch.setenv('AWS_SECRET_ACCESS_KEY', 'TESTSECRET')
    monkeypatch.setenv('AWS_DEFAULT_REGION', 'eu-west-1')
    monkeypatch.setattr(auth, 'session', boto3.session.Session())
    monkeypatch.setattr(auth, 'creds', auth.session.get_credentials())


def test_frozen_credentials():
    creds = auth.get_frozen_credentials()
    assert creds is not None
    assert creds.get('access_key') == 'TESTKEY'
    assert creds.get('secret_key') == 'TESTSECRET'
    assert creds.get('region_name') == 'eu-west-1'


def test_autoaws4auth_keys():
    aa = auth.AutoAWS4Auth('es')
    assert aa.access_id == 'TESTKEY'
    assert aa.service == 'es'
    assert aa.signing_key.secret_key == 'TESTSECRET'


@httpretty.activate
def test_autoaws4auth_signs():
    httpretty.register_uri(
        httpretty.GET,
        'https://example.com/',
        body='response',
    )
    res = requests.get('https://example.com/', auth=auth.AutoAWS4Auth('es'))
    assert_aws4auth_in_headers(res.request.headers)
