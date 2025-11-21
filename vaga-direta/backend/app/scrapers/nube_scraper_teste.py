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
        print("❌ 403 – Cookies inválidos. Execute: python play_nube_session.py")
        raise SystemExit()

    resp.raise_for_status()
    return resp.json()


def scrape_nube():
    all_vagas = []
    offset = 0

    while True:
        data = fetch_page(offset)

        vagas_dict = {k: v for k, v in data.items() if k != "offset"}
        vagas = list(vagas_dict.values())
        all_vagas.extend(vagas)

        print(f"➡️ Capturadas {len(vagas)} (total: {len(all_vagas)})")

        next_offset = data["offset"]["proximo"]

        if next_offset == offset:
            break

        offset = next_offset
        time.sleep(1)

    return all_vagas


if __name__ == "__main__":
    result = scrape_nube()
    print(f"\n🎉 Total final: {len(result)} vagas")

    # ================================================
    # SALVANDO RESULTADO EM JSON
    # ================================================
    output_file = os.path.join(BASE_DIR, "vagas_nube.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    print(f"💾 Arquivo salvo em: {output_file}")
