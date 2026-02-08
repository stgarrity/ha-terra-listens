"""Config flow for Terra Listens integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD

from terra_sdk import TerraClient
from terra_sdk.exceptions import TerraAuthError, TerraError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class TerraListensConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Terra Listens."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step — email and password."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                client = TerraClient(
                    email=user_input[CONF_EMAIL],
                    password=user_input[CONF_PASSWORD],
                )
                token = await self.hass.async_add_executor_job(client.login)
            except TerraAuthError:
                errors["base"] = "invalid_auth"
            except TerraError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error during login")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(user_input[CONF_EMAIL])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Terra Listens ({user_input[CONF_EMAIL]})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
