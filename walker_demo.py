from __future__ import print_function
#from boostsrl import boostsrl
import walker

"""Read the diagram file as a string."""
with open('diagrams/imdb.mayukh') as f:
    diagram = f.read()

dictionaries = WalkER.BuildDictionaries(diagram)


target = dictionaries.target
all_features = list(set(dictionaries.relations).union(set(dictionaries.attributes)) - set([target]))
features = dictionaries.importants

networks = WalkER.Networks(target, features, dictionaries)
all_paths = networks.paths_from_target_to_features()

networks.walkFeatures(all_paths, shortest=True)

bk = networks.all_modes_boostsrl
target = [networks.target]

print(bk)
#background = bsrl.modes(bk, target, useStdLogicVariables=True, treeDepth=4, nodeSize=2)
