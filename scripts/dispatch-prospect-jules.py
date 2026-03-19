#!/usr/bin/env python3
"""Dispatch Jules sessions for Economic Prospect Scores — Gemini 3.1 analysis."""
import json, subprocess, time, sys

JULES_KEY = open('/Users/gab/.openclaw/workspace/.jules-key').read().strip()
SOURCE = "sources/github/GabrielDancause/westmount-fundamentals"

COMPANIES = {
    'MSFT': 'Microsoft Corporation',
    'NVDA': 'NVIDIA Corporation',
    'AMZN': 'Amazon.com Inc.',
    'META': 'Meta Platforms Inc.',
    'BRK.B': 'Berkshire Hathaway Inc.',
    'TSLA': 'Tesla Inc.',
    'AVGO': 'Broadcom Inc.',
    'LLY': 'Eli Lilly and Company',
    'JPM': 'JPMorgan Chase & Co.',
    'V': 'Visa Inc.',
    'MA': 'Mastercard Incorporated',
    'UNH': 'UnitedHealth Group Inc.',
    'COST': 'Costco Wholesale Corporation',
    'HD': 'The Home Depot Inc.',
    'NFLX': 'Netflix Inc.',
    'JNJ': 'Johnson & Johnson',
    'ABBV': 'AbbVie Inc.',
    'WMT': 'Walmart Inc.',
    'ORCL': 'Oracle Corporation',
    'PG': 'Procter & Gamble Co.',
    'BAC': 'Bank of America Corporation',
    'SAP': 'SAP SE',
    'CRM': 'Salesforce Inc.',
    'XOM': 'Exxon Mobil Corporation',
    'TSMC': 'Taiwan Semiconductor Manufacturing',
    'MRK': 'Merck & Co. Inc.',
    'AMD': 'Advanced Micro Devices Inc.',
    'ASML': 'ASML Holding N.V.',
    'KO': 'The Coca-Cola Company',
    'PEP': 'PepsiCo Inc.',
    'TMO': 'Thermo Fisher Scientific Inc.',
    'ACN': 'Accenture plc',
    'CSCO': 'Cisco Systems Inc.',
    'LIN': 'Linde plc',
    'ABT': 'Abbott Laboratories',
    'NOW': 'ServiceNow Inc.',
    'MCD': "McDonald's Corporation",
    'ISRG': 'Intuitive Surgical Inc.',
    'IBM': 'International Business Machines',
    'ADBE': 'Adobe Inc.',
    'GE': 'GE Aerospace',
    'INTU': 'Intuit Inc.',
    'QCOM': 'Qualcomm Incorporated',
    'TXN': 'Texas Instruments Incorporated',
    'PM': 'Philip Morris International Inc.',
    'CAT': 'Caterpillar Inc.',
    'AXP': 'American Express Company',
    'BKNG': 'Booking Holdings Inc.',
    'AMGN': 'Amgen Inc.',
    'PFE': 'Pfizer Inc.',
    'CMCSA': 'Comcast Corporation',
    'DHR': 'Danaher Corporation',
    'BLK': 'BlackRock Inc.',
    'LOW': "Lowe's Companies Inc.",
    'HON': 'Honeywell International Inc.',
    'AMAT': 'Applied Materials Inc.',
    'GS': 'Goldman Sachs Group Inc.',
    'T': 'AT&T Inc.',
}

# Ticker to slug mapping
def ticker_to_slug(ticker, name):
    slug_map = {
        'AAPL': 'apple', 'MSFT': 'microsoft', 'NVDA': 'nvidia', 'AMZN': 'amazon',
        'GOOGL': 'google', 'META': 'meta', 'BRK.B': 'berkshire-hathaway', 'TSLA': 'tesla',
        'AVGO': 'broadcom', 'LLY': 'eli-lilly', 'JPM': 'jpmorgan', 'V': 'visa',
        'MA': 'mastercard', 'UNH': 'unitedhealth', 'COST': 'costco', 'HD': 'home-depot',
        'NFLX': 'netflix', 'JNJ': 'johnson-johnson', 'ABBV': 'abbvie', 'WMT': 'walmart',
        'ORCL': 'oracle', 'PG': 'procter-gamble', 'BAC': 'bank-of-america', 'SAP': 'sap',
        'CRM': 'salesforce', 'XOM': 'exxon-mobil', 'TSMC': 'tsmc', 'MRK': 'merck',
        'AMD': 'amd', 'ASML': 'asml', 'KO': 'coca-cola', 'PEP': 'pepsico',
        'TMO': 'thermo-fisher', 'ACN': 'accenture', 'CSCO': 'cisco', 'LIN': 'linde',
        'ABT': 'abbott', 'NOW': 'servicenow', 'MCD': 'mcdonalds', 'ISRG': 'intuitive-surgical',
        'IBM': 'ibm', 'ADBE': 'adobe', 'GE': 'ge-aerospace', 'INTU': 'intuit',
        'QCOM': 'qualcomm', 'TXN': 'texas-instruments', 'PM': 'philip-morris',
        'CAT': 'caterpillar', 'AXP': 'american-express', 'BKNG': 'booking-holdings',
        'AMGN': 'amgen', 'PFE': 'pfizer', 'CMCSA': 'comcast', 'DHR': 'danaher',
        'BLK': 'blackrock', 'LOW': 'lowes', 'HON': 'honeywell', 'AMAT': 'applied-materials',
        'GS': 'goldman-sachs', 'T': 'att',
    }
    return slug_map.get(ticker, ticker.lower().replace('.', '-'))

def make_prompt(ticker, name, slug):
    return f"""Create a single file: src/data/prospect/{ticker.lower().replace('.', '-')}-gemini.json

This is an Economic Prospect Score for {name} ({ticker}). You CAN make outbound HTTP requests to fetch real data. null over fake data, always.

IMPORTANT: You are creating a JSON data file, NOT an Astro page. The template already exists and will render it automatically.

## Scoring Framework

Three pillars:
1. **Competitive Momentum (0-35)**: Revenue Growth vs. Peers (0-10), Market Share Trajectory (0-10), Pricing Power (0-8), Product Velocity (0-7)
2. **Moat Durability (0-35)**: Switching Costs (0-10), Network Effects (0-10), Regulatory & IP Position (0-8), Capital Intensity Advantage (0-7)
3. **Sentiment & Catalysts (0-30)**: Earnings Estimate Revisions (0-10), News & Narrative Sentiment (0-10), Management & Capital Allocation (0-10)

Overall Score = sum of all three pillars (0-100).

## Verdict Scale
- 70-100: "Strong Prospect"
- 50-69: "Moderate Prospect"
- 30-49: "Weak Prospect"
- 0-29: "Poor Prospect"

## Instructions
1. Research {name} latest financials (FY2025 10-K or most recent annual, recent earnings, news)
2. Score each factor honestly with detailed rationale (2-4 sentences per factor). Be critical — do NOT inflate scores.
3. Write a verdictDetail paragraph (3-4 sentences) summarizing the overall position
4. Include 3 keyRisks and 3 keyCatalysts (specific to {name}, not generic)
5. The slug MUST be "{slug}-economic-prospect-gemini"
6. Set published to "2026-03-19"

## JSON schema (follow exactly):
{{
  "slug": "{slug}-economic-prospect-gemini",
  "ticker": "{ticker}",
  "companyName": "{name}",
  "title": "{name} ({ticker}) Economic Prospect Score — Gemini 3.1 Analysis",
  "description": "Gemini 3.1 forward-looking economic prospect analysis of {name} ({ticker}).",
  "published": "2026-03-19",
  "overallScore": <number>,
  "verdict": "<verdict>",
  "verdictDetail": "<3-4 sentences>",
  "ivSlug": null,
  "pillars": {{
    "competitiveMomentum": {{ "score": <sum>, "maxScore": 35, "title": "Competitive Momentum", "summary": "...", "factors": [
      {{ "name": "Revenue Growth vs. Peers", "score": <0-10>, "maxScore": 10, "rationale": "..." }},
      {{ "name": "Market Share Trajectory", "score": <0-10>, "maxScore": 10, "rationale": "..." }},
      {{ "name": "Pricing Power", "score": <0-8>, "maxScore": 8, "rationale": "..." }},
      {{ "name": "Product Velocity", "score": <0-7>, "maxScore": 7, "rationale": "..." }}
    ] }},
    "moatDurability": {{ "score": <sum>, "maxScore": 35, "title": "Moat Durability", "summary": "...", "factors": [
      {{ "name": "Switching Costs", "score": <0-10>, "maxScore": 10, "rationale": "..." }},
      {{ "name": "Network Effects", "score": <0-10>, "maxScore": 10, "rationale": "..." }},
      {{ "name": "Regulatory & IP Position", "score": <0-8>, "maxScore": 8, "rationale": "..." }},
      {{ "name": "Capital Intensity Advantage", "score": <0-7>, "maxScore": 7, "rationale": "..." }}
    ] }},
    "sentimentCatalyst": {{ "score": <sum>, "maxScore": 30, "title": "Sentiment & Catalysts", "summary": "...", "factors": [
      {{ "name": "Earnings Estimate Revisions", "score": <0-10>, "maxScore": 10, "rationale": "..." }},
      {{ "name": "News & Narrative Sentiment", "score": <0-10>, "maxScore": 10, "rationale": "..." }},
      {{ "name": "Management & Capital Allocation", "score": <0-10>, "maxScore": 10, "rationale": "..." }}
    ] }}
  }},
  "keyRisks": ["<risk1>", "<risk2>", "<risk3>"],
  "keyCatalysts": ["<catalyst1>", "<catalyst2>", "<catalyst3>"],
  "methodology": "Score is based on three pillars: Competitive Momentum (0-35), Moat Durability (0-35), and Sentiment & Catalysts (0-30), totaling 0-100. Each pillar is broken into individually scored factors with transparent rationale. Data sources include FY2025 10-K filings, analyst consensus estimates, news sentiment analysis, and competitive landscape assessment. The score is forward-looking and represents economic prospect over a 2-3 year horizon."
}}

Create the file now. Do not ask for confirmation."""

def dispatch(ticker, name):
    slug = ticker_to_slug(ticker, name)
    prompt = make_prompt(ticker, name, slug)
    payload = json.dumps({
        "prompt": prompt,
        "sourceContext": {
            "source": f"sources/github/GabrielDancause/westmount-fundamentals",
            "githubRepoContext": {"startingBranch": "main"}
        },
        "automationMode": "AUTO_CREATE_PR",
        "title": f"Prospect Score: {name} ({ticker})"
    })
    
    result = subprocess.run(
        ["curl", "-s", "-X", "POST", "https://jules.googleapis.com/v1alpha/sessions",
         "-H", f"X-Goog-Api-Key: {JULES_KEY}",
         "-H", "Content-Type: application/json",
         "-d", payload],
        capture_output=True, text=True
    )
    
    try:
        data = json.loads(result.stdout)
        if 'error' in data:
            return ticker, None, data['error'].get('message', 'Unknown error')
        return ticker, data.get('id'), None
    except:
        return ticker, None, result.stdout[:200]

# Dispatch all
sessions = {}
errors = []
for i, (ticker, name) in enumerate(COMPANIES.items()):
    t, sid, err = dispatch(ticker, name)
    if err:
        errors.append((t, err))
        print(f"[{i+1}/58] ❌ {t}: {err[:80]}")
    else:
        sessions[t] = sid
        print(f"[{i+1}/58] ✅ {t}: {sid}")
    time.sleep(0.5)  # Rate limit

print(f"\n=== SUMMARY ===")
print(f"Dispatched: {len(sessions)}")
print(f"Failed: {len(errors)}")

# Save session IDs
with open('prospect-jules-sessions.json', 'w') as f:
    json.dump(sessions, f, indent=2)

if errors:
    print("\nErrors:")
    for t, e in errors:
        print(f"  {t}: {e[:100]}")
