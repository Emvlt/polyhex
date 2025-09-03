from typing import Dict 

import matplotlib.pyplot as plt
from numpy.typing import ArrayLike
from matplotlib.artist import Artist

from polyhex.objects.nodes import Node
from polyhex.polyhex.objects.nodes import HexagonVertex
from polyhex.polyhex.objects.hexagons import Hexagon

__all__ = ('Edge',)

# class HexagonEdge(BaseModel):
#     """HexagonEdge class.

#     Args:
#         hexagon (Hexagon) : the hexagon to which the edge's belong
#         start (HexagonVertex) : the start vertex
#         end (HexagonVertex) : the end  vertex
#         index (int) : the edge's index in the hexagon (0 to 5)
#         feature (ArrayLike) : the edge's feature
#         free (bool): Identifies if there is something on the edge. Defaults to False.
#         token (ArrayLike): Identifies what is on the edge. Defaults to None

#     Args:
#         BaseModel (_type_): _description_
#     """
#     hexagon : Hexagon
#     start : HexagonVertex
#     end   : HexagonVertex
#     index   : int
#     feature : ArrayLike = 'placeholder'
#     model_config = ConfigDict(arbitrary_types_allowed=True)
#     def __post_init__(self):
#         self.centre = [self.hexagon.x, self.hexagon.y]
#         self.spatial_key = frozenset(
#             self.start.spatial_key, self.end.spatial_key
#         )
#         self.feature_key = frozenset(
#             self.spatial_key, self.feature
#         )
#         self.render_assets = self.hexagon.assets['render']
#         self.compat_assets = self.hexagon.assets['compatibility']
#         self.name = 'HexagonEdge'
#         assert self.name in self.render_assets, f"There is no {self.name} key in the render assets file. Please provide one."
#         assert self.name in self.compat_assets, f"There is no {self.name} key in the compatibility assets file. Please provide one."
#         self.encoding_assets = self.hexagon.assets["encodings"][self.name]

#     @property
#     def encoding(self):
#         return self.encoding_assets[self.feature]

#     def draw(self, save = True):
#         """The draw function is a convenience function that wraps the `render` function. It is used for standalone drawing and generates a figure which is saaved based on the save boolean argument

#         Args:
#             save (bool, optional): _description_. Defaults to True.
#         """
#         fig = plt.figure(figsize=(2,2))
#         axes = fig.gca()
#         axes.axis('off')
#         axes = self.render(axes)
#         if save:
#             plt.savefig(f'{self.name}', bbox_inches = 'tight')
#             plt.clf()
#             plt.close(fig)
#         else:
#             plt.show(axes)

#     def render(self, axes:Artist):
#         render_params = self.render_assets[self.name]["feature"][self.token]
#         axes.plot(
#             [self.start.x, self.end.x], 
#             [self.start.y, self.end.y], 
#             render_params['line'])
#         triangle = [self.start, self.end, self.centre]
#         axes.add_patch(plt.Polygon(triangle, render_params['triangle']))
#         return axes
    
#     def __eq__(self, other):
#         return  isinstance(other, HexagonEdge) and self.feature_key == other.feature_key
    
#     def __str__(self):
#         return f'Edge: {self.start} -> {self.end} \n'
    
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