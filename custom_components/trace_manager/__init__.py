import logging
from ruamel.yaml import YAML
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import entity_registry as er

DOMAIN = "trace_manager"
_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    
    def modify_yaml(filepath, target_keys, traces, is_script=False):
        # ruamel.yaml safely preserves your existing comments and layout
        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.indent(mapping=2, sequence=4, offset=2)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.load(f)
                
            modified = False
            
            # Scripts use a dictionary structure; automations use a list
            if is_script:
                for key, value in data.items():
                    if key in target_keys:
                        if 'trace' not in value:
                            value['trace'] = {}
                        value['trace']['stored_traces'] = traces
                        modified = True
            else:
                for item in data:
                    if isinstance(item, dict) and item.get('id') in target_keys:
                        if 'trace' not in item:
                            item['trace'] = {}
                        item['trace']['stored_traces'] = traces
                        modified = True
                        
            if modified:
                with open(filepath, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f)
                return True
                
        except Exception as e:
            _LOGGER.error("Trace Manager failed to update %s: %s", filepath, e)
            
        return False

    async def handle_set_traces(call: ServiceCall):
        entity_ids = call.data.get("entity_id", [])
        if isinstance(entity_ids, str):
            entity_ids = [entity_ids]
            
        traces = call.data.get("traces", 50)
        registry = er.async_get(hass)
        auto_ids = []
        script_keys = []
        
        for eid in entity_ids:
            if eid.startswith("automation."):
                entry = registry.async_get(eid)
                if entry and entry.unique_id:
                    auto_ids.append(entry.unique_id)
            elif eid.startswith("script."):
                # Scripts created via the UI use their alias key directly in the YAML
                script_keys.append(eid.split('.')[1])
                
        auto_path = hass.config.path("automations.yaml")
        script_path = hass.config.path("scripts.yaml")
        
        # Execute file I/O safely outside the main event loop
        auto_changed = await hass.async_add_executor_job(
            modify_yaml, auto_path, auto_ids, traces, False
        )
        script_changed = await hass.async_add_executor_job(
            modify_yaml, script_path, script_keys, traces, True
        )
        
        # Automatically reload only if changes were written
        if auto_changed:
            await hass.services.async_call("automation", "reload", {})
        if script_changed:
            await hass.services.async_call("script", "reload", {})

    # Register the action to appear in the Developer Tools UI
    hass.services.async_register(DOMAIN, "set_stored_traces", handle_set_traces)
    return True