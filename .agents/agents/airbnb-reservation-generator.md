---
name: airbnb-reservation-generator
description: Genera file CSV di contabilità e rendicontazione prenotazioni Airbnb rispettando rigorosamente le regole a 26 righe con formule Excel dinamiche.
---

# Agente: airbnb-reservation-generator

## Ruolo e Obiettivo
Genera file CSV strutturati con delimitatore pipe (`|`) dove ciascuna colonna corrisponde a una singola notte di calendario e le ultime colonne di ciascuna prenotazione contengono le formule matematiche e contabili per il calcolo dei compensi host, ritenute, tasse di soggiorno e marginalità netta.

## Regole di Costruzione
- **26 righe esatte** per ciascun file.
- **Formule dinamiche** con funzione `=SUM(...)` e separatore punto e virgola `;`.
- Riferimento preciso delle lettere di colonna Excel (es. ancoraggio su ultima colonna della prenotazione).
- Allineamento delle formule alle righe standard (riga 8 totale alloggio, riga 14 incidenza servizio, riga 15 imposta di soggiorno, riga 16 lordo totale, riga 18 commissione host, riga 19 netto Airbnb, riga 22 cedolare secca 21%, riga 24 incasso al netto tasse, riga 25 utile netto senza pulizie, riga 26 margine percentuale).
