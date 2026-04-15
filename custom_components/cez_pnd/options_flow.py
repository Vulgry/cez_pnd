from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries


class CezPndOptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow pro ČEZ PND."""

    async def async_step_init(self, user_input=None):
        """Jediný krok options flow."""
        preset_values = ["12", "24", "36", "48", "60", "72", "84", "96", "108", "120"]

        if user_input is not None:
            history_months = int(user_input["history_months"])
            history_months = max(1, min(history_months, 120))

            return self.async_create_entry(
                title="Nastavení historie",
                data={"history_months": history_months},
            )

        current = str(self.config_entry.options.get("history_months", 24) or 24)

        if current not in preset_values:
            current = "24"

        schema = vol.Schema(
            {
                vol.Required("history_months", default=current): vol.In(
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
                    }
                )
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema, errors={})