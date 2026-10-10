---
name: pricing-update-airbnb
description: >-
  Automatizza l'aggiornamento delle tariffe giornaliere nel calendario host di
  Airbnb tramite un browser già aperto e autenticato sul computer locale.
  Usa questa skill quando l'utente vuole modificare il prezzo per una o più
  date specifiche (fino a 90 giorni) su una proprietà Airbnb identificata dal
  suo ID. Gestisce rate limiting, errori per singola data e produce un report
  finale di successi e fallimenti.
---

# Skill: pricing-update-airbnb

## Descrizione

Questa skill automatizza la modifica delle tariffe nel calendario host Airbnb
operando su una **sessione browser già aperta e autenticata** sul computer
locale (tramite Chrome Remote Debugging Protocol).

---

## Parametri di Input

| Parametro       | Tipo                        | Descrizione                                                                 |
|-----------------|-----------------------------|-----------------------------------------------------------------------------|
| `target_dates`  | Lista di date (dd/mm/yyyy)  | Date da aggiornare. Max 90 date. Può essere un intervallo o una lista puntuale. |
| `new_price`     | Lista di float/int          | Prezzi corrispondenti a ciascuna data in `target_dates` (stessa lunghezza). |
| `property_id`   | Stringa                     | ID della proprietà Airbnb (visibile nell'URL del calendario host).          |

> [!IMPORTANT]
> `target_dates` e `new_price` devono avere la **stessa lunghezza** e lo stesso
> ordine. Se viene fornito un unico prezzo per un intervallo, applicalo a tutte
> le date dell'intervallo.

---

## Prerequisiti

### 1. Avviare Chrome con Remote Debugging (PowerShell)

In PowerShell, usa la sintassi `-ArgumentList` oppure il call operator `&`:

```powershell
# Opzione A — con Start-Process
Start-Process "chrome.exe" -ArgumentList "--remote-debugging-port=9222", "--user-data-dir=C:\ChromeDebug"

# Opzione B — con call operator (più semplice)
& "chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\ChromeDebug"
```

Se `chrome.exe` non è nel PATH, usa il percorso completo:

```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\ChromeDebug"
```

> [!IMPORTANT]
> L'utente deve essere già **loggato su Airbnb** nella sessione Chrome aperta prima di avviare lo script.

### 2. Installare le dipendenze Python

Installa nella directory del progetto usando un **virtual environment**:

```powershell
# Spostati nella directory del progetto
cd "c:\Docs\Personnel et confidentiel\Corsi e Formazioni\2026-06-14 Kaggle_5-Day AI Agents\agy2-projects\my-first-project"

# Crea il venv (solo la prima volta, se non esiste già)
python -m venv .venv

# Attiva il venv
.\.venv\Scripts\Activate.ps1

# Installa le dipendenze
pip install playwright python-dateutil

# Installa il browser Chromium per Playwright
playwright install chromium
```

> [!NOTE]
> Ogni volta che apri un nuovo terminale devi **riattivare il venv** con
> `.\.venv\Scripts\Activate.ps1` prima di eseguire lo script.
> Sai che è attivo quando il prompt mostra `(.venv)` all'inizio.

---

## Logica di Esecuzione

### Passo 1 — Connessione al Browser Esistente

Connettiti alla sessione Chrome già in esecuzione tramite il protocollo CDP
(Chrome DevTools Protocol) usando Playwright o Selenium. Questo preserva
cookie e autenticazione.

```python
# Playwright: connessione a browser esistente
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    context = browser.contexts[0]
    page = context.pages[0]
```

### Passo 2 — Navigazione al Calendario della Proprietà

Controlla l'URL corrente. Se non siamo già sul calendario, naviga verso:

```
https://www.airbnb.com/multicalendar/<property_id>/pricing-and-availability
```

oppure:

```
https://www.airbnb.com/hosting/listings/<property_id>/calendar
```

Attendi che la pagina sia completamente caricata prima di procedere.

### Passo 3 — Iterazione sulle Date (con Rate Limiting)

Per ogni coppia `(data, prezzo)` in `zip(target_dates, new_price)`:

1. **Attesa randomica**: applica un delay tra 2 e 5 secondi prima di ogni
   operazione.
2. **Individua il giorno**: cerca nel DOM il selettore corrispondente alla
   data (es. `[data-testid="calendar-day-YYYY-MM-DD"]` o attributo `aria-label`
   con la data formattata).
3. **Clicca sul giorno** per aprire il pannello/pop-up delle tariffe.
4. **Modifica il prezzo**:
   - Individua il campo di input (`input[type="text"]` o `input[type="number"]`
     con label "Prezzo" / "Price").
   - Cancella il valore attuale con `triple_click` o `Ctrl+A → Delete`.
   - Digita il nuovo prezzo.
5. **Salva**: clicca il pulsante "Salva" / "Save".
6. **Attendi conferma**: aspetta un segnale visivo (es. scomparsa del pannello,
   toast di conferma, o cambio del valore visualizzato nel calendario).

### Passo 4 — Gestione degli Errori

Avvolgi ogni operazione in `try/except`. In caso di errore:
- Aggiungi la data a `failed_updates` con la motivazione.
- **Non interrompere** il loop: continua con la data successiva.

Tipologie di errori da gestire:
- `TimeoutError`: elemento non trovato entro il timeout.
- `ElementNotVisibleError`: elemento presente ma non cliccabile.
- Blocco di sicurezza / CAPTCHA: rilevato tramite presenza di elemento specifico.
- Errore di rete / navigazione.

---

## Script Helper

Usa lo script Python preconfigurato:
[update_airbnb_prices.py](./scripts/update_airbnb_prices.py)

Esegui con:
```bash
python .agents/skills/pricing-update-airbnb/scripts/update_airbnb_prices.py \
  --property-id "12345678" \
  --dates "01/11/2026,02/11/2026,03/11/2026" \
  --prices "150,160,170"
```

---

## Output Finale

Al termine, produci sempre il seguente report:

```
✅ Tariffe aggiornate con successo per le seguenti date:
   - 01/11/2026: € 150
   - 02/11/2026: € 160

❌ Errore nell'aggiornamento per le seguenti date:
   - 03/11/2026: Timeout durante il salvataggio
```

Se tutti i prezzi vengono aggiornati con successo, la sezione ❌ va omessa.
Se tutte le date falliscono, segnala il problema e suggerisci di verificare la
connessione al browser e l'autenticazione.

---

## Note Operative

> [!WARNING]
> Non superare le **90 date** per singola esecuzione. Per intervalli più lunghi,
> suddividi l'aggiornamento in più chiamate consecutive.

> [!TIP]
> Se il browser rileva comportamento automatizzato e mostra un CAPTCHA, interrompi
> lo script, completa manualmente il CAPTCHA, e poi riprendi dall'ultima data
> fallita.

> [!NOTE]
> L'URL esatto del calendario e i selettori DOM possono cambiare con gli
> aggiornamenti di Airbnb. Se uno script fallisce sistematicamente, ispeziona
> il DOM della pagina con i DevTools per aggiornare i selettori nello script.
