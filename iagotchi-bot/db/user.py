#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 14:49:36 2018

@author: frejus
"""

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
