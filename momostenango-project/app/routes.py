from blacksheep.server.responses import json

# from blacksheep.server.websocket import WebSocket
from app.agent import agent  # importamos el agente
from io import BytesIO
from PIL import Image
from base64 import b64encode
from openai import OpenAI
from pdf2image import convert_from_bytes
from app.db import db
from app.mcp import list_knowledge_files, load_knowledge_file, search_knowledge
import json as jsonlib
from sentence_transformers import SentenceTransformer


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
)

client2 = OpenAI(
    base_url="https://api.openai.com/v1",
)

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')  # Gratis y muy bueno


async def poblar_embeddings():


    rows = await db.fetch("SELECT id, contenido FROM knowledge_embeddings WHERE embedding IS NULL")

    for row in rows:
        vector = model.encode(row["contenido"]).tolist()
        vector_str = f"[{', '.join(str(x) for x in vector)}]"
        await db.execute(
            "UPDATE knowledge_embeddings SET embedding = $1::vector WHERE id = $2",
            vector_str,
            row["id"]
        )
        print(f"✅ Embedding actualizado para ID {row['id']}")

    await db.close()


# buscar conocimiento
def generar_embedding(text):
    print("generando embedding", text)
    response = client2.embeddings.create(
        input=text,
        model='text-embedding-3-small'
    )

    print(response)
    return response.data[0].embedding

def generar_embedding_local(text):
    print("Generando embedding localmente")
    embedding = model.encode(text).tolist()
    return embedding

async def buscar_conocimiento(texto: str):
    embedding =  generar_embedding_local(texto)
    vector_str = f"[{', '.join(str(x) for x in embedding)}]"
    query = """
        SELECT id, tipo, titulo, contenido
        FROM knowledge_embeddings
        ORDER BY embedding <-> $1::vector
        LIMIT 5;
    """
    return [dict(row) for row in await db.fetch(query, vector_str)]
    #return await db.fetch(query, vector_str)



## funciones para pdf a base 64
def pdf_to_base64(pdf_bytes):
    ###
    images = convert_from_bytes(pdf_bytes)
    resultados = []

    for image in images:
        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        img_b64 = b64encode(buffer.getvalue()).decode("utf-8")
        resultados.append(img_b64)

    return resultados


async def guardar_consulta(chat_id, pregunta, respuesta):
    # Guardar la pregunta junto con la respuesta en la base de datos
    insert_consulta_query = f"""
        insert into consultas (session_id, tipo_mensaje, contenido)
        values ({chat_id}, 'texto', '{pregunta}')
        RETURNING id;
    """
    await db.execute(insert_consulta_query)
    print("consulta guardada")

    resultado = await db.fetch("select MAX(c.id) as last_id from consultas c")
    last_id = resultado[0]["last_id"] if resultado else None
    print("id de la consulta:", last_id)
    ## todo: validar
    insert_respuesta_query = f"""
        insert into respuestas  (consulta_id, contenido, modelo_usado, confianza)
        values ({last_id}, '{respuesta}', 'qwen/qwen2.5-vl-32b-instruct:free', 95.00);
    """
    response_id = await db.execute(insert_respuesta_query)
    print("respuesta guardada con id:", response_id)

    pass


async def guardar_respuesta(chat_id, pregunta, respuesta):

    resultado = await db.fetch("select MAX(c.id) as last_id from consultas c")
    last_id = resultado[0]["last_id"] if resultado else None
    print("id de la consulta:", last_id)
    ## todo: validar
    insert_respuesta_query = f"""
        insert into respuestas  (consulta_id, contenido, modelo_usado, confianza)
        values ({last_id}, '{respuesta}', 'qwen/qwen2.5-vl-32b-instruct:free', 95.00);
    """
    response_id = await db.execute(insert_respuesta_query)
    print("respuesta guardada con id:", response_id)


async def guardar_archivo(chat_id, tipo_archivo, ruta, nombre_original):
    resultado = await db.fetch("select MAX(c.id) as last_id from consultas c")
    last_id = resultado[0]["last_id"] if resultado else None
    query = f"""
        insert into archivos (consulta_id, tipo_archivo, url_archivo, nombre_original)
        values ({last_id}, '{tipo_archivo}', 'ruta/prueba', '{nombre_original}');
    """
    print(query)
    await db.execute(query)
    print("archivo guardado")

    pass


def register_routes(app):
    @app.router.get("/")
    async def index(request):
        return json({"message": "Welcome to the API!"})

    # para consultar el agente por medio de texto
    @app.router.post("/consultar")
    async def consultar(request):

        try:
            data = await request.json()
            pregunta = data.get("pregunta", "")
            chat_id = data.get("chat_id", 1)
            respuesta = agent.run(pregunta)

            ## guardar pregunta y respuesta en la base de datos
            await guardar_consulta(chat_id, pregunta, respuesta.content)
            return json({"respuesta": respuesta.content, "status": 200}, status=200)

        except Exception as e:
            return json(
                {"error": f"Error al procesar la solicitud: {str(e)}", "status": 500},
                status=500,
            )

    @app.router.post("/analizar-imagen")
    async def analizar_imagen(request):
        form = await request.form()
        chat_id = form.get("chat_id", 1)
        # Accedemos al primer archivo en caso de que sea una lista
        image_file = (
            form.get("image")[0]
            if isinstance(form.get("image"), list)
            else form.get("image")
        )
        pregunta = form.get("pregunta") or "Describe la imagen."

        tipo_archivo = (
            image_file.content_type
        )  # Ejemplo: 'image/png' o 'application/pdf'
        nombre_archivo = image_file.file_name  # Ejemplo: 'foto_perfil.png'

        print(f"Tipo: {tipo_archivo}")
        print(f"Nombre: {nombre_archivo}")

        if not image_file:
            return json({"error": "No se recibió una imagen."}, status=400)

        try:
            # Usamos .data para acceder al contenido del archivo
            image_bytes = (
                image_file.data
            )  # Usamos .data para obtener los bytes del archivo

            # Abrimos la imagen y la procesamos
            image = Image.open(BytesIO(image_bytes))
            buffered = BytesIO()
            image.save(buffered, format="PNG")  # Guardamos la imagen en formato PNG
            img_b64 = b64encode(buffered.getvalue()).decode(
                "utf-8"
            )  # Convertimos la imagen a base64

            # Verificar que la imagen se ha convertido correctamente a base64
            print(
                f"Imagen en base64: {img_b64[:100]}..."
            )  # Solo imprimimos los primeros 100 caracteres para evitar un log muy grande
        except Exception as e:
            return json({"error": f"Error al procesar la imagen: {str(e)}"}, status=500)

        # Llamamos al agente con la imagen en base64
        try:

            completion = client.chat.completions.create(
                model="qwen/qwen2.5-vl-32b-instruct:free",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": pregunta},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img_b64}"
                                },
                            },
                        ],
                    }
                ],
            )
            respuesta = completion.choices[0].message.content
            # Log para ver la respuesta del modelo
            print(f"Respuesta del modelo: {respuesta}")
            # todo: ver como guardar la imagen
            await guardar_consulta(
                1, pregunta, respuesta
            )  # Guardar la consulta y respuesta en la base de datos
            await guardar_archivo(
                1,
                tipo_archivo.decode("utf-8"),
                "ruta/del/archivo",
                nombre_archivo.decode("utf-8"),
            )  # Guardar el archivo en la base de datos
            return json({"respuesta": respuesta, "status": 200}, status=200)
        except Exception as e:
            return json(
                {"error": f"Error al procesar la solicitud del agente: {str(e)}"},
                status=500,
            )

    @app.router.post("/analizar-pdf")
    async def analizar_pdf(request):
        form = await request.form()
        archivo_subido = form.get("archivo")
        chat_id = form.get("chat_id", 1)
        file = archivo_subido[0] if isinstance(archivo_subido, list) else archivo_subido
        pregunta = (
            form.get("pregunta")
            or "Extrae el texto de esta página del PDF y dame un resumen."
        )
        ## ¿Qué información contiene esta página del PDF?

        tipo_archivo = file.content_type  # Ejemplo: 'image/png' o 'application/pdf'
        nombre_archivo = file.file_name  # Ejemplo: 'foto_perfil.png'

        print(f"Tipo: {tipo_archivo}")
        print(f"Nombre: {nombre_archivo}")

        if not file:
            return json({"error": "No se recibió un archivo."}, status=400)

        try:
            ##
            print("")
            pdf_bytes = file.data  # Usamos .data para obtener los bytes del archivo
            imagenes_base64 = pdf_to_base64(
                pdf_bytes
            )  # Convertimos el PDF a imágenes en base64
            respuestas = []

            for idx, img_b64 in enumerate(imagenes_base64):

                print(f"Imagen {idx+1} ...")

                completion = client.chat.completions.create(
                    model="qwen/qwen2.5-vl-32b-instruct:free",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": pregunta},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{img_b64}"
                                    },
                                },
                            ],
                        }
                    ],
                )

                respuesta = completion.choices[0].message.content
                respuestas.append({"pagina": idx + 1, "respuesta": respuesta})

            ###
            contenido_concatenado = "\n\n".join([r["respuesta"] for r in respuestas])
            await guardar_consulta(chat_id, pregunta, contenido_concatenado)
            await guardar_archivo(
                1,
                tipo_archivo.decode("utf-8"),
                "ruta/del/archivo",
                nombre_archivo.decode("utf-8"),
            )

            return json({"respuestas": respuestas, "status": 200}, status=200)

        except Exception as e:
            return json(
                {"error": f"Error al procesar el archivo: {str(e)}"}, status=500
            )

    @app.router.get("/get-chats")
    async def get_chats(request):

        rows = await db.fetch("SELECT * FROM chat_sessions")

        data = [dict(row) for row in rows]

        return json(data)

    @app.router.get("/get-citizens")
    async def get_chats(request):

        rows = await db.fetch("SELECT * FROM citizens")

        data = [dict(row) for row in rows]

        return json(data)

    @app.router.get("/get-messages/chat/{id}")
    async def get_chat(request, id: int):
        # Obtener el ID de la sesión de chat desde la URL
        # id = request.path_params.get("id")

        query = f"""
            select 
                c.id, 
                c.contenido , 
                c.tipo_mensaje, 
                r.contenido as contenido_respuesta,
                r.confianza
                FROM consultas c 
                JOIN respuestas r on c.id  = r.consulta_id
            where  c.session_id  = {id}
            order by c.id asc;
        """

        rows = await db.fetch(query)

        data = [dict(row) for row in rows]

        return json(data)

    @app.router.delete("/delete-chat/{id}")
    async def delete_chat(request, id: int):
        # delete_query = """
        #     DELETE FROM archivos WHERE consulta_id IN (SELECT id FROM consultas WHERE session_id = $1);
        #     DELETE FROM respuestas WHERE consulta_id IN (SELECT id FROM consultas WHERE session_id = $1);
        #     DELETE FROM consultas WHERE session_id = $1;
        # """

        # verify_query = "SELECT COUNT(*) FROM chat_sessions WHERE id = $1"
        # result = await db.fetch(verify_query, [id])

        # if result['count'] == 0:
        #     return json({"error": "El chat no existe"}, status=404)

        # await db.execute(delete_query, [id])
        await db.execute(
        "DELETE FROM archivos WHERE consulta_id IN (SELECT id FROM consultas WHERE session_id = $1)",
        id
            )
        await db.execute(
            "DELETE FROM respuestas WHERE consulta_id IN (SELECT id FROM consultas WHERE session_id = $1)",
            id
        )
        await db.execute(
            "DELETE FROM consultas WHERE session_id = $1",
            id
        )
        return json({"success": True, "message": f"Chat {id} eliminado correctamente", "status": 200}, status=200)

    ### MCP

    @app.router.get("/knowdlege/list")
    async def list_files(request):

        files = await list_knowledge_files()
        return json({"archivos_disponibles": files, "status": 200}, status=200)

    @app.router.get("/knowledge/load/{filename}")
    async def get_file(request, filename: str):
        data = await load_knowledge_file(filename)
        if data:
            return json({"contenido": data, "status": 200}, status=200)
        else:
            return json({"error": "Archivo no encontrado", "status": 404}, status=404)

    @app.router.post("/knowledge/search")
    async def search_files(request):
        data = await request.json()
        query = data.get("query", "")
        chat_id = data.get("chat_id", 1)
        resultados = await search_knowledge(query)
        if not resultados:
            return json({"mensaje": "No se encontró información relacionada."})
        
        json_string = jsonlib.dumps(resultados, default=str)
        pregunta = "convierte este json a un listado de pasos resumido en 200 palabras sin especificar archivo, solo quiero la info " + str(json_string)
        print("pregunta:", pregunta)
        ## todo: guardar consulta en base de datos
        respuesta = agent.run(pregunta)
        print("respuesta:", respuesta)
        ## guardar pregunta y respuesta en la base de datos
        await guardar_consulta(chat_id, query, respuesta.content)

        return json({"resultados": respuesta.content, "status": 200}, status=200)


    @app.router.post("/search/vector")
    async def search_vector(request):

        data = await request.json()
        text= data.get("texto", "")
        results = await buscar_conocimiento(text)
        # buscar en los json previamente creados
        search_json_files = await search_knowledge(text)
        json_results = jsonlib.dumps(results, default=str)
        json_results2 = jsonlib.dumps(search_json_files, default=str)

        json_final = json_results + " " + json_results2
        pregunta = "convierte este json a un listado de pasos resumido en 300 palabras con la data obtenida, sin especificar origen amigo " + str(json_results)

        respuesta = agent.run(pregunta)
        return json({"resultados": respuesta.content, "status": 200}, status=200)
        #return json({"resultados": results, "status": 200}, status=200)
    
    @app.router.post("/admin/actualizar-embeddings")
    async def actualizar_embeddings(request):

        rows = await db.fetch("SELECT id, contenido FROM knowledge_embeddings WHERE embedding IS NULL")

        total = 0
        for row in rows:
            vector = model.encode(row["contenido"]).tolist()
            vector_str = f"[{', '.join(str(x) for x in vector)}]"
            await db.execute(
                "UPDATE knowledge_embeddings SET embedding = $1::vector WHERE id = $2",
                vector_str, row["id"]
            )
            total += 1

        return json({"message": f"{total} embeddings actualizados."}, status=200)