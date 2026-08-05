#!/usr/bin/env python3
import re
import sys

def main():
    # Read the current part7.html to get the head
    current_part7_path = '/var/www/the-foreverbox-institute/history/Stich-Project/stitch_project_repository_analyzer/part7.html'
    with open(current_part7_path, 'r') as f:
        current_content = f.read()
    
    # Extract the head from the current part7.html
    head_match = re.search(r'<head>(.*?)</head>', current_content, re.DOTALL)
    if not head_match:
        print("Could not find head in current part7.html")
        sys.exit(1)
    head_content = head_match.group(1)
    
    # Read the source file
    source_path = '/var/www/the-foreverbox-institute/history/the-project/part7-build-manual.html'
    with open(source_path, 'r') as f:
        source_content = f.read()
    
    # Extract the body content from the source file
    body_match = re.search(r'<body>(.*?)</body>', source_content, re.DOTALL)
    if not body_match:
        print("Could not find body in source file")
        sys.exit(1)
    body_content = body_match.group(1)
    
    # Remove the NAVIGATION INJECTION POINT comment and the foreverbox-nav div
    # We remove the exact pattern: comment followed by the div
    pattern_to_remove = r'<!-- NAVIGATION INJECTION POINT -->\s*<div id="foreverbox-nav">\s*</div>\s*'
    body_content = re.sub(pattern_to_remove, '', body_content, flags=re.DOTALL)
    
    # Now, extract the intro: first h2 and the next p
    # We look for the first h2
    h2_match = re.search(r'<h2[^>]*>(.*?)</h2>', body_content, re.DOTALL)
    if not h2_match:
        print("Could not find h2 in body content")
        sys.exit(1)
    h2_tag = h2_match.group(0)  # the entire h2 tag
    h2_title = h2_match.group(1).strip()  # the text inside
    
    # Look for the first p after the h2
    # We search for <p after the end of the h2 tag
    h2_end = h2_match.end()
    p_match = re.search(r'<p[^>]*>(.*?)</p>', body_content[h2_end:], re.DOTALL)
    if not p_match:
        print("Could not find p after h2")
        sys.exit(1)
    p_tag = p_match.group(0)  # the entire p tag
    p_inner = p_match.group(1).strip()  # the inner HTML of the p tag
    
    # We'll use the p_inner to replace the hero's p content later
    # Remove the h2 and p from the body_content
    # We remove the h2_tag and the p_tag (only the first occurrence of each)
    body_content = body_content.replace(h2_tag, '', 1)
    body_content = body_content.replace(p_tag, '', 1)
    
    # Now, split the remaining content by '<h3' to get sections
    # We split by '<h3' but we want to keep the delimiter for processing
    sections = re.split(r'(<h3[^>]*>)', body_content)
    # The split will give us: [text_before_first_h3, h3_tag1, content_after_h3_until_next_h3, h3_tag2, ...]
    # We ignore the text before the first h3 (should be empty or whitespace)
    
    # Process each section
    section_htmls = []
    icon_map = {
        'part7-24': 'foundation',
        'part7-25': 'hub',
        'part7-26': 'router',
        'part7-27': 'palette',
        'part7-28': 'devices',
        'part7-29': 'verified'
    }
    
    # We'll iterate over the sections list in steps of 2: [tag, content, tag, content, ...]
    # But note: the first element might be text before the first h3
    i = 0
    if sections[0].strip():
        # There is text before the first h3, we treat it as a section without a title? 
        # But we expect the first to be empty or whitespace because we removed the intro.
        # We'll skip it if it's empty.
        pass
    
    for i in range(1, len(sections), 2):
        if i+1 >= len(sections):
            break
        h3_tag = sections[i]
        content = sections[i+1]
        
        # Extract id from h3_tag
        id_match = re.search(r'id="([^"]*)"', h3_tag)
        if not id_match:
            # Skip if no id
            continue
        id_value = id_match.group(1)
        
        # Extract the title from the h3_tag: it's the text between > and <
        # The h3_tag is like: <h3 id="part7-24">24. Phase 1: Foundation</h3>
        # But note: we split at the opening tag, so the h3_tag is the opening tag only.
        # The title is not in the h3_tag, it's in the content until the first '<' (which would be the start of a tag or the closing h3)
        # We need to extract the title from the content: it's the text until the first '<'
        title_end = content.find('<')
        if title_end == -1:
            title = content.strip()
            rest = ''
        else:
            title = content[:title_end].strip()
            rest = content[title_end:]
        
        # Process the rest: wrap <pre> tags in a div with class="glass-panel" and data-node="code"
        # We replace <pre with <div class="glass-panel" data-node="code"><pre
        # and </pre> with </pre></div>
        processed_rest = re.sub(r'<pre([^>]*)>', r'<div class="glass-panel" data-node="code"><pre\1>', rest)
        processed_rest = re.sub(r'</pre>', r'</pre></div>', processed_rest)
        
        # Get the icon
        icon = icon_map.get(id_value, 'widgets')
        
        # Build the section HTML
        section_html = f'''
        <section id="{id_value}" class="mb-12 hud-border bg-surface-container-low/30 p-6 md:p-8 relative overflow-hidden backdrop-blur-md">
            <div class="absolute top-0 right-0 p-4 opacity-20">
                <span class="material-symbols-outlined text-6xl text-primary">{icon}</span>
            </div>
            <h2 class="font-headline-md text-headline-md text-primary font-semibold mb-4 border-b border-primary/20 pb-2 inline-block">{title}</h2>
            {processed_rest}
        </section>
        '''
        section_htmls.append(section_html)
    
    # Build the hero
    # We reuse the hero structure from the current part7.html, but we replace the p content with p_inner
    # Extract the hero from the current part7.html
    # The hero in the current part7.html is:
    # <header class="mb-12 border-b border-outline-variant/30 pb-6">
    #   <div class="flex items-center gap-4 mb-4">
    #     <span class="font-code-label text-code-label bg-surface-variant text-primary px-2 py-1 rounded border border-outline-variant">DOC_ID: 9942</span>
    #     <span class="font-code-label text-code-label text-on-surface-variant/70 flex items-center gap-2">
    #       <span class="material-symbols-outlined text-[14px]">update</span> LAST_MOD: 2026.07.12
    #     </span>
    #   </div>
    #   <h1 class="font-headline-md text-headline-md text-primary tracking-tight mb-2">PART VII: BUILD MANUAL</h1>
    #   <p class="font-code-label text-code-label text-on-surface-variant max-w-2xl">
    #     Technical schematics and implementation phases for the primary containment architecture. Proceed with caution.
    #   </p>
    # </header>
    #
    # We want to replace the p tag's content with p_inner, but keep the rest.
    hero_match = re.search(r'<header class="mb-12 border-b border-outline-variant/30 pb-6">(.*?)</header>', current_content, re.DOTALL)
    if not hero_match:
        print("Could not find hero in current part7.html")
        sys.exit(1)
    hero_content = hero_match.group(1)
    # Now, replace the p tag's content in the hero_content
    # We look for the p tag in the hero_content
    p_in_hero = re.search(r'<p class="font-code-label text-code-label text-on-surface-variant max-w-2xl">(.*?)</p>', hero_content, re.DOTALL)
    if not p_in_hero:
        print("Could not find p in hero")
        sys.exit(1)
    # Replace the content inside the p tag
    new_hero_content = hero_content.replace(p_in_hero.group(1), p_inner, 1)
    # Rebuild the hero
    hero = f'<header class="mb-12 border-b border-outline-variant/30 pb-6">{new_hero_content}</header>'
    
    # Build the full HTML
    html = f'''<!DOCTYPE html>
<html class="dark" lang="en">
<head>
{head_content}
</head>
<body class="bg-background text-on-surface font-body-md overflow-x-hidden selection:bg-primary-container selection:text-on-primary-container min-h-screen flex flex-col relative">
<div class="fixed inset-0 pointer-events-none z-[-1] bg-surface-container-lowest opacity-90"></div>
<div class="fixed inset-0 pointer-events-none z-[-1] hud-scanline"></div>
<div id="fb-header"></div>
<div id="fb-sidenav" class="flex flex-1 pt-16"></div>
<main class="flex-1 md:ml-64 p-margin-safe max-w-container-max mx-auto w-full">
{hero}
{''.join(section_htmls)}
</main>
<div id="fb-footer"></div>
<script src="assets/nav.js"></script>
</body>
</html>'''
    
    # Write the new part7.html
    output_path = '/var/www/the-foreverbox-institute/history/Stich-Project/stitch_project_repository_analyzer/part7.html'
    with open(output_path, 'w') as f:
        f.write(html)
    
    print("Successfully rebuilt part7.html")

if __name__ == '__main__':
    main()