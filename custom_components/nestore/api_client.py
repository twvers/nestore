"""API client for Nestore."""

from __future__ import annotations

import logging

import requests

from .const import (
    MAX_POWER_LEVEL,
    MIN_POWER_LEVEL,
    MIN_DURATION,
    MAX_DURATION,
)

_LOGGER = logging.getLogger(__name__)


class NestoreClient:
    """Main integration class."""

    def __init__(self, host, port, api_key: str):
        """Init function with host address."""
        if api_key == "":
            raise TypeError("API key cannot be empty")
        self.host = host
        self.port = port
        self.api_key = api_key

    def query_data(self) -> str:
        """Query data using the api key."""

        # get URL
        URL = f"http://{self.host}:{self.port}/{self.api_key}"

        try:
            response = requests.get(url=URL, timeout=10)  # Timeout set to 10 seconds
            _LOGGER.debug(f"Performed GET request to {URL}")
        except requests.Timeout:
            _LOGGER.debug("Request Timeout")
            return None

        if response.status_code == 200:
            try:
                series = self.parse_data(response.json())
            except Exception as exc:
                _LOGGER.debug(f"Failed to retrieve data: {response.status_code}")
                raise exc
        else:
            _LOGGER.debug(f"Failed to retrieve data: {response.status_code}")
            return None

        return series

    def make_request(self, bool_state) -> str:
        """Definition of api post call."""

        URL = f"http://{self.host}:{self.port}/{self.api_key}"

        payload = {"path": "DEPENDENT_MODE", "value": str(bool_state)}
        try:
            response = requests.patch(url=URL, json=payload)
            _LOGGER.debug(f"Performing PATCH request to {URL} with {payload}")
        except requests.Timeout:
            _LOGGER.debug("Request Timeout")
            return None

        if response.status_code == 200:
            _LOGGER.debug(f"Successfull call with response: {response.text}")
        else:
            _LOGGER.debug(f"Failed to patch: {response.status_code}")
            return None

    def post_request(self, power_level, soc_level, duration, spin) -> str:
        """Definition API POST call."""

        if power_level <= MAX_POWER_LEVEL and duration >= MIN_DURATION:
            data_json = {
                "TASK": "ControlTask_ChargingElectrical_Start",
                "spin": spin,
                "power": power_level,
                "soc": soc_level,
                "persistent": True,
                "lifetime": duration,
            }

        URL = f"http://{self.host}:{self.port}/{self.api_key}/"

        try:
            response = requests.post(url=URL, json=data_json)
            _LOGGER.debug(f"Performing POST request to {URL} with data {data_json}")
        except requests.Timeout:
            _LOGGER.debug("Request Timeout")
            return None

        if response.status_code == 200:
            _LOGGER.debug(f"Successfull call with response: {response.text}")
        else:
            _LOGGER.debug(f"Failed to patch: {response.status_code}")
            return None

    def parse_data(self, data: dict) -> str:
        """Function to perform some data parsing in the future."""
        # _LOGGER.debug(f"json PAYLOAD BASE: {series}")
        return data
