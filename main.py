# -*- coding: utf-8 -*-
import sys
import os

# Insert the src/fishbattle package folder into path to run it from root
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "fishbattle")
sys.path.insert(0, src_path)

from app import main

if __name__ == "__main__":
    main()
