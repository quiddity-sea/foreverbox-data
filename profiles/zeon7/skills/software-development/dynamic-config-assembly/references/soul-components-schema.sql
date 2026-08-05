-- SOUL Components Table Schema
-- Run against agent_registry database

CREATE DATABASE IF NOT EXISTS agent_registry;

USE agent_registry;

CREATE TABLE IF NOT EXISTS soul_components (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    component_key VARCHAR(64) NOT NULL,
    agent_slug VARCHAR(32),  -- NULL = shared across all agents
    provider_filter VARCHAR(128),  -- NULL = all providers; comma-separated list for specific providers
    section_order INT UNSIGNED NOT NULL,
    section_description VARCHAR(255),
    section_content LONGTEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_component (component_key, agent_slug, provider_filter)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Index for assembly queries
CREATE INDEX idx_agent_provider_order ON soul_components (agent_slug, provider_filter, section_order);

-- Example provider_filter values:
-- NULL                          -> all providers (universal component)
-- 'openrouter,deepseek,anthropic' -> cloud providers only
-- 'ollama'                      -> local/Ollama only
-- 'openrouter'                  -> specific provider only