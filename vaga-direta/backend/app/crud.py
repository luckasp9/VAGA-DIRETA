# app/crud.py
from typing import List, Optional, Dict, Any
import psycopg2
import psycopg2.extras

from app.models import Vaga, VagaCreate


# =========================
# Conexão com o banco
# =========================
def get_connection():
  """
  Ajuste aqui se depois quiser puxar de .env.
  """
  return psycopg2.connect(
      host="localhost",
      database="postgres",
      user="postgres",
      password="1234",
  )


# =========================
# Helpers internos
# =========================
def _vaga_to_dict(row: psycopg2.extras.RealDictRow) -> Dict[str, Any]:
  """
  Converte a linha base da vaga em dict normal.
  """
  return dict(row)


def _carregar_beneficios(cur, vaga_id: int) -> List[str]:
  cur.execute(
      """
      SELECT beneficio
      FROM tcc.beneficio
      WHERE vaga_id = %s
      ORDER BY id;
      """,
      (vaga_id,),
  )
  return [r["beneficio"] for r in cur.fetchall()]


def _carregar_cursos(cur, vaga_id: int) -> List[str]:
  """
  Busca os NOMES dos cursos vinculados à vaga.

  Estrutura atual:
    tcc.curso (id, vaga_id, curso)
  """
  cur.execute(
      """
      SELECT curso
      FROM tcc.curso
      WHERE vaga_id = %s
      ORDER BY curso;
      """,
      (vaga_id,),
  )
  return [r["curso"] for r in cur.fetchall()]


def _sincronizar_cursos(cur, vaga_id: int, cursos: List[str]) -> None:
  """
  Zera e recria registros em tcc.curso para a vaga.
  Agora NÃO existe mais tcc.vaga_curso.
  """
  # apaga cursos antigos da vaga
  cur.execute("DELETE FROM tcc.curso WHERE vaga_id = %s;", (vaga_id,))

  # recria
  for nome in cursos:
    nome = nome.strip()
    if not nome:
      continue
    cur.execute(
        """
        INSERT INTO tcc.curso (vaga_id, curso)
        VALUES (%s, %s);
        """,
        (vaga_id, nome),
    )


def _sincronizar_beneficios(cur, vaga_id: int, beneficios: List[str]) -> None:
  """
  Zera e recria benefícios em tcc.beneficio para a vaga.
  """
  cur.execute("DELETE FROM tcc.beneficio WHERE vaga_id = %s;", (vaga_id,))

  for b in beneficios:
    b = b.strip()
    if not b:
      continue
    cur.execute(
        """
        INSERT INTO tcc.beneficio (vaga_id, beneficio)
        VALUES (%s, %s);
        """,
        (vaga_id, b),
    )


# =========================
# CRUD público
# =========================
def listar_vagas() -> List[Vaga]:
  """
  Lista todas as vagas, já trazendo:
    - campos da tcc.vaga
    - beneficios (tcc.beneficio)
    - cursos (tcc.curso)
  """
  con = get_connection()
  cur = con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

  cur.execute("SELECT * FROM tcc.vaga ORDER BY created_at DESC, id DESC;")
  rows = cur.fetchall()

  resultado: List[dict] = []

  for row in rows:
    vaga_id = row["id"]
    vaga_dict = _vaga_to_dict(row)
    vaga_dict["beneficios"] = _carregar_beneficios(cur, vaga_id)
    vaga_dict["cursos"] = _carregar_cursos(cur, vaga_id)
    resultado.append(vaga_dict)

  con.close()
  return [Vaga(**v) for v in resultado]


def obter_vaga(vaga_id: int) -> Optional[Vaga]:
  """
  Devolve uma vaga específica (ou None se não existir).
  """
  con = get_connection()
  cur = con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

  cur.execute("SELECT * FROM tcc.vaga WHERE id = %s;", (vaga_id,))
  row = cur.fetchone()

  if not row:
    con.close()
    return None

  vaga_dict = _vaga_to_dict(row)
  vaga_dict["beneficios"] = _carregar_beneficios(cur, vaga_id)
  vaga_dict["cursos"] = _carregar_cursos(cur, vaga_id)

  con.close()
  return Vaga(**vaga_dict)


def criar_vaga(dados: VagaCreate) -> Vaga:
  """
  Cria vaga em tcc.vaga e sincroniza:
    - tcc.curso
    - tcc.beneficio
  Estrutura atual NÃO usa mais curso_id nem tcc.vaga_curso.
  """
  con = get_connection()
  cur = con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

  try:
    cur.execute(
        """
        INSERT INTO tcc.vaga (
            id_vaga,
            titulo_vaga,
            empresa_nome,
            descricao_vaga,
            cidade_vaga,
            estado_vaga,
            salario,
            url,
            pcd,
            modalidade
        )
        VALUES (
            NULL,
            %s, %s, %s, %s, %s, %s, %s,
            %s, %s
        )
        RETURNING *;
        """,
        (
            dados.titulo_vaga,
            dados.empresa_nome,
            dados.descricao_vaga,
            dados.cidade_vaga,
            dados.estado_vaga,
            dados.salario,
            dados.url,
            dados.pcd,
            dados.modalidade,
        ),
    )

    row = cur.fetchone()
    vaga_id = row["id"]

    # cursos e benefícios
    _sincronizar_cursos(cur, vaga_id, dados.cursos)
    _sincronizar_beneficios(cur, vaga_id, dados.beneficios)

    con.commit()

    vaga_dict = _vaga_to_dict(row)
    vaga_dict["beneficios"] = _carregar_beneficios(cur, vaga_id)
    vaga_dict["cursos"] = _carregar_cursos(cur, vaga_id)

    return Vaga(**vaga_dict)

  except Exception:
    con.rollback()
    raise
  finally:
    con.close()


def atualizar_vaga(vaga_id: int, dados: VagaCreate) -> Optional[Vaga]:
  """
  Atualiza vaga + cursos + benefícios. Se não existir, devolve None.
  """
  con = get_connection()
  cur = con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

  try:
    # verifica se existe
    cur.execute("SELECT id FROM tcc.vaga WHERE id = %s;", (vaga_id,))
    if not cur.fetchone():
      con.close()
      return None

    cur.execute(
        """
        UPDATE tcc.vaga
        SET
            titulo_vaga    = %s,
            empresa_nome   = %s,
            descricao_vaga = %s,
            cidade_vaga    = %s,
            estado_vaga    = %s,
            salario        = %s,
            url            = %s,
            pcd            = %s,
            modalidade     = %s
        WHERE id = %s
        RETURNING *;
        """,
        (
            dados.titulo_vaga,
            dados.empresa_nome,
            dados.descricao_vaga,
            dados.cidade_vaga,
            dados.estado_vaga,
            dados.salario,
            dados.url,
            dados.pcd,
            dados.modalidade,
            vaga_id,
        ),
    )

    row = cur.fetchone()
    if not row:
      con.rollback()
      con.close()
      return None

    # atualiza relacionamentos
    _sincronizar_cursos(cur, vaga_id, dados.cursos)
    _sincronizar_beneficios(cur, vaga_id, dados.beneficios)

    con.commit()

    vaga_dict = _vaga_to_dict(row)
    vaga_dict["beneficios"] = _carregar_beneficios(cur, vaga_id)
    vaga_dict["cursos"] = _carregar_cursos(cur, vaga_id)

    return Vaga(**vaga_dict)

  except Exception:
    con.rollback()
    raise
  finally:
    con.close()


def excluir_vaga(vaga_id: int) -> bool:
  """
  Remove a vaga e seus relacionamentos.
  Retorna True se algo foi apagado.
  """
  con = get_connection()
  cur = con.cursor()

  try:
    # apaga relacionamentos (mesmo tendo ON DELETE CASCADE,
    # não faz mal garantir)
    cur.execute("DELETE FROM tcc.curso WHERE vaga_id = %s;", (vaga_id,))
    cur.execute("DELETE FROM tcc.beneficio WHERE vaga_id = %s;", (vaga_id,))

    cur.execute("DELETE FROM tcc.vaga WHERE id = %s;", (vaga_id,))
    apagadas = cur.rowcount

    con.commit()
    return apagadas > 0
  except Exception:
    con.rollback()
    raise
  finally:
    con.close()
