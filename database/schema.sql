-- Projeto físico (PostgreSQL). Em desenvolvimento o app cria as tabelas sozinho (SQLite).
CREATE TABLE categoria (
    id    SERIAL PRIMARY KEY,
    nome  VARCHAR(50) NOT NULL UNIQUE,
    tipo  VARCHAR(10) NOT NULL CHECK (tipo IN ('receita', 'despesa'))
);

CREATE TABLE lancamento (
    id           SERIAL PRIMARY KEY,
    descricao    VARCHAR(100)  NOT NULL,
    valor        NUMERIC(10,2) NOT NULL CHECK (valor > 0),
    data         DATE          NOT NULL,
    observacao   VARCHAR(255),
    categoria_id INTEGER       NOT NULL REFERENCES categoria (id)
);

CREATE INDEX idx_lancamento_data      ON lancamento (data);
CREATE INDEX idx_lancamento_categoria ON lancamento (categoria_id);
