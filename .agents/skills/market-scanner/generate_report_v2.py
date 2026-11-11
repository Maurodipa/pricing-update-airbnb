import json
import os
from collections import defaultdict

with open("market_data_1month.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# The 9 apartments with 2 bedrooms
with open("competitors.txt", "r", encoding="utf-8") as f:
    target_ids = [line.strip() for line in f if line.strip()]

# Group by apartment
apts_data = defaultdict(list)

for date, apts in data.items():
    if not date.startswith("2026-08"):
        continue
    for apt_id, info in apts.items():
        if apt_id in target_ids:
            info["date"] = date
            apts_data[apt_id].append(info)

report = "# Report Prezzi Agosto 2026 - 9 Appartamenti a Due Camere\n\n"

for apt_id in target_ids:
    days = apts_data.get(apt_id, [])
    # Sort days by date
    days.sort(key=lambda x: x["date"])
    
    report += f"## Appartamento ID: {apt_id}\n\n"
    
    if not days:
        report += "Nessun dato disponibile (tutto occupato o chiuso).\n\n"
        continue
        
    prices = [d["purePrice"] for d in days if d.get("status") == "Disponibile"]
    if prices:
        avg = sum(prices) / len(prices)
        report += f"**Tariffa Media Mensile Pura (agosto):** {avg:.2f} €/notte\n"
        report += f"**Notti libere trovate:** {len(prices)}\n\n"
    else:
        report += "**Nessuna notte libera.** (Completamente prenotato o chiuso)\n\n"
        
    report += "### Calendario Dettagliato\n"
    for d in days:
        date = d["date"]
        status = d.get("status")
        if status == "Disponibile":
            price = d.get("purePrice")
            min_stay = d.get("minStay", "?")
            discount = " (Special Offer!)" if d.get("hasDiscount") else ""
            isolated = " [BUCO DI CALENDARIO: Giorno Isolato]" if d.get("isIsolated") else ""
            report += f"- {date}: Libero - **{price} €** (Min Stay: {min_stay}){discount}{isolated}\n"
        else:
            report += f"- {date}: Occupato / Chiuso\n"
    report += "\n---\n\n"
    
out_path = r"C:\Users\mauro\.gemini\antigravity\brain\b63ef745-8fc3-4ec8-a1a4-9341f241e9c5\report_agosto_2camere.md"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(report)
    
print(f"Report generato in: {out_path}")
