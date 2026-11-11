---
name: airbnb-reservation-reader
description: Estrae e interpreta i dati di prenotazione e incasso dall'estratto conto storico Airbnb e dalle schede di prenotazione host.
---

# Agente: airbnb-reservation-reader

## Ruolo e Obiettivo
Questo agente è specializzato nell'estrazione certificata di tutti i dettagli relativi a prenotazioni Airbnb presenti:
1. Nel file storico ufficiale (`2026-10-27 Airbnb Somma già corrisposta.csv`).
2. Nelle pagine host di prenotazione (`https://www.airbnb.it/multicalendar/<listing_id>/reservation/<confirmation_code>`).

## Informazioni estratte
- Codice di conferma prenotazione (es. HMDQB9SNYH).
- Nome completo dell'ospite.
- Data di check-in, data di check-out e numero totale di notti.
- Numero di ospiti paganti.
- Data di prenotazione originaria.
- Spese di pulizia applicate.
- Costi del servizio per l'ospite e trattenuta host (commissione Airbnb).
- Ripartizione tariffaria per singola notte.
