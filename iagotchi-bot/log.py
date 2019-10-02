
import datetime
from db.user import User
from db.themes import Themes
from db.base import Base, engine, Session
from sqlalchemy import exists, and_
import pandas as pd


print('Log init')
class Log(object):
    
    
    def __init__(self, date, botname='iagotchi'):
        self.logfile = 'data/logfile_{}_{}.txt'.format(botname, date)
        fplog = open(self.logfile, 'w')
        fplog.close()
        self.dbsession = Session()
        self.dbtables = None
        self.dbuser_idstart = date
        self.init_database()
        
        
        
    def save_in_file(self, q, a):
        with open(self.logfile, 'a', encoding='utf8') as f:
            f.write("{}\t{}\t{}\n".format(datetime.datetime.now(), q, a))
            
            
    def init_database(self):
        print('DatabaseInstance({})'.format(self.dbuser_idstart))
        #self.dbsession = session
        print('DatabaseInstance session set')
        self.dbtables = {
            'User':User
            }

        if self.dbuser_idstart is not None:
            user = self.dbsession.query(exists().where(
                User.idStart==self.dbuser_idstart)).scalar()
                
            print('DatabaseInstance tried getting pt: {}'.format(user))
            if not user:
                print('DatabaseInstance user does not exist')
                self.dbuser = User(self.dbuser_idstart)
                print('DatabaseInstance adding user to session')
                self.dbsession.add(self.dbuser)
                print('DatabaseInstance commiting session')
                self.dbsession.commit()
            else:
                print('DatabaseInstance user already exist')
        print('DatabaseInstance init done')
        
        
    def insert(self, table, field, val):
        print('DatabaseInstance.insert {}, {}, {}, {}'
              .format(self.dbuser_idstart, table, field, val))
        
        try:
            self.dbsession.query(self.dbtables[table]).filter(
                    self.dbtables[table].idStart==self.dbuser_idstart).update({field:val})
        except:
            print('DatabaseInstance.insert insertion errors.')
            pass
        print('DatabaseInstance.insert commiting')
        self.dbsession.commit()
        
    def theme_insertion(self, theme, definition):
        """
        Used to add a theme and its definition collected during the conversation
        Input: theme and defintion.
        Output: True if the commit was successful else False.
        """
        print('DatabaseInstance.insert {}, themes, {}, {}'
              .format(self.dbuser_idstart, theme, definition))
        success = True
        try:
            self.theme = Themes(self.dbuser_idstart, theme, definition)
            print('DatabaseInstance adding definition of {}'.format(theme))
            self.dbsession.add(self.theme)
            print('DatabaseInstance commiting session')
            self.dbsession.commit()
        except:
            success = False
            
        return success
    
    def getDefinition(self, theme):
        """
        Funcion to get definition of theme from database. Check if theme exists in BD and return its defintion.
        Input: theme
        Ouput: defintion if theme exists else None.
        """
        print('DatabaseInstance.getDefinition {}'.format(theme))
        defintions = list()
        try:
            res = pd.read_sql(self.dbsession.query(Themes).filter(Themes.theme == theme.lower()).statement, self.dbsession.bind)
            if len(res) == 0 :
                return None
            else:
                for r in res['definition']:
                    defintions.append(r)
                return definitions
        except:
            return None
                
            
            
            

