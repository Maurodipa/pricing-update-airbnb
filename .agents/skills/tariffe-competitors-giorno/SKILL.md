---
name: tariffe-competitors-giorno
description: Genera una tabella Markdown con le tariffe a calendario e i guadagni netti di tutti i concorrenti (e dell'utente) liberi in una data specifica.
---

# Skill: Tariffe Competitors per Giorno

## Contesto
Questa skill viene usata quando l'utente richiede di conoscere le tariffe esatte di tutti gli appartamenti rimasti liberi (incluso il proprio) in una singola e specifica data.
L'obiettivo è fornire all'utente una visualizzazione chiara sotto forma di tabella a tre colonne: 
- La Tariffa da impostare a Calendario (Lorda)
- La Tariffa per notte che l'ospite vedrà esposta sul sito Airbnb
- Il Guadagno Netto in tasca all'host.

## Istruzioni Operative
1. Apri un terminale nella directory `mr-airbnb`
2. Esegui lo script `get_daily_rates.py` passando la data richiesta nel formato YYYY-MM-DD.
   *Esempio comando:* `python get_daily_rates.py --date 2026-10-16`
3. Lo script genererà in automatico una tabella in sintassi Markdown, formattando:
   - I link corretti ad Airbnb per i concorrenti e per l'appartamento dell'utente.
   - La Tariffa Calendario e il Guadagno Netto per ognuno (con le formule perfette che calcolano fee e pulizie personalizzate della rubrica).
4. Copia e incolla l'output generato dallo script direttamente nella tua risposta all'utente, senza modificare le cifre e senza dover fare calcoli manuali.
5. Se l'utente chiede la *Raccomandazione Strategica* per il suo appartamento (spesso con prezzi più alti) oltre a quella attualmente registrata, puoi integrare la tabella aggiungendo a mano una riga extra basata sulle regole della skill `price-recommender` (o dai vecchi artefatti se la data è passata).
