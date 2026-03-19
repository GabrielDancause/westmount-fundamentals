const cheerio = require('cheerio');

async function fetchHtml(url) {
  const res = await fetch(url, {
    headers: {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
  });
  return res.text();
}

async function scrape() {
  const html = await fetchHtml('https://stockanalysis.com/stocks/dell/');
  const $ = cheerio.load(html);
  const price = $('.text-4xl.font-bold').text();
  console.log("PRICE:", price);
}
scrape();
