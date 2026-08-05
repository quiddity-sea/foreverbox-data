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
    pattern_to_remove = r'<!-- NAVIGATION INJECTION POINT -->\s*<div id="foreverbox-nav">\s*</div>\s*'
    body_content = re.sub(pattern_to_remove, '', body_content, flags=re.DOTALL)
    
    # Extract the intro: first h2 and the next p
    h2_match = re.search(r'<h2[^>]*>(.*?)</h2>', body_content, re.DOTALL)
    if not h2_match:
        print("Could not find h2 in body content")
        sys.exit(1)
    h2_tag = h2_match.group(0)
    h2_title = h2_match.group(1).strip()
    
    h2_end = h2_match.end()
    p_match = re.search(r'<p[^>]*>(.*?)</p>', body_content[h2_end:], re.DOTALL)
    if not p_match:
        print("Could not find p after h2")
        sys.exit(1)
    p_tag = p_match.group(0)
    p_inner = p_match.group(1).strip()  # This includes inner HTML, e.g., <em>...</em>
    
    # Remove the h2 and p tags from the body_content
    body_content = body_content.replace(h2_tag, '', 1)
    body_content = body_content.replace(p_tag, '', 1)
    
    # Now extract all sections: each section is an h3 tag with an id, then the title, then content until next h3 or end
    # We use a regex to match: <h3([^>]*id="([^"]*)"[^>]*>([^<]*)</h3>(.*?)(?=<h3|$))
    # We use re.DOTALL so that . matches newlines
    pattern = r'<h3[^>]*id="([^"]*)"[^>]*>([^<]*)</h3>(.*?)(?=<h3|$)'
    matches = re.findall(pattern, body_content, re.DOTALL)
    
    if not matches:
        print("No sections found")
        sys.exit(1)
    
    # Map section ids to icons
    icon_map = {
        'part7-24': 'foundation',
        'part7-25': 'hub',
        'part7-26': 'router',
        'part7-27': 'palette',
        'part7-28': 'devices',
        'part7-29': 'verified'
    }
    
    section_htmls = []
    for section_id, title, content in matches:
        # Process the content: wrap <pre> tags in a div with class="glass-panel" data-node="code"
        processed_content = re.sub(r'<pre([^>]*)>', r'<div class="glass-panel" data-node="code"><pre\1>', content)
        processed_content = re.sub(r'</pre>', r'</pre></div>', processed_content)
        
        # Get the icon
        icon = icon_map.get(section_id, 'widgets')
        
        # Build the section HTML
        section_html = f'''
        <section id="{section_id}" class="mb-12 hud-border bg-surface-container-low/30 p-6 md:p-8 relative overflow-hidden backdrop-blur-md">
            <div class="absolute top-0 right-0 p-4 opacity-20">
                <span class="material-symbols-outlined text-6xl text-primary">{icon}</span>
            </div>
            <h2 class="font-headline-md text-headline-md text-primary font-semibold mb-4 border-b border-primary/20 pb-2 inline-block">{title.strip()}</h2>
            {processed_content}
        </section>
        '''
        section_htmls.append(section_html)
    
    # Build the hero from the current part7.html's hero, but replace the p content with p_inner
    hero_match = re.search(r'<header class="mb-12 border-b border-outline-variant/30 pb-6">(.*?)</header>', current_content, re.DOTALL)
    if not hero_match:
        print("Could not find hero in current part7.html")
        sys.exit(1)
    hero_content = hero_match.group(1)
    
    # Replace the p tag's content in the hero_content
    p_in_hero = re.search(r'<p class="font-code-label text-code-label text-on-surface-variant max-w-2xl">(.*?)</p>', hero_content, re.DOTALL)
    if not p_in_hero:
        print("Could not find p in hero")
        sys.exit(1)
    # Replace the content inside the p tag with p_inner
    new_hero_content = hero_content.replace(p_in_hero.group(1), p_inner, 1)
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