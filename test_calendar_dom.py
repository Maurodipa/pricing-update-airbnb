import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()
    
    # Scroll through the calendar to load months
    for _ in range(12):
        page.mouse.wheel(0, 1000)
        page.wait_for_timeout(300)
        
    reservations = page.evaluate("""() => {
        const resEls = document.querySelectorAll('[id^="RESERVATION_"]');
        return Array.from(resEls).map(el => el.id.replace('RESERVATION_', '')).sort();
    }""")
    print(f"Total reservation dates found on live calendar: {len(reservations)}")
    print("Reservation dates:", reservations)
