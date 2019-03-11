"""Google login authentication using OAuth 2.0.

Logging into Hangouts using OAuth2 requires a private scope only whitelisted
for certain clients. This module uses the client ID and secret from iOS, so it
will appear to Google to be an iOS device. Access can be revoked from this
page:
    https://security.google.com/settings/security/activity

This module should avoid logging any sensitive login information.

This module may be tested by invoking it directly:
    python -m hangups.auth
"""

import logging
import platform
import urllib.parse

import requests

from hangups import version

logger = logging.getLogger(__name__)
# Set the logging level for requests to at least INFO, since the DEBUG level
# will log sensitive data:
if logging.getLogger('requests').isEnabledFor(logging.DEBUG):
    logging.getLogger('requests').setLevel(logging.INFO)

OAUTH2_CLIENT_ID = '936475272427.apps.googleusercontent.com'
OAUTH2_CLIENT_SECRET = 'KWsJlkaMn1jGLxQpWxMnOox-'
OAUTH2_SCOPES = [
    'https://www.google.com/accounts/OAuthLogin',
    'https://www.googleapis.com/auth/userinfo.email',
]
# Note that '+' separating scopes must not be escaped by urlencode
OAUTH2_LOGIN_URL = (
    'https://accounts.google.com/o/oauth2/programmatic_auth?{}'.format(
        urllib.parse.urlencode(dict(
            scope='+'.join(OAUTH2_SCOPES),
            client_id=OAUTH2_CLIENT_ID,
            device_name='hangups',
        ), safe='+')
    )
)
OAUTH2_TOKEN_REQUEST_URL = 'https://accounts.google.com/o/oauth2/token'
USER_AGENT = 'hangups/{} ({} {})'.format(
    version.__version__, platform.system(), platform.machine()
)

MANUAL_LOGIN_INSTRUCTIONS = '''
To sign in with your Google account:

    1) Open the URL provided below in your browser.

    2) Log into your Google account normally.

    3) You should be redirected to a loading screen. Copy the `oauth_code`
    cookie value set by this page and paste it here.

To obtain the cookie value using Chrome or Firefox:

    1) Press F12 to open developer tools.

    2) Select the "Application" (Chrome) or "Storage" (Firefox) tab.

    3) In the sidebar, expand "Cookies" and select
    `https://accounts.google.com`.

    4) In the cookie list, double click on the value for the `oauth_code`
    cookie to select it, and copy the value.

{}
'''.format(OAUTH2_LOGIN_URL)


class GoogleAuthError(Exception):
    """A Google authentication request failed."""


class CredentialsPrompt:
    """Callbacks for prompting user for their Google account credentials.

    This implementation prompts the user in a terminal using standard in/out.
    """

    @staticmethod
    def get_authorization_code():
        """Prompt for authorization code.

        Returns:
            str: Google account authorization code.
        """
        print(MANUAL_LOGIN_INSTRUCTIONS)
        return input('Authorization code: ')


class RefreshTokenCache:
    """File-based cache for refresh token.

    Args:
        filename (str): Path to file where refresh token will be cached.
    """

    def __init__(self, filename):
        self._filename = filename

    def get(self):
        """Get cached refresh token.

        Returns:
            Cached refresh token, or ``None`` on failure.
        """
        logger.info(
            'Loading refresh_token from %s', repr(self._filename)
        )
        try:
            with open(self._filename) as f:
                return f.read()
        except IOError as e:
            logger.info('Failed to load refresh_token: %s', e)

    def set(self, refresh_token):
        """Cache a refresh token, ignoring any failure.

        Args:
            refresh_token (str): Refresh token to cache.
        """
        logger.info('Saving refresh_token to %s', repr(self._filename))
        try:
            with open(self._filename, 'w') as f:
                f.write(refresh_token)
        except IOError as e:
            logger.warning('Failed to save refresh_token: %s', e)


def get_auth(credentials_prompt, refresh_token_cache, **_kwargs):
    """Authenticate with Google.

    Args:
        refresh_token_cache (RefreshTokenCache): Cache to use so subsequent
            logins may not require credentials.
        credentials_prompt (CredentialsPrompt): Prompt to use if credentials
            are required to log in.

    Returns:
        dict: Google session cookies.

    Raises:
        GoogleAuthError: If authentication with Google fails.
    """
    with requests.Session() as session:
        session.headers = {'user-agent': USER_AGENT}

        try:
            logger.info('Authenticating with refresh token')
            refresh_token = refresh_token_cache.get()
            if refresh_token is None:
                raise GoogleAuthError("Refresh token not found")
            access_token = _auth_with_refresh_token(session, refresh_token)
        except GoogleAuthError as e:
            logger.info('Failed to authenticate using refresh token: %s', e)
            logger.info('Authenticating with credentials')
            authorization_code = (
                credentials_prompt.get_authorization_code()
            )
            access_token, refresh_token = _auth_with_code(
                session, authorization_code
            )
            refresh_token_cache.set(refresh_token)

        logger.info('Authentication successful')
        return _get_session_cookies(session, access_token)


def get_auth_stdin(refresh_token_filename, **_kwargs):
    """Simple wrapper for :func:`get_auth` that prompts the user using stdin.

    Args:
        refresh_token_filename (str): Path to file where refresh token will be
            cached.

    Raises:
        GoogleAuthError: If authentication with Google fails.
    """
    refresh_token_cache = RefreshTokenCache(refresh_token_filename)
    return get_auth(
        CredentialsPrompt(), refresh_token_cache
    )


def _auth_with_refresh_token(session, refresh_token):
    """Authenticate using OAuth refresh token.

    Raises GoogleAuthError if authentication fails.

    Returns access token string.
    """
    # Make a token request.
    token_request_data = {
        'client_id': OAUTH2_CLIENT_ID,
        'client_secret': OAUTH2_CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
    }
    res = _make_token_request(session, token_request_data)
    return res['access_token']


def _auth_with_code(session, authorization_code):
    """Authenticate using OAuth authorization code.

    Raises GoogleAuthError if authentication fails.

    Returns access token string and refresh token string.
    """
    # Make a token request.
    token_request_data = {
        'client_id': OAUTH2_CLIENT_ID,
        'client_secret': OAUTH2_CLIENT_SECRET,
        'code': authorization_code,
        'grant_type': 'authorization_code',
        'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
    }
    res = _make_token_request(session, token_request_data)
    return res['access_token'], res['refresh_token']


def _make_token_request(session, token_request_data):
    """Make OAuth token request.

    Raises GoogleAuthError if authentication fails.

    Returns dict response.
    """
    try:
        r = session.post(OAUTH2_TOKEN_REQUEST_URL, data=token_request_data)
        r.raise_for_status()
    except requests.RequestException as e:
        raise GoogleAuthError('Token request failed: {}'.format(e))
    else:
        res = r.json()
        # If an error occurred, a key 'error' will contain an error code.
        if 'error' in res:
            raise GoogleAuthError(
                'Token request error: {!r}'.format(res['error'])
            )
        return res


def _get_session_cookies(session, access_token):
    """Use the access token to get session cookies.

    Raises GoogleAuthError if session cookies could not be loaded.

    Returns dict of cookies.
    """
    headers = {'Authorization': 'Bearer {}'.format(access_token)}

    try:
        r = session.get(('https://accounts.google.com/accounts/OAuthLogin'
                         '?source=hangups&issueuberauth=1'), headers=headers)
        r.raise_for_status()
    except requests.RequestException as e:
        raise GoogleAuthError('OAuthLogin request failed: {}'.format(e))
    uberauth = r.text

    try:
        r = session.get(('https://accounts.google.com/MergeSession?'
                         'service=mail&'
                         'continue=http://www.google.com&uberauth={}')
                        .format(uberauth), headers=headers)
        r.raise_for_status()
    except requests.RequestException as e:
        raise GoogleAuthError('MergeSession request failed: {}'.format(e))

    cookies = session.cookies.get_dict(domain='.google.com')
    if cookies == {}:
        raise GoogleAuthError('Failed to find session cookies')
    return cookies


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    print(get_auth_stdin('refresh_token.txt'))
