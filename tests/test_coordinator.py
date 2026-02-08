"""Tests for Terra Listens coordinator."""

from unittest.mock import MagicMock, patch

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed

from terra_sdk.exceptions import TerraError
from terra_sdk.models import BirdDetection, Station, StationStats, YardListEntry

from custom_components.terra_listens.coordinator import (
    TerraData,
    TerraDataUpdateCoordinator,
    TerraStationData,
)

MOCK_STATION = Station(
    station_id="DEVICE123",
    alias="Oxbow",
    last_heard="2026-02-08 01:00:00",
    streaming="1",
    lat="37.93",
    lon="-120.27",
    version="3.18",
    serial="SN001",
)

MOCK_STATS = StationStats(
    uniqueSpecies="12",
    callCount="345",
    topBird="Oak Titmouse",
    topBirdCount="42",
    topTime="08:00",
    topTimeCount="15",
)

MOCK_BIRD = BirdDetection(
    id="abc123",
    commonName="Oak Titmouse",
    scientificName="Baeolophus inornatus",
    alphacode="OATI",
    speciesConfidence="0.92",
    stamp="2026-02-08 07:30:00",
    epoch="1770534600",
    audioURL="https://example.com/audio.flac",
    Image_url="https://example.com/OATI.jpg",
    notPredicted="0",
    complete="1",
    anthro="0",
)


def _make_mock_client():
    """Create a mock TerraClient with standard responses."""
    client = MagicMock()
    client.get_devices.return_value = [MOCK_STATION]
    client.get_stats.return_value = MOCK_STATS
    client.get_latest_birds.return_value = [MOCK_BIRD]
    client.get_yard_list.return_value = [MagicMock()] * 47
    return client


def test_fetch_data_success():
    """Test that _fetch_data returns proper TerraData."""
    client = _make_mock_client()
    coordinator = TerraDataUpdateCoordinator.__new__(TerraDataUpdateCoordinator)
    coordinator.client = client

    data = coordinator._fetch_data()

    assert isinstance(data, TerraData)
    assert "DEVICE123" in data.stations
    sd = data.stations["DEVICE123"]
    assert sd.station.alias == "Oxbow"
    assert sd.stats.unique_species == 12
    assert sd.stats.call_count == 345
    assert len(sd.latest_birds) == 1
    assert sd.latest_birds[0].common_name == "Oak Titmouse"
    assert sd.yard_list_count == 47


def test_fetch_data_stats_failure():
    """Test that stats failure is handled gracefully."""
    client = _make_mock_client()
    client.get_stats.side_effect = TerraError("stats down")
    coordinator = TerraDataUpdateCoordinator.__new__(TerraDataUpdateCoordinator)
    coordinator.client = client

    data = coordinator._fetch_data()
    sd = data.stations["DEVICE123"]
    assert sd.stats is None
    assert len(sd.latest_birds) == 1


def test_fetch_data_birds_failure():
    """Test that bird fetch failure is handled gracefully."""
    client = _make_mock_client()
    client.get_latest_birds.side_effect = TerraError("birds down")
    coordinator = TerraDataUpdateCoordinator.__new__(TerraDataUpdateCoordinator)
    coordinator.client = client

    data = coordinator._fetch_data()
    sd = data.stations["DEVICE123"]
    assert sd.latest_birds == []
    assert sd.stats is not None


def test_fetch_data_yard_list_failure():
    """Test that yard list failure is handled gracefully."""
    client = _make_mock_client()
    client.get_yard_list.side_effect = TerraError("yard down")
    coordinator = TerraDataUpdateCoordinator.__new__(TerraDataUpdateCoordinator)
    coordinator.client = client

    data = coordinator._fetch_data()
    sd = data.stations["DEVICE123"]
    assert sd.yard_list_count == 0


def test_fetch_data_devices_failure():
    """Test that device fetch failure raises."""
    client = _make_mock_client()
    client.get_devices.side_effect = TerraError("API down")
    coordinator = TerraDataUpdateCoordinator.__new__(TerraDataUpdateCoordinator)
    coordinator.client = client

    # _fetch_data itself raises TerraError; the coordinator wraps it in UpdateFailed
    with pytest.raises(TerraError):
        coordinator._fetch_data()
