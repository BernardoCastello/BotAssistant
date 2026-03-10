-- =============================================================
-- Habilita a extensão pgvector
-- =============================================================
CREATE EXTENSION IF NOT EXISTS vector;

-- =============================================================
-- Tabela única de conhecimento com embeddings
-- =============================================================
CREATE TABLE IF NOT EXISTS knowledge (
    id         SERIAL PRIMARY KEY,
    category   VARCHAR(50)   NOT NULL,
    keywords   TEXT          NOT NULL,
    text       TEXT          NOT NULL,
    embedding  vector(1536),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índice para busca por similaridade (cosine distance)
CREATE INDEX IF NOT EXISTS knowledge_embedding_idx
    ON knowledge USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 10);

-- =============================================================
-- DADOS DE EXEMPLO — substitua pelos seus
-- 'text' é o que o bot usa para responder
-- 'keywords' é só para sua referência ao editar
-- =============================================================

INSERT INTO knowledge (category, keywords, text) VALUES

('sobre',
 'apresentação, quem é, desenvolvedor, background, experiência',
 'Sou Bernardo Castello, desenvolvedor de software com 2 anos de experiência profissional. Tenho foco em desenvolvimento backend com Python e construção de APIs, automações e sistemas escaláveis. Sou formado em Engenharia de Computação pela Universidade Federal do Rio Grande(FURG)'),

('skill',
 'backend, python, fastapi, flask',
 'No backend, trabalho principalmente com Python (FastAPI e flask). Tenho experiência avançada em construção de APIs REST, workers assíncronos e integrações com serviços externos.'),

('skill',
 'banco de dados, postgresql, mongodb, redis',
 'Trabalho com PostgreSQL e MongoDB como bancos principais. Tenho experiência com modelagem de dados, queries otimizadas, índices e uso de Redis para cache.'),

('skill',
 'devops, docker, ci/cd, github actions, cloud',
 'Utilizo Docker para containerização de todos os projetos. Tenho experiência com pipelines CI/CD via GitHub Actions e deploy em ambientes cloud (AWS e GCP).'),

('projeto',
 'api, gestão, tarefas, jwt, autenticação',
 'Projeto: API de Gestão de Tarefas. API REST completa com autenticação JWT, CRUD de tarefas, envio de notificações por email e documentação automática via Swagger. Stack: Python, FastAPI, PostgreSQL, Docker. Repositório: https://github.com/seuuser/tasks-api'),

('projeto',
 'bot, monitoramento, preços, e-commerce, telegram, whatsapp, scraping',
 'Projeto: Bot de Monitoramento de Preços. Bot que monitora preços em e-commerces e envia alertas via Telegram quando o preço cai. Stack: Python, Selenium, MongoDB, Telegram Bot API. Repositório: https://github.com/seuuser/price-monitor'),

('projeto',
 'dashboard, analytics, métricas, vendas, gráficos',
 'Projeto: Dashboard de Analytics. Dashboard web para visualização de métricas de vendas com gráficos interativos e filtros por período. Stack: React, TypeScript, Node.js, PostgreSQL. Repositório: https://github.com/seuuser/analytics-dashboard'),

('contato',
 'email, contato, mensagem, falar, orçamento',
 'Para entrar em contato por email: becastellosilva@gmail.com. É a forma mais rápida para discutir projetos e orçamentos. Respondo em até 24 horas úteis.'),

('contato',
 'linkedin, rede social, perfil profissional',
 'Perfil no LinkedIn: https://www.linkedin.com/in/bernardo-castello-silva/. Lá você encontra meu histórico profissional completo e projetos em destaque.'),

('contato',
 'github, código, repositórios, open source',
 'GitHub: https://github.com/BernardoCastello. Repositório com projetos pessoais, contribuições open source e exemplos de código.');
