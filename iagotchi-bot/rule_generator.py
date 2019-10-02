import re, pickle
#from string import punctuation
from nltk.corpus import stopwords
from lima import Lima

lima = Lima()



punctuations = '''!()[]{};:"\,<>./?@#$%^&*'''



def get_stopswords():
    '''returns the veronis stopwords in unicode, or if any other value is passed, it returns the default nltk french stopwords'''
    raw_stopword_list = stopwords.words('french')
    #rw_veronis = ["Ap.", "Apr.", "GHz", "MHz", "USD", "a", "afin", "ah", "ai", "aie", "aient", "aies", "ait", "alors", "après", "as", "attendu", "au", "au-delà", "au-devant", "aucun", "aucune", "audit", "auprès", "auquel", "aura", "aurai", "auraient", "aurais", "aurait", "auras", "aurez", "auriez", "aurions", "aurons", "auront", "aussi", "autour", "autre", "autres", "autrui", "aux", "auxdites", "auxdits", "auxquelles", "auxquels", "avaient", "avais", "avait", "avant", "avec", "avez", "aviez", "avions", "avons", "ayant", "ayez", "ayons", "b", "bah", "banco", "ben", "bien", "bé", "c", "c'", "c'est", "c'était", "car", "ce", "ceci", "cela", "celle", "celle-ci", "celle-là", "celles", "celles-ci", "celles-là", "celui", "celui-ci", "celui-là", "celà", "cent", "cents", "cependant", "certain", "certaine", "certaines", "certains", "ces", "cet", "cette", "ceux", "ceux-ci", "ceux-là", "cf.", "cg", "cgr", "chacun", "chacune", "chaque", "chez", "ci", "cinq", "cinquante", "cinquante-cinq", "cinquante-deux", "cinquante-et-un", "cinquante-huit", "cinquante-neuf", "cinquante-quatre", "cinquante-sept", "cinquante-six", "cinquante-trois", "cl", "cm", "cm²", "comme", "contre", "d", "d'", "d'après", "d'un", "d'une", "dans", "de", "depuis", "derrière", "des", "desdites", "desdits", "desquelles", "desquels", "deux", "devant", "devers", "dg", "différentes", "différents", "divers", "diverses", "dix", "dix-huit", "dix-neuf", "dix-sept", "dl", "dm", "donc", "dont", "douze", "du", "dudit", "duquel", "durant", "dès", "déjà", "e", "eh", "elle", "elles", "en", "en-dehors", "encore", "enfin", "entre", "envers", "es", "est", "et", "eu", "eue", "eues", "euh", "eurent", "eus", "eusse", "eussent", "eusses", "eussiez", "eussions", "eut", "eux", "eûmes", "eût", "eûtes", "f", "fait", "fi", "flac", "fors", "furent", "fus", "fusse", "fussent", "fusses", "fussiez", "fussions", "fut", "fûmes", "fût", "fûtes", "g", "gr", "h", "ha", "han", "hein", "hem", "heu", "hg", "hl", "hm", "hm³", "holà", "hop", "hormis", "hors", "huit", "hum", "hé", "i", "ici", "il", "ils", "j", "j'", "j'ai", "j'avais", "j'étais", "jamais", "je", "jusqu'", "jusqu'au", "jusqu'aux", "jusqu'à", "jusque", "k", "kg", "km", "km²", "l", "l'", "l'autre", "l'on", "l'un", "l'une", "la", "laquelle", "le", "lequel", "les", "lesquelles", "lesquels", "leur", "leurs", "lez", "lors", "lorsqu'", "lorsque", "lui", "lès", "m", "m'", "ma", "maint", "mainte", "maintes", "maints", "mais", "malgré", "me", "mes", "mg", "mgr", "mil", "mille", "milliards", "millions", "ml", "mm", "mm²", "moi", "moins", "mon", "moyennant", "mt", "m²", "m³", "même", "mêmes", "n", "n'avait", "n'y", "ne", "neuf", "ni", "non", "nonante", "nonobstant", "nos", "notre", "nous", "nul", "nulle", "nº", "néanmoins", "o", "octante", "oh", "on", "ont", "onze", "or", "ou", "outre", "où", "p", "par", "par-delà", "parbleu", "parce", "parmi", "pas", "passé", "pendant", "personne", "peu", "plus", "plus_d'un", "plus_d'une", "plusieurs", "pour", "pourquoi", "pourtant", "pourvu", "près", "puisqu'", "puisque", "q", "qu", "qu'", "qu'elle", "qu'elles", "qu'il", "qu'ils", "qu'on", "quand", "quant", "quarante", "quarante-cinq", "quarante-deux", "quarante-et-un", "quarante-huit", "quarante-neuf", "quarante-quatre", "quarante-sept", "quarante-six", "quarante-trois", "quatorze", "quatre", "quatre-vingt", "quatre-vingt-cinq", "quatre-vingt-deux", "quatre-vingt-dix", "quatre-vingt-dix-huit", "quatre-vingt-dix-neuf", "quatre-vingt-dix-sept", "quatre-vingt-douze", "quatre-vingt-huit", "quatre-vingt-neuf", "quatre-vingt-onze", "quatre-vingt-quatorze", "quatre-vingt-quatre", "quatre-vingt-quinze", "quatre-vingt-seize", "quatre-vingt-sept", "quatre-vingt-six", "quatre-vingt-treize", "quatre-vingt-trois", "quatre-vingt-un", "quatre-vingt-une", "quatre-vingts", "que", "quel", "quelle", "quelles", "quelqu'", "quelqu'un", "quelqu'une", "quelque", "quelques", "quelques-unes", "quelques-uns", "quels", "qui", "quiconque", "quinze", "quoi", "quoiqu'", "quoique", "r", "revoici", "revoilà", "rien", "s", "s'", "sa", "sans", "sauf", "se", "seize", "selon", "sept", "septante", "sera", "serai", "seraient", "serais", "serait", "seras", "serez", "seriez", "serions", "serons", "seront", "ses", "si", "sinon", "six", "soi", "soient", "sois", "soit", "soixante", "soixante-cinq", "soixante-deux", "soixante-dix", "soixante-dix-huit", "soixante-dix-neuf", "soixante-dix-sept", "soixante-douze", "soixante-et-onze", "soixante-et-un", "soixante-et-une", "soixante-huit", "soixante-neuf", "soixante-quatorze", "soixante-quatre", "soixante-quinze", "soixante-seize", "soixante-sept", "soixante-six", "soixante-treize", "soixante-trois", "sommes", "son", "sont", "sous", "soyez", "soyons", "suis", "suite", "sur", "sus", "t", "t'", "ta", "tacatac", "tandis", "te", "tel", "telle", "telles", "tels", "tes", "toi", "ton", "toujours", "tous", "tout", "toute", "toutefois", "toutes", "treize", "trente", "trente-cinq", "trente-deux", "trente-et-un", "trente-huit", "trente-neuf", "trente-quatre", "trente-sept", "trente-six", "trente-trois", "trois", "très", "tu", "u", "un", "une", "unes", "uns", "v", "vers", "via", "vingt", "vingt-cinq", "vingt-deux", "vingt-huit", "vingt-neuf", "vingt-quatre", "vingt-sept", "vingt-six", "vingt-trois", "vis-à-vis", "voici", "voilà", "vos", "votre", "vous", "w", "x", "y", "z", "zéro", "à", "ç'", "ça", "ès", "étaient", "étais", "était", "étant", "étiez", "étions", "été", "étée", "étées", "étés", "êtes", "être", "ô"]
    #rw_veronis = ["-tu", "-vous", "-il", "-je", "-ils"]
    #raw_stopword_list.extend(rw_veronis) #create a list of all French stopwords
    raw_stopword_list = set(raw_stopword_list)
    stopword_list = [word for word in raw_stopword_list] #make to decode the French stopwords as unicode objects rather than ascii
    return stopword_list



fre_stopwords = get_stopswords()

SPEC = ["'", "~"]

RE_STRIP_REFS = re.compile("\.?\[\d+\]?")

def interjection_concepts(filename):
    interjectionConcepts = dict()
    print(type(interjectionConcepts))
    with open(filename, 'r', encoding='utf8') as f:
        for line in f:
            *first, concept = line.lower().strip().split()
            first = " ".join(first[:])
            first = re.sub('_', ' ', first)
            first = cleanup(first)
            first = "${}$".format(first)
            print(interjectionConcepts)
            if first in interjectionConcepts.keys():
                print(interjectionConcepts[first])
                lstinter = interjectionConcepts[first]
                interjectionConcepts[first].append(concept)
            else:
                interjectionConcepts[first] = [concept]
    print(type(interjectionConcepts))
    print(interjectionConcepts["$aucune chance$"])
    with open('interjections.pickle', 'wb') as handle:
        pickle.dump(interjectionConcepts, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
        
def cleanup(s):
    s = ''.join(c for c in s if c not in punctuations)
    return RE_STRIP_REFS.sub("", s).strip()
        
        
def struc_words(words):
    lstwords = list()
    tmp = 0
    for w in words:
        if not '"' in w and tmp == 0:
            lstwords.append("${}$".format(w.strip('"')))
        elif w.count('"') == 1 and tmp == 0:
            ww = w.strip('"')
            tmp = 1
        elif w.count('"') == 2 and tmp == 0:
            lstwords.append("${}$".format(w.strip('"')))
        elif not '"' in w and tmp == 1:
            ww = "{} {}".format(ww, w)
        elif w.count('"') == 1 and tmp == 1:
            ww = "{} {}".format(ww.strip('"'), w.strip())
            lstwords.append("${}$".format(ww.strip('"')))
            tmp = 0
            
    return lstwords
        
        
def build_concepts(filename):
    concepts_words = dict()
    words_concepts = dict()
    with open(filename, 'r', encoding='utf8') as f:
        for line in f:
            print(line)
            if line.strip():
                line = re.sub('concept:', '', line.strip().lower())
                line = re.sub('\(', ' ', line.strip())
                line = re.sub('\)', ' ', line.strip())
                print(line.split())
                title, *words = line.split()
                words = struc_words(words)
                if title in concepts_words.keys():
                    concepts_words[title].extend(words)
                else:
                    concepts_words[title] = words
                for word in words:
                    if word in words_concepts.keys():
                        words_concepts[word].append(title)
                    else:
                        words_concepts[word] = [title]
    new_concepts_words = dict()
    tilde = True
    while tilde:
        tilde = False
        for key, items in concepts_words.items():
            new_items = list()
            for item in items:
                if "~" in item:
                    tilde = True
                    item_ = re.sub('$', '', item)
                    if item_ in concepts_words.keys():
                        lstitems = concepts_words[item_]
                        for lst in lstitems:
                            new_items.append(lst)
                else:
                    new_items.append(item)
            new_concepts_words[key] = new_items
        concepts_words = new_concepts_words
        
    new_words_concept = dict()
    for key, items in words_concepts.items():
        if "~" in key:
            if key in concepts_words.keys():
                lstworlds = concepts_words[key]
                for w in lstwords:
                    if w in new_words_concept.keys():
                        new_words_concept[w].append(items)
                    else:
                        new_words_concept[w] = items
        else:
            new_words_concept[key] = items
    
    words_concepts = new_words_concept
    
    with open('concepts_words.pickle', 'wb') as handle:
        pickle.dump(concepts_words, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('words_concepts.pickle', 'wb') as handle:
        pickle.dump(words_concepts, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    with open("donn.txt", "a", encoding='utf8') as f:
        for key, items in concepts_words.items():
            f.write("{}\t{}\n\n".format(key, items))
        
                    
                    
                    
                
def QA_File(filename, out_file):
    qa = dict(questions=[], responses=[])
    with open(filename, 'r', encoding='utf8') as f:
        for i, line in enumerate(f):
            if i%2 == 0:
                qa['questions'].append(line.lower().strip())
            else:
                qa['responses'].append(line.lower().strip())
    
    for i, text in enumerate(qa['questions']):
        with open(out_file, 'a', encoding='utf8') as out_:
            out_.write("{}\t{}\n".format(text, qa['responses'][i]))
            
    return out_file, qa
                
            
    
    
def load_interjections_concepts():
    with open('interjections.pickle', 'rb') as handle:
        interjections = pickle.load(handle)
    with open('concepts_words.pickle', 'rb') as handle:
        concepts_words = pickle.load(handle)
    with open('words_concepts.pickle', 'rb') as handle:
        words_concepts = pickle.load(handle)
        
    return interjections, concepts_words, words_concepts


# TODO corriger la sortie du traitement des injections: la fonction change l'ordre des mots après remplacements.
def replace_interjections(question, interjections):
    question_ = question.lower().split()
    inter_concepts = list()
    j = 0
    while j < len(question_):
        i = j
        if not "~" in question_[i]:
            word = "${}$".format(question_[i])
            #print("initial word {}".format(word))
            cpt = 0
            l_i = []
            while i <= len(question_)+1:
                #print("i {}".format(i))
                l_i.append(i)
                if word in interjections.keys():
                    
                    #print("word: {}".format(word))
                    concept = interjections[word]
                    #print("concept found: {}".format(concept))
                    inter_concepts.append((word.strip('$'),concept[0], l_i))
                    #print('inter_concepts {}'.format(inter_concepts))
                    j = i
                i += 1
                #cpt += 1
                if i == len(question_):
                    break
                else:
                    #l_i.append(i)
                    word = "${} {}$".format(word.strip('$'), question_[i])
                    #print("next word {}".format(word))
            
        j = j + 1
    #print('inter_concepts {}'.format(inter_concepts))
    inter_concepts, inter_concepts_ = process_inter_concepts(inter_concepts)
    #print('after process inter_concepts {}'.format(inter_concepts))
    if type(inter_concepts_) is dict:
        for key, concept in inter_concepts_.items():
            question_[key] = concept
        question = " ".join(list(set(question_[:])))
    else:
        for elt in inter_concepts:
            question = re.sub(elt[0], elt[1], question)
    return question
    
def process_inter_concepts(inter_concepts):
    internals = list()
    internals_dict = dict()
    #print(inter_concepts)
    if len(inter_concepts) > 0:
        for word, concept, list_index in inter_concepts:
            word_ = word.split()
            list_index = list_index[0:len(word_)]
            internals.append((word, concept, list_index))
        rm_i = list()
        #print("len{}".format(len(internals)))
        for j in range(len(internals)-1):
            if len(internals[j][2]) == 1 and internals[j][2][0] in internals[j+1][2] and j+1 <= len(internals):
                rm_i.append(j)
        for i in rm_i:
            internals.remove(internals[i])
        for elt in internals:
            for ind in elt[2]:
                internals_dict[ind] = elt[1]            
            
        return internals, internals_dict
    else:
        return inter_concepts, inter_concepts
    
def replace_concepts(question, concepts_words, words_concepts):
    question_ = question.split()
    inter_concepts = list()
    j = 0
    while j < len(question_):
        i = j
        if not "~" in question_[i]:
            word = "${}$".format(question_[i])
            #print("initial word {}".format(word))
            cpt = 0
            l_i = []
            while i <= len(question_)+1:
                #print("i {}".format(i))
                l_i.append(i)
                if word in words_concepts.keys():
                    
                    #print("word: {}".format(word))
                    concept = words_concepts[word]
                    #print("concept found: {}".format(concept))
                    inter_concepts.append((word.strip('$'),concept[0], l_i))
                    #print('inter_concepts {}'.format(inter_concepts))
                    j = i
                i += 1
                #cpt += 1
                if i == len(question_):
                    break
                else:
                    #l_i.append(i)
                    word = "${} {}$".format(word.strip('$'), question_[i])
                    #print("next word {}".format(word))
            
        j = j + 1
    inter_concepts, inter_concepts_ = process_inter_concepts(inter_concepts)
    #print('after process inter_concepts {}'.format(inter_concepts))
    if type(inter_concepts_) is dict:
        for key, concept in inter_concepts_.items():
            if not concept == "~fr_system_joiner":
                question_[key] = concept
        question = " ".join(list(set(question_[:])))
    else:
        for elt in inter_concepts:
            if not elt[1] == "~fr_system_joiner":
                question = re.sub(elt[0].strip('$'), elt[1], question)
    return question


def replace_with_lemma(word, interjections, concepts_words, words_concepts):
    word = lima.sendAndReceiveLima(word, mode="lemma")
    #print(word)
    word = replace_interjections(word, interjections)
    word = replace_concepts(word, concepts_words, words_concepts)
    return word
    
def loaddata(filename):
    qa = dict(questions=[], responses=[])
    with open(filename, 'r', encoding='utf8') as f:
        for i, line in enumerate(f):
            line = line.strip()
            if line:
                question, response = line.split('\t')
                qa['questions'].append(question)
                qa['responses'].append(response)
    return qa


        

def seperate_subject(word):
    raw_words = ["-tu", "-vous", "-il", "-je", "-ils"]
    #if any(rw in word for rw in raw_words):
    for w in raw_words:
        if w in word:
            word = re.sub(w, '', word)
    return word

# TODO combiner deux règles qui ont la même structure en associant les réponses
# TODO quand il y a 'ou' entre deux concepts utiliser '[]' dans la règle.
# TODO si même structure de règles à la différence d'un concept, utiliser '[]'. Si rep différente utiliser 'if'
def generete_rules(qa, interjections, concepts_words, words_concepts):
    questions = list()
    concept_dict = dict()
    for i, question in enumerate(qa['questions']):
        question = replace_interjections(cleanup(question), interjections)
        #print("after interjections {}".format(question))
        question = replace_concepts(question, concepts_words, words_concepts)
        #print("after all concepts {}".format(question))
        question = [w for w in question.split() if not w in fre_stopwords]
        #print("after stopword {}".format(question))
        #question_ = question.split()
        words_no_processed = [(w, i) for i, w in enumerate(question) if not "~" in w]
        for word, it in words_no_processed:
            #if '-' in word: word = re.sub('-', ' ', word)
            word = seperate_subject(word)
            word_p = replace_with_lemma(word, interjections, concepts_words, words_concepts)
            question[it] = word_p
        question = " ".join(question[:])
        questions.append((qa['questions'][i], question, qa['responses'][i], len(question.split())))
    questions.sort(key=lambda tup:tup[3], reverse=True)
    for q in questions:
        rule = "u: (<< {} >>) {}".format(q[1], q[2])
        with open("bdiagotchi.top", "a", encoding='utf8') as f:
            f.write("#! {}\n".format(q[0]))
            f.write("{}\n".format(rule))
        















if __name__ == "__main__":
    interjections_file = "@ChatScriptInstallDir@/LIVEDATA/FRENCH/SUBSTITUTES/interjections.txt"
    concepts_file = "@ChatScriptInstallDir@/RAWDATA/IAGOTCHI/iagotchi_concepts.top"
    data_file = "@CMAKE_INSTALL_PREFIX@/data/base de données RENCONTRE corrigée.txt"
    qafile = "@CMAKE_INSTALL_PREFIX@/data/bd_iagotchi.txt"
    #interjection_concepts(interjections_file)
    build_concepts(concepts_file)
    data_file, data = QA_File(qafile, 'bdiagotchi.txt')
    #data = loaddata(qafile)
    interjections, concepts_words, words_concepts = load_interjections_concepts()
    
    generete_rules(data, interjections, concepts_words, words_concepts)
    
