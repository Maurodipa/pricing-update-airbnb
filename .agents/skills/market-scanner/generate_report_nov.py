import json
import os
from collections import defaultdict

with open("market_data_1month.json", "r", encoding="utf-8") as f:
    data = json.load(f)

import re
with open("../../../mr-airbnb/competitori_vicini_500m_nov_10_14_details.json", "r", encoding="utf-8") as f:
    details_db = json.load(f)

target_ids = []
for apt_id, details in details_db.items():
    if not isinstance(details, list): continue
    guests = -1; bedrooms = -1
    for section in details:
        if section.get("sectionComponentType") == "STAYS_PDP_AVAILABILITY_CALENDAR_INLINE":
            guests = section.get("section", {}).get("maxGuestCapacity", -1)
        sharing_title = section.get("section", {}).get("shareSave", {}).get("sharingConfig", {}).get("title", "").lower()
        if sharing_title:
            match = re.search(r'(\d+)\s+bedroom', sharing_title)
            if match:
                bedrooms = int(match.group(1))
            elif "studio" in sharing_title or "monolocale" in sharing_title:
                bedrooms = 1
    if guests != -1 and guests <= 4 and bedrooms == 1:
        target_ids.append(apt_id)

apts_data = defaultdict(list)

for date, apts in data.items():
    if not date.startswith("2026-11"):
        continue
    for apt_id, info in apts.items():
        if apt_id in target_ids:
            info["date"] = date
            apts_data[apt_id].append(info)

report = "# Report Prezzi Novembre (10-14) 2026 - 54 Gemelli (1 Camera/Monolocale)\n\n"

prices_all = []
booked_count = 0
free_count = 0

for apt_id in target_ids:
    days = apts_data.get(apt_id, [])
    days.sort(key=lambda x: x["date"])
    
    report += f"## Appartamento ID: {apt_id}\n\n"
    
    if not days:
        report += "Nessun dato disponibile.\n\n"
        booked_count += 1
        continue
        
    prices = [d["rate"] for d in days if d.get("status") == "OK"]
    if prices:
        free_count += 1
        avg = sum(prices) / len(prices)
        report += f"**Tariffa Media (10-14 Nov):** {avg:.2f} €/notte\n"
        prices_all.extend(prices)
    else:
        booked_count += 1
        report += "**Completamente Occupato o Chiuso.**\n\n"
        
    report += "### Dettaglio\n"
    for d in days:
        date = d["date"]
        status = d.get("status")
        if status == "OK":
            price = d.get("rate")
            min_stay = d.get("minStay", "?")
            discount = " (Offerta Speciale!)" if d.get("specialOffer") else ""
            isolated = " [Giorno Isolato]" if d.get("isIsolated") else ""
            report += f"- {date}: Libero - **{price} €** (Min Stay: {min_stay}){discount}{isolated}\n"
        else:
            report += f"- {date}: Occupato / Chiuso\n"
    report += "\n---\n\n"
    
if prices_all:
    market_avg = sum(prices_all) / len(prices_all)
    min_price = min(prices_all)
    max_price = max(prices_all)
else:
    market_avg = min_price = max_price = 0

summary = f"**Riepilogo Globale (54 Appartamenti Gemelli)**\n"
summary += f"- Appartamenti con almeno 1 notte libera: {free_count}\n"
summary += f"- Appartamenti totalmente occupati/chiusi: {booked_count}\n"
summary += f"- **Prezzo Medio del Mercato:** {market_avg:.2f} €/notte\n"
summary += f"- Prezzo Minimo Trovato: {min_price} €\n"
summary += f"- Prezzo Massimo Trovato: {max_price} €\n\n"

report = summary + report

out_path = r"C:\Users\mauro\.gemini\antigravity\brain\b63ef745-8fc3-4ec8-a1a4-9341f241e9c5\report_novembre_54_gemelli.md"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(report)
    
print(f"Generato con media: {market_avg:.2f}, minimo: {min_price}, max: {max_price}")
print(f"Liberi: {free_count}, Occupati: {booked_count}")
