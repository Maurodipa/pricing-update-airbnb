const fs = require('fs');
const path = require('path');

const DATA_FILE = path.join(__dirname, '..', 'banca_dati_airbnb.json');
const COMPETITORS_FILE = path.join(__dirname, '..', 'competitors.txt');

// Helper to simulate human delay
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
function randomSleep(minMs, maxMs) {
  const ms = Math.floor(Math.random() * (maxMs - minMs + 1)) + minMs;
  return sleep(ms);
}

async function fetchPrice(listingId, checkIn, checkOut) {
  const url = "https://www.airbnb.com/api/v3/StaysPdpBookItQuery";
  const b64Id = Buffer.from(`DemandStayListing:${listingId}`).toString('base64');
  
  const payload = {
    operationName: "StaysPdpBookItQuery",
    variables: {
      id: b64Id,
      dateRange: { startDate: checkIn, endDate: checkOut },
      guestCounts: { numberOfAdults: 2 },
      includePdpMigrationBookItCalendarSheetFragment: true,
      includePdpMigrationBookItFloatingFooterFragment: true,
      includePdpMigrationBookItNavFragment: true,
      includePdpMigrationBookItSidebarFragment: true,
      includePdpMigrationCancellationPolicyPickerModalFragment: true,
      includeOverviewMerchandisingTipsFragment: true
    },
    extensions: { persistedQuery: { version: 1, sha256Hash: "9dfddf66545e678cb5cb06e0ce5a327e5cbd13309254d94d11500c91d9fbcd40" } }
  };
  
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Airbnb-API-Key': 'd306zoyjsyarp7ifhu67rjxn52tv0t20',
      'X-Airbnb-Currency': 'EUR',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    },
    body: JSON.stringify(payload)
  });
  
  if (res.status === 429) {
      throw new Error("429");
  }

  const data = await res.json();
  const bookIt = data?.data?.node?.pdpPresentation?.bookIt;
  
  if (bookIt?.availability?.isAvailable === false) {
    return { available: false, raw: null };
  }
  
  const priceDetails = bookIt?.structuredDisplayPrice?.explanationData?.priceDetails;
  if (!priceDetails) return { available: false, raw: null };
  
  return { available: true, raw: priceDetails };
}

async function runScan() {
  if (process.argv.length < 4) {
    console.log("Usage: node scan_raw.js <startDate> <endDate>");
    process.exit(1);
  }

  const startDateStr = process.argv[2];
  const endDateStr = process.argv[3];

  const startDate = new Date(startDateStr);
  const endDate = new Date(endDateStr);
  const dates = [];
  
  let current = new Date(startDate);
  while (current <= endDate) {
    dates.push(current.toISOString().split('T')[0]);
    current.setDate(current.getDate() + 1);
  }

  if (!fs.existsSync(COMPETITORS_FILE)) {
    console.error(`Errore: File non trovato.`);
    process.exit(1);
  }
  const competitors = fs.readFileSync(COMPETITORS_FILE, 'utf8').split('\n').map(line => line.trim()).filter(line => line.length > 0);

  console.log(`[RAW SCANNER] Trovati ${competitors.length} appartamenti.`);
  console.log(`[RAW SCANNER] Orizzonte: ${dates.length} giorni.`);
  
  let marketData = {};
  if (fs.existsSync(DATA_FILE)) {
    try {
      marketData = JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
      console.log(`[RAW SCANNER] Riprendo dal file esistente.`);
    } catch (e) {
      console.warn(`[RAW SCANNER] File corrotto, creo da zero.`);
    }
  }

  const startExecution = Date.now();

  for (const dateStr of dates) {
    if (!marketData[dateStr]) marketData[dateStr] = {};

    for (const aptId of competitors) {
      if (marketData[dateStr][aptId]) {
        continue;
      }

      console.log(`\n[${dateStr}] Appartamento: ${aptId}`);
      
      let found = false;
      const start = new Date(dateStr);
      
      for (let n = 1; n <= 7; n++) {
          const d = new Date(start);
          d.setDate(d.getDate() + n);
          const checkOutStr = d.toISOString().split('T')[0];
          
          try {
             const result = await fetchPrice(aptId, dateStr, checkOutStr);
             if (result.available) {
                 marketData[dateStr][aptId] = {
                     status: 'OK',
                     minStay: n,
                     checkout: checkOutStr,
                     rawResponse: result.raw
                 };
                 console.log(`--> Trovato! Soggiorno minimo: ${n} notti.`);
                 found = true;
                 break;
             }
          } catch (e) {
             if (e.message === "429") {
                 console.error("!!! ERRORE 429 !!! IP Bloccato. Interrompo.");
                 // Save execution time
                 const executionTime = (Date.now() - startExecution) / 1000;
                 console.log(`Esecuzione interrotta dopo: ${executionTime} secondi`);
                 process.exit(1);
             }
          }
          // small anti-spam delay between minStay tries
          await randomSleep(200, 500);
      }
      
      if (!found) {
         marketData[dateStr][aptId] = { status: 'Non disponibile' };
         console.log(`--> Occupato / Minimum Stay superiore a 7 notti.`);
      }

      fs.writeFileSync(DATA_FILE, JSON.stringify(marketData, null, 2), 'utf8');

      // Human delay between apartments
      const delayMs = Math.floor(Math.random() * (2000 - 1000 + 1)) + 1000;
      console.log(`[Wait] Sleeping for ${(delayMs/1000).toFixed(1)}s to simulate human...`);
      await sleep(delayMs);
    }
  }

  const totalTimeSeconds = (Date.now() - startExecution) / 1000;
  console.log(`\n[RAW SCANNER] Completato in ${totalTimeSeconds.toFixed(1)} secondi.`);
}

runScan();
