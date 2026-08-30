from sqlalchemy import text
from app.core.database import engine
from app.db.base import Base

def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Auto-migrate SQLite schema for missing columns
    with engine.connect() as conn:
        try:
            res = conn.execute(text("PRAGMA table_info(users)")).fetchall()
            column_names = [r[1] for r in res]
            if "name" not in column_names:
                conn.execute(text("ALTER TABLE users ADD COLUMN name VARCHAR"))
                conn.commit()
        except Exception as e:
            print("Database migration check:", e)
