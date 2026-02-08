"""Tests for Terra Listens sensor and binary sensor entities."""

import pytest

from terra_sdk.models import BirdDetection, Station, StationStats

from custom_components.terra_listens.coordinator import TerraStationData
from custom_components.terra_listens.sensor import (
    _calls_today,
    _last_bird,
    _last_bird_attrs,
    _species_today,
    _top_bird,
    _yard_list_total,
)

MOCK_STATION = Station(
    station_id="DEV1",
    alias="Oxbow",
    last_heard="2026-02-08 01:00:00",
    streaming="1",
    lat="37.93",
    lon="-120.27",
)

MOCK_STATS = StationStats(
    uniqueSpecies="8",
    callCount="120",
    topBird="Acorn Woodpecker",
    topBirdCount="25",
    topTime="07:00",
    topTimeCount="10",
)

MOCK_BIRD = BirdDetection(
    id="det1",
    commonName="California Towhee",
    scientificName="Melozone crissalis",
    alphacode="CALT",
    speciesConfidence="0.78",
    stamp="2026-02-08 07:45:00",
    epoch="1770535500",
    audioURL="https://example.com/audio.flac",
    Image_url="https://example.com/CALT.jpg",
    notPredicted="0",
    complete="1",
    anthro="0",
)


def _make_station_data(
    stats=MOCK_STATS, birds=None, yard_count=30
) -> TerraStationData:
    return TerraStationData(
        station=MOCK_STATION,
        stats=stats,
        latest_birds=birds if birds is not None else [MOCK_BIRD],
        yard_list_count=yard_count,
    )


def test_species_today():
    data = _make_station_data()
    assert _species_today(data) == 8


def test_species_today_no_stats():
    data = _make_station_data(stats=None)
    assert _species_today(data) is None


def test_calls_today():
    data = _make_station_data()
    assert _calls_today(data) == 120


def test_top_bird():
    data = _make_station_data()
    assert _top_bird(data) == "Acorn Woodpecker"


def test_last_bird():
    data = _make_station_data()
    assert _last_bird(data) == "California Towhee"


def test_last_bird_no_detections():
    data = _make_station_data(birds=[])
    assert _last_bird(data) is None


def test_last_bird_attrs():
    data = _make_station_data()
    attrs = _last_bird_attrs(data)
    assert attrs["scientific_name"] == "Melozone crissalis"
    assert attrs["alpha_code"] == "CALT"
    assert attrs["confidence"] == 0.78
    assert attrs["image_url"] == "https://example.com/CALT.jpg"
    assert attrs["audio_url"] == "https://example.com/audio.flac"
    assert "entity_picture" in attrs


def test_last_bird_attrs_empty():
    data = _make_station_data(birds=[])
    assert _last_bird_attrs(data) == {}


def test_yard_list_total():
    data = _make_station_data(yard_count=47)
    assert _yard_list_total(data) == 47


def test_yard_list_total_zero():
    data = _make_station_data(yard_count=0)
    assert _yard_list_total(data) == 0
