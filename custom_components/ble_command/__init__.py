"""
Custom integration to integrate integration_blueprint with Home Assistant.

For more details about this integration, please refer to
https://github.com/ludeeus/integration_blueprint
"""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.loader import async_get_loaded_integration
from homeassistant.components import bluetooth
from bleak import BleakScanner, BleakClient
from bleak.exc import BleakError
from .const import DOMAIN, LOGGER
from bleak_retry_connector import establish_connection
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse

    from .data import IntegrationBlueprintConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
]


ATTR_ADDR = "address"
ATTR_CHAR = "characteristic_uuid"
ATTR_DATA = "data"
SCHEMA_BLE_WRITE = vol.Schema(
    {
        vol.Required(ATTR_ADDR): cv.string,
        vol.Required(ATTR_CHAR): cv.string,
        vol.Required(ATTR_DATA): vol.All(
            cv.ensure_list, [vol.Coerce(int)]
        ),  # List of integers
    }
)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up is called when Home Assistant is loading our component."""

    async def handle_ble_write(call: ServiceCall) -> ServiceResponse:
        """Handle the service action call."""
        # action: ble_command.write
        # data:
        #  address: A4:C1:38:61:67:30
        #  characteristic_uuid: "00001f1f-0000-1000-8000-00805f9b34fb"
        #  data: [0x45, 0x00]
        #
        addr: str = call.data.get(ATTR_ADDR)
        char: str = call.data.get(ATTR_CHAR)
        data: bytes = call.data.get(ATTR_DATA)
        LOGGER.debug("Write %s to %s (%s)", data.hex(), addr, char)
        scanner = bluetooth.async_get_scanner(hass)
        dev = await scanner.find_device_by_address(addr)
        if dev is None:
            return {"status": "ERROR", "msg": f"Failed to find dev {addr}"}
        LOGGER.debug("Device: %s", dev)
        try:
            client = await establish_connection(BleakClient, dev, dev.address)
        except BleakError as e:
            LOGGER.exception("Connection failed")
            return {"status": "ERROR", "msg": str(e)}
        try:
            await client.write_gatt_char(char, data, response=True)
        except BleakError as e:
            LOGGER.exception("Write failed")
            LOGGER.debug("Disconnecting dev: %s", dev)
            await client.disconnect()
            return {"status": "ERROR", "msg": str(e)}
        try:
            response = await client.read_gatt_char(char)
        except BleakError as e:
            LOGGER.exception("Read failed")
            return {"status": "ERROR", "msg": str(e)}
        finally:
            LOGGER.debug("Disconnecting dev: %s", dev)
            await client.disconnect()
        LOGGER.debug("Done: response=%s", response.hex())
        return {"status": "OK", "response": response.hex()}

    LOGGER.info("Register action: %s", config)
    hass.services.async_register(DOMAIN, "write", handle_ble_write, SCHEMA_BLE_WRITE)

    # Return boolean to indicate that initialization was successful.
    return True
