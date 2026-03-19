#!/usr/bin/env python3
"""
Generate sitemap.xml including all IV pages from JSON data + all static .astro pages.
"""
import os, glob, json, re
from datetime import datetime

DOMAIN = "https://westmountfundamentals.com"
PAGES_DIR = "src/pages"
IV_DATA_DIR = "src/data/iv"
OUTPUT = "public/sitemap.xml"

def get_astro_pages():
    """Get all static .astro page slugs"""
    pages = []
    for f in sorted(glob.glob(f"{PAGES_DIR}/*.astro")):
        basename = os.path.basename(f).replace('.astro', '')
        # Skip special files
        if basename.startswith('[') or basename.startswith('_'):
            continue
        if basename == 'index':
            pages.append(('/', 'weekly', '1.0'))
        else:
            pages.append((f'/{basename}/', 'monthly', '0.8'))
    
    # Category pages
    for subdir in glob.glob(f"{PAGES_DIR}/*/"):
        dirname = os.path.basename(subdir.rstrip('/'))
        if dirname.startswith('[') or dirname.startswith('_'):
            continue
        index = os.path.join(subdir, 'index.astro')
        if os.path.exists(index):
            pages.append((f'/{dirname}/', 'weekly', '0.9'))
    
    return pages

def get_iv_pages():
    """Get all IV pages from JSON data"""
    pages = []
    for f in sorted(glob.glob(f"{IV_DATA_DIR}/*.json")):
        with open(f) as fh:
            data = json.load(fh)
        slug = data.get('slug', '')
        if slug:
            published = data.get('published', '2026-03-18')
            pages.append((f'/{slug}/', 'monthly', '0.8', published))
    return pages

def main():
    today = datetime.now().strftime('%Y-%m-%d')
    
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    
    # Static pages
    for page in get_astro_pages():
        loc, freq, priority = page[0], page[1], page[2]
        lines.append(f'  <url><loc>{DOMAIN}{loc}</loc><lastmod>{today}</lastmod><changefreq>{freq}</changefreq><priority>{priority}</priority></url>')
    
    # IV pages
    iv_pages = get_iv_pages()
    for page in iv_pages:
        loc, freq, priority, lastmod = page
        lines.append(f'  <url><loc>{DOMAIN}{loc}</loc><lastmod>{lastmod}</lastmod><changefreq>{freq}</changefreq><priority>{priority}</priority></url>')
    
    # Category pages (only if not already in static pages)
    seen = {p[0] for p in get_astro_pages()}
    for cat in ['tools', 'guides', 'lists']:
        if f'/{cat}/' not in seen:
            lines.append(f'  <url><loc>{DOMAIN}/{cat}/</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq><priority>0.9</priority></url>')
    
    lines.append('</urlset>')
    
    with open(OUTPUT, 'w') as f:
        f.write('\n'.join(lines))
    
    total = len(get_astro_pages()) + len(iv_pages) + 4  # +4 for dashboard + categories
    print(f"Generated {OUTPUT}: {total} URLs ({len(get_astro_pages())} static + {len(iv_pages)} IV)")

if __name__ == "__main__":
    main()
