const fs = require('fs');
const { spawn } = require('child_process');

process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

if (process.argv.length < 4) {
  console.log("Usage: node calculate.js <listingId> <startDate> [fallbackCleaningFee]");
  process.exit(1);
}

const listingId = process.argv[2];
const startDateStr = process.argv[3];
const fallbackCleaningFee = process.argv.length > 4 ? parseFloat(process.argv[4]) : 50;
const guests = 2; // Updated to 2 guests per user request

async function getCleaningFeeFromMCP() {
  return new Promise((resolve) => {
    const mcpServerPath = "C:\\Users\\mauro\\AppData\\Roaming\\npm\\node_modules\\@openbnb\\mcp-server-airbnb\\dist\\index.js";
    const child = spawn('node', [mcpServerPath], {
      env: { ...process.env, NODE_TLS_REJECT_UNAUTHORIZED: "0" }
    });

    const request = {
      jsonrpc: "2.0",
      id: 1,
      method: "tools/call",
      params: {
        name: "airbnb_listing_details",
        arguments: { id: listingId, ignoreRobotsText: true }
      }
    };

    const initRequest = {
      jsonrpc: "2.0", id: 0, method: "initialize",
      params: { protocolVersion: "2024-11-05", capabilities: {}, clientInfo: { name: "test", version: "1.0.0" } }
    };

    let output = "";
    child.stdout.on('data', (data) => { output += data.toString(); });
    
    child.stdin.write(JSON.stringify(initRequest) + '\n');
    setTimeout(() => { child.stdin.write(JSON.stringify(request) + '\n'); }, 500);
    setTimeout(() => { 
      child.kill(); 
      // Parse output to find cleaning fee
      const match = output.match(/pulizi[a-z]*.*?(\d+)/i) || output.match(/cleaning.*?(\d+)/i);
      if (match && match[1]) {
        resolve(parseFloat(match[1]));
      } else {
        console.log("MCP non contiene informazioni sulle pulizie, uso il fallback algebrico/manuale.");
        resolve(null);
      }
    }, 5000);
  });
}

async function fetchPrice(checkIn, checkOut) {
  const url = "https://www.airbnb.com/api/v3/StaysPdpBookItQuery";
  const b64Id = Buffer.from(`DemandStayListing:${listingId}`).toString('base64');
  
  const payload = {
    operationName: "StaysPdpBookItQuery",
    variables: {
      id: b64Id,
      dateRange: { startDate: checkIn, endDate: checkOut },
      guestCounts: { numberOfAdults: guests },
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
  
  const data = await res.json();
  const bookIt = data?.data?.node?.pdpPresentation?.bookIt;
  if (bookIt?.availability?.isAvailable === false) {
    throw new Error(`Dates ${checkIn} to ${checkOut} are not available.`);
  }
  
  const priceDetails = bookIt?.structuredDisplayPrice?.explanationData?.priceDetails;
  if (!priceDetails) return { nightsTotal: 0, taxes: 0 };
  
  let totalGross = 0;
  let taxes = 0;
  
  for (const group of priceDetails) {
    if (group.items) {
      for (const item of group.items) {
        if (item.description === 'Taxes' || item.description === 'Tasse') {
           taxes = parseFloat(item.priceString.replace('€', '').replace(',', '').trim());
        }
        if ((item.__typename === 'HighlightExplanationLineItem' && (item.description === 'Total' || item.description === 'Totale')) || item.description === 'Total') {
           totalGross = parseFloat(item.priceString.replace('€', '').replace(',', '').trim());
        }
      }
    }
  }
  
  const nightsTotal = totalGross - taxes;
  return { nightsTotal, taxes };
}

async function run() {
  console.log("Cerco il costo delle pulizie dal server MCP...");
  let cleaningFee = await getCleaningFeeFromMCP();
  if (cleaningFee === null) {
    cleaningFee = fallbackCleaningFee;
  }
  console.log(`Costo pulizie utilizzato: ${cleaningFee} EUR\n`);

  const start = new Date(startDateStr);
  const feeMultiplier = 1.1637; // Standard guest fee estimate 16.37%
  
  try {
    let minStay = null;
    let baseCost = null;
    let baseTaxes = null;
    
    // 1. Cerca il Minimum Stay da 1 a 7 notti
    for (let n = 1; n <= 7; n++) {
      const d = new Date(start);
      d.setDate(d.getDate() + n);
      const checkOutStr = d.toISOString().split('T')[0];
      
      try {
        const t = await fetchPrice(startDateStr, checkOutStr);
        if (t && t.nightsTotal > 0) {
          minStay = n;
          baseCost = t.nightsTotal;
          baseTaxes = t.taxes;
          break;
        }
      } catch (e) {
        // Rifiutato (probabilmente per minimum stay), proviamo n+1
      }
    }
    
    if (!minStay) {
      throw new Error(`Il giorno ${startDateStr} non è disponibile o richiede un soggiorno minimo superiore a 7 notti.`);
    }
    
    let rates = [];
    // Calcoliamo la media per il blocco base
    const baseNet = (baseCost / feeMultiplier) - cleaningFee;
    const avgBaseRate = baseNet / minStay;
    for (let i = 0; i < minStay; i++) {
      rates.push(avgBaseRate);
    }
    
    let lastCost = baseCost;
    
    // Proviamo a estrarre i margini per le due notti successive al minimum stay (se disponibili)
    const nMarginal1 = minStay + 1;
    const nMarginal2 = minStay + 2;
    
    let d1 = new Date(start); d1.setDate(d1.getDate() + nMarginal1);
    let d2 = new Date(start); d2.setDate(d2.getDate() + nMarginal2);
    
    try {
      const t1 = await fetchPrice(startDateStr, d1.toISOString().split('T')[0]);
      if (t1) {
         const margNet = (t1.nightsTotal / feeMultiplier) - (lastCost / feeMultiplier);
         rates.push(margNet);
         lastCost = t1.nightsTotal;
         
         try {
           const t2 = await fetchPrice(startDateStr, d2.toISOString().split('T')[0]);
           if (t2) {
             const margNet2 = (t2.nightsTotal / feeMultiplier) - (lastCost / feeMultiplier);
             rates.push(margNet2);
           }
         } catch(e) {}
      }
    } catch(e) {}

    const minRate = Math.min(...rates);
    const maxRate = Math.max(...rates);
    const avgRate = rates.reduce((a, b) => a + b, 0) / rates.length;
    
    const end = new Date(start); end.setDate(end.getDate() + rates.length);
    const period = `${startDateStr} - ${end.toISOString().split('T')[0]}`;
    
    console.log(`--- RISULTATI (per 2 ospiti) ---`);
    console.log(`Periodo analizzato: ${period} (${rates.length} notti totali)`);
    console.log(`Minimum Stay Rilevato: ${minStay} notti`);
    console.log(`Metodo utilizzato: Stima dinamica con supporto Soggiorno Minimo (Fee ~16.37%)`);
    console.log(`Costo per notte (Media su ${rates.length} notti): ${avgRate.toFixed(2)} EUR`);
    console.log(`Tariffa Minima: ${minRate.toFixed(2)} EUR`);
    console.log(`Tariffa Massima: ${maxRate.toFixed(2)} EUR`);
    console.log(`Dettaglio per notte: ` + rates.map((r, i) => `Notte ${i+1}: ${r.toFixed(2)} EUR`).join(', '));
    console.log(`Costo delle pulizie: ${cleaningFee.toFixed(2)} EUR`);
    console.log(`Tasse di soggiorno stimate (media 1 notte): ${(baseTaxes / minStay).toFixed(2)} EUR`);
    
  } catch (e) {
    console.log(`Errore: ${e.message}`);
  }
}

run();
