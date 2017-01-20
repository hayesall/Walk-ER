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
- Debug Mode (print all the things)
'''

class InputException(Exception):
    def handle(self):
        print self.message

import json
import sys, os
import pygame

def main():
    # specify file to read
    json_file = read_user_input()
    # import the file
    json_data = import_data(json_file)
    # convert from json format to something more python-friendly
    json_dict = json.loads(json_data)

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

    #print '\n\n' + str(variables) + '\n\n' + str(relationships) + '\n\n' + str(ER_dictionary) + '\n'
    
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

    #print str(relationships_cardinality) + '\n\n'

    print "Please type a target from the list:"
    print relationships.keys()
    sys.stdout.flush()
    try:
        target = raw_input()
    except:
        exit()

    #if target in ER_dictionary.values():
    if target in relationships.keys():
        print 'Target: ', target
    else:
        print 'Error, target not in list.'
        exit()

    print "Please select features you want to learn over (separated by spaces)"
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

    

def read_user_input():
    '''
    Read the user-specified input for the file to parse
    Succeeds if the file is valid.
    '''
    args = sys.argv
    if len(args) != 2:
        raise InputException(
            '\nArgument error, exactly one file should be specified.'
            '\nUsage: $ python walk-er.py [file]'
        )
    if not os.path.isfile(args[1]):
        raise InputException(
            '\nFile error, file not found.'
            '\nUsage: $ python walk-er.py [file]'
        )
    return args[1]

def import_data(file_to_read):
    '''
    Reads the contents of 'file_to_read', raises an exception if it cannot be read.
    '''
    try:
        doc = open(file_to_read).read()
    except:
        raise InputException(
            '\nFile error, could not read file.'
            '\nUsage: $ python walk-er.py [file]'
        )
    return doc
        
def extractVariables(json_dict):
    '''
    Input: a json dictionary
    Returns of dictionary of entities, attributes, and relationships
    '''
    pass

def extractRelationshipCardinality(json_dict):
    '''
    "Determine if a relationship is one-many, many-one, many-many, or unspecified in either direction."
    Input: a json dictionary
    Returns: each relationship in the json_dict bound to its cardinality
    i.e. {'SiblingOf': ['one', 'many'], 'ParentOf': ['one', 'many'], 'Father': ['one', 'many']}
    '''
    pass

def walkFeatures(target, list_of_features):
    '''
    "Use user-selected features to construct background/modes."
    Input: [target feature], [a list of features selected by the user].
    Output: (for now, print modes to terminal, in the future write them to a file)
    '''
    pass

if __name__ == '__main__': main()
