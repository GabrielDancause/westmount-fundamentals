const fs = require('fs');

async function fetchWdcData() {
  try {
    const res = await fetch('https://stockanalysis.com/stocks/wdc/financials/');
    const text = await res.text();

    // Extracted TD tags for revenue
    // the row includes TTM in the main block actually
    const revenueRowRegex = /Revenue<\/a>[\s\S]*?<\/tr>/;
    const revMatch = text.match(revenueRowRegex);
    if (!revMatch) return;

    const row = revMatch[0];
    const tds = row.match(/<td[^>]*>[\s\S]*?<\/td>/g);

    if (tds) {
       console.log("Extracted cells:");
       tds.slice(1).forEach(td => console.log(td.replace(/<[^>]*>?/gm, '').trim()));
    }

  } catch(e) {
    console.error(e);
  }
}
fetchWdcData();
