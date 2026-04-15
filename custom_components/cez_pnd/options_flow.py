from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback


class CezPndOptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow pro ČEZ PND."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """První krok options flow."""
        if user_input is not None:
            preset = user_input["history_preset"]
            custom_val = user_input.get("history_months")

            if preset != "custom":
                history_months = int(preset)
            else:
                try:
                    history_months = int(custom_val)
                except (TypeError, ValueError):
                    history_months = 24

            history_months = max(1, min(history_months, 120))

            return self.async_create_entry(
                title="Nastavení historie",
                data={"history_months": history_months},
            )

        current = int(self.config_entry.options.get("history_months", 24) or 24)

        preset_values = [12, 24, 36, 48, 60, 72, 84, 96, 108, 120]

        if current in preset_values:
            current_preset = str(current)
        else:
            current_preset = "custom"

        schema = vol.Schema(
            {
                vol.Required("history_preset", default=current_preset): vol.In(
                    {
                        "12": "12 měsíců",
                        "24": "24 měsíců",
                        "36": "36 měsíců",
                        "48": "48 měsíců",
                        "60": "60 měsíců",
                        "72": "72 měsíců",
                        "84": "84 měsíců",
                        "96": "96 měsíců",
                        "108": "108 měsíců",
                        "120": "120 měsíců",
                        "custom": "Vlastní počet měsíců",
                    }
                ),
                vol.Optional("history_months", default=current): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=120)
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema, errors={})