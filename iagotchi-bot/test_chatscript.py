
from chatscript import ChatscriptInstance
import argparse, json


with open(r'@CMAKE_INSTALL_PREFIX@/data/config.json', 'r') as sv:
    configfile = json.load(sv)

def main(botname):
    chatscript = ChatscriptInstance(botname)
    chatscript.start_iagotchi_bot()
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--bot', help='bot name')
    
    bots = ['iagotchi', 'iagotchig5']
    
    args= parser.parse_args()
    
    if args.bot and args.bot.lower() in bots:
        main(bot=args.bot.lower())
    elif configfile and configfile['bot']['name'].lower() in bots:
        main(configfile['bot']['name'].lower())
        
