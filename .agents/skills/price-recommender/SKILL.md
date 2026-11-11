---
name: price-recommender
description: Genera raccomandazioni strategiche e operative sui prezzi per notte da applicare nel calendario Airbnb. Calcola l'occupazione dell'area (cluster 54 gemelli a 500m), percentili di prezzo competitivi e deduce la tariffa lorda da impostare a calendario tramite algebra inversa (host-only fee).
---

# Airbnb Price Recommender

Questa skill fornisce raccomandazioni operative e strategiche sui prezzi da impostare nel calendario Airbnb per massimizzare il RevPAR (Revenue Per Available Room) dell'appartamento, proteggendo la marginalità dell'host.

---

## 1. Quando Utilizzare la Skill
Attiva o consulta questa skill quando:
- L'utente chiede suggerimenti su quanto tariffare una specifica data, un fine settimana o un intero mese (es. *"Consigliami un prezzo per novembre"*, *"A quanto dovrei mettere il ponte del 1° novembre?"*).
- Occorre analizzare il livello di saturazione e occupazione del cluster dei concorrenti diretti (54 appartamenti "gemelli" entro 500m da Piazza Navona).
- Si vuole verificare se i prezzi attualmente impostati a calendario sono sottostimati (lasciando soldi sul tavolo) o sovrastimati.
- Si desidera generare un report tabellare pronto con il prezzo netto e l'esatta tariffa lorda da inserire su Airbnb.

---

## 2. Modello Matematico ed Economico

### A. Strategia Dinamica basata sull'Occupazione
La skill analizza tutti gli annunci del cluster competitor per ciascun giorno e calcola il **tasso di occupazione di zona** $\text{Occ} = \frac{\text{annunci occupati}}{\text{totale annunci}}$. In base a questo valore seleziona dinamicamente il percentile di posizionamento:

| Occupazione di Zona | Scenario di Mercato | Percentile Target | Strategia Adottata |
|---|---|---|---|
| **$\ge 90\%$** | Altissima Domanda / Scarsità | **80° percentile** | Prezzo Premium aggressivo |
| **$75\% - 89\%$** | Buona Domanda | **60° percentile** | Posizionamento sopra la media |
| **$50\% - 74\%$** | Domanda Media | **40° percentile** | Allineamento prudenziale |
| **$< 50\%$** | Bassa Domanda / Bassa Stagione | **25° percentile** | Prezzo competitivo per stimolare le conversioni |

### B. Formula Inversa per il Calendario Host
Airbnb deduce dai compensi host commissioni e costi di pulizia. Per garantire che l'host intaschi esattamente il $\text{Target Netto}$ stabilito, la tariffa da impostare a calendario ($\text{Prezzo Calendario}$) viene calcolata invertendo l'algebra della commissione *host-only fee* (~18,911%) e delle spese di pulizia:

$$\text{Prezzo Calendario} = \frac{\text{Target Netto} + 50}{0{,}81089} - 59$$

- **$+50$**: Spese di pulizia sostenute dall'host.
- **$0{,}81089$**: Fattore di scorporo commissione host ($1 - 0{,}18911$).
- **$-59$**: Quota pulizie standard mostrata all'ospite.

---

## 3. Guida Operativa & Comandi

Lo script operativo principale si trova in `scripts/recommend.py`.

### Esecuzione Base (rileva automaticamente il miglior DB disponibile):
```bash
python .agents/skills/price-recommender/scripts/recommend.py
```

### Analisi di un Intervallo Specifico di Date:
```bash
python .agents/skills/price-recommender/scripts/recommend.py --start 2026-10-28 --end 2026-11-15
```

### Esportazione di un Report Markdown:
```bash
python .agents/skills/price-recommender/scripts/recommend.py --start 2026-11-01 --end 2026-11-30 --output report_novembre.md
```

### Parametri Opzionali:
- `--db <path>`: Specifica un file JSON personalizzato (es. `mr-airbnb/banca_dati_airbnb_MCPserver.json`).
- `--user-apt <id>`: ID dell'appartamento dell'utente (default: `1589943047991118285`).
- `--host-cleaning <eur>`: Spese di pulizia host (default: `50.0`).
- `--fee-factor <val>`: Fattore netto host (default: `0.81089`).

---

## 4. Output Generato
La skill produce una tabella comparativa dettagliata contenente:
- **Data e Giorno della settimana** (weekend evidenziati in grassetto).
- **Tasso di Occupazione** della zona.
- **Media e Mediana** dei prezzi praticati dai competitor liberi.
- **Target Netto Raccomandato** (guadagno netto host).
- **DA INSERIRE A CALENDARIO**: Il prezzo esatto in Euro da digitare nel gestionale di Airbnb.
- **Prezzo Attuale**: La tariffa già presente a calendario per l'appartamento dell'host (se disponibile).
- **Azione Consigliata**: Indicatore visivo (🔺 Aumenta, 🔻 Riduci, ✅ Allineato).

---

## 5. Relazioni con altre Componenti
- **`market-scanner`**: È la skill a monte che estrae e aggiorna il Data Lake grezzo (`banca_dati_airbnb_MCPserver.json`). `price-recommender` consuma questi dati.
- **`airbnb-nightly-rate`**: Condivide i principi di scorporo algebrico inverso per singola notte.
- **`Architettura del Progetto`**: È registrata come skill analitico-decisionale nel catalogo `.agents/skills/`.