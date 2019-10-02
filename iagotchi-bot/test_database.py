
import datetime
from db.user import User
from db.themes import Themes
from db.base import Base, engine, Session
from sqlalchemy import exists, and_
import pandas as pd

dbsession = Session()
user = dbsession.query(exists().where(Themes.theme=='vie')).all()
res = pd.read_sql(
            dbsession.query(Themes).filter(
            Themes.theme == 'vie').statement, dbsession.bind)

for r in res['definition']:
    print(r)
print(len(res))
