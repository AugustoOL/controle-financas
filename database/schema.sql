-- Projeto físico (PostgreSQL). Em desenvolvimento o app cria as tabelas sozinho (SQLite).
CREATE TABLE usuario (
    id         SERIAL PRIMARY KEY,
    nome       VARCHAR(80)  NOT NULL,
    email      VARCHAR(120) NOT NULL UNIQUE,   -- guardado em minúsculas
    senha_hash VARCHAR(255) NOT NULL           -- hash (werkzeug); nunca a senha pura
);

CREATE TABLE categoria (
    id         SERIAL PRIMARY KEY,
    nome       VARCHAR(50) NOT NULL,
    tipo       VARCHAR(10) NOT NULL CHECK (tipo IN ('receita', 'despesa')),
    usuario_id INTEGER     NOT NULL REFERENCES usuario (id),
    CONSTRAINT uq_categoria_usuario_nome UNIQUE (usuario_id, nome)
);

CREATE TABLE lancamento (
    id           SERIAL PRIMARY KEY,
    descricao    VARCHAR(100)  NOT NULL,
    valor        NUMERIC(10,2) NOT NULL CHECK (valor > 0),
    data         DATE          NOT NULL,
    observacao   VARCHAR(255),
    categoria_id INTEGER       NOT NULL REFERENCES categoria (id),
    usuario_id   INTEGER       NOT NULL REFERENCES usuario (id)
);

CREATE INDEX idx_categoria_usuario    ON categoria  (usuario_id);
CREATE INDEX idx_lancamento_usuario   ON lancamento (usuario_id);
CREATE INDEX idx_lancamento_data      ON lancamento (data);
CREATE INDEX idx_lancamento_categoria ON lancamento (categoria_id);
