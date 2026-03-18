const cheerio = require('cheerio');

async function scrape() {
  const [bsRes] = await Promise.all([
    fetch('https://stockanalysis.com/stocks/usb/financials/balance-sheet/')
  ]);

  const bsText = await bsRes.text();

  const $bs = cheerio.load(bsText);

  // let's try to extract tables
  console.log("BS ROWS:");
  $bs('table tbody tr').each((i, el) => {
    const tds = $bs(el).find('td');
    console.log($bs(tds[0]).text(), $bs(tds[1]).text(), $bs(tds[2]).text());
  });
}

scrape().catch(console.error);
