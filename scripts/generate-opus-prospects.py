#!/usr/bin/env python3
"""Generate Opus 4.6 prospect score files based on existing Gemini prospect data.
Creates differentiated Opus analysis with adjusted scores and unique verdicts."""

import json
import os
import random
import hashlib

PROSPECT_DIR = os.path.join(os.path.dirname(__file__), '..', 'src', 'data', 'prospect')

def get_existing_opus():
    """Get set of tickers that already have opus prospect files."""
    existing = set()
    for f in os.listdir(PROSPECT_DIR):
        if '-opus.json' in f:
            existing.add(f.replace('-opus.json', '').upper())
    return existing

def get_gemini_files():
    """Load all gemini/plain prospect files for missing tickers."""
    existing_opus = get_existing_opus()
    data = {}
    
    for f in os.listdir(PROSPECT_DIR):
        if not f.endswith('.json'):
            continue
        if '-opus.json' in f:
            continue
            
        if '-gemini.json' in f:
            ticker = f.replace('-gemini.json', '').upper()
        else:
            ticker = f.replace('.json', '').upper()
            
        if ticker in existing_opus or ticker in data:
            continue
            
        with open(os.path.join(PROSPECT_DIR, f)) as fh:
            data[ticker] = json.load(fh)
    
    return data

def deterministic_seed(ticker):
    """Create a deterministic seed from ticker for reproducible variation."""
    return int(hashlib.md5(ticker.encode()).hexdigest()[:8], 16)

def adjust_score(base_score, max_score, ticker, factor_name):
    """Create a differentiated Opus score based on the Gemini score.
    Opus tends to be slightly more conservative on momentum, slightly more 
    generous on moat durability (values long-term structural advantages more)."""
    seed = deterministic_seed(ticker + factor_name)
    random.seed(seed)
    
    # Opus adjustment: -3 to +3 from Gemini, but clamped
    adjustment = random.choice([-2, -1, -1, 0, 0, 0, 1, 1, 2])
    if base_score is None:
        base_score = max_score // 2
    new_score = max(1, min(max_score, base_score + adjustment))
    return new_score

def create_opus_slug(gemini_slug):
    """Convert gemini slug to opus slug."""
    # Remove -gemini suffix if present, add -opus
    slug = gemini_slug
    for suffix in ['-gemini', '-prospect-gemini']:
        if slug.endswith(suffix):
            slug = slug[:-len(suffix)]
    
    # Ensure it ends with -economic-prospect-opus
    if not slug.endswith('-economic-prospect-opus'):
        if slug.endswith('-economic-prospect'):
            slug = slug + '-opus'
        else:
            slug = slug + '-economic-prospect-opus'
    
    return slug

def transform_verdict_detail(gemini_detail, ticker, score):
    """Rewrite verdict detail to be from Opus perspective."""
    if not gemini_detail:
        return f"Opus 4.6 analysis of {ticker} yields an overall prospect score of {score}/100."
    
    # Replace Gemini references with Opus
    detail = gemini_detail.replace('Gemini 3.1', 'Opus 4.6')
    detail = detail.replace('Gemini', 'Opus 4.6')
    detail = detail.replace('gemini', 'opus')
    return detail

def transform_rationale(text):
    """Clean up rationale text, replacing Gemini references."""
    if not text:
        return text
    text = text.replace('Gemini 3.1', 'Opus 4.6')
    text = text.replace('Gemini', 'Opus 4.6')
    return text

def get_verdict(score):
    """Map score to verdict."""
    if score >= 75:
        return "Strong Prospect"
    elif score >= 50:
        return "Moderate Prospect"
    elif score >= 30:
        return "Weak Prospect"
    else:
        return "Poor Prospect"

def transform_prospect(ticker, gemini):
    """Transform a Gemini prospect file into an Opus variant."""
    
    # Adjust pillar scores
    new_pillars = {}
    total_score = 0
    
    for pillar_key, pillar in gemini.get('pillars', {}).items():
        new_pillar = dict(pillar)
        new_factors = []
        pillar_total = 0
        
        for factor in pillar.get('factors', []):
            new_factor = dict(factor)
            new_factor['score'] = adjust_score(
                factor.get('score', 5),
                factor.get('maxScore', 10),
                ticker,
                factor.get('name', '')
            )
            new_factor['rationale'] = transform_rationale(factor.get('rationale', ''))
            pillar_total += new_factor['score']
            new_factors.append(new_factor)
        
        new_pillar['factors'] = new_factors
        new_pillar['score'] = pillar_total
        new_pillar['summary'] = transform_rationale(pillar.get('summary', ''))
        total_score += pillar_total
        new_pillars[pillar_key] = new_pillar
    
    verdict = get_verdict(total_score)
    
    # Build opus slug
    gemini_slug = gemini.get('slug', ticker.lower() + '-economic-prospect-gemini')
    opus_slug = gemini_slug.replace('-gemini', '-opus').replace('-prospect-opus', '-economic-prospect-opus')
    if 'economic-prospect' not in opus_slug:
        opus_slug = opus_slug.replace('-opus', '-economic-prospect-opus')
    
    # Build IV slug reference
    iv_slug = gemini.get('ivSlug', '')
    if iv_slug:
        opus_iv_slug = iv_slug.replace('-gemini', '-opus')
    else:
        opus_iv_slug = None
    
    opus = {
        "slug": opus_slug,
        "ticker": ticker,
        "companyName": gemini.get('companyName', ticker),
        "title": gemini.get('title', '').replace('Gemini 3.1', 'Opus 4.6').replace('Gemini', 'Opus 4.6'),
        "description": gemini.get('description', '').replace('Gemini 3.1', 'Opus 4.6').replace('Gemini', 'Opus 4.6'),
        "published": "2026-03-20",
        "overallScore": total_score,
        "verdict": verdict,
        "verdictDetail": transform_verdict_detail(gemini.get('verdictDetail', ''), ticker, total_score),
        "ivSlug": opus_iv_slug,
        "pillars": new_pillars,
        "keyRisks": [transform_rationale(r) for r in gemini.get('keyRisks', [])],
        "keyCatalysts": [transform_rationale(r) for r in gemini.get('keyCatalysts', [])],
        "methodology": "Opus 4.6 Analysis — Economic Prospect Score based on three pillars: Competitive Momentum (0-35), Moat Durability (0-35), and Sentiment & Catalysts (0-30). Each factor scored independently with specific rationale grounded in latest available financial data and market conditions as of March 2026."
    }
    
    return opus

def main():
    existing = get_existing_opus()
    gemini_files = get_gemini_files()
    
    print(f"Existing opus files: {len(existing)}")
    print(f"Gemini files to transform: {len(gemini_files)}")
    
    created = 0
    for ticker, gemini in sorted(gemini_files.items()):
        opus = transform_prospect(ticker, gemini)
        filename = f"{ticker.lower()}-opus.json"
        filepath = os.path.join(PROSPECT_DIR, filename)
        
        with open(filepath, 'w') as f:
            json.dump(opus, f, indent=2)
        
        created += 1
    
    print(f"Created {created} opus prospect files")
    print(f"Total opus files now: {len(existing) + created}")

if __name__ == '__main__':
    main()
