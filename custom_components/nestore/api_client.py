"""API client for Nestore."""

from __future__ import annotations

from config.custom_components.entsoe.api_client import URL
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import aiohttp
import asyncio

import logging
import hashlib

import requests

from .const import (
    MAX_POWER_LEVEL,
    MIN_POWER_LEVEL,
    MIN_DURATION,
    MAX_DURATION,
    CONF_USERNAME,
    CONF_PASSWORD,
)

_LOGGER = logging.getLogger(__name__)


class NestoreClient:
    """Main integration class."""

    def __init__(self, hass, host, port, token: str):
        """Init function with host address."""

        self._session = async_get_clientsession(hass)
        self.host = host
        self.port = port
        self.header = {"Content-Type": "application/json"}
        if token != "":
            self.set_token(token)

    @property
    def base_url(self):
        return f"http://{self.host}:{self.port}"

    def set_password(self, password: str):
        """Set the password for the client."""
        self.password = password

    def set_token(self, token: str):
        """Set the token for the client."""
        self.token = token
        self.header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

    async def async_query_host(self, api_key) -> str:
        """Query the host to see if response is OK"""
        URL = f"{self.base_url}/{api_key}/"

        try:
            async with self._session.get(
                URL, timeout=10
            ) as response:  # Timeout set to 10 seconds
                response.raise_for_status()  # Raise an exception for HTTP errors
                _LOGGER.debug(f"Successfully connected to {URL}")
                return True
        except aiohttp.ClientResponseError as err:
            _LOGGER.debug(f"HTTP error from {URL}: {err.status}")
            return False

        except asyncio.TimeoutError:
            _LOGGER.debug(f"Timeout connecting to {URL}")
            return False

        except aiohttp.ClientError as err:
            _LOGGER.debug(f"Connection error to {URL}: {err}")
            return False

    async def async_get_token(
        self, api_key, CONF_USERNAME: str, CONF_PASSWORD: str
    ) -> str:
        """Get the token from the API."""
        URL = f"{self.base_url}/{api_key}"

        # hash the password
        my_pass = hashlib.sha256(CONF_PASSWORD.encode()).hexdigest()
        payload = {"password": my_pass}

        try:
            async with self._session.post(
                URL, timeout=10, headers=self.header, json=payload
            ) as response:  # noqa: PLE1142
                response.raise_for_status()  # Raise an exception for HTTP errors
                _LOGGER.debug(f"Successfully retrieved token from {URL}")
                return await response.json()
        except aiohttp.ClientResponseError as err:
            _LOGGER.debug(f"HTTP error from {URL}: {err.status}")
            return None

        except asyncio.TimeoutError:
            _LOGGER.debug(f"Timeout connecting to {URL}")
            return None

        except aiohttp.ClientError as err:
            _LOGGER.debug(f"Connection error to {URL}: {err}")
            return None

    async def async_query_data(self, api_key) -> str:
        """Query data using the api key."""

        # get URL
        URL = f"{self.base_url}/{api_key}"

        try:
            async with self._session.get(
                URL, timeout=10, headers=self.header
            ) as response:
                response.raise_for_status()  # Raise an exception for HTTP errors
                _LOGGER.debug(f"Successfully retrieved data from {URL}")
                try:
                    data = await response.json()
                    series = self.parse_data(data)
                    return series
                except Exception as exc:
                    _LOGGER.debug(f"Failed to retrieve data: {response.status}")
                    return None
        except aiohttp.ClientResponseError as err:
            _LOGGER.debug(f"HTTP error from {URL}: {err.status}")
            return None

        except asyncio.TimeoutError:
            _LOGGER.debug(f"Timeout connecting to {URL}")
            return None

        except aiohttp.ClientError as err:
            _LOGGER.debug(f"Connection error to {URL}: {err}")
            return None

    async def async_post_request(self, api_key, settings) -> str:
        """Definition API POST call."""

        # get URL
        URL = f"{self.base_url}/{api_key}"

        if settings["task"] == "ControlTask_ChargingElectrical_Start":
            if (
                settings["power_level"] <= MAX_POWER_LEVEL
                and settings["duration"] >= MIN_DURATION
            ):
                data_json = {
                    "TASK": settings["task"],
                    "spin": settings["spin"],
                    "power": settings["power_level"],
                    "soc": settings["soc_level"],
                    "persistent": True,
                    "lifetime": settings["duration"],
                }
        elif settings["task"] == "ControlTask_ChargingElectrical_Stop":
            data_json = {
                "TASK": settings["task"],
                "spin": settings["spin"],
                "persistent": True,
                "lifetime": settings["duration"],
            }
        else:
            _LOGGER.debug("Unknown task: %s", settings["task"])
            return None

        try:
            async with self._session.post(
                URL, timeout=10, headers=self.header, json=data_json
            ) as response:
                response.raise_for_status()  # Raise an exception for HTTP errors
                _LOGGER.debug("Successfully posted data to %s", URL)

        except aiohttp.ClientResponseError as err:
            _LOGGER.debug(f"HTTP error from {URL}: {err.status}")

        except asyncio.TimeoutError:
            _LOGGER.debug(f"Timeout connecting to {URL}")

        except aiohttp.ClientError as err:
            _LOGGER.debug(f"Connection error to {URL}: {err}")

        return None

    def parse_data(self, data: dict) -> str:
        """Function to perform some data parsing in the future."""
        _LOGGER.debug(f"JSON PAYLOAD BASE: {data}")
        return data
