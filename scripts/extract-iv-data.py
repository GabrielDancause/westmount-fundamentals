#!/usr/bin/env python3
"""
Extract IV data from .astro files and produce JSON data files.
Handles both hardcoded and dynamic-fetch page patterns.
"""

import os
import re
import json
import glob
import sys

PAGES_DIR = "src/pages"
OUTPUT_DIR = "src/data/iv"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_frontmatter(content):
    """Extract content between --- markers"""
    parts = content.split("---", 2)
    if len(parts) >= 3:
        return parts[1], parts[2]
    return content, ""

def find_value(content, patterns, default=None):
    """Try multiple regex patterns, return first match"""
    for pattern in patterns:
        m = re.search(pattern, content)
        if m:
            val = m.group(1).strip()
            # Clean up the value
            val = val.replace(",", "").replace("$", "").replace("%", "")
            try:
                return float(val)
            except:
                return val
    return default

def find_text(content, patterns, default=""):
    """Try multiple regex patterns for text content"""
    for pattern in patterns:
        m = re.search(pattern, content, re.DOTALL)
        if m:
            return m.group(1).strip()
    return default

def extract_meta(frontmatter):
    """Extract export const meta"""
    meta = {}
    m = re.search(r'export\s+const\s+meta\s*=\s*\{([^}]+)\}', frontmatter, re.DOTALL)
    if m:
        block = m.group(1)
        for key in ['title', 'description', 'category', 'published']:
            km = re.search(rf'{key}\s*:\s*["\']([^"\']+)["\']', block)
            if km:
                meta[key] = km.group(1)
    return meta

def extract_assumptions(content):
    """Extract the 3 key assumptions with rationales"""
    assumptions = {}
    
    # FCF Growth
    fcf_growth = find_value(content, [
        r'(?:fcfGrowth|FCF_GROWTH|fcf_growth_rate|growthRate).*?=\s*([\d.]+)',
        r'FCF Growth Rate.*?(\d+\.?\d*)%',
        r'growth.*?rate.*?(\d+\.?\d*)%',
    ])
    
    # Discount Rate / WACC
    wacc = find_value(content, [
        r'(?:WACC|wacc|discountRate|discount_rate|DISCOUNT_RATE).*?=\s*([\d.]+)',
        r'Discount Rate.*?(\d+\.?\d*)%',
        r'WACC.*?(\d+\.?\d*)%',
    ])
    
    # Terminal Growth
    terminal = find_value(content, [
        r'(?:terminalGrowth|terminal_growth|TERMINAL_GROWTH|terminalRate).*?=\s*([\d.]+)',
        r'Terminal Growth.*?(\d+\.?\d*)%',
        r'terminal.*?growth.*?(\d+\.?\d*)%',
    ])
    
    return fcf_growth, wacc, terminal

def extract_financial_inputs(frontmatter):
    """Extract base FCF, shares outstanding, current price, net cash/debt"""
    base_fcf = find_value(frontmatter, [
        r'(?:BASE_FCF|baseFCF|base_fcf|fcfBase|FCF_BASE|lastFCF|LAST_FCF|fcf\s*=)\s*[=:]?\s*([\d,.]+)',
        r'(?:free.cash.flow|FCF).*?([\d,.]+)',
    ])
    
    shares = find_value(frontmatter, [
        r'(?:SHARES|sharesOutstanding|shares_outstanding|SHARES_OUT|sharesOut)\s*[=:]?\s*([\d,.]+)',
    ])
    
    price = find_value(frontmatter, [
        r'(?:CURRENT_PRICE|currentPrice|current_price|PRICE)\s*[=:]?\s*([\d,.]+)',
        r'currentPriceData.*?:\s*([\d,.]+)',
    ])
    
    net_cash = find_value(frontmatter, [
        r'(?:NET_CASH|netCash|net_cash|netDebt|NET_DEBT)\s*[=:]?\s*(-?[\d,.]+)',
    ])
    
    return base_fcf, shares, price, net_cash

def extract_sensitivity(frontmatter):
    """Extract sensitivity matrix parameters"""
    discount_rates = []
    growth_rates = []
    
    # Look for array patterns
    dr_match = re.search(r'(?:sensitivityDiscountRates|discountRates|waccRange)\s*[=:]\s*\[([\d.,\s]+)\]', frontmatter)
    if dr_match:
        discount_rates = [float(x.strip()) for x in dr_match.group(1).split(",") if x.strip()]
    
    gr_match = re.search(r'(?:sensitivityGrowthRates|growthRates|terminalRange)\s*[=:]\s*\[([\d.,\s]+)\]', frontmatter)
    if gr_match:
        growth_rates = [float(x.strip()) for x in gr_match.group(1).split(",") if x.strip()]
    
    return discount_rates, growth_rates

def extract_text_sections(html_part):
    """Extract thesis, risks, FAQ from HTML"""
    result = {}
    
    # Thesis - look for the thesis section
    thesis_title = find_text(html_part, [
        r'<h2[^>]*>(The AI Thesis:[^<]+)</h2>',
        r'<h2[^>]*>(.*?Thesis.*?)</h2>',
    ])
    
    # Extract thesis paragraphs
    thesis_paragraphs = []
    thesis_match = re.search(r'(?:AI Thesis|thesis).*?</h2>\s*((?:<p[^>]*>.*?</p>\s*)+)', html_part, re.DOTALL | re.IGNORECASE)
    if thesis_match:
        paras = re.findall(r'<p[^>]*>(.*?)</p>', thesis_match.group(1), re.DOTALL)
        thesis_paragraphs = [p.strip() for p in paras if p.strip()]
    
    result['thesisTitle'] = thesis_title
    result['thesisParagraphs'] = thesis_paragraphs
    
    # Assumptions with rationales
    assumptions_data = {}
    assumption_blocks = re.findall(
        r'<(?:div|section)[^>]*class="[^"]*assumption[^"]*"[^>]*>(.*?)</(?:div|section)>',
        html_part, re.DOTALL
    )
    
    # Also try to find rationale text near assumption labels
    for label_key, search_terms in [
        ('fcfGrowth', ['FCF Growth', 'Growth Rate.*Y1', 'growth rate']),
        ('discountRate', ['Discount Rate', 'WACC']),
        ('terminalGrowth', ['Terminal Growth', 'terminal growth']),
    ]:
        for term in search_terms:
            rationale_match = re.search(
                rf'{term}.*?(?:Rationale|rationale)[:\s]*</?\w+[^>]*>\s*(.*?)</(?:p|div)',
                html_part, re.DOTALL | re.IGNORECASE
            )
            if rationale_match:
                assumptions_data[label_key] = rationale_match.group(1).strip()
                break
    
    result['assumptionRationales'] = assumptions_data
    
    # Risks
    risks = []
    risk_items = re.findall(
        r'<h3[^>]*>((?:\d+\.\s*)?[^<]+(?:Risk|risk)[^<]*)</h3>\s*<p[^>]*>(.*?)</p>',
        html_part, re.DOTALL
    )
    if not risk_items:
        risk_items = re.findall(
            r'<h3[^>]*>(\d+\.\s*[^<]+)</h3>\s*<p[^>]*>(.*?)</p>',
            html_part, re.DOTALL
        )
    for title, desc in risk_items:
        risks.append({"title": title.strip(), "description": desc.strip()})
    
    result['risks'] = risks
    
    # FAQ
    faq = []
    faq_items = re.findall(
        r'<h3[^>]*>(.*?\?)</h3>\s*<p[^>]*>(.*?)</p>',
        html_part, re.DOTALL
    )
    for q, a in faq_items:
        q_clean = re.sub(r'<[^>]+>', '', q).strip()
        a_clean = a.strip()
        if q_clean and '?' in q_clean:
            faq.append({"question": q_clean, "answer": a_clean})
    
    result['faq'] = faq
    
    # Risk intro text
    risk_intro = find_text(html_part, [
        r'(?:risks?.*?section|risk-section).*?<p[^>]*>(.*?)</p>',
    ])
    result['risksIntro'] = risk_intro
    
    return result

def extract_slug_from_filename(filepath):
    """Get slug from filename"""
    basename = os.path.basename(filepath).replace(".astro", "")
    return basename

def process_file(filepath):
    """Process a single .astro file and return JSON data"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    frontmatter, html_part = extract_frontmatter(content)
    slug = extract_slug_from_filename(filepath)
    
    # Meta
    meta = extract_meta(frontmatter)
    
    # Ticker from meta title or content
    ticker_match = re.search(r'\(([A-Z]{1,5})\)', meta.get('title', '') or '')
    if not ticker_match:
        ticker_match = re.search(r'ticker.*?["\']([A-Z]{1,5})["\']', frontmatter)
    ticker = ticker_match.group(1) if ticker_match else slug.replace('-intrinsic-value', '').upper()
    
    # Company name
    company = find_text(frontmatter, [
        r'title\s*:\s*["\']([^("\']+?)(?:\s*\()',
    ]) or meta.get('title', '').split('(')[0].strip()
    
    # Financial inputs
    base_fcf, shares, price, net_cash = extract_financial_inputs(frontmatter)
    
    # Assumptions
    fcf_growth, wacc, terminal = extract_assumptions(frontmatter)
    
    # Sensitivity
    sens_dr, sens_gr = extract_sensitivity(frontmatter)
    
    # Text sections
    text_data = extract_text_sections(html_part)
    
    # Build JSON
    data = {
        "slug": slug,
        "ticker": ticker,
        "companyName": company,
        "title": meta.get('title', f"{company} ({ticker}) Intrinsic Value"),
        "description": meta.get('description', f"An independent DCF intrinsic value analysis of {company} ({ticker}) compiled by Gemini 3.1."),
        "published": meta.get('published', '2026-03-18'),
    }
    
    # Add financial inputs (only if found)
    if base_fcf is not None: data["baseFCF"] = base_fcf
    if shares is not None: data["sharesOut"] = shares
    if price is not None: data["currentPrice"] = price
    if net_cash is not None: data["netCash"] = net_cash
    
    # Growth rates - normalize to decimal if > 1
    if fcf_growth is not None:
        data["fcfGrowthRate"] = fcf_growth / 100 if fcf_growth > 1 else fcf_growth
    if wacc is not None:
        data["discountRate"] = wacc / 100 if wacc > 1 else wacc
    if terminal is not None:
        data["terminalGrowthRate"] = terminal / 100 if terminal > 1 else terminal
    
    if sens_dr: data["sensitivityDiscountRates"] = sens_dr
    if sens_gr: data["sensitivityGrowthRates"] = sens_gr
    
    # Text content
    if text_data.get('thesisTitle'):
        data["thesisTitle"] = text_data['thesisTitle']
    if text_data.get('thesisParagraphs'):
        data["thesisParagraphs"] = text_data['thesisParagraphs']
    
    # Assumptions with rationales
    assumptions = {}
    labels = [
        ('fcfGrowth', 'FCF Growth Rate (Y1-Y5)', data.get('fcfGrowthRate')),
        ('discountRate', 'Discount Rate (WACC)', data.get('discountRate')),
        ('terminalGrowth', 'Terminal Growth Rate', data.get('terminalGrowthRate')),
    ]
    for key, title, rate in labels:
        if rate is not None:
            assumptions[key] = {
                "title": title,
                "rate": rate,
                "rationale": text_data.get('assumptionRationales', {}).get(key, "")
            }
    if assumptions:
        data["assumptions"] = assumptions
    
    # Risks
    if text_data.get('risks'):
        data["risks"] = {
            "introText": text_data.get('risksIntro', ''),
            "items": text_data['risks']
        }
    
    # FAQ
    if text_data.get('faq'):
        data["faq"] = text_data['faq']
    
    data["verdictFooter"] = "Based on FY2025 actuals. Data via S&P Global (Mar 18, 2026)."
    
    return data

def main():
    files = sorted(glob.glob(f"{PAGES_DIR}/*-intrinsic-value.astro"))
    print(f"Found {len(files)} IV pages to process")
    
    success = 0
    errors = []
    missing_fields = {}
    
    for filepath in files:
        slug = extract_slug_from_filename(filepath)
        try:
            data = process_file(filepath)
            ticker = data.get('ticker', 'unknown').lower()
            outpath = os.path.join(OUTPUT_DIR, f"{ticker}.json")
            
            # Track missing critical fields
            critical = ['baseFCF', 'sharesOut', 'currentPrice', 'fcfGrowthRate', 'discountRate', 'terminalGrowthRate']
            missing = [f for f in critical if f not in data]
            if missing:
                missing_fields[slug] = missing
            
            with open(outpath, 'w') as f:
                json.dump(data, f, indent=2)
            
            success += 1
            if success % 20 == 0:
                print(f"  Processed {success}/{len(files)}...")
                
        except Exception as e:
            errors.append((slug, str(e)))
            print(f"  ERROR: {slug}: {e}")
    
    print(f"\nDone: {success}/{len(files)} extracted")
    if errors:
        print(f"\nErrors ({len(errors)}):")
        for slug, err in errors:
            print(f"  {slug}: {err}")
    
    if missing_fields:
        print(f"\nPages missing critical fields ({len(missing_fields)}):")
        for slug, fields in sorted(missing_fields.items()):
            print(f"  {slug}: {', '.join(fields)}")

if __name__ == "__main__":
    main()
