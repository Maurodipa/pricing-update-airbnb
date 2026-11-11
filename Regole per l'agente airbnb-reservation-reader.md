# Regole per l'agente airbnb-reservation-reader

## Base Dati Ufficiale
- Il file sorgente ufficiale di riferimento per lo storico delle prenotazioni, compensi e dettagli ospiti è:
  `2026-10-27 Airbnb Somma già corrisposta.csv`

## Regole generali
- Il separatore nei CSV deve essere | (non la virgola).
- Il numero delle colonne = numero delle notti.
- La prima colonna = data di inizio del soggiorno.
- L'ultima colonna = ultima notte (giorno prima della data di fine).
- Le righe con giorni, date, tariffe devono avere tutte le colonne piene.
- Le altre righe devono avere solo l'ultima colonna piena.
- Prima del rilascio, il CSV deve passare il sanity check: deve rispettare unicamente le regole che mi hai dato, senza iniziative o valori nuovi.
- La colonna EB corrisponde al 3 giugno (nello schema originale); se ci sono state traslazioni o inserimenti di colonne antecedenti (es. 30 maggio = EY), seguire la progressione naturale di Excel.
- Il 1 agosto 2026 è la colonna HJ.
- La data di prenotazione si trova nel file `2026-10-27 Airbnb Somma già corrisposta.csv`.
- Colonna finale = deve coincidere con l'ultima notte.
- Le colonne relative ad altre date cambiano le lettere secondo come fa excel.
- Il numero delle colonne è uguale al numero delle notti.
- Prima di rilasciare il CSV verificare che il numero di separatori sia corretto rispetto al numero delle colonne.
- Quando inizia il soggiorno? Quando termina? La prima colonna coincide con la data di inizio del soggiorno. L'ultima colonna con l'ultima notte, che è un giorno prima della data di fine.

## 📌 Regole specifiche per le righe (Formule con =SUM() e argomenti separati da virgola `,`)
- Riga 1: deve riportare il numero degli ospiti (dal file `2026-10-27 Airbnb Somma già corrisposta.csv`, ricavabile anche da `Tassa / (notti * 6)`)
- Riga 2: deve riportare il numero delle notti.
- Riga 3: abbreviazioni dei giorni (sab, dom, lun, mar, mer, gio, ven)
- Riga 4: deve riportare le date della prenotazione (usa le formattazioni: gg-mmm, i.e.: 7-giu, 2-lug, 13-mag, 2-set, etc.. in italiano)
- Riga 5: deve riportare le tariffe per notte (i.e.: 109 €, 118 €, 103 €).
- Riga 6 e 7: vuote
- Riga 8: formula `=SUM(OFFSET(XX5, 0, -XX2+1, 1, XX2))`  (Nota: XX deve essere la colonna dell'ultima notte)
- Riga 9: "Airbnb"
- Riga 10: Riporta il nome completo dell'ospite (da `2026-10-27 Airbnb Somma già corrisposta.csv`)
- Riga 11: deve riportare la data di prenotazione (da `2026-10-27 Airbnb Somma già corrisposta.csv`).
- Riga 12: deve riportare il costo di pulizia (i.e.: 50 € o 59 €).
- Riga 13: deve riportare il costo del servizio ospite.
- Riga 14: formula `=XX13/SUM(XX8,XX12)`
- Riga 15: la formula deve essere `=6*numero_ospiti*numero_notti`.
- Riga 16: formula `=SUM(XX8,XX12,XX13,XX15,XX7)`
- Riga 17: la formula include le costanti 3% e 1,22: `=3%*1,22`
- Riga 18: formula `=-SUM(XX8,XX7,XX12)*XX17`
- Riga 19: formula `=SUM(XX8,XX12,XX18,XX7)`
- Riga 20: vuota
- Riga 21: deve riportare solo il numero `21%`
- Riga 22: formula `=-XX21*XX19`
- Riga 23: vuota
- Riga 24: formula `=SUM(XX19,XX22)`
- Riga 25: formula `=XX24-XX12`
- Riga 26: formula `=XX25/XX16`
