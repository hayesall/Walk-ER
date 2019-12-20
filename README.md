<p align="center">
   <img src="media/WalkERLogo.png">
</p>

<br><br>

Source code and TeX for "*User Friendly Automatic Construction of Background Knowledge: Mode Construction from ER Diagrams*." K-CAP 2017

[![](https://img.shields.io/badge/DOI-10.1145%2F3148011.3148027-blue)](https://doi.org/10.1145/3148011.3148027)

## Paper

Explore further on [hayesall.com](https://hayesall.com/publications/construction-background-knowledge/).

- [📄 Read Online](https://starling.utdallas.edu/assets/pdfs/KCAP17Mode.pdf)
  - [ACM Digital Library](https://dl.acm.org/citation.cfm?doid=3148011.3148027)
  - [Preprint - arXiv:1912.07650 [cs.AI]](https://arxiv.org/abs/1912.07650)
  - [DeepAI Publication Page](https://deepai.org/publication/user-friendly-automatic-construction-of-background-knowledge-mode-construction-from-er-diagrams)
- [📥 Download a PDF](https://github.com/starling-lab/Walk-ER/raw/master/TeX_src/UserFriendlyAutomatedConstructionOfBackgroundKnowledge.pdf)

### Updates

- (2019-12-16): [Harsha Kokel](http://utdallas.edu/~hkokel/) extended this in "Just-another Walk-ER" ([GitHub](https://github.com/harshakokel/JA-Walk-ER), [ReadTheDocs](https://ja-walk-er.readthedocs.io/en/latest/index.html)).

### Citation

If you build on this code or the ideas of the paper, please consider citing.

```latex
@inproceedings{hayes2017userfriendly,
   author = {Hayes, Alexander L. and Das, Mayukh and Odom, Phillip and Natarajan, Sriraam},
   title = {User Friendly Automatic Construction of Background Knowledge: Mode Construction from ER Diagrams},
   booktitle = {Proceedings of the Knowledge Capture Conference},
   series = {K-CAP 2017},
   year = {2017},
   isbn = {978-1-4503-5553-7},
   location = {Austin, TX, USA},
   pages = {30:1--30:8},
   articleno = {30},
   numpages = {8},
   url = {http://doi.acm.org/10.1145/3148011.3148027},
   doi = {10.1145/3148011.3148027},
   acmid = {3148027},
   publisher = {ACM},
   address = {New York, NY, USA},
}
```

---

## Getting Started

> Modes are used to restrict/guide the search space and are a powerful tool in getting relational algorithms such as BoostSRL to work. If your algorithm does not learn anything useful, then the first debug point would be the modes (in the background.txt file).

Walk-ER is a system for defining background knowledge for use in relational learning algorithms by exploring entity/attribute/relationships in Entity-Relational Diagrams. Refer to the [BoostSRL Basic Modes Guide](https://starling.utdallas.edu/software/boostsrl/wiki/basic-modes/) for more information about modes.

### Prerequisites

* Java 1.8
* Python (2.7, 3.5)

### Installation

Download the latest version from the GitHub repository. This includes five datasets:

```bash
$ git clone https://github.com/hayesall/Walk-ER.git
```

## Basic Usage

- Files representing the ER-Diagrams are in the [`diagrams/`](https://github.com/hayesall/Walk-ER/tree/master/diagrams) directory.
- Datasets used in the experiments are in the [`datasets/`](https://github.com/hayesall/Walk-ER/tree/master/datasets) directory.

Walk-ER can either be invoked from a terminal.

- Options overview (output of `python walker.py -h`):

  ```
  usage: WalkER_rewrite.py [-h] [-v] [--number NUMBER] [-w | -s | -e | -r | -rw] diagram_file

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
  ```

### Examples

  - `$ python walker.py -w diagrams/imdb.mayukh`

  ```console
  //target is workedunder
  mode: actor(+personid).
  mode: female_gender(+personid).
  mode: genre(+personid,-genreid).
  mode: movie(-movieid,+personid).
  mode: workedunder(+personid,+personid).
  ```

  - `$ python walker.py -rw --number 10 diagrams/imdb.mayukh`

  ```console
  //target is workedunder
  mode: actor(+personid).
  mode: female_gender(+personid).
  mode: genre(+personid,-genreid).
  mode: movie(+movieid,+personid).
  mode: workedunder(+personid,+personid).
  mode: workedunder(+personid,-personid).
  mode: workedunder(-personid,+personid).
  ```

## Acknowledgements

* Mayukh Das and Sriraam Natarajan gratefully acknowledge the support of the CwC Program Contract W911NF-15-1-0461 with the US Defense Advanced Research Projects Agency (DARPA) and the Army Research Office (ARO).
* Phillip Odom and Sriraam Natarajan acknowledge the support of the Army Research Office (ARO) grant number W911NF-13-1-0432 under the Young Investigator Program.
* Icon in the logo is "Trail" by [Martina Krasnayová](https://thenounproject.com/bubblee.tinka/) from the Noun Project, used under a [Creative Commons (CC) Attribution 3.0 United States License](https://creativecommons.org/licenses/by/3.0/us/).
