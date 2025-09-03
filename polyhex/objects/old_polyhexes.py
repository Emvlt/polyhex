from typing import List, Dict, Tuple

import matplotlib.pyplot as plt 
from scipy.cluster.hierarchy import DisjointSet
import pandas as pd 

from polyhex.objects.decorators import hex_coord_system_dependent
from polyhex.objects import Hexagon, Edge

__all__ = ('Polyhex',)

class Polyhex(object):
    def __init__(
        self,
        hexagons : List[Hexagon] | Dict[str, Hexagon] | Tuple[Hexagon]
        ):
        
        assert hexagons is not None, f"A Polyhex can only be created using a list of hexagons `hexagon_list`."

        # Physical properties
        self.polyhex_border = {}
        # self.feature_border_edges = {}
        # self.inner_borders = {}
        self.border_edges_connectivity = {}

        self.edges    = {}
        self.hexagons = {}
        self.vertices = {}
        # feature DisjointSets
        self.hexes_in_area = {}

        self._create_from_iterable(hexagons)
        
    def _check_iterable_consistency(
            self, hexagons :List[Hexagon] | Dict[str, Hexagon]
            ):
        if isinstance(hexagons, List):
            if len(hexagons) == 1:
                return True
            first_hex = hexagons[0]
            return all([first_hex.is_compatible(other_hex) for other_hex in hexagons[1:]]) and len(hexagons) == len(set(hexagons))
        elif isinstance(hexagons, Dict):
            raise NotImplementedError
        else:
            raise ValueError


    def _create_from_list(self, hexagons:List[Hexagon]):
        # Extract the properties of the polyhex from the first hexagon
        self._hex_coord_system = hexagons[0].hex_coord_system 
        self._radius = hexagons[0].radius 
        self._top = hexagons[0].top 
        self._angle_orientation = hexagons[0].angle_orientation
        for i, hexagon in enumerate(hexagons):
            # Add the hexagon to the list of polyhexes
            self.append_hex(hexagon)

    def _create_from_iterable(
            self, hexagons :List[Hexagon] | Dict[str, Hexagon]
            ):
        # 1) We check that the Hexagon list is consistent
        assert self._check_iterable_consistency(hexagons)
        if isinstance (hexagons, List):
            self._create_from_list(hexagons)
        elif isinstance(hexagons, Dict):
            raise NotImplementedError
        else:
            raise ValueError

    @property
    def angle_orientation(self):
        return self._angle_orientation
    
    @property
    def hex_coord_system(self):
        return self._hex_coord_system

    @property
    def radius(self):
        return self._radius
    
    @property
    def top(self):
        return self._top
    
    def __len__(self):
        return len(self.hexagons)
    
    @hex_coord_system_dependent
    def __str__(self):
        return_str = ""
        return_str += f"Coordinates System: {self.hex_coord_system} \n"
        return_str += f"Radius: {self.radius} \n"
        return_str += f"Top-orientation: {self.top} \n"
        return_str += f"Angle Orientation: {self.angle_orientation} \n"
        return_str += f"N Hexagons: {len(self)} \n"
        return_str += f"Hexagons: \n"
        max_cord_length = 9
        max_slot_length = len("bear_hawk_salmon")
        for coord, hex in self.hexagons.items():
            extra_space_coord =(max_cord_length - len(str(coord))) * ' '
            extra_space_slot =(max_slot_length - len(str(hex.centre_node.feature))) * ' '
            f = 'Free    ' if hex.free else 'Occupied'
            return_str += f"Coordinates : {coord} {extra_space_coord}| Slot {hex.centre_node.feature} {extra_space_slot} | {f} | {hex.token} \n"
        return return_str
    
    def placeholder_hex(self, **kwargs):
        return Hexagon(
                    hex_coord_system=self.hex_coord_system,
                    hex_centre_coord=kwargs.pop('hex_centre_coord', (0,0)),
                    outer_radius = self.radius,
                    top = self.top,
                    node_feature=kwargs.pop('node_feature', None),
                    vertex_feature=[None],
                    edge_feature=kwargs.pop('edge_feature', [None]),
                    angle_orientation=self.angle_orientation
            )
    
    def _update_border_connectivity(self, new_keys:List[Tuple[str]]):
        # Once that is done, we can create the connectivity of each edge 
        # First, from the existing keys to the nex ones
        for key_0 in self.border_edges_connectivity:
            e_0, enc_0, inner_hex_0, border_hex_0 = self.polyhex_border[key_0]
            for key_1 in new_keys:
                e_1, enc_1, inner_hex_1, border_hex_1 = self.polyhex_border[key_1]
                self.border_edges_connectivity[key_0][key_1] = self.encode_edge_connectivity(
                        inner_hex_0, inner_hex_1,
                        border_hex_0, border_hex_1
                    )

        # Then, from the new keys to the existing ones
        for key_0 in new_keys:
            e_0, enc_0, inner_hex_0, border_hex_0 = self.polyhex_border[key_0]
            # As we are sure that the key was never seen, we can safely allocate a new dict for it 
            self.border_edges_connectivity[key_0] = {}
            for key_1, (e_1, enc_1, inner_hex_1, border_hex_1) in self.polyhex_border.items():
                if key_0 != key_1:
                    self.border_edges_connectivity[key_0][key_1] = self.encode_edge_connectivity(
                        inner_hex_0, inner_hex_1,
                        border_hex_0, border_hex_1
                    )

    def _update_border(self, hexagon:Hexagon):
        # We record the keys already in the border (locally)
        new_keys = []
        for edge in hexagon.edges.values():
            edge:Edge            
            # If, when appending a new hex, one of its edges is in the border (this should always be the case except for the first hex), we remove it from the border.
            # We use the edges' spatial key rather than the entire key. This is useful to distinguish the polyhexes' border from the areas within the polyhex.
            if edge.spatial_key in self.polyhex_border:
                self.polyhex_border.pop(edge.spatial_key)
                #### We now remove it from the hex connectivity.
                # First, from the dict linking the edge to the others
                self.border_edges_connectivity.pop(edge.spatial_key)
                # Then, we remove it from the other dicts
                for edge_connect in self.border_edges_connectivity.values():
                    edge_connect.pop(edge.spatial_key)
            else:
                # The "outer border hex" is a placeholder hexagon. That is helpful when drawing, for instance, or recording the current edge's feature
                border_hex = self.placeholder_hex(
                    hex_centre_coord = hexagon.get_edge_adjency(edge.index),
                    edge_feature     = [edge.feature]
                )
                # Register the border edge
                self.polyhex_border[edge.spatial_key] = (
                    edge, self.encode_edge(edge, hexagon, border_hex),
                    hexagon, border_hex
                    )
                new_keys.append(edge.spatial_key)

        self._update_border_connectivity(new_keys)
        

    def append_edge(self, hex_coord:Tuple[int], adjency:Tuple[int], edge:Edge):
        feature = edge.feature
        # Create the DisjointSet if the feature has not been seen
        if feature not in self.hexes_in_area:
            self.hexes_in_area[feature] = DisjointSet()
    
        if edge.key in self.edges:  
            self.hexes_in_area[feature].add(hex_coord)
            self.hexes_in_area[feature].merge(adjency, hex_coord)
        
        else:         
            self.edges[edge.key] = edge
            self.hexes_in_area[feature].add(hex_coord)
    
    @hex_coord_system_dependent
    def append_hex(self, hexagon:Hexagon):
        coord = hexagon.hex_coord
        assert coord not in self.hexagons, f"The polyhex already contains an hexagon at coord {coord}"
        # Append the hex to the hexagons
        self.hexagons[coord] = hexagon
        for (adjency, edge) in zip(hexagon.adjency, hexagon.edges.values()):
            # Append each Edge
            self.append_edge(coord, adjency, edge)
            
        # Update the border of the polyhex
        self._update_border(hexagon)
        
    def add_token(self, coord:tuple, token:tuple):
        self.hexagons[coord].add_token(token)       

    def compute_habitat_result(self, verbose=False):
        total = 0 
        for habitat, dsu in self.hexes_in_area.items():
            result = max([len(subset) for subset in dsu.subsets()])
            total += result
            if verbose:
                print(f'The habitat {habitat} yields {result} points')
        if verbose:
            print(f'For a total of {total} points')
        return total     

    def draw(self, 
        scale = False,
        save_path = './image.jpg',
        buffer = False
        ):
        fig = plt.figure()
        axes = fig.gca()
        axes.axis('off')
        for hex in self.hexagons.values():
            axes = hex.draw(axes, scale=scale)
        # Draw border
        for edge, _, _, outer_border in self.polyhex_border.values():
            axes = outer_border.centre_node.draw(
                axes, 
                colour='k', 
                marker='o',
                scale=scale
                )
            axes = edge.draw(axes, scale=scale, color = 'grey', linewidth=5, alpha=0.7, zorder=200)
            
        if buffer:
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        else:
            plt.savefig(save_path)
        plt.clf()
        plt.close(fig)

    @hex_coord_system_dependent
    def compute_distance(self, hex1:Hexagon, hex2:Hexagon):        
        return abs(hex1.q - hex2.q) + abs(hex1.r - hex2.r) 
    
    def encode_edge(self, edge: Edge, inner_hex: Hexagon, outer_hex: Hexagon):
        q = (outer_hex.q - inner_hex.q) /2
        r = (outer_hex.r - inner_hex.r) /2
        return [q, r] + edge.encoding
    
    def encode_edge_connectivity(
            self, 
            inner_hex1  : Hexagon, inner_hex2  : Hexagon,
            border_hex1 : Hexagon, border_hex2 : Hexagon, 
            ):
        distance = 1 / (1+ self.compute_distance(border_hex1, border_hex2))
        # Bogus indexing, they all have the same feature by default
        feature1 = border_hex1.edges[0].feature
        feature2 = border_hex2.edges[0].feature
        feature_indicator = 1 if feature1 == feature2 else 0
        area_indicator    = 0
        if feature_indicator == 1:
            if self.hexes_in_area[feature1].connected(inner_hex1.hex_coord, inner_hex2.hex_coord):
                area_indicator +=1
        return [distance, feature_indicator, area_indicator]
    
    def index_to_edge_key(self, index):
        for start_index, start_key in enumerate(self.polyhex_border):
            if start_index == index:
                return start_key
            
    def edge_key_to_index(self, edge_key):
        for index, key in enumerate(self.polyhex_border):
            if key == edge_key:
                return index
    
    def get_graph_edges(self):
        # index_to_edge mapping
        starts = []
        ends   = []
        edge_attrs = []
        for start_index, start_key in enumerate(self.polyhex_border):
            for end_index, end_key in enumerate(self.polyhex_border):
                if start_index != end_index:
                    starts.append(start_index)
                    ends.append(end_index)
                    edge_attrs.append(self.border_edges_connectivity[start_key][end_key])
        return [starts, ends], edge_attrs
    
    def get_graph_nodes(self):
        nodes = []
        for (_, encoding, _, _) in self.polyhex_border.values():
            nodes.append(encoding)
        return nodes
    