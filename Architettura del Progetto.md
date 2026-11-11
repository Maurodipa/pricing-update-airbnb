# Architettura del Progetto: Mr. Airbnb Management & Market Scanner

Questo documento descrive l'architettura complessiva, l'elenco degli agenti, le loro responsabilità, i meccanismi di interazione, i file di configurazione, i modelli contabili e le basi di dati del progetto.

---

## 1. 🏗️ Visione Generale dell'Architettura

Il progetto è una piattaforma multi-agente per la **gestione strategica, analisi competitiva e contabilità analitica** dell'appartamento Airbnb (*Appartamento silenzioso a 300m da Piazza Navona*).

L'architettura si articola in tre rami operativi principali, potenziati da un insieme di **Skills specializzate**:

1. **Mercato & Competitor Intelligence (Market Scanner):** Monitoraggio continuo e massivo dei competitor diretti su Roma per calcolare prezzi netti reali e alimentare il Data Lake.
2. **Strategia Dinamica di Prezzo (Price Recommender):** Analisi dell'occupazione del rione a 500m (cluster 54 gemelli), calcolo dei percentili competitivi e generazione delle tariffe pure da inserire nel calendario host.
3. **Contabilità, Prenotazioni & Reporting Fiscale (Reservation & Accounting):** Elaborazione analitica delle prenotazioni effettive, allineamento allo storico dei bonifici ricevuti e generazione automatizzata di matrici CSV per la contabilità.
4. **Skill Layer (.agents/skills):** Competenze procedurali modulari (script Node/Python, regole e logiche riusabili) che gli agenti attivano su richiesta.

```
+---------------------------------------------------------------------------------------------------+
|                                 AGENTE PRINCIPALE (Orchestratore)                                  |
+-------------------------------------------------+-------------------------------------------------+
                                                  |
         +----------------------------------------+----------------------------------------+
         |                                        |                                        |
+--------v---------------------------+   +--------v---------------------------+   +--------v---------------------------+
| RAMO 1: MARKET INTELLIGENCE        |   | RAMO 2: PRICING STRATEGY           |   | RAMO 3: RESERVATION & ACCOUNTING   |
|                                    |   |                                    |   |                                    |
| 1. Background Scanner (scan_fase2) |   | 1. Skill price-recommender         |   | 1. Subagent airbnb-reservation-    |
|    - MCP Server Airbnb             |   |    - scripts/recommend.py          |   |    reader (o Generator)            |
|    - Motore anti-ban & rotazione   |   |    - Analisi saturazione zona      |   |    - Regole CSV & formule Excel    |
| 2. Cron Sentry Task                |   |    - Algoritmo percentili          |   |    - Incrocio storico Payouts      |
|    - Check ogni 15 min             |   |    - Formula inversa calendario    |   |    - Sanity Checker automatico     |
|    - Allerta a blocchi di 5 giorni |   |      per host-only fee             |   |                                    |
+------------------------------------+   +------------------------------------+   +------------------------------------+
```

---

## 2. 🤖 Agenti e Task: Ruoli e Funzioni

### 1. **Agente Principale (Orchestratore / Pair Programmer)**
- **Ruolo:** Coordina l'intero workspace, riceve i comandi utente, gestisce i task di background a lungo termine (scansione mercato), supervisiona la sentinella e delega i compiti verticali a subagenti specializzati.
- **Interazione:** Dialoga direttamente con l'utente via chat, gestisce i task asincroni (`run_command`), imposta i cron schedulati (`schedule`) e istanzia i subagenti dedicati (`invoke_subagent`).

### 2. **Subagent: `airbnb-reservation-reader` (o Generator)**
- **Ruolo:** Specialista contabile e di data extraction per le prenotazioni di Airbnb.
- **Funzioni:**
  - Legge e analizza le schede di prenotazione (ospiti, date, notti, tariffe, pulizie, commissioni host e costi del servizio ospite).
  - Consulta lo storico dei pagamenti per incrociare i dati ufficiali (date di prenotazione originarie, codici di conferma `HM...`, compensi netti).
  - Applica rigidamente le formule matematico-fiscali (cedolare secca al 21%, tassa di soggiorno a 6 €/ospite/notte, commissione host 3% + IVA 22%, formule offset per totali).
  - Esegue il **Sanity Check** preventivo per verificare che il CSV rispetti senza eccezioni il numero di colonne, separatori `|` e formule riferite alle colonne alfabetiche progressive di Excel (`EB`, `EC`, `ED`, ..., `FB`, `FC`, ...).
- **Interazione:** Viene invocato dall'agente principale, opera in contesto isolato, produce i file CSV e restituisce il report di convalida.

### 3. **Task di Background: `Scanner di Mercato` (`scan_fase2_resume.py`)**
- **Ruolo:** Worker asincrono non-stop per l'estrazione massiva dei dati di mercato.
- **Funzioni:**
  - Interroga l'MCP Server di Airbnb giorno per giorno.
  - Per ciascuna data analizza l'intero pool di competitor omogenei su Roma (~100 annunci).
  - Utilizza la formula algebrica inversa host-only fee (`cal_price = ((net + 50) / 0.81089) - 59`) per scorporare i costi e risalire alla vera tariffa pura da calendario impostata dall'host.
  - Integra protezioni anti-ban avanzate (pause dinamiche casuali da 10s a 20s tra annunci, e cooldown di sicurezza automatico di 120s in caso di errore).

### 4. **Task Sentinella: `Monitoraggio Progresso` (`parse_progress.py` + `schedule` cron)**
- **Ruolo:** Demone di sorveglianza periodico schedulato ogni 15 minuti.
- **Funzioni:**
  - Legge lo stream dei log attivi dello scanner.
  - Calcola la velocità media per giorno, il giorno attualmente in elaborazione e verifica eventuali cooldown scattati.
  - Se viene superata una soglia di **5 giorni completati**, emette l'evento `--- ALLERTA PER AGENTE ---` risvegliando l'orchestratore per notificare l'avanzamento all'utente.

### 5. **Motore di Pricing: `price-recommender` (`scripts/recommend.py`)**
- **Ruolo:** Consulente strategico di revenue management e generatore di tariffe per l'host.
- **Funzioni:**
  - Analizza lo snapshot di mercato per qualsiasi data o intervallo temporale.
  - Calcola l'indice di saturazione/occupazione del cluster dei 54 appartamenti gemelli (1 camera/max 4 ospiti entro 500m da Navona).
  - Applica la scala dinamica dei percentili di prezzo (80° percentile per occupazione $\ge 90\%$, 60° per $75-89\%$, 40° per $50-74\%$, 25° per $< 50\%$).
  - Applica la formula algebrica inversa host-only fee per determinare l'esatto valore da digitare a calendario Airbnb:
    $$\text{Prezzo Calendario} = \frac{\text{Target Netto} + 50}{0{,}81089} - 59$$
  - Confronta in tempo reale il target con il prezzo impostato da Mauro, fornendo indicazioni di rialzo (`🔺 Aumenta`), ribasso (`🔻 Riduci`) o allineamento (`✅ Allineato`).

---

## 3. 🧩 Skill Layer del Progetto (`.agents/skills`)

Le **Skills** sono pacchetti modulari di istruzioni (`SKILL.md`), script operativi (Node.js/Python) e logiche riusabili situati nella cartella `.agents/skills/`. Vengono richiamate dagli agenti in base all'esigenza:

### 1. `airbnb-nightly-rate`
- **Scopo:** Calcola la tariffa notturna reale e pura di un annuncio Airbnb estraendola dal prezzo totale tramite algebra inversa (bypassa la commissione nascosta dell'ospite).
- **Componenti:** Script Node.js `calculate.js`, supporto iterativo al Minimum Stay (da 1 a 7 notti) e rilevazione automatica spese di pulizia.

### 2. `market-scanner`
- **Scopo:** Motore di estrazione massiva dei prezzi reali creando il Data Lake grezzo.
- **Componenti:** Gestione pause dinamiche anti-ban (8-15s), bypass dei blocchi IP (errore 429), archiviazione nel data lake JSON e moduli di calcolo sconti host e durate minime.

### 3. `price-recommender`
- **Scopo:** Motore analitico e decisionale per la raccomandazione strategica dei prezzi per notte da inserire a calendario Airbnb.
- **Componenti:** Script CLI `recommend.py`, calcolo della percentuale di occupazione di zona su cluster di 54 gemelli (500m), attribuzione dinamica dei percentili target (25°, 40°, 60°, 80° percentile) e formula algebrica inversa host-only fee per convertire il netto desiderato nel prezzo esatto di calendario:
  $$\text{Prezzo Calendario} = \frac{\text{Target Netto} + 50}{0{,}81089} - 59$$

### 4. Skills di Supporto al Codice e Sviluppo
- **`git-commit-formatter`:** Formattazione rigorosa dei messaggi di commit secondo lo standard Conventional Commits.
- **`code-review`:** Analisi della qualità del codice, controllo bug e rispetto dei pattern di progetto.
- **`database-schema-validator`:** Validazione delle definizioni schema SQL e consistenza dei campi.
- **`json-to-pydantic`:** Conversione automatica dei payload JSON dell'API Airbnb in modelli dati Pydantic tipizzati.
- **`license-header-adder`:** Aggiunta di header di licenza open-source ai sorgenti.

---

## 4. 📂 Basi di Dati e File del Progetto

### 🗄️ Basi di Dati (Data Lake Airbnb)
- **`banca_dati_airbnb_MCPserver.json`:** Data Lake grezzo principale contenente decine di migliaia di snapshot di prezzi dei competitor per tutte le date scansionate (estate, autunno e inverno 2026/2027).
- **`banca_dati_airbnb_MCPserver_recovered.json`:** Archivio snapshot consolidato utilizzato per le query storiche aggregate.
- **`titles.txt`:** Mappatura univoca tra ID annuncio Airbnb e nome reale del competitor (per evitare annunci omonimi nei report).

### 📑 Disciplinari Tecnici e Dati Storici
- **`Regole per l'agente airbnb-reservation-reader.md`:** Disciplinare tecnico assoluto che descrive le 26 righe del modello contabile, la progressione delle colonne Excel con i capisaldi di allineamento verificati (`EB = 3 giugno 2026` e `HJ = 1 agosto 2026`), la sintassi delle formule e le regole del sanity check.
- **`2026-07-06 Airbnb Somma già corrisposta.csv`:** Database storico contenente l'estratto conto ufficiale di oltre 60 bonifici e prenotazioni del 2026 (con date di prenotazione originarie, codici `HM...`, payout netti, costi del servizio e pulizie).
- **`monitor_state.json`:** Stato persistente del tracker di progresso dello scanner (memorizza l'ultimo blocco di 5 giorni notificato).

### 📊 File CSV Generati per la Contabilità
- **`prenotazione_amelie_gervais_regole.csv`:** Matrice a 5 colonne (30 mag - 3 giu, colonna finale `EB`).
- **`prenotazione_stefan_bergman_regole.csv`:** Matrice a 1 colonna (4 giu, colonna finale `EC`).
- **`prenotazioni_nicolas_eduardo_regole.csv`:** Matrice combinata a 5 colonne (5 - 9 giu, colonne finali `EF` ed `EH`).
- **`prenotazioni_giugno_10_30_regole.csv`:** Matrice a 20 colonne consecutive (10 - 29 giu, colonne finali `EM`, `ES`, `EV`, `EY`, `FB`).
- **`prenotazioni_luglio_agosto_regole.csv`:** Matrice a 33 colonne consecutive (30 giu - 1 ago, con colonna 24 lug vuota).
- **`prenotazioni_agosto_settembre_regole.csv`:** Matrice a 31 colonne consecutive (2 ago - 1 set 2026, con colonne giorni liberi `GY`, `HI`, `HM` vuote eccetto righe 3 e 4).

---

## 5. 🔄 Flussi di Lavoro Operativi

1. **Scansione Massiva di Mercato:**
   - L'utente lancia il goal (es. `/goal ...`).
   - L'Agente Principale attiva lo script `scan_fase2_resume.py` in background e schedula la sentinella cron `parse_progress.py`.
   - Ad ogni ciclo di 15 minuti, la sentinella controlla i log. Quando 5 giorni completi vengono archiviati, scatta la notifica automatica.
2. **Generazione e Contabilizzazione Prenotazioni:**
   - L'utente fornisce la scheda della prenotazione o un gruppo di prenotazioni.
   - L'Agente Principale delega il task a `airbnb-reservation-reader`.
   - Il subagent consulta le **Regole**, incrocia i dati con lo **Storico Payouts**, mappa l'intervallo temporale sulle colonne Excel, formatta le 26 righe con separatore `|` e convalida il risultato tramite script Python di **Sanity Check** prima del rilascio finale.
3. **Raccomandazione Dinamica Tariffe Calendario:**
   - L'utente richiede consulenza su prezzi di vendita per date specifiche o periodi futuri (es. *"consigliami i prezzi per novembre"*).
   - L'Agente Principale attiva la skill `price-recommender` (tramite `scripts/recommend.py`).
   - La skill interroga il Data Lake aggiornato, calcola l'indice di saturazione/occupazione del rione, seleziona il percentile di prezzo ottimale, applica l'algebra inversa per compensare commissioni host e pulizie, e genera la matrice di raccomandazione con i prezzi esatti da digitare a calendario Airbnb.

---

## 6. 🔗 Matrice delle Interazioni e Chiamate

### 1. **Chi chiama chi: Agenti verso Agenti (Agent-to-Agent)**
- **Agente Principale (Orchestratore) ➔ `airbnb-reservation-reader` (o Generator):**
  - **Relazione:** Invocazione gerarchica via `invoke_subagent`.
  - **Motivo:** Quando l'utente fornisce schede di prenotazione da contabilizzare, l'Orchestratore delega l'intero ciclo (estrazione, incrocio storico, calcolo formule e sanity check) a questo subagent, isolando il contesto di lavoro per evitare allucinazioni e preservare il contesto dell'agente principale.
- **`airbnb-reservation-reader` ➔ Agente Principale:**
  - **Relazione:** Risposta asincrona via messaggio con esito e sanity check report.

### 2. **Chi chiama chi: Agenti verso Skills (Agent-to-Skill)**
- **Agente Principale ➔ `market-scanner`:**
  - **Utilizzo:** L'Orchestratore sfrutta le istruzioni e le formule definite in `market-scanner` per orchestrare ed eseguire `scan_fase2_resume.py`, gestire la pipeline ETL dei prezzi e monitorare i ritardi anti-ban.
- **Agente Principale ➔ `price-recommender`:**
  - **Utilizzo:** L'Orchestratore invoca la skill `price-recommender` per trasformare i dati grezzi del Data Lake in raccomandazioni strategiche di prezzo a calendario, calcolando percentili di saturazione e applicando la formula algebrica host-only fee.
- **Agente Principale ➔ `airbnb-nightly-rate`:**
  - **Utilizzo:** Viene invocata quando occorre calcolare estemporaneamente la tariffa base di un singolo annuncio o effettuare verifiche puntuali su un competitor specifico attraverso `calculate.js`.
- **Agente Principale / Subagent ➔ `code-review` & `git-commit-formatter`:**
  - **Utilizzo:** Utilizzate nelle fasi di refactoring, creazione di nuovi script o quando viene richiesto di formattare messaggi di commit git secondo le convenzioni standard.
- **`airbnb-reservation-reader` ➔ Disciplinare Regole:**
  - **Utilizzo:** Il subagent legge e applica rigidamente le istruzioni codificate in `Regole per l'agente airbnb-reservation-reader.md` come proprio standard operativo (equivalente a una skill contabile specializzata).

### 3. **Interazioni tra Skills (Skill-to-Skill)**
- **`price-recommender` ➔ `market-scanner` (Dipendenza Dati):**
  - **Relazione logica:** `price-recommender` consuma direttamente gli snapshot storici e correnti prodotti dalla pipeline di scansione massiva di `market-scanner` (`banca_dati_airbnb_MCPserver.json`).
- **`market-scanner` ➔ `airbnb-nightly-rate` (Condivisione Logica di Dominio):**
  - **Relazione logica:** La skill `market-scanner` estende ed applica su scala massiva (tramite loop asincroni e data lake) la medesima algebra inversa di estrazione del prezzo puro originariamente codificata nella skill atomica `airbnb-nightly-rate` (sottrazione della tourist tax, deduzione del cleaning fee host-specifico e scorporo della commissione).
- **`price-recommender` ➔ `airbnb-nightly-rate` (Condivisione Formule Inversion):**
  - **Relazione logica:** Entrambe condividono i parametri algebrici di reverse pricing per scorporare pulizie e commissioni host-only fee.
- **Altre Skills:** Le skill di utilità (`json-to-pydantic`, `git-commit-formatter`, `code-review`, `database-schema-validator`) sono modulari e indipendenti; non effettuano chiamate dirette l'una verso l'altra, ma operano come strumenti atomici riusabili.

```
+-------------------------------------------------------------------------------------------------------+
|                                           AGENTE PRINCIPALE                                           |
+---+----------------------------+------------------------------------------+-----------------------+---+
    |                            |                                          |                       |
    | (invoke_subagent)          | (attiva istruzioni/script)              | (attiva calcolo)      | (esegue pricing)
    v                            v                                          v                       v
+-----------------------+   +-----------------------+                  +-----------------------+ +-----------------------+
|  SUBAGENT             |   |  SKILL                |   (estende su    |  SKILL                | |  SKILL                |
|  airbnb-reservation-  |   |  market-scanner       |=== scala massiva>|  airbnb-nightly-rate  | |  price-recommender    |
|  reader               |   +-----------+-----------+   la logica di)  +-----------------------+ +-----------+-----------+
+-----------------------+               |                                                                    |
                                        +=================== fornisce dati a ================================+
```

---

## 4. Stato Avanzamento Data Lake e Scansioni di Mercato

### 4.1. Fase 2 Completata al 100% (Data Lake Annuale Grezzo)
* **File archivio:** [`mr-airbnb/banca_dati_airbnb_MCPserver.json`](file:///c:/Docs/Personnel%20et%20confidentiel/Corsi%20e%20Formazioni/2026-06-14%20Kaggle_5-Day%20AI%20Agents/agy2-projects/my-first-project/mr-airbnb/banca_dati_airbnb_MCPserver.json)
* **Date coperte al 100%:** dal `2026-09-20` al `2027-01-31` (99 date consecutive, 51 appartamenti gemelli monitorati, 5.023 slot totali).
* **Script di sintesi statistica:** [`mr-airbnb/genera_sintesi_mercato.py`](file:///c:/Docs/Personnel%20et%20confidentiel/Corsi%20e%20Formazioni/2026-06-14%20Kaggle_5-Day%20AI%20Agents/agy2-projects/my-first-project/mr-airbnb/genera_sintesi_mercato.py)
* **Report aggregato:** [`mr-airbnb/sintesi_dati_mercato.md`](file:///c:/Docs/Personnel%20et%20confidentiel/Corsi%20e%20Formazioni/2026-06-14%20Kaggle_5-Day%20AI%20Agents/agy2-projects/my-first-project/mr-airbnb/sintesi_dati_mercato.md)

### 4.2. Secondo Passaggio Attivo (Serie Storica / Variazione Tariffe nel Tempo)
* **Script di esecuzione:** [`mr-airbnb/scan_seconda_fase.py`](file:///c:/Docs/Personnel%20et%20confidentiel/Corsi%20e%20Formazioni/2026-06-14%20Kaggle_5-Day%20AI%20Agents/agy2-projects/my-first-project/mr-airbnb/scan_seconda_fase.py)
* **Perimetro date (98 date):**
  - Singole date isolate: `2026-10-16` e `2026-10-20`
  - Finestra continua: dal `2026-10-28` al `2027-01-31`
* **Gestione Versionamento:** Quando una data già archiviata viene riscansita, il record precedente viene storicizzato nell'array `history` con timestamp `collected_at`, permettendo l'analisi differenziale dei prezzi e delle nuove prenotazioni concorrenti.
