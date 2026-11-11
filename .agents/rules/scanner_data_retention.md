---
name: scanner_data_retention
description: Regola tassativa per la gestione dei dati del datalake da parte dello scanner.
always_on: true
---

# Regola di Conservazione Dati dello Scanner

Ogni volta che viene eseguito o modificato lo script dello scanner (es. mcp_market_scanner.py), vige la seguente regola ASSOLUTA richiesta dall'utente:

**Ogni nuovo scanner non deve MAI cancellare nessun dato, deve solo aggiungere nuove informazioni al datalake.**

Qualsiasi aggiornamento al JSON deve preservare i prezzi precedenti, muovendoli all'interno dell'array history o accodandoli in liste, senza mai sovrascrivere distruttivamente i dati di passate rilevazioni.
