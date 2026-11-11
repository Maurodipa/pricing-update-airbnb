import sys

def run_sanity_check(csv_path):
    print(f"=== SANITY CHECK ON {csv_path} ===")
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.splitlines()
    print(f"1. Total lines: {len(lines)} (expected: 26)")
    assert len(lines) == 26, f"Expected 26 lines, found {len(lines)}"

    cols_expected = 33
    pipes_expected = 32
    
    print("\n2. Checking separators per row (expected 32 pipes / 33 columns per row):")
    for r_idx, line in enumerate(lines, 1):
        pipe_count = line.count('|')
        cells = line.split('|')
        if pipe_count != pipes_expected or len(cells) != cols_expected:
            raise AssertionError(f"Row {r_idx}: expected {pipes_expected} pipes ({cols_expected} cells), got {pipe_count} pipes ({len(cells)} cells)")
    print("   -> ALL 26 ROWS HAVE EXACTLY 32 PIPES (33 COLUMNS)! PASS.")

    # Parse matrix
    matrix = [line.split('|') for line in lines]

    # Reservation columns mapping
    # 0-indexed column indices
    res_last_cols = {
        2: {'col': 'FE', 'name': 'Juan Gonzalez', 'guests': '3', 'nights': '3', 'date': '29/06/2026', 'cleaning': '50 €', 'service': '35,65 €'},
        5: {'col': 'FH', 'name': 'Béatrice Dieudonne', 'guests': '3', 'nights': '3', 'date': '21/02/2026', 'cleaning': '50 €', 'service': '66,91 €'},
        7: {'col': 'FJ', 'name': 'Jorge Calvo', 'guests': '4', 'nights': '2', 'date': '29/05/2026', 'cleaning': '50 €', 'service': '43,10 €'},
        12: {'col': 'FO', 'name': 'Roberto Pedrouzo', 'guests': '4', 'nights': '5', 'date': '18/02/2026', 'cleaning': '50 €', 'service': '110,18 €'},
        15: {'col': 'FR', 'name': 'Adrian Zakrzewski', 'guests': '4', 'nights': '3', 'date': '31/03/2026', 'cleaning': '50 €', 'service': '60,43 €'},
        18: {'col': 'FU', 'name': 'Joe Kouri', 'guests': '3', 'nights': '3', 'date': '04/05/2026', 'cleaning': '50 €', 'service': '57,99 €'},
        21: {'col': 'FX', 'name': 'Allan Coimbra Santana', 'guests': '3', 'nights': '3', 'date': '22/02/2026', 'cleaning': '50 €', 'service': '59,20 €'},
        23: {'col': 'FZ', 'name': 'Erica Martinez', 'guests': '4', 'nights': '2', 'date': '20/04/2026', 'cleaning': '50 €', 'service': '47,30 €'},
        27: {'col': 'GD', 'name': 'Jacobo Perez', 'guests': '4', 'nights': '3', 'date': '01/03/2026', 'cleaning': '50 €', 'service': '66,79 €'},
        28: {'col': 'GE', 'name': 'Ismael Pichardo', 'guests': '4', 'nights': '1', 'date': '28/07/2026', 'cleaning': '59 €', 'service': '0,00 €'},
        30: {'col': 'GG', 'name': 'Carsten Tappe', 'guests': '3', 'nights': '2', 'date': '01/03/2026', 'cleaning': '50 €', 'service': '45,86 €'},
        32: {'col': 'GI', 'name': 'Cel In', 'guests': '4', 'nights': '2', 'date': '21/02/2026', 'cleaning': '50 €', 'service': '43,37 €'},
    }
    
    empty_col_idx = 24 # GA (24-lug)

    print("\n3. Checking Column GA (col index 25, 0-based 24 - 24 luglio):")
    for r_idx in range(26):
        val = matrix[r_idx][empty_col_idx]
        assert val == '', f"Row {r_idx+1}, Col GA is not empty: '{val}'"
    print("   -> Col GA is completely empty across all 26 rows! PASS.")

    print("\n4. Checking fully empty rows (Rows 6, 7, 20, 23 - 1-indexed):")
    for r in [6, 7, 20, 23]:
        for c in range(cols_expected):
            val = matrix[r-1][c]
            assert val == '', f"Row {r}, Col {c+1} expected empty, got '{val}'"
    print("   -> Rows 6, 7, 20, 23 are 100% empty! PASS.")

    print("\n5. Checking Row 1 (Guests) and Row 2 (Nights):")
    for c in range(cols_expected):
        g_val = matrix[0][c]
        n_val = matrix[1][c]
        if c in res_last_cols:
            exp_g = res_last_cols[c]['guests']
            exp_n = res_last_cols[c]['nights']
            assert g_val == exp_g, f"Col {c+1}: expected guests {exp_g}, got {g_val}"
            assert n_val == exp_n, f"Col {c+1}: expected nights {exp_n}, got {n_val}"
        else:
            assert g_val == '', f"Col {c+1}: expected empty guests, got {g_val}"
            assert n_val == '', f"Col {c+1}: expected empty nights, got {n_val}"
    print("   -> Row 1 and Row 2 values and empty placements are correct! PASS.")

    print("\n6. Checking Row 3 (Days of week):")
    expected_days = [
        'mar', 'mer', 'gio', # Juan
        'ven', 'sab', 'dom', # Béatrice
        'lun', 'mar',        # Jorge
        'mer', 'gio', 'ven', 'sab', 'dom', # Roberto
        'lun', 'mar', 'mer', # Adrian
        'gio', 'ven', 'sab', # Joe
        'dom', 'lun', 'mar', # Allan
        'mer', 'gio',        # Erica
        '',                  # GA empty
        'sab', 'dom', 'lun', # Jacobo
        'mar',               # Ismael
        'mer', 'gio',        # Carsten
        'ven', 'sab'         # Cel In
    ]
    for c in range(cols_expected):
        assert matrix[2][c] == expected_days[c], f"Col {c+1}: expected day {expected_days[c]}, got {matrix[2][c]}"
    print("   -> Row 3 (Days) are completely correct! PASS.")

    print("\n7. Checking Row 4 (Dates gg-mmm):")
    expected_dates = [
        '30-giu', '1-lug', '2-lug',
        '3-lug', '4-lug', '5-lug',
        '6-lug', '7-lug',
        '8-lug', '9-lug', '10-lug', '11-lug', '12-lug',
        '13-lug', '14-lug', '15-lug',
        '16-lug', '17-lug', '18-lug',
        '19-lug', '20-lug', '21-lug',
        '22-lug', '23-lug',
        '',
        '25-lug', '26-lug', '27-lug',
        '28-lug',
        '29-lug', '30-lug',
        '31-lug', '1-ago'
    ]
    for c in range(cols_expected):
        assert matrix[3][c] == expected_dates[c], f"Col {c+1}: expected date {expected_dates[c]}, got {matrix[3][c]}"
    print("   -> Row 4 (Dates) are completely correct! PASS.")

    print("\n8. Checking Row 5 (Rates per night):")
    expected_rates = [
        '61,20 €', '61,20 €', '61,20 €',
        '117 €', '119 €', '109 €',
        '100 €', '100 €',
        '119 €', '119 €', '119 €', '119 €', '119 €',
        '91 €', '91 €', '90 €',
        '106 €', '111 €', '113 €',
        '105 €', '103 €', '103 €',
        '130 €', '130 €',
        '',
        '118 €', '112 €', '111 €',
        '59 €',
        '111 €', '112 €',
        '106 €', '100 €'
    ]
    for c in range(cols_expected):
        assert matrix[4][c] == expected_rates[c], f"Col {c+1}: expected rate {expected_rates[c]}, got {matrix[4][c]}"
    print("   -> Row 5 (Rates) are completely correct! PASS.")

    print("\n9. Checking reservation-specific rows (8 to 19, 21, 22, 24, 25, 26):")
    for c in range(cols_expected):
        if c not in res_last_cols:
            for r in [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 20, 21, 23, 24, 25]:
                assert matrix[r][c] == '', f"Row {r+1}, Col {c+1} expected empty, got '{matrix[r][c]}'"
        else:
            info = res_last_cols[c]
            col_letter = info['col']
            
            # Row 8: formula =SUM(OFFSET(<COL>5; 0; -<COL>2+1;1;<COL>2))
            exp_r8 = f"=SUM(OFFSET({col_letter}5; 0; -{col_letter}2+1;1;{col_letter}2))"
            assert matrix[7][c] == exp_r8, f"Row 8, Col {c+1}: expected {exp_r8}, got {matrix[7][c]}"

            # Row 9: Airbnb
            assert matrix[8][c] == "Airbnb", f"Row 9, Col {c+1}: expected Airbnb, got {matrix[8][c]}"

            # Row 10: Full guest name
            assert matrix[9][c] == info['name'], f"Row 10, Col {c+1}: expected {info['name']}, got {matrix[9][c]}"

            # Row 11: Booking date
            assert matrix[10][c] == info['date'], f"Row 11, Col {c+1}: expected {info['date']}, got {matrix[10][c]}"

            # Row 12: Cleaning fee
            assert matrix[11][c] == info['cleaning'], f"Row 12, Col {c+1}: expected {info['cleaning']}, got {matrix[11][c]}"

            # Row 13: Guest service fee
            assert matrix[12][c] == info['service'], f"Row 13, Col {c+1}: expected {info['service']}, got {matrix[12][c]}"

            # Row 14: =<COL>13/(<COL>8+<COL>12)
            exp_r14 = f"={col_letter}13/({col_letter}8+{col_letter}12)"
            assert matrix[13][c] == exp_r14, f"Row 14, Col {c+1}: expected {exp_r14}, got {matrix[13][c]}"

            # Row 15: =6*<guests>*<nights>
            exp_r15 = f"=6*{info['guests']}*{info['nights']}"
            assert matrix[14][c] == exp_r15, f"Row 15, Col {c+1}: expected {exp_r15}, got {matrix[14][c]}"

            # Row 16: =<COL>8+<COL>12+<COL>13+<COL>15+<COL>7
            exp_r16 = f"={col_letter}8+{col_letter}12+{col_letter}13+{col_letter}15+{col_letter}7"
            assert matrix[15][c] == exp_r16, f"Row 16, Col {c+1}: expected {exp_r16}, got {matrix[15][c]}"

            # Row 17: =3%*1,22
            assert matrix[16][c] == "=3%*1,22", f"Row 17, Col {c+1}: expected =3%*1,22, got {matrix[16][c]}"

            # Row 18: =-(<COL>8+<COL>7+<COL>12)*<COL>17
            exp_r18 = f"=-({col_letter}8+{col_letter}7+{col_letter}12)*{col_letter}17"
            assert matrix[17][c] == exp_r18, f"Row 18, Col {c+1}: expected {exp_r18}, got {matrix[17][c]}"

            # Row 19: =<COL>8+<COL>12+<COL>18+<COL>7
            exp_r19 = f"={col_letter}8+{col_letter}12+{col_letter}18+{col_letter}7"
            assert matrix[18][c] == exp_r19, f"Row 19, Col {c+1}: expected {exp_r19}, got {matrix[18][c]}"

            # Row 21: 21%
            assert matrix[20][c] == "21%", f"Row 21, Col {c+1}: expected 21%, got {matrix[20][c]}"

            # Row 22: =-<COL>21*<COL>19
            exp_r22 = f"=-{col_letter}21*{col_letter}19"
            assert matrix[21][c] == exp_r22, f"Row 22, Col {c+1}: expected {exp_r22}, got {matrix[21][c]}"

            # Row 24: =<COL>19+<COL>22
            exp_r24 = f"={col_letter}19+{col_letter}22"
            assert matrix[23][c] == exp_r24, f"Row 24, Col {c+1}: expected {exp_r24}, got {matrix[23][c]}"

            # Row 25: =<COL>24-<COL>12
            exp_r25 = f"={col_letter}24-{col_letter}12"
            assert matrix[24][c] == exp_r25, f"Row 25, Col {c+1}: expected {exp_r25}, got {matrix[24][c]}"

            # Row 26: =<COL>25/<COL>16
            exp_r26 = f"={col_letter}25/{col_letter}16"
            assert matrix[25][c] == exp_r26, f"Row 26, Col {c+1}: expected {exp_r26}, got {matrix[25][c]}"

    print("   -> All formulas, values, and column references in Rows 8-26 match rules perfectly! PASS.")
    print("\n==========================================")
    print("SANITY CHECK PASSED WITH 100% SUCCESS!")
    print("==========================================")

if __name__ == '__main__':
    run_sanity_check('prenotazioni_luglio_agosto_regole.csv')
