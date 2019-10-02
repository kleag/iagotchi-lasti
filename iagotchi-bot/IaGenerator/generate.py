from textgenrnn import textgenrnn
import json, sys, argparse, os


def check_arguments(args):
    """
    Function for checking if required arguments are in the command line. 
    Input: args
    Ouput: n and temperature.
    """
    if args.model is None or args.vocab is None or args.config is None:
         sys.exit("[IaTextGenerator] Vocab, model and config files are necessary for text generating")
    try:
        n = int(args.n)
    except:
        n = 5
    try:
        temp = int(args.temperature)
        if temp > 1:
            temp = 1
    except:
        temp = 1
        
    return n, temp
        

def main(args):
    n, temp = check_arguments(args)
    # For testing
    textgen = textgenrnn(weights_path=args.model, 
                        vocab_path=args.vocab,
                        config_path=args.config)

    print(textgen.generate(n=n, temperature=int(temp)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--model', help='weights_path')
    parser.add_argument('--vocab', help='vocab file')
    parser.add_argument('--config', help='config file')
    parser.add_argument('--n', help='number of texts to generate')
    parser.add_argument('--temperature', help='temperature, values [0, 0.5, 1]')
    
    args= parser.parse_args()
    
    main(args)
