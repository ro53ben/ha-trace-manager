import logging
from ruamel.yaml import YAML
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import entity_registry as er
from homeassistant.config_entries import ConfigEntry

DOMAIN = "trace_manager"
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    
    def modify_yaml(filepath, target_keys, traces, is_script=False):
        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.indent(mapping=2, sequence=4, offset=2)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.load(f)
                
            modified = False
            
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
                entry_reg = registry.async_get(eid)
                if entry_reg and entry_reg.unique_id:
                    auto_ids.append(entry_reg.unique_id)
            elif eid.startswith("script."):
                script_keys.append(eid.split('.')[1])
                
        auto_path = hass.config.path("automations.yaml")
        script_path = hass.config.path("scripts.yaml")
        
        auto_changed = await hass.async_add_executor_job(
            modify_yaml, auto_path, auto_ids, traces, False
        )
        script_changed = await hass.async_add_executor_job(
            modify_yaml, script_path, script_keys, traces, True
        )
        
        if auto_changed:
            await hass.services.async_call("automation", "reload", {})
        if script_changed:
            await hass.services.async_call("script", "reload", {})

    hass.services.async_register(DOMAIN, "set_stored_traces", handle_set_traces)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.services.async_remove(DOMAIN, "set_stored_traces")
    return True