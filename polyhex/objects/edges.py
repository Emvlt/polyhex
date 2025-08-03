from typing import Dict 

import matplotlib.pyplot as plt
from numpy.typing import ArrayLike

from polyhex.objects.nodes import Node

__all__ = ('Edge',)

class Edge(object):
    def __init__(
            self, 
            vertex_0 : Node,
            vertex_1 : Node,
            index : int,
            config_file:Dict ,
            feature : ArrayLike = None,    
            hexagon = None
            ):
        self._vertex_0 = vertex_0
        self._vertex_1 = vertex_1
        self.feature  = feature
        if feature is None:
            self.encoding = None
        else:            
            self.encoding = config_file["encodings"]["habitat"][feature]
        self.index = index
        self.config_file = config_file
        coord_u = self.start.cartesian_coord_vector
        coord_v = self.end.cartesian_coord_vector
        self._key = frozenset((coord_u, coord_v, self.feature))
        self.spatial_key = frozenset((coord_u, coord_v))
        self.hexagon = hexagon
    @property
    def end(self):
        return self._vertex_1
    
    @property
    def key(self):
        return self._key
    
    @property
    def start(self):
        return self._vertex_0   
    
    def draw(
        self, axes, 
        scale = False,
        **kwargs
        ):
        palette = self.config_file['palette']
        if scale:
            start = self.start.cartesian_coord
            end   = self.end.cartesian_coord
        else:
            start = self.start.cartesian_coord_vector
            end   = self.end.cartesian_coord_vector
        if kwargs == {}:
            axes.plot(
                [start[0], end[0]], 
                [start[1], end[1]], palette['edge_colour'],
                )
        else:
            axes.plot(
                [start[0], end[0]], 
                [start[1], end[1]], **kwargs
                )
        polygon_color = palette['habitat'][str(self.feature)]
        
        triangle = [start, end, self.hexagon.centre_node.cartesian_coord_vector]
        axes.add_patch(plt.Polygon(triangle, color=polygon_color))
        return axes
    
    def __eq__(self, other):
        equal_kwd = 'cartesian_coord'
        c0 = isinstance(other, Edge) 
        c1 = (self._vertex_0.equal(other._vertex_0, equal_kwd) and self._vertex_1.equal(other._vertex_1, equal_kwd))
        c2 = (self._vertex_0.equal(other._vertex_1, equal_kwd) and self._vertex_1.equal(other._vertex_0, equal_kwd))
        return c0 and (c1 or c2)

    def __str__(self):
        start_coord = f'({self.start.cartesian_coord_vector[0]}, {self.start.cartesian_coord_vector[1]})'
        end_coord = f'({self.end.cartesian_coord_vector[0]}, {self.end.cartesian_coord_vector[1]})'
        return_str = f'Edge: {start_coord} -> {end_coord} \n'
        return return_str