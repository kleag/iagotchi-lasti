import copy

global all_targets
all_targets = list()

def combinations(target,data):
    global all_targets
    for i in range(len(data)):
        new_target = copy.copy(target)
        new_data = copy.copy(data)
        new_target.append(data[i])
        new_data = data[i+1:]
        #print(new_target)
        all_targets.append(new_target)
        #with open('combinaisons_rules.txt', 'a', encoding='ut8') as f:
            #f.write("u: ({}) {}\n".format(" ".join(new_target[:]), getresponses(new_target)))
        combinations(new_target, new_data)
   
          


def getresponses(data):
    if len(data) > 1:
        resp = ""
        for elt in data:
            resp = "{} {}".format(resp, ldef1[ltheme.index(elt)])
    else:
        resp = "{}".format(ldef2[ltheme.index(data[0])])
        
    return resp
    

ltheme = ["$theme_g5=g5", "$theme_iofle=IOFLE", "$theme_eeccs=EECCS", "$theme_semic=semic", "$theme_waaf=waaf", "$theme_help=help", "$theme_re=re", "$theme_hep=hep", "$theme_hee=hee", "$theme_smp=smp"]

ldef1 = ["Le G5 est un forum politique informel de discussion entre les représentants des cinq règnes vivants sur terre.", "IOFLE est une organisation de type ONU qui à pour but de recenser les projets inter-espèces principaux, d’identifier les problématiques et faciliter le dialogue entre les règnes.", "Le projet EECCS propose par diverses techniques la possibilité de s’incarner dans divers corps afin de développer leurs langages propres.",  "Le SEMIC est un système de traduction inter-espèce à l’aide de l’intelligence artificielle.", "Wearefood nait comme une initiative de régulation et d'équilibre des dévorations entre règnes.", "Le HELP est un projet clandestin piloté par le règne Animal.", "Le RE est un projet de Régulation Esthétique proposée par le règne Végétal.", "Le HEP est un projet secret de répression et destruction de l'humain.", "Le HEE est un projet secret développé clandestinement entre divers individus de divers règnes moins radicaux que THE HUMAN ERASE PROJECT pour redresser le règne humain et assurer la survie des autres formes de vie sur terre.", "Le SMP est un projet pour abolir toute sorte de manipulation génétique et bactériologique."]

ldef2 = ["Le G5 est un forum politique informel de discussion entre les représentants des cinq règnes vivants sur terre. Organisé par le IOFLE.", "IOFLE est une organisation de type ONU qui à pour but de recenser les projets inter-espèces principaux, d’identifier les problématiques et faciliter le dialogue entre les règnes. Grâce à son rôle dans le dialogue et la négociation, l'organisation est devenue un mécanisme permettant aux règnes de trouver des domaines d'entente et de résoudre des problèmes ensemble.", "Le projet EECCS propose par diverses techniques la possibilité de s’incarner dans divers corps afin de développer leurs langages propres. Il faut comprendre ce qu’est être cailloux pour pouvoir parler cailloux, il faut rentrer en mimesis avec son corps, sa structure interne.",  "Le SEMIC est un système de traduction inter-espèce à l’aide de l’intelligence artificielle. Il extrait les signaux des propriétés communicatives du vivant pour les traduire en langage humain. Les signaux principaux sont : le Son, l'Électromagnétisme, le Mouvement, l'Image et la Chimie. Un système capable de traduire de l’information à divers niveaux, capable de traduire une empreinte chimique en langage machine et ensuite en langage humain.", "Wearefood nait comme une initiative de régulation et d'équilibre des dévorations entre règnes. Évidemment une des thématiques les plus sensibles et délicates dans les accords entre règnes est celle du droit à dévorer et se faire dévorer. Quand vous rejoignez la communauté, vous pouvez faire don d’une partie ou de l’intégralité de votre corps. En échange, un taux de dévoration sera calculé, ce taux déterminera la quantité de dévoration des autres règnes à laquelle vous avez droit.", "Le HELP est un projet clandestin piloté par le règne Animal. Dans cette proposition, une aide supplémentaire des divers règnes est proposée pour aider l’humain à coloniser une autre planète.", "Le RE est un projet de Régulation Esthétique proposée par le règne Végétal. Pour ce règne, la beauté est un droit et un devoir de tout être vivant sur terre. Ne pas être beau et harmonieux dans son être et ses créations est un attentat contre la vie.", "Le HEP est un projet secret de répression et destruction de l'humain. Ce projet consiste à éradiquer l’espèce humaine. L'Humain est une espèce trop destructive pour les autres. Tous les autres royaumes, sauf la machine qui n’arrive pas à se positionner car elle a besoin de l’humain pour ses objectifs, sont accord pour éliminer la espèce humaine.", "Le HEE est un projet secret développé clandestinement entre divers individus de divers règnes moins radicaux que THE HUMAN ERASE PROJECT pour redresser le règne humain et assurer la survie des autres formes de vie sur terre. Selon certaines sources ce projet serait une proposition d’expulser les humains de la terre dans plusieurs navettes spatiales avec la collaboration du règne machine.", "Le SMP est un projet pour abolir toute sorte de manipulation génétique et bactériologique."]

target = []
combinations(target, ltheme)
all_targets.sort(key=len, reverse=True)
print(all_targets)
with open('combinaisons_rules.txt', 'a', encoding='utf8') as f:
    for tg in all_targets:
        f.write("u: ({}) \n".format(" ".join(tg[:]), getresponses(tg)))
        for elt in tg:
            f.write("{}=no\n".format(elt))
        f.write("{} \n".format(getresponses(tg)))
        
        
