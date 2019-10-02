from textgenrnn import textgenrnn
import json, sys, argparse, os



parameters = {"new_model": True, "rnn_bidirectional": True, "rnn_size": 64, "dim_embeddings": 300, "num_epochs":10, "model_name": "iagotchi_new"}

def check_config_file(configfile):
    try:
        with open(r'{}'.format(configfile), 'r') as cfg:
            config = json.load(cfg)
    except:
        sys.exit("[IaTextGenerator] Problem with {}".format(configfile))
    if config['source'] and os.path.exists(config['source']):
        data = config['source']
    else:
        sys.exit("[IaTextGenerator] source file doesn't exist.")
    
    if config['model_name'] and len(config['model_name']):
        model_name = config['model_name']
    else:
        sys.exit("[IaTextGenerator] Model name doesn't exist.")
        
    for param, value in parameters.items():
        if param in config.keys():
            try:
                parameters[param] = config[param]
            except:
                pass
    return data


def train(data):
    # For Training a new model
    textgen = textgenrnn(name=parameters['model_name'])
    textgen.reset()
    textgen.train_from_file(data, **parameters)


def main(jsonfile):
    data = check_config_file(jsonfile)
    train(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--parametersfile', help='parameters file')
    
    args= parser.parse_args()
    
    main(args.parametersfile)
