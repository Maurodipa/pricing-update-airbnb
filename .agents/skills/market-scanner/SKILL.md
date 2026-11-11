---
name: market-scanner
description: Estrae massivamente i prezzi reali di Airbnb creando un Data Lake grezzo. Calcola le vere tariffe pure deducendo sconti speciali, spese di pulizia dinamiche per host e minimum stay.
---

# Market Scanner

Questa skill permette di lanciare un'analisi competitiva dettagliata su più appartamenti, scansionando in totale sicurezza il mercato senza incorrere nel blocco IP (Error 429).
L'architettura è divisa in due fasi: **Estrazione** (Data Lake) ed **Elaborazione** (ETL).

## 1. Configurazione
Aggiungi o rimuovi gli ID degli appartamenti Airbnb che vuoi tracciare nel file `competitors.txt` (un ID per riga).

## 2. Fase di Estrazione (Raw Data Lake)
Per evitare blocchi e non perdere dati preziosi, lo script `scan_raw.js`:
1. Mantiene pause casuali da 8 a 15 secondi tra una chiamata e l'altra (simulando un umano).
2. Interroga le API "BookIt" cercando iterativamente il **Minimum Stay** accettato (da 1 a 7 notti).
3. Salva l'intero payload JSON grezzo di Airbnb in un data lake (`banca_dati_airbnb.json`), permettendo ricalcoli futuri senza dover ri-effettuare le richieste.

**Comando di avvio:**
```bash
node scripts/scan_raw.js <data-inizio> <data-fine>
# Esempio: node scripts/scan_raw.js 2026-06-25 2026-07-25
```
> [!WARNING]
> Scansionare 10 appartamenti per 1 mese richiede circa **1 ora e mezza**. Lascia girare il comando in background.

## 3. Fase di Elaborazione (Processamento Tariffe)
Una volta ottenuto il Data Lake grezzo, il motore matematico `process_data.js`:
1. Estrae il vero prezzo pagato (sottraendo le tasse statali al totale e rilevando automaticamente gli sconti "**Special Offer**").
2. Sottrae l'**esatto costo di pulizia specifico per quell'host** (tramite dizionario hardcoded).
3. Salva le metriche finali, il `minStay` e l'indicatore di sconto in `market_data_1month.json`.

**Comando di avvio:**
```bash
node scripts/process_data.js
```

## 4. Generazione del Report
Un ulteriore script si occupa di generare la reportistica avanzata basandosi sui dati elaborati, producendo un file markdown che include:
- **Tariffa Media Mensile Pura** incassata dall'host.
- **Calendario Dettagliato**, raggruppando blocchi di date con lo stesso prezzo.
- **Evidenziazione Sconti**: Indica se il prezzo beneficia di un'offerta speciale o last-minute.
- **Avviso Giorni Isolati**: Rileva le date libere incastrate tra due prenotazioni e le etichetta con il tag `[BUCO DI CALENDARIO: Giorno Isolato]`, segnalandone l'inutilizzabilità pratica qualora il minimum stay richiesto sia maggiore di 1.
