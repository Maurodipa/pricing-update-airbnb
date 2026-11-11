"""
update_airbnb_prices.py
-----------------------
Script per l'aggiornamento automatico delle tariffe nel calendario host Airbnb.

Prerequisiti:
  pip install playwright python-dateutil
  playwright install chromium

Chrome deve essere avviato con:
  chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\\ChromeDebug"

Uso:
  python update_airbnb_prices.py \
      --property-id "12345678" \
      --dates "01/11/2026,02/11/2026" \
      --prices "150,160"

  oppure con range di date (stesso prezzo per tutte):
  python update_airbnb_prices.py \
      --property-id "12345678" \
      --date-from "01/11/2026" \
      --date-to "30/11/2026" \
      --price 150
"""

import argparse
import random
import sys
import time
from datetime import datetime, timedelta

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, sync_playwright

# ---------------------------------------------------------------------------
# Configurazione
# ---------------------------------------------------------------------------
CDP_URL = "http://localhost:9222"
MAX_DATES = 90
CALENDAR_URL_TEMPLATE = (
    "https://www.airbnb.com/multicalendar/{property_id}/pricing-and-availability"
)
FALLBACK_CALENDAR_URL_TEMPLATE = (
    "https://www.airbnb.com/hosting/listings/{property_id}/calendar"
)
DEFAULT_TIMEOUT_MS = 15_000  # 15 secondi


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_dates_from_args(args: argparse.Namespace) -> list[datetime]:
    """Restituisce la lista di oggetti datetime dalle date fornite via CLI."""
    if args.dates:
        raw = [d.strip() for d in args.dates.split(",") if d.strip()]
        return [datetime.strptime(d, "%d/%m/%Y") for d in raw]

    if args.date_from and args.date_to:
        start = datetime.strptime(args.date_from, "%d/%m/%Y")
        end = datetime.strptime(args.date_to, "%d/%m/%Y")
        if end < start:
            raise ValueError("--date-to deve essere uguale o successivo a --date-from")
        delta = (end - start).days + 1
        return [start + timedelta(days=i) for i in range(delta)]

    raise ValueError(
        "Fornisci --dates oppure --date-from e --date-to"
    )


def parse_prices_from_args(args: argparse.Namespace, n_dates: int) -> list[float]:
    """Restituisce la lista di prezzi, espansa se necessario."""
    if args.prices:
        raw = [p.strip() for p in args.prices.split(",") if p.strip()]
        prices = [float(p) for p in raw]
        if len(prices) == 1:
            return prices * n_dates
        if len(prices) != n_dates:
            raise ValueError(
                f"Il numero di prezzi ({len(prices)}) non corrisponde "
                f"al numero di date ({n_dates})"
            )
        return prices

    if args.price is not None:
        return [float(args.price)] * n_dates

    raise ValueError("Fornisci --prices oppure --price")


def random_delay(min_s: float = 2.0, max_s: float = 5.0) -> None:
    """Attesa randomica anti-rate-limiting."""
    delay = random.uniform(min_s, max_s)
    time.sleep(delay)


def format_date_iso(dt: datetime) -> str:
    """Converte datetime in stringa ISO YYYY-MM-DD per i selettori DOM."""
    return dt.strftime("%Y-%m-%d")


def format_date_display(dt: datetime) -> str:
    """Converte datetime in formato leggibile dd/mm/yyyy."""
    return dt.strftime("%d/%m/%Y")


# ---------------------------------------------------------------------------
# Core: aggiornamento singola data
# ---------------------------------------------------------------------------

def update_single_date(page, dt: datetime, price: float) -> None:
    """
    Aggiorna il prezzo per una singola data.
    Solleva eccezione in caso di errore.
    """
    iso_date = format_date_iso(dt)

    # -------------------------------------------------------------------------
    # Step 0: chiudi il pannello di selezione multipla se è aperto
    # Se il calendario è in modalità multi-selezione (URL contiene /edit-selected-dates),
    # cliccare su un giorno aggiungerebbe quella data alla selezione esistente anziché
    # aprire il pannello di modifica singola. Si chiude navigando al calendario base.
    # IMPORTANTE: questo step deve avvenire PRIMA di cercare il day_element nel DOM,
    # perché la navigazione invaliderebbe l'ElementHandle.
    # -------------------------------------------------------------------------
    current_url = page.url
    if "edit-selected-dates" in current_url:
        print(f"      ↩  Pannello multi-selezione aperto — chiusura in corso...")
        base_url = current_url.split("/edit-selected-dates")[0] + "/pricing-and-availability"
        page.goto(base_url, wait_until="domcontentloaded", timeout=30_000)
        page.wait_for_timeout(1_500)
    else:
        # Prova a chiudere il pannello laterale se è già aperto (bottone X)
        try:
            for label in ["Close", "Cerrar", "Chiudi", "cerrar"]:
                close_btn = page.query_selector(f'button[aria-label*="{label}"]')
                if close_btn and close_btn.is_visible():
                    close_btn.click()
                    page.wait_for_timeout(600)
                    break
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # Step 1: trova e clicca il giorno nel calendario
    # Dal DOM reale: i bottoni giorno hanno id="date-YYYY-MM-DD" e data-date="YYYY-MM-DD"
    # (questo step viene DOPO Step 0 per evitare ElementHandle stale dopo navigazione)
    # -------------------------------------------------------------------------
    day_selectors = [
        f'button[data-date="{iso_date}"]',   # ✅ Confermato dal DOM reale
        f'#date-{iso_date}',                  # ✅ Alternativa con id
        f'[data-date="{iso_date}"]',          # Generico (td, div, ecc.)
    ]

    day_element = None
    for selector in day_selectors:
        try:
            el = page.wait_for_selector(selector, timeout=6_000)
            if el:
                day_element = el
                break
        except PlaywrightTimeoutError:
            continue

    if day_element is None:
        raise RuntimeError(
            f"Elemento DOM per la data {iso_date} non trovato. "
            f"Il giorno potrebbe non essere visibile: scrolla il calendario verso {iso_date}."
        )

    # Scrolla il giorno nella viewport e clicca
    day_element.scroll_into_view_if_needed()
    page.wait_for_timeout(500)
    day_element.click()
    page.wait_for_timeout(2_000)  # Attendi apertura pannello laterale

    # -------------------------------------------------------------------------
    # Step 2: clicca sulla card del prezzo nel pannello laterale
    # Usa JavaScript per trovare il bottone/div che contiene il prezzo corrente
    # evitando i falsi positivi di :has-text() che matcha elementi antenati
    # -------------------------------------------------------------------------
    price_card_clicked = page.evaluate(r"""
        () => {
            // Cerca il contenitore diretto del prezzo (es. "€130")
            // L'elemento deve avere solo testo figlio o al più un livello
            const candidates = [...document.querySelectorAll('*')].filter(el => {
                const text = el.innerText?.trim() || '';
                return /^€\s*\d+$/.test(text) && el.children.length <= 2;
            });
            if (candidates.length > 0) {
                // Prendi il più piccolo (più specifico)
                candidates.sort((a, b) =>
                    a.getBoundingClientRect().width - b.getBoundingClientRect().width
                );
                candidates[0].click();
                return true;
            }
            return false;
        }
    """)

    if not price_card_clicked:
        # Fallback: prova con Playwright selector su testo numerico
        try:
            page.locator("main >> text=/€\\d+/").first.click(timeout=4_000)
        except Exception:
            pass  # Continua comunque: forse l'input è già visibile

    page.wait_for_timeout(1_200)

    # -------------------------------------------------------------------------
    # Step 3: trova il campo di input del prezzo nel pannello
    # -------------------------------------------------------------------------
    price_input = None

    # Strategia: cerca input visibili nella pagina dopo l'apertura della card
    input_selectors = [
        'input[type="number"]',
        'input[type="text"]',
        'input[id*="price"]',
        'input[name*="price"]',
        'input[aria-label*="recio"]',   # Precio
        'input[aria-label*="rice"]',    # Price
    ]

    for selector in input_selectors:
        try:
            els = page.query_selector_all(selector)
            for el in els:
                if el.is_visible():
                    price_input = el
                    break
            if price_input:
                break
        except Exception:
            continue

    if price_input is None:
        raise RuntimeError(
            "Campo di input del prezzo non trovato nel pannello laterale. "
            "Prova ad aprire manualmente il pannello del prezzo e verifica "
            "che esista un campo di testo editabile."
        )

    # Cancella valore attuale e inserisci il nuovo prezzo
    price_input.click(click_count=3)
    page.wait_for_timeout(300)
    price_input.fill(str(int(price)))
    page.wait_for_timeout(600)

    # -------------------------------------------------------------------------
    # Step 4: clicca il pulsante Salva
    # -------------------------------------------------------------------------
    save_button_selectors = [
        'button[data-testid*="save"]',
        'button:has-text("Guardar")',   # Spagnolo (airbnb.mx)
        'button:has-text("Save")',
        'button:has-text("Salva")',
        'button:has-text("Apply")',
        'button:has-text("Applica")',
        'button[aria-label*="Guardar"]',
        'button[aria-label*="Save"]',
    ]

    save_button = None
    for selector in save_button_selectors:
        try:
            el = page.wait_for_selector(selector, timeout=5_000)
            if el and el.is_visible():
                save_button = el
                break
        except PlaywrightTimeoutError:
            continue

    if save_button is None:
        raise RuntimeError("Pulsante 'Salva' non trovato")

    save_button.click()

    # Attendi conferma visiva (scomparsa del dialogo o toast)
    try:
        page.wait_for_selector('[role="dialog"]', state="hidden", timeout=DEFAULT_TIMEOUT_MS)
    except PlaywrightTimeoutError:
        # Fallback: attendi semplicemente che il pannello laterale si chiuda
        page.wait_for_timeout(3_000)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Aggiorna le tariffe del calendario Airbnb via browser automation."
    )
    parser.add_argument("--property-id", required=True, help="ID della proprietà Airbnb")
    parser.add_argument(
        "--dates",
        help="Date separate da virgola (dd/mm/yyyy). Es: 01/11/2026,02/11/2026",
    )
    parser.add_argument("--date-from", help="Inizio intervallo (dd/mm/yyyy)")
    parser.add_argument("--date-to", help="Fine intervallo (dd/mm/yyyy)")
    parser.add_argument(
        "--prices",
        help="Prezzi separati da virgola, corrispondenti a --dates",
    )
    parser.add_argument("--price", type=float, help="Prezzo singolo per tutte le date")
    parser.add_argument(
        "--cdp-url",
        default=CDP_URL,
        help=f"URL del Chrome DevTools Protocol (default: {CDP_URL})",
    )
    args = parser.parse_args()

    # --- Parsing input ---
    try:
        dates = parse_dates_from_args(args)
        prices = parse_prices_from_args(args, len(dates))
    except ValueError as e:
        print(f"[ERRORE INPUT] {e}")
        sys.exit(1)

    if len(dates) > MAX_DATES:
        print(f"[ERRORE] Massimo {MAX_DATES} date per esecuzione. "
              f"Fornite: {len(dates)}. Suddividi in più chiamate.")
        sys.exit(1)

    print(f"\n🏠 Proprietà: {args.property_id}")
    print(f"📅 Date da aggiornare: {len(dates)}")
    print(f"🔗 Connessione CDP: {args.cdp_url}\n")

    successful_updates: list[str] = []
    failed_updates: list[tuple[str, str]] = []

    with sync_playwright() as p:
        # Connessione alla sessione browser esistente
        try:
            browser = p.chromium.connect_over_cdp(args.cdp_url)
        except Exception as e:
            print(
                f"[ERRORE CRITICO] Impossibile connettersi al browser su {args.cdp_url}.\n"
                f"Assicurati che Chrome sia avviato con --remote-debugging-port=9222.\n"
                f"Dettaglio: {e}"
            )
            sys.exit(1)

        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()

        # Navigazione al calendario
        calendar_url = CALENDAR_URL_TEMPLATE.format(property_id=args.property_id)
        current_url = page.url

        if args.property_id not in current_url or "calendar" not in current_url:
            print(f"📍 Navigazione verso il calendario: {calendar_url}")
            try:
                # 'domcontentloaded' è più tollerante di 'networkidle' per pagine pesanti
                page.goto(calendar_url, wait_until="domcontentloaded", timeout=60_000)
            except PlaywrightTimeoutError:
                fallback_url = FALLBACK_CALENDAR_URL_TEMPLATE.format(
                    property_id=args.property_id
                )
                print(f"⚠️  Timeout sul primo URL, tentativo con: {fallback_url}")
                try:
                    page.goto(fallback_url, wait_until="domcontentloaded", timeout=60_000)
                except PlaywrightTimeoutError:
                    print("⚠️  Timeout anche sul secondo URL. La pagina potrebbe richiedere login.")
            except Exception as e:
                print(f"⚠️  Errore di navigazione: {e}")
        else:
            print(f"✅ Già sul calendario ({current_url})")

        # --- Pausa manuale per login / OTP ---
        print()
        print("=" * 60)
        print("⏸️  PAUSA — Controlla il browser Chrome.")
        print("   Se Airbnb ha richiesto login o OTP, completalo ora.")
        print("   Quando il CALENDARIO è visibile nel browser,")
        print("   torna qui e premi INVIO per continuare...")
        print("=" * 60)
        input()
        print("▶️  Ripresa esecuzione...\n")

        # --- Loop principale ---
        for idx, (dt, price) in enumerate(zip(dates, prices), start=1):
            date_str = format_date_display(dt)
            print(f"[{idx}/{len(dates)}] Aggiornamento {date_str} → € {price:.0f} ...", end=" ")

            try:
                random_delay(2.0, 5.0)
                update_single_date(page, dt, price)
                print("✅")
                successful_updates.append(f"{date_str}: € {price:.0f}")

            except PlaywrightTimeoutError as e:
                msg = f"Timeout durante l'operazione ({e})"
                print(f"❌ ({msg})")
                failed_updates.append((date_str, msg))

            except Exception as e:
                msg = str(e)
                print(f"❌ ({msg})")
                failed_updates.append((date_str, msg))

    # --- Report finale ---
    print("\n" + "=" * 60)
    print("📊 REPORT FINALE")
    print("=" * 60)

    if successful_updates:
        print("\n✅ Tariffe aggiornate con successo per le seguenti date:")
        for entry in successful_updates:
            print(f"   - {entry}")

    if failed_updates:
        print("\n❌ Errore nell'aggiornamento per le seguenti date:")
        for date_str, reason in failed_updates:
            print(f"   - {date_str}: {reason}")

    if not failed_updates:
        print("\n🎉 Tutti gli aggiornamenti completati senza errori!")
    elif not successful_updates:
        print(
            "\n⚠️  Nessun aggiornamento riuscito. "
            "Verifica la connessione al browser e l'autenticazione Airbnb."
        )
    else:
        print(
            f"\n📈 Successi: {len(successful_updates)} | "
            f"Fallimenti: {len(failed_updates)}"
        )


if __name__ == "__main__":
    main()
