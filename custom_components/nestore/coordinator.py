"""Get the latest data and update the states."""

from __future__ import annotations

import logging
from datetime import timedelta

import homeassistant.helpers.config_validation as cv
from homeassistant.core import HomeAssistant
from homeassistant.helpers.template import Template
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt
from jinja2 import pass_context
from requests.exceptions import HTTPError

from .api_client import NestoreClient

_LOGGER = logging.getLogger(__name__)


class NestoreCoordinator(DataUpdateCoordinator):
    """Get the latest data and update the states."""

    def __init__(
        self,
        hass: HomeAssistant,
        hostname,
        port,
        api_keys,
        username,
        pwd,
        min_interval,
        full_logging,
        control_enabled,
    ) -> None:
        """Initialize the data object."""
        self.hass = hass
        self.host = hostname
        self.port = port
        self.api_keys = api_keys
        self.user = username
        self.pwd = pwd
        self.min_interval = min_interval
        self.full_logging = full_logging
        self.control_enabled = control_enabled
        self.power_level = 0
        self.target_soc = 0

        self.data_base = None
        self.data_derived = None
        self.data_counters = None

        logger = logging.getLogger(__name__)
        super().__init__(
            hass,
            logger,
            name="Nestore coordinator",
            update_interval=timedelta(seconds=self.min_interval),
        )

    # Triggered by HA to refresh the data
    async def _async_update_data(self) -> dict:
        """Get the latest data from NEStore"""
        _LOGGER.debug("Nestore DataUpdateCoordinator data update")

        # fetching all data
        data = await self.fetch_data(self.api_keys["DATA"])
        _LOGGER.debug(f"received data = {data.keys()}")

        data_control = await self.fetch_data(self.api_keys["CONTROL"])
        _LOGGER.debug(f"received data = {data_control.keys()}")

        data_control = await self.fetch_data(self.api_keys["CONTROL"])
        _LOGGER.debug(f"received data = {data_control.keys()}")

        data_active = await self.fetch_data(self.api_keys["ACTIVE"])
        _LOGGER. debug(f"received data = {data_active.keys()}")

        if data is not None:
            self.data_base = data["PAYLOAD"]["BASE"]
            self.data_counters = data["PAYLOAD"]["COUNTERS"]
            self.data_derived = data["PAYLOAD"]["DERIVED"]
            self.logger.debug(f"parsed DATA")

        if data_control is not None:
            self.device_state = data_control["PAYLOAD"]["NAME"]
            self.logger.debug(f"parsed CONTROL")

        if data_active is not None:
            self.active = {}
            self.active["MODE"] = data_active["PAYLOAD"]["DEPENDENT_MODE"]
            self.active["ONLINE"] = data_active["PAYLOAD"]["ONLINE_MODE"]
            self.logger.debug(f"parsed ACTIVE")

        return {"Data": 1, "Control": 1, "Active": 1}

    # GENERAL: New data using an async job
    async def fetch_data(self, api_loc):
        try:
            # run api_update in async job
            resp = await self.hass.async_add_executor_job(
                self.api_update, self.host, self.port, api_loc
            )
            return resp

        except HTTPError as exc:
            if exc.response.status_code == 401:
                raise UpdateFailed("Unauthorized: Please check your API-key.") from exc
        except Exception as exc:
            self.logger.warning(
                f"Warning the integration doesn't have any up to date local data this means that entities won't get updated but access remains to restorable entities: {exc}."
            )

    async def update_state(self, api_loc, state_flag):
        try:
            # run api_update in async job
            resp = await self.hass.async_add_executor_job(
                self.api_patch, self.host, self.port, api_loc, state_flag
            )
            return resp

        except HTTPError as exc:
            if exc.response.status_code == 401:
                raise UpdateFailed("Unauthorized: Please check your API-key.") from exc
        except Exception as exc:
            self.logger.warning(
                f"Warning the integration doesn't have any up to date local data this means that entities won't get updated but access remains to restorable entities: {exc}."
            )

    async def post_state(self, api_loc, power_level):
        try:
            # run api_update in async job
            resp = await self.hass.async_add_executor_job(
                self.api_post, self.host, self.port, api_loc, power_level
            )
            return resp

        except HTTPError as exc:
            if exc.response.status_code == 401:
                raise UpdateFailed("Unauthorized: Please check your API-key.") from exc
        except Exception as exc:
            self.logger.warning(
                f"Warning the integration doesn't have any up to date local data this means that entities won't get updated but access remains to restorable entities: {exc}."
            )

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
    def api_post(self, host, port, api_key, power_level):
        client = NestoreClient(host=host, port=port, api_key=api_key)
        return client.post_request(power_level)

    # ENTSO: Return the data for the given date
    # def get_all_base_data(self):
    #    return {k: v for k, v in self.data_base.items()}

    # DATA RETRIEVAL: Get current state of charge
    def get_current_soc(self):
        return self.data_derived["SOC_VES"]

    def get_current_soc_total(self):
        return self.data_derived["SOC_VES_TOTAL"]

    def get_heater_temp(self):
        return self.data_base["TEMP_HTR_OUT"]

    def get_flow(self):
        return self.data_derived["FLOW_DHW"]

    def get_current_pressure(self):
        return self.data_base["PRES_SYS"]

    def get_temp_vessel(self, id):
        return self.data_base[f"TEMP_VES_INT_{id}"]

    def get_power_heater(self):
        return self.data_base["POWER_HEATER"]

    def get_device_state(self):
        return self.device_state

    def get_operation_mode(self):
        return self.active["MODE"]

    def get_online_mode(self):
        return self.active["ONLINE"]

    def set_target_power_level(self, value):
        self.power_level = int(value)

    def get_target_power_level(self):
        return self.power_level

    def set_target_soc_level(self, value):
        self.target_soc = value

    def get_target_soc_level(self):
        return self.target_soc

    # total output energy dhw in kJ
    def get_total_energy_dhw(self):
        return self.data_counters["ENERGY_DHW_THERMAL"] / 1000.0

    # total stored energy in kJ
    def get_current_energy_dhw(self):
        return self.data_counters["ENERGY_DHW_THERMAL_THEORETICAL"] / 1000.0

    # return total electrical input power in kJ
    def get_total_electrical(self):
        return self.data_counters["ENERGY_CRG_ELECTRICAL"] / 1000.0

    # return total volume DHW in L
    def get_total_dhw(self):
        return self.data_counters["VOL_DHW"] / 1000.0
