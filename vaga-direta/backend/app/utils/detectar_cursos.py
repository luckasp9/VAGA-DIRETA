from .curso_map import CURSO_MAP

def detectar_cursos(texto: str) -> list[str]:
    if not texto:
        return []
    
    texto = texto.lower()
    encontrados = set()

    for key, curso in CURSO_MAP.items():
        if key in texto:
            encontrados.add(curso)

    return sorted(list(encontrados))
