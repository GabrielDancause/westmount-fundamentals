const fs = require('fs');
const cheerio = require('cheerio');

const parseTable = (file, titlePattern) => {
    const html = fs.readFileSync(file, 'utf-8');
    const $ = cheerio.load(html);

    // Find rows
    $('tr').each((i, row) => {
        const text = $(row).text().replace(/\s+/g, ' ').trim();
        if (text.match(titlePattern)) {
            console.log(file, '->', text);
        }
    });
};

parseTable('cf.html', /Operating Cash Flow/i);
parseTable('cf.html', /Capital Expenditures/i);
parseTable('cf.html', /Net Income/i);
