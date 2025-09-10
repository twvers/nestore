# custom_components/my_custom_integration/number.py
import logging

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .coordinator import NestoreCoordinator

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.device_registry import DeviceEntryType

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from .const import DOMAIN, DEFAULT_LOC_FLAG, MIN_DURATION, MAX_DURATION

_LOGGER = logging.getLogger(__name__)

NUMBER_HEATER_KEY = "Target Power Level"


@dataclass(frozen=True, kw_only=True)
class NestoreNumberEntityDescription(NumberEntityDescription):
    """Describes Nestore number entity."""

    max_value_fn: Callable[[NestoreCoordinator], float]
    min_value_fn: Callable[[NestoreCoordinator], float]
    set_value_fn: Callable[[NestoreCoordinator], Callable[[float], Awaitable[None]]]


NUMBER_TYPES: dict[str, NestoreNumberEntityDescription] = {
    NUMBER_HEATER_KEY: NestoreNumberEntityDescription(
        key="Target Power Level",
        translation_key="target_power_level",
        max_value_fn=3400,
        min_value_fn=0,
        set_value_fn=0,
        native_step=100,
    ),
    NUMBER_HEATER_KEY: NestoreNumberEntityDescription(
        key=NUMBER_HEATER_KEY,
        translation_key="target_power_level",
        max_value_fn=3400,
        min_value_fn=0,
        set_value_fn=0,
        native_step=100,
    ),
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    number_power = NestoreNumber1(coordinator, "Target Power Level")
    number_soc = NestoreNumber2(coordinator, "Target State of Charge")
    number_duration = NestoreNumber3(coordinator, "Target Duration")

    # check if control is enabled
    if coordinator.control_enabled:
        _LOGGER.debug(f"Adding number entities to integration")
        async_add_entities([number_power, number_soc, number_duration], True)


class NestoreNumber1(CoordinatorEntity, NumberEntity):
    def __init__(
        self,
        coordinator: NestoreCoordinator,
        input_name: str,
    ) -> None:
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._attr_name = input_name
        self._attr_native_min_value = 0
        self._attr_native_max_value = 3400
        self._attr_native_step = 100
        self._attr_natuve_step = 100
        self._attr_native_value = 0
        # _LOGGER.debug(f"Min: {self._attr_min_value}, Max: {self._attr_max_value}")

    @property
    def unique_id(self):
        return f"nestore_number_{self._attr_name}"

    @property
    def native_value(self):
        return self._attr_native_value

    @property
    def native_max_value(self) -> float:
        """Return the maximum available value."""
        return self._attr_native_max_value

    @property
    def native_min_value(self) -> float:
        """Return the minimum available value."""
        return self._attr_native_min_value

    async def async_set_value(self, value: int):
        self._attr_native_value = int(value)
        self._coordinator.set_target_power_level(self._attr_native_value)
        self.async_write_ha_state()
        _LOGGER.debug(f"Set target power level to {self._attr_native_value}")

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


class NestoreNumber2(CoordinatorEntity, NumberEntity):
    def __init__(self, coordinator: NestoreCoordinator, input_name: str):
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._attr_name = input_name
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 5
        self._attr_native_value = 20
        # _LOGGER.debug(f"Min: {self._attr_min_value}, Max: {self._attr_max_value}")

    @property
    def unique_id(self):
        return f"nestore_number_{self._attr_name}"

    @property
    def native_value(self):
        return self._attr_native_value

    @property
    def native_max_value(self) -> float:
        """Return the maximum available value."""
        return self._attr_native_max_value

    @property
    def native_min_value(self) -> float:
        """Return the minimum available value."""
        return self._attr_native_min_value

    async def async_set_value(self, value: int):
        self._attr_native_value = value
        self._coordinator.set_target_soc_level(value)
        self.async_write_ha_state()
        # Optionally, update your coordinator data or trigger any other actions
        _LOGGER.debug(f"Set target SoC level to {value}")

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


class NestoreNumber3(CoordinatorEntity, NumberEntity):
    def __init__(self, coordinator: NestoreCoordinator, input_name: str):
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._attr_name = input_name
        self._attr_native_min_value = 0
        self._attr_native_max_value = 5
        self._attr_native_step = 0.5
        self._attr_native_value = 0.0

    @property
    def unique_id(self):
        return f"nestore_number_{self._attr_name}"

    @property
    def native_value(self):
        return self._attr_native_value

    @property
    def native_max_value(self) -> float:
        """Return the maximum available value."""
        return self._attr_native_max_value

    @property
    def native_min_value(self) -> float:
        """Return the minimum available value."""
        return self._attr_native_min_value

    async def async_set_value(self, value: float):
        self._attr_native_value = value
        value_sec = int(value * 3600)
        self._coordinator.set_target_duration(value_sec)
        self.async_write_ha_state()
        # Optionally, update your coordinator data or trigger any other actions
        _LOGGER.debug(f"Set target duration level to {value_sec} seconds")

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
