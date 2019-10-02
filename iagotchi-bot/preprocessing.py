import re, argparse, os
from lima import Lima


punctuations = '''!()[]{};:"\,<>./?@#$%^&*'''
RE_STRIP_REFS = re.compile("\.?\[\d+\]?")

lima = Lima()

def cleanup(s):
    s = ''.join(c for c in s if c not in punctuations)
    if "-" in s: s = re.sub('-', ' ', s)
    return RE_STRIP_REFS.sub("", s).strip()



def process(filename):
    path, filename_ = os.path.split(filename)
    filename_, file_extension = os.path.splitext(filename_)
    output = os.path.join(path, "{}_lima.txt".format(filename_))
    with open(filename, 'r', encoding='utf8') as in_:
        for line in in_:
            line = cleanup(line.lower().strip())
            print(line)
            line = lima.sendAndReceiveLima(line, mode='text')
            with open(output, 'a', encoding='utf8') as out_:
                out_.write(line+'\n')
            
            


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='name of file to process')
    
    args = parser.parse_args()

    process(args.filename)
