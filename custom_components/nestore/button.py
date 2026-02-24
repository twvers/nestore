# custom_components/my_custom_integration/button.py
import logging
import asyncio
from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.device_registry import DeviceEntryType


from .coordinator import NestoreCoordinator
from .api_client import NestoreClient

from .const import (
    DOMAIN,
    MIN_POWER_LEVEL,
    MIN_DURATION,
    UPDATE_DELAY,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Nestore button"""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [NestoreRefreshTokenButton(coordinator, "Refresh Token", 0)], False
    )


class NestoreRefreshTokenButton(ButtonEntity):
    """Button to manually refresh the Nestore token."""

    def __init__(
        self,
        coordinator: NestoreCoordinator,
        input_name: str,
        input_type: int,
        name: int = "",
    ):
        super().__init__()
        self._coordinator = coordinator
        self._attr_name = input_name
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_refresh_token"

    @property
    def name(self):
        return self._attr_name

    @property
    def unique_id(self):
        return f"nestore_button_{self._attr_name}"

    async def async_press(self) -> None:
        """Handle button press."""
        _LOGGER.debug("Manual token refresh triggered")

        try:
            await self._coordinator.async_refresh_token()
            _LOGGER.debug("Token refreshed successfully")

        except Exception as e:
            _LOGGER.error("Token refresh failed: %s", e)

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={
                (DOMAIN, f"{self._coordinator.config_entry.entry_id}_nestore")
            },
            manufacturer="Nestore",
            model="",
            name="Nestore",
        )
