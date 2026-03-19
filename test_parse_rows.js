async function run() {
    const res = await fetch('https://stockanalysis.com/stocks/wdc/financials/');
    const html = await res.text();
    const rows = [...html.matchAll(/<tr[^>]*>[\s\S]*?<\/tr>/g)];
    for (let r of rows) {
        if (r[0].includes('Revenue')) {
            let matches = [...r[0].matchAll(/<td[^>]*>(.*?)<\/td>/g)].map(m => m[1].replace(/<[^>]+>/g, '').trim());
            console.log("ROW:", matches);
        }
    }
}
run();
