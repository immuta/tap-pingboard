# tap-pingboard

`tap-pingboard` is a Singer tap for Pingboard.

Build with the [Singer SDK](https://gitlab.com/meltano/singer-sdk).

## Installation

```bash
pipx install tap-pingboard
```

## Configuration

The following configuration options are available:

- `client_id` (required): Client Id for Pingboard
- `client_secret` (required): Client Secret for Pingboard
- `start_date` (optional): should be used on first sync to indicate how far back to grab records. Start dates should conform to the RFC3339 specification.

A full list of supported settings and capabilities for this
tap is available by running:

```bash
tap-pingboard --about
```

## Usage

You can easily run `tap-pingboard` by itself or in a pipeline using [Meltano](www.meltano.com).

### Executing the Tap Directly

```bash
tap-pingboard --version
tap-pingboard --help
tap-pingboard --config CONFIG --discover > ./catalog.json
```

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tap-pingboard/tests` subfolder and
  then run:

```bash
pip install pytest
pytest tap-pingboard/tests
```
### Singer SDK Dev Guide

See the [dev guide](../../docs/dev_guide.md) for more instructions on how to use the Singer SDK to 
develop your own taps and targets.
