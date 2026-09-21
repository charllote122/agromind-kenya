-- Enable extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- USERS — Kenyan farmers
-- =====================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone VARCHAR(20) UNIQUE,
    name VARCHAR(100),
    preferred_language VARCHAR(5) DEFAULT 'sw',
    county VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_county ON users(county);
CREATE INDEX idx_users_language ON users(preferred_language);

-- =====================================================
-- FARMS — each farmer's plots
-- =====================================================
CREATE TABLE farms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    crop VARCHAR(50) NOT NULL,
    location_lat FLOAT,
    location_lon FLOAT,
    county VARCHAR(50),
    size_acres FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_farms_user ON farms(user_id);
CREATE INDEX idx_farms_crop ON farms(crop);

-- =====================================================
-- CONVERSATIONS — chat sessions
-- =====================================================
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    farm_id UUID REFERENCES farms(id) ON DELETE SET NULL,
    language VARCHAR(5),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_conversations_user ON conversations(user_id);

-- =====================================================
-- MESSAGES — individual messages + agent trace
-- =====================================================
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(10) NOT NULL CHECK (role IN ('user', 'agent')),
    content TEXT,
    language VARCHAR(5),
    image_url TEXT,
    agent_trace JSONB,
    sources JSONB,
    latency_ms INT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_created ON messages(created_at);

-- =====================================================
-- KNOWLEDGE CHUNKS — RAG embeddings
-- =====================================================
CREATE TABLE knowledge_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source VARCHAR(200) NOT NULL,
    language VARCHAR(5) NOT NULL,
    chunk_text TEXT NOT NULL,
    chunk_text_en TEXT,
    embedding vector(384) NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_knowledge_embedding ON knowledge_chunks
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX idx_knowledge_language ON knowledge_chunks(language);
CREATE INDEX idx_knowledge_source ON knowledge_chunks(source);

-- =====================================================
-- DISEASES — reference table
-- =====================================================
CREATE TABLE diseases (
    id SERIAL PRIMARY KEY,
    name_en VARCHAR(100) NOT NULL,
    name_sw VARCHAR(100) NOT NULL,
    crop VARCHAR(50) NOT NULL,
    symptoms TEXT,
    treatment_en TEXT,
    treatment_sw TEXT,
    sources JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_diseases_crop ON diseases(crop);

-- =====================================================
-- TOOL CALLS — every agent tool call (for evaluation)
-- =====================================================
CREATE TABLE tool_calls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID REFERENCES messages(id) ON DELETE CASCADE,
    tool_name VARCHAR(50) NOT NULL,
    arguments JSONB,
    result JSONB,
    latency_ms INT,
    success BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tool_calls_message ON tool_calls(message_id);
CREATE INDEX idx_tool_calls_tool ON tool_calls(tool_name);

-- =====================================================
-- SEED DATA — sample diseases
-- =====================================================
INSERT INTO diseases (name_en, name_sw, crop, symptoms, treatment_en, treatment_sw, sources) VALUES
(
    'Maize Lethal Necrosis Disease',
    'Ugonjwa wa Ukame wa Mahindi',
    'maize',
    'Yellowing leaves, drying leaf edges, stunted growth, premature death',
    'Remove and burn infected plants. Control thrips and aphids. Report to county agricultural officer. Plant resistant varieties next season.',
    'Ng''oa na choma mimea iliyoambukizwa. Dhibiti thrips na aphids. Ripoti kwa afisa wa kilimo wa kaunti. Panda mbegu zinazostahimili msimu ujao.',
    '["KALRO Maize Guide 2023", "FAO East Africa Advisory"]'::jsonb
),
(
    'Coffee Leaf Rust',
    'Kuvu ya Majani ya Kahawa',
    'coffee',
    'Orange-yellow powdery spots on leaf undersides, defoliation, reduced yield',
    'Apply copper-based fungicide. Prune affected branches. Improve air circulation. Consult KALRO Coffee Research Institute.',
    'Tumia dawa ya kuvu yenye shaba. Pogoa matawi yaliyoathirika. Boresha mzunguko wa hewa. Wasiliana na KALRO.',
    '["KALRO Coffee Guide 2023"]'::jsonb
),
(
    'Tomato Late Blight',
    'Blight ya Tomato',
    'tomato',
    'Dark water-soaked spots on leaves, white mold on undersides, rapid wilting',
    'Remove infected plants immediately. Apply fungicide. Avoid overhead watering. Improve drainage.',
    'Ondoa mimea iliyoambukizwa mara moja. Tumia dawa ya kuvu. Epuka kumwagilia kutoka juu. Boresha mifereji ya maji.',
    '["KALRO Horticulture Guide 2023"]'::jsonb
);