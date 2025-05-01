# examen-desa-backend

# Idea general del proyecto

Desarrollar un agente AI multimodal para apoyar a la Municipalidad de Momostenango, permitiendo consultas inteligentes sobre reglamentos, trámites y documentación usando texto, imágenes o archivos PDF.

El prototipo extrae conocimiento estructurado de múltiples fuentes usando LLMs gratuitos y ejecuta inferencias sobre documentos mediante un protocolo de contexto (MCP).



# 🤖 Agente AI Multimodal para la Municipalidad de Momostenango

Este proyecto es un prototipo funcional de agente de inteligencia artificial multimodal desarrollado usando:

- [BlackSheep](https://www.neoteroi.dev/blacksheep/): servidor HTTP asincrónico.
- [Agno](https://github.com/agneum/agno): orquestador de agentes inteligentes.
- [PostgreSQL + pgvector](https://github.com/pgvector/pgvector): almacenamiento vectorial para consultas semánticas.
- Modelos gratuitos (etiquetados como `:free`) disponibles en [OpenRouter](https://openrouter.ai/).

---

## ⚙️ Configuración del entorno

## Estructura del proyecto
```
momostenango-project/
│
├── app/
│   ├── knowledge_base/                     # Repositorio de archivos JSON para consultas
│   │   ├── citas_identidad.json
│   │   ├── impuestos_tasas_reglamentos.json
│   │   ├── impuestos_vehiculares.json
│   │   ├── index.json
│   │   ├── plantillas_tramites.json
│   │   ├── recoleccion_basura.json
│   │   ├── reporte_incidencias.json
│   │   └── tramites_construccion.json
│   │
│   ├── agent.py                            # Orquestador del agente (Agno)
│   ├── db.py                               # Conexión y queries a PostgreSQL
│   ├── main.py                             # Punto de entrada del servidor BlackSheep
│   ├── mcp.py                              # Lógica para protocolo de exploración MCP
│   ├── preguntas.txt                       # Archivo con preguntas de ejemplo
│   ├── prueba.py                           # Script de prueba o utilidades adicionales
│   └── routes.py                           # Definición de rutas HTTP (endpoints)
│
├── db/
│   ├── ddl.sql                             # Definición de tablas y estructuras SQL
│   └── diagram.clj                         # Diagrama de entidad-relación (opcional, Clojure)
│
├── docker-compose.yml                      # Configuración de servicios (PostgreSQL, etc.)
├── .env                                    # Variables de entorno
├── requirements.txt                        # Dependencias del proyecto
└── README.md

```

### Base depositos
```yaml
version: '3.8'

services:
  postgres:
    image: ankane/pgvector:latest     # Imagen que incluye PostgreSQL + pgvector
    container_name: postgres_db       # Nombre del contenedor
    restart: always                   # Se reinicia automáticamente si se cae
    environment:
      POSTGRES_USER: usuario          # Usuario por defecto
      POSTGRES_PASSWORD: contraseña  # Contraseña del usuario
      POSTGRES_DB: mibasededatos      # Nombre de la base de datos a crear
    ports:
      - "5432:5432"                   # Expone el puerto 5432 a tu máquina
    volumes:
      - postgres_data:/var/lib/postgresql/data  # Persistencia de datos

volumes:
  postgres_data:                      # Define un volumen llamado postgres_data

```

### Ejecutar la base de datos

```
docker-compose up -d

```
### Detener la base de datos

```sh
docker-compose down

## Eliminar datos (EJECUTAR CON PRECAUCIÓN)
docker-compose down -v

```

### Variables de entorno (`.env`)

```env
OPENROUTER_API_KEY=sk-or-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DATABASE_URL=postgresql://user:password@localhost:5432/chatdb
EMBEDDING_MODEL=openai/text-embedding-3-small
````
## Instalación

```sh
# Crear entorno virtual
python -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar proyecto
uvicorn app.main:app --reload
```


## Requisitos adicionales 

### Instalar pgvector 16
```sh
CREATE EXTENSION IF NOT EXISTS vector;

```

### Decisiones técnologicas

* BlackSheep: por su bajo overhead y soporte nativo a WebSockets y ASGI.
* Agno: permite orquestar agentes bajo arquitecturas jerárquicas o multi-agente.
* pgvector + PostgreSQL: ideal para almacenamiento semántico vectorial.
* OpenRouter: ofrece acceso gratuito a modelos útiles para procesamiento multimodal.
* Model Context Protocol (MCP): estrategia de exploración autónoma de directorios.

## Flujo del agente

* El usuario envía texto, imagen o PDF.
* El agente (vía Agno) identifica el tipo de entrada y delega el procesamiento.
* Se extraen embeddings (si aplica) y se consulta la base de conocimiento con pgvector.
* Se genera una respuesta natural en lenguaje humano, opcionalmente en JSON estructurado.
* Se guarda la interacción en la base PostgreSQL (ciudadano, sesión, consulta, respuesta).


## Casos de uso implementados

* Consulta sobre trámites municipales (IUSI, licencias, permisos).
* Resumen automático de reglamentos (PDF).
* Exploración autónoma de archivos JSON o TXT.
* Búsqueda semántica sobre base documental con índice pgvector.



### ✅ **Lecciones aprendidas y desafíos encontrados**

1. **Desafío: Campos `embedding` vacíos en la base de datos**
   - **Causa:** No se estaban generando correctamente los vectores o no se estaban guardando.
   - **Lección:** Es fundamental validar que la función de generación de embeddings (`generar_embedding_local` o desde la API de OpenAI) devuelva un vector antes de intentar guardarlo.
   - **Solución aplicada:** Revisar la función de generación y asegurarse de que el tipo de dato (`vector`) esté bien mapeado y que el vector no sea `None`.

2. **Desafío: Mal uso del tipo de dato en la consulta vectorial**
   - **Causa:** Se estaba enviando el vector como un string (`f"[1.0, 0.9, ...]"`) en lugar del tipo `vector` de PostgreSQL.
   - **Lección:** Convertir correctamente los datos antes de la consulta y utilizar el parámetro `$1::vector` es esencial para el funcionamiento correcto de `pgvector`.
   - **Solución aplicada:** Asegurarse de que el motor de consulta (`asyncpg` o similar) reciba un vector como lista de `floats` y no como string plano.

3. **Desafío: Configuración de múltiples clientes de OpenAI**
   - **Lección:** Al trabajar con distintos proveedores (OpenRouter y OpenAI directamente), es crucial modularizar bien las instancias del cliente y controlar qué modelo se usa en cada flujo (por ejemplo, generar embeddings localmente vs. en la nube).
   - **Mejora futura:** Centralizar en un archivo de configuración el manejo de las APIs y definir estrategias de fallback si una API falla.

4. **Desafío: Endpoints protegidos**
   - **Lección:** Si los endpoints están protegidos (autenticación), hay que validar correctamente los permisos del usuario antes de realizar la búsqueda vectorial o almacenar nuevos conocimientos.
   - **Mejora:** Implementar un middleware de autenticación reutilizable para proteger los endpoints sensibles.

---

### 🚀 **Cómo mejorar el proyecto a futuro**

- **Persistencia robusta de embeddings**: Agregar validaciones estrictas para evitar insertar `NULL` en el campo `embedding`. Incluso puedes usar triggers o constraints.
  
- **Indexación con `pgvector`**: Asegúrate de tener índices `IVFFLAT` o `HNSW` para escalar mejor cuando haya muchos registros.

- **Monitoreo de calidad del embedding**: Guardar la longitud del vector, modelo usado y un checksum para verificar si fue generado correctamente.

- **Separación de responsabilidades**: Modularizar claramente las funciones de:
  - Generación de embeddings
  - Inserción en la base de datos
  - Consultas vectoriales
  - Manejo de autenticación

- **Manejo de errores y logs**: Mejorar el logging para capturar errores en generación de embeddings y fallas en la consulta a la base.
