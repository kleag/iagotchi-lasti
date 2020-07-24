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


