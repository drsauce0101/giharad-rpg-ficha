from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends # Injeção de dependência da FastAPI
from sqlmodel import Session, select
from .database import engine, get_session # Função de conexão
from .models import SQLModel, Personagem # Importando o modelo de personagem

# Lifespan do Servidor (roda automaticamente quando starta)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Builda as tabelas
    SQLModel.metadata.create_all(engine)
    yield
    # Ordens de shutdown (por enquanto nenhuma)

# Começo da API
app = FastAPI(lifespan=lifespan)

# ROTAS

@app.get("/")
def home():
    return {"status": "Online"}

# ROTA POST: Criação do personagem

@app.post("/personagem/", response_model=Personagem)
def criar_personagem(personagem: Personagem, session: Session = Depends(get_session)):
    session.add(personagem)      # Prepara o salvamento
    session.commit()             # Salva no banco de verdade
    session.refresh(personagem)  # Atualiza o objeto e pega o ID gerado
    return personagem

# ROTA GET: Lista tudo
@app.get("/personagem/", response_model=list[Personagem])
def listar_personagens(session: Session = Depends(get_session)):
    statement = select(Personagem)
    resultados = session.exec(statement).all()
    return resultados