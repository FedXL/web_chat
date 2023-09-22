from sqlalchemy import create_engine


from base.models import Base
from config.config_app import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME

DB_URL2 = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
crate_db_engine = create_engine(DB_URL2)
if __name__ == "__main__":
    Base.metadata.create_all(crate_db_engine)