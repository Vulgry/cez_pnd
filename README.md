# ⚡ ČEZ PND (neoficiální) – Home Assistant integrace

[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![Version](https://img.shields.io/github/v/release/Vulgry/cez_pnd?style=for-the-badge)](https://github.com/Vulgry/cez_pnd/releases)
[![License](https://img.shields.io/github/license/Vulgry/cez_pnd?style=for-the-badge)](LICENSE)

Neoficiální integrace pro načítání spotřeby elektroměru z portálu **ČEZ PND** do Home Assistantu.

---

## Instalace přes HACS

[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?repository=https://github.com/Vulgry/cez_pnd&category=integration)

Po kliknutí na tlačítko se repozitář otevře přímo v HACS.

### Postup

1. Přidej repozitář do HACS
2. Nainstaluj integraci
https://github.com/Vulgry/cez_pnd

3. Restartuj Home Assistant
4. Otevři **Nastavení → Integrace**
5. Přidej **ČEZ PND**

### Nastavení

- zadej přihlašovací údaje do ČEZ PND
- vyber elektroměr
- integrace začne načítat data


### 🔹 Ruční instalace

Zkopíruj složku do:


/config/custom_components/cez_pnd


Restartuj Home Assistant.



## ⚙️ Konfigurace

### Přidání integrace


Nastavení → Integrace → Přidat integraci → ČEZ PND


### Přihlášení

Zadej:
- e-mail
- heslo do portálu ČEZ PND

### Výběr elektroměru

Integrace automaticky načte dostupné elektroměry, např.:


* ELM 96645

* ELM 60224247


### Nastavení historie

U senzoru historie lze nastavit, kolik měsíců zpětně se má načítat.

K dispozici jsou:

rychlé volby po 12 měsících
vlastní hodnota
rozsah 1 až 120 měsíců

Nastavení změníš v:

Nastavení → Zařízení a služby → ČEZ PND → Konfigurovat

---

## 📊 Dostupné senzory


| Entita | Typ | Popis |
|--------|-----|------|
| `sensor.cez_pnd_spotreba_dnes` | Sensor (kWh) | Spotřeba za aktuální den |
| `sensor.cez_pnd_vcera_spotreba` | Sensor (kWh) | Spotřeba za předchozí den |
| `sensor.cez_pnd_spotreba_tento_mesic` | Sensor (kWh) | Spotřeba za aktuální měsíc |
| `sensor.cez_pnd_spotreba_minuly_mesic` | Sensor (kWh) | Spotřeba za minulý měsíc |
| `sensor.cez_pnd_spotreba_tento_rok` | Sensor (kWh) | Spotřeba od začátku roku |
| `sensor.cez_pnd_spotreba_minuly_rok` | Sensor (kWh) | Spotřeba za celý minulý rok |
| `sensor.cez_pnd_historie_mesicu` | Sensor (kWh) | Součet historie + atribut `history` (YYYY-MM → kWh) |


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

[![Buy me a coffee](https://img.shields.io/badge/Buy_me_a_coffee-Odměň_mě_kávou-yellow?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/Vulgry)