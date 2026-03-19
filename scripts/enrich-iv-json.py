#!/usr/bin/env python3
"""
Enrich existing IV JSON files with text content from old rendered HTML.
Only adds missing fields — never overwrites existing data.
"""
import os, re, json, glob
from html.parser import HTMLParser

DIST_DIR = "dist"
DATA_DIR = "src/data/iv"

class TextExtractor(HTMLParser):
    """Simple HTML to text converter"""
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = False
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip = True
    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip = False
    def handle_data(self, data):
        if not self.skip:
            self.text.append(data)
    def get_text(self):
        return ' '.join(self.text)

def html_to_text(html):
    e = TextExtractor()
    e.feed(html)
    return e.get_text().strip()

def extract_text_content(html):
    """Extract thesis, risks, FAQ from rendered HTML using multiple strategies"""
    result = {}
    
    # === THESIS ===
    # Strategy 1: Look for "AI Thesis" or "Investment Thesis" section headers
    thesis_patterns = [
        r'<h2[^>]*>((?:The )?(?:AI |Investment |My )?Thesis[^<]*)</h2>(.*?)(?=<(?:h2|section)[^>]*>)',
        r'<h2[^>]*>(The AI Thesis[^<]*)</h2>(.*?)(?=<(?:h2|section))',
    ]
    for pat in thesis_patterns:
        m = re.search(pat, html, re.DOTALL | re.IGNORECASE)
        if m:
            result['thesisTitle'] = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            paras = re.findall(r'<p[^>]*>(.*?)</p>', m.group(2), re.DOTALL)
            paras = [p.strip() for p in paras if len(p.strip()) > 30]
            if paras:
                result['thesisParagraphs'] = paras
            break
    
    # === RISKS ===
    # Find risk section - various headers
    risk_headers = [
        r'Key Risks',
        r'Structural Risks',
        r'Risk Factors',
        r'Risks to (?:This )?Valuation',
        r'Key Risks to (?:This )?Valuation',
        r'Key Risks to Consider',
    ]
    for header in risk_headers:
        risk_match = re.search(
            rf'<h2[^>]*>[^<]*{header}[^<]*</h2>(.*?)(?=<(?:h2|section|footer|div[^>]*class="[^"]*(?:faq|disclaimer|newsletter)))',
            html, re.DOTALL | re.IGNORECASE
        )
        if risk_match:
            section = risk_match.group(1)
            
            # Extract intro paragraph
            intro_match = re.search(r'^[^<]*<p[^>]*>(.*?)</p>', section, re.DOTALL)
            intro = intro_match.group(1).strip() if intro_match else ""
            
            # Try h3 + p pattern
            items = re.findall(r'<h3[^>]*>(.*?)</h3>\s*<p[^>]*>(.*?)</p>', section, re.DOTALL)
            
            # Try li pattern if h3 didn't work
            if not items:
                lis = re.findall(r'<li[^>]*>(.*?)</li>', section, re.DOTALL)
                for li in lis:
                    strong = re.search(r'<strong[^>]*>(.*?)</strong>', li)
                    if strong:
                        title = re.sub(r'<[^>]+>', '', strong.group(1)).strip().rstrip(':')
                        desc = re.sub(r'<strong[^>]*>.*?</strong>', '', li)
                        desc = re.sub(r'<[^>]+>', '', desc).strip()
                        items.append((title, desc))
            
            if items:
                risk_items = []
                for title, desc in items:
                    t = re.sub(r'<[^>]+>', '', title).strip()
                    if t:
                        risk_items.append({
                            "title": t,
                            "description": desc.strip()
                        })
                if risk_items:
                    result['risks'] = {
                        "introText": re.sub(r'<[^>]+>', '', intro).strip() if intro else "",
                        "items": risk_items
                    }
            break
    
    # === FAQ ===
    faq_match = re.search(
        r'<(?:h2|section)[^>]*>[^<]*(?:Frequently Asked|FAQ)[^<]*</(?:h2|section)>(.*?)(?=<(?:section|div)[^>]*class="[^"]*disclaimer|<footer)',
        html, re.DOTALL | re.IGNORECASE
    )
    if not faq_match:
        # Try finding by class
        faq_match = re.search(
            r'class="[^"]*faq[^"]*"[^>]*>(.*?)(?=<(?:section|div)[^>]*class="[^"]*disclaimer|<footer)',
            html, re.DOTALL | re.IGNORECASE
        )
    
    if faq_match:
        section = faq_match.group(1)
        
        # h3 + p pattern
        faq_items = re.findall(r'<h3[^>]*>(.*?)</h3>\s*<p[^>]*>(.*?)</p>', section, re.DOTALL)
        
        # details/summary pattern
        if not faq_items:
            faq_items = re.findall(r'<summary[^>]*>(.*?)</summary>.*?<p[^>]*>(.*?)</p>', section, re.DOTALL)
        
        faq = []
        for q, a in faq_items:
            q_clean = re.sub(r'<[^>]+>', '', q).strip()
            if '?' in q_clean and len(a.strip()) > 20:
                faq.append({"question": q_clean, "answer": a.strip()})
        
        if faq:
            result['faq'] = faq
    
    # === ASSUMPTION RATIONALES (if empty) ===
    # Try to extract from various card/section patterns
    rationales = {}
    
    for key, patterns in {
        'fcfGrowth': [
            r'(?:FCF Growth|Growth Rate).*?(?:Rationale|rationale)[:\s]*</?\w+[^>]*>\s*(.*?)</(?:p|div)',
            r'(?:FCF Growth|Growth Rate \(Y|Growth Rate \(Years).*?<p[^>]*>(.*?)</p>',
            r'(?:FCF Growth|Growth Rate).*?assumption-card[^>]*>.*?<p[^>]*>(.*?)</p>',
        ],
        'discountRate': [
            r'(?:Discount Rate|WACC|Cost of (?:Capital|Equity)).*?(?:Rationale|rationale)[:\s]*</?\w+[^>]*>\s*(.*?)</(?:p|div)',
            r'(?:Discount Rate|WACC).*?<p[^>]*>(.*?)</p>',
        ],
        'terminalGrowth': [
            r'(?:Terminal Growth).*?(?:Rationale|rationale)[:\s]*</?\w+[^>]*>\s*(.*?)</(?:p|div)',
            r'(?:Terminal Growth).*?<p[^>]*>(.*?)</p>',
        ],
    }.items():
        for pat in patterns:
            m = re.search(pat, html, re.DOTALL | re.IGNORECASE)
            if m:
                text = m.group(1).strip()
                # Clean up
                text = re.sub(r'<strong[^>]*>Rationale:</strong>\s*', '', text)
                text = re.sub(r'<[^>]+>', '', text).strip()
                if len(text) > 30:
                    rationales[key] = text
                    break
    
    if rationales:
        result['rationales'] = rationales
    
    return result

def main():
    json_files = sorted(glob.glob(f"{DATA_DIR}/*.json"))
    print(f"Processing {len(json_files)} JSON files")
    
    updated = 0
    
    for jpath in json_files:
        with open(jpath) as f:
            data = json.load(f)
        
        slug = data.get('slug', '')
        html_path = os.path.join(DIST_DIR, slug, "index.html")
        
        if not os.path.exists(html_path):
            continue
        
        with open(html_path) as f:
            html = f.read()
        
        extracted = extract_text_content(html)
        changed = False
        
        # Only add missing fields
        if not data.get('thesisParagraphs') and extracted.get('thesisParagraphs'):
            data['thesisTitle'] = extracted['thesisTitle']
            data['thesisParagraphs'] = extracted['thesisParagraphs']
            changed = True
        
        if not data.get('risks', {}).get('items') and extracted.get('risks', {}).get('items'):
            data['risks'] = extracted['risks']
            changed = True
        
        if not data.get('faq') and extracted.get('faq'):
            data['faq'] = extracted['faq']
            changed = True
        
        # Fill empty rationales
        if extracted.get('rationales'):
            assumptions = data.get('assumptions', {})
            for key, text in extracted['rationales'].items():
                if key in assumptions and not assumptions[key].get('rationale'):
                    assumptions[key]['rationale'] = text
                    changed = True
            data['assumptions'] = assumptions
        
        if changed:
            with open(jpath, 'w') as f:
                json.dump(data, f, indent=2)
            updated += 1
    
    print(f"Updated {updated}/{len(json_files)} files")
    
    # Recount
    stats = {'thesis': 0, 'risks': 0, 'faq': 0, 'rationale': 0}
    for f in glob.glob(f"{DATA_DIR}/*.json"):
        with open(f) as fh:
            d = json.load(fh)
        if d.get('thesisParagraphs'): stats['thesis'] += 1
        if d.get('risks', {}).get('items'): stats['risks'] += 1
        if d.get('faq'): stats['faq'] += 1
        if any(d.get('assumptions', {}).get(k, {}).get('rationale') for k in ['fcfGrowth', 'discountRate', 'terminalGrowth']):
            stats['rationale'] += 1
    
    print(f"\nAfter enrichment:")
    for k,v in stats.items():
        print(f"  {k}: {v}/168")

if __name__ == "__main__":
    main()
