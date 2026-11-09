from app.database import engine, SessionLocal
from app.models import Base, Tester

Base.metadata.create_all(bind=engine)
db = SessionLocal()
for i in range(1, 21):
    token_name = f"tester{i:02d}"
    if not db.query(Tester).filter(Tester.token == token_name).first():
        db.add(Tester(token=token_name))
db.commit()
print("🐝 ¡20 Testers creados exitosamente!")
