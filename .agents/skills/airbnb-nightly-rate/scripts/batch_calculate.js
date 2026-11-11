const { exec } = require('child_process');
const util = require('util');
const path = require('path');
const execPromise = util.promisify(exec);

// Simulate human behavior: random sleep between min and max milliseconds
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
function randomSleep(minMs, maxMs) {
  const ms = Math.floor(Math.random() * (maxMs - minMs + 1)) + minMs;
  return sleep(ms);
}

async function runBatch() {
  if (process.argv.length < 5) {
    console.log("Usage: node batch_calculate.js <listingId> <startDate> <endDate>");
    process.exit(1);
  }

  const listingId = process.argv[2];
  const startDateStr = process.argv[3];
  const endDateStr = process.argv[4];

  const startDate = new Date(startDateStr);
  const endDate = new Date(endDateStr);
  const dates = [];
  
  let current = new Date(startDate);
  while (current <= endDate) {
    dates.push(current.toISOString().split('T')[0]);
    current.setDate(current.getDate() + 1);
  }

  console.log(`[ANTI-BOT ENABLED] Starting polite batch processing for ${dates.length} days...`);
  console.log(`Listing ID: ${listingId}`);
  console.log(`Period: ${startDateStr} to ${endDateStr}`);
  console.log(`Using sequential execution with 2-5 seconds random delays.\n`);

  const results = {};
  const calculateScriptPath = path.join(__dirname, 'calculate.js');
  const startTimestamp = Date.now();

  for (let i = 0; i < dates.length; i++) {
    const d = dates[i];
    process.stdout.write(`Analyzing ${d} (${i + 1}/${dates.length})... `);
    
    try {
      const { stdout } = await execPromise(`node "${calculateScriptPath}" ${listingId} ${d}`);
      const rateMatch = stdout.match(/Notte 1: ([\d.-]+) EUR/);
      if (rateMatch) {
         results[d] = `${rateMatch[1]} EUR`;
         console.log(`OK: ${rateMatch[1]} EUR`);
      } else {
         results[d] = `Non disponibile`;
         console.log(`BLOCKED/BOOKED`);
      }
    } catch (e) {
      results[d] = `Non disponibile`;
      console.log(`BLOCKED/BOOKED`);
    }

    // Don't sleep after the very last request
    if (i < dates.length - 1) {
      const delayMs = Math.floor(Math.random() * (5000 - 2000 + 1)) + 2000; // 2s to 5s
      await sleep(delayMs);
    }
  }

  // Aggregate results into blocks
  let currentRate = null;
  let blockStart = null;
  let blockEnd = null;
  const blocks = [];

  for (let i = 0; i < dates.length; i++) {
    const d = dates[i];
    const r = results[d];
    
    if (r !== currentRate) {
      if (currentRate !== null) {
        blocks.push({ start: blockStart, end: blockEnd, rate: currentRate });
      }
      currentRate = r;
      blockStart = d;
      blockEnd = d;
    } else {
      blockEnd = d;
    }
  }
  if (currentRate !== null) {
    blocks.push({ start: blockStart, end: blockEnd, rate: currentRate });
  }

  console.log(`\n--- TARIFFE DAL ${startDateStr} AL ${endDateStr} ---`);
  for (const b of blocks) {
    if (b.start === b.end) {
      console.log(`${b.start}: ${b.rate}`);
    } else {
      console.log(`Dal ${b.start} al ${b.end}: ${b.rate}`);
    }
  }

  const endTimestamp = Date.now();
  console.log(`\nScript execution time: ${((endTimestamp - startTimestamp) / 1000).toFixed(2)} seconds`);
}

runBatch();
