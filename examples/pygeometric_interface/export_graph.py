"""Example script to export a polyhex to PyGeometric"""

from polyhex.objects import Polyhex
from polyhex.objects.exporters import PyGExporter
from polyhex.objects.graphs import HexagonGraph, HexagonBorderGraph

# Creating the hypergraph
hypergraph = {
    "HexagonGraph": HexagonGraph(),
    "HexagonBorderGraph": HexagonBorderGraph(),
}

# The spiral creation requires to record the HexagonBorderGraph
p = Polyhex.create_spiral(3, hypergraph)

exporter = PyGExporter()

pyg_heterodata = exporter.export_graphs(hypergraph)

print(pyg_heterodata)