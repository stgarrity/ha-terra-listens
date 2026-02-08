"""Binary sensor platform for Terra Listens."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import TerraDataUpdateCoordinator
from .entity import TerraEntity


class TerraStreamingBinarySensor(TerraEntity, BinarySensorEntity):
    """Binary sensor indicating whether the station is streaming."""

    _attr_translation_key = "streaming"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_icon = "mdi:broadcast"

    def __init__(
        self,
        coordinator: TerraDataUpdateCoordinator,
        station_id: str,
    ) -> None:
        super().__init__(coordinator, station_id)
        self._attr_unique_id = f"{station_id}_streaming"

    @property
    def is_on(self) -> bool | None:
        """Return True if the station is streaming."""
        if self._station_data is None:
            return None
        return self._station_data.station.streaming


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Terra Listens binary sensor entities."""
    coordinator: TerraDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        TerraStreamingBinarySensor(coordinator, station_id)
        for station_id in coordinator.data.stations
    ]
    async_add_entities(entities)
