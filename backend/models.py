from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import JSON, Column

class Personagem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # --- CABEÇALHO COMPLETO ---
    nome: str
    jogador: str
    raca: str
    classe: str
    nivel: int = Field(default=1)
    
    # Identidade
    antecedente: str = Field(default="")
    guardiao: str = Field(default="")
    ascensao: str = Field(default="")

    # --- ATRIBUTOS ---
    forca: int = Field(default=4)
    destreza: int = Field(default=4)
    constituicao: int = Field(default=4)
    inteligencia: int = Field(default=4)
    sabedoria: int = Field(default=4)
    carisma: int = Field(default=4)

    # --- COMBATE E PROGRESSO ---
    defesa: int = Field(default=10)
    experiencia: int = Field(default=0)

    # --- COMPETÊNCIAS (PERÍCIAS) ---
    competencias: dict = Field(default={}, sa_column=Column(JSON))

    # --- BARRAS VITAIS ---
    pv_max: int = Field(default=10)
    pv_atual: int = Field(default=10)
    ph_max: int = Field(default=0)
    ph_atual: int = Field(default=0)
    pg_max: int = Field(default=0)
    pg_atual: int = Field(default=0)
    pa_max: int = Field(default=0)
    pa_atual: int = Field(default=0)