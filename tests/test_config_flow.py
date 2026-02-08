"""Tests for Terra Listens config flow."""

from unittest.mock import MagicMock, patch

import pytest
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.terra_listens.const import DOMAIN

MOCK_USER_INPUT = {
    CONF_EMAIL: "test@example.com",
    CONF_PASSWORD: "testpass123",
}


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for all tests."""
    yield


@pytest.fixture
def mock_client():
    """Return a mocked TerraClient."""
    with patch(
        "custom_components.terra_listens.config_flow.TerraClient"
    ) as mock_cls:
        client = MagicMock()
        client.login.return_value = "fake-token-123"
        mock_cls.return_value = client
        yield mock_cls


async def test_form_valid_credentials(hass: HomeAssistant, mock_client):
    """Test successful config flow with valid credentials."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], MOCK_USER_INPUT
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Terra Listens (test@example.com)"
    assert result["data"] == MOCK_USER_INPUT


async def test_form_invalid_auth(hass: HomeAssistant, mock_client):
    """Test config flow with invalid credentials."""
    from terra_sdk.exceptions import TerraAuthError

    mock_client.return_value.login.side_effect = TerraAuthError("Bad creds")

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], MOCK_USER_INPUT
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}


async def test_form_cannot_connect(hass: HomeAssistant, mock_client):
    """Test config flow when API is unreachable."""
    from terra_sdk.exceptions import TerraAPIError

    mock_client.return_value.login.side_effect = TerraAPIError("Timeout")

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], MOCK_USER_INPUT
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_form_unknown_error(hass: HomeAssistant, mock_client):
    """Test config flow with unexpected exception."""
    mock_client.return_value.login.side_effect = RuntimeError("boom")

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], MOCK_USER_INPUT
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "unknown"}
