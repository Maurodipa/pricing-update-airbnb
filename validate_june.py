import os

files = [
    'prenotazione_amelie_gervais_regole.csv',
    'prenotazione_stefan_bergman_regole.csv',
    'prenotazioni_nicolas_eduardo_regole.csv',
    'prenotazioni_giugno_10_30_regole.csv'
]
data = []
for fname in files:
    with open(fname, encoding='utf-8') as f:
        data.append(f.read().splitlines())

merged_rows = []
for r in range(26):
    parts = [data[f_idx][r] for f_idx in range(4)]
    merged_line = '|'.join(parts)
    merged_rows.append(merged_line)

matrix = [r.split('|') for r in merged_rows]

print(f'Total Rows: {len(matrix)}')
for i, r in enumerate(matrix):
    if len(r) != 31:
        print(f'Row {i+1} has {len(r)} columns instead of 31!')

last_cols = {
    4: 'FC', 5: 'FD', 8: 'FG', 10: 'FI', 15: 'FN', 21: 'FT', 24: 'FW', 27: 'FZ', 30: 'GC'
}

expected_data = {
    4: {'guest': 'Amelie Gervais', 'book': '27/03/2026', 'guests': '2', 'nights': '5', 'clean': '50 €', 'serv': '91,09 €'},
    5: {'guest': 'Stefan Bergman', 'book': '01/06/2026', 'guests': '2', 'nights': '1', 'clean': '50 €', 'serv': '21,36 €'},
    8: {'guest': 'Nicolas Uliana', 'book': '27/03/2026', 'guests': '2', 'nights': '3', 'clean': '50 €', 'serv': '57,99 €'},
    10: {'guest': 'Eduardo Jimenez', 'book': '05/04/2026', 'guests': '4', 'nights': '2', 'clean': '50 €', 'serv': '47,76 €'},
    15: {'guest': 'Dennis Myers', 'book': '30/01/2026', 'guests': '3', 'nights': '5', 'clean': '50 €', 'serv': '101,32 €'},
    21: {'guest': 'Daniela Basile', 'book': '28/03/2026', 'guests': '2', 'nights': '6', 'clean': '50 €', 'serv': '128,26 €'},
    24: {'guest': 'Diego Fregossi Perrone', 'book': '13/02/2026', 'guests': '4', 'nights': '3', 'clean': '50 €', 'serv': '88,04 €'},
    27: {'guest': 'Renaud St-Jean', 'book': '08/02/2026', 'guests': '4', 'nights': '3', 'clean': '50 €', 'serv': '67,29 €'},
    30: {'guest': 'Marta Raya', 'book': '30/01/2026', 'guests': '4', 'nights': '3', 'clean': '50 €', 'serv': '68,16 €'}
}

empty_rows = [5, 6, 19, 22] # Rows 6, 7, 20, 23 (0-indexed)
errors = []

for r_idx in range(26):
    for c_idx in range(31):
        val = matrix[r_idx][c_idx]
        if r_idx in [2, 3, 4]:
            if not val:
                errors.append(f'Row {r_idx+1} col {c_idx} empty')
        elif r_idx in empty_rows:
            if val != '':
                errors.append(f'Row {r_idx+1} col {c_idx} not empty: {val}')
        else:
            if c_idx in last_cols:
                col_let = last_cols[c_idx]
                info = expected_data[c_idx]
                exp_map = {
                    0: info['guests'],
                    1: info['nights'],
                    7: f'=SUM(OFFSET({col_let}5; 0; -{col_let}2+1;1;{col_let}2))',
                    8: 'Airbnb',
                    9: info['guest'],
                    10: info['book'],
                    11: info['clean'],
                    12: info['serv'],
                    13: f'={col_let}13/({col_let}8+{col_let}12)',
                    14: f'=6*{info["guests"]}*{info["nights"]}',
                    15: f'={col_let}8+{col_let}12+{col_let}13+{col_let}15+{col_let}7',
                    16: '=3%*1,22',
                    17: f'=-({col_let}8+{col_let}7+{col_let}12)*{col_let}17',
                    18: f'={col_let}8+{col_let}12+{col_let}18+{col_let}7',
                    20: '21%',
                    21: f'=-{col_let}21*{col_let}19',
                    23: f'={col_let}19+{col_let}22',
                    24: f'={col_let}24-{col_let}12',
                    25: f'={col_let}25/{col_let}16',
                }
                if r_idx in exp_map and val != exp_map[r_idx]:
                    errors.append(f'Row {r_idx+1} col {c_idx} ({col_let}): expected "{exp_map[r_idx]}", got "{val}"')
            else:
                if val != '':
                    errors.append(f'Row {r_idx+1} col {c_idx} should be empty: {val}')

print(f'Total errors found: {len(errors)}')
for e in errors[:20]:
    print(e)

if len(errors) == 0:
    print('ALL 26 ROWS AND 31 COLUMNS VALIDATED 100% PERFECTLY!')
