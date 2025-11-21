import requests

BASE_URL = "https://www.empregare.com/api/pt-br/vagas/buscar-novo"

def buscar_vagas_empregare(pagina: int = 1, itens_por_pagina: int = 9999, nivel: str = "Estágio"):
    params = {
        "pagina": pagina,
        "itensPagina": itens_por_pagina,
        "nivel": nivel
    }

    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    return response.json()
