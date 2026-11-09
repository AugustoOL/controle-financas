-- Categorias padrão (o aplicativo já as cria sozinho na primeira execução; este arquivo documenta a carga).
INSERT INTO categoria (nome, tipo) VALUES
  ('Salário', 'receita'),
  ('Renda extra', 'receita'),
  ('Alimentação', 'despesa'),
  ('Moradia', 'despesa'),
  ('Transporte', 'despesa'),
  ('Lazer', 'despesa'),
  ('Saúde', 'despesa');
