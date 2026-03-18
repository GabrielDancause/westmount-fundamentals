const cheerio = require('cheerio');

async function scrape() {
  const [finRes, cfRes, bsRes] = await Promise.all([
    fetch('https://stockanalysis.com/stocks/usb/financials/'),
    fetch('https://stockanalysis.com/stocks/usb/financials/cash-flow-statement/'),
    fetch('https://stockanalysis.com/stocks/usb/financials/balance-sheet/')
  ]);

  const finText = await finRes.text();
  const cfText = await cfRes.text();
  const bsText = await bsRes.text();

  const $fin = cheerio.load(finText);
  const $cf = cheerio.load(cfText);
  const $bs = cheerio.load(bsText);

  // let's try to extract tables
  console.log("FINANCIALS HEADERS:");
  $fin('table thead th').each((i, el) => console.log($fin(el).text()));

  console.log("FINANCIALS ROWS:");
  $fin('table tbody tr').each((i, el) => {
    const tds = $fin(el).find('td');
    console.log($fin(tds[0]).text(), $fin(tds[1]).text(), $fin(tds[2]).text());
  });
}

scrape().catch(console.error);
