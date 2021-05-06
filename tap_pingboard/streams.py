"""Stream type classes for tap-pingboard."""

from pathlib import Path

from tap_pingboard.client import PingboardStream

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class UsersStream(PingboardStream):
    """Users stream class."""

    name = "users"
    path = "/users?include=departments%2Clocations%2Cgroups%2Cstatuses&page_size=1000"
    primary_keys = ["id"]
    replication_key = "updated_at"
    response_result_key = "users"

    schema_filepath = SCHEMAS_DIR / "users.json"
