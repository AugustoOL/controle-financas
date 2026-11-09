-- Categorias padrão. O aplicativo as cria sozinho para CADA novo usuário, no cadastro;
-- este arquivo documenta a carga. Troque :usuario_id pelo id do usuário recém-criado.
INSERT INTO categoria (nome, tipo, usuario_id) VALUES
  ('Salário', 'receita', :usuario_id),
  ('Renda extra', 'receita', :usuario_id),
  ('Alimentação', 'despesa', :usuario_id),
  ('Moradia', 'despesa', :usuario_id),
  ('Transporte', 'despesa', :usuario_id),
  ('Lazer', 'despesa', :usuario_id),
  ('Saúde', 'despesa', :usuario_id);
