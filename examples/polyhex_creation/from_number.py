"""Example script to create a polyhex from a number of hexagons"""

from polyhex.objects.graphs import HexagonGraph, HexagonBorderGraph
from polyhex.objects import Polyhex


hypergraph = {
    "HexagonGraph": HexagonGraph(),
    "HexagonBorderGraph": HexagonBorderGraph(),
}

p = Polyhex.create_from_number(5, hypergraph)

p.draw(hypergraph, save_path="from_number")
