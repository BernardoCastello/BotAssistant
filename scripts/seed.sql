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
 'Sou [Seu Nome], desenvolvedor de software com X anos de experiência. Tenho foco em desenvolvimento backend com Python e construção de APIs, automações e sistemas escaláveis. Trabalho tanto com projetos freelance quanto consultoria técnica.'),

('skill',
 'backend, python, fastapi, django, node',
 'No backend, trabalho principalmente com Python (FastAPI e Django) e Node.js. Tenho experiência avançada em construção de APIs REST, workers assíncronos e integrações com serviços externos.'),

('skill',
 'frontend, react, typescript, html, css',
 'No frontend, trabalho com React e TypeScript para construção de interfaces web. Tenho experiência intermediária com estilização, componentes reutilizáveis e integração com APIs.'),

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
 'bot, monitoramento, preços, e-commerce, telegram, scraping',
 'Projeto: Bot de Monitoramento de Preços. Bot que monitora preços em e-commerces e envia alertas via Telegram quando o preço cai. Stack: Python, Selenium, MongoDB, Telegram Bot API. Repositório: https://github.com/seuuser/price-monitor'),

('projeto',
 'dashboard, analytics, métricas, vendas, gráficos',
 'Projeto: Dashboard de Analytics. Dashboard web para visualização de métricas de vendas com gráficos interativos e filtros por período. Stack: React, TypeScript, Node.js, PostgreSQL. Repositório: https://github.com/seuuser/analytics-dashboard'),

('contato',
 'email, contato, mensagem, falar, orçamento',
 'Para entrar em contato por email: seuemail@gmail.com. É a forma mais rápida para discutir projetos e orçamentos. Respondo em até 24 horas úteis.'),

('contato',
 'linkedin, rede social, perfil profissional',
 'Perfil no LinkedIn: https://linkedin.com/in/seuperfil. Lá você encontra meu histórico profissional completo e projetos em destaque.'),

('contato',
 'github, código, repositórios, open source',
 'GitHub: https://github.com/seuuser. Repositório com projetos pessoais, contribuições open source e exemplos de código.'),

('servico',
 'freelance, disponibilidade, projetos, consultoria, contratar',
 'Estou disponível para projetos freelance, consultoria técnica e desenvolvimento sob demanda. Serviços: desenvolvimento de APIs, automação de processos, integrações entre sistemas e consultoria em arquitetura. Para orçamentos, entre em contato por email.'),

('servico',
 'prazo, entrega, tempo, cronograma',
 'Prazos variam conforme complexidade. Projetos simples (automações, APIs básicas) levam de 1 a 2 semanas. Sistemas completos de 1 a 3 meses. Cronograma sempre alinhado antes de iniciar.');
