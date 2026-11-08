from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

# Apunta a la carpeta 'data' en la raíz
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/colmena.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Habilita WAL para que múltiples procesos (tus scripts y la API) no bloqueen la BD
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()