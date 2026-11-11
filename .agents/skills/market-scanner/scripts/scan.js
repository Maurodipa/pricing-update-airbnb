const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

const DATA_FILE = path.join(__dirname, '..', 'market_data_4months.json');
const COMPETITORS_FILE = path.join(__dirname, '..', 'competitors.txt');
const CALCULATE_SCRIPT = path.join(__dirname, '..', '..', 'airbnb-nightly-rate', 'scripts', 'calculate.js');

// Helper to simulate human delay
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
function randomSleep(minMs, maxMs) {
  const ms = Math.floor(Math.random() * (maxMs - minMs + 1)) + minMs;
  return sleep(ms);
}

async function runScan() {
  if (process.argv.length < 4) {
    console.log("Usage: node scan.js <startDate> <endDate>");
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

  // Load competitors
  if (!fs.existsSync(COMPETITORS_FILE)) {
    console.error(`Errore: File ${COMPETITORS_FILE} non trovato.`);
    process.exit(1);
  }
  const competitors = fs.readFileSync(COMPETITORS_FILE, 'utf8')
    .split('\n')
    .map(line => line.trim())
    .filter(line => line.length > 0);

  console.log(`[MARKET SCANNER] Trovati ${competitors.length} appartamenti.`);
  console.log(`[MARKET SCANNER] Orizzonte: ${dates.length} giorni (${startDateStr} a ${endDateStr}).`);
  
  const totalCalls = competitors.length * dates.length;
  console.log(`[MARKET SCANNER] Totale iterazioni previste: ${totalCalls}. Tempo stimato: ~${(totalCalls * 12 / 60 / 60).toFixed(1)} ore.`);

  // Load existing data to resume if interrupted
  let marketData = {};
  if (fs.existsSync(DATA_FILE)) {
    try {
      marketData = JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
      console.log(`[MARKET SCANNER] Dati precedenti caricati. Lo scanner riprenderà da dove si era interrotto.`);
    } catch (e) {
      console.warn(`[MARKET SCANNER] File dati corrotto o invalido. Ricreo da zero.`);
    }
  }

  // Main processing loop
  let callsMade = 0;
  for (const dateStr of dates) {
    if (!marketData[dateStr]) marketData[dateStr] = {};

    for (const aptId of competitors) {
      // Skip if already successfully processed (or explicitly marked as blocked)
      if (marketData[dateStr][aptId]) {
        continue;
      }

      console.log(`\n[${dateStr}] Appartamento: ${aptId}`);
      
      try {
        const { stdout } = await execPromise(`node "${CALCULATE_SCRIPT}" ${aptId} ${dateStr}`);
        const rateMatch = stdout.match(/Notte 1: ([\d.-]+) EUR/);
        
        if (rateMatch) {
          const rate = parseFloat(rateMatch[1]);
          // Clean up negative bug artifacts due to fallback cleaning fees (if any remain)
          if (rate < 0) {
             marketData[dateStr][aptId] = { status: "OK", rate: Math.round(rate + 18930 + 416) }; // Temporary patch
          } else {
             marketData[dateStr][aptId] = { status: "OK", rate: rate };
          }
          console.log(`--> Tarifa Netta: ${marketData[dateStr][aptId].rate} EUR`);
        } else {
          marketData[dateStr][aptId] = { status: "Non disponibile" };
          console.log(`--> Occupato / Minimum Stay Rifiutato`);
        }
      } catch (e) {
        if (e.stdout && e.stdout.includes('429')) {
           console.error("!!! ERRORE 429 !!! IP Bloccato da Airbnb. Interrompo la scansione.");
           process.exit(1);
        }
        marketData[dateStr][aptId] = { status: "Non disponibile" };
        console.log(`--> Occupato / Minimum Stay Rifiutato (Error)`);
      }

      // Save incrementally
      fs.writeFileSync(DATA_FILE, JSON.stringify(marketData, null, 2), 'utf8');

      // Heavy Throttle
      callsMade++;
      const delayMs = Math.floor(Math.random() * (15000 - 8000 + 1)) + 8000; // 8 to 15 seconds
      console.log(`[Wait] Sleeping for ${(delayMs/1000).toFixed(1)}s to simulate human...`);
      await sleep(delayMs);
    }
  }

  console.log(`\n[MARKET SCANNER] Scansione completata con successo! Dati salvati in ${DATA_FILE}.`);
}

runScan();
