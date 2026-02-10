from sqlmodel import SQLModel, create_engine, Session

# String de Conexão
# Formato Base: postgresql://usuario:senha@endereco:porta/nome_banco
DATABASE_URL = "postgresql://postgres:1234@localhost:5432/giharad_rpg"

# Engine
# Forçando a amostragem do terminal pra facilitar debugs posteriores (echo true).
engine = create_engine(DATABASE_URL, echo=True)

# Função base de pegar sessão
def get_session():
    with Session(engine) as session:
        yield session