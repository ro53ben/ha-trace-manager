# HA Trace Manager
Trace Manager integration for Home Assistant is a feature that makes it easier to increase/decrease trace debugging of specifed automations/scripts. 

The idea is that you can go to Developer Tools...Actions and choose the "Set Stored Traces" option. From here you can pick one of more Automation/Script entities, set a target number and click the action button. The YAML for each entity will have the required number of traces added/updated.
<img width="1198" height="881" alt="image" src="https://github.com/user-attachments/assets/b390348e-518e-47da-83d3-f7fe26098350" />

HA Trace Manager removes the need to manually edit the YAML for each entity, one at a time.

Using the entity, you will be able to change the number of traces for:

* One of more automations/scripts
* All automations/scripts in a specific room
* All automations/scripts with a specific label
 
## How to install

### HACS

1) Open HACS → Integrations → ⋮ → Custom Repositories

2) Add: https://github.com/ro53ben/ha-trace-manager 

3) Install "HA Trace Manager"

4) Add the following line to your configuration.yaml

trace_manager:

5) Restart Home Assistant


### Manual

You should take the latest [published release](https://github.com/ro53ben/ha-trace-manager/releases). The current state of `beta` will be in flux and therefore possibly subject to change.

To install, place the contents of `custom_components` into the `<config directory>/custom_components` folder of your Home Assistant installation. Once installed, don't forget to restart your home assistant instance for the integration to be picked up.

## How to setup

No setup needed, just go to Settings...Developer Tools...Actions and choose "Set Stored Traces"
