from blacksheep import Application
from app.routes import register_routes
from dotenv import load_dotenv
from app.db import db
from blacksheep.server.cors import CORSPolicy

load_dotenv()

app = Application()

cors_policy = CORSPolicy(
    allow_origins=["*"],  # Permitir todos los orígenes
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Métodos permitidos
    allow_headers=["*"],  # Permitir todos los encabezados
    allow_credentials=True,  # Permitir credenciales
)


app.use_cors(
    allow_origins="*",  # Permitir todos los orígenes (en dev)
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers="*",  # Permitir todos los headers
    allow_credentials=True,
)


@app.on_start
async def app_startup():
    register_routes(app)
    await db.connect()
    print("Database connected")


@app.on_stop
async def app_shutdown():
    await db.disconnect()
    print("Database disconnected")
