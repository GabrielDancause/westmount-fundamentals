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

parseTable('fin.html', /Operating Margin/i);
parseTable('fin.html', /Profit Margin/i);
parseTable('fin.html', /Free Cash Flow Margin/i);
parseTable('cf.html', /Free Cash Flow Margin/i);
parseTable('bs.html', /Cash & Short-Term Investments/i);
