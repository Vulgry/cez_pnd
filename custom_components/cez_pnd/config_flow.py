from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .api import CezPndClient


class CezPndFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Konfigurační průvodce."""

    VERSION = 1

    def __init__(self):
        self._username = None
        self._password = None
        self._device_options = None

    # --------------------------------------
    # KROK 1: EMAIL + HESLO
    # --------------------------------------
    async def async_step_user(self, user_input=None):
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required("username"): str,
                        vol.Required("password"): str,
                    }
                ),
            )

        self._username = user_input["username"]
        self._password = user_input["password"]

        # otestujeme login + načteme zařízení
        try:
            client = CezPndClient(
                self._username,
                self._password,
                device_set_id=0,
                assembly_id=0,
                electrometer_id=0,
            )
            devices = await self.hass.async_add_executor_job(client.list_devices)
            self._device_options = devices

        except Exception as e:
            return self.async_show_form(
                step_id="user",
                errors={"base": "login_failed"},
                data_schema=vol.Schema(
                    {
                        vol.Required("username"): str,
                        vol.Required("password"): str,
                    }
                ),
            )

        return await self.async_step_select_meter()

    # --------------------------------------
    # KROK 2: VÝBĚR ELEKTROMĚRU
    # --------------------------------------
    async def async_step_select_meter(self, user_input=None):
        meters = self._device_options["electrometers"]

        # vytvoříme volby např. "ELM 60228277"
        choices = {m["id"]: m["label"] for m in meters}

        if user_input is None:
            return self.async_show_form(
                step_id="select_meter",
                data_schema=vol.Schema(
                    {vol.Required("electrometer_id"): vol.In(choices)}
                ),
            )

        selected_id = user_input["electrometer_id"]

        return self.async_create_entry(
            title=f"ČEZ PND – {choices[selected_id]}",
            data={
                "username": self._username,
                "password": self._password,
                "assembly_id": -1001,
                "device_set_id": self._device_options["device_set_id"],
                "electrometer_id": selected_id,
            },
        )
