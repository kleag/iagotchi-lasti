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


class User(Base):
    __tablename__ = 'User'
    
    idStart = Column(String, primary_key=True)
    username = Column(String)

    #patient_id_start = Column(String, ForeignKey('Patient.id_start'))
    #patient_state = Column(Integer, ForeignKey('Patient.state'))
    
    #patient = relationship("Patient", backref=backref("ATCD", uselist=False), foreign_keys=[patient_id_start])
    #patientstate = relationship("Patient", foreign_keys=[patient_state])

    
    def __init__(self, idStart, username=None):
        self.idStart = idStart
        self.username = username

        
Base.metadata.create_all(engine)
