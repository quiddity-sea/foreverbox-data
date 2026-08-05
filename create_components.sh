mkdir -p /var/www/the-foreverbox-institute/interactions/components/{typography,containers,data}

cat > /var/www/the-foreverbox-institute/interactions/components/typography/hero_header.html << 'HEREDOC'
<!-- Hero Header Component -->
<!-- Reference: part1.html header block -->
<header class="relative border-l-4 border-primary-container pl-6 py-2">
    <div class="absolute -left-1.5 top-0 w-2 h-16 bg-primary-container/20 blur-sm"></div>
    <div class="font-code-label text-code-label uppercase text-primary/60 tracking-widest mb-2 flex items-center gap-2">
        <span class="material-symbols-outlined text-sm">{{HERO_ICON}}</span>
        {{SEQUENCE_LABEL}}
    </div>
    <h1 class="font-hero-lg-mobile md:font-hero-lg flex flex-col gap-1">
        <span class="font-semibold text-on-surface">{{TITLE_LINE_1}}</span>
        <span class="font-thin text-primary-fixed tracking-tight">{{TITLE_LINE_2}}</span>
    </h1>
    <p class="text-on-surface-variant text-sm mt-3 italic max-w-2xl">{{SUBTITLE}}</p>
    <div class="flex items-center gap-3 mt-4">
        <span class="font-code-label text-[10px] bg-primary/10 text-primary px-2 py-1 rounded-sm border border-primary/20">{{BADGE_TEXT}}</span>
        <span class="font-code-label text-[10px] text-on-surface-variant/50">{{META_TEXT}}</span>
    </div>
</header>
HEREDOC

cat > /var/www/the-foreverbox-institute/interactions/components/typography/section_header.html << 'HEREDOC'
<!-- Section Header Component -->
<!-- Reference: part1.html section divider pattern -->
<div class="flex items-center justify-between mb-8 border-b border-primary/20 pb-4" id="{{SECTION_ID}}">
    <h3 class="font-anchor-sm text-anchor-sm uppercase tracking-widest text-primary flex items-center gap-2">
        <span class="material-symbols-outlined text-sm">{{ICON_NAME}}</span>
        {{SECTION_TITLE}}
    </h3>
    <div class="font-code-label text-code-label text-on-surface-variant/50">{{NODE_LABEL}}</div>
</div>
HEREDOC

cat > /var/www/the-foreverbox-institute/interactions/components/typography/epigraph_block.html << 'HEREDOC'
<!-- Epigraph Block Component -->
<!-- Reference: part1.html epigraph pattern -->
<div class="glass-panel hud-border p-6 relative overflow-hidden">
    <div class="absolute top-0 left-0 w-1 h-full bg-primary/30"></div>
    <div class="absolute top-2 right-2 font-code-label text-[10px] text-primary/30">SIG: {{SPEAKER_TAG}}</div>
    <p class="text-on-surface leading-relaxed italic text-base pl-3">"{{QUOTE_TEXT}}"</p>
    <p class="text-on-surface-variant text-sm mt-2 pl-3">— {{ATTRIBUTION}}</p>
    <!-- Optional commentary block: include only when needed -->
    <!-- <div class="mt-4 pl-3 border-l-2 border-primary/20 text-on-surface-variant text-sm leading-relaxed">
        <span class="font-code-label text-[10px] text-primary/50 uppercase tracking-wider block mb-1">COMMENTARY</span>
        {{COMMENTARY_TEXT}}
    </div> -->
</div>
HEREDOC

cat > /var/www/the-foreverbox-institute/interactions/components/containers/narrative_card.html << 'HEREDOC'
<!-- Narrative Card Component (Corner-Bracketed HUD Card) -->
<!-- Reference: part1.html, part3.html narrative sections -->
<div class="hud-border p-6 bg-surface-dim/50 backdrop-blur-sm relative">
    <div class="absolute top-0 left-0 w-2 h-2 border-t border-l border-primary-container"></div>
    <div class="absolute top-0 right-0 w-2 h-2 border-t border-r border-primary-container"></div>
    <div class="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-primary-container"></div>
    <div class="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-primary-container"></div>
    <div class="flex items-center gap-2 mb-4">
        <span class="w-2 h-2 rounded-full bg-primary-container animate-pulse shadow-[0_0_8px_rgba(0,255,65,0.8)]"></span>
        <span class="font-code-label text-code-label text-primary/70">{{CARD_TAG}}</span>
    </div>
    <h4 class="font-headline-md text-headline-md font-semibold text-primary mb-4 flex items-center gap-2">
        <span class="w-1.5 h-6 bg-primary inline-block"></span>
        {{CARD_TITLE}}
    </h4>
    <div class="text-on-surface-variant leading-relaxed text-sm space-y-3">
        {{CARD_CONTENT}}
    </div>
</div>
HEREDOC

cat > /var/www/the-foreverbox-institute/interactions/components/containers/tech_card.html << 'HEREDOC'
<!-- Tech Specification Card Component -->
<!-- Reference: part3.html topology node cards, part4.html quadrant cards -->
<div class="hud-border bg-surface-container/30 hover:bg-surface-container/50 transition-colors duration-300 relative group overflow-hidden">
    <div class="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-primary-container to-transparent"></div>
    <div class="absolute top-0 left-0 w-2 h-2 border-t border-l border-primary-container"></div>
    <div class="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-primary-container"></div>
    <!-- Optional: large watermark background icon -->
    <!-- <span class="absolute top-3 right-3 opacity-5 group-hover:opacity-15 transition-opacity material-symbols-outlined text-6xl text-primary">{{WATERMARK_ICON}}</span> -->
    <div class="p-6 relative z-10">
        <div class="flex justify-between items-start mb-4">
            <h4 class="font-anchor-sm text-primary flex items-center gap-2">
                <span class="material-symbols-outlined text-sm">{{CARD_ICON}}</span>
                {{CARD_TITLE}}
            </h4>
            <span class="font-code-label text-[10px] text-primary/50">{{NODE_ID}}</span>
        </div>
        <p class="text-on-surface-variant text-sm leading-relaxed mb-4">{{CARD_DESCRIPTION}}</p>
        <div class="space-y-2 font-code-label text-code-label">
            {{KEY_VALUE_ROWS}}
            <!-- Each row: <div class="flex justify-between border-b border-outline-variant/30 pb-1.5"><span class="text-on-surface-variant/70">KEY</span><span class="text-primary">VALUE</span></div> -->
        </div>
        <div class="mt-4 pt-3 border-t border-primary/10">
            <span class="text-[10px] uppercase tracking-wider bg-primary/10 border border-primary/20 px-1.5 py-0.5 text-primary inline-block font-code-label">{{STATUS_TAG}}</span>
        </div>
    </div>
</div>
HEREDOC

cat > /var/www/the-foreverbox-institute/interactions/components/containers/glass_panel.html << 'HEREDOC'
<!-- Glass Panel Component -->
<!-- Reference: part4.html Voice DNA panel, part5.html Wolf Protocol -->
<div class="hud-border glass-panel p-6 md:p-8 hud-glow relative">
    <div class="absolute top-2 right-3 font-code-label text-[10px] text-primary/50">{{PANEL_TAG}}</div>
    <div class="flex items-center gap-2 mb-4">
        <span class="material-symbols-outlined text-primary-container">{{PANEL_ICON}}</span>
        <h4 class="font-anchor-sm text-primary">{{PANEL_TITLE}}</h4>
    </div>
    <div class="text-on-surface-variant text-sm leading-relaxed">
        {{PANEL_BODY}}
    </div>
</div>
HEREDOC

cat > /var/www/the-foreverbox-institute/interactions/components/containers/image_frame.html << 'HEREDOC'
<!-- HUD Image Frame Component -->
<!-- Reference: part3.html target-reticle image viewport -->
<div class="relative group">
    <div class="absolute inset-0 hud-border-active -m-4 pointer-events-none opacity-20 group-hover:opacity-100 transition-opacity duration-500">
        <div class="absolute top-0 left-0 w-8 h-8 border-t-2 border-l-2 border-primary-container"></div>
        <div class="absolute top-0 right-0 w-8 h-8 border-t-2 border-r-2 border-primary-container"></div>
        <div class="absolute bottom-0 left-0 w-8 h-8 border-b-2 border-l-2 border-primary-container"></div>
        <div class="absolute bottom-0 right-0 w-8 h-8 border-b-2 border-r-2 border-primary-container"></div>
        <div class="absolute top-2 right-2 font-code-label text-[10px] text-primary/50">{{IMAGE_REF}}</div>
        <div class="absolute bottom-2 left-2 font-code-label text-[10px] text-primary/50">{{IMAGE_LAYER}}</div>
    </div>
    <div class="relative overflow-hidden bg-surface-container-highest hud-glow aspect-[1.50]">
        <div class="absolute inset-0 bg-cover bg-center mix-blend-luminosity opacity-70" style="background-image: url('{{IMAGE_SRC}}')"></div>
        <div class="absolute inset-0 bg-[linear-gradient(rgba(0,255,65,0.05)_1px,transparent_1px)] bg-[size:100%_4px] pointer-events-none"></div>
    </div>
</div>
HEREDOC

cat > /var/www/the-foreverbox-institute/interactions/components/data/code_block.html << 'HEREDOC'
<!-- Code Block Component (HUD Terminal Style) -->
<!-- Reference: part3.html terminal window block -->
<div class="hud-border bg-surface-dim/50 backdrop-blur-sm relative overflow-hidden">
    <div class="absolute top-0 right-0 w-1/2 h-[1px] bg-gradient-to-l from-primary-container to-transparent"></div>
    <div class="flex items-center justify-between px-4 py-2 border-b border-primary/20">
        <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-primary-container"></span>
            <span class="font-code-label text-code-label text-primary/70">{{CODE_TITLE}}</span>
        </div>
        <span class="font-code-label text-[10px] text-on-surface-variant/50 uppercase">{{LANG_LABEL}}</span>
    </div>
    <pre class="bg-[#05090c] border border-primary/20 p-4 font-code-label text-code-label overflow-x-auto text-primary"><code>{{CODE_CONTENT}}</code></pre>
</div>
HEREDOC

cat > /var/www/the-foreverbox-institute/interactions/components/data/data_table.html << 'HEREDOC'
<!-- Data Table Component -->
<!-- Reference: part3.html memory layer table, part5.html signal matrix -->
<div class="hud-border glass-panel p-6 md:p-8 hud-glow relative">
    <div class="absolute top-2 right-3 font-code-label text-[10px] text-primary/50">{{TABLE_TAG}}</div>
    <div class="overflow-x-auto">
        <table class="w-full text-sm">
            <thead>
                <tr class="border-b border-primary/30 text-left">
                    {{TABLE_HEADERS}}
                    <!-- Each: <th class="p-3 font-code-label text-primary text-xs uppercase tracking-wider">HEADER</th> -->
                </tr>
            </thead>
            <tbody>
                {{TABLE_ROWS}}
                <!-- Each: <tr class="border-b border-primary/10 hover:bg-primary/5 transition-colors">
                    <td class="p-3 font-code-label text-primary/70">KEY</td>
                    <td class="p-3">VALUE</td>
                </tr> -->
            </tbody>
        </table>
    </div>
</div>
HEREDOC

cat > /var/www/the-foreverbox-institute/interactions/components/data/status_badge.html << 'HEREDOC'
<!-- Status Badge Component -->
<!-- Reference: part3.html, part5.html, part6.html -->
<!-- Variant: Primary (default) -->
<!-- <span class="font-code-label text-[10px] bg-primary/10 text-primary px-2 py-1 rounded-sm border border-primary/20">{{BADGE_TEXT}}</span> -->

<!-- Variant: Active (filled green) -->
<!-- <span class="bg-primary-container text-on-primary-container px-2 py-0.5 rounded-sm text-[11px] font-code-label">{{BADGE_TEXT}}</span> -->

<!-- Variant: Secondary (green accent) -->
<!-- <span class="font-code-label text-[10px] bg-secondary-container text-on-secondary-container px-2 py-1 rounded-sm border border-secondary/20">{{BADGE_TEXT}}</span> -->

<!-- Variant: Outline -->
<!-- <span class="border border-primary/50 text-primary px-2 py-0.5 rounded-sm text-[11px] font-code-label">{{BADGE_TEXT}}</span> -->

<!-- Variant: Inline tag -->
<span class="text-[10px] uppercase tracking-wider bg-primary/10 border border-primary/20 px-1.5 py-0.5 text-primary inline-block font-code-label">{{BADGE_TEXT}}</span>
HEREDOC

cat > /var/www/the-foreverbox-institute/interactions/components/containers/vertical_step_list.html << 'HEREDOC'
<!-- Vertical Step List Component -->
<!-- Reference: part5.html waterfall method, part6.html dialectic mix -->
<div class="space-y-3">
    <!-- Each step row: -->
    <!-- <div class="flex gap-4 items-start border-l border-primary/20 pl-4 py-2">
        <div class="font-code-label text-primary opacity-70 w-32 shrink-0 text-xs">{{STEP_LABEL}}</div>
        <p class="text-sm text-on-surface-variant leading-relaxed">{{STEP_DESCRIPTION}}</p>
    </div> -->
    {{STEP_ROWS}}
</div>
HEREDOC

cat > /var/www/the-foreverbox-institute/interactions/components/containers/status_banner.html << 'HEREDOC'
<!-- Status Banner Component -->
<!-- Reference: part5.html coloured status update banners -->
<!-- Variant: Secondary (green update) -->
<div class="hud-border p-6 bg-surface-container/30 relative border-l-4 border-secondary">
    <div class="absolute top-0 right-0 w-2 h-2 border-t border-r border-secondary/50"></div>
    <h4 class="font-anchor-sm text-secondary mb-2 flex items-center gap-2">
        <span class="material-symbols-outlined text-sm">{{BANNER_ICON}}</span>
        {{BANNER_TITLE}}
    </h4>
    <div class="text-on-surface-variant text-sm leading-relaxed">
        {{BANNER_CONTENT}}
    </div>
</div>

<!-- Variant: Error (red alert) -->
<!-- Change border-secondary to border-error, text-secondary to text-error, border-secondary/50 to border-error/50 -->
HEREDOC

cat > /var/www/the-foreverbox-institute/interactions/components/containers/toc_link_card.html << 'HEREDOC'
<!-- Table of Contents Link Card Component -->
<!-- Reference: index.html TOC grid cards -->
<div class="border border-outline-variant/50 bg-surface-container-high/30 hover:border-primary/30 transition-all p-5">
    <h3 class="font-anchor-sm text-lg text-on-surface mb-3 border-b border-primary/20 pb-2">
        <a href="{{LINK_URL}}">{{PART_TITLE}}</a>
    </h3>
    <ol class="space-y-1.5 font-code-label text-[0.75rem]">
        {{LINK_ITEMS}}
        <!-- Each: <li><a href="{{ITEM_URL}}" class="text-on-surface-variant hover:text-primary no-underline transition-colors">{{ITEM_TEXT}}</a></li> -->
        <!-- Sub-items: <li class="ml-4"><a href="{{SUB_URL}}" class="text-on-surface-variant/70 hover:text-primary no-underline transition-colors">{{SUB_TEXT}}</a></li> -->
    </ol>
</div>
HEREDOC

cat > /var/www/the-foreverbox-institute/interactions/components/containers/hover_reticle.html << 'HEREDOC'
<!-- Hover Target Reticle Overlay Component -->
<!-- Reference: part3.html, part4.html target-reticle patterns -->
<!-- Wrap around any card or image to add tactical HUD hover brackets -->
<div class="absolute inset-0 hud-border-active -m-4 pointer-events-none opacity-20 group-hover:opacity-100 transition-opacity duration-500">
    <div class="absolute top-0 left-0 w-8 h-8 border-t-2 border-l-2 border-primary-container"></div>
    <div class="absolute top-0 right-0 w-8 h-8 border-t-2 border-r-2 border-primary-container"></div>
    <div class="absolute bottom-0 left-0 w-8 h-8 border-b-2 border-l-2 border-primary-container"></div>
    <div class="absolute bottom-0 right-0 w-8 h-8 border-b-2 border-r-2 border-primary-container"></div>
    <div class="absolute top-2 right-2 font-code-label text-[10px] text-primary/50">{{RETICLE_REF}}</div>
    <div class="absolute bottom-2 left-2 font-code-label text-[10px] text-primary/50">{{RETICLE_LAYER}}</div>
</div>
HEREDOC

cat > /var/www/the-foreverbox-institute/interactions/components/data/compilation_footer.html << 'HEREDOC'
<!-- Compilation Footer Marker Component -->
<!-- Reference: part4.html end-of-page marker -->
<div class="mt-20 mb-12 text-center">
    <div class="font-code-label text-code-label text-on-surface-variant/50 border-t border-primary/10 pt-6">
        {{FOOTER_TEXT}}
    </div>
</div>
HEREDOC

ls -la /var/www/the-foreverbox-institute/interactions/components/typography/ /var/www/the-foreverbox-institute/interactions/components/containers/ /var/www/the-foreverbox-institute/interactions/components/data/
