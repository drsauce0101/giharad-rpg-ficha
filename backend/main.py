from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Depends, Request, Form, Body # Adicionado Body
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from .database import engine, get_session
from .models import SQLModel, Personagem
from fastapi.staticfiles import StaticFiles 

# LISTA MESTRA DE COMPETÊNCIAS
LISTA_COMPETENCIAS = [
    "Acrobacia", "Adestramento", "Atletismo", "Atuação", "Cavalgar", 
    "Conhecimento", "Cura", "Diplomacia", "Enganação", "Fortitude", 
    "Furtividade", "Tática", "Intimidação", "Intuição", "Investigação", 
    "Jogatina", "Ladinagem", "Feitiçaria", "Nobreza", "Percepção", 
    "Pilotagem", "Reflexos", "Religião", "Sobrevivência", "Vontade"
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)

BASE_DIR = Path(__file__).resolve().parent.parent 
TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"
STATIC_DIR = BASE_DIR / "frontend" / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

def safe_int(value, default=0):
    try:
        if value is None or str(value).strip() == "":
            return default
        return int(value)
    except (ValueError, TypeError):
        return default

def processar_listas(form_data):
    lista_ataques = []
    for i in range(100):
        nome = form_data.get(f"ataque_nome_{i}")
        if not nome: continue
        lista_ataques.append({
            "nome": nome,
            "atributo": form_data.get(f"ataque_attr_{i}") or "-",
            "acerto": form_data.get(f"ataque_acerto_{i}") or "+0",
            "dano": form_data.get(f"ataque_dano_{i}") or "-",
            "explosivo": form_data.get(f"ataque_explosivo_{i}") or "-",
            "margem": form_data.get(f"ataque_margem_{i}") or "20",
            "alcance": form_data.get(f"ataque_alcance_{i}") or "-"
        })

    lista_habilidades = []
    for i in range(100):
        nome = form_data.get(f"hab_nome_{i}")
        if not nome: continue
        lista_habilidades.append({
            "nome": nome,
            "custo": form_data.get(f"hab_custo_{i}") or "-",
            "efeito": form_data.get(f"hab_efeito_{i}") or "-"
        })

    lista_inventario = []
    for i in range(100):
        nome = form_data.get(f"item_nome_{i}")
        if not nome: continue
        lista_inventario.append({
            "nome": nome,
            "qtd": form_data.get(f"item_qtd_{i}") or "1",
            "espacos": form_data.get(f"item_slot_{i}") or "0"
        })

    lista_magias = []
    for i in range(100):
        nome = form_data.get(f"magia_nome_{i}")
        if not nome: continue
        lista_magias.append({
            "nome": nome,
            "circulo": form_data.get(f"magia_circulo_{i}") or "1",
            "alcance": form_data.get(f"magia_alcance_{i}") or "-",
            "efeito": form_data.get(f"magia_efeito_{i}") or "-"
        })
            
    return lista_ataques, lista_habilidades, lista_inventario, lista_magias

@app.get("/", response_class=HTMLResponse)
def home(request: Request, session: Session = Depends(get_session)):
    statement = select(Personagem)
    resultados = session.exec(statement).all()
    return templates.TemplateResponse(request=request, name="index.html", context={"personagens": resultados})

@app.get("/ficha/{char_id}", response_class=HTMLResponse)
def visualizar_ficha(request: Request, char_id: int, session: Session = Depends(get_session)):
    personagem = session.get(Personagem, char_id)
    if not personagem: return RedirectResponse("/")
    return templates.TemplateResponse(request=request, name="ficha.html", context={"ficha": personagem})

@app.get("/novo", response_class=HTMLResponse)
def pagina_cadastro(request: Request):
    return templates.TemplateResponse(request=request, name="cadastro.html", context={"lista_skills": LISTA_COMPETENCIAS})

@app.post("/enviar_cadastro")
async def processar_formulario(request: Request, session: Session = Depends(get_session)):
    form_data = await request.form()
    competencias_selecionadas = {s: safe_int(form_data.get(s)) for s in LISTA_COMPETENCIAS}
    ataques, habilidades, inventario, magias = processar_listas(form_data)

    # Processamento dos Marcadores Unificados (0 a 4)
    morte_val = sum(1 for i in range(1, 5) if form_data.get(f"morte_{i}"))
    fadiga_val = sum(1 for i in range(1, 5) if form_data.get(f"fadiga_{i}"))
    cicatrizes_val = sum(1 for i in range(1, 5) if form_data.get(f"cicatriz_{i}"))

    novo_char = Personagem(
        nome=form_data.get("nome"),
        jogador=form_data.get("jogador"),
        raca=form_data.get("raca"),
        classe=form_data.get("classe"),
        nivel=safe_int(form_data.get("nivel"), 1),
        antecedente=form_data.get("antecedente"),
        guardiao=form_data.get("guardiao"),
        ascensao=form_data.get("ascensao"),
        forca=safe_int(form_data.get("forca"), 4),
        destreza=safe_int(form_data.get("destreza"), 4),
        constituicao=safe_int(form_data.get("constituicao"), 4),
        inteligencia=safe_int(form_data.get("inteligencia"), 4),
        sabedoria=safe_int(form_data.get("sabedoria"), 4),
        carisma=safe_int(form_data.get("carisma"), 4),
        defesa=safe_int(form_data.get("defesa"), 10),
        experiencia=safe_int(form_data.get("experiencia"), 0),
        pv_max=safe_int(form_data.get("pv_max"), 1), pv_atual=safe_int(form_data.get("pv_max"), 1),
        ph_max=safe_int(form_data.get("ph_max"), 0), ph_atual=safe_int(form_data.get("ph_max"), 0),
        pa_max=safe_int(form_data.get("pa_max"), 0), pa_atual=safe_int(form_data.get("pa_max"), 0),
        pg_max=safe_int(form_data.get("pg_max"), 0), pg_atual=safe_int(form_data.get("pg_max"), 0),
        # Campos de marcadores numéricos
        marcadores_morte=morte_val,
        marcadores_fadiga=fadiga_val,
        marcadores_cicatrizes=cicatrizes_val,
        competencias=competencias_selecionadas,
        ataques=ataques, habilidades=habilidades, inventario=inventario, magias=magias,
        notas=form_data.get("notas"),
        tradicao=form_data.get("tradicao"),
        escolas=form_data.get("escolas"),
        atributo_chave=form_data.get("atributo_chave") or "Inteligencia",
        cd_magia=safe_int(form_data.get("cd_magia"), 10),
        slots_nv1=safe_int(form_data.get("slots_nv1")),
        slots_nv2=safe_int(form_data.get("slots_nv2")),
        slots_nv3=safe_int(form_data.get("slots_nv3")),
        slots_nv4=safe_int(form_data.get("slots_nv4")),
        slots_nv5=safe_int(form_data.get("slots_nv5")),
        slots_nv6=safe_int(form_data.get("slots_nv6")),
    )
    session.add(novo_char)
    session.commit()
    return RedirectResponse("/", status_code=303)

@app.post("/atualizar_cadastro/{char_id}")
async def atualizar_personagem(request: Request, char_id: int, session: Session = Depends(get_session)):
    personagem = session.get(Personagem, char_id)
    if not personagem: return RedirectResponse("/")
    form_data = await request.form()

    # Campos básicos
    personagem.nome = form_data.get("nome")
    personagem.jogador = form_data.get("jogador")
    personagem.raca = form_data.get("raca")
    personagem.classe = form_data.get("classe")
    personagem.nivel = safe_int(form_data.get("nivel"), 1)
    personagem.antecedente = form_data.get("antecedente")
    personagem.guardiao = form_data.get("guardiao")
    personagem.ascensao = form_data.get("ascensao")
    
    # Atributos e Status
    personagem.forca = safe_int(form_data.get("forca"), 4)
    personagem.destreza = safe_int(form_data.get("destreza"), 4)
    personagem.constituicao = safe_int(form_data.get("constituicao"), 4)
    personagem.inteligencia = safe_int(form_data.get("inteligencia"), 4)
    personagem.sabedoria = safe_int(form_data.get("sabedoria"), 4)
    personagem.carisma = safe_int(form_data.get("carisma"), 4)
    personagem.defesa = safe_int(form_data.get("defesa"), 10)
    personagem.experiencia = safe_int(form_data.get("experiencia"), 0)
    
    personagem.pv_max = safe_int(form_data.get("pv_max"), 1)
    personagem.pv_atual = safe_int(form_data.get("pv_atual"), 1)
    personagem.ph_max = safe_int(form_data.get("ph_max"), 0)
    personagem.ph_atual = safe_int(form_data.get("ph_atual"), 0)
    personagem.pa_max = safe_int(form_data.get("pa_max"), 0)
    personagem.pa_atual = safe_int(form_data.get("pa_atual"), 0)
    personagem.pg_max = safe_int(form_data.get("pg_max"), 0)
    personagem.pg_atual = safe_int(form_data.get("pg_atual"), 0)

    # Atualização dos Marcadores (Contagem de checkboxes morte_i, fadiga_i, cicatriz_i)
    personagem.marcadores_morte = sum(1 for i in range(1, 5) if form_data.get(f"morte_{i}"))
    personagem.marcadores_fadiga = sum(1 for i in range(1, 5) if form_data.get(f"fadiga_{i}"))
    personagem.marcadores_cicatrizes = sum(1 for i in range(1, 5) if form_data.get(f"cicatriz_{i}"))

    # Competências
    personagem.competencias = {s: safe_int(form_data.get(s)) for s in LISTA_COMPETENCIAS}

    # Listas Dinâmicas
    ataques, habilidades, inventario, magias = processar_listas(form_data)
    personagem.ataques = ataques
    personagem.habilidades = habilidades
    personagem.inventario = inventario
    personagem.magias = magias
    personagem.notas = form_data.get("notas")

    # Magia
    personagem.tradicao = form_data.get("tradicao")
    personagem.escolas = form_data.get("escolas")
    personagem.atributo_chave = form_data.get("atributo_chave")
    personagem.cd_magia = safe_int(form_data.get("cd_magia"), 10)
    personagem.slots_nv1 = safe_int(form_data.get("slots_nv1"))
    personagem.slots_nv2 = safe_int(form_data.get("slots_nv2"))
    personagem.slots_nv3 = safe_int(form_data.get("slots_nv3"))
    personagem.slots_nv4 = safe_int(form_data.get("slots_nv4"))
    personagem.slots_nv5 = safe_int(form_data.get("slots_nv5"))
    personagem.slots_nv6 = safe_int(form_data.get("slots_nv6"))

    session.add(personagem)
    session.commit()
    return RedirectResponse("/", status_code=303)

@app.post("/deletar/{char_id}")
def deletar_personagem(char_id: int, session: Session = Depends(get_session)):
    personagem = session.get(Personagem, char_id)
    if personagem:
        session.delete(personagem)
        session.commit()
    return RedirectResponse("/", status_code=303)

@app.get("/editar/{char_id}", response_class=HTMLResponse)
def pagina_editar(request: Request, char_id: int, session: Session = Depends(get_session)):
    personagem = session.get(Personagem, char_id)
    if not personagem: return RedirectResponse("/")
    return templates.TemplateResponse(request=request, name="editar.html", context={"ficha": personagem, "lista_skills": LISTA_COMPETENCIAS})

@app.post("/api/atualizar_campo/{char_id}")
async def api_atualizar_campo(
    char_id: int, 
    data: dict = Body(...), 
    session: Session = Depends(get_session)
):
    personagem = session.get(Personagem, char_id)
    if not personagem:
        return {"status": "error", "message": "Personagem não encontrado"}

    for campo, valor in data.items():
        if hasattr(personagem, campo):
            # Lógica para campos que devem ser convertidos para inteiro
            campos_numericos = [
                "nivel", "forca", "destreza", "constituicao", "inteligencia", 
                "sabedoria", "carisma", "defesa", "experiencia",
                "pv_max", "pv_atual", "pa_max", "pa_atual", 
                "ph_max", "ph_atual", "pg_max", "pg_atual",
                "marcadores_morte", "marcadores_fadiga", "marcadores_cicatrizes"
            ]
            
            if campo in campos_numericos:
                setattr(personagem, campo, safe_int(valor))
            elif campo == "competencias":
                # Para dicionários de competências enviadas via API
                personagem.competencias = valor
            else:
                setattr(personagem, campo, valor)
    
    session.add(personagem)
    session.commit()
    return {"status": "success", "field": list(data.keys())[0]}