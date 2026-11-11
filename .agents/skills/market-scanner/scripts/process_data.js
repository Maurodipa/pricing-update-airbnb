const fs = require('fs');
const path = require('path');

const RAW_FILE = path.join(__dirname, '..', 'banca_dati_airbnb.json');
const OUT_FILE = path.join(__dirname, '..', 'market_data_1month.json');

const cleaningFees = {
  '1589943047991118285': 50, // Mauro
  '602489771443051475': 50,  // Stefania
  '1280484040857767756': 0,   // Ugo
  '1243259212458138393': 50,  // Navona
  '2153298': 50,              // Elegante
  '1105673287932582735': 50,  // Perla
  '14159837': 120,            // Barbara
  '14290915': 73,             // Blue Navona
  '4050526': 60               // Junior Suite
};

const feeMultiplier = 1.1637;

function processData() {
  if (!fs.existsSync(RAW_FILE)) {
    console.error("No banca_dati_airbnb.json found!");
    process.exit(1);
  }

  const rawData = JSON.parse(fs.readFileSync(RAW_FILE, 'utf8'));
  const processed = {};

  for (const date of Object.keys(rawData)) {
    processed[date] = {};
    for (const apt of Object.keys(rawData[date])) {
      const entry = rawData[date][apt];
      
      if (!entry || entry.status !== 'OK' || !entry.rawResponse) {
         processed[date][apt] = { status: 'Non disponibile' };
         continue;
      }
      
      let totalGross = 0;
      let taxes = 0;
      let hasSpecialOffer = false;
      
      for (const group of entry.rawResponse) {
        if (group.items) {
          for (const item of group.items) {
            if (item.__typename === 'DiscountedExplanationLineItem') {
                hasSpecialOffer = true;
            }
            if (item.description === 'Taxes' || item.description === 'Tasse') {
               const match = item.priceString.match(/[\d.,]+/);
               if (match) {
                   // if it has a period and comma, handle it. Usually it's US format: 630.81 or 1,230.81
                   const s = match[0].replace(/,/g, ''); // remove all commas
                   taxes = parseFloat(s);
               }
            }
            if ((item.__typename === 'HighlightExplanationLineItem' && (item.description === 'Total' || item.description === 'Totale')) || item.description === 'Total') {
               const match = item.priceString.match(/[\d.,]+/);
               if (match) {
                   const s = match[0].replace(/,/g, ''); // remove all commas
                   totalGross = parseFloat(s);
               }
            }
          }
        }
      }
      
      const cleaningFee = cleaningFees[apt] || 50;
      const minStay = entry.minStay || 1;
      
      const totalNetWithCleaning = (totalGross - taxes) / feeMultiplier;
      const pureTotal = totalNetWithCleaning - cleaningFee;
      const pureNightly = pureTotal / minStay;
      
      processed[date][apt] = {
         status: 'OK',
         rate: Math.round(pureNightly),
         minStay: minStay,
         specialOffer: hasSpecialOffer
      };
    }
  }

  fs.writeFileSync(OUT_FILE, JSON.stringify(processed, null, 2), 'utf8');
  console.log(`[PROCESSOR] Data elaborati e salvati in ${OUT_FILE}`);
}

processData();
