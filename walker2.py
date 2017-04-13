'''
Walk-ER : a system for walking paths in an entity-relational diagram.
usage: testing.py [-h] [-v] [-n] [-w] [-p] diagram_file
'''

from __future__ import print_function
from collections import OrderedDict
import argparse
import os

# Setup

class Setup:
    
    def __init__(self):
        
        # Start by creating an argument parser to help with user input.
        parser = argparse.ArgumentParser(description="Walk-ER: a system for walking the paths in an entity-relational diagram."\
                                         " Written by Alexander L. Hayes (hayesall@indiana.edu)"\
                                         " and Mayukh Das (maydas@indiana.edu). Indiana University STARAI Lab.", 
                                         epilog="Copyright 2017 Free Software Foundation, Inc."\
                                         " License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>."\
                                         " This is free software: you are free to change and redistribute it."\
                                         " There is NO WARRANTY, to the extent permitted by law.")
        # Add the arguments.
        walk = parser.add_mutually_exclusive_group()
        parser.add_argument("diagram_file")
        parser.add_argument("-v", "--verbose", 
                            help="Increase verbosity to help with debugging.", 
                            action="store_true")
        walk.add_argument("-n", "--nowalk",
                          help="Instantiate variables without walking (base case).", 
                          action="store_true")
        walk.add_argument("-w", "--walk",
                          help="Walk graph from target to features (efficient).", 
                          action="store_true")
        walk.add_argument("-p", "--powerset",
                          help="Walk graph from every feature to every feature (slow).",
                          action="store_true")
        # Get the args.
        args = parser.parse_args()
        if os.path.isfile(args.diagram_file):
            print("true")

        

if __name__ == '__main__':
    setup = Setup()
