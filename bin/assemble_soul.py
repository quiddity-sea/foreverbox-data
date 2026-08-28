#!/usr/bin/env python3
"""
Dynamic SOUL Assembly Script
Generates agent SOUL.md files from the agent_registry database
based on the current provider (cloud vs local/ollama).
"""

import os
import sys
import mysql.connector
from mysql.connector import Error
from pathlib import Path

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'zeon7_user'),
    'password': os.environ.get('DB_PASSWORD') or os.environ.get('FOREVERBOX_DB_PASS') or 'F0reverb0x#2o26sql',
    'database': os.environ.get('DB_NAME', 'agent_registry')
}

# Provider detection
def get_current_provider():
    """Detect current provider from environment or config."""
    # Check environment variable first
    provider = os.environ.get('HERMES_PROVIDER', '').lower()
    if provider:
        return provider
    
    # Fallback: check Hermes config
    config_paths = [
        Path.home() / '.hermes' / 'profiles' / 'zeon7' / 'config.yaml',
        Path.home() / '.hermes' / 'config.yaml',
    ]
    
    for config_path in config_paths:
        if config_path.exists():
            import yaml
            with open(config_path) as f:
                config = yaml.safe_load(f)
                if config and 'model' in config:
                    model = config['model']
                    if 'ollama' in str(model).lower() or config.get('provider') == 'ollama':
                        return 'ollama'
                    return 'cloud'
    
    # Default to cloud
    return 'cloud'

def get_provider_filter(provider):
    """Get the provider filter for the current provider."""
    if provider == 'ollama':
        return ['ollama', None]
    elif provider == 'coder':
        return ['coder', None]
    else:
        return ['cloud', 'openrouter', 'deepseek', 'anthropic', None]

def fetch_components(agent_slug, provider_filters):
    """Fetch SOUL components for an agent matching the provider filter."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # Build query with provider-specific variant preference
        # When a variant (coder, ollama) exists, exclude shared (NULL) fallbacks
        placeholders = ', '.join(['%s'] * len(provider_filters))
        current_filter = provider_filters[0]  # The specific filter (e.g. 'coder', 'ollama')
        query = f"""
            SELECT component_key, section_order, section_description, section_content
            FROM soul_components c
            WHERE (c.agent_slug = %s OR c.agent_slug IS NULL)
            AND (
                c.provider_filter = %s
                OR (
                    c.provider_filter IS NULL
                    AND NOT EXISTS (
                        SELECT 1 FROM soul_components c2
                        WHERE c2.component_key = c.component_key
                        AND (c2.agent_slug = c.agent_slug OR (c2.agent_slug IS NULL AND c.agent_slug IS NULL))
                        AND c2.provider_filter = %s
                    )
                )
            )
            ORDER BY 
                CASE WHEN agent_slug IS NULL THEN 1 ELSE 0 END,
                section_order
        """
        
        params = [agent_slug, current_filter, current_filter]
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return rows
    except Error as e:
        print(f"Database error: {e}", file=sys.stderr)
        return []

def assemble_soul(agent_slug, provider):
    """Assemble SOUL.md content for an agent."""
    provider_filters = get_provider_filter(provider)
    components = fetch_components(agent_slug, provider_filters)
    
    if not components:
        return f"# SOUL: {agent_slug}\n\n*No components found in database.*"
    
    parts = []
    for comp in components:
        parts.append(comp['section_content'])
    
    return '\n\n'.join(parts)

def write_soul_file(agent_slug, content):
    """Write assembled SOUL.md to agent profile directory."""
    profile_dir = Path(f"/foreverbox_data/profiles/{agent_slug}")
    profile_dir.mkdir(parents=True, exist_ok=True)
    
    soul_path = profile_dir / "SOUL.md"
    soul_path.write_text(content)
    return soul_path

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 assemble_soul.py <agent_slug> [provider]")
        print("Agent slugs: zeon7, leon, gemma, otec, wolf")
        print("Providers: ollama, openrouter, deepseek, anthropic (default: auto-detect)")
        sys.exit(1)
    
    agent_slug = sys.argv[1].lower()
    valid_agents = ['zeon7', 'leon', 'gemma', 'otec', 'wolf']
    
    if agent_slug not in valid_agents:
        print(f"Unknown agent: {agent_slug}. Valid: {valid_agents}")
        sys.exit(1)
    
    provider = sys.argv[2].lower() if len(sys.argv) > 2 else get_current_provider()
    
    print(f"Assembling SOUL for {agent_slug} (provider: {provider})...")
    
    content = assemble_soul(agent_slug, provider)
    path = write_soul_file(agent_slug, content)
    
    print(f"Written to {path}")

if __name__ == '__main__':
    main()