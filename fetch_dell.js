const cheerio = require('cheerio');

async function fetchHtml(url) {
  const res = await fetch(url, {
    headers: {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
  });
  return res.text();
}

async function scrape() {
  const finHtml = await fetchHtml('https://stockanalysis.com/stocks/dell/financials/');
  const bsHtml = await fetchHtml('https://stockanalysis.com/stocks/dell/financials/balance-sheet/');
  const cfHtml = await fetchHtml('https://stockanalysis.com/stocks/dell/financials/cash-flow-statement/');

  // We could just print the HTML or use cheerio to extract tables
  // Let's just output the HTML to files to grep them, or parse them directly
  const fs = require('fs');
  fs.writeFileSync('fin.html', finHtml);
  fs.writeFileSync('bs.html', bsHtml);
  fs.writeFileSync('cf.html', cfHtml);
  console.log('Saved html files');
}

scrape();
