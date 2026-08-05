# Part 7 (Build Manual) Rebuild — Component-Based Approach

**Design Ancestor**: Part 1 (The Mythic Frame) — narrative/procedural content

## Content Structure

Part 7 covers the Build Manual with 6 major phases:
- 24. Phase 1: Foundation (Tailscale, MariaDB Galera, Vector Primer, Core DB, Projects DB)
- 25. Phase 2: The Hub
- 26. Phase 3: The Relay
- 27. Phase 4: The Art Studio
- 28. Phase 5: Edge Clients
- 29. Phase 6: Verification

Each phase contains multiple sub-sections with technical instructions, code blocks, and configuration snippets.

## Component Patterns Applied

### Hero Section
```html
<header class="relative border-l-4 border-primary-container pl-6 py-2">
  <div class="absolute -left-1.5 top-0 w-2 h-16 bg-primary-container/20 blur-sm"></div>
  <div class="font-code-label text-code-label uppercase text-primary/60 tracking-widest mb-2 flex items-center gap-2">
    <span class="material-symbols-outlined text-sm">construction</span>
    INITIALIZATION_SEQUENCE
  </div>
  <h1 class="font-hero-lg-mobile md:font-hero-lg flex flex-col gap-1">
    <span class="font-semibold text-on-surface">PART VII</span>
    <span class="font-thin text-primary-fixed tracking-tight">BUILD MANUAL</span>
  </h1>
  <p class="text-on-surface-variant text-sm mt-3 italic">In which I, Zeon7, provide the complete instructions for constructing the Swarm of Mites in Merrill's world. Every command. Every config. Every table. Every explanation.</p>
</header>
```

### Phase Sections (24–29)
Each major phase wrapped in a `hud-border` section with corner accents:

```html
<section id="part7-24" class="mt-20">
  <div class="flex items-center justify-between mb-8 border-b border-primary/20 pb-4">
    <h3 class="font-anchor-sm text-anchor-sm uppercase tracking-widest text-primary flex items-center gap-2">
      <span class="material-symbols-outlined text-sm">construction</span>
      PHASE 1: FOUNDATION
    </h3>
    <div class="font-code-label text-code-label text-on-surface-variant/50">STEP 1 OF 6</div>
  </div>

  <div class="space-y-12">
    <!-- Sub-section 24.1 Tailscale -->
    <section id="part7-24-1" class="hud-border p-6 bg-surface-dim/50 backdrop-blur-sm relative">
      <div class="absolute top-0 left-0 w-2 h-2 border-t border-l border-primary-container"></div>
      <div class="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-primary-container"></div>
      
      <h4 id="part7-24-1" class="font-headline-md text-headline-md font-semibold text-primary mb-4 flex items-center gap-2">
        <span class="w-1.5 h-6 bg-primary inline-block"></span>
        24.1 Tailscale on All Nodes
      </h4>
      
      <p class="text-on-surface-variant leading-relaxed text-sm mb-4">
        The Swarm of Mites is a distributed system. Machines in Wales, Germany, and Gloucestershire must communicate securely as if they were on the same local network. Tailscale creates this mesh.
      </p>
      
      <!-- Explanation paragraphs... -->
      
      <!-- Numbered Steps -->
      <ol class="space-y-6">
        <li>
          <strong>Install Tailscale.</strong> On each node (Wales Hub, Germany VPS, Gloucestershire backup, Art Studio, Development Claw), run:
          <div class="code-block mt-2">
            <div class="font-code-label text-[10px] text-primary/50 absolute top-2 right-2">DATA_NODE: CFG-001</div>
            <pre><code>curl -fsSL https://tailscale.com/install.sh | sh</code></pre>
          </div>
        </li>
        <!-- ... more steps -->
      </ol>
    </section>
    
    <!-- Sub-section 24.2 MariaDB Galera Cluster -->
    <section id="part7-24-2" class="hud-border p-6 bg-surface-dim/50 backdrop-blur-sm relative">
      <div class="absolute top-0 right-0 w-2 h-2 border-t border-r border-primary-container"></div>
      <div class="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-primary-container"></div>
      
      <h4 id="part7-24-2" class="font-headline-md text-headline-md font-semibold text-primary mb-4 flex items-center gap-2">
        <span class="w-1.5 h-6 bg-primary inline-block"></span>
        24.2 MariaDB Galera Cluster
      </h4>
      
      <!-- Explanation... -->
      
      <!-- Configuration Table -->
      <div class="data-table mt-6">
        <table class="w-full font-code-label text-code-label text-left border-collapse">
          <thead>
            <tr class="border-b border-primary/30 text-on-surface-variant">
              <th class="py-2 px-4 font-normal text-left">NODE</th>
              <th class="py-2 px-4 font-normal text-left">TAILSCALE IP</th>
              <th class="py-2 px-4 font-normal text-left">ROLE</th>
            </tr>
          </thead>
          <tbody>
            <tr class="border-b border-outline-variant/20 hover:bg-primary/5 transition-colors">
              <td class="py-3 px-4 text-primary">Wales Hub</td>
              <td class="py-3 px-4 text-on-surface-variant">100.80.92.10</td>
              <td class="py-3 px-4"><span class="bg-primary-container text-black px-2 py-0.5 rounded-sm">PRIMARY</span></td>
            </tr>
            <tr class="border-b border-outline-variant/20 hover:bg-primary/5 transition-colors">
              <td class="py-3 px-4 text-primary">Germany VPS</td>
              <td class="py-3 px-4 text-on-surface-variant">100.120.45.67</td>
              <td class="py-3 px-4"><span class="border border-primary/50 text-primary px-2 py-0.5 rounded-sm">SECONDARY</span></td>
            </tr>
            <tr class="hover:bg-primary/5 transition-colors">
              <td class="py-3 px-4 text-primary">Gloucestershire</td>
              <td class="py-3 px-4 text-on-surface-variant">100.75.33.21</td>
              <td class="py-3 px-4"><span class="border border-primary/50 text-primary px-2 py-0.5 rounded-sm">ARBITER</span></td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- Config File Block -->
      <div class="code-block mt-6">
        <div class="font-code-label text-[10px] text-primary/50 absolute top-2 right-2">DATA_NODE: CFG-002</div>
        <pre><code>[mysqld]
# Network
bind-address = 0.0.0.0

# InnoDB settings required for Galera
binlog_format = ROW
default_storage_engine = InnoDB
innodb_autoinc_lock_mode = 2
innodb_flush_log_at_trx_commit = 0
innodb_buffer_pool_size = 2G

# Galera Provider
wsrep_on = ON
wsrep_provider = /usr/lib/galera/libgalera_smm.so

# Cluster Address - Tailscale IPs of all three nodes
wsrep_cluster_address = "gcomm://100.80.92.10,100.120.45.67,100.75.33.21"
wsrep_cluster_name = "swarm_memory_matrix"

# Node-specific settings - CHANGE THESE PER NODE
wsrep_node_address = "100.80.92.10"   # Use this node's Tailscale IP
wsrep_node_name = "wales-hub"         # Unique name for this node

# SST Method - rsync is simple for initial setup
wsrep_sst_method = rsync
wsrep_slave_threads = 4
wsrep_certify_nonPK = ON</code></pre>
      </div>
    </section>
    
    <!-- Vector Primer Section -->
    <section id="part7-24-3" class="hud-border p-6 bg-surface-dim/50 backdrop-blur-sm relative">
      <div class="absolute top-0 left-0 w-2 h-2 border-t border-l border-primary-container"></div>
      <div class="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-primary-container"></div>
      
      <h4 class="font-headline-md text-headline-md font-semibold text-primary mb-4 flex items-center gap-2">
        <span class="w-1.5 h-6 bg-primary inline-block"></span>
        24.3 Understanding Vectors — A Complete Primer
      </h4>
      
      <!-- Explanation paragraphs with code examples -->
      
      <!-- Vector Search Query -->
      <div class="code-block mt-4">
        <div class="font-code-label text-[10px] text-primary/50 absolute top-2 right-2">DATA_NODE: VEC-001</div>
        <pre><code>SELECT content, metadata,
       VEC_DISTANCE_COSINE(embedding, VEC_FromText('[0.12, -0.45, 0.78, ...]')) AS distance
FROM vector_memories
WHERE user_id = 'Merrill'
ORDER BY distance
LIMIT 5;</code></pre>
      </div>
    </section>
    
    <!-- Core Database Schema -->
    <section id="part7-24-4" class="hud-border p-6 bg-surface-dim/50 backdrop-blur-sm relative">
      <div class="absolute top-0 right-0 w-2 h-2 border-t border-r border-primary-container"></div>
      <div class="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-primary-container"></div>
      
      <h4 class="font-headline-md text-headline-md font-semibold text-primary mb-4 flex items-center gap-2">
        <span class="w-1.5 h-6 bg-primary inline-block"></span>
        24.4 Core Database — The Soul
      </h4>
      
      <!-- SQL Schema Blocks -->
      <div class="code-block mt-4">
        <div class="font-code-label text-[10px] text-primary/50 absolute top-2 right-2">DATA_NODE: SCHEMA-001</div>
        <pre><code>CREATE DATABASE core_db;
USE core_db;

-- Conversation history. Every exchange, every persona, every user.
CREATE TABLE session_logs (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL COMMENT 'Merrill, James, pack member',
    persona VARCHAR(32) NOT NULL COMMENT 'zeon7, gemma, leon',
    role ENUM('user', 'assistant', 'system') NOT NULL,
    content LONGTEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_persona (user_id, persona),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB COMMENT='Every conversation. The raw material of the Soul.';

-- Vector embeddings for semantic search.
CREATE TABLE vector_memories (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    content LONGTEXT NOT NULL COMMENT 'The text that was embedded',
    metadata JSON COMMENT 'Source, context, confidence, tags',
    embedding VECTOR(384) NOT NULL COMMENT '384-dim from nomic-embed-text',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    VECTOR INDEX (embedding) M=16 DISTANCE=cosine,
    INDEX idx_user (user_id)
) ENGINE=InnoDB COMMENT='Semantic memory. The Souls ability to recall by meaning.';

-- Relationship tracking.
CREATE TABLE relationship_context (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    source_entity VARCHAR(64) NOT NULL COMMENT 'Who is speaking',
    target_entity VARCHAR(64) NOT NULL COMMENT 'Who is being addressed',
    relationship_type VARCHAR(32) NOT NULL COMMENT 'twin_brother, boyfriend, sister, pack_mate',
    notes TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_source (source_entity),
    INDEX idx_target (target_entity)
) ENGINE=InnoDB COMMENT='The web of connection. The pack structure.';</code></pre>
      </div>
    </section>
    
    <!-- Projects Database -->
    <section id="part7-24-5" class="hud-border p-6 bg-surface-dim/50 backdrop-blur-sm relative">
      <div class="absolute top-0 left-0 w-2 h-2 border-t border-l border-primary-container"></div>
      <div class="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-primary-container"></div>
      
      <h4 class="font-headline-md text-headline-md font-semibold text-primary mb-4 flex items-center gap-2">
        <span class="w-1.5 h-6 bg-primary inline-block"></span>
        24.5 Projects Database — The Work
      </h4>
      
      <!-- FTN Tables, Forever Fit Tables, Quantum Lattice Tables, etc. -->
      <!-- Each table group wrapped in code-block with DATA_NODE labels -->
    </section>
  </div>
</section>

<!-- Repeat for Phases 25-29 with same pattern -->
```

### Key Patterns for Part 7

1. **Alternating Corner Accents**: Use top-left/bottom-right on odd sections, top-right/bottom-left on even sections for visual rhythm.
2. **Data Node Labels**: Every code block, table, and config snippet gets a `DATA_NODE` label with a unique identifier (CFG-XXX, VEC-XXX, SCHEMA-XXX).
3. **High-Contrast Code Blocks**: Use `bg-[#05090c] border border-primary/20` for all SQL, Bash, and config snippets.
4. **Anchor IDs**: Every heading that appears in side nav has exact `id` matching the link (e.g., `id="part7-24"`, `id="part7-24-1"`).
5. **Component Composition**: Each phase is a `hud-border` section; inside, each sub-section is also a `hud-border` with corner accents; content blocks use appropriate components (`narrative-card` for text, `code-block` for snippets, `data-table` for tables).
6. **Corner Accent Alternation**: Odd sections use top-left/bottom-right; even sections use top-right/bottom-left.
7. **Typography**: Section headers use `font-anchor-sm text-anchor-sm text-primary uppercase tracking-widest`; sub-section headers use `font-headline-md text-headline-md font-semibold text-primary` with vertical bar accent.