def downcase_keys(dict_):
    return {k.lower(): v for k, v in dict_.items()}


def assert_aws4auth_in_headers(headers):
    lc_headers = downcase_keys(headers)
    assert 'authorization' in lc_headers
    assert 'x-amz-date' in lc_headers
    assert 'x-amz-content-sha256' in lc_headers
    auth_header = lc_headers.get('authorization')
    assert auth_header
    assert 'TESTKEY' in auth_header
    assert 'eu-west-1' in auth_header
    assert 'Signature=' in auth_header
