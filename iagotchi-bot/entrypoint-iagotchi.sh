#!/bin/bash

# MODELFILE="data/embeddings/rencontre.bin"
# if [ ! -f "$MODELFILE" ]; then
#    python3 similarity.py
# fi  
# case "$3" in "iagotchi")
#     cd ChatScript/BINARIES/
#     ./LinuxChatScript64 &
#     cd ../../
#     python3 test_chatscript.py --bot iagotchi & python3 main.py --runbot iagotchi
#     ;;
#     "iagotchig5 ")
#     cd ChatScript/BINARIES/
#     ./LinuxChatScript64 &
#     cd ../../
#     python3 test_chatscript.py --bot iagotchig5 & python3 main.py --runbot iagotchig5
#     ;;    
#     "build_similarity")
#     python3 main.py --build similarity
#     ;;
#     *)
#     echo "You have failed to specify what to do correctly."
#     exit 1
#     ;;
# esac

cd ChatScript/BINARIES/
./LinuxChatScript64 &
cd ../../
python3 test_chatscript.py & python3 main.py
