#!/usr/bin/env python3
"""
Extract IV data from BUILT HTML files (dist/) instead of source .astro files.
The built HTML has all computed values rendered as text — much more reliable.
"""

import os
import re
import json
import glob
from html.parser import HTMLParser

DIST_DIR = "dist"
OUTPUT_DIR = "src/data/iv"
PAGES_DIR = "src/pages"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def clean_text(text):
    """Remove HTML tags and clean whitespace"""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_number(text):
    """Extract a number from text like '$142.23' or '8.5%' or '123,324'"""
    if not text:
        return None
    text = text.replace(',', '').replace('$', '').strip()
    m = re.search(r'(-?[\d.]+)', text)
    if m:
        return float(m.group(1))
    return None

def process_html(filepath, slug):
    """Extract data from a built HTML file"""
    with open(filepath, 'r') as f:
        html = f.read()
    
    data = {"slug": slug}
    
    # Title - from <h1>
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    if m:
        title = clean_text(m.group(1))
        data['title'] = title
        # Extract ticker
        tm = re.search(r'\(([A-Z]{1,5})\)', title)
        if tm:
            data['ticker'] = tm.group(1)
            data['companyName'] = title.split('(')[0].strip().rstrip(' –—-')
    
    # Meta description
    m = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', html)
    if m:
        data['description'] = m.group(1)
    
    # Fair Value / Intrinsic Value - the big number
    # Look for the verdict/value card
    iv_patterns = [
        r'(?:Fair Value|Intrinsic Value).*?(?:Estimate|Per Share).*?<[^>]*class="[^"]*value[^"]*"[^>]*>\s*\$?([\d,.]+)',
        r'class="[^"]*value[^"]*"[^>]*>\s*\$?([\d,.]+).*?per share',
        r'<span[^>]*class="[^"]*value[^"]*"[^>]*>\s*\$?([\d,.]+)',
        r'Fair Value.*?\$\s*([\d,.]+)\s*(?:per share)?',
        r'intrinsic.*?value.*?\$\s*([\d,.]+)',
    ]
    for pat in iv_patterns:
        m = re.search(pat, html, re.DOTALL | re.IGNORECASE)
        if m:
            data['computedIV'] = extract_number(m.group(1))
            break
    
    # Current Price
    price_patterns = [
        r'Current Price.*?\$\s*([\d,.]+)',
        r'current.*?price.*?\$\s*([\d,.]+)',
        r'Market Price.*?\$\s*([\d,.]+)',
    ]
    for pat in price_patterns:
        m = re.search(pat, html, re.DOTALL | re.IGNORECASE)
        if m:
            data['currentPrice'] = extract_number(m.group(1))
            break
    
    # Margin of Safety
    m = re.search(r'Margin of Safety.*?(-?[\d.]+)%', html, re.DOTALL | re.IGNORECASE)
    if m:
        data['marginOfSafety'] = float(m.group(1))
    
    # Verdict
    m = re.search(r'Verdict.*?(OVERVALUED|UNDERVALUED|FAIRLY VALUED)', html, re.DOTALL | re.IGNORECASE)
    if m:
        data['verdict'] = m.group(1).upper()
    
    # Assumptions - FCF Growth, WACC, Terminal Growth
    # These are typically in assumption cards with rate values
    # Try multiple patterns for growth rate extraction
    fcf_patterns = [
        r'FCF Growth Rate.*?(\d+\.?\d*)%',
        r'FCF Growth.*?(\d+\.?\d*)%',
        r'Growth Rate.*?Y1.*?(\d+\.?\d*)%',
        r'Growth Rate \(Years? 1.*?(\d+\.?\d*)%',
        r'Growth Rate \(Y1.*?(\d+\.?\d*)%',
        r'growth.*?rate.*?<[^>]*>(\d+\.?\d*)%',
        r'assumption-val[^>]*>(\d+\.?\d*)%.*?FCF Growth',
        r'FCF Growth.*?assumption-val[^>]*>(\d+\.?\d*)%',
        r'grow at.*?(\d+\.?\d*)%.*?per year',
        r'grow at.*?<strong[^>]*>(\d+\.?\d*)%',
        r'Growth Rate.*?<[^>]*class="[^"]*(?:value|metric|assumption)[^"]*"[^>]*>\s*(\d+\.?\d*)%',
        r'growth rate of.*?(\d+\.?\d*)%',
    ]
    for pat in fcf_patterns:
        m = re.search(pat, html, re.DOTALL | re.IGNORECASE)
        if m:
            data['fcfGrowthRate'] = float(m.group(1)) / 100
            break
    
    wacc_patterns = [
        r'(?:Discount Rate|WACC|Cost of (?:Capital|Equity)).*?(\d+\.?\d*)%',
        r'discount rate.*?<[^>]*>(\d+\.?\d*)%',
        r'discount.*?(\d+\.?\d*)%.*?rate',
        r'WACC.*?<[^>]*class="[^"]*(?:value|metric|assumption)[^"]*"[^>]*>\s*(\d+\.?\d*)%',
    ]
    for pat in wacc_patterns:
        m = re.search(pat, html, re.DOTALL | re.IGNORECASE)
        if m:
            data['discountRate'] = float(m.group(1)) / 100
            break
    
    terminal_patterns = [
        r'Terminal Growth.*?(\d+\.?\d*)%',
        r'terminal.*?rate.*?(\d+\.?\d*)%',
        r'terminal.*?<[^>]*>(\d+\.?\d*)%',
        r'Terminal Growth.*?<[^>]*class="[^"]*(?:value|metric|assumption)[^"]*"[^>]*>\s*(\d+\.?\d*)%',
        r'growth stabilizes at.*?(\d+\.?\d*)%',
        r'perpetual.*?growth.*?(\d+\.?\d*)%',
    ]
    for pat in terminal_patterns:
        m = re.search(pat, html, re.DOTALL | re.IGNORECASE)
        if m:
            data['terminalGrowthRate'] = float(m.group(1)) / 100
            break
    
    # Assumption rationales
    assumptions = {}
    for key, label, search in [
        ('fcfGrowth', 'FCF Growth Rate (Y1-Y5)', r'FCF Growth'),
        ('discountRate', 'Discount Rate (WACC)', r'(?:Discount Rate|WACC)'),
        ('terminalGrowth', 'Terminal Growth Rate', r'Terminal Growth'),
    ]:
        # Find the rate
        rate_match = re.search(rf'{search}.*?(\d+\.?\d*)%', html, re.DOTALL | re.IGNORECASE)
        rate = float(rate_match.group(1)) / 100 if rate_match else None
        
        # Find the rationale - typically after "Rationale:" or in a paragraph after the rate
        rationale = ""
        rat_match = re.search(rf'{search}.*?(?:Rationale|rationale)[:\s]*(?:</[^>]+>)*\s*(.*?)</(?:p|div)', html, re.DOTALL | re.IGNORECASE)
        if rat_match:
            rationale = rat_match.group(1).strip()
        
        if rate is not None:
            assumptions[key] = {
                "title": label,
                "rate": rate,
                "rationale": rationale
            }
    
    if assumptions:
        data['assumptions'] = assumptions
    
    # Thesis
    thesis_match = re.search(r'<h2[^>]*>((?:The )?AI Thesis[^<]*)</h2>\s*(.*?)(?=<(?:section|h2|div[^>]*class="[^"]*(?:assumption|risk|faq)))', html, re.DOTALL | re.IGNORECASE)
    if thesis_match:
        data['thesisTitle'] = clean_text(thesis_match.group(1))
        paras = re.findall(r'<p[^>]*>(.*?)</p>', thesis_match.group(2), re.DOTALL)
        data['thesisParagraphs'] = [p.strip() for p in paras if p.strip() and len(p.strip()) > 20]
    
    # Risks
    risks = []
    # Find risk section
    risk_section = re.search(r'(?:Key Risks|Structural Risks|Risk Factors).*?</h2>(.*?)(?=<section|<div[^>]*class="[^"]*(?:faq|disclaimer))', html, re.DOTALL | re.IGNORECASE)
    if risk_section:
        risk_intro_match = re.search(r'<p[^>]*>(.*?)</p>', risk_section.group(1), re.DOTALL)
        risk_intro = risk_intro_match.group(1).strip() if risk_intro_match else ""
        
        risk_items = re.findall(r'<h3[^>]*>(.*?)</h3>\s*<p[^>]*>(.*?)</p>', risk_section.group(1), re.DOTALL)
        for title, desc in risk_items:
            risks.append({
                "title": clean_text(title),
                "description": desc.strip()
            })
        
        if risks:
            data['risks'] = {
                "introText": risk_intro,
                "items": risks
            }
    
    # FAQ
    faq = []
    faq_section = re.search(r'(?:Frequently Asked|FAQ).*?</h2>(.*?)(?=<section|<div[^>]*class="[^"]*disclaimer|<footer)', html, re.DOTALL | re.IGNORECASE)
    if faq_section:
        faq_items = re.findall(r'<h3[^>]*>(.*?)</h3>\s*<p[^>]*>(.*?)</p>', faq_section.group(1), re.DOTALL)
        for q, a in faq_items:
            q_clean = clean_text(q)
            if '?' in q_clean:
                faq.append({"question": q_clean, "answer": a.strip()})
    
    if faq:
        data['faq'] = faq
    
    data['verdictFooter'] = "Based on FY2025 actuals. Data via S&P Global (Mar 18, 2026)."
    
    return data

def get_meta_from_source(slug):
    """Get meta from source .astro file"""
    source_path = os.path.join(PAGES_DIR, f"{slug}.astro")
    if not os.path.exists(source_path):
        return {}
    
    with open(source_path, 'r') as f:
        content = f.read()
    
    meta = {}
    m = re.search(r'export\s+const\s+meta\s*=\s*\{([^}]+)\}', content, re.DOTALL)
    if m:
        block = m.group(1)
        for key in ['title', 'description', 'category', 'published']:
            km = re.search(rf'{key}\s*:\s*["\']([^"\']+)["\']', block)
            if km:
                meta[key] = km.group(1)
    return meta

def main():
    # Find all built IV pages
    pattern = os.path.join(DIST_DIR, "*-intrinsic-value", "index.html")
    files = sorted(glob.glob(pattern))
    print(f"Found {len(files)} built IV pages")
    
    success = 0
    errors = []
    incomplete = []
    
    for filepath in files:
        # Extract slug from path
        slug = filepath.split("/")[-2]  # e.g., "apple-intrinsic-value"
        
        try:
            data = process_html(filepath, slug)
            
            # Merge in source meta
            meta = get_meta_from_source(slug)
            if meta.get('published') and 'published' not in data:
                data['published'] = meta['published']
            if meta.get('title') and 'title' not in data:
                data['title'] = meta['title']
            if meta.get('description') and 'description' not in data:
                data['description'] = meta['description']
            data.setdefault('published', '2026-03-18')
            
            # Check completeness
            critical = ['ticker', 'companyName', 'computedIV', 'currentPrice', 'fcfGrowthRate', 'discountRate', 'terminalGrowthRate']
            missing = [f for f in critical if f not in data or data[f] is None]
            
            ticker = data.get('ticker', slug.replace('-intrinsic-value', '')).lower()
            outpath = os.path.join(OUTPUT_DIR, f"{ticker}.json")
            
            with open(outpath, 'w') as f:
                json.dump(data, f, indent=2)
            
            success += 1
            if missing:
                incomplete.append((slug, missing))
            
            if success % 20 == 0:
                print(f"  Processed {success}/{len(files)}...")
                
        except Exception as e:
            errors.append((slug, str(e)))
            print(f"  ERROR: {slug}: {e}")
    
    print(f"\nDone: {success}/{len(files)} extracted")
    
    complete_count = success - len(incomplete)
    print(f"Complete (all fields): {complete_count}")
    print(f"Incomplete (missing some fields): {len(incomplete)}")
    
    if errors:
        print(f"\nErrors ({len(errors)}):")
        for slug, err in errors:
            print(f"  {slug}: {err}")
    
    if incomplete:
        print(f"\nIncomplete pages ({len(incomplete)}):")
        for slug, fields in incomplete[:20]:
            print(f"  {slug}: missing {', '.join(fields)}")
        if len(incomplete) > 20:
            print(f"  ... and {len(incomplete) - 20} more")

if __name__ == "__main__":
    main()
