-- MEOK AI Labs Database Schema
-- PostgreSQL with pgvector

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    api_key VARCHAR(64) UNIQUE NOT NULL,
    name VARCHAR(255),
    plan VARCHAR(50) DEFAULT 'free',
    rate_limit INTEGER DEFAULT 100,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_api_key ON users(api_key);

-- Analyses table
CREATE TABLE analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content_hash VARCHAR(64) NOT NULL,
    framework VARCHAR(50) NOT NULL,
    content_type VARCHAR(20) DEFAULT 'text',
    score FLOAT NOT NULL,
    passed BOOLEAN NOT NULL,
    violations JSONB DEFAULT '[]',
    recommendations JSONB DEFAULT '[]',
    processing_time_ms FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_analysis_user_created ON analyses(user_id, created_at);
CREATE INDEX idx_analysis_framework ON analyses(framework);
CREATE INDEX idx_analysis_passed ON analyses(passed);

-- Memories table with vector embeddings
CREATE TABLE memories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    content_embedding VECTOR(1536),
    memory_type VARCHAR(50) DEFAULT 'episodic',
    tags TEXT[] DEFAULT '{}',
    importance FLOAT DEFAULT 0.5,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_memory_user_type ON memories(user_id, memory_type);
CREATE INDEX idx_memory_importance ON memories(importance DESC);
CREATE INDEX idx_memory_user_created ON memories(user_id, created_at);
CREATE INDEX idx_memory_embedding ON memories USING ivfflat (content_embedding vector_cosine_ops);

-- Agents table
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    capabilities TEXT[] DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'active',
    current_tasks INTEGER DEFAULT 0,
    max_concurrent INTEGER DEFAULT 5,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_agents_status ON agents(status);
CREATE INDEX idx_agents_name ON agents(name);

-- Tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    instruction TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'normal',
    status VARCHAR(20) DEFAULT 'pending',
    result JSONB,
    error TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX idx_tasks_created ON tasks(created_at);

-- Consciousness states table
CREATE TABLE consciousness_states (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL,
    state_type VARCHAR(50),
    awareness_level FLOAT DEFAULT 0.0,
    coherence FLOAT DEFAULT 0.0,
    active_patterns JSONB DEFAULT '[]',
    anomalies JSONB DEFAULT '[]',
    metrics JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_consciousness_session ON consciousness_states(session_id, created_at);
CREATE INDEX idx_consciousness_type ON consciousness_states(state_type);

-- Audit logs table
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    details JSONB DEFAULT '{}',
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_user ON audit_logs(user_id, created_at);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_created ON audit_logs(created_at DESC);

-- Webhook subscriptions table
CREATE TABLE webhook_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    events TEXT[] NOT NULL,
    secret VARCHAR(64),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_triggered TIMESTAMP,
    failure_count INTEGER DEFAULT 0
);

CREATE INDEX idx_webhook_user ON webhook_subscriptions(user_id);
CREATE INDEX idx_webhook_active ON webhook_subscriptions(active);

-- Functions

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at trigger to relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_memories_updated_at BEFORE UPDATE ON memories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row-level security (if using PostgreSQL 9.5+)

-- ALTER TABLE analyses ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE memories ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

-- Policies would be created based on user_id ownership
-- CREATE POLICY analysis_user_policy ON analyses FOR ALL
--     USING (user_id = current_user_id());

-- Seed data for agents
INSERT INTO agents (name, description, capabilities, status) VALUES
    ('researcher', 'Research and gather information', ARRAY['web_search', 'document_analysis', 'data_retrieval'], 'active'),
    ('writer', 'Content creation and editing', ARRAY['writing', 'editing', 'summarization'], 'active'),
    ('analyst', 'Data analysis and insights', ARRAY['data_analysis', 'visualization', 'reporting'], 'active'),
    ('coder', 'Code generation and review', ARRAY['code_generation', 'code_review', 'debugging'], 'active'),
    ('planner', 'Task planning and coordination', ARRAY['planning', 'scheduling', 'coordination'], 'active')
ON CONFLICT (name) DO NOTHING;
