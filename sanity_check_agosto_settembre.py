import sys

def run_sanity_check(csv_path):
    print(f"=== INIZIO SANITY CHECK: {csv_path} ===")
    errors = []
    warnings = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        lines = [l.rstrip('\r\n') for l in f]

    # 1. Row count check
    if len(lines) != 26:
        errors.append(f"Numero di righe errato: trovato {len(lines)}, atteso 26")
    else:
        print("[OK] Numero righe: esattamente 26")

    # 2. Delimiter and column count check
    for i, line in enumerate(lines):
        pipes = line.count('|')
        cols = line.split('|')
        if pipes != 30:
            errors.append(f"Riga {i+1}: numero delimitatori '|' errato: {pipes}, atteso 30")
        if len(cols) != 31:
            errors.append(f"Riga {i+1}: numero colonne errato: {len(cols)}, atteso 31")

    if not any("delimitatori" in e or "colonne errato" in e for e in errors):
        print("[OK] Delimitatori: esattamente 30 '|' per ciascuna delle 26 righe (31 colonne)")

    grid = [l.split('|') for l in lines]

    # Expected column mapping
    col_names = [
        'GK', 'GL', 'GM', 'GN', 'GO', 'GP', 'GQ', 'GR', 'GS', 'GT',
        'GU', 'GV', 'GW', 'GX', 'GY', 'GZ', 'HA', 'HB', 'HC', 'HD',
        'HE', 'HF', 'HG', 'HH', 'HI', 'HJ', 'HK', 'HL', 'HM', 'HN', 'HO'
    ]

    expected_days = [
        'dom', 'lun', 'mar', 'mer', 'gio', 'ven', 'sab', 'dom', 'lun', 'mar',
        'mer', 'gio', 'ven', 'sab', 'dom', 'lun', 'mar', 'mer', 'gio', 'ven',
        'sab', 'dom', 'lun', 'mar', 'mer', 'gio', 'ven', 'sab', 'dom', 'lun', 'mar'
    ]

    expected_dates = [
        '2-ago', '3-ago', '4-ago', '5-ago', '6-ago', '7-ago', '8-ago', '9-ago', '10-ago', '11-ago',
        '12-ago', '13-ago', '14-ago', '15-ago', '16-ago', '17-ago', '18-ago', '19-ago', '20-ago', '21-ago',
        '22-ago', '23-ago', '24-ago', '25-ago', '26-ago', '27-ago', '28-ago', '29-ago', '30-ago', '31-ago', '1-set'
    ]

    expected_rates = [
        '80 €', '80 €', '80 €',
        '50 €', '50 €', '50 €',
        '89,75 €', '89,75 €', '89,75 €', '89,75 €',
        '91 €', '92 €', '98 €', '98 €',
        '', # GY
        '89 €', '90 €', '88 €', '88 €',
        '48,96 €',
        '81 €', '78 €', '78 €', '79 €',
        '', # HI
        '87 €', '91 €', '93 €',
        '', # HM
        '91 €', '105 €'
    ]

    # Check Row 3 (days)
    for idx, (val, exp) in enumerate(zip(grid[2], expected_days)):
        if val != exp:
            errors.append(f"Riga 3, colonna {col_names[idx]} (indice {idx}): valore '{val}', atteso '{exp}'")
    print("[OK] Riga 3 (giorni): tutti i 31 giorni corretti")

    # Check Row 4 (dates)
    for idx, (val, exp) in enumerate(zip(grid[3], expected_dates)):
        if val != exp:
            errors.append(f"Riga 4, colonna {col_names[idx]} (indice {idx}): valore '{val}', atteso '{exp}'")
    print("[OK] Riga 4 (date): tutte le 31 date corrette")

    # Check Row 5 (rates)
    for idx, (val, exp) in enumerate(zip(grid[4], expected_rates)):
        if val != exp:
            errors.append(f"Riga 5, colonna {col_names[idx]} (indice {idx}): valore '{val}', atteso '{exp}'")
    print("[OK] Riga 5 (tariffe): tutte le tariffe corrette e colonne libere vuote")

    # Check empty columns GY (14), HI (24), HM (28)
    free_indices = {'GY': 14, 'HI': 24, 'HM': 28}
    for col_str, col_idx in free_indices.items():
        for r in range(26):
            if r not in (2, 3): # Not rows 3 and 4 (0-indexed 2 and 3)
                if grid[r][col_idx] != '':
                    errors.append(f"Colonna {col_str} (indice {col_idx}) riga {r+1} NON e vuota: '{grid[r][col_idx]}'")
    print("[OK] Colonne libere GY, HI, HM: vuote eccetto righe 3 e 4")

    # Check completely empty rows across all columns: Row 6 (idx 5), Row 7 (idx 6), Row 20 (idx 19), Row 23 (idx 22)
    empty_rows = [5, 6, 19, 22] # 1-indexed: 6, 7, 20, 23
    for r in empty_rows:
        for c in range(31):
            if grid[r][c] != '':
                errors.append(f"Riga {r+1} colonna {col_names[c]} doveva essere vuota, contiene '{grid[r][c]}'")
    print("[OK] Righe 6, 7, 20, 23: completamente vuote su tutte le colonne")

    # Check last night columns
    last_night_data = {
        'GM': {'idx': 2, 'guests': '3', 'nights': '3', 'name': 'Michael Romero', 'bdate': '21/07/2026', 'clean': '50 €', 'srv': '44,25 €', 'f15': '=6*3*3'},
        'GP': {'idx': 5, 'guests': '2', 'nights': '3', 'name': 'Y\u2006Unting C\u2006Ai', 'bdate': '04/08/2026', 'clean': '59 €', 'srv': '0,00 €', 'f15': '=6*2*3'},
        'GT': {'idx': 9, 'guests': '4', 'nights': '4', 'name': 'Mmaauudd Ddoorriizzoonn', 'bdate': '06/03/2026', 'clean': '50 €', 'srv': '69,29 €', 'f15': '=6*4*4'},
        'GX': {'idx': 13, 'guests': '4', 'nights': '4', 'name': 'Graziela Azevedo', 'bdate': '10/03/2026', 'clean': '50 €', 'srv': '70,35 €', 'f15': '=6*4*4'},
        'HC': {'idx': 18, 'guests': '4', 'nights': '4', 'name': 'Stéphanie Vaculik', 'bdate': '23/02/2026', 'clean': '50 €', 'srv': '68,62 €', 'f15': '=6*4*4'},
        'HD': {'idx': 19, 'guests': '4', 'nights': '1', 'name': 'Juris Rozenbergs', 'bdate': '21/08/2026', 'clean': '59 €', 'srv': '0,00 €', 'f15': '=6*4*1'},
        'HH': {'idx': 23, 'guests': '4', 'nights': '4', 'name': 'Jackson Reis', 'bdate': '18/06/2026', 'clean': '50 €', 'srv': '68,32 €', 'f15': '=6*4*4'},
        'HL': {'idx': 27, 'guests': '3', 'nights': '3', 'name': 'Gerard Maronski', 'bdate': '04/03/2026', 'clean': '50 €', 'srv': '48,98 €', 'f15': '=6*3*3'},
        'HO': {'idx': 30, 'guests': '3', 'nights': '2', 'name': 'Addie Lowe', 'bdate': '19/03/2026', 'clean': '50 €', 'srv': '43,17 €', 'f15': '=6*3*2'},
    }

    last_cols_indices = set(d['idx'] for d in last_night_data.values())

    for col_letter, d in last_night_data.items():
        c_idx = d['idx']
        # Row 1: guests
        if grid[0][c_idx] != d['guests']:
            errors.append(f"Riga 1 col {col_letter}: '{grid[0][c_idx]}', atteso '{d['guests']}'")
        # Row 2: nights
        if grid[1][c_idx] != d['nights']:
            errors.append(f"Riga 2 col {col_letter}: '{grid[1][c_idx]}', atteso '{d['nights']}'")
        # Row 8: sum formula
        exp_r8 = f"=SUM(OFFSET({col_letter}5; 0; -{col_letter}2+1;1;{col_letter}2))"
        if grid[7][c_idx] != exp_r8:
            errors.append(f"Riga 8 col {col_letter}: '{grid[7][c_idx]}', atteso '{exp_r8}'")
        # Row 9: Airbnb
        if grid[8][c_idx] != 'Airbnb':
            errors.append(f"Riga 9 col {col_letter}: '{grid[8][c_idx]}', atteso 'Airbnb'")
        # Row 10: name
        if grid[9][c_idx] != d['name']:
            errors.append(f"Riga 10 col {col_letter}: '{grid[9][c_idx]}', atteso '{d['name']}'")
        # Row 11: bdate
        if grid[10][c_idx] != d['bdate']:
            errors.append(f"Riga 11 col {col_letter}: '{grid[10][c_idx]}', atteso '{d['bdate']}'")
        # Row 12: cleaning
        if grid[11][c_idx] != d['clean']:
            errors.append(f"Riga 12 col {col_letter}: '{grid[11][c_idx]}', atteso '{d['clean']}'")
        # Row 13: srv
        if grid[12][c_idx] != d['srv']:
            errors.append(f"Riga 13 col {col_letter}: '{grid[12][c_idx]}', atteso '{d['srv']}'")
        # Row 14: ratio formula
        exp_r14 = f"={col_letter}13/({col_letter}8+{col_letter}12)"
        if grid[13][c_idx] != exp_r14:
            errors.append(f"Riga 14 col {col_letter}: '{grid[13][c_idx]}', atteso '{exp_r14}'")
        # Row 15: f15
        if grid[14][c_idx] != d['f15']:
            errors.append(f"Riga 15 col {col_letter}: '{grid[14][c_idx]}', atteso '{d['f15']}'")
        # Row 16: sum all
        exp_r16 = f"={col_letter}8+{col_letter}12+{col_letter}13+{col_letter}15+{col_letter}7"
        if grid[15][c_idx] != exp_r16:
            errors.append(f"Riga 16 col {col_letter}: '{grid[15][c_idx]}', atteso '{exp_r16}'")
        # Row 17: constant
        exp_r17 = "=3%*1,22"
        if grid[16][c_idx] != exp_r17:
            errors.append(f"Riga 17 col {col_letter}: '{grid[16][c_idx]}', atteso '{exp_r17}'")
        # Row 18: formula
        exp_r18 = f"=-({col_letter}8+{col_letter}7+{col_letter}12)*{col_letter}17"
        if grid[17][c_idx] != exp_r18:
            errors.append(f"Riga 18 col {col_letter}: '{grid[17][c_idx]}', atteso '{exp_r18}'")
        # Row 19: formula
        exp_r19 = f"={col_letter}8+{col_letter}12+{col_letter}18+{col_letter}7"
        if grid[18][c_idx] != exp_r19:
            errors.append(f"Riga 19 col {col_letter}: '{grid[18][c_idx]}', atteso '{exp_r19}'")
        # Row 21: 21%
        if grid[20][c_idx] != "21%":
            errors.append(f"Riga 21 col {col_letter}: '{grid[20][c_idx]}', atteso '21%'")
        # Row 22: formula
        exp_r22 = f"=-{col_letter}21*{col_letter}19"
        if grid[21][c_idx] != exp_r22:
            errors.append(f"Riga 22 col {col_letter}: '{grid[21][c_idx]}', atteso '{exp_r22}'")
        # Row 24: formula
        exp_r24 = f"={col_letter}19+{col_letter}22"
        if grid[23][c_idx] != exp_r24:
            errors.append(f"Riga 24 col {col_letter}: '{grid[23][c_idx]}', atteso '{exp_r24}'")
        # Row 25: formula
        exp_r25 = f"={col_letter}24-{col_letter}12"
        if grid[24][c_idx] != exp_r25:
            errors.append(f"Riga 25 col {col_letter}: '{grid[24][c_idx]}', atteso '{exp_r25}'")
        # Row 26: formula
        exp_r26 = f"={col_letter}25/{col_letter}16"
        if grid[25][c_idx] != exp_r26:
            errors.append(f"Riga 26 col {col_letter}: '{grid[25][c_idx]}', atteso '{exp_r26}'")

    print("[OK] Dati e formule delle 9 prenotazioni nelle rispettive ultime colonne: 100% corretti")

    # Check non-last-night columns: rows other than 3, 4, 5 (and for free days only 3, 4) must be empty
    for c_idx in range(31):
        if c_idx not in last_cols_indices:
            for r in range(26):
                if r not in (2, 3, 4): # not day, date, rate
                    if grid[r][c_idx] != '':
                        errors.append(f"Colonna {col_names[c_idx]} (non ultima notte), riga {r+1} deve essere vuota, invece: '{grid[r][c_idx]}'")

    print("[OK] Tutte le colonne intermedie/non finali: righe 1, 2, 6-26 perfettamente vuote")

    if errors:
        print(f"\n[FAIL] SANITY CHECK FALLITO con {len(errors)} errori:")
        for e in errors:
            print(f"  - {e}")
        return False
    else:
        print("\n[SUCCESS] SANITY CHECK COMPLETATO CON SUCCESSO! TUTTI I CRITERI RISPETTATI AL 100%.")
        return True

if __name__ == '__main__':
    ok = run_sanity_check('prenotazioni_agosto_settembre_regole.csv')
    sys.exit(0 if ok else 1)
