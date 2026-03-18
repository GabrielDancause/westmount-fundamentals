import fs from 'fs';

async function test() {
    const res = await fetch('https://stockanalysis.com/stocks/dis/financials/');
    const html = await res.text();
    const startIdx = html.indexOf('financialData:');
    if (startIdx !== -1) {
        let openBraces = 0;
        let objStr = '';
        let started = false;
        for (let i = startIdx + 14; i < html.length; i++) {
            const char = html[i];
            objStr += char;
            if (char === '{') {
                openBraces++;
                started = true;
            } else if (char === '}') {
                openBraces--;
            }
            if (started && openBraces === 0) {
                break;
            }
        }
        console.log("Extracted object length:", objStr.length);
        try {
            const parsed = eval('(' + objStr + ')');
            console.log("Successfully parsed! keys:", Object.keys(parsed).slice(0, 5));
        } catch (e) {
            console.error("Eval failed", e.message);
        }
    } else {
        console.log("Not found");
    }
}
test();
