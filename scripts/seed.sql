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


INSERT INTO knowledge (category, keywords, text) VALUES

('sobre',
 'apresentação, quem é, desenvolvedor, background, experiência',
 'Sou Bernardo Castello, desenvolvedor de software com 2 anos de experiência profissional. Tenho foco em desenvolvimento backend com Python e construção de APIs, automações e sistemas escaláveis.
  Sou formado em Engenharia de Computação pela Universidade Federal do Rio Grande(FURG)'),

('contato',
 'email, contato, mensagem, falar, orçamento',
 'Para entrar em contato por email: becastellosilva@gmail.com. É a forma mais rápida para discutir projetos e orçamentos. Respondo em até 24 horas úteis.'),

('contato',
 'linkedin, rede social, perfil profissional',
 'Perfil no LinkedIn: https://www.linkedin.com/in/bernardo-castello-silva/. Lá você encontra meu histórico profissional completo e projetos em destaque.'),

('contato',
 'github, código, repositórios, open source',
 'GitHub: https://github.com/BernardoCastello. Repositório com projetos pessoais, contribuições open source e exemplos de código.'),

('skill',
 'backend, python, fastapi, flask',
 'No backend, trabalho principalmente com Python (FastAPI e flask). Tenho experiência avançada em construção de APIs REST, workers assíncronos e integrações com serviços externos.'),

('skill',
 'banco de dados, postgresql, mongodb, redis',
 'Trabalho com PostgreSQL e MongoDB como bancos principais. Tenho experiência com modelagem de dados, queries otimizadas, índices e uso de Redis para cache.'),

('skill',
 'devops, docker, ci/cd, github actions, cloud',
 'Utilizo Docker para containerização de todos os projetos. Tenho experiência com pipelines CI/CD via GitHub Actions e deploy em ambientes cloud (AWS e GCP).'),

('skill',
 'openai api, llm, automação, nlp, tts, stt, tradução',
 'Experiência no uso da API da OpenAI para integração de modelos de linguagem em aplicações. Implementação de respostas automáticas, chatbots inteligentes, geração e análise de texto,
  tradução automática, conversão de texto em fala (TTS) e fala em texto (STT). Integração com APIs REST e sistemas backend para automação de tarefas, processamento de linguagem natural e criação de assistentes virtuais.'), 

('project',
 'chatbot multicanal com llm e retrieval',
 'Desenvolvimento de um chatbot inteligente integrado ao Telegram e preparado para integração com WhatsApp. 
 O sistema foi desenvolvido em Python utilizando arquitetura assíncrona com APIs e workers para alta eficiência
no processamento de mensagens. Utiliza MongoDB para armazenamento do histórico completo das conversas e PostgreSQL 
(com suporte a retrieval) para armazenar informações estruturadas utilizadas pelo modelo.
 Integra a API da OpenAI para geração de respostas, processamento de linguagem natural e execução de tarefas inteligentes.
  A aplicação é containerizada com Docker, permitindo fácil deploy e escalabilidade.
  O objetivo do chatbot é me apresentar e fornecer informações minhas e de meus projetos.');