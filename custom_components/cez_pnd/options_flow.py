from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN


class CezPndOptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow pro ČEZ PND."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """První (a jediný) krok options flow."""
        if user_input is not None:
            preset = user_input["history_preset"]
            custom_val = user_input.get("history_months") or 24

            if preset != "custom":
                history_months = int(preset)
            else:
                history_months = int(custom_val)

            return self.async_create_entry(
                title="Nastavení historie",
                data={"history_months": history_months},
            )

        current = self.config_entry.options.get("history_months", 24)

        if current in (12, 24, 36, 60):
            current_preset = str(current)
            current_custom = current
        else:
            current_preset = "custom"
            current_custom = current

        schema = vol.Schema(
            {
                vol.Required("history_preset", default=current_preset): vol.In(
                    {
                        "12": "Posledních 12 měsíců",
                        "24": "Posledních 24 měsíců (doporučeno)",
                        "36": "Posledních 36 měsíců",
                        "60": "Posledních 60 měsíců",
                        "custom": "Vlastní počet měsíců",
                    }
                ),
                vol.Optional("history_months", default=current_custom): vol.All(
                    int, vol.Range(min=1, max=120)
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema, errors={})

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return CezPndOptionsFlowHandler(config_entry)
