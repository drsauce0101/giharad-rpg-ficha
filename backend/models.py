from typing import Optional
from sqlmodel import Field, SQLModel

class Personagem(SQLModel, table=True):
    # Identificador
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Cabeçalho
    nome: str
    jogador: str
    raca: str
    classe: str
    nivel: int = Field(default=1)
    antecedente: Optional[str] = None

    # Atributos Principais (Dados: 4, 6, 8, 10, 12)
    forca: int = Field(default=4)
    destreza: int = Field(default=4)
    constituicao: int = Field(default=4)
    inteligencia: int = Field(default=4)
    sabedoria: int = Field(default=4)
    carisma: int = Field(default=4)

    # Recursos Vitais
    # PV - Pontos de Vida
    pv_max: int = Field(default=10)
    pv_atual: int = Field(default=10)
    
    # PH - Pontos de Hafa
    ph_max: int = Field(default=0)
    ph_atual: int = Field(default=0)

    # PG - Pontos de Grima (NOVO)
    pg_max: int = Field(default=0)
    pg_atual: int = Field(default=0)

    # PA - Pontos de Ação (NOVO)
    pa_max: int = Field(default=0)
    pa_atual: int = Field(default=0)