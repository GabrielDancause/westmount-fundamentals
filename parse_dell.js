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

parseTable('fin.html', /Revenue/i);
parseTable('fin.html', /EPS \(Diluted\)/i);
parseTable('fin.html', /Shares Outstanding/i);
parseTable('cf.html', /Free Cash Flow/i);
parseTable('bs.html', /Cash & Equivalents/i);
parseTable('bs.html', /Total Debt/i);
