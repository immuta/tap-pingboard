"""Stream type classes for tap-pingboard."""

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

    def get_url_params(
        self, partition: Optional[dict], next_page_token: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}

        params["include"] = ",".join(["departments", "locations"])
        params["page_size"] = "3000"

        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        resp_json = response.json()

        if self.response_result_key:
            for key in self.response_result_key.split("."):
                if isinstance(resp_json, dict) and key in resp_json:
                    resp_json = resp_json[key]

        if isinstance(resp_json, dict):
            yield resp_json
        else:
            for row in resp_json:
                yield row

    def post_process(self, row: dict, partition: Optional[dict] = None) -> dict:
        """As needed, append or transform raw data to match expected structure."""

        return row


class UsersStream(PingboardStream):
    """Users stream class."""

    name = "users"
    path = "/users"
    primary_keys = ["id"]
    replication_key = "updated_at"
    response_result_key = "users"

    schema_filepath = SCHEMAS_DIR / "users.json"


class DepartmentsStream(PingboardStream):
    """Departments stream class."""

    name = "departments"
    path = "/users"
    primary_keys = ["id"]
    replication_key = "updated_at"
    response_result_key = "linked.departments"

    schema_filepath = SCHEMAS_DIR / "departments.json"


class LocationsStream(PingboardStream):
    """Locations stream class."""

    name = "locations"
    path = "/users"
    primary_keys = ["id"]
    replication_key = "updated_at"
    response_result_key = "linked.locations"

    schema_filepath = SCHEMAS_DIR / "locations.json"
