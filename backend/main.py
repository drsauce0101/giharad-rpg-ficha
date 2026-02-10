from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse # <--- Importante pra funcionar o Delete
from sqlmodel import Session, select
from .database import engine, get_session
from .models import SQLModel, Personagem

# Lifespan do Servidor (roda automaticamente quando starta)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Builda as tabelas
    SQLModel.metadata.create_all(engine)
    yield

# API
app = FastAPI(lifespan=lifespan)

# Configuração Visual (diz pro FastAPI procurar os HTMLs dentro da pasta frontend/templates)
BASE_DIR = Path(__file__).resolve().parent.parent 
TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# --- ROTAS ---

# ROTA HOME: Retorna HTML com as fichas
@app.get("/", response_class=HTMLResponse)
def home(request: Request, session: Session = Depends(get_session)):
    # Busca todos os personagens no banco
    statement = select(Personagem)
    resultados = session.exec(statement).all()
    
    # Renderiza o HTML passando a lista de personagens
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"personagens": resultados}
    )

# ROTA POST: Criação do personagem (API/Swagger)
@app.post("/personagem/", response_model=Personagem)
def criar_personagem(personagem: Personagem, session: Session = Depends(get_session)):
    session.add(personagem)      # Prepara o salvamento
    session.commit()             # Salva no banco de verdade
    session.refresh(personagem)  # Atualiza o objeto e pega o ID gerado
    return personagem

# ROTA GET (API): Lista tudo em JSON (para futuros debugs)
@app.get("/api/personagem/", response_model=list[Personagem])
def listar_personagens_api(session: Session = Depends(get_session)):
    statement = select(Personagem)
    resultados = session.exec(statement).all()
    return resultados

# --- ROTAS DE FORMULÁRIO (WEB) ---

# GET - Página de Cadastro
@app.get("/novo", response_class=HTMLResponse)
def pagina_cadastro(request: Request):
    return templates.TemplateResponse(request=request, name="cadastro.html")

# POST - Processar Cadastro
@app.post("/enviar_cadastro")
def processar_formulario(
    session: Session = Depends(get_session),
    nome: str = Form(...),
    jogador: str = Form(...),
    raca: str = Form(...),
    classe: str = Form(...),
    nivel: int = Form(1),
    forca: int = Form(4),
    destreza: int = Form(4),
    constituicao: int = Form(4),
    inteligencia: int = Form(4),
    sabedoria: int = Form(4),
    carisma: int = Form(4),
    pv_max: int = Form(10),
    pa_max: int = Form(0),
    ph_max: int = Form(0),
    pg_max: int = Form(0)
):
    # Cria o objeto Python
    novo_char = Personagem(
        nome=nome,
        jogador=jogador,
        raca=raca,
        classe=classe,
        nivel=nivel,
        forca=forca,
        destreza=destreza,
        constituicao=constituicao,
        inteligencia=inteligencia,
        sabedoria=sabedoria,
        carisma=carisma,
        
        # Status
        pv_max=pv_max,
        pv_atual=pv_max,
        pa_max=pa_max,
        pa_atual=pa_max,
        ph_max=ph_max,
        ph_atual=ph_max,
        pg_max=pg_max,
        pg_atual=pg_max
    )

    # Salva no Banco
    session.add(novo_char)
    session.commit()

    # REDIRECT: Manda o navegador voltar para a Home
    return RedirectResponse("/", status_code=303)

# --- ROTA DE EXCLUIR ---
@app.post("/deletar/{char_id}")
def deletar_personagem(char_id: int, session: Session = Depends(get_session)):
    # Busco o personagem no banco pelo ID
    personagem = session.get(Personagem, char_id)
    
    if personagem:
        # Removo o item e confirmo a transação
        session.delete(personagem)
        session.commit()
    
    # Redireciono pra home pra ver a lista atualizada
    return RedirectResponse("/", status_code=303)