import * as cheerio from 'cheerio';
const res = await fetch('https://stockanalysis.com/stocks/mrsh/financials/');
const html = await res.text();
const $ = cheerio.load(html);
const rows = $('table tbody tr');
rows.each((i, row) => {
  const title = $(row).find('td').first().text().trim();
  if (title.includes('Revenue') || title.includes('Free Cash Flow') || title.includes('Shares')) {
    const vals = [];
    $(row).find('td').each((j, col) => {
      if (j > 0) vals.push($(col).text().trim());
    });
    console.log(title, vals.slice(0, 5));
  }
});
