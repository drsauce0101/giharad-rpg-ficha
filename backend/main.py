from contextlib import asynccontextmanager
from fastapi import FastAPI
from .database import engine
from .models import SQLModel, Personagem # Importando o modelo do personagem

# Lifespan do Servidor (roda automaticamente quando starta)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Builda as tabelas
    SQLModel.metadata.create_all(engine)
    yield
    # Ordens de shutdown (por enquanto nenhuma)

# Começo da API
app = FastAPI(lifespan=lifespan)

# Teste no navegador pra ver se ta rodando
@app.get("/")
def home():
    return {"status": "Online", "mensagem": "Rodando"}