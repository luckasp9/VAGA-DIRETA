import os
import requests
import json
from dotenv import load_dotenv
import os
print("Diretório atual do Python:", os.getcwd())


# Carrega as variáveis do .env
load_dotenv()

# Sua chave RapidAPI (pegando do .env)
API_KEY = os.getenv("JSEARCH_API_KEY")

# Endpoint correto
url = "https://jsearch.p.rapidapi.com/search"

# Parâmetros da busca
query_params = {
    "query": "estágio",
    "page": "1",
    "num_pages": "1",
    "country": "br",
    "date_posted": "all"
}

headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "jsearch.p.rapidapi.com"
}

# Fazendo a requisição
print("🔍 Consultando a API JSearch...")
response = requests.get(url, headers=headers, params=query_params)

# Checando o status
print(f"Status: {response.status_code}")

if response.status_code != 200:
    print("❌ Erro ao buscar dados:", response.text)
    exit()

# Decodificando o JSON
data = response.json()

# --- Salvando na pasta backend/tests ---
save_dir = os.path.join(os.getcwd(), "tests")  # cria o caminho absoluto
os.makedirs(save_dir, exist_ok=True)           # garante que a pasta exista

save_path = os.path.join(save_dir, "resposta_jsearch.json")

with open(save_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"✅ Resposta salva em '{save_path}'")
