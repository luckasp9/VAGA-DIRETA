import json
import os
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIE_FILE = os.path.join(BASE_DIR, "nube_cookies.json")

def refresh_nube_cookies():
    print("🌐 Iniciando Playwright...")

    with sync_playwright() as p:
        print("➡ Abrindo navegador...")
        browser = p.chromium.launch(headless=False)  # MOSTRAR navegador para conferir
        context = browser.new_context()

        page = context.new_page()
        print("➡ Indo para a página do Nube...")

        try:
            page.goto("https://www.nube.com.br/estudantes/vagas", timeout=30000)
            print("✅ Página carregada!")

        except Exception as e:
            print("❌ ERRO ao carregar a página:", e)
            browser.close()
            return

        print("📥 Capturando cookies...")
        cookies = context.cookies()

        print(f"🍪 Cookies obtidos ({len(cookies)} encontrados):")
        print(cookies)

        if len(cookies) == 0:
            print("❌ Nenhum cookie capturado! Algo bloqueou o carregamento.")
            browser.close()
            return

        try:
            print("💾 Salvando cookies em:", COOKIE_FILE)
            with open(COOKIE_FILE, "w", encoding="utf-8") as f:
                json.dump(cookies, f, indent=4)
        except Exception as e:
            print("❌ ERRO ao salvar arquivo:", e)
            browser.close()
            return

        browser.close()
        print("✅ Cookies salvos com sucesso!")

if __name__ == "__main__":
    refresh_nube_cookies()
