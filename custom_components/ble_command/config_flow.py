"""Adds config flow for Blueprint."""

from __future__ import annotations

from homeassistant import config_entries

from .const import DOMAIN


class BleCommandFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for BLE command."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        return self.async_create_entry(title="BLE command", data={})
