# ⚡ ČEZ PND (neoficiální) – Home Assistant integrace

[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/v/release/Vulgry/cez_pnd)](https://github.com/Vulgry/cez_pnd/releases)
[![License](https://img.shields.io/github/license/Vulgry/cez_pnd)](LICENSE)

Neoficiální integrace pro načítání spotřeby elektroměru z portálu **ČEZ PND** do Home Assistantu.

---

## ✨ Funkce

- 📅 Spotřeba dnes
- 📆 Spotřeba včera
- 🗓️ Spotřeba tento měsíc
- 📉 Spotřeba minulý měsíc
- 📈 Spotřeba tento a minulý rok
- 🗂 Historie spotřeby po měsících
- ⚙️ Automatická detekce elektroměrů
- 🔋 Podpora Energy Dashboardu

---

## 📦 Instalace

### 🔹 HACS (doporučeno)

1. Otevři **HACS**
2. Klikni na **⋮ → Custom repositories**
3. Přidej:

https://github.com/Vulgry/cez_pnd

4. Typ: **Integration**
5. Nainstaluj integraci
6. Restartuj Home Assistant

---

### 🔹 Ruční instalace

Zkopíruj složku do:


/config/custom_components/cez_pnd


Restartuj Home Assistant.

---

## ⚙️ Konfigurace

### Přidání integrace


Nastavení → Integrace → Přidat integraci → ČEZ PND


### Přihlášení

Zadej:
- e-mail
- heslo do portálu ČEZ PND

### Výběr elektroměru

Integrace automaticky načte dostupné elektroměry, např.:


ELM 96645
ELM 60224247


---

## 📊 Dostupné senzory

| Senzor | Popis |
|------|------|
| Spotřeba dnes | aktuální den |
| Spotřeba včera | předchozí den |
| Spotřeba tento měsíc | aktuální měsíc |
| Spotřeba minulý měsíc | předchozí měsíc |
| Spotřeba tento rok | od 1. 1. |
| Spotřeba minulý rok | celý minulý rok |
| Historie | atribut `history` (YYYY-MM → kWh) |

---

## 📈 Energy Dashboard

Integrace je kompatibilní s Home Assistant Energy Dashboardem.

---

## ⚡ Výkon

- 1 login na update
- minimalizace requestů
- cache historických dat
- inkrementální aktualizace

---

## 🔒 Bezpečnost

- přihlašovací údaje jsou uloženy v HA
- heslo se neloguje
- komunikace probíhá přes HTTPS (CAS login)
- žádná data se neposílají třetím stranám

---

## ⚠️ Omezení

- neoficiální integrace
- závislá na dostupnosti ČEZ PND
- změny na straně ČEZ mohou integraci rozbít

---

## 🐞 Hlášení chyb

👉 https://github.com/Vulgry/cez_pnd/issues

---

## ❤️ Podpora

Pokud ti integrace pomohla, můžeš mě podpořit:

[![Buy Me a Coffee](https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&slug=Vulgry&button_colour=FFDD00&font_colour=000000&outline_colour=000000&coffee_colour=ffffff)](https://buymeacoffee.com/Vulgry)

---

## 📜 Licence

MIT