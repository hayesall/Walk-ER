# Walk-ER

Repository for Knowledge Capture (K-CAP) 2017 paper submission: "User Friendly Automatic Construction of Background Knowledge: Mode Construction from ER Diagrams."

## Getting Started

> Modes are used to restrict/guide the search space and are a powerful tool in getting relational algorithms such as BoostSRL to work. If your algorithm does not learn anything useful, then the first debug point would be the modes (in the background.txt file).

Walk-ER is a system for defining background knowledge for use in relational learning algorithms by exploring entity/attribute/relationships in Entity-Relational Diagrams. Refer to the [BoostSRL Basic Modes Guide](https://github.com/boost-starai/BoostSRL/wiki/Basic-Modes-Guide) for more information about modes.

### Prerequisites

* Java 1.8
* Python (2.7, 3.5)

### Installation

`git clone https://github.com/batflyer/Walk-ER.git`

### Basic Usage

WalkER can either be invoked from a terminal or imported as a Python package. Examples of both follow:

1. Interactive version:

   `python WalkER.py -w diagrams/imdb.mayukh`

   `python WalkER.py -rw --number 10 diagrams/imdb.mayukh`

2. As an imported package:

   ```python
   import walker
   from boostsrl import boostsrl

   """Read a diagram file as a string."""
   with open('diagrams/imdb.mayukh') as f:
       diagram = f.read()

   bk = walker.walk(diagram, algo='w', n=3)
   target = bk.target

   background = boostsrl.modes(bk, target, useStdLogicVariables=True, treeDepth=8)
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

* Work was funded partially under a grant from Air Force Office of Scientific Research (AFOSR); Small Business Technology Transfer (STTR); AF13-AT11: "Enhancing the Scaling and Accuracy of Text Analytics Using Joint Inference" (AFOSR STTR Topic AF13-AT11)