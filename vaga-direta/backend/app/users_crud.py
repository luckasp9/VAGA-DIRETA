# app/users_crud.py
from typing import Optional
import psycopg2
import psycopg2.extras

from app.models import UsuarioCreate, UsuarioPublic, UsuarioUpdate
from app.security import hash_password


def get_connection():
  """
  Conexão básica – igual você usa pro módulo de vagas.
  """
  return psycopg2.connect(
      host="localhost",
      database="postgres",
      user="postgres",
      password="1234",
  )


def criar_usuario(dados: UsuarioCreate) -> UsuarioPublic:
  """
  Insere um usuário em tcc.usuario com SENHA EM HASH (argon2).
  """
  con = get_connection()
  cur = con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

  try:
      senha_hash = hash_password(dados.senha)

      cur.execute(
          """
          INSERT INTO tcc.usuario (
              nome,
              email,
              senha,
              tipo_usuario,
              telefone,
              curso,
              semestre,
              estado
          )
          VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
          RETURNING
              id,
              nome,
              email,
              tipo_usuario,
              telefone,
              curso,
              semestre,
              estado;
          """,
          (
              dados.nome,
              dados.email,
              senha_hash,           # hash aqui
              dados.tipo_usuario,   # ex.: 'aluno' ou 'admin'
              dados.telefone,
              dados.curso,
              dados.semestre,
              dados.estado,
          ),
      )

      row = cur.fetchone()
      con.commit()

      return UsuarioPublic(**row)

  except psycopg2.IntegrityError:
      con.rollback()
      # por exemplo: email já existe (UNIQUE)
      raise
  finally:
      con.close()


def obter_usuario_por_email(email: str) -> Optional[dict]:
  """
  Busca um usuário pela coluna email.
  Retorna dict com TUDO (inclusive senha), ou None.
  """
  con = get_connection()
  cur = con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

  cur.execute(
      """
      SELECT
          id,
          nome,
          email,
          senha,
          tipo_usuario,
          telefone,
          curso,
          semestre,
          estado
      FROM tcc.usuario
      WHERE email = %s;
      """,
      (email,),
  )

  row = cur.fetchone()
  con.close()
  return dict(row) if row else None


def atualizar_usuario(user_id: int, dados: UsuarioUpdate) -> Optional[UsuarioPublic]:
  """
  Atualiza dados de perfil do usuário (sem mexer em email, senha, tipo_usuario).
  Retorna UsuarioPublic ou None se não existir.
  """
  con = get_connection()
  cur = con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

  try:
      # Busca usuário atual
      cur.execute(
          """
          SELECT
              id,
              nome,
              email,
              senha,
              tipo_usuario,
              telefone,
              curso,
              semestre,
              estado
          FROM tcc.usuario
          WHERE id = %s;
          """,
          (user_id,),
      )
      row = cur.fetchone()
      if not row:
          con.close()
          return None

      # Mantém valores antigos se o campo não vier no update
      nome = dados.nome if dados.nome is not None else row["nome"]
      telefone = dados.telefone if dados.telefone is not None else row["telefone"]
      curso = dados.curso if dados.curso is not None else row["curso"]
      semestre = dados.semestre if dados.semestre is not None else row["semestre"]
      estado = dados.estado if dados.estado is not None else row["estado"]

      cur.execute(
          """
          UPDATE tcc.usuario
          SET
              nome = %s,
              telefone = %s,
              curso = %s,
              semestre = %s,
              estado = %s
          WHERE id = %s
          RETURNING
              id,
              nome,
              email,
              tipo_usuario,
              telefone,
              curso,
              semestre,
              estado;
          """,
          (nome, telefone, curso, semestre, estado, user_id),
      )

      updated = cur.fetchone()
      con.commit()

      return UsuarioPublic(**updated)

  except Exception:
      con.rollback()
      raise
  finally:
      con.close()
