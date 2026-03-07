from sqlalchemy import text
from sqlmodel import Session
from backend.database import engine
from sqlalchemy import inspect

print("Iniciando migracao manual...")
inspector = inspect(engine)
if inspector.has_table("personagem"):
    columns = [col['name'] for col in inspector.get_columns('personagem')]
    with Session(engine) as session:
        if 'usuario_id' not in columns:
            session.exec(text("ALTER TABLE personagem ADD COLUMN usuario_id INTEGER DEFAULT NULL"))
            print("Adicionado usuario_id")
        if 'is_active' not in columns:
            session.exec(text("ALTER TABLE personagem ADD COLUMN is_active BOOLEAN DEFAULT false"))
            print("Adicionado is_active")
        session.commit()
print("Sucesso!")
