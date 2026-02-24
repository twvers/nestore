"""Get the latest data and update the states."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from requests.exceptions import HTTPError

from .api_client import NestoreClient

_LOGGER = logging.getLogger(__name__)

from .const import (
    CONF_TOKEN,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_UPDATE_INTERVAL,
    CONF_FULL_LOGGING,
    CONF_CONTROL,
    DEFAULT_LOC_TOKEN,
    DEFAULT_LOC_ACTIVE,
    DEFAULT_LOC_FLAG,
    DEFAULT_LOC_CONTROLLER,
    DEFAULT_LOC_INPUT,
    DEFAULT_LOC_DATA,
    UPDATE_DELAY,
)


class NestoreCoordinator(DataUpdateCoordinator):
    """Get the latest data and update the states."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry,
        api_keys,
    ) -> None:
        """Initialize the data object."""
        self.hass = hass
        self.config_entry = config_entry
        self.api_keys = api_keys
        self.host = api_keys["HOST"]
        self.port = api_keys["PORT"]

        self.min_interval = self.config_entry.options[CONF_UPDATE_INTERVAL]
        self.full_logging = self.config_entry.options[CONF_FULL_LOGGING]
        self.control_enabled = self.config_entry.options[CONF_CONTROL]
        self.control_token = self.config_entry.data[CONF_TOKEN]
        self.control_username = self.config_entry.options[CONF_USERNAME]
        self.control_password = self.config_entry.options[CONF_PASSWORD]

        # control entities
        self.power_level = 0
        self.target_soc = 0
        self.duration = 0
        self.operation_mode = "AUTO"

        # initiate data containers
        self.data_base = None
        self.data_derived = None
        self.data_counters = None
        self.active = {"MODE": False, "ONLINE": False}

        # create api client
        self.client = NestoreClient(self.hass, self.host, self.port, self.control_token)

        logger = logging.getLogger(__name__)
        super().__init__(
            hass,
            logger,
            name="Nestore coordinator",
            update_method=self._async_update_data,
            update_interval=timedelta(seconds=self.min_interval),
        )

    async def async_update_interval(self, new_seconds: float) -> None:
        """Update the polling interval."""
        new_interval = timedelta(seconds=new_seconds)

        _LOGGER.debug("Updating polling interval to %s seconds", new_seconds)

        # Update the interval
        self.update_interval = new_interval

        # Force an immediate update and reschedule
        # Cancel any existing update task
        if self._unsub_refresh:
            self._unsub_refresh()
            self._unsub_refresh = None
        # Restart the update task with the new interval
        self._unsub_refresh = self._schedule_refresh()

        # trigger a refresh data
        await self.async_refresh()

    def get_polling_interval(self):
        return self.update_interval

    # Triggered by HA to refresh the data
    async def _async_update_data(self) -> dict:
        """Get the latest data from NEStore."""
        _LOGGER.info("Nestore DataUpdateCoordinator data update")

        data = await self.client.async_query_data(self.api_keys["DATA"])
        data_control = await self.client.async_query_data(self.api_keys["CONTROL"])

        returnStates = {}

        if data is not None:
            self.data_base = data["PAYLOAD"]["BASE"]
            self.data_counters = data["PAYLOAD"]["COUNTERS"]
            self.data_derived = data["PAYLOAD"]["DERIVED"]
            self.logger.debug("Parsed DATA log")
            returnStates["Data"] = True

        if data_control is not None:
            self.device_state = data_control["PAYLOAD"]["NAME"]
            self.logger.debug("Parsed CONTROL log")
            returnStates["Control"] = True

        # update switch states

        return returnStates

    async def async_post_state(self, settings):
        """Post state using api routine."""
        await self.client.async_post_request(self.api_keys["FLAGS"], settings)

    async def async_refresh_token(self):
        """get a new token"""

        self.control_token = await self.client.async_get_token(
            DEFAULT_LOC_TOKEN, self.control_username, self.control_password
        )
        _LOGGER.debug("Obtained a new token: %s", self.control_token)

        _LOGGER.debug("Updating token in API client")
        self.client.set_token(self.control_token)

        self.hass.config_entries.async_update_entry(
            self.config_entry,
            data={**self.config_entry.data, "token": self.control_token},
        )

    # storing switch entity

    def set_operation_mode(self, value):
        """Set operation mode"""
        self.operation_mode = value

    def get_operation_mode(self):
        """Get operation mode"""
        return self.operation_mode

    def get_target_duration(self):
        """Get target duration."""
        return self.duration

    def set_target_duration(self, value):
        """Set target duration."""
        self.duration = int(value)

    # Data retrieval routines

    def get_current_soc(self):
        """Get current state of charge."""
        return self.data_derived["SOC_VES"]

    def get_current_soc_total(self):
        """Get current total state of charge."""
        return self.data_derived["SOC_VES_TOTAL"]

    def get_heater_temp(self):
        """Get current heater temperature."""
        return self.data_base["TEMP_HTR_OUT"]

    def get_flow(self):
        """Get water flow."""
        return self.data_derived["FLOW_DHW"]

    def get_current_pressure(self):
        """Get current pressure."""
        return self.data_base["PRES_SYS"]

    def get_temp_vessel(self, id):
        """Get internal temperature of specified zone."""
        return self.data_base[f"TEMP_VES_INT_{id}"]

    def get_power_heater(self):
        """Get heater electrical power."""
        return self.data_derived["POWER_HEATER"]

    def get_device_state(self):
        """Get current device state."""
        return self.device_state

    def set_target_power_level(self, value):
        """Set target power level."""
        self.power_level = int(value)

    def get_target_power_level(self):
        """Get target power level."""
        return self.power_level

    def set_target_soc_level(self, value):
        """Set target max state of charge level."""
        self.target_soc = int(value)

    def get_target_soc_level(self):
        """Get target max state of charge level."""
        return self.target_soc

    def get_total_energy_dhw(self):
        """Get total energy DHW in kWh"""
        return self.data_counters["ENERGY_DHW_THERMAL_THEORETICAL"] / 1000.0

    def get_current_energy_dhw(self):
        """Get current stored energy DHW in kWh"""
        return self.data_derived["TE"] / 1000.0

    def get_total_electrical(self):
        """Get total electrical energy input in kWh"""
        return self.data_counters["ENERGY_CRG_ELECTRICAL"] / 1000.0

    def get_total_dhw(self):
        """Get total water volume provided in"""
        return self.data_counters["VOL_DHW_THEORETICAL"] / 1000.0
