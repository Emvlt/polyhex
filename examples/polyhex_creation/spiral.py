"""Example script to create a polyhex with a spiral pattern"""

from polyhex.objects.graphs import HexagonGraph, HexagonBorderGraph
from polyhex.objects import Polyhex

# Creating the hypergraph
hypergraph = {
    "HexagonGraph": HexagonGraph(),
    "HexagonBorderGraph": HexagonBorderGraph(),
}

# The spiral creation requires to record the HexagonBorderGraph
p = Polyhex.create_spiral(3, hypergraph)

p.draw(hypergraph, save_path="spiral")
