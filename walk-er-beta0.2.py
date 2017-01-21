'''
Walk-ER vBeta0.2
"Walker" for Entity-Relational Diagrams from ERDPlus
https://erdplus.com/#/

Written by Alexander L. Hayes, Indiana University STARAI Lab
Last Updated: January 20, 2017

> Used for parsing the JSON file exports from ERDPlus.
> Parses the document, rebuilds the relationships and assists the user in creating
  a BoostSRL Background Modes file.

TODO:
- SQL Table Conversion (may or may not be possible)
- pygame
- Multivalued vs. binary Attributes:
  --> multivalued: departmenta(+professorid,#departmenta).
  --> binary:      male(#nameid).
'''

class InputException(Exception):
    def handle(self):
        print self.message

import json
import sys, os
import pygame

class setup:
    
    def __init__(self):
        self.debugmode = False

    def read_user_input(self):
        '''Read the user-specified input for the file to parse
        Succeeds if the file is valid.'''
        args = sys.argv
        if '-d' in args:
            self.debugmode = True
            args.remove('-d')
        if len(args) != 2:
            raise InputException(
                '\nArgument error, exactly one file should be specified.'
                '\nUsage: $ python walk-er.py [-d] [file]'
            )
        if not os.path.isfile(args[1]):
            raise InputException(
                '\nFile error, file not found.'
                '\nUsage: $ python walk-er.py [-d] [file]'
            )
        return args[1]

    def import_data(self, file_to_read):
        '''Reads the contents of 'file_to_read', raises an exception if it cannot be read.'''
        try:
            doc = open(file_to_read).read()
        except:
            raise InputException(
                '\nFile error, could not read file.'
                '\nUsage: $ python walk-er.py [-d] [file]'
            )
        return doc

class walker:

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
        
        if 'shapes' in json_dict:
            for i in range(len(json_dict['shapes'])):
                current = json_dict['shapes'][i]
                if ('type' in current) and ('details' in current):
                    number = str(current['details'].get('id'))
                    name = str(current['details'].get('name'))
                    ER_dictionary[number] = name
                    if current['type'] == 'Entity':
                        variable_dictionary[number] = name.lower() + 'id'
        if self.debugmode:
            print 'Variables:\n', str(variable_dictionary)
            print 'All Shapes:\n', str(ER_dictionary)
        return ER_dictionary, variable_dictionary
        
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
                        #print current
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
        TODO: ensure that directions are correct 1-->one, 1-->many
        "Determine if if a relationship is one-many, many-one, many-many, or unspecified."
        Input: a json dictionary and a variable dictionary
        Returns a dictionary of [to, from, toCardinality, fromCardinality]
        i.e. {'Father': ['1', '1', 'one', 'many'], ...}
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
                relationship_dictionary[name].append(dir1)
                relationship_dictionary[name].append(dir2)

        if self.debugmode:
            print 'Relationships:\n', str(relationship_dictionary)
        return relationship_dictionary

    def userOptions(self, attribute_dictionary, relationship_dictionary):
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
        return [target, final_features]
        
    def walkFeatures(self, target, list_of_features):
        '''
        "Use user-selected features to construct background/modes."
        Input: [target feature], [a list of features selected by the user].
        Output: (for now, print modes to terminal, in the future write them to a file)
        '''
        pass

def main():
    Setup = setup()
    # specify file to read
    json_file = Setup.read_user_input()
    # import the file
    json_data = Setup.import_data(json_file)
    # convert from json format to something more python-friendly
    json_dict = json.loads(json_data)
    
    #Check if the user set the "debug mode" flag (-d)
    Walker = walker(Setup.debugmode)
    Walker.debug()
    
    # find the variables (based on entities in the graph), also create a dictionary of all shapes
    ER_dictionary, variable_dictionary = Walker.extractVariables(json_dict)

    # find the attributes
    attribute_dictionary = Walker.extractAttributes(json_dict, ER_dictionary, variable_dictionary)
    
    # find the relationships and their cardinality # {'Friends', ['1','1','many','many']}
    relationship_dictionary = Walker.extractRelationships(json_dict, variable_dictionary)
    
    # ask the user to choose some a target and relavent features:
    targetAndFeatures = Walker.userOptions(attribute_dictionary, relationship_dictionary)

    print targetAndFeatures
    exit()
    
    """
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

    """
    
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
                    
        '''
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
        '''


if __name__ == '__main__': main()
