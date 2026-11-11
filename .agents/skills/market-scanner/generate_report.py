import json
import os
from collections import defaultdict

with open("market_data_1month.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    
report = "# Report Prezzi Agosto 2026 - Appartamenti 2 Camere (Max 4 Ospiti)\n\n"

for apt_id, days in data.items():
    report += f"## Appartamento ID: {apt_id}\n\n"
    
    if not days:
        report += "Nessun dato disponibile (tutto occupato o chiuso).\n\n"
        continue
        
    prices = [d["price"] for d in days if d["status"] == "available"]
    if prices:
        avg = sum(prices) / len(prices)
        report += f"**Tariffa Media Mensile Pura (agosto):** {avg:.2f} €/notte\n"
        report += f"**Notti libere trovate:** {len(prices)}\n\n"
    else:
        report += "Nessuna notte libera.\n\n"
        
    report += "### Calendario Dettagliato\n"
    for d in days:
        date = d["date"]
        status = d["status"]
        if status == "available":
            price = d["price"]
            min_stay = d["minStay"]
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
