"""Adds config flow for Blueprint."""

from __future__ import annotations

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import DOMAIN


class BleCommandFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for BLE command."""

    VERSION = 1

    async def async_step_user(self, _: dict | None = None) -> ConfigFlowResult:
        """Handle the initial step."""
        return self.async_create_entry(title="BLE command", data={})
