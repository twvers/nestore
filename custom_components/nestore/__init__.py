"""The Nestore integration."""

from __future__ import annotations

import logging
import socket

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_API_KEY,
    CONF_PORT,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_UPDATE_INTERVAL,
    CONF_FULL_LOGGING,
    CONF_CONTROL,
    DEFAULT_LOC_ACTIVE,
    DEFAULT_LOC_FLAG,
    DEFAULT_LOC_CONTROLLER,
    DEFAULT_LOC_INPUT,
    DEFAULT_LOC_DATA,
)

from .services import async_setup_services
from .coordinator import NestoreCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.NUMBER, Platform.SENSOR, Platform.SWITCH]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up services."""
    async_setup_services(hass)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up nestore from a config entry."""

    _LOGGER.debug(f"Setup config data {entry.data} {entry.options}")

    hostname = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]

    if len(hostname) > 0:
        _LOGGER.info("Using fixed IP address %s at port %s ", hostname, port)
    else:
        # find the host name
        hostID = "nestore.home"  # Replace with your target hostname
        try:
            hostname = socket.gethostbyname(hostID)
            _LOGGER.info("The IP address of %s is %s", hostID, hostname)
            # You can now use this IP address for further configuration
        except socket.gaierror:
            _LOGGER.error("Unable to resolve hostname: %s", hostID)

    # list of api keys
    api_keys = {}
    api_keys["HOST"] = hostname
    api_keys["PORT"] = port
    api_keys["DATA"] = DEFAULT_LOC_DATA
    api_keys["CONTROL"] = DEFAULT_LOC_CONTROLLER
    api_keys["INPUT"] = DEFAULT_LOC_INPUT
    api_keys["FLAGS"] = DEFAULT_LOC_FLAG
    api_keys["CONTROLLER"] = DEFAULT_LOC_CONTROLLER
    api_keys["ACTIVE"] = DEFAULT_LOC_ACTIVE

    # create coordinator
    nestore_coordinator = NestoreCoordinator(
        hass,
        entry,
        api_keys,
    )
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = nestore_coordinator

    # fetch initial data
    await nestore_coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    # await hass.config_entries.async_reload(entry.entry_id)
    coordinator = hass.data[DOMAIN][entry.entry_id]
    await coordinator.async_update_interval(entry.options[CONF_UPDATE_INTERVAL])
    _LOGGER.debug("Updating polling interval")
