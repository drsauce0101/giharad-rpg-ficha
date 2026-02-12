from typing import Optional, Dict, List, Any
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

    # Marcadores (0 a 4)
    marcadores_morte: int = 0  
    marcadores_fadiga: int = 0 
    marcadores_cicatrizes: int = 0 

    # -- LISTAS ESPECIAIS --
    competencias: Dict[str, int] = Field(default={}, sa_type=JSON)
    
    # Lista de Ataques: [{nome, dano, acerto...}]
    ataques: List[Dict[str, str]] = Field(default=[], sa_type=JSON)
    
    # Lista de Habilidades: [{nome, custo, efeito...}]
    habilidades: List[Dict[str, str]] = Field(default=[], sa_type=JSON)
    
    # Lista de Itens: [{nome, qtd, slots...}]
    inventario: List[Dict[str, str]] = Field(default=[], sa_type=JSON)
    
    # Texto Livre
    notas: Optional[str] = Field(default="", sa_column_kwargs={"nullable": True})

    # -- SISTEMA DE MAGIA (NOVO) --
    tradicao: Optional[str] = Field(default="")
    escolas: Optional[str] = Field(default="")
    
    atributo_chave: str = Field(default="Inteligência")
    cd_magia: int = Field(default=10)
    
    # Espaços de Magia (Slots Máximos)
    slots_nv1: int = Field(default=0)
    slots_nv2: int = Field(default=0)
    slots_nv3: int = Field(default=0)
    slots_nv4: int = Field(default=0)
    slots_nv5: int = Field(default=0)
    slots_nv6: int = Field(default=0)
    
    # Grimório: Lista de Magias [{nome, circulo, alcance, efeito}]
    magias: List[Dict[str, str]] = Field(default=[], sa_type=JSON)