import requests
import json
import time
import os
import sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))        # .../app/scrapers
APP_DIR = os.path.dirname(CURRENT_DIR)                         # .../app
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)
    

# importa mapa de cursos (assumindo app/utils/curso_map.py)
try:
    from utils.curso_map import CURSO_MAP
    from utils.detectar_cursos import detectar_cursos
except Exception as e:
    CURSO_MAP = {"__default__": "Outros"}
    print(" Aviso: não encontrou utils. Usando fallback. Erro:", e)


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

    print(f" Buscando offset = {offset} ...")

    resp = requests.get(url, headers=HEADERS, cookies=cookies)

    if resp.status_code == 403:
        print(" 403 – Cookies inválidos. Rode: python play_nube_session.py")
        raise SystemExit()

    resp.raise_for_status()
    return resp.json()


def normalizar_nube(item):
    view = item.get("view", {})
    vaga = item.get("vaga", {})

    # ---------------------
    # LOCALIDADE (cidade / estado)
    # ---------------------
    local_raw = view.get("local", "")
    cidade, estado = ("", "")

    if "|" in local_raw:
        partes = local_raw.split("|")
        cidade = partes[0].strip()
        estado = partes[1].strip()

        if "<br>" in estado:
            estado = estado.split("<br>")[0].strip()


        # ---------------------
    # MODALIDADE
    # ---------------------
    id_modalidade = view.get("id_modalidade_atuacao")

    if id_modalidade == 1:
        modalidade = "Presencial"

    elif id_modalidade == 3:
        modalidade = "Híbrido"
        cidade = "Híbrido"

    elif id_modalidade == 2:
        modalidade = "Remoto"
        cidade = "Remoto"

    else:
        modalidade = ""



    # ---------------------
    # DESCRIÇÃO
    # ---------------------
    descricao = vaga.get("descricao_vaga", "")

    # ---------------------
    # CURSOS (agora com descrição + título)
    # ---------------------
    texto_curso = descricao + " " + vaga.get("regex_filtro", "")
    cursos = detectar_cursos(texto_curso)

    # ---------------------
    # RETURN NA ORDEM PEDIDA
    # ---------------------
    return {
        "id": vaga.get("id_vaga"),
        "titulo": "Estágio",
        "empresa": view.get("titulo"),
        "descricao": descricao,
        "cidade": cidade,
        "estado": estado,
        "bolsa": view.get("bolsa_valor"),
        "beneficios": [b.get("titulo", "") for b in view.get("beneficios", [])],
        "logo": "",
        "pcd": False,
        "modalidade": modalidade,
        "cursos": cursos,
        "url": "https://www.nube.com.br" + view.get("url", "")
    }




def scrape_nube():
    all_vagas = []
    offset = 0

    while True:
        data = fetch_page(offset)

        if "dict_por_id_vaga" not in data:
            print(" Estrutura inesperada, ignorando página...")
            break

        vagas_dict = data["dict_por_id_vaga"]

        print(f" Capturadas {len(vagas_dict)} vagas (total: {len(all_vagas) + len(vagas_dict)})")

        for vaga_id, vaga_data in vagas_dict.items():
            all_vagas.append(normalizar_nube(vaga_data))

        lista_ids = data.get("lista_ids_vaga", [])
        if not lista_ids:
            break

        offset += 30
        time.sleep(1)

    return all_vagas

if __name__ == "__main__":
    print(" Iniciando captura do Nube...")
    vagas = scrape_nube()

    print(f"\n Normalizando {len(vagas)} vagas...")

    output_file = os.path.join(BASE_DIR, "vagas_nube.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(vagas, f, ensure_ascii=False, indent=4)

    print(f" Arquivo final salvo em: {output_file}")
    print(" Concluído com sucesso!")

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(OUTPUT_DIR, "vagas_nube.json")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(vagas, f, ensure_ascii=False, indent=4)

print(f" Arquivo salvo em: {OUTPUT_FILE}")
