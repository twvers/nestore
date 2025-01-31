# custom_components/my_custom_integration/switch.py
import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from .coordinator import NestoreCoordinator

from .const import (
    DOMAIN,
    DEFAULT_LOC_INPUT,
    DEFAULT_LOC_FLAG,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Nestore switch."""
    coordinator: NestoreCoordinator = hass.data[DOMAIN][entry.entry_id]

    _LOGGER.debug(
        f"SWITCH calling coordinator values:  {str(coordinator.data.values())}"
    )

    switch1 = NestoreSwitchEntity(coordinator, "Heater Enable", 1)
    switch2 = NestoreSwitchEntity(coordinator, "Manual Mode", 0)
    async_add_entities([switch1, switch2], True)


async def async_setup_platform(
    hass: HomeAssistant, config, async_add_entities, discovery_info=None
):
    coordinator = hass.data[DOMAIN]
    switch1 = NestoreSwitchEntity(coordinator, "Heater Enable", 1)
    switch2 = NestoreSwitchEntity(coordinator, "Power Mode", 0)
    async_add_entities([switch1, switch2], True)


class NestoreSwitchEntity(SwitchEntity):
    def __init__(
        self, coordinator: NestoreCoordinator, input_name: str, input_type: int
    ):
        self._coordinator = coordinator
        self._name = input_name
        self._state = self._coordinator.get_operation_mode()
        self._api_key = DEFAULT_LOC_INPUT
        self._data = None
        self._type = input_type

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return f"nestore_switch_{self._name}"

    @property
    def is_on(self):
        return self._state

    async def async_turn_on(self, **kwargs):
        self._state = True
        _LOGGER.debug(f"SWITCH turning ON")
        await self._coordinator.update_state(self._api_key, self._state)

        if self._type > 0:
            power_level = self._coordinator.get_target_power_level()
            _LOGGER.debug(f"SET POWER to {power_level}")
            await self._coordinator.post_state(DEFAULT_LOC_FLAG, power_level)
            # self.schedule_update_ha_state()
            # self._coordinator.async_set_updated_data({"state": "on"})

        # force update of integration
        await self._coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        self._state = False
        _LOGGER.debug(f"SWITCH turning OFF")
        if self._type > 0:
            # check power
            power_level = self._coordinator.get_power_heater()
            if power_level > 0:
                power_level = 0
                _LOGGER.debug(f"SET POWER to {power_level}")
                await self._coordinator.post_state(DEFAULT_LOC_FLAG, power_level)
        # back to basic mode
        await self._coordinator.update_state(self._api_key, self._state)
        # force update of integration
        await self._coordinator.async_request_refresh()
        # self.schedule_update_ha_state()
        # self._coordinator.async_set_updated_data({"state": "off"})

    async def async_update(self):
        # Fetch data from the coordinator
        await self._coordinator._async_update_data()
        self._data = self._coordinator.data
        _LOGGER.debug(f"Fetched SWITCH data: {self._data}")
        # check if updated and then apply?
