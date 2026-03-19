const cheerio = require('cheerio');

async function scrape() {
  const [cfRes] = await Promise.all([
    fetch('https://stockanalysis.com/stocks/usb/financials/cash-flow-statement/')
  ]);

  const cfText = await cfRes.text();

  const $cf = cheerio.load(cfText);

  // let's try to extract tables
  console.log("CF ROWS:");
  $cf('table tbody tr').each((i, el) => {
    const tds = $cf(el).find('td');
    console.log($cf(tds[0]).text(), $cf(tds[1]).text(), $cf(tds[2]).text());
  });
}

scrape().catch(console.error);
