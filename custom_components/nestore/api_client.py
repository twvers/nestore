"""API client for Nestore."""

from __future__ import annotations

import logging

import requests

from .const import (
    MAX_POWER_LEVEL,
    MIN_POWER_LEVEL,
)

_LOGGER = logging.getLogger(__name__)


class NestoreClient:
    def __init__(self, host, port, api_key: str):
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
            _LOGGER.debug("Performed GET request to {URL}")
        except requests.Timeout:
            _LOGGER.debug("Request Timeout")
            return None

        if response.status_code == 200:
            try:
                series = self.parse_data(response.json())
            except Exception as exc:
                _LOGGER.debug("Failed to retrieve data: {response.status_code}")
                raise exc
        else:
            _LOGGER.debug("Failed to retrieve data: {response.status_code}")
            return None

        return series

    def make_request(self, bool_state) -> str:
        """Definition of api post call."""

        URL = f"http://{self.host}:{self.port}/{self.api_key}"

        payload = {"path": "DEPENDENT_MODE", "value": str(bool_state)}
        response = requests.patch(url=URL, json=payload)
        _LOGGER.debug("Performing PATCH request to {URL} with {payload}")

        if response.status_code == 200:
            _LOGGER.debug("Successfull call with response: {response.text}")
        else:
            _LOGGER.debug("Failed to patch: {response.status_code}")
            return None

    def post_request(self, power_level) -> str:
        """Definition API POST call."""

        if power_level < MIN_POWER_LEVEL:
            stext = "charge_electrical_stop_force"
        elif power_level < MAX_POWER_LEVEL:
            stext = "charge_electrical_start_force?power={power_level}"

        URL = f"http://{self.host}:{self.port}/{self.api_key}/{stext}"

        response = requests.post(url=URL)
        _LOGGER.debug("Performing POST request to {URL}")

        if response.status_code == 200:
            _LOGGER.debug("Successfull call with response: {response.text}")
        else:
            _LOGGER.debug("Failed to patch: {response.status_code}")
            return None

    # lets process the received document (future need)
    def parse_data(self, data: dict) -> str:
        # _LOGGER.debug(f"json PAYLOAD BASE: {series}")
        return data
