"""Pingboard Authentication."""


from singer_sdk.authenticators import OAuthAuthenticator


class PingboardAuthenticator(OAuthAuthenticator):
    """Authenticator class for Pingboard."""

    @property
    def oauth_request_body(self) -> dict:
        """Define the OAuth request body for the Pingboard API."""

        return {
            'client_id': self.config["client_id"],
            'client_secret': self.config["client_secret"],
        }

    @classmethod
    def create_for_stream(cls, stream):
        auth_url = "https://app.pingboard.com/oauth/token?grant_type=client_credentials"

        return cls(
            stream=stream,
            auth_endpoint=auth_url,
        )
