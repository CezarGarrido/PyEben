from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg://admin:admin@localhost/ebenezer"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

