---
name: sintesi-mercato
description: Genera automaticamente un report di sintesi e analisi aggregata del Data Lake di Airbnb per blocchi di date o per l'intero orizzonte temporale scansionato.
---

# Sintesi Mercato

Questa skill analizza i dati del Data Lake di Airbnb (`banca_dati_airbnb_MCPserver.json` o `banca_dati_airbnb_MCPserver_safe.json`) ed elabora un report sintetico e aggregato in formato Markdown.

## Funzionalità Principali
- **Analisi Mensile e Raggruppamento:** Calcola il tasso di occupazione del cluster (51 appartamenti gemelli) e distribuisce le tariffe per percentile (Minimo, 25°, Mediana 50°, 75°, Massimo).
- **Scorporo Algebrico Fee e Pulizie:** Dedece i costi di pulizia dinamici specifici per ogni host e le commissioni di servizio, estraendo il vero guadagno netto in tasca.
- **Dettaglio Giorni Speciali:** Analizza automaticamente l'occupazione e i picchi di prezzo per i giorni festivi (Halloween, Vigilia, Natale, Capodanno, Epifania).
- **Confronto Costi Utente vs Mercato:** Genera una tabella comparativa tra la struttura costi dell'appartamento dell'utente e le mediane dei competitor.

## Istruzioni Operative
1. Apri il terminale nella cartella `mr-airbnb`.
2. Esegui lo script:
   ```bash
   uv run python genera_sintesi_mercato.py
   ```
3. Lo script genererà il report sintetico aggiornato e lo salverà in `sintesi_dati_mercato.md` e negli artefatti della conversazione.
