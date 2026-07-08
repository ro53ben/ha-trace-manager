import logging
import voluptuous as vol
from homeassistant import config_entries

DOMAIN = "trace_manager"

class TraceManagerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Trace Manager."""
    
    VERSION = 1

    async def async_step_user(self, user_input=None):
        # Prevent the user from installing it multiple times
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(title="Trace Manager", data={})

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({})
        )