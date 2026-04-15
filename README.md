# ⚡ ČEZ PND (neoficiální) – Home Assistant integrace

Neoficiální integrace pro načítání spotřeby elektroměru z portálu **ČEZ PND**.

---

## ✨ Funkce

Integrace umožňuje sledovat:

- 📅 **Spotřebu dnes**
- 📆 **Spotřebu tento měsíc**
- 📈 **Spotřebu za tento a minulý rok**
- 🗂 **Historii spotřeby až 24 měsíců (po měsících)**
- ⚙️ **Automatickou detekci elektroměrů z PND**

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

1. Stáhni složku `cez_pnd`
2. Zkopíruj ji do:

/config/custom_components/cez_pnd

3. Restartuj Home Assistant

---

## ⚙️ Konfigurace

### 1️⃣ Přidání integrace

Nastavení → Integrace → Přidat integraci → ČEZ PND

---

### 2️⃣ Přihlášení

Zadej:

- 📧 e-mail (uživatelské jméno)
- 🔑 heslo (login do ČEZ PND)

---

### 3️⃣ Výběr elektroměru

Integrace automaticky načte dostupné elektroměry:

ELM 96645
ELM 60224447

Vyber požadovaný elektroměr a potvrď.

---

## 📊 Dostupné senzory

| Název | Popis |
|------|------|
| ČEZ PND – Spotřeba dnes | aktuální den |
| ČEZ PND – Spotřeba včera | předchozí den |
| ČEZ PND – Spotřeba tento měsíc | aktuální měsíc |
| ČEZ PND – Spotřeba minulý měsíc | předchozí měsíc |
| ČEZ PND – Spotřeba tento rok | od 1. 1. |
| ČEZ PND – Spotřeba minulý rok | celý minulý rok |
| ČEZ PND – Historie | atribut `history` (YYYY-MM → kWh) |

---

## 🔒 Bezpečnost

- přihlašovací údaje jsou uloženy v Home Assistant Config Entry
- heslo se nikde neloguje
- komunikace probíhá přes HTTPS (CAS login)
- žádná data se neposílají třetím stranám

---

## ⚠️ Omezení

- integrace není oficiálně podporována ČEZem
- závisí na dostupnosti portálu PND
- změny na straně ČEZ mohou integraci rozbít

---

## 🐞 Hlášení chyb / Feature request

Použij:
👉 https://github.com/Vulgry/cez_pnd/issues

---

## 🤝 Přispívání

Uvítáme:

- pull requesty
- bug reporty
- návrhy funkcí

---

## 📜 Licence

MIT License

---

## ❤️ Podpora

Pokud ti integrace pomohla, můžeš mě podpořit:

https://buymeacoffee.com/Vulgry
