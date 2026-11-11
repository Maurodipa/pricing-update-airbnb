# Script to generate prenotazioni_luglio_agosto_regole.csv
# following Regole per l'agente airbnb-reservation-reader.md

cols = [
    # 1. Juan Gonzalez (FC, FD, FE)
    {'col': 'FC', 'day': 'mar', 'date': '30-giu', 'rate': '61,20 €'},
    {'col': 'FD', 'day': 'mer', 'date': '1-lug', 'rate': '61,20 €'},
    {'col': 'FE', 'day': 'gio', 'date': '2-lug', 'rate': '61,20 €', 'is_last': True,
     'guests': 3, 'nights': 3, 'name': 'Juan Gonzalez', 'booking_date': '29/06/2026', 'cleaning': '50 €', 'service': '35,65 €'},
    
    # 2. Béatrice Dieudonne (FF, FG, FH)
    {'col': 'FF', 'day': 'ven', 'date': '3-lug', 'rate': '117 €'},
    {'col': 'FG', 'day': 'sab', 'date': '4-lug', 'rate': '119 €'},
    {'col': 'FH', 'day': 'dom', 'date': '5-lug', 'rate': '109 €', 'is_last': True,
     'guests': 3, 'nights': 3, 'name': 'Béatrice Dieudonne', 'booking_date': '21/02/2026', 'cleaning': '50 €', 'service': '66,91 €'},

    # 3. Jorge Calvo (FI, FJ)
    {'col': 'FI', 'day': 'lun', 'date': '6-lug', 'rate': '100 €'},
    {'col': 'FJ', 'day': 'mar', 'date': '7-lug', 'rate': '100 €', 'is_last': True,
     'guests': 4, 'nights': 2, 'name': 'Jorge Calvo', 'booking_date': '29/05/2026', 'cleaning': '50 €', 'service': '43,10 €'},

    # 4. Roberto Pedrouzo (FK, FL, FM, FN, FO)
    {'col': 'FK', 'day': 'mer', 'date': '8-lug', 'rate': '119 €'},
    {'col': 'FL', 'day': 'gio', 'date': '9-lug', 'rate': '119 €'},
    {'col': 'FM', 'day': 'ven', 'date': '10-lug', 'rate': '119 €'},
    {'col': 'FN', 'day': 'sab', 'date': '11-lug', 'rate': '119 €'},
    {'col': 'FO', 'day': 'dom', 'date': '12-lug', 'rate': '119 €', 'is_last': True,
     'guests': 4, 'nights': 5, 'name': 'Roberto Pedrouzo', 'booking_date': '18/02/2026', 'cleaning': '50 €', 'service': '110,18 €'},

    # 5. Adrian Zakrzewski (FP, FQ, FR)
    {'col': 'FP', 'day': 'lun', 'date': '13-lug', 'rate': '91 €'},
    {'col': 'FQ', 'day': 'mar', 'date': '14-lug', 'rate': '91 €'},
    {'col': 'FR', 'day': 'mer', 'date': '15-lug', 'rate': '90 €', 'is_last': True,
     'guests': 4, 'nights': 3, 'name': 'Adrian Zakrzewski', 'booking_date': '31/03/2026', 'cleaning': '50 €', 'service': '60,43 €'},

    # 6. Joe Kouri (FS, FT, FU)
    {'col': 'FS', 'day': 'gio', 'date': '16-lug', 'rate': '106 €'},
    {'col': 'FT', 'day': 'ven', 'date': '17-lug', 'rate': '111 €'},
    {'col': 'FU', 'day': 'sab', 'date': '18-lug', 'rate': '113 €', 'is_last': True,
     'guests': 3, 'nights': 3, 'name': 'Joe Kouri', 'booking_date': '04/05/2026', 'cleaning': '50 €', 'service': '57,99 €'},

    # 7. Allan Coimbra Santana (FV, FW, FX)
    {'col': 'FV', 'day': 'dom', 'date': '19-lug', 'rate': '105 €'},
    {'col': 'FW', 'day': 'lun', 'date': '20-lug', 'rate': '103 €'},
    {'col': 'FX', 'day': 'mar', 'date': '21-lug', 'rate': '103 €', 'is_last': True,
     'guests': 3, 'nights': 3, 'name': 'Allan Coimbra Santana', 'booking_date': '22/02/2026', 'cleaning': '50 €', 'service': '59,20 €'},

    # 8. Erica Martinez (FY, FZ)
    {'col': 'FY', 'day': 'mer', 'date': '22-lug', 'rate': '130 €'},
    {'col': 'FZ', 'day': 'gio', 'date': '23-lug', 'rate': '130 €', 'is_last': True,
     'guests': 4, 'nights': 2, 'name': 'Erica Martinez', 'booking_date': '20/04/2026', 'cleaning': '50 €', 'service': '47,30 €'},

    # 9. GA: 24 luglio (colonna vuota)
    {'col': 'GA', 'is_empty_col': True},

    # 10. Jacobo Perez (GB, GC, GD)
    {'col': 'GB', 'day': 'sab', 'date': '25-lug', 'rate': '118 €'},
    {'col': 'GC', 'day': 'dom', 'date': '26-lug', 'rate': '112 €'},
    {'col': 'GD', 'day': 'lun', 'date': '27-lug', 'rate': '111 €', 'is_last': True,
     'guests': 4, 'nights': 3, 'name': 'Jacobo Perez', 'booking_date': '01/03/2026', 'cleaning': '50 €', 'service': '66,79 €'},

    # 11. Ismael Pichardo (GE)
    {'col': 'GE', 'day': 'mar', 'date': '28-lug', 'rate': '59 €', 'is_last': True,
     'guests': 4, 'nights': 1, 'name': 'Ismael Pichardo', 'booking_date': '28/07/2026', 'cleaning': '59 €', 'service': '0,00 €'},

    # 12. Carsten Tappe (GF, GG)
    {'col': 'GF', 'day': 'mer', 'date': '29-lug', 'rate': '111 €'},
    {'col': 'GG', 'day': 'gio', 'date': '30-lug', 'rate': '112 €', 'is_last': True,
     'guests': 3, 'nights': 2, 'name': 'Carsten Tappe', 'booking_date': '01/03/2026', 'cleaning': '50 €', 'service': '45,86 €'},

    # 13. Cel In (GH, GI)
    {'col': 'GH', 'day': 'ven', 'date': '31-lug', 'rate': '106 €'},
    {'col': 'GI', 'day': 'sab', 'date': '1-ago', 'rate': '100 €', 'is_last': True,
     'guests': 4, 'nights': 2, 'name': 'Cel In', 'booking_date': '21/02/2026', 'cleaning': '50 €', 'service': '43,37 €'},
]

grid = [[] for _ in range(26)]

for c in cols:
    col_letter = c['col']
    is_empty = c.get('is_empty_col', False)
    is_last = c.get('is_last', False)

    # Row 1: guests
    grid[0].append(str(c['guests']) if is_last else '')
    # Row 2: nights
    grid[1].append(str(c['nights']) if is_last else '')
    # Row 3: day
    grid[2].append('' if is_empty else c['day'])
    # Row 4: date
    grid[3].append('' if is_empty else c['date'])
    # Row 5: rate
    grid[4].append('' if is_empty else c['rate'])
    # Row 6: empty
    grid[5].append('')
    # Row 7: empty
    grid[6].append('')
    # Row 8: formula sum
    grid[7].append(f'=SUM(OFFSET({col_letter}5; 0; -{col_letter}2+1;1;{col_letter}2))' if is_last else '')
    # Row 9: Airbnb
    grid[8].append('Airbnb' if is_last else '')
    # Row 10: name
    grid[9].append(c['name'] if is_last else '')
    # Row 11: booking date
    grid[10].append(c['booking_date'] if is_last else '')
    # Row 12: cleaning
    grid[11].append(c['cleaning'] if is_last else '')
    # Row 13: guest service
    grid[12].append(c['service'] if is_last else '')
    # Row 14: formula =col13/(col8+col12)
    grid[13].append(f'={col_letter}13/({col_letter}8+{col_letter}12)' if is_last else '')
    # Row 15: formula =6*guests*nights
    grid[14].append(f'=6*{c["guests"]}*{c["nights"]}' if is_last else '')
    # Row 16: formula =col8+col12+col13+col15+col7
    grid[15].append(f'={col_letter}8+{col_letter}12+{col_letter}13+{col_letter}15+{col_letter}7' if is_last else '')
    # Row 17: formula =3%*1,22
    grid[16].append('=3%*1,22' if is_last else '')
    # Row 18: formula =-(col8+col7+col12)*col17
    grid[17].append(f'=-({col_letter}8+{col_letter}7+{col_letter}12)*{col_letter}17' if is_last else '')
    # Row 19: formula =col8+col12+col18+col7
    grid[18].append(f'={col_letter}8+{col_letter}12+{col_letter}18+{col_letter}7' if is_last else '')
    # Row 20: empty
    grid[19].append('')
    # Row 21: 21%
    grid[20].append('21%' if is_last else '')
    # Row 22: formula =-col21*col19
    grid[21].append(f'=-{col_letter}21*{col_letter}19' if is_last else '')
    # Row 23: empty
    grid[22].append('')
    # Row 24: formula =col19+col22
    grid[23].append(f'={col_letter}19+{col_letter}22' if is_last else '')
    # Row 25: formula =col24-col12
    grid[24].append(f'={col_letter}24-{col_letter}12' if is_last else '')
    # Row 25: formula =col25/col16
    grid[25].append(f'={col_letter}25/{col_letter}16' if is_last else '')

lines = ['|'.join(r) for r in grid]
output_content = '\n'.join(lines) + '\n'

with open('prenotazioni_luglio_agosto_regole.csv', 'w', encoding='utf-8') as f:
    f.write(output_content)

print('Successfully generated prenotazioni_luglio_agosto_regole.csv')
