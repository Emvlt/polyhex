""" Example script to create a polyhex that are tilings"""

from polyhex.objects.graphs import HexagonGraph, HexagonBorderGraph
from polyhex.objects import Polyhex

### odd-right rectangular tiling
hypergraph = {
    "HexagonGraph": HexagonGraph(),
    "HexagonBorderGraph": HexagonBorderGraph(),
}

p = Polyhex.create_tiling(5, 5, "rectangular", hypergraph, offset="odd-r")

p.draw(hypergraph, save_path="rectangular odd-r tiling")

### even-right rectangular tiling
hypergraph = {
    "HexagonGraph": HexagonGraph(),
    "HexagonBorderGraph": HexagonBorderGraph(),
}

p = Polyhex.create_tiling(5, 5, "rectangular", hypergraph, offset="even-r")

p.draw(hypergraph, save_path="rectangular even-r tiling")

### tilted tiling

hypergraph = {
    "HexagonGraph": HexagonGraph(),
    "HexagonBorderGraph": HexagonBorderGraph(),
}

Polyhex.create_tiling(5, 5, "tilted", hypergraph)

p.draw(hypergraph, save_path="tilted tiling")
