import base64
from openai import OpenAI

# Abre la imagen local y convierte a base64
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Ruta de la imagen local
image_path = "/Users/juansolares/courses/prueba-innovacion/backend/img/chat.png"  # Cambia esta ruta por la ubicación de tu imagen

# Convierte la imagen a base64
image_base64 = image_to_base64(image_path)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

completion = client.chat.completions.create(
    model="qwen/qwen2.5-vl-32b-instruct:free",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe el contenido de esta imagen:"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    },
                },
            ],
        }
    ]
)
# Imprime la respuesta
print(completion.choices[0].message.content)
# completion = client.chat.completions.create(
#     # extra_headers={
#     #     "HTTP-Referer": "<YOUR_SITE_URL>",  # Optional. Site URL for rankings on openrouter.ai.
#     #     "X-Title": "<YOUR_SITE_NAME>",  # Optional. Site title for rankings on openrouter.ai.
#     # },
#     extra_body={},
#     model="qwen/qwen2.5-vl-32b-instruct:free",
#     messages=[
#         {
#             "role": "user",
#             "content": [
#                 {"type": "text", "text": "What is in this image?"},
#                 {
#                     "type": "image_url",
#                     "image_url": {
#                         "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
#                     },
#                 },
#             ],
#         }
#     ],
# )
# print(completion.choices[0].message.content)
