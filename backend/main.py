from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from .database import engine, get_session
from .models import SQLModel, Personagem
from fastapi.staticfiles import StaticFiles 

# --- LISTA MESTRA DE COMPETÊNCIAS ---
LISTA_COMPETENCIAS = [
    "Acrobacia", "Adestramento", "Atletismo", "Atuação", "Cavalgar", 
    "Conhecimento", "Cura", "Diplomacia", "Enganação", "Fortitude", 
    "Furtividade", "Tática", "Intimidação", "Intuição", "Investigação", 
    "Jogatina", "Ladinagem", "Feitiçaria", "Nobreza", "Percepção", 
    "Pilotagem", "Reflexos", "Religião", "Sobrevivência", "Vontade"
]

# Lifespan do Servidor
@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)

# --- CONFIGURAÇÃO DE ARQUIVOS ---
BASE_DIR = Path(__file__).resolve().parent.parent 
TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"
STATIC_DIR = BASE_DIR / "frontend" / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# --- FUNÇÕES AUXILIARES ---

# Processa as listas de Ataques, Habilidades e Inventário do form
def processar_listas(form_data):
    # Processar Ataques (5 slots) com NOVAS COLUNAS
    lista_ataques = []
    for i in range(5):
        nome = form_data.get(f"ataque_nome_{i}")
        if nome: 
            lista_ataques.append({
                "nome": nome,
                "atributo": form_data.get(f"ataque_attr_{i}") or "-",
                "acerto": form_data.get(f"ataque_acerto_{i}") or "+0",
                "dano": form_data.get(f"ataque_dano_{i}") or "-",
                "explosivo": form_data.get(f"ataque_explosivo_{i}") or "-", 
                "margem": form_data.get(f"ataque_margem_{i}") or "20",       
                "alcance": form_data.get(f"ataque_alcance_{i}") or "-"       
            })

    # Processar Habilidades (5 slots)
    lista_habilidades = []
    for i in range(5):
        nome = form_data.get(f"hab_nome_{i}")
        if nome:
            lista_habilidades.append({
                "nome": nome,
                "custo": form_data.get(f"hab_custo_{i}") or "-",
                "efeito": form_data.get(f"hab_efeito_{i}") or "-"
            })

    # Processar Inventário (10 slots) com ESPAÇOS
    lista_inventario = []
    for i in range(10):
        nome = form_data.get(f"item_nome_{i}")
        if nome:
            lista_inventario.append({
                "nome": nome,
                "qtd": form_data.get(f"item_qtd_{i}") or "1",
                "espacos": form_data.get(f"item_slot_{i}") or "0" 
            })
            
    return lista_ataques, lista_habilidades, lista_inventario

# --- ROTAS ---

# ROTA HOME (Menu de Seleção)
@app.get("/", response_class=HTMLResponse)
def home(request: Request, session: Session = Depends(get_session)):
    statement = select(Personagem)
    resultados = session.exec(statement).all()
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"personagens": resultados}
    )

# ROTA VISUALIZAR FICHA 
@app.get("/ficha/{char_id}", response_class=HTMLResponse)
def visualizar_ficha(request: Request, char_id: int, session: Session = Depends(get_session)):
    personagem = session.get(Personagem, char_id)
    if not personagem:
        return RedirectResponse("/")
    
    return templates.TemplateResponse(
        request=request, 
        name="ficha.html", 
        context={"ficha": personagem}
    )

# ROTA POST (API)
@app.post("/personagem/", response_model=Personagem)
def criar_personagem(personagem: Personagem, session: Session = Depends(get_session)):
    session.add(personagem)
    session.commit()
    session.refresh(personagem)
    return personagem

# ROTA API LISTAR
@app.get("/api/personagem/", response_model=list[Personagem])
def listar_personagens_api(session: Session = Depends(get_session)):
    statement = select(Personagem)
    resultados = session.exec(statement).all()
    return resultados

# --- ROTAS DE FORMULÁRIO (WEB) ---

# GET - Página de Cadastro
@app.get("/novo", response_class=HTMLResponse)
def pagina_cadastro(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="cadastro.html", 
        context={"lista_skills": LISTA_COMPETENCIAS}
    )

# POST - Processar Cadastro
@app.post("/enviar_cadastro")
async def processar_formulario(request: Request, session: Session = Depends(get_session)):
    form_data = await request.form()
    
    # Processa as Competências
    competencias_selecionadas = {}
    for skill in LISTA_COMPETENCIAS:
        valor_str = form_data.get(skill)
        # Se tem valor converte pra int, senao salva 0
        if valor_str:
            competencias_selecionadas[skill] = int(valor_str)
        else:
            competencias_selecionadas[skill] = 0

    # Processar as novas listas dinâmicas
    ataques, habilidades, inventario = processar_listas(form_data)

    novo_char = Personagem(
        nome=form_data.get("nome"),
        jogador=form_data.get("jogador"),
        raca=form_data.get("raca"),
        classe=form_data.get("classe"),
        nivel=int(form_data.get("nivel")),
        
        antecedente=form_data.get("antecedente"),
        guardiao=form_data.get("guardiao"),
        ascensao=form_data.get("ascensao"),

        forca=int(form_data.get("forca")),
        destreza=int(form_data.get("destreza")),
        constituicao=int(form_data.get("constituicao")),
        inteligencia=int(form_data.get("inteligencia")),
        sabedoria=int(form_data.get("sabedoria")),
        carisma=int(form_data.get("carisma")),

        defesa=int(form_data.get("defesa")),
        experiencia=int(form_data.get("experiencia")),

        competencias=competencias_selecionadas,
        
        ataques=ataques,
        habilidades=habilidades,
        inventario=inventario,
        notas=form_data.get("notas"),

        pv_max=int(form_data.get("pv_max")),
        pv_atual=int(form_data.get("pv_max")),
        pa_max=int(form_data.get("pa_max")),
        pa_atual=int(form_data.get("pa_max")),
        ph_max=int(form_data.get("ph_max")),
        ph_atual=int(form_data.get("ph_max")),
        pg_max=int(form_data.get("pg_max")),
        pg_atual=int(form_data.get("pg_max")),
    )

    session.add(novo_char)
    session.commit()
    return RedirectResponse("/", status_code=303)

# --- ROTA DE EXCLUIR ---
@app.post("/deletar/{char_id}")
def deletar_personagem(char_id: int, session: Session = Depends(get_session)):
    personagem = session.get(Personagem, char_id)
    if personagem:
        session.delete(personagem)
        session.commit()
    return RedirectResponse("/", status_code=303)

# --- ROTAS DE EDIÇÃO ---

# GET - Página de Edição
@app.get("/editar/{char_id}", response_class=HTMLResponse)
def pagina_editar(request: Request, char_id: int, session: Session = Depends(get_session)):
    personagem = session.get(Personagem, char_id)
    if not personagem:
        return RedirectResponse("/")
    
    return templates.TemplateResponse(
        request=request, 
        name="editar.html", 
        context={"ficha": personagem, "lista_skills": LISTA_COMPETENCIAS} 
    )

# POST - Salvar Edição
@app.post("/atualizar_cadastro/{char_id}")
async def atualizar_personagem(
    request: Request, 
    char_id: int, 
    session: Session = Depends(get_session)
):
    personagem = session.get(Personagem, char_id)
    if not personagem:
        return RedirectResponse("/")
    
    form_data = await request.form()

    personagem.nome = form_data.get("nome")
    personagem.jogador = form_data.get("jogador")
    personagem.raca = form_data.get("raca")
    personagem.classe = form_data.get("classe")
    personagem.nivel = int(form_data.get("nivel"))
    
    personagem.antecedente = form_data.get("antecedente")
    personagem.guardiao = form_data.get("guardiao")
    personagem.ascensao = form_data.get("ascensao")

    personagem.forca = int(form_data.get("forca"))
    personagem.destreza = int(form_data.get("destreza"))
    personagem.constituicao = int(form_data.get("constituicao"))
    personagem.inteligencia = int(form_data.get("inteligencia"))
    personagem.sabedoria = int(form_data.get("sabedoria"))
    personagem.carisma = int(form_data.get("carisma"))

    personagem.defesa = int(form_data.get("defesa"))
    personagem.experiencia = int(form_data.get("experiencia"))

    personagem.pv_max = int(form_data.get("pv_max"))
    personagem.pv_atual = int(form_data.get("pv_atual"))
    personagem.ph_max = int(form_data.get("ph_max"))
    personagem.ph_atual = int(form_data.get("ph_atual"))
    personagem.pa_max = int(form_data.get("pa_max"))
    personagem.pa_atual = int(form_data.get("pa_atual"))
    personagem.pg_max = int(form_data.get("pg_max"))
    personagem.pg_atual = int(form_data.get("pg_atual"))

    # Lógica de atualização das skills numericas
    competencias_selecionadas = {}
    for skill in LISTA_COMPETENCIAS:
        valor_str = form_data.get(skill)
        if valor_str:
            competencias_selecionadas[skill] = int(valor_str)
        else:
            competencias_selecionadas[skill] = 0
    
    personagem.competencias = competencias_selecionadas

    # Atualiza as novas listas e notas
    ataques, habilidades, inventario = processar_listas(form_data)
    personagem.ataques = ataques
    personagem.habilidades = habilidades
    personagem.inventario = inventario
    personagem.notas = form_data.get("notas")

    session.add(personagem)
    session.commit()
    
    return RedirectResponse("/", status_code=303)