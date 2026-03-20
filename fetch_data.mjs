import https from 'https';

const TICKERS = ['AFL', 'A', 'APD'];

async function fetchFromWikipedia(title) {
  const url = `https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exsentences=10&titles=${encodeURIComponent(title)}&explaintext=1&formatversion=2&format=json`;
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          resolve(json.query.pages[0].extract);
        } catch (e) {
          resolve(null);
        }
      });
    }).on('error', reject);
  });
}

async function fetchStockAnalysis(ticker) {
  const url = `https://stockanalysis.com/stocks/${ticker.toLowerCase()}/`;
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' } }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        const out = {};

        // Match metrics
        const revMatch = data.match(/"revenue":([0-9.]+)/);
        if (revMatch) out.revenue = revMatch[1];

        const fcfMatch = data.match(/"freeCashFlow":([0-9.]+)/);
        if (fcfMatch) out.fcf = fcfMatch[1];

        const priceMatch = data.match(/<div class="text-4xl font-bold inline-block">([0-9.]+)<\/div>/);
        if (priceMatch) out.price = parseFloat(priceMatch[1]);
        else {
             const priceMatch2 = data.match(/"price":([0-9.]+)/);
             if (priceMatch2) out.price = parseFloat(priceMatch2[1]);
        }

        resolve(out);
      });
    }).on('error', reject);
  });
}

async function main() {
  for (const t of TICKERS) {
    console.log(`\n--- ${t} ---`);
    const name = t === 'AFL' ? 'Aflac' : (t === 'A' ? 'Agilent Technologies' : 'Air Products');
    const wiki = await fetchFromWikipedia(name);
    console.log("WIKI:", wiki ? wiki.substring(0, 300) + '...' : 'null');

    const sa = await fetchStockAnalysis(t);
    console.log("STOCK ANALYSIS:", sa);
  }
}

main();
