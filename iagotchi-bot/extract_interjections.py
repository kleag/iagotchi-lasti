import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='name of file to process')
    ##parser.add_argument('filename_original', help='name of file to process')
    #parser.add_argument('tfidf_folder', help='folder')
    
    args = parser.parse_args()
    
    res = ""
    
    with open(args.filename, 'r', encoding='utf8') as f:
        for line in f:
            line = line.strip()
            if "~no" in line:
                line = line.replace('~no', '')
                line = line.replace('<', '')
                if '>' in line:
                    line = line.replace('>', '')
                if '_' in line:
                    line = ' '.join(line.split('_'))
                    line = '"{}"'.format(line.strip())
                res = "{} {}".format(res, line)
    print(res)
                
