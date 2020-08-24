#!/usr/bin/env python3
import os
import requests
import json
import singer
from singer import utils, metadata
from singer.catalog import Catalog, CatalogEntry
from singer.schema import Schema


REQUIRED_CONFIG_KEYS = ["start_date", "client_id", "client_secret"]
LOGGER = singer.get_logger()


def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


def load_schemas():
    """ Load schemas from schemas folder """
    schemas = {}
    for filename in os.listdir(get_abs_path("schemas")):
        path = get_abs_path("schemas") + "/" + filename
        file_raw = filename.replace(".json", "")
        with open(path) as file:
            schemas[file_raw] = Schema.from_dict(json.load(file))
    return schemas


def discover():
    raw_schemas = load_schemas()
    streams = []
    for stream_id, schema in raw_schemas.items():
        # TODO: populate any metadata and stream's key properties here..
        stream_metadata = [{"breadcrumb": [], "metadata": {"selected": True}}]
        key_properties = ["id"]
        streams.append(
            CatalogEntry(
                tap_stream_id=stream_id,
                stream=stream_id,
                schema=schema,
                key_properties=key_properties,
                metadata=stream_metadata,
                replication_key="updated_at",
                is_view=None,
                database=None,
                table=None,
                row_count=None,
                stream_alias=None,
                replication_method=None,
            )
        )
    return Catalog(streams)


def sync(config, state, catalog):
    """ Sync data from tap source """

    # URL for doing a POST to retrieve a Pingboard token to use when retrieving Pingboard data
    #  https://app.pingboard.com/oauth/token?grant_type=client_credentials
    # Body to be posted:
    #  'client_id=' + client_id + '&client_secret=' + client_secret

    # curl command to get token for testing
    #  curl -d "client_id=CLIENT_ID_HERE&client_secret=CLIENT_SECRET_HERE" https://app.pingboard.com/oauth/token?grant_type=client_credentials

    # URL for retrieving Pingboard data for employees, departments, locations, groups, and statuses
    #  https://app.pingboard.com/api/v2/users?include=departments%2Clocations%2Cgroups%2Cstatuses&page_size=3000

    # Get the Pingboard token to use when retreiving Pingboard data
    response = requests.post(
        "https://app.pingboard.com/oauth/token?grant_type=client_credentials",
        data={
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
        },
    )
    auth_token = json.loads(response.text)["access_token"]

    # Loop over selected streams in catalog
    for stream in catalog.get_selected_streams(state):
        LOGGER.info("Syncing stream:" + stream.tap_stream_id)

        if stream.tap_stream_id == "users":

            bookmark_column = stream.replication_key
            is_sorted = True  # TODO: indicate whether data is sorted ascending on bookmark value

            singer.write_schema(
                stream_name=stream.tap_stream_id,
                schema=stream.schema.to_dict(),
                key_properties=stream.key_properties,
            )

            # curl command to retrieve data for testing
            #  curl -H "Authorization: Bearer TOKEN_HERE" -output response.json https://app.pingboard.com/api/v2/users?include=departments%2Clocations%2Cgroups%2Cstatuses&page_size=3000
            # response schema:
            #    properties: {
            #      users: { type: 'array', items: [Object] },
            #      meta: { type: 'object', properties: [Object] },
            #      links: { type: 'object', properties: [Object] },
            #      linked: { type: 'object', properties: [Object] }
            #   }
            response = requests.get(
                "https://app.pingboard.com/api/v2/users?include=departments%2Clocations%2Cgroups%2Cstatuses&page_size=3000",
                headers={"Authorization": "Bearer " + auth_token},
            )
            response = json.loads(response.text)

            linked = response["linked"]

            # create dictionary of departments
            departments = {}
            for department in linked["departments"]:
                departments[str(department["id"])] = department["name"]

            # create dictionary of locations
            locations = {}
            for location in linked["locations"]:
                locations[str(location["id"])] = location["name"]

            for user in response["users"]:

                record = {
                    "id": user["id"],
                    "created_at": user["created_at"],
                    "updated_at": user["updated_at"],
                    "first_name": user["first_name"],
                    "last_name": user["last_name"],
                    "nickname": user["nickname"],
                    "start_date": user["start_date"],
                    "email": user["email"],
                    "job_title": user["job_title"],
                    "reports_to_id": str(user["reports_to_id"]),
                    "bio": user["bio"],
                    "phone": user["phone"],
                    "department": None,
                    "location": None,
                }

                if "departments" in user["links"]:
                    record["department"] = departments[user["links"]["departments"][0]]

                if "locations" in user["links"]:
                    record["location"] = locations[user["links"]["locations"][0]]

                singer.write_records(stream.tap_stream_id, [record])

    return


@utils.handle_top_exception(LOGGER)
def main():
    # Parse command line arguments
    args = utils.parse_args(REQUIRED_CONFIG_KEYS)

    # If discover flag was passed, run discovery mode and dump output to stdout
    if args.discover:
        catalog = discover()
        catalog.dump()
    # Otherwise run in sync mode
    else:
        if args.catalog:
            catalog = args.catalog
        else:
            catalog = discover()
        sync(args.config, args.state, catalog)


if __name__ == "__main__":
    main()
