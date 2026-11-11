---
name: airbnb-nightly-rate
description: Calculates the exact nightly rate of an Airbnb listing by querying available dates and using algebra to extract the rate from the total price, bypassing the hidden guest service fee.
---

# Airbnb Nightly Rate Calculator

Use this skill when the user asks to find the exact base nightly rate of an Airbnb apartment for available dates.

## Prerequisites
You need the following information:
1. **Listing ID**: The Airbnb listing ID.
2. **Start Date**: A date that is available on the calendar (format YYYY-MM-DD).
3. **Cleaning Fee (Optional)**: If known, otherwise the script will fallback to 50 EUR.

## How to use
1. Run the script provided in this skill: `node .agents/skills/airbnb-nightly-rate/scripts/calculate.js <listingId> <startDate> [cleaningFee]`
2. The script will automatically query the MCP server to find the cleaning fee.
3. It queries the Airbnb GraphQL API (`StaysPdpBookItQuery`) for 2 ospiti.
4. **Minimum Stay Support**: It automatically scans booking intervals from 1 to 7 nights. If the host has a minimum stay requirement (e.g. 4 nights), the script will automatically discover it, extract the total cost for the minimum stay block, and average it out to find the base rate per night.
5. It then extracts the exact marginal cost of the next 2 nights beyond the minimum stay using differential estimation (assuming ~16.37% guest fee), successfully handling scenarios where consecutive nights have vastly different prices.
6. The script outputs:
   - Periodo analizzato (Start and End date, and total nights)
   - Minimum Stay Rilevato (e.g., 4 notti)
   - Costo per notte (Media)
   - Tariffa Minima e Tariffa Massima
   - Dettaglio per ogni singola notte elaborata
   - Tasse di soggiorno (Tourist tax)
   - Costo delle pulizie (Cleaning cost)

## Caveats
- If the dates are genuinely blocked by the host, or the minimum stay exceeds 7 nights, the script will return an error because the API will say "Those dates are not available".
- The formula assumes the guest service fee percentage is almost perfectly flat between consecutive stays. Small rounding differences might yield a rate like `130.07 €` instead of exactly `130.00 €`. You should round it logically when presenting it to the user.
