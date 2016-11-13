
import boto3
from requests_aws4auth import AWS4Auth

session = boto3.session.Session()
creds = session.get_credentials()


class CredentialError(Exception):
    pass


def get_frozen_credentials():
    if creds:
        frozen = creds.get_frozen_credentials()._asdict()
        frozen['region_name'] = session.region_name
        return frozen


class AutoAWS4Auth(AWS4Auth):

    def __init__(self, aws_service):
        frozen = get_frozen_credentials()
        if not frozen:
            raise CredentialError("boto failed to discover access keys")
        if not frozen.get('region_name'):
            raise CredentialError("boto failed to discover region")
        super(AutoAWS4Auth, self).__init__(
            frozen['access_key'],
            frozen['secret_key'],
            frozen['region_name'],
            aws_service,
            session_token=frozen['token'],
        )
