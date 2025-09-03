"""Example script to create a polyhex from a list of hexagons"""

from polyhex.objects.graphs import HexagonGraph, HexagonBorderGraph
from polyhex.objects.hexagons import Hexagon
from polyhex.objects import Polyhex

hypergraph = {
    "HexagonGraph": HexagonGraph(),
    "HexagonBorderGraph": HexagonBorderGraph(),
}

hex_list = [
    Hexagon(hex_coord=(0, 0)),
    Hexagon(hex_coord=(0, 1)),
    Hexagon(hex_coord=(-1, 0)),
    Hexagon(hex_coord=(1, 0)),
]

p = Polyhex.create_from_iterable(hex_list, hypergraph)

p.draw(hypergraph, "from_list")
