from sqlalchemy import create_engine

DB_URL = "postgresql+psycopg2://postgres:123456@localhost:5432/matriz_unica_db"
engine = create_engine(DB_URL, connect_args={'client_encoding': 'latin1'})

def obtener_motor():
    return engine