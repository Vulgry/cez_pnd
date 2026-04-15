from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Inicializace integrace ČEZ PND."""
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Odpojení integrace."""
    return await hass.config_entries.async_unload_platforms(entry, ["sensor"])


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload při změně options."""
    await hass.config_entries.async_reload(entry.entry_id)