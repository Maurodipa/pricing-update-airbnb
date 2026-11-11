#!/usr/bin/env python3
"""
recommend.py - Pricing Recommender for Airbnb Short-Term Rentals
Calculates zone occupancy, competitor pricing percentiles, and computes the exact
base calendar rate to insert into Airbnb using inverse host-only fee algebra.
Supports both preprocessed databases (with 'rate' key) and raw MCP server databases (with 'rawResponse').
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime


def find_default_db():
    candidates = [
        os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'mr-airbnb', 'banca_dati_airbnb_MCPserver.json'),
        os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'mr-airbnb', 'banca_dati_airbnb_MCPserver_recovered.json'),
        os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'mr-airbnb', 'banca_dati_airbnb_MCPserver_cleaned.json'),
        os.path.join(os.path.dirname(__file__), '..', '..', 'market-scanner', 'banca_dati_airbnb.json'),
        os.path.join(os.path.dirname(__file__), '..', '..', 'market-scanner', 'market_data_1month.json'),
    ]
    for c in candidates:
        abs_c = os.path.abspath(c)
        if os.path.exists(abs_c) and os.path.getsize(abs_c) > 100:
            return abs_c
    return None


def load_cleaning_fees():
    fees = {}
    comp_paths = [
        os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'mr-airbnb', 'competitors.txt'),
        os.path.join(os.path.dirname(__file__), '..', '..', 'market-scanner', 'competitors.txt'),
    ]
    for p in comp_paths:
        abs_p = os.path.abspath(p)
        if os.path.exists(abs_p):
            try:
                with open(abs_p, 'r', encoding='utf-8') as f:
                    for line in f:
                        parts = line.strip().split(':')
                        if len(parts) >= 2:
                            try:
                                fees[parts[0].strip()] = float(parts[1].strip())
                            except ValueError:
                                pass
            except Exception:
                pass
            if fees:
                break
    return fees


def parse_price(price_string):
    if not price_string:
        return 0.0
    match = re.search(r'[\d.,]+', str(price_string))
    if match:
        num_str = match.group(0)
        if '.' in num_str and ',' in num_str:
            num_str = num_str.replace('.', '').replace(',', '.')
        elif ',' in num_str and len(num_str.split(',')[-1]) <= 2:
            num_str = num_str.replace(',', '.')
        else:
            num_str = num_str.replace(',', '')
        try:
            return float(num_str)
        except ValueError:
            return 0.0
    return 0.0


def extract_nightly_rate(entry, apt_id, fees_dict, default_cleaning=50.0, fee_mult=1.1637):
    """Extracts pure nightly rate from either preprocessed rate or rawResponse."""
    if isinstance(entry, list) and entry:
        entry = entry[-1]
    if not isinstance(entry, dict):
        return None, None
    if entry.get("status") != "OK":
        return None, None

    # Case 1: Already processed rate
    if "rate" in entry and isinstance(entry["rate"], (int, float)) and entry["rate"] > 0:
        return float(entry["rate"]), float(entry["rate"]) / 0.81089

    # Case 2: Raw MCP response
    raw = entry.get("rawResponse")
    if not raw or not isinstance(raw, dict):
        return None, None

    structured_price = raw.get("structuredDisplayPrice") or {}
    explanation_data = structured_price.get("explanationData") or {}
    price_details = explanation_data.get("priceDetails") or []

    taxes = 0.0
    total_gross = 0.0
    for group in price_details:
        for item in group.get("items", []):
            desc = item.get("description", "")
            price_str = item.get("priceString", "")
            if desc in ("Taxes", "Tasse"):
                taxes = parse_price(price_str)
            if (item.get("__typename") == "HighlightExplanationLineItem" and desc in ("Total", "Totale")) or desc in ("Total", "Totale"):
                total_gross = parse_price(price_str)

    min_stay = entry.get("minStay", 1)
    if min_stay <= 0:
        min_stay = 1

    cleaning_fee_net = fees_dict.get(apt_id, default_cleaning)
    cleaning_fee_gross = cleaning_fee_net * 1.18

    if total_gross > 0:
        calendar_total = total_gross - taxes - cleaning_fee_gross
        pure_total = calendar_total * 0.81089
        pure_nightly = pure_total / min_stay
        site_rate = (total_gross - taxes) / min_stay
        if pure_nightly > 0:
            return pure_nightly, site_rate

    return None, None


def calculate_percentile(sorted_list, p):
    """Calculates the p-th percentile of a sorted list."""
    if not sorted_list:
        return 0.0
    idx = int(round(p * (len(sorted_list) - 1)))
    idx = max(0, min(idx, len(sorted_list) - 1))
    return sorted_list[idx]


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    parser = argparse.ArgumentParser(description="Airbnb Nightly Price Recommender")
    parser.add_argument("--start", type=str, help="Start date (YYYY-MM-DD)", default=None)
    parser.add_argument("--end", type=str, help="End date (YYYY-MM-DD)", default=None)
    parser.add_argument("--db", type=str, help="Path to raw or cleaned JSON database", default=None)
    parser.add_argument("--user-apt", type=str, help="User listing ID", default="1589943047991118285")
    parser.add_argument("--output", type=str, help="Output markdown file path", default=None)
    parser.add_argument("--host-cleaning", type=float, help="Host cleaning fee (EUR)", default=50.0)
    parser.add_argument("--guest-cleaning", type=float, help="Guest cleaning fee in reverse formula (EUR)", default=59.0)
    parser.add_argument("--fee-factor", type=float, help="Host net factor", default=0.81089)

    args = parser.parse_args()

    db_path = args.db if args.db else find_default_db()
    if not db_path or not os.path.exists(db_path):
        print("Error: Database not found. Please specify --db with a valid JSON file.", file=sys.stderr)
        sys.exit(1)

    print(f"Caricamento database da: {db_path}")
    with open(db_path, "r", encoding="utf-8") as f:
        db = json.load(f)

    cleaning_fees = load_cleaning_fees()

    all_dates = sorted([k for k in db.keys() if k != "static_details" and len(k) == 10 and k.startswith("20")])
    if args.start:
        all_dates = [d for d in all_dates if d >= args.start]
    if args.end:
        all_dates = [d for d in all_dates if d <= args.end]

    if not all_dates:
        print("Nessuna data valida trovata nell'intervallo specificato.", file=sys.stderr)
        sys.exit(0)

    # Carica la lista dei competitor validi
    valid_competitors = set()
    competitors_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), "mr-airbnb", "competitors.txt")
    if os.path.exists(competitors_path):
        with open(competitors_path, 'r', encoding='utf-8') as f:
            for line in f:
                if '===' in line: break
                parts = line.split(':')
                if parts[0].strip().isdigit():
                    valid_competitors.add(parts[0].strip())

    results = []

    for d in all_dates:
        apts = db[d]
        if not isinstance(apts, dict):
            continue

        rates = []
        site_rates = []
        user_curr_rate = None

        user_site_rate = None

        user_entry = apts.get(args.user_apt)
        user_min_stay = 1
        if user_entry:
            user_curr_rate, user_site_rate = extract_nightly_rate(user_entry, args.user_apt, cleaning_fees, args.host_cleaning)
            e = user_entry[-1] if isinstance(user_entry, list) else user_entry
            user_min_stay = e.get("minStay", 1) if isinstance(e, dict) else 1
            if user_min_stay <= 0: user_min_stay = 1

        occ = 0
        avail = 0

        for apt_id, entry in apts.items():
            if apt_id == args.user_apt:
                continue
                
            if valid_competitors and apt_id not in valid_competitors:
                continue

            rate, s_rate = extract_nightly_rate(entry, apt_id, cleaning_fees, args.host_cleaning)
            if rate is not None and rate > 0:
                rates.append(rate)
                if s_rate: site_rates.append(s_rate)
                avail += 1
            else:
                occ += 1

        total = avail + occ
        occ_rate = (occ / total) * 100.0 if total > 0 else 0.0

        if not rates:
            results.append({
                "date": d,
                "occ": occ_rate,
                "avail": avail,
                "booked": occ,
                "avg": 0.0,
                "median": 0.0,
                "median_site": 0.0,
                "target_net": 0.0,
                "target_cal": 0.0,
                "user_curr": user_curr_rate,
                "user_site": user_site_rate,
                "user_min_stay": user_min_stay,
                "note": "100% Occupato o nessun dato disponibile"
            })
            continue

        rates.sort()
        site_rates.sort()
        avg_rate = sum(rates) / len(rates)
        median_rate = calculate_percentile(rates, 0.5)
        median_site_rate = calculate_percentile(site_rates, 0.5) if site_rates else 0.0

        if occ_rate >= 90.0:
            target_net = calculate_percentile(rates, 0.8)
            strategy = "Alta domanda (>90%): Mediana"
        elif occ_rate >= 75.0:
            target_net = calculate_percentile(rates, 0.6)
            strategy = "Buona domanda (75-90%): Mediana"
        elif occ_rate >= 50.0:
            target_net = calculate_percentile(rates, 0.4)
            strategy = "Media domanda (50-75%): Mediana"
        else:
            target_net = calculate_percentile(rates, 0.25)
            strategy = "Bassa domanda (<50%): Mediana"

        # Sostituiamo la logica a percentili complessa con la stessa formula esatta di get_daily_rates.py
        if median_site_rate > 0:
            cal_price = median_site_rate - (args.guest_cleaning / user_min_stay)
        else:
            cal_price = 0
            
        cal_price = round(cal_price)

        results.append({
            "date": d,
            "occ": occ_rate,
            "avail": avail,
            "booked": occ,
            "avg": avg_rate,
            "median": median_rate,
            "median_site": median_site_rate,
            "target_net": target_net,
            "target_cal": cal_price,
            "user_curr": user_curr_rate,
            "user_site": user_site_rate,
            "user_min_stay": user_min_stay,
            "strategy": strategy,
            "note": "OK"
        })

    header = f"# Raccomandazioni Strategiche Prezzi Airbnb\n\n"
    header += f"- **Database analizzato:** `{os.path.basename(db_path)}`\n"
    header += f"- **Intervallo:** {all_dates[0]} ➔ {all_dates[-1]} ({len(all_dates)} date)\n"
    header += f"- **Formula a calendario:** `Tariffa su Airbnb (Mediana) - ({args.guest_cleaning:.0f} / Minimum Stay)`\n\n"

    table = "| Data | Giorno | Occupazione | Disp / Tot | Competitor Netto (Mediana) | Competitor Calendario (Mediana) | Competitor Calendario Mediana -10% | Tariffa su Airbnb (Mediana) | airbnb-10% | Tariffa da mettere a calendario per il mio appartamento | Tariffa da mettere a calendario per il mio appartamento -10% | Target Netto | **Raccomandazione Gemini per tariffa da inserire a calendario** | Tariffa attuale sul calendario | La tua tariffa su Airbnb | Azione Consigliata |\n"
    table += "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"

    weekday_it = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]

    for r in results:
        try:
            dt = datetime.strptime(r["date"], "%Y-%m-%d")
            giorno = weekday_it[dt.weekday()]
            if dt.weekday() in (4, 5):
                giorno = f"**{giorno}**"
        except:
            giorno = "-"

        disp_str = f"{r.get('avail',0)}/{r.get('avail',0)+r.get('booked',0)}"
        if r["avg"] == 0:
            table += f"| {r['date']} | {giorno} | {r['occ']:.1f}% | {disp_str} | N/D | N/D | N/D | N/D | N/D | N/D | N/D | N/D | **N/D** | - | - | {r['note']} |\n"
            continue

        user_curr_cal = (r['user_curr'] / args.fee_factor) if r['user_curr'] else None
        user_curr_str = f"{user_curr_cal:.0f} €" if user_curr_cal else "-"
        
        user_site_str = f"{r.get('user_site'):.0f} €" if r.get('user_site') else "-"

        action = "-"
        if user_curr_cal:
            diff = r['target_cal'] - user_curr_cal
            if abs(diff) <= 3:
                action = "✅ Allineato"
            elif diff > 3:
                action = f"🔺 Aumenta (+{diff:.0f} €)"
            else:
                action = f"🔻 Riduci ({diff:.0f} €)"
        else:
            action = "Imposta tariffa"

        comp_cal_median = r['median'] / args.fee_factor
        comp_cal_median_discount = comp_cal_median * 0.90
        airbnb_10_percent = r['median_site'] * 0.90
        user_min_stay = r.get('user_min_stay', 1)
        
        user_cal_for_site = r['median_site'] - (args.guest_cleaning / user_min_stay)
        user_cal_for_site_10 = airbnb_10_percent - (args.guest_cleaning / user_min_stay)
        
        table += f"| {r['date']} | {giorno} | {r['occ']:.1f}% | {disp_str} | {r['median']:.0f} € | {comp_cal_median:.0f} € | {comp_cal_median_discount:.0f} € | {r['median_site']:.0f} € | {airbnb_10_percent:.0f} € | {user_cal_for_site:.0f} € | {user_cal_for_site_10:.0f} € | {r['target_net']:.0f} € | **{r['target_cal']:.0f} €** | {user_curr_str} | {user_site_str} | {action} |\n"

    full_report = header + table

    print(full_report)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(full_report)
        print(f"\nReport salvato con successo in: {args.output}")


if __name__ == '__main__':
    main()