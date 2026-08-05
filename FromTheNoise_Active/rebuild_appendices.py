import re

def main():
    # Read the source file
    source_path = '/var/www/the-foreverbox-institute/history/the-project/appendices.html'
    with open(source_path, 'r') as f:
        source_content = f.read()
    
    # Extract content between <!-- APPENDICES --> and </body>
    start_marker = '<!-- APPENDICES -->'
    end_marker = '</body>'
    
    start_index = source_content.find(start_marker)
    if start_index == -1:
        print("Error: Could not find start marker")
        return
    start_index += len(start_marker)
    
    end_index = source_content.find(end_marker, start_index)
    if end_index == -1:
        print("Error: Could not find end marker")
        return
    
    extracted = source_content[start_index:end_index].strip()
    
    # Remove the ending paragraph, footer, and script
    # We'll remove from the ending paragraph to the end of the extracted string.
    # Pattern for the ending paragraph
    end_para_pattern = r'<p style="margin-top:2rem;"><em>End of Appendices\. The ForeverBox document is complete\.<\/em><\/p>\s*'
    # Pattern for the footer
    footer_pattern = r'<footer>[\s\S]*?<\/footer>\s*'
    # Pattern for the script
    script_pattern = r'<script src="assets/nav\.js"><\/script>\s*'
    
    # Combine the patterns to remove the entire block
    combined_pattern = end_para_pattern + footer_pattern + script_pattern
    # Apply the pattern
    cleaned = re.sub(combined_pattern, '', extracted, flags=re.DOTALL)
    
    # Now we have the content from <!-- APPENDICES --> to before the ending paragraph.
    # We'll split this content into sections by <h3 id="appendix-">
    # But we want to keep the h2 and p that come before the first appendix.
    # Let's split by the pattern that matches the appendix headers.
    
    # First, let's extract the intro (everything before the first appendix header)
    intro_match = re.search(r'(.*?)(<h3 id="appendix-[a-z]">)', cleaned, re.DOTALL)
    if intro_match:
        intro = intro_match.group(1)
        rest = cleaned[intro_match.end():]
    else:
        intro = cleaned
        rest = ''
    
    # Now split the rest by the appendix headers, but we want to keep the headers.
    # We'll split by the pattern that matches the header and keep the delimiter.
    parts = re.split(r'(<h3 id="appendix-[a-z]">)', rest)
    
    # Rebuild the sections: each section is a header plus the following text until the next header.
    sections = []
    i = 0
    while i < len(parts):
        if i % 2 == 0:
            # This is text between headers (or before the first header if we started with text)
            # But note: after splitting, the first part might be empty if the string starts with a header.
            # We'll ignore empty parts.
            if parts[i].strip():
                # This shouldn't happen in our split because we split on the header and then the text.
                # Actually, the split will give: [text_before_first_header, header1, text_after_header1_until_next_header, header2, ...]
                # So the even indices are the text between headers.
                # We'll attach this text to the previous header? Let's change approach.
                pass
            i += 1
        else:
            # This is a header
            header = parts[i]
            # The next part is the text until the next header (or end)
            if i+1 < len(parts):
                text = parts[i+1]
                section = header + text
                sections.append(section)
                i += 2
            else:
                # Last header with no following text
                sections.append(header)
                i += 1
    
    # Process the intro: we want to make it a hero.
    # Remove the chapter-marker div
    intro = re.sub(r'<div class="chapter-marker">[^<]+</div>\s*', '', intro)
    # Change h2 to h1
    intro = re.sub(r'<h2>', '<h1>', intro)
    intro = re.sub(r'</h2>', '</h1>', intro)
    
    # Build the hero div
    hero = f'''<div class="hud-border" style="border-left: 4px solid hsl(var(--primary-container)); position: relative;">
  <div class="absolute left-0 top-0 h-full w-2 bg-primary-container/20"></div>
  <div class="relative p-6">
    {intro.strip()}
    <span class="inline-flex items-center px-3 py-1 mb-4 text-xs font-semibold tracking-wider text-primary-container bg-primary/20 rounded-full" data-node="header">
      INITIALIZATION_SEQUENCE
    </span>
  </div>
</div>'''
    
    # Process each section: wrap code blocks and tables in glass-panel with data-node
    processed_sections = []
    for section in sections:
        # Wrap code blocks
        # We need to replace <pre><code> with <div class="glass-panel" data-node="code-block"><pre><code>
        # and </code></pre> with </code></pre></div>
        # Use regex to allow for possible whitespace inside the tags? Actually the tags are exactly as written.
        section = re.sub(r'(<pre><code>)', r'<div class="glass-panel" data-node="code-block">\1', section)
        section = re.sub(r'(</code></pre>)', r'\1</div>', section)
        # Wrap tables: match <table ...>
        section = re.sub(r'(<table[^>]*>)', r'<div class="glass-panel" data-node="table">\1', section)
        section = re.sub(r'(</table>)', r'\1</div>', section)
        # Wrap the entire section in a hud-border div
        wrapped = f'''<div class="hud-border" style="border-left: 4px solid hsl(var(--primary-container)); position: relative; margin: 2rem 0;">
  <div class="absolute left-0 top-0 h-full w-2 bg-primary-container/20"></div>
  <div class="relative p-6">
    {section.strip()}
  </div>
</div>'''
        processed_sections.append(wrapped)
    
    # Combine everything
    main_content = hero + '\n' + '\n'.join(processed_sections)
    
    # Now, read the target file
    target_path = '/var/www/the-foreverbox-institute/history/Stich-Project/stitch_project_repository_analyzer/appendices.html'
    with open(target_path, 'r') as f:
        target_content = f.read()
    
    # Replace the content of the main tag
    main_open = '<main class="flex-1 md:ml-64 p-margin-safe max-w-container-max mx-auto w-full">'
    main_close = '</main>'
    
    start_main = target_content.find(main_open)
    if start_main == -1:
        print("Error: Could not find main open")
        return
    start_main += len(main_open)
    
    end_main = target_content.find(main_close, start_main)
    if end_main == -1:
        print("Error: Could not find main close")
        return
    
    # Build the new target content
    new_target = target_content[:start_main] + '\n' + main_content + '\n' + target_content[end_main:]
    
    # Write the target file
    with open(target_path, 'w') as f:
        f.write(new_target)
    
    print("Successfully rebuilt appendices.html")

if __name__ == '__main__':
    main()