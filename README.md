# Project Title

[![License: Apache](https://img.shields.io/badge/License-Apache-yellow.svg)](https://opensource.org/license/apache-2-0)

Polyhex is a Python library to easily create polyhexes from regular hexagons and export their underlying graph structure to deep-learning frameworks. 

## ✨ About The Project

Polyhex aims to be at the interface between a natural creation of polyhexes and a reliable graph representation of the polyhexes' attributes.

It was designed for the Material Science and Reinforcement Learning communities, but can surely be used for other purposes. 

**Key Features:**
* **Beginner friendly.** Create a polyhex, from <br>
▶️ A list of hexagons or a number of hexagons <br>
▶️ Predefined shapes with flexible dimensions <br>
* **Modular.** Record a polyhex's graph structure: record the edges, the vertices, the hexagons and the border of a polyhex in a simple call.
* **Built for Machine-Learning.** Polyhex offers an off-the-shelf export of your graphs to [PyGeom](https://pytorch-geometric.readthedocs.io/en/latest/), a popular framework for deep-learning on graphs. 

## 🚀 Getting Started

Installing `polyhex` should be as easy as
```
pip install polyhex
```
You can then have a look at the `examples` folder.

## 📓✏️ Documentation

Work in progress

## 🗺️ Roadmap

- [x] Ability to create a polyhex and export it to PyGeom's data format.
- [ ] Implementation of games rules and scoring, like [Cascadia](https://en.wikipedia.org/wiki/Cascadia_(board_game))
- [ ] Game assets
- [ ] C++ routines
- [ ] [OpenSpiel](https://openspiel.readthedocs.io/en/latest/) binders

## 🤝 Contributing

Any contribution and feedback is **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## 📜 License

Distributed under the Apache License. See `LICENSE` for more information.

## 📧 Contact

Contact the authors directly at: emilienvalat@gmail.com

## 🙏 Acknowledgments

Huge thanks to Amit Patel (Red Blob Games) for all the resources about hexagons.

* [Red Blob Games](https://www.redblobgames.com/)