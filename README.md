# NEStore integration for Home Assistant

This is a custom integration that supports reading information from a local Nestore waterbattery systems via the official REST API. This integration is loosely based on the same structure used in other API integrations for HA (such as ENTSO-E). This is my first ever custom integration so obviously I have no clue what I am doing and I am learning along the way, with a bit/lot of help from Stackoverflow and Co-Pilot. 

## Installation

This routine is not officially published in HACS or HA (it would require significantly higher code quality to do so and I am already happy with something that works). To install this custom integration follow the steps below.
1. Download the files and place in your custom_components location. Or add this repository to HACS resource list.
2. Restart HA and add Nestore device
    
## Configuration is done in the UI
At the configuration you can select the following
1. System IP address [Must] - You only need the system's IP address to setup the integration if you want to have read-only information for logging purposes. 2. Logging interval - default is every 300s or 5min. Shorther doesn't really make sense. Considering timeouts I would never go below 60s.
3. Enable full logging [Optional] - default is ON
4. Enable control [Optional] - default is ON
5. Username and Password [Optional] - if you want to enable control you need the Password. You can find this in the service manual.

## How it works
Once enabled you will see a Nestore application which shows the main measured parameters that are part of the functional logging. Not all measurement are exported to the integration but only the most relevant ones,
1. State of charge [%] - fraction of available
2. Total state of charge [%] - fraction of total
3. current stored energy [kWh]
4. hot water flow [L/min]
5. pressure [bar]
6. heater power [W]
7. total energy DHW (domestic hot water) [kWh]
8. total heater energy [kWh]
9. total water volume [L]
10. Vessel internal temperature per zone [dC]

In my opinion the total energy counters are not that reliable and I am still investigating what they represent. The most obvious entities of interest are the state of charge and pressure. Well operating systems should have pressures in the range of 2-3bar when loaded >50%. Monitoring pressure is a good way of assessing system health. The state of charge is no longer used as a control mechanism to start automatic charging, but instead the remaining volume of volume is used in the algorithm of the supplier. 

## Open items

1. The configuration IP adress is no longer detected in the configuration stage as this requires a reliable way of knowing the host name. Nestore systems have ID's that you could know from your cloud app. But I have not found a reliable way to include in the config, websocket or nmap takes too long.
2. I am working on more advanced controls, like setting timers
<!---->

## Questions, Contributions or other
Normal channels

***

[integration_blueprint]: https://github.com/ludeeus/integration_blueprint
[buymecoffee]: https://www.buymeacoffee.com/ludeeus
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/ludeeus/integration_blueprint.svg?style=for-the-badge
[commits]: https://github.com/ludeeus/integration_blueprint/commits/main
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[exampleimg]: example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/ludeeus/integration_blueprint.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Joakim%20Sørensen%20%40ludeeus-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/ludeeus/integration_blueprint.svg?style=for-the-badge
[releases]: https://github.com/ludeeus/integration_blueprint/releases
