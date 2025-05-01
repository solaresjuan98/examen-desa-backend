import os
import json


BASE_KNOWLEDGE_DIR = "/Users/juansolares/courses/prueba-innovacion/backend/momostenango-project/app/knowledge_base"


async def list_knowledge_files():
    """Lista los archivos disponibles en knowledge_base/."""
    files = []
    for file in os.listdir(BASE_KNOWLEDGE_DIR):
        if file.endswith(".json"):
            files.append(file)
    return files


async def load_knowledge_file(filename: str):
    """Carga el contenido de un archivo específico."""
    filepath = os.path.join(BASE_KNOWLEDGE_DIR, filename)
    
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


async def search_knowledge(query: str):
    """Busca de manera creativa en todos los archivos relacionados con la consulta."""
    files = await list_knowledge_files()
    resultados = []

    for file in files:
        contenido = await load_knowledge_file(file)
        contenido_textual = json.dumps(contenido).lower()

        if query.lower() in contenido_textual:
            resultados.append({
                "archivo": file,
                "contenido": contenido
            })

    return resultados
