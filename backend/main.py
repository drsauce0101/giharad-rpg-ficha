from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Depends, Request, Body
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select, SQLModel
from sqlalchemy import Column, JSON
from sqlalchemy.orm.attributes import flag_modified

# Importações internas
from .database import engine, get_session
from .models import Personagem

# ==============================================================================
# 1. LISTA MESTRA DE COMPETÊNCIAS (ATUALIZADA)
# ==============================================================================
LISTA_COMPETENCIAS = [
    "Vigor", "Manejo Animal", "Dissimulação", "Artimanha", 
    "Esoterismo", "Sagacidade", "Condução", "Reflexos", 
    "Fortitude", "Vontade", "Aristocracia", "Coordenação", 
    "Sobrevivência", "Medicina", "Profissão", "Idioma", "Atuação"
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)

# Configurações de Caminhos
BASE_DIR = Path(__file__).resolve().parent.parent 
TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"
STATIC_DIR = BASE_DIR / "frontend" / "static"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# ==============================================================================
# 2. UTILITÁRIOS
# ==============================================================================
def safe_int(value, default=0):
    try:
        if value is None or str(value).strip() == "":
            return default
        return int(value)
    except (ValueError, TypeError):
        return default

# ==============================================================================
# 3. ROTAS DE VISUALIZAÇÃO
# ==============================================================================
@app.get("/", response_class=HTMLResponse)
def home(request: Request, session: Session = Depends(get_session)):
    statement = select(Personagem)
    resultados = session.exec(statement).all()
    return templates.TemplateResponse(
        name="index.html", 
        context={"request": request, "personagens": resultados}
    )

@app.get("/ficha/{char_id}", response_class=HTMLResponse)
def visualizar_ficha(request: Request, char_id: int, session: Session = Depends(get_session)):
    personagem = session.get(Personagem, char_id)
    if not personagem: 
        return RedirectResponse(url="/", status_code=303)
    
    return templates.TemplateResponse(
        name="ficha.html", 
        context={
            "request": request, 
            "ficha": personagem, 
            "lista_skills": LISTA_COMPETENCIAS
        }
    )

@app.get("/novo")
def criar_personagem_direto(session: Session = Depends(get_session)):
    novo_char = Personagem(
        nome="Personagem",
        jogador="Jogador",
        raca="Nenhuma",
        classe="Nenhuma",
        nivel=1,
        fisico=4, presenca=4, carisma=4, astucia=4,
        pv_max=10, pv_atual=10,
        pa_max=3, pa_atual=3,
        defesa=10,
        competencias={s: 0 for s in LISTA_COMPETENCIAS}, # Dicionário com acentos
        ataques=[], 
        habilidades=[], 
        inventario=[], 
        magias=[], 
        notas=""
    )
    
    try:
        session.add(novo_char)
        session.commit()
        session.refresh(novo_char)
        return RedirectResponse(url=f"/ficha/{novo_char.id}", status_code=303)
    except Exception as e:
        session.rollback()
        print(f"ERRO NO BANCO: {e}")
        return {"error": str(e)}

# ==============================================================================
# 4. ROTAS DE AÇÃO
# ==============================================================================

@app.post("/deletar/{char_id}")
def deletar_personagem(char_id: int, session: Session = Depends(get_session)):
    personagem = session.get(Personagem, char_id)
    if personagem:
        session.delete(personagem)
        session.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/api/atualizar_campo/{char_id}")
async def api_atualizar_campo(
    char_id: int, 
    data: dict = Body(...), 
    session: Session = Depends(get_session)
):
    personagem = session.get(Personagem, char_id)
    if not personagem: 
        return {"status": "error"}
    
    try:
        for campo, valor in data.items():
            # Converte números se necessário
            if campo in ['nivel', 'pv_max', 'pv_atual', 'pa_max', 'pa_atual', 'defesa', 'fisico', 'presenca', 'carisma', 'astucia']:
                valor = safe_int(valor)
            
            if hasattr(personagem, campo):
                setattr(personagem, campo, valor)
                
                # Garante que o SQLAlchemy salve listas/dicionários
                if isinstance(valor, (list, dict)):
                    flag_modified(personagem, campo)
        
        session.add(personagem)
        session.commit()
        return {"status": "success"}
    
    except Exception as e:
        session.rollback()
        print(f"ERRO NO AUTO-SAVE: {e}")
        return {"status": "error", "message": str(e)}