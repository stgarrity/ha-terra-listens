"""The Terra Listens integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant

from terra_sdk import TerraClient

from .const import DOMAIN
from .coordinator import TerraDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Terra Listens from a config entry."""
    client = TerraClient(
        email=entry.data[CONF_EMAIL],
        password=entry.data[CONF_PASSWORD],
    )

    # Login synchronously in executor
    await hass.async_add_executor_job(client.login)

    coordinator = TerraDataUpdateCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: TerraDataUpdateCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        coordinator.client.close()
    return unload_ok
