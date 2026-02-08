"""DataUpdateCoordinator for Terra Listens."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from terra_sdk import TerraClient
from terra_sdk.exceptions import TerraError
from terra_sdk.models import BirdDetection, Station, StationStats

from .const import DOMAIN, SCAN_INTERVAL_SECONDS

_LOGGER = logging.getLogger(__name__)


@dataclass
class TerraStationData:
    """Holds all polled data for a single station."""

    station: Station
    stats: StationStats | None = None
    latest_birds: list[BirdDetection] = field(default_factory=list)
    yard_list_count: int = 0


@dataclass
class TerraData:
    """Container for all data from the coordinator."""

    stations: dict[str, TerraStationData] = field(default_factory=dict)


class TerraDataUpdateCoordinator(DataUpdateCoordinator[TerraData]):
    """Fetch data from Terra Listens API."""

    def __init__(self, hass: HomeAssistant, client: TerraClient) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL_SECONDS),
        )
        self.client = client

    async def _async_update_data(self) -> TerraData:
        """Fetch data from the API."""
        try:
            return await self.hass.async_add_executor_job(self._fetch_data)
        except TerraError as err:
            raise UpdateFailed(f"Error communicating with Terra API: {err}") from err

    def _fetch_data(self) -> TerraData:
        """Synchronous data fetch (runs in executor)."""
        devices = self.client.get_devices()
        data = TerraData()

        for device in devices:
            station_data = TerraStationData(station=device)
            try:
                station_data.stats = self.client.get_stats(device.id)
            except TerraError:
                _LOGGER.warning("Failed to get stats for %s", device.alias)

            try:
                station_data.latest_birds = self.client.get_latest_birds(
                    device.id, count=5
                )
            except TerraError:
                _LOGGER.warning("Failed to get latest birds for %s", device.alias)

            try:
                yard_list = self.client.get_yard_list(device.id, timeframe="all")
                station_data.yard_list_count = len(yard_list)
            except TerraError:
                _LOGGER.warning("Failed to get yard list for %s", device.alias)

            data.stations[device.id] = station_data

        return data
