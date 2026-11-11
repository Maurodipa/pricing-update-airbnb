import json

with open("market_data_1month.json", "r", encoding="utf-8") as f:
    data = json.load(f)

my_apt = "1589943047991118285"
historical_comps = [
    "602489771443051475",
    "1280484040857767756",
    "1243259212458138393",
    "2153298",
    "1105673287932582735",
    "14159837",
    "14290915",
    "4050526"
]

nov_dates = ["2026-11-10", "2026-11-11", "2026-11-12", "2026-11-13", "2026-11-14"]

my_prices = []
comp_prices = []

for date in nov_dates:
    if date in data:
        # User's apt
        my_info = data[date].get(my_apt)
        if my_info and my_info.get("status") == "OK":
            my_prices.append(my_info["rate"])
            
        # Historical competitors
        for comp_id in historical_comps:
            info = data[date].get(comp_id)
            if info and info.get("status") == "OK":
                comp_prices.append(info["rate"])

my_avg = sum(my_prices) / len(my_prices) if my_prices else 0
hist_avg = sum(comp_prices) / len(comp_prices) if comp_prices else 0
# 54 twins average is known: 147.07

report = f"""# Price Recommendation: 10-14 Novembre 2026

## Dati di Mercato Estratti
- **Il tuo appartamento (Mauro):** {my_avg:.2f} €/notte (su {len(my_prices)} notti trovate)
- **Media 8 Competitor Storici:** {hist_avg:.2f} €/notte (su {len(comp_prices)} notti disponibili)
- **Media 54 Gemelli (1 Camera/Max 4 Ospiti a 500m):** 147.07 €/notte

## Analisi della Strategia di Pricing
"""

if my_avg == 0:
    report += "Il tuo appartamento risulta **non disponibile/occupato** in queste date. Se le hai bloccate volontariamente o sei pieno, ottimo! Se invece è un errore di calendario, controlla subito Airbnb.\n\n"
elif my_avg < 147.07:
    report += f"Il tuo prezzo medio di {my_avg:.2f}€ è **inferiore alla media del mercato (147.07€)**.\nStai lasciando soldi sul tavolo. I tuoi 54 concorrenti diretti riescono a vendere a cifre più alte.\n\n"
else:
    report += f"Il tuo prezzo medio di {my_avg:.2f}€ è **superiore alla media del mercato (147.07€)**.\nSei posizionato su una fascia premium.\n\n"

report += "### Suggerimento Operativo\n"
if hist_avg > 0:
    report += f"Considerando che i tuoi 8 concorrenti storici si posizionano a {hist_avg:.2f}€ e il resto del rione a 147€, "
    if my_avg > 0 and my_avg < 145:
        report += "ti consiglio di **aumentare subito i prezzi del 10-15%** per queste date. La domanda per metà Novembre sembra ottima e non ha senso vendersi a meno del mercato."
    elif my_avg > 0 and my_avg > 180:
        report += "ti consiglio di **monitorare attentamente la conversione**. Se non ricevi visite o prenotazioni entro fine mese, prova ad abbassare gradualmente verso i 160-170€ per rimanere competitivo ma premium."
    else:
        report += "il tuo prezzo attuale è **perfettamente allineato**. Mantienilo così e aspetta che le prenotazioni dei competitor più economici si saturino, per poi raccogliere la domanda residua (che prenota all'ultimo minuto) senza fare sconti."
else:
    report += "I tuoi 8 concorrenti storici sono tutti occupati o chiusi in quelle date! Hai campo libero. Consiglio di **alzare le tariffe** sfruttando la scarsità di offerta di alta qualità."

out_path = r"C:\Users\mauro\.gemini\antigravity\brain\b63ef745-8fc3-4ec8-a1a4-9341f241e9c5\price_recommendation.md"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(report)
    
print("Recommendation generated.")
