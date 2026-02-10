from typing import Optional
from sqlmodel import Field, SQLModel

class Personagem (SQLModel, table = True):
    id: Optional [int] = Field (default=None, primary_key=True)

    # Caracteristicas Basicas
    nome: str
    jogador: str
    raca: str
    classe: str 
    nivel: int = Field (default=1)
    antecedente: Optional[str] = None 

    # Atributos (Aqui os numeros são os LADOS do dado, só pra constar)

    forca = int = Field(default=4)
    destreza = int = Field(default=4)
    constituicao = int = Field(default=4)
    inteligencia = int = Field(default=4)
    sabedoria = int = Field(default=4)
    carisma = int = Field(default=4)

    # Recursos Vitais (Vida, Ação, Hafa, Grima etc)

    # Vida (PV)
    pv_max: int = Field (default=0)
    pv_atual: int = Field (default=0)

    # Ações (PA)
    pa_max: int = Field (default=0)
    pa_atual: int = Field (default=0)

    # Hafa (PH)
    ph_max: int = Field (default=0)
    ph_atual: int = Field (default=0)

    # Grima (PG)
    pg_max: int = Field (default=0)
    pg_atual: int = Field (default=0)

    ## Nota mental: criar tabela pras competências depois porque agora to com preguiça



