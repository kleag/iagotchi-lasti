from generator.generator import Generator
import re
import osc
client = osc.Client('127.0.0.1', 5006)
generator = Generator('generator/iagotchi.model')

client.send('/generate')



#result = generator.generate(200)
#result = re.sub('<eos>', '.', ' '.join(result))
#print(result)
#r = True
#while r:
    #if '. .' in result:
        #result = result.replace('. .', '.')
    #else:
        #r = False
#print(result)
#print(len(result))
