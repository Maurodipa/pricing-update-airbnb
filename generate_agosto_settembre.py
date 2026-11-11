# Generator and Sanity Check script for prenotazioni_agosto_settembre_regole.csv

cols = [
    # 1. Michael Romero (GK, GL, GM)
    {'col': 'GK', 'day': 'dom', 'date': '2-ago', 'rate': '80 €'},
    {'col': 'GL', 'day': 'lun', 'date': '3-ago', 'rate': '80 €'},
    {'col': 'GM', 'day': 'mar', 'date': '4-ago', 'rate': '80 €', 'is_last': True,
     'guests': 3, 'nights': 3, 'name': 'Michael Romero', 'booking_date': '21/07/2026', 'cleaning': '50 €', 'service': '44,25 €'},

    # 2. Y Unting C Ai (GN, GO, GP)
    {'col': 'GN', 'day': 'mer', 'date': '5-ago', 'rate': '50 €'},
    {'col': 'GO', 'day': 'gio', 'date': '6-ago', 'rate': '50 €'},
    {'col': 'GP', 'day': 'ven', 'date': '7-ago', 'rate': '50 €', 'is_last': True,
     'guests': 2, 'nights': 3, 'name': 'Y\u2006Unting C\u2006Ai', 'booking_date': '04/08/2026', 'cleaning': '59 €', 'service': '0,00 €'},

    # 3. Mmaauudd Ddoorriizzoonn (GQ, GR, GS, GT)
    {'col': 'GQ', 'day': 'sab', 'date': '8-ago', 'rate': '89,75 €'},
    {'col': 'GR', 'day': 'dom', 'date': '9-ago', 'rate': '89,75 €'},
    {'col': 'GS', 'day': 'lun', 'date': '10-ago', 'rate': '89,75 €'},
    {'col': 'GT', 'day': 'mar', 'date': '11-ago', 'rate': '89,75 €', 'is_last': True,
     'guests': 4, 'nights': 4, 'name': 'Mmaauudd Ddoorriizzoonn', 'booking_date': '06/03/2026', 'cleaning': '50 €', 'service': '69,29 €'},

    # 4. Graziela Azevedo (GU, GV, GW, GX)
    {'col': 'GU', 'day': 'mer', 'date': '12-ago', 'rate': '91 €'},
    {'col': 'GV', 'day': 'gio', 'date': '13-ago', 'rate': '92 €'},
    {'col': 'GW', 'day': 'ven', 'date': '14-ago', 'rate': '98 €'},
    {'col': 'GX', 'day': 'sab', 'date': '15-ago', 'rate': '98 €', 'is_last': True,
     'guests': 4, 'nights': 4, 'name': 'Graziela Azevedo', 'booking_date': '10/03/2026', 'cleaning': '50 €', 'service': '70,35 €'},

    # 5. Colonna 16 Agosto (GY) - Giorno libero: vuota eccetto righe 3 e 4
    {'col': 'GY', 'day': 'dom', 'date': '16-ago', 'is_free_day': True},

    # 6. Stéphanie Vaculik (GZ, HA, HB, HC)
    {'col': 'GZ', 'day': 'lun', 'date': '17-ago', 'rate': '89 €'},
    {'col': 'HA', 'day': 'mar', 'date': '18-ago', 'rate': '90 €'},
    {'col': 'HB', 'day': 'mer', 'date': '19-ago', 'rate': '88 €'},
    {'col': 'HC', 'day': 'gio', 'date': '20-ago', 'rate': '88 €', 'is_last': True,
     'guests': 4, 'nights': 4, 'name': 'Stéphanie Vaculik', 'booking_date': '23/02/2026', 'cleaning': '50 €', 'service': '68,62 €'},

    # 7. Juris Rozenbergs (HD)
    {'col': 'HD', 'day': 'ven', 'date': '21-ago', 'rate': '48,96 €', 'is_last': True,
     'guests': 4, 'nights': 1, 'name': 'Juris Rozenbergs', 'booking_date': '21/08/2026', 'cleaning': '59 €', 'service': '0,00 €'},

    # 8. Jackson Reis (HE, HF, HG, HH)
    {'col': 'HE', 'day': 'sab', 'date': '22-ago', 'rate': '81 €'},
    {'col': 'HF', 'day': 'dom', 'date': '23-ago', 'rate': '78 €'},
    {'col': 'HG', 'day': 'lun', 'date': '24-ago', 'rate': '78 €'},
    {'col': 'HH', 'day': 'mar', 'date': '25-ago', 'rate': '79 €', 'is_last': True,
     'guests': 4, 'nights': 4, 'name': 'Jackson Reis', 'booking_date': '18/06/2026', 'cleaning': '50 €', 'service': '68,32 €'},

    # 9. Colonna 26 Agosto (HI) - Giorno libero: vuota eccetto righe 3 e 4
    {'col': 'HI', 'day': 'mer', 'date': '26-ago', 'is_free_day': True},

    # 10. Gerard Maronski (HJ, HK, HL)
    {'col': 'HJ', 'day': 'gio', 'date': '27-ago', 'rate': '87 €'},
    {'col': 'HK', 'day': 'ven', 'date': '28-ago', 'rate': '91 €'},
    {'col': 'HL', 'day': 'sab', 'date': '29-ago', 'rate': '93 €', 'is_last': True,
     'guests': 3, 'nights': 3, 'name': 'Gerard Maronski', 'booking_date': '04/03/2026', 'cleaning': '50 €', 'service': '48,98 €'},

    # 11. Colonna 30 Agosto (HM) - Giorno libero: vuota eccetto righe 3 e 4
    {'col': 'HM', 'day': 'dom', 'date': '30-ago', 'is_free_day': True},

    # 12. Addie Lowe (HN, HO)
    {'col': 'HN', 'day': 'lun', 'date': '31-ago', 'rate': '91 €'},
    {'col': 'HO', 'day': 'mar', 'date': '1-set', 'rate': '105 €', 'is_last': True,
     'guests': 3, 'nights': 2, 'name': 'Addie Lowe', 'booking_date': '19/03/2026', 'cleaning': '50 €', 'service': '43,17 €'},
]

grid = [[] for _ in range(26)]

for c in cols:
    col_letter = c['col']
    is_free = c.get('is_free_day', False)
    is_last = c.get('is_last', False)

    # Row 1: guests (empty if not last night or free day)
    grid[0].append(str(c['guests']) if is_last else '')
    # Row 2: nights (empty if not last night or free day)
    grid[1].append(str(c['nights']) if is_last else '')
    # Row 3: day of week
    grid[2].append(c['day'])
    # Row 4: date (gg-mmm)
    grid[3].append(c['date'])
    # Row 5: rate (empty if free day)
    grid[4].append('' if is_free else c['rate'])
    # Row 6: empty
    grid[5].append('')
    # Row 7: empty
    grid[6].append('')
    # Row 8: formula sum
    grid[7].append(f'=SUM(OFFSET({col_letter}5; 0; -{col_letter}2+1;1;{col_letter}2))' if is_last else '')
    # Row 9: Airbnb
    grid[8].append('Airbnb' if is_last else '')
    # Row 10: guest name
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
    # Row 26: formula =col25/col16
    grid[25].append(f'={col_letter}25/{col_letter}16' if is_last else '')

lines = ['|'.join(r) for r in grid]
output_content = '\n'.join(lines) + '\n'

output_file = 'prenotazioni_agosto_settembre_regole.csv'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(output_content)

print(f'Generated {output_file} successfully.')
