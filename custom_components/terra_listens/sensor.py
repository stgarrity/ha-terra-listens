"""Sensor platform for Terra Listens."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import TerraDataUpdateCoordinator, TerraStationData
from .entity import TerraEntity


@dataclass(frozen=True, kw_only=True)
class TerraSensorDescription(SensorEntityDescription):
    """Describes a Terra sensor."""

    value_fn: Callable[[TerraStationData], Any]
    extra_attrs_fn: Callable[[TerraStationData], dict[str, Any]] | None = None


def _species_today(data: TerraStationData) -> int | None:
    return data.stats.unique_species if data.stats else None


def _calls_today(data: TerraStationData) -> int | None:
    return data.stats.call_count if data.stats else None


def _top_bird(data: TerraStationData) -> str | None:
    return data.stats.top_bird if data.stats else None


def _last_bird(data: TerraStationData) -> str | None:
    if data.latest_birds:
        return data.latest_birds[0].common_name
    return None


def _last_bird_attrs(data: TerraStationData) -> dict[str, Any]:
    if not data.latest_birds:
        return {}
    bird = data.latest_birds[0]
    return {
        "scientific_name": bird.scientific_name,
        "alpha_code": bird.alpha_code,
        "confidence": round(bird.confidence, 3),
        "image_url": bird.image_url,
        "audio_url": bird.audio_url,
        "timestamp": bird.timestamp,
        "entity_picture": bird.image_url,
    }


def _yard_list_total(data: TerraStationData) -> int:
    return data.yard_list_count


SENSOR_DESCRIPTIONS: tuple[TerraSensorDescription, ...] = (
    TerraSensorDescription(
        key="species_today",
        translation_key="species_today",
        native_unit_of_measurement="species",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_species_today,
        icon="mdi:bird",
    ),
    TerraSensorDescription(
        key="calls_today",
        translation_key="calls_today",
        native_unit_of_measurement="calls",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_calls_today,
        icon="mdi:waveform",
    ),
    TerraSensorDescription(
        key="top_bird",
        translation_key="top_bird",
        value_fn=_top_bird,
        icon="mdi:trophy-outline",
    ),
    TerraSensorDescription(
        key="last_bird",
        translation_key="last_bird",
        value_fn=_last_bird,
        extra_attrs_fn=_last_bird_attrs,
        icon="mdi:bird",
    ),
    TerraSensorDescription(
        key="yard_list_total",
        translation_key="yard_list_total",
        native_unit_of_measurement="species",
        state_class=SensorStateClass.TOTAL,
        value_fn=_yard_list_total,
        icon="mdi:format-list-numbered",
    ),
)


class TerraSensor(TerraEntity, SensorEntity):
    """A Terra Listens sensor entity."""

    entity_description: TerraSensorDescription

    def __init__(
        self,
        coordinator: TerraDataUpdateCoordinator,
        station_id: str,
        description: TerraSensorDescription,
    ) -> None:
        super().__init__(coordinator, station_id)
        self.entity_description = description
        self._attr_unique_id = f"{station_id}_{description.key}"

    @property
    def native_value(self) -> Any:
        """Return the sensor value."""
        if self._station_data is None:
            return None
        return self.entity_description.value_fn(self._station_data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes."""
        if self._station_data is None or self.entity_description.extra_attrs_fn is None:
            return None
        return self.entity_description.extra_attrs_fn(self._station_data)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Terra Listens sensor entities."""
    coordinator: TerraDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[TerraSensor] = []
    for station_id in coordinator.data.stations:
        for description in SENSOR_DESCRIPTIONS:
            entities.append(TerraSensor(coordinator, station_id, description))

    async_add_entities(entities)
