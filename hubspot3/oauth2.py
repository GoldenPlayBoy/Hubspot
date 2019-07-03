"""
hubspot OAuth2 api
"""
from urllib.parse import urlencode

from hubspot3 import logging_helper
from hubspot3.base import BaseClient

OAUTH2_API_VERSION = "1"


class OAuth2Client(BaseClient):
    """
    The hubspot3 OAuth2 client uses the _make_request method to call the
    API for data.  It returns a python object translated from the json returned
    """

    def __init__(self, *args, **kwargs):
        """initialize a contacts client"""
        # Since this client is used to generate tokens for authentication, it does not require
        # authentication itself.
        kwargs["disable_auth"] = True
        super(OAuth2Client, self).__init__(*args, **kwargs)
        self.log = logging_helper.get_log("hubspot3.oauth2")
        self.options["content_type"] = "application/x-www-form-urlencoded"
        # Make sure that certain credentials that wouldn't be used anyway are not set. Not having
        # an access token will also make sure that the `_call_raw` implementation does not try to
        # refresh access tokens on its own.
        self.api_key = None
        self.access_token = None

    def _get_path(self, subpath):
        return "oauth/v{}/{}".format(OAUTH2_API_VERSION, subpath)

    def get_tokens(
        self,
        authorization_code: str,
        redirect_uri: str,
        client_id: str = None,
        client_secret: str = None,
        **options
    ):
        """
        Request an initial token pair using the provided credentials.

        If any of the optional parameters are not provided, their value will be read from the
        corresponding attributes on this client.
        If the value for all optional parameters had to be read from the attributes, the refresh
        token returned from the API will be stored on this client to allow for further
        `refresh_token` calls without having to provide the refresh token.
        """
        data = {
            "grant_type": "authorization_code",
            "client_id": client_id or self.client_id,
            "client_secret": client_secret or self.client_secret,
            "redirect_uri": redirect_uri,
            "code": authorization_code,
        }
        result = self._call("token", method="POST", data=urlencode(data), **options)

        if not client_id and not client_secret:
            self.refresh_token = result["refresh_token"]
        return result

    def refresh_tokens(
        self,
        client_id: str = None,
        client_secret: str = None,
        refresh_token: str = None,
        **options
    ):
        """
        Request a new token pair using the provided access token and credentials.

        If any of the optional parameters are not provided, their value will be read from the
        corresponding attributes on this client.
        If the value for all optional parameters had to be read from the attributes, the refresh
        token returned from the API will be stored on this client to allow for further
        `refresh_token` calls without having to provide the refresh token.
        """
        data = {
            "grant_type": "refresh_token",
            "client_id": client_id or self.client_id,
            "client_secret": client_secret or self.client_secret,
            "refresh_token": refresh_token or self.refresh_token,
        }
        result = self._call("token", method="POST", data=urlencode(data), **options)

        if not client_id and not client_secret and not refresh_token:
            self.refresh_token = result["refresh_token"]
        return result
