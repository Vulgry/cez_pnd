from __future__ import annotations

import datetime as dt
import logging
import re
from contextlib import closing

import requests

_LOGGER = logging.getLogger(__name__)

PND_START_URL = "https://pnd.cezdistribuce.cz/cezpnd2/external/dashboard/view"
DEFINITION_URL = "https://pnd.cezdistribuce.cz/cezpnd2/external/dashboard/window/definition"
EXPORT_BASE_URL = "https://pnd.cezdistribuce.cz/cezpnd2/external/data/export"


class CezPndClient:
    """Klient pro ČEZ PND – CAS login + CSV."""

    def __init__(
        self,
        username: str,
        password: str,
        device_set_id: int,
        assembly_id: int,
        electrometer_id: int,
    ):
        self._username = username
        self._password = password
        self._device_set_id = device_set_id
        self._assembly_id = assembly_id
        self._electrometer_id = electrometer_id

        # debug statistiky
        self._login_count = 0
        self._request_count = 0

    # ----------------------------------------------------------------------
    # SESSION
    # ----------------------------------------------------------------------

    def _new_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0"})
        return session

    def create_logged_session(self) -> requests.Session:
        """Vrátí novou přihlášenou session."""
        session = self._new_session()
        self._login(session)
        return session

    def reset_stats(self) -> None:
        """Vynuluje debug statistiky."""
        self._login_count = 0
        self._request_count = 0

    # ----------------------------------------------------------------------
    # LOGIN
    # ----------------------------------------------------------------------

    def _login(self, session: requests.Session) -> None:
        self._login_count += 1

        r = session.get(PND_START_URL, allow_redirects=True, timeout=30)
        r.raise_for_status()

        if "cas.cez.cz/cas/login" not in r.url:
            return

        m = re.search(r'name="execution"\s+value="([^"]+)"', r.text)
        if not m:
            raise RuntimeError("CAS login: missing execution token")

        payload = {
            "username": self._username,
            "password": self._password,
            "execution": m.group(1),
            "_eventId": "submit",
            "geolocation": "",
        }

        r2 = session.post(r.url, data=payload, allow_redirects=True, timeout=30)
        r2.raise_for_status()

        if "pnd.cezdistribuce.cz" not in r2.url:
            raise RuntimeError("CAS login failed")

    # ----------------------------------------------------------------------
    # LIST DEVICES (config_flow)
    # ----------------------------------------------------------------------

    def list_devices(self) -> dict:
        with closing(self.create_logged_session()) as session:
            r = session.get(DEFINITION_URL, timeout=30)
            r.raise_for_status()
            data = r.json()

        return {
            "assembly_id": data["assemblies"][0]["value"],
            "device_set_id": data["deviceSets"][0]["value"],
            "electrometers": [
                {"id": e["value"], "label": e["label"]}
                for e in data["electrometers"]
            ],
        }

    # ----------------------------------------------------------------------
    # CSV DOWNLOAD
    # ----------------------------------------------------------------------

    def _download_csv_with_session(
        self,
        session: requests.Session,
        start: dt.datetime,
        end: dt.datetime,
    ) -> str:
        self._request_count += 1

        params = {
            "format": "csv-stats",
            "idAssembly": str(self._assembly_id),
            "idDeviceSet": str(self._device_set_id),
            "intervalFrom": start.strftime("%d.%m.%Y %H:%M"),
            "intervalTo": end.strftime("%d.%m.%Y %H:%M"),
            "compareFrom": "",
            "opmId": "",
            "electrometerId": str(self._electrometer_id),
            "splitStrategy": "",
        }

        r = session.get(EXPORT_BASE_URL, params=params, timeout=60)
        r.raise_for_status()
        return r.text

    def _download_csv(self, start: dt.datetime, end: dt.datetime) -> str:
        """Fallback režim – vytvoří vlastní session, přihlásí se a stáhne CSV."""
        with closing(self.create_logged_session()) as session:
            return self._download_csv_with_session(session, start, end)

    # ----------------------------------------------------------------------
    # PARSE CSV
    # ----------------------------------------------------------------------

    @staticmethod
    def parse_kwh_from_csv(csv: str) -> float:
        lines = csv.splitlines()
        if len(lines) < 2:
            return 0.0

        header = [h.strip('"\ufeff ') for h in lines[0].split(";")]
        row = [d.strip('"\ufeff ') for d in lines[1].split(";")]

        normalized = [h.lower().replace(" ", "") for h in header]

        try:
            idx = next(i for i, h in enumerate(normalized) if "celkemvintervalu" in h)
        except StopIteration:
            try:
                idx = next(i for i, h in enumerate(normalized) if h == "celkem")
            except StopIteration:
                return 0.0

        raw = row[idx].lower().replace("kwh", "").replace(" ", "")

        if "," in raw and "." in raw:
            if raw.rfind(".") > raw.rfind(","):
                raw = raw.replace(",", "")
            else:
                raw = raw.replace(".", "").replace(",", ".")
        elif "," in raw:
            raw = raw.replace(",", ".")

        try:
            return float(raw)
        except Exception:
            return 0.0

    # ----------------------------------------------------------------------
    # PUBLIC API
    # ----------------------------------------------------------------------

    def get_day_consumption(
        self,
        date: dt.date,
        session: requests.Session | None = None,
    ) -> float:
        start = dt.datetime(date.year, date.month, date.day)
        end = start + dt.timedelta(days=1)

        if session is not None:
            return self.parse_kwh_from_csv(
                self._download_csv_with_session(session, start, end)
            )

        return self.parse_kwh_from_csv(self._download_csv(start, end))

    def get_month_consumption(
        self,
        year: int,
        month: int,
        session: requests.Session | None = None,
    ) -> float:
        start = dt.datetime(year, month, 1)
        end = (
            dt.datetime(year + 1, 1, 1)
            if month == 12
            else dt.datetime(year, month + 1, 1)
        )

        if session is not None:
            return self.parse_kwh_from_csv(
                self._download_csv_with_session(session, start, end)
            )

        return self.parse_kwh_from_csv(self._download_csv(start, end))

    def get_year_consumption(
        self,
        year: int,
        session: requests.Session | None = None,
    ) -> float:
        total = 0.0
        for month in range(1, 13):
            total += self.get_month_consumption(year, month, session=session)
        return total