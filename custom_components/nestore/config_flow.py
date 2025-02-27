"""Config flow for nestore integration."""

from __future__ import annotations

import logging
from typing import Any, Optional

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
    callback,
)

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaCommonFlowHandler,
    SchemaFlowError,
    SchemaFlowFormStep,
    SchemaOptionsFlowHandler,
)
from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PORT,
    CONF_API_KEY,
    CONF_USERNAME,
    CONF_PASSWORD,
    DEFAULT_USERNAME,
    DEFAULT_PASSWORD,
    DEFAULT_PORT,
    DEFAULT_HOST,
    DEFAULT_LOC_DATA,
    DEFAULT_INTERVAL,
    CONF_FULL_LOGGING,
    CONF_CONTROL,
    DEFAULT_LOGGING,
    DEFAULT_CONTROL,
    CONF_ENTITY_NAME,
    UNIQUE_ID,
    CONF_UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_HOST, default=DEFAULT_HOST): vol.All(vol.Coerce(str)),
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): vol.All(vol.Coerce(str)),
        vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=30, max=3600)
        ),
        vol.Required(CONF_FULL_LOGGING, default=DEFAULT_LOGGING): bool,
        vol.Required(CONF_CONTROL, default=DEFAULT_CONTROL): bool,
    }
)


class NestoreConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the Heater integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[dict[str, Any]] = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate the input here
            try:
                # Your validation logic for API connection
                return self.async_create_entry(
                    title="Nestore Device", data=user_input, options=user_input
                )
            except Exception as error:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OptionsFlow:
        """Create the options flow."""
        return NestoreOptionsFlowHandler(config_entry)


class NestoreOptionsFlowHandler(OptionsFlow):
    """Handle options flow changes."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.min_interval = config_entry.options[CONF_UPDATE_INTERVAL]

    async def async_step_init(
        self, user_input: Optional[dict[str, Any]] = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        errors = {}

        if user_input is not None:
            # Update the config entry
            return self.async_create_entry(title="", data=user_input)

        OPTIONS_SCHEMA = vol.Schema(
            {
                vol.Optional(CONF_UPDATE_INTERVAL, default=self.min_interval): vol.All(
                    vol.Coerce(int), vol.Range(min=30, max=3600)
                ),
                vol.Required(CONF_FULL_LOGGING, default=DEFAULT_LOGGING): bool,
                vol.Required(CONF_CONTROL, default=DEFAULT_CONTROL): bool,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=OPTIONS_SCHEMA,
            errors=errors,
        )
