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
    DOMAIN,
    CONF_HOST,
    CONF_API_KEY,
    CONF_PORT,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_UPDATE_INTERVAL,
    CONF_FULL_LOGGING,
    CONF_CONTROL,
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

        # control entities
        self.power_level = 0
        self.target_soc = 0
        self.duration = 0
        self.operation_mode = "AUTO"

        # data containers
        self.data_base = None
        self.data_derived = None
        self.data_counters = None
        self.active = {"MODE": False, "ONLINE": False}

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

        # fetching all data locations
        data = await self.fetch_data(self.api_keys["DATA"])
        # _LOGGER.debug(f"received data = {data.keys()}")

        data_control = await self.fetch_data(self.api_keys["CONTROL"])
        # _LOGGER.debug(f"received data = {data_control.keys()}")

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

    async def fetch_data(self, api_loc):
        """Fetch data using api routine."""
        try:
            # run api_update in async job
            resp = await self.hass.async_add_executor_job(
                self.api_update, self.host, self.port, api_loc
            )
            return resp

        except HTTPError as exc:
            if exc.response.status_code == 401:
                raise UpdateFailed("Unauthorized: Please check your API-key.") from exc
            else:
                _LOGGER.debug("Fetch data failed")
                return None

    async def update_state(self, api_loc, state_flag):
        """Update state using api routine."""
        try:
            # run api_update in async job
            resp = await self.hass.async_add_executor_job(
                self.api_patch, self.host, self.port, api_loc, state_flag
            )
            return resp

        except HTTPError as exc:
            if exc.response.status_code == 401:
                raise UpdateFailed("Unauthorized: Please check your API-key.") from exc
            else:
                _LOGGER.debug("Update call failed")
                return None

    async def post_state(self, api_loc, power_level, soc_level, duration, spin):
        """Post state using api routine."""
        try:
            # run api_update in async job
            resp = await self.hass.async_add_executor_job(
                self.api_post,
                self.host,
                self.port,
                api_loc,
                power_level,
                soc_level,
                duration,
                spin,
            )
            return resp

        except HTTPError as exc:
            if exc.response.status_code == 401:
                raise UpdateFailed("Unauthorized: Please check your API-key.") from exc
            else:
                _LOGGER.debug("Post call failed")
                return None

    # GENERAL: async fetch job itself
    def api_update(self, host, port, api_key):
        client = NestoreClient(host=host, port=port, api_key=api_key)
        return client.query_data()

    # GENERAL: post data
    def api_patch(self, host, port, api_key, state_flag):
        self.logger.debug(f"Calling API patch: {api_key}")
        client = NestoreClient(host=host, port=port, api_key=api_key)
        return client.make_request(state_flag)

    # GENERAL: post data
    def api_post(self, host, port, api_key, power_level, soc_level, duration, spin):
        client = NestoreClient(host=host, port=port, api_key=api_key)
        return client.post_request(power_level, soc_level, duration, spin)

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
        return self.data_base["POWER_HEATER"]

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
