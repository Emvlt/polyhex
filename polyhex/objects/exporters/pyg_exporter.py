"""
Module that defines the export of polyhex graphs to a PyGeometric Hetero Data object
"""
# pylint: disable=line-too-long
from typing import Dict

import torch
from torch_geometric.data import HeteroData, Data
from polyhex.objects.graphs import Graph

__all__ = ('PyGExporter',)


class PyGExporter:
    """
    PyGExporter class: interface between `polyhex` graphs and PyGeometric graphs
    """
    def __init__(self):
        pass

    def template_exporter(self, graph: Graph, distance_kwd: str, record_y=False):
        """Template function to export a graph to PyG

        Args:
            graph (Graph): Graph object. It must have `nodes`, `weights` and `node_to_index` dicts.
            distance_kwd (str): the string identifier of the distance function.
            record_y (bool, optional): Whether or not to record the spatial position of the nodes. As it is ambiguous for the edges, it is not a default parameter of the template. Defaults to False.

        Returns:
            Data: A PyGeometric Data object (https://pytorch-geometric.readthedocs.io/en/latest/generated/torch_geometric.data.Data.html)
        """
        ### Defining graph attributes
        x = []
        edge_index = [[], []]
        edge_attr = []
        y = [] if record_y else None
        ### Appending graph attributes
        for key, node in graph.nodes.items():
            x.append(node.encoding)
            if y is not None:
                y.append([node.x, node.y])
            for neighbour in graph.weights[key]:
                # start node for the edge
                edge_index[0].append(graph.node_to_index[key])
                # End node for the edge
                edge_index[1].append(graph.node_to_index[neighbour.spatial_key])
                edge_attr.append(node.distance(neighbour, kwd=distance_kwd))
        return Data(
            x=torch.tensor(x),
            edge_index=torch.tensor(edge_index),
            edge_attr=torch.tensor(edge_attr),
            num_nodes=graph.n_nodes,
            y=y,
        )

    def export_graph(self, graph: Graph):
        """Factory function to extract a graph

        Args:
            graph (Graph): Graph object. It must have a `name`, a number of nodes `n_nodes`, and `nodes`, `weights`, `node_to_index` dicts.

        Raises:
            NotImplementedError: there is no unique way to export a graph. As `polyhex` aims to be modular, it will throw a `NotImplementedError` if a graph.name has no matching condition explicitely added here.

        Returns:
            Data: A PyGeometric Data object (https://pytorch-geometric.readthedocs.io/en/latest/generated/torch_geometric.data.Data.html)
        """
        if graph.name in ["VertexGraph", "HexagonGraph", "HexagonBorderGraph"]:
            return self.template_exporter(
                graph, distance_kwd="euclidian", record_y=True
            )
        if graph.name in ["EdgeGraph", "EdgeBorderGraph"]:
            return self.template_exporter(graph, distance_kwd="path")

        raise NotImplementedError(
            f"`export_graph` method not implemented for {graph.name}"
        )

    def export_graphs(self, graphs: Dict[str, Graph]):
        """Exports a dict of Graphs

        Args:
            graphs (Dict[str, Graph]): A dictionnary holding the graphs

        Returns:
            HeteroData: A PyGeometric HeteroData object (https://pytorch-geometric.readthedocs.io/en/latest/generated/torch_geometric.data.HeteroData.html)
        """
        return_graph = HeteroData()
        for name, graph in graphs.items():
            return_graph[name] = self.export_graph(graph)
        return return_graph
