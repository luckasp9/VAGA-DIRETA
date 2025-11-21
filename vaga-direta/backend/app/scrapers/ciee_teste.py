import requests
import json

URL = "https://api.ciee.org.br/vagas/vitrine-vaga/publicadas"

PARAMS = {
    "page": 0,
    "size": 5000,  # garante pegar todas
    "sort": "codigoVaga,desc",
    "tipoVaga": "ESTAGIO"
}

def fetch_vagas():
    response = requests.get(URL, params=PARAMS)
    response.raise_for_status()
    data = response.json()
    return data.get("content", [])

def normalize(v):
    """Normaliza uma vaga no formato mais limpo possível."""
    local = v.get("local") or {}

    return {
        "codigo": v.get("codigoVaga"),
        "tipoVaga": v.get("tipoVaga"),
        "empresa": v.get("nomeEmpresa"),
        "areaProfissional": v.get("areaProfissional"),
        "descricao": v.get("descricao"),

        # Local
        "cidade": local.get("cidade"),
        "estado": local.get("uf"),
        "bairro": local.get("bairro"),

        # Remuneração
        "bolsaAuxilio": v.get("bolsaAuxilio"),
        "tipoValorBolsa": v.get("tipoValorBolsa"),
        "tipoAuxilioBolsa": v.get("tipoAuxilioBolsa"),
        "beneficios": v.get("beneficios"),

        # Horários
        "tipoHorario": v.get("tipoHorario"),
        "entrada": v.get("horarioEntrada"),
        "saida": v.get("horarioSaida"),
        "cargaHoraria": v.get("cargaHoraria"),

        # Atividades e Requisitos
        "atividades": v.get("atividades"),
        "requisitos": {
            "semestreInicio": v.get("requisitos", {}).get("semestreInicio"),
            "semestreFinal": v.get("requisitos", {}).get("semestreFinal"),
        },

        "nivelEscolar": v.get("nivelEscolar"),
        "logo": v.get("logo"),

        # Completo
        "raw": v  # Mantemos tudo para debug ou para inserir no PostgreSQL depois
    }

def save_json(vagas, path="vagas_ciee.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(vagas, f, ensure_ascii=False, indent=4)
    print(f"Arquivo salvo: {path} ({len(vagas)} vagas)")

def save_jsonl(vagas, path="vagas_ciee.jsonl"):
    with open(path, "w", encoding="utf-8") as f:
        for v in vagas:
            f.write(json.dumps(v, ensure_ascii=False) + "\n")
    print(f"Arquivo salvo: {path} ({len(vagas)} vagas)")

if __name__ == "__main__":
    print("Coletando vagas de estágio do CIEE (Brasil inteiro)...")

    raw = fetch_vagas()
    vagas = [normalize(v) for v in raw]

    save_jsonl(vagas)       # recomendado para bases grandes
    save_json(vagas)        # útil para debug

    print("Finalizado!")
