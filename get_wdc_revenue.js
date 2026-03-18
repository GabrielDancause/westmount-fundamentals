const fs = require('fs');
async function fetchWdcData() {
  try {
    const res = await fetch('https://stockanalysis.com/stocks/wdc/financials/');
    const text = await res.text();
    // try to find the revenue row using simpler regex or index
    const matches = text.match(/<tr[^>]*>[\s\S]*?Revenue[\s\S]*?<\/tr>/g);
    if (matches && matches.length > 0) {
      console.log(matches[0]);
    } else {
      console.log("Revenue row not found via TR");
    }
  } catch(e) {
    console.error(e);
  }
}
fetchWdcData();
