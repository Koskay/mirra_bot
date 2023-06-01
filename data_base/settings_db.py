import databases
import sqlalchemy

from local_conf.config import DB_NAME


metadata = sqlalchemy.MetaData()
engine = sqlalchemy.create_engine(f'sqlite:///{DB_NAME}')
database = databases.Database(f'sqlite:///{DB_NAME}')
# engine = sqlalchemy.create_engine(f'sqlite:///db.sqlite3')
# database = databases.Database(f'sqlite:///db.sqlite3')


# Подключение к бд
async def db_connect() -> bool:
    metadata.create_all(engine)
    if not database.is_connected:
        await database.connect()
    return database.is_connected
