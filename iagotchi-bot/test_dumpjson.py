
import pickle


#topic = ['rencontre','g5']
#responses_ = {'rencontre':dict(), 'g5':dict()}
#for t in topic:
    #with open('data/{}.txt'.format(t), 'r') as f:
        #lines = f.readlines()
    ##print(lines)
    #for i, line in enumerate(lines):

        #if i < len(lines) -1 :
            #responses_[t][i] = [lines[i+1].strip()]
        #else:
            #responses_[t][i] = [lines[0].strip()]


def save_obj(obj):
    with open('data/responses.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj():
    with open('data/responses.pkl', 'rb') as f:
        return pickle.load(f)
    
#save_obj(responses_)
r = load_obj()
print(r)
rr = list()
r['rencontre'][17].append('toto')
#rr.append('toto')
#r.append('toto')
print(r)
