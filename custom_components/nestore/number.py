# custom_components/my_custom_integration/number.py
import logging

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .coordinator import NestoreCoordinator

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from .const import DOMAIN, DEFAULT_LOC_FLAG

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
    number_entity1 = NestoreNumber(coordinator, "Target Power Level")
    number_entity2 = NestoreNumberSoc(coordinator, "Target State of Charge")

    async_add_entities([number_entity1, number_entity2], True)


class NestoreNumber(CoordinatorEntity, NumberEntity):
    def __init__(self, coordinator: NestoreCoordinator, input_name: str):
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
        # Optionally, update your coordinator data or trigger any other actions
        _LOGGER.debug(f"Set target power level to {self._attr_native_value}")
        # Calling the update (this should be in coordinato
        # if operating mode enabled then updte power
        if self._coordinator.get_operation_mode():
            _LOGGER.debug(f"Calling update to power level")
            await self._coordinator.post_state(
                DEFAULT_LOC_FLAG, self._attr_native_value
            )


class NestoreNumberSoc(CoordinatorEntity, NumberEntity):
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
