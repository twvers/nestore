# NEStore integration for Home Assistant

This is a custom integration that supports reading information from a local Nestore waterbattery systems via the RESTful API. This integration is loosely based on the same structure used in other API integrations for HA (such as ENTSO-E). This is my first ever custom integration so obviously I have no clue what I am doing and I am learning along the way, with a bit of help of Stackoverflow and Co-pilot. 

## Installation

This routine is not officially published in HACS or HA (it would require significantly higher code quality, so its on the to-do list). Therefore follow the below steps
1. Download the files and place in your custom_components location
2. Restart HA and add Nestore device
    
## Configuration is done in the UI
The configuration IP adress is automatically detected in the configuration stage. If not, this can be overruled in the configuration page (to-do). The configuration has several options
1. Enable full logging (loads all relevant logging)
2. Set polling interval (default is 300s). Recommended is not to increase polling frequency lower than 60s to prevent time-out. 
3. Enable write access - includes switches and manual settings the configuration which enables the system for manual mode. In this way you can control the system via Automations 

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
