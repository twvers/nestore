"""Nestore heat storage sensor description"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from homeassistant.components.sensor import (
    DOMAIN,
    RestoreSensor,
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)

from homeassistant.components.number import (
    NumberDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfVolumeFlowRate,
    UnitOfTemperature,
    UnitOfPower,
    UnitOfEnergy,
    UnitOfVolume,
    UnitOfPressure,
)
from homeassistant.core import HassJob, HomeAssistant
from homeassistant.helpers import event
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import utcnow

from datetime import timedelta
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    ATTRIBUTION,
    CONF_ENTITY_NAME,
    DOMAIN,
)

from .coordinator import NestoreCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass
class NestoreEntityDescription(SensorEntityDescription):
    """Describes Nestore sensor entity."""

    value_fn: Callable[[dict], StateType] = None


def sensor_descriptions() -> tuple[NestoreEntityDescription, ...]:
    """Construct NestoreEntityDescription."""
    return (
        NestoreEntityDescription(
            key="current_soc",
            name="state of charge",
            native_unit_of_measurement=f"{PERCENTAGE}",
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:percent",
            suggested_display_precision=1,
            value_fn=lambda coordinator: coordinator.get_current_soc(),
        ),
        NestoreEntityDescription(
            key="vessel_soc",
            name="total state of charge",
            native_unit_of_measurement=f"{PERCENTAGE}",
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:percent",
            suggested_display_precision=1,
            value_fn=lambda coordinator: coordinator.get_current_soc_total(),
        ),
        NestoreEntityDescription(
            key="heater_power",
            name="heater power",
            native_unit_of_measurement=f"{UnitOfPower.WATT}",
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:heating-coil",
            suggested_display_precision=1,
            value_fn=lambda coordinator: coordinator.get_power_heater(),
        ),
        NestoreEntityDescription(
            key="vessel_temp_int1",
            name="vessel temp internal 1",
            native_unit_of_measurement=f"{UnitOfTemperature.CELSIUS}",
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:temperature-celsius",
            suggested_display_precision=1,
            value_fn=lambda coordinator: coordinator.get_temp_vessel(id=1),
        ),
        NestoreEntityDescription(
            key="vessel_temp_int2",
            name="vessel temp internal 2",
            native_unit_of_measurement=f"{UnitOfTemperature.CELSIUS}",
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:temperature-celsius",
            suggested_display_precision=1,
            value_fn=lambda coordinator: coordinator.get_temp_vessel(id=2),
        ),
        NestoreEntityDescription(
            key="vessel_temp_int3",
            name="vessel temp internal 3",
            native_unit_of_measurement=f"{UnitOfTemperature.CELSIUS}",
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:temperature-celsius",
            suggested_display_precision=1,
            value_fn=lambda coordinator: coordinator.get_temp_vessel(id=3),
        ),
        NestoreEntityDescription(
            key="vessel_temp_int4",
            name="vessel temp internal 4",
            native_unit_of_measurement=f"{UnitOfTemperature.CELSIUS}",
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:temperature-celsius",
            suggested_display_precision=1,
            value_fn=lambda coordinator: coordinator.get_temp_vessel(id=4),
        ),
        NestoreEntityDescription(
            key="vessel_temp_int5",
            name="vessel temp internal 5",
            native_unit_of_measurement=f"{UnitOfTemperature.CELSIUS}",
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:temperature-celsius",
            suggested_display_precision=1,
            value_fn=lambda coordinator: coordinator.get_temp_vessel(id=5),
        ),
        NestoreEntityDescription(
            key="pressure",
            name="pressure",
            native_unit_of_measurement=f"{UnitOfPressure.BAR}",
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:water",
            suggested_display_precision=1,
            value_fn=lambda coordinator: coordinator.get_current_pressure(),
        ),
        NestoreEntityDescription(
            key="flow_dwh",
            name="hot water flow",
            native_unit_of_measurement=f"{UnitOfVolumeFlowRate.LITERS_PER_MINUTE}",
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:water",
            suggested_display_precision=1,
            value_fn=lambda coordinator: coordinator.get_flow(),
        ),
        NestoreEntityDescription(
            key="device_state",
            name="device state",
            icon="mdi:cog-outline",
            state_class=None,
            value_fn=lambda coordinator: coordinator.get_device_state(),
        ),
        NestoreEntityDescription(
            key="total energy dhw",
            name="total energy dhw",
            native_unit_of_measurement=f"{UnitOfEnergy.KILO_JOULE}",
            state_class=SensorStateClass.TOTAL_INCREASING,
            icon="mdi:temperature-celsius",
            suggested_display_precision=1,
            value_fn=lambda coordinator: coordinator.get_total_energy_dhw(),
        ),
        NestoreEntityDescription(
            key="current stored energy",
            name="current stored energy",
            native_unit_of_measurement=f"{UnitOfEnergy.KILO_JOULE}",
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:temperature-celsius",
            suggested_display_precision=1,
            value_fn=lambda coordinator: coordinator.get_current_energy_dhw(),
        ),
        NestoreEntityDescription(
            key="total heater energy",
            name="total heater energy",
            native_unit_of_measurement=f"{UnitOfEnergy.KILO_JOULE}",
            state_class=SensorStateClass.TOTAL_INCREASING,
            icon="mdi:temperature-celsius",
            suggested_display_precision=1,
            value_fn=lambda coordinator: coordinator.get_total_electrical(),
        ),
        NestoreEntityDescription(
            key="total water volume",
            name="total water volume",
            native_unit_of_measurement=f"{UnitOfVolume.LITERS}",
            state_class=SensorStateClass.TOTAL_INCREASING,
            icon="mdi:temperature-celsius",
            suggested_display_precision=1,
            value_fn=lambda coordinator: coordinator.get_total_dhw(),
        ),
    )


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Nestore sensor entries."""
    nestore_coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = []
    entity = {}
    for description in sensor_descriptions():
        entity = description
        entities.append(NestoreSensor(nestore_coordinator, entity))

    # Add an entity for each sensor type
    async_add_entities(entities, True)

    # ensure updating
    async def update_entities(event_time):
        for entity in entities:
            await entity.async_update_ha_state(True)

    poll_interval = nestore_coordinator.get_polling_interval()

    async_track_time_interval(hass, update_entities, poll_interval)


class NestoreSensor(CoordinatorEntity, RestoreSensor):
    """Representation of a Nestore sensor."""

    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: NestoreCoordinator,
        description: NestoreEntityDescription,
        name: str = "",
    ) -> None:
        """Initialize the sensor."""
        self.description = description
        self.last_update_success = True

        if name not in (None, ""):
            # The Id used for addressing the entity in the ui, recorder history etc.
            self.entity_id = f"{DOMAIN}.{name}_{description.name}"
            # unique id in .storage file for ui configuration.
            self._attr_unique_id = f"nestore.{name}_{description.key}"
            self._attr_name = f"{description.name} ({name})"
        else:
            self.entity_id = f"{DOMAIN}.nestore_{description.name}"
            self._attr_unique_id = f"nestore.{description.key}"
            self._attr_name = f"{description.name}"

        self.entity_description: NestoreEntityDescription = description
        self._attr_icon = description.icon
        if self.entity_description.state_class is not None:
            self._attr_suggested_display_precision = (
                description.suggested_display_precision
                if description.suggested_display_precision is not None
                else 2
            )

        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={
                (
                    DOMAIN,
                    f"{coordinator.config_entry.entry_id}_nestore",
                )
            },
            manufacturer="nestore",
            model="",
            name="nestore" + ((" (" + name + ")") if name != "" else ""),
        )

        self._update_job = HassJob(self.async_schedule_update_ha_state)
        self._unsub_update = None

        super().__init__(coordinator)

    async def async_update(self) -> None:
        """Get the latest data and updates the states."""
        _LOGGER.debug(f"update function for '{self.entity_id} called.'")

        value: Any = None
        try:
            # _LOGGER.debug(f"current coordinator.data value: {self.coordinator.data}")
            value = self.entity_description.value_fn(self.coordinator)

            self._attr_native_value = value
            self.last_update_success = True
            # _LOGGER.debug(f"updated '{self.entity_id}' to value: {value}")
            # force updae
            # self.async_write_ha_state()
        except Exception as exc:
            # No data available
            self.last_update_success = False
            _LOGGER.warning(
                f"Unable to update entity '{self.entity_id}', value: {value} and error: {exc}, data: {self.coordinator.data}"
            )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.last_update_success
