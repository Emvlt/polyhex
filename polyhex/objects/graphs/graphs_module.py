from abc import ABC, abstractmethod
from typing import Dict, Tuple, List

from polyhex.objects.new_hexagons import Hexagon
from polyhex.objects.new_nodes import HexagonVertex
from polyhex.objects.new_edges import HexagonEdge
from polyhex.objects.new_polyhexes import Polyhex

__all__ = ('Graph', 'HexagonGraph', 'VertexGraph', 'EdgeGraph', 'EdgeBorderGraph', 'HexagonBorderGraph')

class Graph(ABC):
    def __init__(self, name : str):
        self.name = name
        self.n_nodes = 0

        self.nodes : Dict[Tuple[int], Hexagon]= {}
        self.weights : Dict[Tuple[int], List[Hexagon]] = {}
        self.node_to_index : Dict[Tuple[int], int] = {}

    @abstractmethod
    def append(self, object):
        pass

    @abstractmethod
    def remove(self, object):
        pass

class VertexGraph(Graph):
    def __init__(self, name = 'VertexGraph'):
        super().__init__(name)
        
    def append(self, hexagon : Hexagon):
        # Add the vertices to the list
        for vertex in hexagon.vertices_list:
            vertex : HexagonVertex
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

    def remove(self, hexagon:Hexagon):
        raise NotImplementedError
    
class EdgeGraph(Graph):
    def __init__(self, name = 'EdgeGraph'):
        super().__init__(name)
        
    def append(self, hexagon : Hexagon):
        # Add the edges to the list
        for edge in hexagon.edges_list:
            edge : HexagonEdge
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

    def remove(self, hexagon:Hexagon):
        raise NotImplementedError


class HexagonGraph(Graph):
    def __init__(self, name = 'HexagonGraph'):
        super().__init__(name)
        
    def append(self, hexagon : Hexagon):
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

    def remove(self, hexagon:Hexagon):
        raise NotImplementedError
    
class EdgeBorderGraph(Graph):
    def __init__(self, name = 'EdgeBorderGraph'):
        super().__init__(name)
        
    def append(self, hexagon : Hexagon):
        for edge in hexagon.edges_list:    
            edge:HexagonEdge        
            if edge.spatial_key in self.nodes:
                self.remove(hexagon, edge)

            else:
                self.add(hexagon, edge)

    def add(self, hexagon: Hexagon, edge:HexagonEdge):
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
                
    def remove(self, hexagon: Hexagon, edge:HexagonEdge):
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
    def __init__(self, name = 'HexagonBorderGraph'):
        super().__init__(name)
        
    def append(
            self, 
            hexagon : Hexagon, 
            hexagon_graph: HexagonGraph, 
            polyhex:Polyhex
            ):
        if self.nodes == {}:
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

    def add(self, polyhex: Polyhex,  adj:HexagonEdge, hexagon_graph):
        border_hex = polyhex.placeholder_hex(hex_coord = adj)
        if adj not in hexagon_graph.nodes:
            self.nodes[adj] = border_hex
            self.weights[adj] = []
            for phantom_adj in self.nodes[adj].adjency:
                if phantom_adj in self.nodes:
                    self.weights[adj].append(polyhex.placeholder_hex(hex_coord = phantom_adj))
                    self.weights[phantom_adj].append(border_hex)

            self.node_to_index[adj] = self.n_nodes
            self.n_nodes += 1
                
    def remove(self, hexagon: Hexagon):
        raise NotImplementedError

    
