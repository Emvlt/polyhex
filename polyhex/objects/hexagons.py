from typing import List, Dict
import math 
import json
import pathlib 
from collections import defaultdict

parent_path = pathlib.Path(__file__).parent.parent.resolve()
with open(parent_path.joinpath('config.json'), 'rb') as fp:
    DEFAULT_CONFIG_FILE = dict(json.load(fp))

import numpy as np
from numpy.typing import ArrayLike

from polyhex.objects import Node, Edge
from polyhex.utilities import replicate_vector
from polyhex.objects import hex_coord_system_dependent
__all__ = ('Hexagon','DEFAULT_CONFIG_FILE')

class Hexagon(object):
    
    def __init__(
            self,
            hex_coord_system  : str = 'axial',
            hex_centre_coord : List[int] = [0,0],
            outer_radius : float = 1,
            top  : str = 'pointy',
            node_feature    : ArrayLike = 0,
            vertex_feature  : ArrayLike = [0],
            edge_feature    : ArrayLike = [0],
            angle_orientation : str = 'clockwise',
            config_file : Dict = None
            ):
        if config_file is None: 
            self.config_file = DEFAULT_CONFIG_FILE
        else:
            self.config_file = config_file
        self._check_hex_coord(hex_coord_system)
        self._hex_coord_system = hex_coord_system

        self._check_hex_centre_coord(hex_centre_coord)

        self._check_top(top)
        self._top = top

        self._centre_node = Node(
            config_file = self.config_file,
            feature = node_feature,
            hex_coord_system = hex_coord_system,
            hex_coord = hex_centre_coord,
            cartesian_coord_vector = self._hex_coord_to_cartesian(hex_centre_coord)
            )
        self._allocate_hex_coord(hex_centre_coord)

        self._check_radius(outer_radius)
        self._radius = outer_radius

        self._compute_dimensions()
        
        self._check_angle_orientation(angle_orientation)
        self._angle_orientation = angle_orientation

        self._create_vertices(vertex_feature)

        self._create_edges(edge_feature)

        # self._set_edges_hex_neighbours()
        # self._set_edges_edge_neighbours()

        self._compute_cartesian_coord()
        self.free  = True
        self.token = None

    def _allocate_hex_coord(self, hex_coord):
        if self.hex_coord_system in ['axial', 'offset', 'doubled']:
            assert len(hex_coord) == 2
            self._q = hex_coord[0]
            self._r = hex_coord[1]
            self._s = None
        elif self.hex_coord_system == ['cube']:
            assert len(hex_coord) == 3
            self._q = hex_coord[0]
            self._r = hex_coord[1]
            self._s = hex_coord[2]
        else:
            raise NotImplementedError
    
    def _check_angle_orientation(self, angle_orientation:str):
        assert angle_orientation == 'clockwise' or angle_orientation == 'counterclockwise', f"The angle orientation of an hexagon can only be 'clockwise' or 'counterclockwise', got {angle_orientation}"

    def _check_hex_centre_coord(self, coordinates:List[int]):
        if self.hex_coord_system in ['offset', 'axial', 'doubled']:
            assert len(coordinates) == 2
        else:
            assert len(coordinates) == 3

        assert all(isinstance(item, int) for item in coordinates)
    
    def _check_hex_coord(self, hex_coord_system):
        assert hex_coord_system in ['offset', 'cube', 'axial', 'doubled']
        if hex_coord_system != 'axial':
            raise NotImplementedError

    def _check_top(self, top:str):
        assert top == 'flat' or top == 'pointy', f"The top of an hexagon can only be 'flat' or 'pointy', got {top}"
        if top == 'flat':
            raise NotImplementedError

    def _check_radius(self, radius: float):
        assert isinstance(radius, (float, int)), f"The outer radius of the hexagon must be defined as an int or a float, got {type(radius)}"

    def _compute_dimensions(self):
        if self.top == 'flat':
            raise NotImplementedError
            self._height = math.sqrt(3) * self.radius
            self._width  = 2* self.radius

        elif self.top == 'pointy':
            self._height = 2 * self.radius
            self._width  = math.sqrt(3) * self.radius
            self._min_h = self.radius /2
            self._min_w  = self._width
        else:
            raise ValueError
        
    def _compute_cartesian_coord(self):
        # centre_node
        self.centre_node.cartesian_coord = np.einsum('i,i->i',self.centre_node.cartesian_coord_vector, self.min_dims)
            
        for i in range(6):
            v = self.get_vertex(i)
            v.cartesian_coord = np.einsum('i,i->i', v.cartesian_coord_vector, self.min_dims)
        
    def _vertex_coord_factory(self):
        centre_node_coord_vector = self.centre_node.cartesian_coord_vector
        cx = centre_node_coord_vector[0]
        cy = centre_node_coord_vector[1]
        vertex_coords_vec = []
        if self.top == 'pointy':
            if self.angle_orientation == 'clockwise':
                vertex_coords_vec.append((cx, cy+2))
                vertex_coords_vec.append((cx+1, cy+1))
                vertex_coords_vec.append((cx+1, cy-1))
                vertex_coords_vec.append((cx, cy-2))
                vertex_coords_vec.append((cx-1, cy-1))
                vertex_coords_vec.append((cx-1, cy+1))
                
            elif self.angle_orientation == 'counterclockwise':
                raise NotImplementedError
        else:
            raise ValueError
        return vertex_coords_vec

    def _create_vertices(self, vertex_feature):
        if len(vertex_feature) == 1:
            vertex_feature = replicate_vector(vertex_feature, 6)
        elif len(vertex_feature) == 6:
            pass
        else:
            raise ValueError(f'Length of vertex_feature can only be 1 or 6, got {len(vertex_feature)}')

        vertex_coords = self._vertex_coord_factory()
        self._vertices = {
                    i : Node(
                        config_file=self.config_file,
                        feature = None,
                        cartesian_coord_vector = vertex_coords[i]
                    ) for i in range(6)
                }  
        
    def _create_edges(self, edge_feature):
        if len(edge_feature) == 1:
            edge_feature = replicate_vector(edge_feature, 6)
        elif len(edge_feature) == 6:
            pass
        else:
            raise ValueError(f'Length of edge_feature {edge_feature} can only be 1 or 6, got {len(edge_feature)}')
        self.edges = {}
        self.edges_to_feature = {}
        self.feature_to_edges = defaultdict(list)
        for i in range(6):
            feature = edge_feature[i]
            edge = Edge(
                    vertex_0 = self.get_vertex(i), 
                    vertex_1 = self.get_vertex((i+1)%6),
                    feature = feature,
                    index = i,
                    config_file=self.config_file,
                    hexagon=self
                    )
            self.edges[i] = edge
            # Map the key to the feature
            self.edges_to_feature[edge.key] = feature
            # Map the feature to the keys
            self.feature_to_edges[feature].append(edge.key)

    def _hex_coord_to_cartesian(self, hex_coord):
        if self.hex_coord_system == 'axial':
            assert len(hex_coord) == 2, f"For the axial coordinate system, two coordinates are requires, got {len(hex_coord)}"
            x, y = self._axial_to_cartesian(
                q=hex_coord[0],
                r=hex_coord[1]
                )
        else:
            raise NotImplementedError(f'Not implemented for {self.hex_coord_system}')
        return (x,y)

    def _axial_to_cartesian(self, q:int,r:int):
        assert isinstance(q, int)
        assert isinstance(r, int)
        
        if self.top == 'pointy':
            x = 2*q + r
            y = -3*r
        elif self.top == 'flat':
            raise NotImplementedError
        else:
            raise ValueError(f'{self.top=}')
        
        return x, y 

    # @hex_coord_system_dependent
    @property
    def adjency(self):
        if self.angle_orientation == 'clockwise':
            q = self.q
            r = self.r
            return [(q+1, r-1),(q+1, r),(q, r+1),
                (q-1, r+1),(q-1, r),(q, r-1)]
        else:
            raise NotImplementedError

    @property
    def angle_orientation(self):
        return self._angle_orientation
    
    @property
    def centre_node(self):
        return self._centre_node
    
    @property
    def feature(self):
        return self.centre_node.feature
    
    @property
    def hex_coord(self):
        if self.hex_coord_system =='axial':
            return (self.q, self.r)
        else:
            raise NotImplementedError
    
    @property
    def hex_coord_system(self):
        return self._hex_coord_system
    
    @property
    def height(self):
        return self._height
    
    @property
    def min_h(self):
        return self._min_h
    
    @property
    def min_dims(self):
        return [self.min_w, self.min_h]
    
    @property
    def min_w(self):
        return self._min_w
    
    @property
    def q(self):
        return self._q
    
    @q.setter
    def q(self, value):
        self._q = value

    @property
    def r(self):
        return self._r
    
    @r.setter
    def r(self, value):
        self._r = value
    
    @property
    def radius(self):
        return self._radius
    
    @property
    def s(self):
        return self._s
    
    @s.setter
    def s(self, value):
        self._s = value
    
    @property
    def top(self):
        return self._top
    
    @property
    def vertices(self):
        return self._vertices

    @property
    def width(self):
        return self._width
        
    def add_token(self, token):
        assert self.free, f'The hexagon ({self.q}, {self.r}) is occupied.'
        assert self.centre_node.free, f'The centre node of the hexagon ({self.q}, {self.r}) is occupied.'
        assert self.feature in self.config_file['compatibility']["token_to_habitat"][token]
        self.centre_node.token = token
        self.centre_node.free = False
        self.token = token
        self.free = False
        
    def is_compatible(self, other):
        return (isinstance(other, Hexagon) 
                and self.hex_coord_system == other.hex_coord_system 
                and self.radius == other.radius
                and self.top == other.top 
                and self.angle_orientation == other.angle_orientation
                )         
    
    def get_vertex(self, index:int):
        assert isinstance(index, int), f'{type(index)}'
        assert 0 <= index <= 5
        return self.vertices[index]
    
    def get_edge(self, index:int):
        assert isinstance(index, int), f'{type(index)}'
        assert 0 <= index <= 5
        return self.edges[index]    

    def get_edge_adjency(self, index:int):
        return self.adjency[index]
    
    def get_graph_nodes(self):
        return [edge.encoding for edge in self.edges.values()]

    def get_graph_edges(self):
        starts = []
        ends   = []
        edge_attrs = []
        for i in range(6):
            for j in range(6):
                if i!=j:
                    starts.append(i)
                    ends.append(j)
                    edge_attrs.append(1 if self.edges[i].feature == self.edges[j].feature else 0)
        return  [starts, ends, edge_attrs]
    
    def draw(self, axes,
        scale = False
        ):
        axes = self.centre_node.draw(
            axes, 
            scale=scale
            )
        for i in range(6):
            axes = self.get_edge(i).draw(
                axes,
                scale=scale
                )
        return axes

    def __str__(self):
        # centre_node
        print_str = f'centre_node = ({self.centre_node})\n'
        return print_str
    
    def __repr__(self):
        return f'{self.centre_node.hex_coord}'
    
    def __eq__(self, other):
        return self.is_compatible(other) and self.centre_node.equal(other.centre_node, 'hex_coord')
    
    def __hash__(self):
        return hash(
                (
                type(self), self.centre_node
                )
            )