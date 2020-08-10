# tap-pingboard

This is a [Singer](https://singer.io) tap that produces JSON-formatted data
following the [Singer
spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

This tap:

- Pulls raw data from Immuta's [Pingboard](https://immuta.pingboard.com/home)
- Extracts the following resources:  Users
- Outputs the schema for each resource

Running the tap:

pip3 install -e .
tap-pingboard --config config.json --catalog catalog.json