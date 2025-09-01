from typing import Dict

import torch
from torch_geometric.data import HeteroData, Data
from polyhex.objects.graphs import Graph

class PyGExporter():
    def __init__(self):
        pass

    def template_exporter(self, graph:Graph, distance_kwd:str, record_y =False):
        ### Defining grpah attributes
        x = []
        edge_index = [[],[]]
        edge_attr = []
        y = [] if record_y else None            
        ### Appending graph attributes
        for key, node in graph.nodes.items():
            x.append(node.encoding)
            if y is not None : y.append([node.x, node.y]) 
            for neighbour in graph.weights[key]:
                # start node for the edge
                edge_index[0].append(
                    graph.node_to_index[key]
                    )
                # End node for the edge
                edge_index[1].append(
                    graph.node_to_index[neighbour.spatial_key]
                    )
                edge_attr.append(node.distance(neighbour, kwd=distance_kwd))
        return Data(
            x = torch.tensor(x),
            edge_index = torch.tensor(edge_index),
            edge_attr  = torch.tensor(edge_attr),
            num_nodes = graph.n_nodes,
            y = y
            )

    def export_graph(self, graph : Graph):
        if graph.name in ['VertexGraph', 'HexagonGraph', 'HexagonBorderGraph']:
            return self.template_exporter(graph, distance_kwd = 'euclidian', record_y=True)
        elif graph.name in ['EdgeGraph', 'EdgeBorderGraph']:
            return self.template_exporter(graph, distance_kwd = 'path')
        else:
            raise NotImplementedError(f'`export_graph` method not implemented for {graph.name}')
    
    def export_graphs(self, graphs : Dict[str, Graph]):
        return_graph = HeteroData()
        for name, graph in graphs.items():
            return_graph[name] = self.export_graph(graph)
        return return_graph


