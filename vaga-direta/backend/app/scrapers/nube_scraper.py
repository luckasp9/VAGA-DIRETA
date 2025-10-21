import requests
from bs4 import BeautifulSoup


def get_nube_vagas(limit: int = 50):
    """
    Raspa vagas de estágio do site do Nube.
    Retorna uma lista de dicionários no formato padrão.
    """
    vagas = []
    base_url = "https://www.nube.com.br/estudantes/vagas"

    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"[NUBE] Erro ao acessar o site: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.select(".vaga")  # classe dos cards de vaga
    for card in cards[:limit]:
        try:
            titulo = card.select_one(".vaga__titulo").get_text(strip=True)
            empresa = card.select_one(".vaga__empresa").get_text(strip=True) if card.select_one(".vaga__empresa") else "Nube"
            cidade = card.select_one(".vaga__cidade").get_text(strip=True) if card.select_one(".vaga__cidade") else ""
            salario = card.select_one(".vaga__valor").get_text(strip=True) if card.select_one(".vaga__valor") else ""
            beneficios = ", ".join([b.get_text(strip=True) for b in card.select(".vaga__beneficio")])
            descricao = card.select_one(".vaga__descricao").get_text(strip=True) if card.select_one(".vaga__descricao") else ""
            link = "https://www.nube.com.br" + card.select_one("a")["href"]

            vagas.append({
                "job_id": link,
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
            print(f"[NUBE] Erro ao processar vaga: {e}")
            continue

    return vagas
