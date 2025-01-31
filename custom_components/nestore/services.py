"""The NEstore services."""

from __future__ import annotations

import logging
from datetime import date, datetime
from functools import partial
from typing import Final

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
    callback,
)
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import selector
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import NestoreCoordinator

_LOGGER = logging.getLogger(__name__)

ATTR_CONFIG_ENTRY: Final = "config_entry"
ATTR_START: Final = "start"
ATTR_END: Final = "end"

ENERGY_SERVICE_NAME: Final = "get_nestore_values"

SERVICE_SCHEMA: Final = vol.Schema(
    {
        vol.Required(ATTR_CONFIG_ENTRY): selector.ConfigEntrySelector(
            {
                "integration": DOMAIN,
            }
        ),
        vol.Optional(ATTR_START): str,
        vol.Optional(ATTR_END): str,
    }
)


def __get_coordinator(hass: HomeAssistant, call: ServiceCall) -> NestoreCoordinator:
    """Get the coordinator from the entry."""
    entry_id: str = call.data[ATTR_CONFIG_ENTRY]
    entry: ConfigEntry | None = hass.config_entries.async_get_entry(entry_id)

    if not entry:
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="invalid_config_entry",
            translation_placeholders={
                "config_entry": entry_id,
            },
        )
    if entry.state != ConfigEntryState.LOADED:
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="unloaded_config_entry",
            translation_placeholders={
                "config_entry": entry.title,
            },
        )

    coordinator: NestoreCoordinator = hass.data[DOMAIN][entry_id]
    return coordinator


async def __get_values(
    call: ServiceCall,
    *,
    hass: HomeAssistant,
) -> ServiceResponse:
    coordinator = __get_coordinator(hass, call)

    # TODO define get values
    data = await coordinator.get_values()

    return data


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    """Set up Nestore services."""

    hass.services.async_register(
        DOMAIN,
        ENERGY_SERVICE_NAME,
        partial(__get_values, hass=hass),
        schema=SERVICE_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
