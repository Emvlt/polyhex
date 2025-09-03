"""
Module that defines the abstract Graph class and different classes of Graphs that inherit from it
"""
# pylint: disable=arguments-differ
# pylint: line-too-long
# pylint: too-few-public-methods

from abc import ABC, abstractmethod
from typing import Dict, Tuple

from polyhex.objects.hexagons import Hexagon
from polyhex.objects.nodes import HexagonVertex
from polyhex.objects.edges import HexagonEdge
from polyhex.objects.polyhexes import Polyhex

__all__ = (
    "Graph",
    "HexagonGraph",
    "VertexGraph",
    "EdgeGraph",
    "EdgeBorderGraph",
    "HexagonBorderGraph",
)


class Graph(ABC):
    """
    Abstract Graph class
    """

    def __init__(self, name: str):
        """Constructor for a graph

        Args:
            name (str) : name of the graph

        By default, a graph has:
            name (str)     : name of the Graph
            n_nodes (int)  : number of nodes
            nodes (dict)   : dictionnary with spatial coordinates as keys and objects (Hexagon, Edge...) as values. It refers to the nodes of the graph.
            weights (dict) : dictionnary with spatial coordinates as keys and a list of objects (Hexagon, Edge...) as values. It refers to the connexions between the nodes of the graph
            nodes (dict)   : the dictionnary with spatial coordinates as keys and integers as values. It refers to the indexing of each node in the graph
        """
        self.name = name
        self.n_nodes = 0

        self.nodes: Dict = {}
        self.weights: Dict = {}
        self.node_to_index: Dict = {}

    @abstractmethod
    def append(self):
        """Append method for the Graph"""
        raise NotImplementedError(
            "The `append` function is not implemented for the abstract `Graph` class"
        )

class VertexGraph(Graph):
    """
    Graph of polyhex vertices
    """

    def __init__(self, name="VertexGraph"):
        super().__init__(name)

    def append(self, hexagon: Hexagon):
        """Append method of the VertexGraph

        Args:
            hexagon (Hexagon): Hexagon of which vertices to append to the graph
        """
        # Add the vertices to the list
        for vertex in hexagon.vertices_list:
            vertex: HexagonVertex
            if vertex.spatial_key not in self.nodes:
                self.nodes[vertex.spatial_key] = vertex
                self.weights[vertex.spatial_key] = []
                self.node_to_index[vertex.spatial_key] = self.n_nodes
                self.n_nodes += 1

                adjency = hexagon.get_vertex_adjency(vertex)
                for coord in adjency:
                    if coord in self.nodes:
                        self.weights[vertex.spatial_key].append(self.nodes[coord])
                        self.weights[coord].append(self.nodes[vertex.spatial_key])


class EdgeGraph(Graph):
    """
    Graph of polyhex edges
    """

    def __init__(self, name="EdgeGraph"):
        super().__init__(name)

    def append(self, hexagon: Hexagon):
        """Append method of the EdgeGraph

        Args:
            hexagon (Hexagon): Hexagon of which edges to append to the graph
        """
        # Add the edges to the list
        for edge in hexagon.edges_list:
            edge: HexagonEdge
            if edge.spatial_key not in self.nodes:
                self.nodes[edge.spatial_key] = edge
                self.weights[edge.spatial_key] = []
                self.node_to_index[edge.spatial_key] = self.n_nodes
                self.n_nodes += 1

                adjency = hexagon.get_edge_adjency(edge)
                for coord in adjency:
                    if coord in self.nodes:
                        self.weights[edge.spatial_key].append(self.nodes[coord])
                        self.weights[coord].append(self.nodes[edge.spatial_key])


class HexagonGraph(Graph):
    """
    Graph of polyhex hexagons
    """

    def __init__(self, name="HexagonGraph"):
        super().__init__(name)

    def append(self, hexagon: Hexagon):
        """Append method of the HexagonGraph

        Args:
            hexagon (Hexagon): Hexagon to append to the graph
        """
        coord = hexagon.hex_coord
        self.nodes[coord] = hexagon
        self.node_to_index[coord] = self.n_nodes
        self.weights[coord] = []
        self.n_nodes += 1
        # Make add all the connections from the new hex to the existing ones
        for adj in hexagon.adjency:
            if adj in self.nodes:
                self.weights[coord].append(self.nodes[adj])
                self.weights[adj].append(self.nodes[coord])


class EdgeBorderGraph(Graph):
    """
    Graph of polyhex edges border
    """

    def __init__(self, name="EdgeBorderGraph"):
        super().__init__(name)

    def append(self, hexagon: Hexagon):
        """Append method of the EdgeBorderGraph.
        The border of a polyhex can be defined by its Edges of by its Hexagons. For Polyhex with varying edge features, it is important to know what edges are on the border

        Args:
            hexagon (Hexagon): Hexagon to append to the graph.
        """
        for edge in hexagon.edges_list:
            edge: HexagonEdge
            if edge.spatial_key in self.nodes:
                self.remove(hexagon, edge)
            else:
                self.add(hexagon, edge)

    def add(self, hexagon: Hexagon, edge: HexagonEdge):
        """Internal helper function to clarify the append code

        Args:
            hexagon (Hexagon): Hexagon to append to the border
            edge (HexagonEdge): Edge considered
        """
        self.nodes[edge.spatial_key] = edge
        self.node_to_index[edge.spatial_key] = self.n_nodes
        self.weights[edge.spatial_key] = []
        # Adding the edge to the weight dictionnary
        adjency = hexagon.get_edge_adjency(edge)
        for coord in adjency:
            if coord in self.nodes:
                self.weights[edge.spatial_key].append(self.nodes[coord])
                self.weights[coord].append(self.nodes[edge.spatial_key])
        # Updating the number of nodes
        self.n_nodes += 1

    def remove(self, hexagon: Hexagon, edge: HexagonEdge):
        """Internal helper function to clarify the append code

        Args:
            hexagon (Hexagon): Hexagon to append to the border
            edge (HexagonEdge): Edge considered
        """
        self.nodes.pop(edge.spatial_key)
        self.node_to_index.pop(edge.spatial_key)
        # Removing the edge from the weight dictionnary
        self.weights.pop(edge.spatial_key)
        adjency = hexagon.get_edge_adjency(edge)
        for coord in adjency:
            if coord in self.nodes and edge in self.weights[coord]:
                self.weights[coord].remove(edge)
        # Updating the number of nodes
        self.n_nodes -= 1


class HexagonBorderGraph(Graph):
    """
    Graph of polyhex hexagons border
    """

    def __init__(self, name="HexagonBorderGraph"):
        super().__init__(name)

    def append(self, hexagon: Hexagon, hexagon_graph: HexagonGraph, polyhex: Polyhex):
        """Append method of the EdgeBorderGraph.
        The border of a polyhex can be defined by its Edges of by its Hexagons. When considering the Hexagon border, it is important to consider the following:
            1. the hexagon border is defined only against a hexagon graph
            2. the hexagon border is made of placeholder hexagons, that look like the ones the polyhex would expect. This is why a `polyhex` object is required.

        Args:
            hexagon (Hexagon): The hexagon to append to the border.
            hexagon_graph (HexagonGraph): The hexagon graph to build the border against.
            polyhex (Polyhex): The polyhex considered
        """
        if not self.nodes:
            for adj in hexagon.adjency:
                self.add(polyhex, adj, hexagon_graph)
        else:
            # 1. Remove the hex from the border
            assert hexagon.spatial_key in self.nodes
            self.nodes.pop(hexagon.spatial_key)
            self.weights.pop(hexagon.spatial_key)
            self.n_nodes -= 1
            for adj in hexagon.adjency:
                phantom = polyhex.placeholder_hex(hex_coord=hexagon.spatial_key)
                if adj in self.nodes:
                    if phantom in self.weights[adj]:
                        self.weights[adj].remove(phantom)
                # 2. Append the border
                else:
                    self.add(polyhex, adj, hexagon_graph)

    def add(self, polyhex: Polyhex, adj: Tuple[int], hexagon_graph: HexagonGraph):
        """Helper function for clarifying the `append` method of the HexagonBorderGraph class.

        Args:
            polyhex (Polyhex): the polyhex considered. The border cannot be defined without the polyhex as it creates placeholder nodes.
            adj (Tuple[int]): One of the adjency coordinate of the considered hexagon
            hexagon_graph (HexagonGraph): the hexagon graph representing the polyhex. The border cannot be defined without the HexagonGraph.
        """
        border_hex = polyhex.placeholder_hex(hex_coord=adj)
        if adj not in hexagon_graph.nodes:
            self.nodes[adj] = border_hex
            self.weights[adj] = []
            for phantom_adj in self.nodes[adj].adjency:
                if phantom_adj in self.nodes:
                    self.weights[adj].append(
                        polyhex.placeholder_hex(hex_coord=phantom_adj)
                    )
                    self.weights[phantom_adj].append(border_hex)

            self.node_to_index[adj] = self.n_nodes
            self.n_nodes += 1
