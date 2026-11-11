import sys

with open('prenotazioni_giugno_2026_complete_regole.csv', encoding='utf-8') as f:
    lines = f.read().splitlines()

print(f"Total lines: {len(lines)}")
assert len(lines) == 26, f"Expected 26 lines, got {len(lines)}"

for idx, line in enumerate(lines):
    pipe_count = line.count('|')
    cols = line.split('|')
    assert pipe_count == 30, f"Line {idx+1} has {pipe_count} pipes, expected 30"
    assert len(cols) == 31, f"Line {idx+1} has {len(cols)} columns, expected 31"

print("All 26 lines have exactly 30 pipes and 31 columns!")

# Verify empty rows 6, 7, 20, 23 (indices 5, 6, 19, 22)
for empty_idx in [5, 6, 19, 22]:
    assert lines[empty_idx] == '|' * 30, f"Line {empty_idx+1} is not empty pipes: {lines[empty_idx]}"
print("Empty rows 6, 7, 20, 23 strictly verified (30 empty pipes each)!")

# Verify rows 3, 4, 5 are all filled
matrix = [l.split('|') for l in lines]
for r in [2, 3, 4]:
    for c in range(31):
        assert matrix[r][c] != '', f"Row {r+1} col {c+1} should not be empty"
print("Rows 3, 4, 5 strictly verified (all 31 cells filled)!")

last_cols = {
    4: 'FC', 5: 'FD', 8: 'FG', 10: 'FI', 15: 'FN', 21: 'FT', 24: 'FW', 27: 'FZ', 30: 'GC'
}

for r in range(26):
    if r in [2, 3, 4, 5, 6, 19, 22]:
        continue
    for c in range(31):
        val = matrix[r][c]
        if c not in last_cols:
            assert val == '', f"Row {r+1} col {c+1} should be empty but is '{val}'"
        else:
            assert val != '', f"Row {r+1} col {c+1} should not be empty"

print("Intermediate and last-column placement strictly verified across all rows!")

# Now verify the exact formulas and values on the last columns:
expected = {
    4: {'name': 'Amelie Gervais', 'col': 'FC', 'guests': '2', 'nights': '5', 'date': '27/03/2026', 'clean': '50 €', 'serv': '91,09 €'},
    5: {'name': 'Stefan Bergman', 'col': 'FD', 'guests': '2', 'nights': '1', 'date': '01/06/2026', 'clean': '50 €', 'serv': '21,36 €'},
    8: {'name': 'Nicolas Uliana', 'col': 'FG', 'guests': '2', 'nights': '3', 'date': '27/03/2026', 'clean': '50 €', 'serv': '57,99 €'},
    10: {'name': 'Eduardo Jimenez', 'col': 'FI', 'guests': '4', 'nights': '2', 'date': '05/04/2026', 'clean': '50 €', 'serv': '47,76 €'},
    15: {'name': 'Dennis Myers', 'col': 'FN', 'guests': '3', 'nights': '5', 'date': '30/01/2026', 'clean': '50 €', 'serv': '101,32 €'},
    21: {'name': 'Daniela Basile', 'col': 'FT', 'guests': '2', 'nights': '6', 'date': '28/03/2026', 'clean': '50 €', 'serv': '128,26 €'},
    24: {'name': 'Diego Fregossi Perrone', 'col': 'FW', 'guests': '4', 'nights': '3', 'date': '13/02/2026', 'clean': '50 €', 'serv': '88,04 €'},
    27: {'name': 'Renaud St-Jean', 'col': 'FZ', 'guests': '4', 'nights': '3', 'date': '08/02/2026', 'clean': '50 €', 'serv': '67,29 €'},
    30: {'name': 'Marta Raya', 'col': 'GC', 'guests': '4', 'nights': '3', 'date': '30/01/2026', 'clean': '50 €', 'serv': '68,16 €'}
}

for c, info in expected.items():
    col = info['col']
    g = info['guests']
    n = info['nights']
    assert matrix[0][c] == g, f"Row 1: {matrix[0][c]} != {g}"
    assert matrix[1][c] == n, f"Row 2: {matrix[1][c]} != {n}"
    assert matrix[7][c] == f"=SUM(OFFSET({col}5; 0; -{col}2+1;1;{col}2))", f"Row 8: {matrix[7][c]}"
    assert matrix[8][c] == "Airbnb", f"Row 9: {matrix[8][c]}"
    assert matrix[9][c] == info['name'], f"Row 10: {matrix[9][c]}"
    assert matrix[10][c] == info['date'], f"Row 11: {matrix[10][c]}"
    assert matrix[11][c] == info['clean'], f"Row 12: {matrix[11][c]}"
    assert matrix[12][c] == info['serv'], f"Row 13: {matrix[12][c]}"
    assert matrix[13][c] == f"={col}13/({col}8+{col}12)", f"Row 14: {matrix[13][c]}"
    assert matrix[14][c] == f"=6*{g}*{n}", f"Row 15: {matrix[14][c]}"
    assert matrix[15][c] == f"={col}8+{col}12+{col}13+{col}15+{col}7", f"Row 16: {matrix[15][c]}"
    assert matrix[16][c] == "=3%*1,22", f"Row 17: {matrix[16][c]}"
    assert matrix[17][c] == f"=-({col}8+{col}7+{col}12)*{col}17", f"Row 18: {matrix[17][c]}"
    assert matrix[18][c] == f"={col}8+{col}12+{col}18+{col}7", f"Row 19: {matrix[18][c]}"
    assert matrix[20][c] == "21%", f"Row 21: {matrix[20][c]}"
    assert matrix[21][c] == f"=-{col}21*{col}19", f"Row 22: {matrix[21][c]}"
    assert matrix[23][c] == f"={col}19+{col}22", f"Row 24: {matrix[23][c]}"
    assert matrix[24][c] == f"={col}24-{col}12", f"Row 25: {matrix[24][c]}"
    assert matrix[25][c] == f"={col}25/{col}16", f"Row 26: {matrix[25][c]}"

print("All formulas, anchored columns, and reservation values verified 100%!")
print("SANITY CHECK PASSED WITH FULL SUCCESS!")
