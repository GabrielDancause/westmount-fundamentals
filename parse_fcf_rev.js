async function run() {
    let output = "const WDC_revHistory = [\n";
    const res = await fetch('https://stockanalysis.com/stocks/wdc/financials/');
    const html = await res.text();
    const rows = [...html.matchAll(/<tr[^>]*>[\s\S]*?<\/tr>/g)];
    for (let r of rows) {
        if (r[0].includes('Revenue') && !r[0].includes('Growth') && !r[0].includes('Cost')) {
            let matches = [...r[0].matchAll(/<td[^>]*>(.*?)<\/td>/g)].map(m => m[1].replace(/<[^>]+>/g, '').trim());
            // [ 'Revenue', '10,734', '9,520', '6,317', '6,255', '18,793', '16,922' ]
            // The columns correspond to:
            // TTM (10,734), FY25 (9,520), FY24 (6,317), FY23 (6,255), FY22 (18,793), FY21 (16,922)
            // Note: Wait, WDC fiscal year ends in June.
            // FY25 is missing or incomplete for annual, maybe FY24 was Jun 2024.
            // Let's use the actual labels.
            // 2021: 16922
            // 2022: 18793
            // 2023: 6255
            // 2024: 6317
            // 2025: 9520 (Wait, TTM is 10734)
            console.log(matches);
        }
    }
}
run();
