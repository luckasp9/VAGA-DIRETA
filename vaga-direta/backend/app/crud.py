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

    Assumindo estrutura:
      tcc.curso      (id, nome, ...)
      tcc.vaga_curso  (vaga_id, curso_id, ...)
    """
    cur.execute(
        """
        SELECT c.nome
        FROM tcc.curso c
        JOIN tcc.vaga_curso vc ON vc.curso_id = c.id
        WHERE vc.vaga_id = %s
        ORDER BY c.nome;
        """,
        (vaga_id,),
    )
    return [r["nome"] for r in cur.fetchall()]


def _obter_ou_criar_curso(cur, nome: str) -> int:
    """
    Garante que existe um curso com esse nome
    e devolve o id dele em tcc.curso.
    """
    nome = nome.strip()
    if not nome:
        raise ValueError("Nome de curso vazio.")

    # tenta buscar
    cur.execute(
        "SELECT id FROM tcc.curso WHERE nome = %s;",
        (nome,),
    )
    row = cur.fetchone()
    if row:
        return row["id"]

    # se não existir, cria
    cur.execute(
        """
        INSERT INTO tcc.curso (nome)
        VALUES (%s)
        RETURNING id;
        """,
        (nome,),
    )
    new_id = cur.fetchone()["id"]
    return new_id


def _sincronizar_cursos(cur, vaga_id: int, cursos: List[str]) -> None:
    """
    Zera e recria vínculos em tcc.vaga_curso para a vaga.
    """
    cur.execute(
        "DELETE FROM tcc.vaga_curso WHERE vaga_id = %s;",
        (vaga_id,),
    )

    for nome in cursos:
        nome = nome.strip()
        if not nome:
            continue
        curso_id = _obter_ou_criar_curso(cur, nome)
        cur.execute(
            """
            INSERT INTO tcc.vaga_curso (vaga_id, curso_id)
            VALUES (%s, %s)
            ON CONFLICT (vaga_id, curso_id) DO NOTHING;
            """,
            (vaga_id, curso_id),
        )


def _sincronizar_beneficios(cur, vaga_id: int, beneficios: List[str]) -> None:
    """
    Zera e recria benefícios em tcc.beneficio para a vaga.
    """
    cur.execute(
        "DELETE FROM tcc.beneficio WHERE vaga_id = %s;",
        (vaga_id,),
    )

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
      - cursos (tcc.curso via tcc.vaga_curso)
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
      - tcc.vaga_curso
      - tcc.beneficio
    """
    con = get_connection()
    cur = con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        # se quiser, define curso_id na tabela como "primeiro curso" (opcional)
        curso_id_principal = None
        cursos_limpos = [c.strip() for c in dados.cursos if c.strip()]
        if cursos_limpos:
            curso_id_principal = _obter_ou_criar_curso(cur, cursos_limpos[0])

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
                curso_id,
                pcd,
                modalidade
            )
            VALUES (
                NULL,
                %s, %s, %s, %s, %s, %s, %s,
                %s,
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
                curso_id_principal,
                dados.pcd,
                dados.modalidade,
            ),
        )

        row = cur.fetchone()
        vaga_id = row["id"]

        # cursos e benefícios (N:N e 1:N)
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
    Atualiza vaga+relacionamentos. Se não existir, devolve None.
    """
    con = get_connection()
    cur = con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        # verifica se existe
        cur.execute("SELECT id FROM tcc.vaga WHERE id = %s;", (vaga_id,))
        if not cur.fetchone():
            con.close()
            return None

        curso_id_principal = None
        cursos_limpos = [c.strip() for c in dados.cursos if c.strip()]
        if cursos_limpos:
            curso_id_principal = _obter_ou_criar_curso(cur, cursos_limpos[0])

        cur.execute(
            """
            UPDATE tcc.vaga
            SET
                titulo_vaga   = %s,
                empresa_nome  = %s,
                descricao_vaga = %s,
                cidade_vaga   = %s,
                estado_vaga   = %s,
                salario       = %s,
                url           = %s,
                curso_id      = %s,
                pcd           = %s,
                modalidade    = %s
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
                curso_id_principal,
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
        # apaga vínculos com cursos e benefícios (caso não haja ON DELETE CASCADE)
        cur.execute("DELETE FROM tcc.vaga_curso WHERE vaga_id = %s;", (vaga_id,))
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
