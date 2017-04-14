'''
Walk-ER : a system for walking paths in an entity-relational diagram.
usage: walker.py [-h] [-v] [-n | -w | -p] diagram_file
'''

from __future__ import print_function
from collections import OrderedDict
import argparse
#import itertools
import json
#import networkx (not currently implemented for pagerank, but could still be necessary elsewhere)
import os

# Define a short class for raising exceptions to help with debugging.

class ExceptionCase(Exception):
    def handle(self):
        print(self.message)

# Setup: parse the commandline input, perform checks, and import/parse the specified file.

class Setup:
    
    def __init__(self):

        self.diagram_file = None # The diagram we're walking.
        self.verbose = False     # -v, --verbose
        self.nowalk = False      # -n, --nowalk
        self.walk = True         # -w, --walk
        self.powerset = False    # -p, --powerset
        
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
                          help="Walk graph from every feature to every feature (potentially infinite).",
                          action="store_true")
        # Get the args.
        args = parser.parse_args()

        # Make sure the diagram_file is valid.
        if not os.path.isfile(args.diagram_file):
            raise ExceptionCase('Error [2]: Could not find file: "' + args.diagram_file + '"')

        # Import the file:
        '''Reads the contents of 'file_to_read', raises an exception if it cannot be read.'''
        try:
            self.diagram_file = open(args.diagram_file).read()
        except:
            raise ExceptionCase('Error [2]: Could not read the file: "' + args.diagram_file + '"')
            
        # Since the files exist, we can go ahead and set the rest of the parameters, starting with verbose
        self.verbose = args.verbose
                    
        # Check the rest of the parameters, update if necessary.
        if not (args.walk or args.nowalk or args.powerset):
            # If this occurs, no flags were specified, so keep defaults (default: self.walk=True).
            pass
        else:
            self.nowalk = args.nowalk
            self.walk = args.walk
            self.powerset = args.powerset

class BuildDictionaries:

    def __init__(self, json_dict):
        self.verbose = setup.verbose
        self.json_dict = json_dict
        self.ER_dictionary = {}
        self.attribute_dictionary = {}
        self.relationship_dictionary = {}
        self.variable_dictionary = {}

    def extractVariables(self):
        '''Returns a dictionary of variables bound to their entity id
        e.g. {'1': 'professorid', '10': 'courseid', '6': 'studentid'}'''
        
        if 'shapes' in self.json_dict:
            for i in range(len(self.json_dict['shapes'])):
                current = self.json_dict['shapes'][i]
                if ('type' in current) and ('details' in current):
                    number = str(current['details'].get('id'))
                    name = str(current['details'].get('name'))
                    
                    self.ER_dictionary[number] = [name, str(current['type'])]

                    if current['type'] == 'Entity':
                        self.variable_dictionary[number] = name.lower() + 'id'

        if self.verbose:
            print('Variables:\n', str(self.variable_dictionary))
            print('All Shapes:\n', str(self.ER_dictionary))
            
    def extractAttributes(self):
        '''Returns a dictionary of [entity-id, isMultivalued] bound to their name:
        e.g. {'Salary': ['True', '1'], 'Tenure': ['False', '1'], 'Rating': ['True', '10'], ...}'''
        
        if 'shapes' in self.json_dict:
            for i in range(len(self.json_dict['shapes'])):
                current = self.json_dict['shapes'][i]
                if ('type' in current) and ('details' in current):
                    if current['type'] == 'Attribute':
                        name = str(current['details'].get('name'))
                        multi = str(current['details'].get('isMultivalued'))
                        
                        self.attribute_dictionary[name] = [multi]
                        
        if 'connectors' in json_dict:
            for i in range(len(self.json_dict['connectors'])):
                current = self.json_dict['connectors'][i]
                if 'type' in current:
                    # Rebuild the graph as an undirected dictionary which we can search.
                    src = str(current['source'])
                    dest = str(current['destination'])
                    if (current['type'] == 'Connector'):
                        # Attributes can be inferred if it's a regular connector.
                        name = str(self.ER_dictionary.get(str(current['source']))[0])
                        if name in self.attribute_dictionary:
                            self.attribute_dictionary[name].append(dest)

        if self.verbose:
            print('Attributes:\n', str(self.attribute_dictionary))

    def rebuildGraph(self):
        pass

    def extractRelationships(self):
        pass

class CmdInteraction:
    
    def __init__(self):
        pass
        
    def targetFeatureSelector(self):
        pass

class FileWriter:
    
    def __init__(self):
        pass

    def write_modes_to_file(self):
        pass

class ConstructModes:
    
    def __init__(self):
        pass

    def handleTargetVariables(self):
        pass

    def handleRelationVariables(self):
        pass

    def handleAttributeVariables(self):
        pass

class Networks:
    
    def __init__(self):
        pass
        
    def find_all_paths(self, graph, start, end, path=[]):
        pass

    def paths_from_target_to_features(self, graph):
        pass

    def path_powerset(self, graph):
        pass

    def walkFeatures(self):
        import itertools
        pass

class UnitTests:

    def __init__(self):
        pass

    def run_unit_tests(self):
        pass

if __name__ == '__main__':

    '''Parse the commandline input, import the file. Contents are stored in setup.diagram_file.'''
    setup = Setup()
    json_dict = json.loads(setup.diagram_file)
    #print(json_dict)

    '''Turn turn the file into dictionaries.'''
    dictionaries = BuildDictionaries(json_dict)
    dictionaries.extractVariables()
    dictionaries.extractAttributes()
