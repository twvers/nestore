"""Config flow for nestore integration."""

from __future__ import annotations

import logging
from typing import Any

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


async def validate_options_input(
    handler: SchemaCommonFlowHandler, user_input: dict[str, Any]
) -> dict[str, Any]:
    """Validate options are valid."""

    if CONF_UPDATE_INTERVAL in user_input:
        polling_interval: int = user_input[CONF_UPDATE_INTERVAL]
        if not 1 <= polling_interval <= 3600:
            raise SchemaFlowError("invalid_polling_interval")

    return user_input


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Check that the inputs are valid."""

    title = {"title": "NEStore Local"}
    return title


STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=DEFAULT_HOST): vol.All(vol.Coerce(str)),
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): vol.All(vol.Coerce(str)),
        vol.Optional(CONF_API_KEY, default=DEFAULT_LOC_DATA): vol.All(vol.Coerce(str)),
    }
)

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_INTERVAL): vol.All(
            vol.Coerce(int)
        ),
        vol.Required(CONF_FULL_LOGGING, default=DEFAULT_LOGGING): bool,
        vol.Required(CONF_CONTROL, default=DEFAULT_CONTROL): bool,
    }
)

OPTIONS_FLOW = {
    "init": SchemaFlowFormStep(
        OPTIONS_SCHEMA,
        validate_user_input=validate_options_input,
    )
}


class NestoreFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for nestore."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        # adding a few default items
        if user_input is not None:
            user_input[CONF_USERNAME] = DEFAULT_USERNAME
            user_input[CONF_PASSWORD] = DEFAULT_PASSWORD
            user_input[CONF_FULL_LOGGING] = DEFAULT_LOGGING
            user_input[CONF_CONTROL] = DEFAULT_CONTROL

        user_options = {}
        user_options[CONF_UPDATE_INTERVAL] = DEFAULT_INTERVAL
        user_options[CONF_FULL_LOGGING] = DEFAULT_LOGGING
        user_options[CONF_CONTROL] = DEFAULT_CONTROL

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(
                title=info["title"], data=user_input, options=user_options
            )

        # Only called if there was an error.
        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OptionsFlow:
        """Get the options flow for this handler."""
        return SchemaOptionsFlowHandler(config_entry, OPTIONS_FLOW)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
