from typing import Optional, Dict, List
from sqlmodel import Field, SQLModel, JSON

# -- MODELOS DE DADOS --
class Personagem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Identificação
    nome: str
    jogador: str
    raca: str
    classe: str
    nivel: int = 1
    
    # Lore
    antecedente: Optional[str] = None
    guardiao: Optional[str] = None
    ascensao: Optional[str] = None
    
    # Atributos (d4, d6, etc...)
    forca: int
    destreza: int
    constituicao: int
    inteligencia: int
    sabedoria: int
    carisma: int

    # Status de Combate
    defesa: int
    experiencia: int

    # Barras de Status (Máximos e Atuais)
    pv_max: int
    pv_atual: int
    pa_max: int
    pa_atual: int
    ph_max: int
    ph_atual: int
    pg_max: int
    pg_atual: int

    # -- LISTAS ESPECIAIS --
    competencias: Dict[str, int] = Field(default={}, sa_type=JSON)
    
    # Lista de Ataques: 
    ataques: List[Dict[str, str]] = Field(default=[], sa_type=JSON)
    
    # Lista de Habilidades: 
    habilidades: List[Dict[str, str]] = Field(default=[], sa_type=JSON)
    
    # Lista de Itens: 
    inventario: List[Dict[str, str]] = Field(default=[], sa_type=JSON)
    
    # Texto Livre
    notas: Optional[str] = Field(default="", sa_column_kwargs={"nullable": True})