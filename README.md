# Walk-ER

Repository for Knowledge Capture (K-CAP) 2017 paper submission: "User Friendly Automatic Construction of Background Knowledge: Mode Construction from ER Diagrams."

## Getting Started

> Modes are used to restrict/guide the search space and are a powerful tool in getting relational algorithms such as BoostSRL to work. If your algorithm does not learn anything useful, then the first debug point would be the modes (in the background.txt file).

Walk-ER is a system for defining background knowledge for use in relational learning algorithms by exploring entity/attribute/relationships in Entity-Relational Diagrams. Refer to the [BoostSRL Basic Modes Guide](https://github.com/boost-starai/BoostSRL/wiki/Basic-Modes-Guide) for more information about modes.

### Prerequisites

* Java 1.8
* Python (2.7, 3.5)

### Installation

* Download the latest version from the GitHub repository (including five datasets):

  ```bash
  $ git clone https://github.com/batflyer/Walk-ER.git
  ```

### Basic Usage

WalkER can either be invoked from a terminal or imported as a Python package. Examples of both follow:

1. Interactive version:

   * Options overview (output of `python walker.py -h`):

   ```
   usage: WalkER_rewrite.py [-h] [-v] [--number NUMBER] [-w | -s | -e | -r | -rw]
                         diagram_file
   
   Walk-ER: a system for walking the paths in anentity-relational diagram.
   Written by Alexander L. Hayes (Alexander.Hayes@utdallas.edu) and Mayukh Das.
   University of Texas at Dallas. STARAI Lab (dir. Professor Natarajan)
   
   positional arguments:
     diagram_file
   
   optional arguments:
     -h, --help         show this help message and exit
     -v, --verbose      Increase verbosity to help with debugging.
     --number NUMBER    Select number of features to walk to (assumes that
                        Important features are ordered from most important to
                        least important). Defaults to number_attributes +
                        number_relations if chosen number is greater than both.
     -w, --walk         [Default] Walk graph from target to features.
     -s, --shortest     Walk the graph from target to features. If there are
                        multiple paths, take the shortest. If the shortest are
                        equal lengths, walk both.
     -e, --exhaustive   Walk graph from every feature to every feature.
     -r, --random       Ignore features the user selected and walk (-w) from the
                        target to random features.
     -rw, --randomwalk  Walk a random path from the target until reaching a depth
                        limit (specified with --number).
   
   Copyright 2017 Free Software Foundation, Inc. License GPLv3+: GNU GPL version
   3 or later <http://gnu.org/licenses/gpl.html>. This is free software: you are
   free to change and redistribute it. There is NO WARRANTY, to the extent
   permitted by law.
   ```

   * Examples:
   
      * `$ python walker.py -w diagrams/imdb.mayukh`
      
      * `$ python walker.py -rw --number 10 diagrams/imdb.mayukh`

2. As an imported package:

   ```python
   import walker
   from boostsrl import boostsrl

   """Read a diagram file as a string."""
   with open('diagrams/imdb.mayukh') as f:
       diagram = f.read()

   """walk method accepts the same algorithm names as the interactive version."""
   bk = walker.walk(diagram, algo='w', n=3)
   target = [bk.target]

   """Use the boostsrl package to construct modes."""
   background = boostsrl.modes(bk, target, useStdLogicVariables=True, maxTreeDepth=4, nodeSize=3)

   ...

   ```

## Citation

If you build on this code or the ideas of the paper, please use the following citation.

```
@inproceedings{kcap2017ermodeconstruction,
  author = {Alexander Hayes and Mayukh Das and Phillip Odom and Sriraam Natarajan},
  title  = {User Friendly Automatic Construction of Background Knowledge: Mode Construction from ER Diagrams},
  booktitle = {KCAP},
  year   = {2017}
}
```

## Acknowledgements

* Mayukh Das and Sriraam Natarajan gratefully acknowledge the support of the CwC Program Contract W911NF-15-1-0461 with the US Defense Advanced Research Projects Agency (DARPA) and the Army Research Office (ARO).
* Phillip Odom and Sriraam Natarajan acknowledge the support of the Army Research Office (ARO) grant number W911NF-13-1-0432 under the Young Investigator Program.
