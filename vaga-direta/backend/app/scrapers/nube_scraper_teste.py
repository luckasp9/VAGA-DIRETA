import requests
import json
import time
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIE_FILE = os.path.join(BASE_DIR, "nube_cookies.json")

BASE_URL = "https://www.nube.com.br/estudantes/vagas/json?offset={offset}"

HEADERS = {
    "accept": "*/*",
    "referer": "https://www.nube.com.br/estudantes/vagas",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}


def load_cookies():
    with open(COOKIE_FILE, "r", encoding="utf-8") as f:
        cookies = json.load(f)
    return {c["name"]: c["value"] for c in cookies}


def fetch_page(offset: int):
    cookies = load_cookies()
    url = BASE_URL.format(offset=offset)

    print(f"📡 Buscando offset = {offset} ...")

    resp = requests.get(url, headers=HEADERS, cookies=cookies)

    if resp.status_code == 403:
        print("❌ 403 – Cookies inválidos. Rode: python play_nube_session.py")
        raise SystemExit()

    resp.raise_for_status()
    return resp.json()


def normalizar_nube(item):
    view = item.get("view", {})
    vaga = item.get("vaga", {})

    local = view.get("local", "")
    cidade, estado = ("", "")

    if "|" in local:
        partes = local.split("|")
        cidade = partes[0].strip()
        estado = partes[1].strip()

    return {
        "id": vaga.get("id_vaga", ""),
        "url": "https://www.nube.com.br" + view.get("url", ""),
        "titulo": vaga.get("regex_filtro", ""),
        "bolsa_valor": view.get("bolsa_valor", ""),
        "cidade": cidade,
        "estado": estado,
        "beneficio": [b.get("titulo", "") for b in view.get("beneficios", [])],
        "logo": "",
        "empresa": view.get("titulo", ""),
        "descricao": "",
        "curso": ""
    }


def scrape_nube():
    all_vagas = []
    offset = 0

    while True:
        data = fetch_page(offset)

        if "dict_por_id_vaga" not in data:
            print("❌ Estrutura inesperada, ignorando página...")
            break

        vagas_dict = data["dict_por_id_vaga"]

        print(f"➡️ Capturadas {len(vagas_dict)} vagas (total: {len(all_vagas) + len(vagas_dict)})")

        for vaga_id, vaga_data in vagas_dict.items():
            all_vagas.append(normalizar_nube(vaga_data))

        # Controle de finalização
        lista_ids = data.get("lista_ids_vaga", [])
        if not lista_ids:  # Se vier vazio, acabou
            break

        offset += 30
        time.sleep(1)

    return all_vagas


if __name__ == "__main__":
    print("🔍 Iniciando captura do Nube...")
    vagas = scrape_nube()

    print(f"\n🔄 Normalizando {len(vagas)} vagas...")

    output_file = os.path.join(BASE_DIR, "vagas_nube.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(vagas, f, ensure_ascii=False, indent=4)

    print(f"💾 Arquivo final salvo em: {output_file}")
    print("✨ Concluído com sucesso!")
