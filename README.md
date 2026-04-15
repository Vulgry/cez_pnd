ČEZ PND (neoficiální) – Home Assistant integrace



⚡ Neoficiální integrace pro načítání spotřeby elektroměru z portálu ČEZ PND

Pomocí této integrace můžete v Home Assistantu sledovat:



📅 dnešní spotřebu



📆 měsíční spotřebu



📈 spotřebu za tento a minulý rok



🗂 historii za posledních až 24 měsíců



⚙ automatickou detekci dostupných elektroměrů z PND



podporu Energy Dashboardu (HA Energy)



🛠 Instalace

1\) Ruční instalace



Stáhněte složku cez\_pnd



Zkopírujte ji do:



/config/custom\_components/cez\_pnd





Restartujte Home Assistant.



🔧 Konfigurace

1️⃣ Přidání integrace



V Home Assistant:



Nastavení → Integrace → Přidat integraci → ČEZ PND



2️⃣ Krok 1 – přihlášení



Zadejte:



e-mail (uživatelské jméno)



heslo k portálu PND (CAS)



3️⃣ Krok 2 – výběr elektroměru



Integrace automaticky načte dostupné elektroměry, např.:



ELM 96645

ELM 60224247



Vyberte jeden a potvrďte.



📊 Dostupné senzory

Název senzoru	Popis

ČEZ PND – Spotřeba dnes	spotřeba za aktuální den

ČEZ PND – Spotřeba tento měsíc	součet spotřeby za aktuální měsíc

ČEZ PND – Spotřeba tento rok	spotřeba od 1. 1. daného roku

ČEZ PND – Spotřeba minulý rok	spotřeba za předchozí kalendářní rok

ČEZ PND – Historie za 24 měsíců	atribut s hodnotami po měsících (YYYY-MM → kWh)



🔒 Bezpečnost



přihlašovací údaje jsou uloženy jako součást HA Config Entry

heslo není nikde logováno

komunikace probíhá přímo na portál ČEZ přes HTTPS (CAS login)

neodesílají se žádná data třetím stranám



🤝 Přispívání



Rádi uvítáme:



pull requesty

hlášení chyb

návrhy na rozšíření



