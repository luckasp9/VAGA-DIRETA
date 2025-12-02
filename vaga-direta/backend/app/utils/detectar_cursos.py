# utils/detectar_cursos.py

from .curso_map import CURSO_MAP

def detectar_cursos(texto: str):
    if not texto:
        return CURSO_MAP.get("__default__", ["Outros"])

    texto = texto.lower()
    encontrados = set()

    for chave, cursos in CURSO_MAP.items():
        if chave == "__default__":
            continue
        if chave in texto:
            for c in cursos:
                encontrados.add(c)

    if not encontrados:
        return CURSO_MAP.get("__default__", ["Outros"])

    return sorted(list(encontrados))
