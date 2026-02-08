# Terra Listens for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A Home Assistant custom integration for [Terra Listens](https://terralistens.com/) bioacoustic bird monitoring stations. Exposes real-time bird detection data, species counts, and station status as HA entities.

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click the three dots in the top right → **Custom repositories**
3. Add `https://github.com/stgarrity/ha-terra-listens` as an **Integration**
4. Search for "Terra Listens" and install
5. Restart Home Assistant

### Manual

Copy the `custom_components/terra_listens` directory into your `config/custom_components/` folder and restart Home Assistant.

## Setup

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **Terra Listens**
3. Enter your [Terra Listens portal](https://terralistens.com/portal/) email and password
4. Your station(s) will be discovered automatically

## Entities

Each Terra station appears as a device with the following entities:

| Entity | Type | Description |
|--------|------|-------------|
| Species today | Sensor | Number of unique species detected today |
| Calls today | Sensor | Total bird calls detected today |
| Top bird | Sensor | Most frequently detected species today |
| Last bird | Sensor | Most recently detected bird (with extra attributes) |
| Yard list total | Sensor | Total species ever detected (life list) |
| Streaming | Binary Sensor | Whether the station is online and streaming |

### Last Bird Attributes

The "Last bird" sensor includes extra state attributes for use in dashboards and automations:

- `scientific_name` — Scientific name of the species
- `alpha_code` — AOU alpha code (e.g., "OATI")
- `confidence` — Detection confidence (0.0–1.0)
- `image_url` — URL to a reference image of the species
- `audio_url` — URL to the audio clip of the detection
- `timestamp` — When the bird was detected
- `entity_picture` — Same as `image_url` (for Lovelace card display)

## Configuration

- **Polling interval**: 5 minutes (data is refreshed every 5 minutes)
- **Multi-station support**: If your account has multiple stations, each gets its own device

## Dependencies

This integration uses the [terra-sdk](https://github.com/stgarrity/terra-api) Python library to communicate with the Terra Listens API.

## License

MIT
