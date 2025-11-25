import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_json_safely(path):
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            with open(path, "r", encoding=enc) as f:
                return json.load(f)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Não foi possível ler o arquivo {path}.")


# ------------------------------------------------------------
# NORMALIZADORES
# ------------------------------------------------------------

def normalizar_ciee(vaga):
    return {
        "id": vaga.get("codigo", ""),
        "url": f"https://ciee.app/detalhes-vaga/{vaga.get('codigo', '')}",
        "titulo": vaga.get("tipoVaga", ""),
        "bolsa_valor": vaga.get("bolsaAuxilio", ""),
        "cidade": vaga.get("local", {}).get("cidade", ""),
        "estado": vaga.get("local", {}).get("UF", ""),
        "beneficio": vaga.get("beneficios", []),
        "logo": vaga.get("logo", ""),
        "empresa": vaga.get("empresa", ""),
        "descricao": vaga.get("descricao", ""),
        "curso": ""
    }


def normalizar_nube(vaga):
    local = vaga.get("local", "")
    cidade, estado = ("", "")
    if " - " in local:
        cidade, estado = local.split(" - ", 1)

    return {
        "id": vaga.get("id_vaga", ""),
        "url": "https://www.nube.com.br" + vaga.get("url", ""),
        "titulo": vaga.get("titulo", ""),
        "bolsa_valor": vaga.get("bolsa_valor", ""),
        "cidade": cidade,
        "estado": estado,
        "beneficio": vaga.get("beneficios", []),
        "logo": "",
        "empresa": vaga.get("empresa", ""),
        "descricao": vaga.get("descricao", ""),
        "curso": vaga.get("curso", "")
    }


def normalizar_empregare(vaga):
    cidade = estado = ""

    cidades = vaga.get("cidades", "")
    if "," in cidades:
        cidade, estado = cidades.split(",", 1)

    return {
        "id": vaga.get("id", ""),
        "url": "https://www.empregare.com/" + vaga.get("url", ""),
        "titulo": vaga.get("titulo", ""),
        "bolsa_valor": vaga.get("salario", ""),
        "cidade": cidade.strip(),
        "estado": estado.strip(),
        "beneficio": [],
        "logo": "",
        "empresa": vaga.get("empresa", ""),
        "descricao": vaga.get("descricao", ""),
        "curso": ""
    }


# ------------------------------------------------------------
# CARREGAMENTO DOS ARQUIVOS
# ------------------------------------------------------------

ciee_data = load_json_safely(os.path.join(BASE_DIR, "Json_vagas", "vagas_ciee.json"))
nube_raw = load_json_safely(os.path.join(BASE_DIR, "Json_vagas", "vagas_nube.json"))
nube_raw = load_json_safely(os.path.join(BASE_DIR, "Json_vagas", "vagas_nube.json"))

# Transformar dicionário em lista de vagas reais
nube_list = []
for key, item in nube_raw.items():
    if not isinstance(item, dict):
        continue
    if "vaga" in item and "view" in item:
        vaga = {}

        # juntando o que precisamos
        vaga["id_vaga"] = item["vaga"].get("id_vaga", "")
        vaga["regex_filtro"] = item["vaga"].get("regex_filtro", "")
        vaga["url"] = item["view"].get("url", "")
        vaga["titulo"] = item["view"].get("titulo", "")
        vaga["local"] = f"{item['view'].get('cidade', '')} - {item['view'].get('uf', '')}"
        vaga["bolsa_valor"] = item["view"].get("bolsa_valor", "")
        vaga["beneficios"] = item["view"].get("beneficios", [])
        vaga["empresa"] = item["view"].get("subtitulo", "")
        vaga["descricao"] = item["view"].get("descricao", "")

        nube_list.append(vaga)


# Extrair listas reais
ciee_list = ciee_data
nube_list = nube_raw["model"]["dados"]      # CORREÇÃO IMPORTANTE
empregare_list = empregare_raw["model"]["vagas"]  # CORREÇÃO IMPORTANTE


# ------------------------------------------------------------
# UNIFICAÇÃO
# ------------------------------------------------------------

vagas_unificadas = []

for vaga in ciee_list:
    vagas_unificadas.append(normalizar_ciee(vaga))

for vaga in nube_list:
    vagas_unificadas.append(normalizar_nube(vaga))

for vaga in empregare_list:
    vagas_unificadas.append(normalizar_empregare(vaga))


# ------------------------------------------------------------
# SALVAR RESULTADO FINAL
# ------------------------------------------------------------

output_path = os.path.join(BASE_DIR, "vagas_unificadas.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(vagas_unificadas, f, ensure_ascii=False, indent=4)

print("-> Arquivo 'vagas_unificadas.json' gerado com sucesso!")


# ADICIONAR VAGAS AFIRMATIVAS