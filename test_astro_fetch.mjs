import * as cheerio from 'cheerio';
const res = await fetch('https://stockanalysis.com/stocks/mrsh/financials/');
console.log(res.status);
