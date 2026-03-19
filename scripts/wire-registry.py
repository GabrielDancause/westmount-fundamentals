#!/usr/bin/env python3
"""
Wire .astro pages to read from pages-registry.json.
Replaces hardcoded meta/title/description/h1 with registry lookups.
"""
import os, re, glob, json

PAGES_DIR = "src/pages"
REGISTRY = "src/data/pages-registry.json"

with open(REGISTRY) as f:
    registry = json.load(f)

def process_file(filepath):
    slug = os.path.basename(filepath).replace('.astro', '')
    
    if slug not in registry:
        return False, "not in registry"
    
    page = registry[slug]
    if 'h1' not in page:
        return False, "no h1 in registry"
    
    with open(filepath) as f:
        content = f.read()
    
    # Skip if already wired
    if 'pages-registry.json' in content:
        return False, "already wired"
    
    # Split into frontmatter and html
    parts = content.split('---', 2)
    if len(parts) < 3:
        return False, "no frontmatter"
    
    frontmatter = parts[1]
    html = parts[2]
    
    original_frontmatter = frontmatter
    original_html = html
    
    # 1. Add registry import (after SiteLayout import)
    if 'import SiteLayout' in frontmatter:
        if 'import registry' not in frontmatter:
            frontmatter = frontmatter.replace(
                'import SiteLayout from "../layouts/SiteLayout.astro";',
                'import SiteLayout from "../layouts/SiteLayout.astro";\nimport registry from "../data/pages-registry.json";\n\nconst page = (registry as any)["' + slug + '"];'
            )
    else:
        return False, "no SiteLayout import"
    
    # 2. Remove export const meta block (if present)
    # Keep it simple - just remove the export const meta
    frontmatter = re.sub(
        r'\nexport\s+const\s+meta\s*=\s*\{[^}]*\};\s*\n',
        '\n',
        frontmatter,
        flags=re.DOTALL
    )
    
    # 3. Replace SiteLayout props - title
    # Pattern: title="..." or title={meta.title} or title={`...`}
    html = re.sub(
        r'title\s*=\s*\{meta\.title\}',
        'title={page.title}',
        html
    )
    html = re.sub(
        r'title\s*=\s*\{`[^`]*`\}',
        'title={page.title}',
        html
    )
    # Only replace title="string" in SiteLayout tag, not in other elements
    def replace_sitelayout_title(match):
        tag = match.group(0)
        tag = re.sub(r'title\s*=\s*"[^"]*"', 'title={page.title}', tag, count=1)
        return tag
    html = re.sub(r'<SiteLayout[^>]*>', replace_sitelayout_title, html, count=1)
    
    # 4. Replace description prop
    html = re.sub(
        r'description\s*=\s*\{meta\.description\}',
        'description={page.description}',
        html
    )
    def replace_sitelayout_desc(match):
        tag = match.group(0)
        tag = re.sub(r'description\s*=\s*"[^"]*"', 'description={page.description}', tag, count=1)
        return tag
    html = re.sub(r'<SiteLayout[^>]*>', replace_sitelayout_desc, html, count=1)
    
    # 5. Replace canonical URL
    html = re.sub(
        r'canonical\s*=\s*"https://westmountfundamentals\.com/[^"]*"',
        'canonical={`https://westmountfundamentals.com/${page.slug}`}',
        html
    )
    
    # 6. Replace H1 content
    h1_text = page.get('h1', '')
    if h1_text:
        # Match <h1>exact text</h1> or <h1 class="...">exact text</h1>
        html = re.sub(
            r'(<h1[^>]*>)' + re.escape(h1_text) + r'(</h1>)',
            r'\1{page.h1}\2',
            html
        )
    
    # Check if anything actually changed
    if frontmatter == original_frontmatter and html == original_html:
        return False, "no changes needed"
    
    # Reassemble
    new_content = '---' + frontmatter + '---' + html
    
    with open(filepath, 'w') as f:
        f.write(new_content)
    
    return True, "wired"

def main():
    files = sorted(glob.glob(f"{PAGES_DIR}/*.astro"))
    
    success = 0
    skipped = {}
    errors = []
    
    for filepath in files:
        slug = os.path.basename(filepath).replace('.astro', '')
        
        # Skip dynamic routes
        if slug.startswith('[') or slug.startswith('_'):
            continue
        
        # Skip dashboard (already custom)
        if 'dashboard' in slug:
            continue
            
        try:
            ok, reason = process_file(filepath)
            if ok:
                success += 1
            else:
                skipped[reason] = skipped.get(reason, 0) + 1
        except Exception as e:
            errors.append((slug, str(e)))
    
    print(f"Wired: {success}")
    print(f"Skipped:")
    for reason, count in sorted(skipped.items()):
        print(f"  {reason}: {count}")
    if errors:
        print(f"Errors ({len(errors)}):")
        for slug, err in errors:
            print(f"  {slug}: {err}")

if __name__ == "__main__":
    main()
