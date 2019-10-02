import argparse, os


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--filename', help='top filename')
    
    args= parser.parse_args()
    
    if args.filename and os.path.isfile(args.filename):
        with open(args.filename, 'r', encoding='utf8') as f:
            for line in f:
                if line and "#!" in line.strip():
                    with open('G5_questions_with_rules.txt', 'a', encoding='utf8') as fout:
                        fout.write(line.strip()+"\n")
