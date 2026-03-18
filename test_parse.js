async function run() {
    const res = await fetch('https://stockanalysis.com/stocks/wdc/financials/');
    const html = await res.text();
    const revRowMatch = html.match(/Revenue<\/a>[\s\S]*?<\/tr>/);
    if(revRowMatch) {
       let str = revRowMatch[0];
       let matches = [...str.matchAll(/<td[^>]*>(.*?)<\/td>/g)].map(m => m[1].replace(/<[^>]+>/g, '').trim());
       console.log(matches);
    }
}
run();
