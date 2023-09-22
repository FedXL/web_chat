from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config.config_app import DB_URL, DB_TEST

async_engine = create_async_engine(DB_URL, echo=False)
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)
async_test_engine = create_async_engine(DB_TEST, echo=False)




