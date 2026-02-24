"""Constants for the nestore integration."""

DOMAIN = "nestore"
ATTRIBUTION = "Local Data from NEStore"
UNIQUE_ID = f"{DOMAIN}_component"
COMPONENT_TITLE = "NEStore Data Platform"

CONF_API_KEY = "api_key"
CONF_TOKEN = "token"
CONF_HOST = "localhost"
CONF_ENTITY_NAME = "name"
CONF_PORT = "port"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_UPDATE_INTERVAL = "Interval"
CONF_FULL_LOGGING = "All sensor logging"
CONF_CONTROL = "Allow control"

DEFAULT_HOST = "192.168.1.197"
DEFAULT_PORT = 4805
DEFAULT_USERNAME = ""
DEFAULT_PASSWORD = ""
DEFAULT_INTERVAL = 300
DEFAULT_LOGGING = True
DEFAULT_CONTROL = True

DEFAULT_LOC_DATA = "api/v3/data/engineering"
DEFAULT_LOC_MEAS = "api/v3/data/measured"
DEFAULT_LOC_CONTROLLER = "api/v3/data/control_state"
DEFAULT_LOC_ACTIVE = "api/v3/configuration/active"
DEFAULT_LOC_INPUT = "api/v3/configuration/settings/input"
DEFAULT_LOC_FLAG = "api/v3/control/task"
DEFAULT_LOC_TOKEN = "api/v3/auth/requesttoken"

MAX_POWER_LEVEL = 3400
MIN_POWER_LEVEL = 1000
MIN_DURATION = 1799
MAX_DURATION = 18001

UPDATE_DELAY = 30
DATETIMEFORMAT = "%Y%m%d%H00"
