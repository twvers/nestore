"""Constants for the nestore integration."""

DOMAIN = "nestore"
ATTRIBUTION = "Local Data from NEStore"
UNIQUE_ID = f"{DOMAIN}_component"
COMPONENT_TITLE = "NEStore Data Platform"

CONF_API_KEY = "api_key"
CONF_HOST = "localhost"
CONF_ENTITY_NAME = "name"
CONF_PORT = "port"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_UPDATE_INTERVAL = "Interval"
CONF_FULL_LOGGING = "All sensor logging"
CONF_CONTROL = "Allow control"

DEFAULT_HOST = "192.168.1.100"
DEFAULT_PORT = 4805
DEFAULT_USERNAME = ""
DEFAULT_PASSWORD = ""
DEFAULT_INTERVAL = 60
DEFAULT_LOGGING = True
DEFAULT_CONTROL = True

DEFAULT_LOC_DATA = "api/v1/data/engineering"
DEFAULT_LOC_MEAS = "api/v1/data/measured"
DEFAULT_LOC_CONTROLLER = "api/v1/data/controller"
DEFAULT_LOC_ACTIVE = "api/v1/configuration/installer/active"
DEFAULT_LOC_INPUT = "api/v1/configuration/settings/input"
DEFAULT_LOC_FLAG = "api/v1/controller/flags"

MAX_POWER_LEVEL = 3400
MIN_POWER_LEVEL = 1000

DATETIMEFORMAT = "%Y%m%d%H00"
