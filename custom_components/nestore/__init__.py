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

    _LOGGER.debug("config data {entry.options}")
    # initialize with the config data that is saved
    username = entry.data[CONF_USERNAME]
    pwd = entry.data[CONF_PASSWORD]
    hostname = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    min_interval = entry.options[CONF_UPDATE_INTERVAL]
    full_logging = entry.options[CONF_FULL_LOGGING]
    control_enabled = entry.options[CONF_CONTROL]

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
    api_keys["DATA"] = entry.data[CONF_API_KEY]
    api_keys["CONTROL"] = DEFAULT_LOC_CONTROLLER
    api_keys["INPUT"] = DEFAULT_LOC_INPUT
    api_keys["FLAGS"] = DEFAULT_LOC_FLAG
    api_keys["CONTROLLER"] = DEFAULT_LOC_CONTROLLER
    api_keys["ACTIVE"] = DEFAULT_LOC_ACTIVE

    # create coordinator
    nestore_coordinator = NestoreCoordinator(
        hass,
        hostname,
        port,
        api_keys,
        username,
        pwd,
        min_interval,
        full_logging,
        control_enabled,
    )
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = nestore_coordinator

    # fetch initial data
    await nestore_coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)
