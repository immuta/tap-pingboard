"""Pingboard tap class."""

from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_pingboard.streams import (
    UsersStream,
    GroupsStream,
)

STREAM_TYPES = [
    UsersStream,
    GroupsStream,
]


class TapPingboard(Tap):
    """Pingboard tap class."""

    name = "tap-pingboard"

    config_jsonschema = th.PropertiesList(
        th.Property("start_date", th.DateTimeType),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]


# CLI Execution:

cli = TapPingboard.cli
