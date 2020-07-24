""" Script used to send request to wikipedia. """
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

import wikipedia


class Wiki(object):
    
    def __init__(self, language='fr'):
        wikipedia.set_lang(language)
        
        
        
    def getDefinition(self, word):
        wiki_options = None
        definition = None
        try:
            definition = wikipedia.summary(word.lower(), sentences=1)
        except wikipedia.exceptions.DisambiguationError as e:
            wiki_options = e.options
        # partiellement résolu
        except wikipedia.exceptions.PageError as e:
            pass
            
            
        return definition, wiki_options, word
    
    def check_if_def_found(self, definition, wiki_options, word):
        wiki_word = None
        if wiki_options is not None and len(wiki_options) > 0:
            for wiki_option in wiki_options:
                try:
                    definition = wikipedia.summary(wiki_option, sentences=1)
                    wiki_word = wiki_option
                    break
                except:
                    pass
        return definition, wiki_word, word
        
    def run(self, word):
        d, wiki_o, w = self.getDefinition(word)
        return self.check_if_def_found(d, wiki_o, w)
        


