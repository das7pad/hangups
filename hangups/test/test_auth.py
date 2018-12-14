import json

import httpretty
import pytest

from hangups import auth


# pylint: disable=redefined-outer-name


class FakeCredentialsPrompt(auth.CredentialsPrompt):

    def __init__(self):
        self.was_prompted = False

    def get_authorization_code(self):
        self.was_prompted = True
        return 'auth_code'


@pytest.fixture
def credentials_prompt():
    return FakeCredentialsPrompt()


class FakeRefreshTokenCache(auth.RefreshTokenCache):

    def __init__(self):
        super().__init__('fake_filename')
        self._refresh_token = None

    def get(self):
        return self._refresh_token

    def set(self, refresh_token):
        self._refresh_token = refresh_token


@pytest.fixture
def refresh_token_cache():
    return FakeRefreshTokenCache()


def mock_google():
    """Set up httpretty to mock authentication requests.

    This simplifies the sequence of redirects and doesn't make any assertions
    about the requests.
    """
    httpretty.HTTPretty.allow_net_connect = False
    httpretty.register_uri(
        httpretty.POST, 'https://accounts.google.com/o/oauth2/token',
        body=json.dumps(dict(access_token='access', refresh_token='refresh')),
        content_type='application/json'
    )
    httpretty.register_uri(
        httpretty.GET, 'https://accounts.google.com/accounts/OAuthLogin',
        body='uberauth', content_type='text/html'
    )
    httpretty.register_uri(
        httpretty.GET, 'https://accounts.google.com/MergeSession',
        body='uberauth', content_type='text/html',
        set_cookie='session=foo; Domain=.google.com'
    )


@httpretty.activate
def test_refresh_token(credentials_prompt, refresh_token_cache):
    mock_google()
    refresh_token_cache.set('foo')
    cookies = auth.get_auth(credentials_prompt, refresh_token_cache)
    assert not credentials_prompt.was_prompted
    assert refresh_token_cache.get() is not None
    assert cookies['session'] == 'foo'


@httpretty.activate
def test_manual_login(credentials_prompt, refresh_token_cache):
    mock_google()
    cookies = auth.get_auth(
        credentials_prompt, refresh_token_cache, manual_login=True
    )
    assert credentials_prompt.was_prompted
    assert refresh_token_cache.get() is not None
    assert cookies['session'] == 'foo'
