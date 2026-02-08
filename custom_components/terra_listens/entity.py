"""Base entity for Terra Listens."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import TerraDataUpdateCoordinator


class TerraEntity(CoordinatorEntity[TerraDataUpdateCoordinator]):
    """Base class for Terra Listens entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: TerraDataUpdateCoordinator,
        station_id: str,
    ) -> None:
        super().__init__(coordinator)
        self._station_id = station_id

    @property
    def _station_data(self):
        """Get the station data from the coordinator."""
        return self.coordinator.data.stations.get(self._station_id)

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for grouping entities under a station."""
        station = self._station_data.station if self._station_data else None
        name = station.alias if station else self._station_id
        return DeviceInfo(
            identifiers={(DOMAIN, self._station_id)},
            name=f"Terra {name}",
            manufacturer=MANUFACTURER,
            model=MODEL,
            sw_version=station.version if station else None,
        )
