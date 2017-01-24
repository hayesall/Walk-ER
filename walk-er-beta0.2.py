'''
TODO:
- SQL Table Conversion (may or may not be possible)
- pygame
- Multivalued vs. binary Attributes:
  --> multivalued: departmenta(+professorid,#departmenta).
  --> binary:      male(#nameid).
- Rebuild the graph (networkx can operate over dictionaries of lists, where the key is the node id
  and the value is a list of nodes the id is directed to).
'''

class InputException(Exception):
    def handle(self):
        print self.message

class InvalidArgumentException(Exception):
    def handle(self):
        print self.message

import json
import sys, os
from collections import OrderedDict
import pygame


class setup:
    
    def __init__(self):
        self.debugmode = False
        self.cmdmode = True
        self.helpmode = False
        self.validargs = ['-h', '--help', '-v', '--verbose', '-c', '--cmd']

    def read_user_input(self):
        '''Read the user-specified input for the file to parse
        Succeeds if the file is valid.'''
        args = sys.argv
        flags = args[1:-1]

        for flag in flags:
            if flag not in self.validargs:
                raise InvalidArgumentException(
                    '\nUnknown argument: %s' % flag
                )

        # Help: print help to out and terminate program.
        if ('-h' in args) or ('--help' in args):
            self.helpmode = True
            print '''
NAME
    Walk-ER vBeta0.2

SYNOPSIS
    $ python walker.py [OPTIONS] [FILE]
    
    >>> import walker

DESCRIPTION
    "Walker" for Entity-Relational Diagrams from ERDPlus
    https://erdplus.com/#/

    Used for parsing the JSON file exports from ERDPlus.
    Parses the document, rebuilds the relationships and assists the user in creating a BoostSRL Background File.

OPTIONS
    -h, --help: Print a message that briefly summarizes command-line options and help information, then exits.
            
    -v, --verbose:
            "Debug Mode," where intermediate steps are printed to terminal.
            Most applicable when Commandline mode is also activated.

    -c, --cmd: "Commandline Mode", override the gui and interact through the shell.

AUTHOR
    Written by Alexander L. Hayes, Indiana University STARAI Lab
    Bugs/Questions: hayesall@indiana.edu
    Last Updated: January 23, 2017

COPYRIGHT
    Copyright 2017 Free Software Foundation, Inc.  License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.
    This is free software: you are free to change and redistribute it.  There is NO WARRANTY, to the extent permitted by law.
            '''
            exit()

        # Debug Mode:
        if ('-v' in args) or ('--verbose' in args):
            self.debugmode = True

        # gui override: commandline mode
        if ('-c' in args) or ('--cmd' in args):
            self.cmdmode = True

        if not os.path.isfile(args[-1]):
            raise InputException(
                '\nFile error, file not found.'
                '\nUsage: $ python walker.py [OPTIONS] [FILE]'
            )
        return args[-1]

    def import_data(self, file_to_read):
        '''Reads the contents of 'file_to_read', raises an exception if it cannot be read.'''
        try:
            doc = open(file_to_read).read()
        except:
            raise InputException(
                '\nFile error, could not read file.'
                '\nUsage: $ python walker.py [OPTIONS] [FILE]'
            )
        return doc

class buildDictionaries:

    def __init__(self, debugmode=False):
        self.debugmode = debugmode

    def debug(self):
        if self.debugmode:
            print "\n'Debug Mode' is activated, intermediate steps will be printed to terminal.\n"

    def extractVariables(self, json_dict):
        '''
        Input: a json dictionary
        Returns of dictionary of variables bound to their entity-id from ERDPlus
        i.e. {'1': 'professorid', '10': 'courseid', '6': 'studentid'}
        '''
        ER_dictionary = {}
        variable_dictionary = {}
        coordinate_dictionary = {}
        
        if 'shapes' in json_dict:
            for i in range(len(json_dict['shapes'])):
                current = json_dict['shapes'][i]
                if ('type' in current) and ('details' in current):
                    number = str(current['details'].get('id'))
                    name = str(current['details'].get('name'))
                    xcoord = str(current['details'].get('x'))
                    ycoord = str(current['details'].get('y'))

                    coordinate_dictionary[number] = [xcoord, ycoord]
                    ER_dictionary[number] = name
                    if current['type'] == 'Entity':
                        variable_dictionary[number] = name.lower() + 'id'
        if self.debugmode:
            print 'Variables:\n', str(variable_dictionary)
            print 'All Shapes:\n', str(ER_dictionary)
            print 'Coordinates:\n', str(coordinate_dictionary)
        return ER_dictionary, variable_dictionary, coordinate_dictionary
        
    def extractAttributes(self, json_dict, ER_dictionary, variable_dictionary):
        '''
        Input: a json dictionary, ER_dictionary, variable_dictionary
        Returns a dictionary of [entity-id, isMultivalued] bound to their name:
        i.e. {'Salary': ['True', '1'], 'Tenure': ['False', '1'], 'Rating': ['True', '10'], ...}
        '''
        attribute_dictionary = {}

        if 'shapes' in json_dict:
            for i in range(len(json_dict['shapes'])):
                current = json_dict['shapes'][i]
                if ('type' in current) and ('details' in current):
                    if current['type'] == 'Attribute':
                        name = str(current['details'].get('name'))
                        multi = str(current['details'].get('isMultivalued'))
                        attribute_dictionary[name] = [multi]

        if 'connectors' in json_dict:
            for i in range(len(json_dict['connectors'])):
                current = json_dict['connectors'][i]
                if 'type' in current:
                    if (current['type'] == 'Connector'):
                        name = str(ER_dictionary.get(str(current['source'])))
                        if name in attribute_dictionary:
                            dest = str(current['destination'])
                            attribute_dictionary[name].append(dest)
        if self.debugmode:
            print 'Attributes:\n', str(attribute_dictionary)
        return attribute_dictionary

    def extractRelationships(self, json_dict, variable_dictionary):
        '''
        "Determine if if a relationship is one-many, many-one, many-many, or unspecified."
        Input: a json dictionary and a variable dictionary
        Returns a dictionary of [to, from, toCardinality, fromCardinality]
        i.e. {'Advises': ['6', '1', 'many', 'one']}
          --> Many students are advised by a professor.
        i.e. {'Takes': ['10', '6', 'many', 'many']}
          --> Many courses are taken by many students.
          --(or)-> students take multiple courses, and courses are taken by multiple students.
        '''
        relationship_dictionary = {}
        
        if 'shapes' in json_dict:
            for i in range(len(json_dict['shapes'])):
                current = json_dict['shapes'][i]
                if ('type' in current) and ('details' in current):
                    name = str(current['details'].get('name'))
                    if current['type'] == 'Relationship':
                        temp = current['details'].get('slots')
                        var1 = variable_dictionary.get(str(temp[0]['entityId']))
                        var2 = variable_dictionary.get(str(temp[1]['entityId']))
                        relationship_dictionary[name] = [str(temp[1]['entityId']), str(temp[0]['entityId'])]

        for x in json_dict['shapes']:
            shapes_dict = x['details'].get('slots')
            if shapes_dict:
                name = str(x['details'].get('name'))
                dir1 = str(shapes_dict[0].get('cardinality'))
                dir2 = str(shapes_dict[1].get('cardinality'))
                relationship_dictionary[name].append(dir2)
                relationship_dictionary[name].append(dir1)

        if self.debugmode:
            print 'Relationships:\n', str(relationship_dictionary)
        return relationship_dictionary

class cmdlineMode:

    def __init__(self, debugmode=False):
        self.debugmode = debugmode

    def targetFeatureSelection(self, attribute_dictionary, relationship_dictionary):
        '''Ask the user for ['target', ['feature1', 'feature2', ...]]'''
        possible_targets = attribute_dictionary.keys() + relationship_dictionary.keys()
        
        while 1:
            print "\nPlease select your target from this list:\n\t" + '    '.join(possible_targets)
            sys.stdout.flush()
            target = raw_input()
            if target in possible_targets:
                possible_targets.remove(target)
                break
            else:
                print '\tError, target not in list.'

        while 1:
            print "\nPlease select features you want to learn over (separated by spaces):\n\t" + '    '.join(possible_targets)
            sys.stdout.flush()
            features = raw_input()
            features = features.split()
            final_features = []
            for feature in features:
                if feature in possible_targets:
                    final_features.append(feature)
                else:
                    print '\tError, "' + feature + '" not in list.'
            if (len(final_features) == len(features)):
                break
        
        targetAndFeatures = [target, list(OrderedDict.fromkeys(final_features))]
        if self.debugmode:
            print targetAndFeatures
        return targetAndFeatures

class constructModes:

    def __init__(self, targetAndFeatures, ER_dictionary, variable_dictionary, attribute_dictionary, relationship_dictionary, cmdlinemode=True):
        self.cmdmode = cmdlinemode
        self.target = targetAndFeatures[0]
        self.features = targetAndFeatures[1]
        self.ER_dictionary = ER_dictionary
        self.variable_dictionary = variable_dictionary
        self.attribute_dictionary = attribute_dictionary
        if self.cmdmode:
            print "\n\n//Modes:"

    def handleTargetVariables(self):
        if self.cmdmode:
            print "//target:"
        target_variable = self.target

    def handleRelationVariables(self):
        pass
    
    def handleAttributeVariables(self):
        pass

    """
    target_variables = relationships[target]
    #print target_variables
    if len(target_variables) == 1:
        print "mode: %s(+%s,#%s)." % (target.lower(), variables.get(relationships[target][0]), target.lower())
    if len(target_variables) == 2:
        print "mode: %s(+%s,+%s)." % (target.lower(), variables.get(relationships[target][0]), variables.get(relationships[target][1]))
    
    print '//features'
    #for feature in features:
    # attributes that are "multivalued" should only include the hash value
    for feature in relationships:
        if (len(relationships[feature]) == 2):
            symbol = relationships[feature]
            if (symbol[0] == symbol[1]):
                # This section can be simplified, pay attention to where 'many' is.
                if (relationships_cardinality.get(feature) == ['many', 'many']):
                    #i.e. (friends relationship), print two lines
                    print "mode: %s(%s,%s)." % (feature.lower(), '+' + variables[symbol[0]], '-' + variables[symbol[1]])
                    print "mode: %s(%s,%s)." % (feature.lower(), '-' + variables[symbol[0]], '+' + variables[symbol[1]])
                elif (relationships_cardinality.get(feature) == ['one', 'many']):
                    #i.e. (siblingof), print one line
                    print "mode: %s(%s,%s)." % (feature.lower(), '+' + variables[symbol[0]], '-' + variables[symbol[1]])
                elif (relationships_cardinality.get(feature) == ['many', 'one']):
                    print "mode: %s(%s,%s)." % (feature.lower(), '-' + variables[symbol[0]], '+' + variables[symbol[1]])
        
        if (feature not in features):
            if (len(relationships[feature]) == 1):
                # attributes
                # check if the variable is multivalued
                var = variables.get(relationships[feature][0])
                print "mode: %s(%s,#%s)." % (feature.lower(), '+' + var, feature.lower())
            else:
                output = []
                for var in relationships[feature]:
                    output.append('+' + variables.get(var))
                print "mode: %s(%s)." % (feature.lower(), ','.join(output))
        else:
            # lists of length 1 are attributes
            if (len(relationships[feature]) == 1):
                if relationships[feature][0] in target_variables:
                    # assign +
                    symbol = '+'
                else:
                    # assign -
                    symbol = '+'
                var = variables.get(relationships[feature][0])
                print "mode: %s(%s%s,#%s)." % (feature.lower(), symbol, var, feature.lower())
            # lists of length 2 are relationships
            else:
                output = []
                for var in relationships[feature]:
                    if var in target_variables:
                        # assign +
                        symbol = '+'
                    else:
                        # assign -
                        symbol = '-'
                    var = variables.get(var)
                    output.append(symbol+var)
                print "mode: %s(%s)." % (feature.lower(), ','.join(output))
                    
    """

class unitTests:
    
    def __init__(self):
        pass

    def run_unit_tests(self):
        pass

class networks:
    
    def __init__(self):
        import networkx as nx

    def find_pagerank(graph):
        '''Takes a graph in the form of a python dictionary, returns dictionary of pageranks for each node'''
        G = nx.from_dict_of_lists(graph)
        return nx.pagerank(G, alpha=0.85)

    def walkFeatures(self, target, list_of_features):
        '''
        "Use user-selected features to construct background/modes."
        Input: [target feature], [a list of features selected by the user].
        Output: (for now, print modes to terminal, in the future write them to a file)
        '''
        pass

def main():
    '''Setup'''
    Setup = setup()
    # specify file to read
    json_file = Setup.read_user_input()
    # import the file
    json_data = Setup.import_data(json_file)
    # convert from json format to something more python-friendly
    json_dict = json.loads(json_data)
    
    '''Create dictionaries from the provided file'''
    #Check if the user set the "debug mode" flag (-v, --verbose)
    BuildDictionaries = buildDictionaries(Setup.debugmode)
    BuildDictionaries.debug()
    
    # find the variables (based on entities in the graph), also create a dictionary of all shapes
    ER_dictionary, variable_dictionary, coordinate_dictionary = BuildDictionaries.extractVariables(json_dict)

    # find the attributes
    attribute_dictionary = BuildDictionaries.extractAttributes(json_dict, ER_dictionary, variable_dictionary)
    
    # find the relationships and their cardinality # {'Friends', ['1','1','many','many']}
    relationship_dictionary = BuildDictionaries.extractRelationships(json_dict, variable_dictionary)
    
    '''Different options depending on whether the user is in gui/cmdline mode'''
    if Setup.cmdmode:
        cmdlinemode = cmdlineMode(Setup.debugmode)
        # Ask the user for the target and useful features.
        targetAndFeatures = cmdlinemode.targetFeatureSelection(attribute_dictionary, relationship_dictionary)
    else:
        # guimode currently isn't implemented
        guimode = guiMode(coordinate_dictionary) #debugmode is irrelevant with the gui.
        #targetAndFeatures = guimode.targetFeatureSelection(attribute_dictionary, relationship_dictionary)
        
    #ConstructModes = constructModes(targetAndFeatures)
    ConstructModes = constructModes(targetAndFeatures, ER_dictionary, variable_dictionary, attribute_dictionary, relationship_dictionary)
    ConstructModes.handleTargetVariables()        

    exit()
    
    """
Target:  Advises
Please select features you want to learn over (separated by spaces)
DepartmentA DepartmentB TAs Teaches
Features:  ['DepartmentA', 'DepartmentB', 'TAs', 'Teaches']

Modes:
//target
mode: advises(+studentid,+professorid).
//features
mode: advises(+studentid,+professorid).
mode: salary(+professorid,#salary).
mode: takes(+courseid,+studentid).
mode: tas(-courseid,+studentid).
mode: departmenta(+professorid,#departmenta).
mode: rating(+courseid,#rating).
mode: gpa(+studentid,#gpa).
mode: tenure(+professorid,#tenure).
mode: teaches(-courseid,+professorid).
mode: departmentb(+studentid,#departmentb).

    exit()
    variables = {}
    relationships = {}
    relationships_cardinality = {}
    ER_dictionary = {}

    if 'shapes' in json_dict:
        for i in range(len(json_dict['shapes'])):
            current = json_dict['shapes'][i]
            if ('type' in current) and ('details' in current):
                # Find all shapes in the er-diagram (map id# to the name)
                number = str(current['details'].get('id'))
                name = str(current['details'].get('name'))
                ER_dictionary[number] = name

                # create the variables from which we construct the predicates
                if current['type'] == 'Entity':
                    variables[number] = name.lower() + 'id'
                    
                # attributes must reference the entity they are associated with
                # if name is 'Attribute':

                # Find the direction of the relationships (prof advises student =/= student advises professor)
                # TODO: Move this to a separate part of the function based on the possibility that variables haven't been
                # added before they are referenced (small chance but still possible)
                # append to the 'relationships' list
                if current['type'] == 'Relationship':
                    temp = current['details'].get('slots')
                    var1 = variables.get(str(temp[0]['entityId']))
                    var2 = variables.get(str(temp[1]['entityId']))
                    #print current['details'].get('slots')[0]['entityId'], name, current['details'].get('slots')[1]['entityId']
                    #print temp[0]['entityId'], name.lower(), temp[1]['entityId']
                    #print "%s(%s,%s)." % (name.lower(), var1, var2)
                    # Instead appends the relationship ('name', '1', '6') to the relationships list, these can be reconstructed at the end.
                    # Remember that we're doing predicate-logic format, so we would expect relations of the form:
                    # advises(+sid, +pid) --> pid advises sid
                    #relationships.append([name, str(temp[1]['entityId']), str(temp[0]['entityId'])])
                    relationships[name] = [str(temp[1]['entityId']), str(temp[0]['entityId'])]
                
                #print current['type'], current['details'].get('name'), current['details'].get('id'), '(', current['details'].get('x'), ',', current['details'].get('y'), ')'
    
    if 'connectors' in json_dict:
        for i in range(len(json_dict['connectors'])):
            current = json_dict['connectors'][i]
            if 'type' in current:
                if current['type'] == 'Connector':
                    #print current['source'], '<-->', current['destination']
                    #continue
                    var1 = ER_dictionary.get(str(current['source']))
                    var2 = variables.get(str(current['destination']))
                    var3 = str(current['destination'])
                    #relationships.append([var1, var2, var1])
                    #print '   ', var1, var2, var3
                    #relationships.append([str(current['source']), str(current['destination']), str(current['destination'])])
                    #relationships.append([var1, var3])
                    relationships[var1] = [var3]
                    #print "%s(%s,#%s)" % (var1, var2, var1)
                # relationships have already been constructed by looking at properties of the shapes.
                #if current['type'] == 'RelationshipConnector':
                #    print current['source'], '--->', current['destination']
                #    continue

    if Setup.debugmode:            
        print '\n\n' + str(variables) + '\n\n' + 'relationships: ' + str(relationships) + '\n\n' + str(ER_dictionary) + '\n'
    
    '''
    DETERMINE CARDINALITY OF THE RELATIONSHIPS
    This is some basic code for determining whether a relationship is one-many, many-many, or unspecified.
    TODO: Warn the user if relationship type is invalid (many-one?), but default to one-one
    '''
    for x in json_dict['shapes']:
        shapes_dict = x['details'].get('slots')
        if shapes_dict:
            name = str(x['details'].get('name'))
            dir1 = str(shapes_dict[0].get('cardinality'))
            dir2 = str(shapes_dict[1].get('cardinality'))
            #print x['details'].get('name'), temp[0].get('cardinality'), temp[1].get('cardinality')
            relationships_cardinality[name] = [dir1, dir2]

    if Setup.debugmode:
        print str(relationships_cardinality) + '\n\n'

    possible_targets = relationship_dictionary.keys() + attribute_dictionary.keys()

    print "\nPlease type a target from the list:"
    print '\t' + '    '.join(possible_targets)
    sys.stdout.flush()
    try:
        target = raw_input()
    except:
        exit()

    #if target in ER_dictionary.values():
    if target in possible_targets:
        print 'Target: ', target
        possible_targets.remove(target)
    else:
        print 'Error, target not in list.'
        exit()

    print "\nPlease select features you want to learn over (separated by spaces):"
    print '\t' + '    '.join(possible_targets)
    sys.stdout.flush()
    try:
        features = raw_input()
        features = features.split()
    except:
        exit()
    print 'Features: ', features


    
    print '\n\n' + 'Modes:'

    print '//target'
    target_variables = relationships[target]
    #print target_variables
    if len(target_variables) == 1:
        print "mode: %s(+%s,#%s)." % (target.lower(), variables.get(relationships[target][0]), target.lower())
    if len(target_variables) == 2:
        print "mode: %s(+%s,+%s)." % (target.lower(), variables.get(relationships[target][0]), variables.get(relationships[target][1]))
    
    print '//features'
    #for feature in features:
    # attributes that are "multivalued" should only include the hash value
    for feature in relationships:
        if (len(relationships[feature]) == 2):
            symbol = relationships[feature]
            if (symbol[0] == symbol[1]):
                # This section can be simplified, pay attention to where 'many' is.
                if (relationships_cardinality.get(feature) == ['many', 'many']):
                    #i.e. (friends relationship), print two lines
                    print "mode: %s(%s,%s)." % (feature.lower(), '+' + variables[symbol[0]], '-' + variables[symbol[1]])
                    print "mode: %s(%s,%s)." % (feature.lower(), '-' + variables[symbol[0]], '+' + variables[symbol[1]])
                elif (relationships_cardinality.get(feature) == ['one', 'many']):
                    #i.e. (siblingof), print one line
                    print "mode: %s(%s,%s)." % (feature.lower(), '+' + variables[symbol[0]], '-' + variables[symbol[1]])
                elif (relationships_cardinality.get(feature) == ['many', 'one']):
                    print "mode: %s(%s,%s)." % (feature.lower(), '-' + variables[symbol[0]], '+' + variables[symbol[1]])
        
        if (feature not in features):
            if (len(relationships[feature]) == 1):
                # attributes
                # check if the variable is multivalued
                var = variables.get(relationships[feature][0])
                print "mode: %s(%s,#%s)." % (feature.lower(), '+' + var, feature.lower())
            else:
                output = []
                for var in relationships[feature]:
                    output.append('+' + variables.get(var))
                print "mode: %s(%s)." % (feature.lower(), ','.join(output))
        else:
            # lists of length 1 are attributes
            if (len(relationships[feature]) == 1):
                if relationships[feature][0] in target_variables:
                    # assign +
                    symbol = '+'
                else:
                    # assign -
                    symbol = '+'
                var = variables.get(relationships[feature][0])
                print "mode: %s(%s%s,#%s)." % (feature.lower(), symbol, var, feature.lower())
            # lists of length 2 are relationships
            else:
                output = []
                for var in relationships[feature]:
                    if var in target_variables:
                        # assign +
                        symbol = '+'
                    else:
                        # assign -
                        symbol = '-'
                    var = variables.get(var)
                    output.append(symbol+var)
                print "mode: %s(%s)." % (feature.lower(), ','.join(output))
                    
        if (feature not in features):
            if (len(relationships[feature]) == 1):
                # attributes
                # check if the variable is multivalued
                var = variables.get(relationships[feature][0])
                print "mode: %s(%s,#%s)." % (feature.lower(), '+' + var, feature.lower())
            else:
                output = []
                for var in relationships[feature]:
                    output.append('+' + variables.get(var))
                print "mode: %s(%s)." % (feature.lower(), ','.join(output))

    """


if __name__ == '__main__': main()
