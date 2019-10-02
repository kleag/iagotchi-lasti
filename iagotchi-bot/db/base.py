# coding=utf-8
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import sys

file = "sqlite:///data/iagotchi.sqlite"

print('db.base Creating database file: {}'.format(file))
#print(file)
engine = create_engine(file)
engine.connect()

Session = sessionmaker(bind=engine)

Base = declarative_base()
print('db.base Base created')

sys.stdout.flush()


