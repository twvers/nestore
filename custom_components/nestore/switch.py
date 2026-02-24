# custom_components/my_custom_integration/switch.py
import logging
import asyncio
from homeassistant.components.switch import SwitchEntity
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
    """Set up Nestore switch."""
    coordinator: NestoreCoordinator = hass.data[DOMAIN][entry.entry_id]

    _LOGGER.debug(
        f"SWITCH calling coordinator values:  {str(coordinator.data.values())}"
    )

    switch1 = NestoreSwitchEntity1(coordinator, "Heater Enable", 1)
    switch2 = NestoreSwitchEntity2(coordinator, "Heater Disable", 1)

    # check if control is enabled
    if coordinator.control_enabled:
        _LOGGER.debug(f"Adding switch entities to integration")
        async_add_entities([switch1, switch2], False)


class NestoreSwitchEntity1(SwitchEntity):
    def __init__(
        self,
        coordinator: NestoreCoordinator,
        input_name: str,
        input_type: int,
        name: int = "",
    ):
        super().__init__()
        self._coordinator = coordinator
        self._name = input_name
        self._attr_name = input_name
        self._state = False  # self._coordinator.get_operation_mode()
        self._data = None
        self._type = input_type
        self._settings = {}
        self._settings["task"] = "ControlTask_ChargingElectrical_Start"

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
        _LOGGER.debug(f"SWITCH {self._name} turning ON")

        # get settings and store locally
        self._settings["power_level"] = self._coordinator.get_target_power_level()
        self._settings["soc_level"] = self._coordinator.get_target_soc_level()
        self._settings["duration"] = self._coordinator.get_target_duration()
        self._settings["spin"] = True

        if (
            self._settings["power_level"] >= MIN_POWER_LEVEL
            and self._settings["soc_level"] > self._coordinator.get_current_soc()
            and self._settings["duration"] > MIN_DURATION
        ):
            _LOGGER.debug(f"Settings set to {self._settings}")
            try:
                await self._coordinator.async_post_state(self._settings)
                self._state = True
                self._coordinator.set_operation_mode("MANUAL_HEATER")
            except Exception as e:
                _LOGGER.error(f"Error posting state to coordinator: {e}")
        else:
            _LOGGER.debug(f"Power level set too low")

        self.schedule_update_ha_state()

        # Introduce a delay before updating the state
        _LOGGER.debug("Waiting %s seconds before refreshing coordinator", UPDATE_DELAY)
        await asyncio.sleep(UPDATE_DELAY)

        # force update of integration
        await self._coordinator.async_request_refresh()
        # update all switches in entity
        await self._update_all_switches()

    async def async_turn_off(self, **kwargs):
        """turn off heater via spin down"""
        # turn off the switch anyway
        _LOGGER.debug(f"SWITCH {self._name} turning OFF")

        if self._coordinator.get_power_heater() > 0:
            _LOGGER.debug(f"Heater still on, so disabling heater")
            # removing previous task by spinning down, this will stop the heater
            self._settings["spin"] = False
            try:
                await self._coordinator.async_post_state(self._settings)
                self._coordinator.set_operation_mode("AUTO")
                self._state = False
            except Exception as e:
                _LOGGER.error(f"Error posting state to coordinator: {e}")
        else:
            _LOGGER.debug(f"Power already off, no action needed, return to AUTO mode")
            self._coordinator.set_operation_mode("AUTO")
            self._state = False

        self.schedule_update_ha_state()

        # Introduce a delay before updating the state
        _LOGGER.debug("Waiting %s seconds before refreshing coordinator", UPDATE_DELAY)
        await asyncio.sleep(UPDATE_DELAY)

        # force update of integration
        await self._coordinator.async_request_refresh()
        if self._type > 0:
            await self._update_all_switches()

    async def _update_all_switches(self):
        for entity in self.hass.data[DOMAIN]:
            if isinstance(entity, NestoreSwitchEntity1):
                await entity.async_update()
                entity.async_schedule_update_ha_state()

    async def async_update(self):
        # Fetch data from the coordinator
        # await self._coordinator._async_update_data()
        _LOGGER.debug(f"Synced switch with coordinator: {self._state}")
        # check if power heater is still running and operation mode in manual
        current_power_level = self._coordinator.get_power_heater()
        current_operation_mode = self._coordinator.get_operation_mode()

        if current_power_level < 1 and current_operation_mode != "AUTO":
            _LOGGER.debug(
                f"Heater off but operation mode MANUAL, switch to AUTO mode and set switch to off state"
            )
            self._state = False
            self._coordinator.set_operation_mode("AUTO")
            # force update of integration
            await self.async_write_ha_state()
            await self._coordinator.async_request_refresh()
            await self._update_all_switches()

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


class NestoreSwitchEntity2(SwitchEntity):
    def __init__(
        self,
        coordinator: NestoreCoordinator,
        input_name: str,
        input_type: int,
        name: int = "",
    ):
        super().__init__()
        self._coordinator = coordinator
        self._name = input_name
        self._attr_name = input_name
        self._state = False  # self._coordinator.get_operation_mode()
        self._data = None
        self._type = input_type
        self._settings = {}
        self._settings["task"] = "ControlTask_ChargingElectrical_Stop"
        self._settings["spin"] = True

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
        _LOGGER.debug(f"SWITCH {self._name} turning ON")

        # get operation mode
        mode = self._coordinator.get_device_state()
        if mode == "Charging Electrical Main":
            _LOGGER.debug(f"Current operation mode is {mode}")
            self._settings["duration"] = self._coordinator.get_target_duration()
            try:
                await self._coordinator.async_post_state(self._settings)
                self._state = True
                self._coordinator.set_operation_mode("MANUAL_STOP")
            except Exception as e:
                _LOGGER.error(f"Error posting state to coordinator: {e}")
        else:
            _LOGGER.debug(f"Power level set too low")

        self.schedule_update_ha_state()

        # Introduce a delay before updating the state
        _LOGGER.debug("Waiting %s seconds before refreshing coordinator", UPDATE_DELAY)
        await asyncio.sleep(UPDATE_DELAY)

        # force update of integration
        await self._coordinator.async_request_refresh()
        # update all switches in entity
        await self._update_all_switches()

    async def async_turn_off(self, **kwargs):
        """turn off heater via spin down"""
        # turn off the switch anyway
        _LOGGER.debug(f"SWITCH {self._name} turning OFF")

        try:
            # removing previous task by spinning down, this will stop the heater
            self._settings["spin"] = False
            await self._coordinator.async_post_state(self._settings)
            self._state = False
        except Exception as e:
            _LOGGER.error(f"Error posting state to coordinator: {e}")

        self.schedule_update_ha_state()

        # Introduce a delay before updating the state
        _LOGGER.debug("Waiting %s seconds before refreshing coordinator", UPDATE_DELAY)
        await asyncio.sleep(UPDATE_DELAY)

        # force update of integration
        await self._coordinator.async_request_refresh()
        if self._type > 0:
            await self._update_all_switches()

    async def _update_all_switches(self):
        for entity in self.hass.data[DOMAIN]:
            if isinstance(entity, NestoreSwitchEntity1):
                await entity.async_update()
                entity.async_schedule_update_ha_state()

    async def async_update(self):
        # Fetch data from the coordinator
        # await self._coordinator._async_update_data()
        _LOGGER.debug(f"Synced switch with coordinator: {self._state}")

        current_operation_mode = self._coordinator.get_operation_mode()

        if current_operation_mode != "MANUAL_STOP":
            # force update of integration
            self._state = False
            await self.async_write_ha_state()
            await self._coordinator.async_request_refresh()
            await self._update_all_switches()

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
