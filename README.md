# Walk-ER
Walk-ER for exploring entity/attribute/relationships in Entity-Relational Diagrams and constructing BoostSRL background modes. Parsed from ERDPlus JSON.

> Modes are used to restrict/guide the search space and are a powerful tool in getting relational algorithms such as BoostSRL to work. If your algorithm does not learn anything useful, then the first debug point would be the modes (in the background.txt file).

[GitHub Basic Modes Guide](https://github.com/boost-starai/BoostSRL/wiki/Basic-Modes-Guide)

We define modes as being a powerful tool for getting BoostSRL to function properly, but it leaves an open question: how do we set them in the first place? One of our lab's focus is on users interacting with our algorithms (human-in-the-loop learning and learning with advice). So far we've tried to make modes approachable by writing thorough tutorials, but requiring a user to learn our method by reading lots of documentation does not necessarily imply "easy interaction."

If we cannot necessarily expect the user to know our method from the beginning, perhaps we can present the information in a way that they are more familiar with. **Entity Relational Diagrams** usually come up as a way to express the underlying structure of a database. We want to find an intersection between these diagrams and the BoostSRL modes.

A basic ER-Diagram has three shapes: entities, attributes, and relations.

[https://erdplus.com/#/](https://erdplus.com/#/)