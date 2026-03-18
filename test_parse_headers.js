async function run() {
    const res = await fetch('https://stockanalysis.com/stocks/wdc/financials/');
    const html = await res.text();
    const theadMatch = html.match(/<thead[\s\S]*?<\/thead>/);
    if(theadMatch) {
       let str = theadMatch[0];
       let matches = [...str.matchAll(/<th[^>]*>(.*?)<\/th>/g)].map(m => m[1].replace(/<[^>]+>/g, '').trim());
       console.log(matches);
    }
}
run();
