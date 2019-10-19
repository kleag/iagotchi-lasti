"""
Script used to send request to wikipedia.
"""
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
        


