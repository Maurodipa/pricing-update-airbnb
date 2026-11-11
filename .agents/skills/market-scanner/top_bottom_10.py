import json
import re
from collections import defaultdict

with open("market_data_1month.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Get the 54 twin IDs
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
            if info.get("status") == "OK":
                apts_data[apt_id].append(info["rate"])

# Calculate averages
avg_prices = []
for apt_id, prices in apts_data.items():
    if prices:
        avg = sum(prices) / len(prices)
        avg_prices.append((apt_id, avg))

# Sort by price
avg_prices.sort(key=lambda x: x[1])

lowest_10 = avg_prices[:10]
highest_10 = avg_prices[-10:]
highest_10.reverse()  # Top most expensive first

report = "# Classifica Prezzi: Top 10 e Flop 10 (10-14 Novembre 2026)\n\n"
report += "Di seguito i 10 concorrenti più economici e i 10 più costosi tra i tuoi 54 \"gemelli\".\n\n"

report += "## 💰 I 10 Appartamenti più Economici (Flop 10)\n"
report += "| Pos | ID Appartamento | Prezzo Medio (€/notte) |\n"
report += "|---|---|---|\n"
for i, (apt_id, price) in enumerate(lowest_10, 1):
    report += f"| {i} | {apt_id} | **{price:.2f} €** |\n"
    
report += "\n## 💎 I 10 Appartamenti più Costosi (Top 10)\n"
report += "| Pos | ID Appartamento | Prezzo Medio (€/notte) |\n"
report += "|---|---|---|\n"
for i, (apt_id, price) in enumerate(highest_10, 1):
    report += f"| {i} | {apt_id} | **{price:.2f} €** |\n"

out_path = r"C:\Users\mauro\.gemini\antigravity\brain\b63ef745-8fc3-4ec8-a1a4-9341f241e9c5\top_bottom_10_prezzi.md"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(report)
    
print("Report generato con successo.")
