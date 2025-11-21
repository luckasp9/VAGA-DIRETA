import json
import requests
import os

BASE_URL = "https://www.empregare.com/api/pt-br/vagas/buscar-novo"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.empregare.com/vagas",
    "Origin": "https://www.empregare.com",
    "X-Requested-With": "XMLHttpRequest"
}

def buscar_vagas_empregare(pagina: int = 1, itens: int = 9999, nivel: str = "Estágio"):
    params = {
        "pagina": pagina,
        "itensPagina": itens,
        "nivel": nivel
    }

    response = requests.get(BASE_URL, headers=HEADERS, params=params)

    if response.status_code == 403:
        print("❌ Acesso negado (403). Falta algum header obrigatório.")
        print("Tente abrir o site e copiar os headers do request.")
        raise SystemExit()

    response.raise_for_status()
    return response.json()


def salvar_vagas_json(filename="vagas_empregare.json"):
    vagas = buscar_vagas_empregare()

    save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(vagas, f, indent=4, ensure_ascii=False)

    print(f"✅ Arquivo salvo: {save_path}")


if __name__ == "__main__":
    salvar_vagas_json()
