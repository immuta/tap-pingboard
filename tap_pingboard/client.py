"""REST client handling, including PingboardStream base class."""

import requests
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from singer_sdk.streams import RESTStream
from tap_pingboard.auth import PingboardAuthenticator


SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class PingboardStream(RESTStream):
    """Pingboard stream class."""

    url_base = "https://app.pingboard.com/api/v2"

    @property
    def authenticator(self) -> PingboardAuthenticator:
        """Return a new authenticator object."""
        return PingboardAuthenticator.create_for_stream(self)

    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any] = None
    ) -> Optional[Any]:
        """Return a token for identifying next page or None if no more pages."""
        # Decide on whether to use pagination or skip because of small amount of users
        next_page_token = response.headers.get("X-Next-Page", None)
        if next_page_token:
            self.logger.info(f"Next page token retrieved: {next_page_token}")
        return next_page_token

    def get_url_params(
        self, partition: Optional[dict], next_page_token: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        # Decide whether to hardcode url parameters in api url or to codify them there
        params: dict = {}
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key
        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        # Figure out including non users element information
        resp_json = response.json()

        if self.response_result_key:
            resp_json = resp_json[self.response_result_key]

        if isinstance(resp_json, dict):
            yield resp_json
        else:
            for row in resp_json:
                yield row

    def post_process(self, row: dict, partition: Optional[dict] = None) -> dict:
        """As needed, append or transform raw data to match expected structure."""
        # Decide whether to pass along links/departments/locations to map in values here
        return row
