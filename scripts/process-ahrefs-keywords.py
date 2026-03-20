#!/usr/bin/env python3
"""
Ahrefs Keyword Pipeline for Westmount Fundamentals
===================================================
Drop CSVs into ~/Desktop/ahrefs/ → run this script → get prioritized page opportunities.

Usage:
  python3 scripts/process-ahrefs-keywords.py                    # Process all new exports
  python3 scripts/process-ahrefs-keywords.py --force             # Reprocess everything
  python3 scripts/process-ahrefs-keywords.py --topic intrinsic   # Process specific topic only
  python3 scripts/process-ahrefs-keywords.py --top 50            # Show top N opportunities

Output:
  src/data/keyword-opportunities.json   — Machine-readable opportunities
  src/data/keyword-state.json           — Processing state (tracks what's been processed)
"""

import csv
import json
import os
import re
import sys
import hashlib
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Paths
AHREFS_DIR = Path.home() / "Desktop" / "ahrefs"
REPO_DIR = Path.home() / "Desktop" / "westmount-fundamentals"
PAGES_DIR = REPO_DIR / "src" / "pages"
DATA_DIR = REPO_DIR / "src" / "data"
STATE_FILE = DATA_DIR / "keyword-state.json"
OUTPUT_FILE = DATA_DIR / "keyword-opportunities.json"

# Scoring weights
VOLUME_WEIGHT = 1.0
DIFFICULTY_PENALTY = 0.5   # Lower difficulty = better
TOOL_BOOST = 2.5           # Calculator/tool keywords get boosted
CPC_BOOST = 1.5            # High CPC = commercial intent = valuable

# Keywords that signal tool/calculator pages (our moat)
TOOL_SIGNALS = ['calculator', 'calc', 'formula', 'template', 'spreadsheet', 'excel',
                'tool', 'screener', 'tracker', 'finder', 'checker', 'analyzer',
                'comparison', 'compare', 'vs', 'list', 'ranking', 'top']


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"processed_files": {}, "last_run": None}


def save_state(state):
    DATA_DIR.mkdir(exist_ok=True)
    state["last_run"] = datetime.utcnow().isoformat()
    STATE_FILE.write_text(json.dumps(state, indent=2))


def get_existing_pages():
    """Get all existing page slugs."""
    pages = set()
    if PAGES_DIR.exists():
        for f in PAGES_DIR.glob("*.astro"):
            pages.add(f.stem)
    return pages


def get_existing_page_titles():
    """Get page titles from registry for matching."""
    registry_file = DATA_DIR / "pages-registry.json"
    titles = {}
    if registry_file.exists():
        reg = json.loads(registry_file.read_text())
        for slug, data in reg.items():
            titles[slug] = data.get("title", "").lower()
    return titles


def file_hash(path):
    return hashlib.md5(path.read_bytes()).hexdigest()


def parse_csv(filepath):
    """Parse an Ahrefs CSV export into keyword records."""
    keywords = {}
    with open(filepath, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            kw = row.get('Keyword', '').strip().lower()
            if not kw:
                continue

            vol_str = row.get('Volume', '0').strip()
            try:
                vol = int(vol_str) if vol_str else 0
            except ValueError:
                vol = 0

            diff_str = row.get('Difficulty', '0').strip()
            try:
                diff = int(diff_str) if diff_str else 0
            except ValueError:
                diff = 0

            cpc_str = row.get('CPC', '0').strip()
            try:
                cpc = float(cpc_str) if cpc_str else 0
            except ValueError:
                cpc = 0

            gvol_str = row.get('Global volume', '0').strip()
            try:
                gvol = int(gvol_str) if gvol_str else 0
            except ValueError:
                gvol = 0

            tp_str = row.get('Traffic potential', '0').strip()
            try:
                tp = int(tp_str) if tp_str else 0
            except ValueError:
                tp = 0

            intent = row.get('Intents', '')
            url = row.get('URL', '')
            position = row.get('Position', '')
            serp_type = row.get('Type', '')
            title = row.get('Title', '')
            parent_topic = row.get('Parent Topic', '')
            parent_vol_str = row.get('Parent Topic Volume', '0').strip()
            try:
                parent_vol = int(parent_vol_str) if parent_vol_str else 0
            except ValueError:
                parent_vol = 0

            # Keep best data per keyword
            if kw not in keywords or vol > keywords[kw].get('volume', 0):
                keywords[kw] = {
                    'keyword': kw,
                    'volume': vol,
                    'difficulty': diff,
                    'cpc': cpc,
                    'global_volume': gvol,
                    'traffic_potential': tp,
                    'intent': intent,
                    'parent_topic': parent_topic,
                    'parent_volume': parent_vol,
                }

            # Track SERP competitors for organic results
            if 'competitors' not in keywords[kw]:
                keywords[kw]['competitors'] = []
            if url and 'Organic' in serp_type and len(keywords[kw]['competitors']) < 5:
                try:
                    pos = int(position)
                except:
                    pos = 99
                keywords[kw]['competitors'].append({
                    'url': url,
                    'position': pos,
                    'title': title,
                })

    return keywords


def extract_topic_from_filename(filepath):
    """Extract the topic seed from the Ahrefs filename."""
    name = filepath.stem
    # google_us_ebitda_matching-terms_serps_2026-03-16_22-23-48
    parts = name.split('_')
    # Find the topic between 'us' and 'matching'
    topic_parts = []
    capture = False
    for p in parts:
        if p == 'us':
            capture = True
            continue
        if 'matching' in p:
            break
        if capture:
            topic_parts.append(p)
    return '-'.join(topic_parts) if topic_parts else name


def score_keyword(kw_data):
    """Score a keyword opportunity. Higher = better."""
    vol = kw_data.get('volume', 0)
    diff = kw_data.get('difficulty', 0)
    cpc = kw_data.get('cpc', 0)
    tp = kw_data.get('traffic_potential', 0)
    kw = kw_data.get('keyword', '')

    # Base score from volume
    score = max(vol, tp) * VOLUME_WEIGHT

    # Difficulty penalty (KD 0 = full score, KD 100 = 0)
    diff_mult = max(0, 1 - (diff / 100) * DIFFICULTY_PENALTY)
    score *= diff_mult

    # Tool/calculator boost — these are our moat
    is_tool = any(sig in kw for sig in TOOL_SIGNALS)
    if is_tool:
        score *= TOOL_BOOST

    # CPC boost for commercial intent
    if cpc > 1.0:
        score *= min(CPC_BOOST, 1 + cpc * 0.2)

    return round(score, 1)


def cluster_keywords(all_keywords):
    """Cluster keywords into page-level opportunities."""
    # Group by parent topic first, then by semantic similarity
    clusters = defaultdict(list)

    for kw, data in all_keywords.items():
        parent = data.get('parent_topic', '').lower().strip()
        if parent and parent in all_keywords:
            clusters[parent].append(data)
        else:
            # Use the keyword itself as cluster key
            clusters[kw].append(data)

    # Merge small clusters into their closest parent
    merged = {}
    for key, members in clusters.items():
        total_vol = sum(m.get('volume', 0) for m in members)
        best_kw = max(members, key=lambda m: m.get('volume', 0))
        avg_diff = sum(m.get('difficulty', 0) for m in members) / len(members) if members else 0

        merged[key] = {
            'primary_keyword': best_kw['keyword'],
            'keywords': [m['keyword'] for m in members],
            'keyword_count': len(members),
            'total_volume': total_vol,
            'best_volume': best_kw.get('volume', 0),
            'avg_difficulty': round(avg_diff, 1),
            'max_cpc': max(m.get('cpc', 0) for m in members),
            'traffic_potential': max(m.get('traffic_potential', 0) for m in members),
            'intent': best_kw.get('intent', ''),
            'competitors': best_kw.get('competitors', []),
            'score': 0,  # computed below
        }

    return merged


def match_existing_pages(clusters, existing_pages, page_titles):
    """Check which clusters are already served by existing pages."""
    for key, cluster in clusters.items():
        kw = cluster['primary_keyword']
        slug_guess = re.sub(r'[^a-z0-9]+', '-', kw).strip('-')

        # Direct slug match
        matched = None
        for page in existing_pages:
            if page == slug_guess or slug_guess in page or page in slug_guess:
                matched = page
                break

        # Title match
        if not matched:
            for page, title in page_titles.items():
                kw_words = set(kw.split())
                title_words = set(title.split())
                overlap = len(kw_words & title_words) / max(len(kw_words), 1)
                if overlap > 0.5:
                    matched = page
                    break

        # Check secondary keywords too
        if not matched:
            for secondary_kw in cluster['keywords'][:5]:
                sec_slug = re.sub(r'[^a-z0-9]+', '-', secondary_kw).strip('-')
                for page in existing_pages:
                    if sec_slug in page or page in sec_slug:
                        matched = page
                        break
                if matched:
                    break

        cluster['existing_page'] = matched
        cluster['status'] = 'served' if matched else 'gap'

    return clusters


def classify_page_type(cluster):
    """Classify what type of page this should be."""
    kw = cluster['primary_keyword']
    keywords_text = ' '.join(cluster['keywords'])

    if any(w in keywords_text for w in ['calculator', 'calc', 'formula', 'compute']):
        return 'calculator'
    elif any(w in keywords_text for w in ['list', 'top', 'best', 'ranking']):
        return 'list'
    elif any(w in keywords_text for w in ['what is', 'what are', 'meaning', 'definition', 'explained']):
        return 'educational'
    elif any(w in keywords_text for w in ['vs', 'versus', 'comparison', 'difference']):
        return 'comparison'
    elif any(w in keywords_text for w in ['screener', 'tracker', 'finder']):
        return 'tool'
    elif any(w in keywords_text for w in ['example', 'how to', 'guide', 'step']):
        return 'guide'
    else:
        return 'educational'


def run(force=False, topic_filter=None, top_n=30):
    state = load_state()
    existing_pages = get_existing_pages()
    page_titles = get_existing_page_titles()

    print(f"📁 Scanning {AHREFS_DIR}")
    print(f"📄 Existing pages: {len(existing_pages)}")

    # Find all CSV files
    csv_files = sorted(AHREFS_DIR.glob("*.csv"))
    print(f"📊 Found {len(csv_files)} Ahrefs CSV exports\n")

    if topic_filter:
        csv_files = [f for f in csv_files if topic_filter.lower() in f.stem.lower()]
        print(f"🔍 Filtered to {len(csv_files)} files matching '{topic_filter}'\n")

    all_keywords = {}
    topics_processed = set()
    new_files = 0

    for csv_file in csv_files:
        fhash = file_hash(csv_file)
        topic = extract_topic_from_filename(csv_file)

        if not force and csv_file.name in state['processed_files']:
            if state['processed_files'][csv_file.name] == fhash:
                topics_processed.add(topic)
                # Still load the data for analysis
                kws = parse_csv(csv_file)
                all_keywords.update(kws)
                continue

        print(f"  Processing: {csv_file.name} ({topic})")
        kws = parse_csv(csv_file)
        all_keywords.update(kws)
        topics_processed.add(topic)
        state['processed_files'][csv_file.name] = fhash
        new_files += 1

    print(f"\n✅ Parsed {len(all_keywords)} unique keywords from {len(topics_processed)} topics")
    if new_files > 0:
        print(f"   ({new_files} new/updated files)")

    # Cluster keywords
    clusters = cluster_keywords(all_keywords)
    print(f"🔗 Clustered into {len(clusters)} keyword groups")

    # Match against existing pages
    clusters = match_existing_pages(clusters, existing_pages, page_titles)

    # Score and classify
    for key, cluster in clusters.items():
        cluster['score'] = score_keyword({
            'keyword': cluster['primary_keyword'],
            'volume': cluster['total_volume'],
            'difficulty': cluster['avg_difficulty'],
            'cpc': cluster['max_cpc'],
            'traffic_potential': cluster['traffic_potential'],
        })
        cluster['page_type'] = classify_page_type(cluster)

    # Sort by score
    ranked = sorted(clusters.values(), key=lambda c: c['score'], reverse=True)

    # Split into gaps and served
    gaps = [c for c in ranked if c['status'] == 'gap']
    served = [c for c in ranked if c['status'] == 'served']

    # Summary
    total_gap_volume = sum(c['total_volume'] for c in gaps)
    total_served_volume = sum(c['total_volume'] for c in served)

    print(f"\n{'='*60}")
    print(f"📊 RESULTS SUMMARY")
    print(f"{'='*60}")
    print(f"  Total keyword clusters: {len(ranked)}")
    print(f"  Already served:         {len(served)} ({total_served_volume:,} monthly vol)")
    print(f"  GAPS (new pages):       {len(gaps)} ({total_gap_volume:,} monthly vol)")
    print(f"{'='*60}\n")

    # Print top gaps
    print(f"🎯 TOP {min(top_n, len(gaps))} PAGE OPPORTUNITIES (gaps)\n")
    print(f"{'Score':>7} {'Vol':>7} {'KD':>4} {'Type':<13} {'Primary Keyword':<45} {'#KWs':>5}")
    print(f"{'-'*7} {'-'*7} {'-'*4} {'-'*13} {'-'*45} {'-'*5}")

    for c in gaps[:top_n]:
        print(f"{c['score']:>7.0f} {c['total_volume']:>7,} {c['avg_difficulty']:>4.0f} {c['page_type']:<13} {c['primary_keyword'][:45]:<45} {c['keyword_count']:>5}")

    # Print served pages
    print(f"\n✅ TOP SERVED (already have pages)\n")
    print(f"{'Score':>7} {'Vol':>7} {'Page':<35} {'Primary Keyword':<40}")
    print(f"{'-'*7} {'-'*7} {'-'*35} {'-'*40}")
    for c in served[:20]:
        print(f"{c['score']:>7.0f} {c['total_volume']:>7,} {c['existing_page'][:35]:<35} {c['primary_keyword'][:40]:<40}")

    # Page type breakdown for gaps
    type_counts = defaultdict(lambda: {'count': 0, 'volume': 0})
    for c in gaps:
        type_counts[c['page_type']]['count'] += 1
        type_counts[c['page_type']]['volume'] += c['total_volume']

    print(f"\n📋 GAP BREAKDOWN BY PAGE TYPE\n")
    for ptype, data in sorted(type_counts.items(), key=lambda x: x[1]['volume'], reverse=True):
        print(f"  {ptype:<15} {data['count']:>4} pages  {data['volume']:>8,} monthly vol")

    # Save output
    output = {
        'generated_at': datetime.utcnow().isoformat(),
        'total_keywords': len(all_keywords),
        'total_clusters': len(ranked),
        'gaps_count': len(gaps),
        'served_count': len(served),
        'gap_volume': total_gap_volume,
        'served_volume': total_served_volume,
        'topics': sorted(topics_processed),
        'gaps': [{
            'primary_keyword': c['primary_keyword'],
            'keywords': c['keywords'][:20],  # cap to keep file size down
            'keyword_count': c['keyword_count'],
            'total_volume': c['total_volume'],
            'avg_difficulty': c['avg_difficulty'],
            'max_cpc': c['max_cpc'],
            'traffic_potential': c['traffic_potential'],
            'score': c['score'],
            'page_type': c['page_type'],
            'intent': c['intent'],
            'competitors': c['competitors'][:3],
        } for c in gaps[:200]],  # top 200 gaps
        'served': [{
            'primary_keyword': c['primary_keyword'],
            'existing_page': c['existing_page'],
            'total_volume': c['total_volume'],
            'score': c['score'],
        } for c in served[:100]],
    }

    OUTPUT_FILE.write_text(json.dumps(output, indent=2))
    print(f"\n💾 Saved to {OUTPUT_FILE}")

    save_state(state)
    print(f"💾 State saved to {STATE_FILE}")

    return output


if __name__ == '__main__':
    force = '--force' in sys.argv
    topic_filter = None
    top_n = 30

    for i, arg in enumerate(sys.argv):
        if arg == '--topic' and i + 1 < len(sys.argv):
            topic_filter = sys.argv[i + 1]
        if arg == '--top' and i + 1 < len(sys.argv):
            top_n = int(sys.argv[i + 1])

    run(force=force, topic_filter=topic_filter, top_n=top_n)
