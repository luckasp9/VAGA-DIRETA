import requests

URL = "https://www.superestagios.com.br/index/comunicacaoAjax/vagas.php"

def buscar_vagas_super_estagios(
    id_estado: int = 7,          # DF
    id_nivel_ensino: int = 2,    # Ensino Superior
    id_curso: int = 7,           # Ciência da Computação
    id_cidade: str = "",
    limite: int = 0              # 0 = listar todas
):
    payload = {
        "acao": "listarAtivas",
        "limite": limite,
        "geo": 0,
        "id_estado": id_estado,
        "id_nivel_ensino": id_nivel_ensino,
        "id_curso": id_curso,
        "id_vaga": "",
        "id_cidade": id_cidade,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest",
    }

    try:
        response = requests.post(URL, data=payload, headers=headers, timeout=15)
        response.raise_for_status()

        try:
            return response.json()
        except ValueError:
            return {"erro": "Resposta não é JSON", "conteudo": response.text}

    except requests.RequestException as e:
        return {"erro": "Falha na requisição", "detalhes": str(e)}
