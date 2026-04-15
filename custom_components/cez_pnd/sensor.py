from __future__ import annotations

import datetime as dt
import logging
import time
from contextlib import closing
from datetime import timedelta
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import CezPndClient

_LOGGER = logging.getLogger(__name__)


def _month_key(year: int, month: int) -> str:
    return f"{year:04d}-{month:02d}"


def _shift_month(year: int, month: int) -> tuple[int, int]:
    if month == 1:
        return year - 1, 12
    return year, month - 1


def _recent_month_keys(today: dt.date, count: int) -> list[str]:
    keys: list[str] = []
    year = today.year
    month = today.month
    for _ in range(count):
        keys.append(_month_key(year, month))
        year, month = _shift_month(year, month)
    return keys


def _parse_dt(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    try:
        parsed = dt.datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=dt.timezone.utc)
        return parsed
    except Exception:
        return None


class CezPndCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Jeden koordinátor pro všechny senzory."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: CezPndClient,
    ) -> None:
        self.hass = hass
        self.entry = entry
        self.client = client
        self.store = Store(hass, 1, f"cez_pnd_{entry.entry_id}_cache")
        self._store_loaded = False
        self._month_cache: dict[str, float] = {}
        self._last_yesterday_refresh: dt.datetime | None = None
        self._last_monthly_refresh: dt.datetime | None = None

        super().__init__(
            hass,
            _LOGGER,
            name="ČEZ PND",
            update_interval=timedelta(minutes=15),
        )

    @property
    def history_months(self) -> int:
        configured = int(self.entry.options.get("history_months", 24))
        return max(1, min(configured, 120))

    async def _async_load_store_once(self) -> None:
        if self._store_loaded:
            return

        payload = await self.store.async_load() or {}
        raw_cache = payload.get("month_cache", {}) or {}
        self._month_cache = {
            str(key): float(value)
            for key, value in raw_cache.items()
            if value is not None
        }

        self._last_yesterday_refresh = _parse_dt(payload.get("last_yesterday_refresh"))
        self._last_monthly_refresh = _parse_dt(payload.get("last_monthly_refresh"))

        stored_data = payload.get("data")
        if isinstance(stored_data, dict) and self.data is None:
            self.data = stored_data

        self._store_loaded = True

    def _should_refresh_yesterday(self, now_utc: dt.datetime) -> bool:
        if not self.data or "yesterday" not in self.data:
            return True
        if self._last_yesterday_refresh is None:
            return True
        return (now_utc - self._last_yesterday_refresh) >= timedelta(hours=6)

    def _should_refresh_monthly(
        self,
        today: dt.date,
        now_utc: dt.datetime,
    ) -> bool:
        if not self.data or "history" not in self.data:
            return True

        if int(self.data.get("history_months", 0)) != self.history_months:
            return True

        if self._last_monthly_refresh is None:
            return True

        if (now_utc - self._last_monthly_refresh) >= timedelta(hours=24):
            return True

        current_key = _month_key(today.year, today.month)
        history = self.data.get("history", {}) or {}
        return current_key not in history

    def _prune_month_cache(self, today: dt.date) -> None:
        keep_count = max(self.history_months, 24)
        keep_keys = set(_recent_month_keys(today, keep_count))
        self._month_cache = {
            key: value
            for key, value in self._month_cache.items()
            if key in keep_keys
        }

    async def _async_save_store(self) -> None:
        payload = {
            "month_cache": {k: round(float(v), 3) for k, v in self._month_cache.items()},
            "last_yesterday_refresh": (
                self._last_yesterday_refresh.isoformat()
                if self._last_yesterday_refresh
                else None
            ),
            "last_monthly_refresh": (
                self._last_monthly_refresh.isoformat()
                if self._last_monthly_refresh
                else None
            ),
            "data": self.data,
        }
        await self.store.async_save(payload)

    async def _async_update_data(self) -> dict[str, Any]:
        await self._async_load_store_once()

        start_time = time.time()
        self.client.reset_stats()

        stats = {
            "cache_hits": 0,
            "downloads": 0,
        }

        now_utc = dt.datetime.now(dt.timezone.utc)
        today = dt.date.today()
        yesterday = today - dt.timedelta(days=1)

        current_data = dict(self.data or {})

        refresh_yesterday = self._should_refresh_yesterday(now_utc)
        refresh_monthly = self._should_refresh_monthly(today, now_utc)
        refresh_day = True

        def _fetch() -> dict[str, Any]:
            result: dict[str, Any] = {}
            runtime_month_cache: dict[str, float] = {}

            with closing(self.client.create_logged_session()) as session:

                if refresh_day:
                    result["day"] = round(
                        float(self.client.get_day_consumption(today, session=session)),
                        3,
                    )

                if refresh_yesterday:
                    result["yesterday"] = round(
                        float(self.client.get_day_consumption(yesterday, session=session)),
                        3,
                    )

                if refresh_monthly:
                    current_key = _month_key(today.year, today.month)

                    if today.month == 1:
                        last_month_year = today.year - 1
                        last_month_num = 12
                    else:
                        last_month_year = today.year
                        last_month_num = today.month - 1

                    last_month_key = _month_key(last_month_year, last_month_num)
                    old_history = (current_data.get("history", {}) or {}).copy()

                    def get_month(
                        year: int,
                        month: int,
                        *,
                        force_refresh: bool = False,
                    ) -> float:
                        key = _month_key(year, month)

                        if not force_refresh:
                            if key in runtime_month_cache:
                                stats["cache_hits"] += 1
                                return runtime_month_cache[key]

                            if key in self._month_cache:
                                stats["cache_hits"] += 1
                                runtime_month_cache[key] = float(self._month_cache[key])
                                return runtime_month_cache[key]

                        stats["downloads"] += 1
                        value = float(
                            self.client.get_month_consumption(
                                year,
                                month,
                                session=session,
                            )
                        )
                        runtime_month_cache[key] = value
                        return value

                    history: dict[str, float] = {}
                    year = today.year
                    month = today.month

                    for _ in range(self.history_months):
                        key = _month_key(year, month)

                        if key == current_key or key == last_month_key:
                            history[key] = round(
                                get_month(year, month, force_refresh=True),
                                3,
                            )
                        elif key in old_history:
                            history[key] = round(float(old_history[key]), 3)
                            if key not in self._month_cache:
                                self._month_cache[key] = float(old_history[key])
                        else:
                            history[key] = round(get_month(year, month), 3)

                        year, month = _shift_month(year, month)

                    result["this_month"] = round(
                        get_month(today.year, today.month, force_refresh=True),
                        3,
                    )
                    result["last_month"] = round(
                        get_month(last_month_year, last_month_num, force_refresh=True),
                        3,
                    )
                    result["this_year"] = round(
                        sum(
                            get_month(
                                today.year,
                                month,
                                force_refresh=(month == today.month),
                            )
                            for month in range(1, today.month + 1)
                        ),
                        3,
                    )

                    last_year = today.year - 1
                    result["last_year"] = round(
                        sum(get_month(last_year, month) for month in range(1, 13)),
                        3,
                    )
                    result["history"] = history
                    result["history_months"] = self.history_months
                    result["month_cache_updates"] = runtime_month_cache

            return result

        try:
            fetched = await self.hass.async_add_executor_job(_fetch)
        except Exception as err:
            raise UpdateFailed(f"ČEZ PND update failed: {err}") from err

        if refresh_day and "day" in fetched:
            current_data["day"] = fetched["day"]

        if refresh_yesterday and "yesterday" in fetched:
            current_data["yesterday"] = fetched["yesterday"]
            self._last_yesterday_refresh = now_utc

        if refresh_monthly:
            for key, value in fetched.get("month_cache_updates", {}).items():
                self._month_cache[key] = round(float(value), 3)

            self._prune_month_cache(today)
            self._last_monthly_refresh = now_utc

            current_data["this_month"] = fetched["this_month"]
            current_data["last_month"] = fetched["last_month"]
            current_data["this_year"] = fetched["this_year"]
            current_data["last_year"] = fetched["last_year"]
            current_data["history"] = fetched["history"]
            current_data["history_months"] = fetched["history_months"]

        self.data = current_data
        await self._async_save_store()

        duration = round(time.time() - start_time, 2)
        _LOGGER.warning(
            "CEZ PND DEBUG:\n"
            "duration: %ss\n"
            "logins: %s\n"
            "requests: %s\n"
            "downloads (months): %s\n"
            "cache hits: %s\n"
            "history size: %s",
            duration,
            self.client._login_count,
            self.client._request_count,
            stats["downloads"],
            stats["cache_hits"],
            len(current_data.get("history", {})),
        )

        return current_data


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Nastavení senzorů po vytvoření config entry."""

    data = entry.data

    client = CezPndClient(
        username=data["username"],
        password=data["password"],
        device_set_id=int(data["device_set_id"]),
        assembly_id=int(data["assembly_id"]),
        electrometer_id=int(data["electrometer_id"]),
    )

    coordinator = CezPndCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()

    entities: list[SensorEntity] = [
        CezPndDaySensor(coordinator),
        CezPndYesterdaySensor(coordinator),
        CezPndThisMonthSensor(coordinator),
        CezPndLastMonthSensor(coordinator),
        CezPndThisYearSensor(coordinator),
        CezPndLastYearSensor(coordinator),
        CezPndHistorySensor(coordinator),
    ]

    async_add_entities(entities)


class _BaseCezPndSensor(CoordinatorEntity[CezPndCoordinator], SensorEntity):
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR

    @staticmethod
    def _round(val: float | None) -> float | None:
        if val is None:
            return None
        return round(float(val), 3)


class CezPndDaySensor(_BaseCezPndSensor):
    _attr_name = "ČEZ PND – Spotřeba dnes"
    _attr_unique_id = "cez_pnd_spotreba_dnes"

    @property
    def native_value(self) -> float | None:
        data = self.coordinator.data or {}
        return self._round(data.get("day"))


class CezPndYesterdaySensor(_BaseCezPndSensor):
    _attr_name = "ČEZ PND – Spotřeba včera"
    _attr_unique_id = "cez_pnd_vcera_spotreba"

    @property
    def native_value(self) -> float | None:
        data = self.coordinator.data or {}
        return self._round(data.get("yesterday"))


class CezPndThisMonthSensor(_BaseCezPndSensor):
    _attr_name = "ČEZ PND – Spotřeba tento měsíc"
    _attr_unique_id = "cez_pnd_spotreba_tento_mesic"

    @property
    def native_value(self) -> float | None:
        data = self.coordinator.data or {}
        return self._round(data.get("this_month"))


class CezPndLastMonthSensor(_BaseCezPndSensor):
    _attr_name = "ČEZ PND – Spotřeba minulý měsíc"
    _attr_unique_id = "cez_pnd_spotreba_minuly_mesic"

    @property
    def native_value(self) -> float | None:
        data = self.coordinator.data or {}
        return self._round(data.get("last_month"))


class CezPndThisYearSensor(_BaseCezPndSensor):
    _attr_name = "ČEZ PND – Spotřeba tento rok"
    _attr_unique_id = "cez_pnd_spotreba_tento_rok"

    @property
    def native_value(self) -> float | None:
        data = self.coordinator.data or {}
        return self._round(data.get("this_year"))


class CezPndLastYearSensor(_BaseCezPndSensor):
    _attr_name = "ČEZ PND – Spotřeba minulý rok"
    _attr_unique_id = "cez_pnd_spotreba_minuly_rok"

    @property
    def native_value(self) -> float | None:
        data = self.coordinator.data or {}
        return self._round(data.get("last_year"))


class CezPndHistorySensor(_BaseCezPndSensor):
    _attr_unique_id = "cez_pnd_historie_mesicu"

    @property
    def name(self) -> str:
        data = self.coordinator.data or {}
        hm = data.get("history_months", self.coordinator.history_months)
        return f"ČEZ PND – Historie za {hm} měsíců"

    @property
    def native_value(self) -> float | None:
        data = self.coordinator.data or {}
        history: dict[str, float] = data.get("history", {}) or {}
        total = sum(float(v) for v in history.values())
        return self._round(total)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        history = data.get("history", {}) or {}
        hm = data.get("history_months", self.coordinator.history_months)
        rounded_history = {k: round(float(v), 3) for k, v in history.items()}
        return {
            "history": rounded_history,
            "history_months": hm,
        }