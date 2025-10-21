from playwright.sync_api import sync_playwright


def get_ciee_vagas(limit: int = 30):
    """
    Raspa vagas de estágio do portal CIEE usando Playwright.
    Retorna lista de dicionários no formato padrão.
    """
    vagas = []
    url = "https://portal.ciee.org.br/portal/estudantes/vagas"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)
            page.wait_for_timeout(6000)  # espera JS carregar

            cards = page.query_selector_all(".card-vaga")
            for card in cards[:limit]:
                try:
                    titulo = card.query_selector(".titulo-vaga").inner_text().strip()
                    empresa = card.query_selector(".nome-empresa").inner_text().strip() if card.query_selector(".nome-empresa") else "CIEE"
                    cidade = card.query_selector(".localizacao").inner_text().strip() if card.query_selector(".localizacao") else ""
                    salario = card.query_selector(".valor-bolsa").inner_text().strip() if card.query_selector(".valor-bolsa") else ""
                    beneficios = card.query_selector(".beneficios").inner_text().strip() if card.query_selector(".beneficios") else ""
                    descricao = card.query_selector(".descricao-vaga").inner_text().strip() if card.query_selector(".descricao-vaga") else ""
                    link = card.query_selector("a").get_attribute("href")

                    vagas.append({
                        "job_id": link or titulo,
                        "job_title": titulo,
                        "employer_name": empresa,
                        "job_description": descricao,
                        "job_city": cidade,
                        "job_state": "",
                        "job_country": "Brasil",
                        "job_employment_type": "Estágio",
                        "job_apply_link": link,
                        "job_salary": salario,
                        "job_benefits": beneficios
                    })
                except Exception as e:
                    print(f"[CIEE] Erro ao processar vaga: {e}")
                    continue

            browser.close()

    except Exception as e:
        print(f"[CIEE] Erro ao acessar o site: {e}")

    return vagas
