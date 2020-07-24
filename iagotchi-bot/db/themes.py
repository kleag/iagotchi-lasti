#
# Copyright 2020 CEA LIST
# This file is part of Iagotchi-bot.
# Iagotchi-bot is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# Iagotchi-bot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with Iagotchi-bot.  If not, see <http://www.gnu.org/licenses/>
# 
#

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
