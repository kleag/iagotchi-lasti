from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref

from db.base import Base
from db.base import engine, Session



class Themes(Base):
    __tablename__ = 'Themes'
    
    idStart = Column(String, primary_key=True)
    theme = Column(String, primary_key=True)
    definition = Column(String)
    
    
    def __init__(self, idStart, theme, definition):
        self.idStart = idStart
        self.theme = theme
        self.definition = definition

Base.metadata.create_all(engine)
