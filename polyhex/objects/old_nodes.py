from typing import List, Dict, Tuple
import math 

from matplotlib.patches import Ellipse

from numpy.typing import ArrayLike

__all__ = ('Node',)

class Node(object):
    def __init__(
            self,          
            config_file:Dict ,
            feature : ArrayLike = None,
            **kwargs
        ):
        # Hex Coordinate System
        self.hex_coord_system = kwargs.pop('hex_coord_system', None)
        self.hex_coord = kwargs.pop('hex_coord', None)
        # Cartesian Coordinate
        self.cartesian_coord_vector = kwargs.pop('cartesian_coord_vector', None)
        self._cartesian_coord = None
        assert self.hex_coord is not None or self.cartesian_coord_vector is not None, 'A Node must have coordinates in the cartesian or the hexagonal grid'
        # Feature Vector
        self.config_file = config_file
        self.feature = feature
        if feature is not None:
            self.encoding = config_file['encodings']['slots'][feature]
        else:
            self.encoding = None
        # Neighbours
        self.tag = config_file['palette']['node_colour'] + config_file['palette']['node_marker']
        # Occupation
        self.free = True
        self.token = False

    def _hex_coord_str(self):
        if self.hex_coord_system is None:
            return ''
        else:
            if self.hex_coord_system == 'axial':
                return (f'q={self.hex_coord[0]}, r={self.hex_coord[1]}')
            else:
                raise NotImplementedError
            
    def __eq__(self, other):
        raise NotImplementedError(f'The equality method is not implemented for Nodes.')
            
    def equal(self, other, coordinates:str):
        assert coordinates in ['cartesian_coord', 'hex_coord']
        c_self  = getattr(self, coordinates)
        c_other = getattr(other, coordinates)
        cond = (isinstance(other, Node) and c_self == c_other)
        if coordinates == 'cartesian_coord':
            return cond.all()
        else:
            return cond

    def __str__(self):
        return_str = ''
        if self.hex_coord_system is not None:
            return_str += f'Hex Coordinates System : {self.hex_coord_system} \n'
        if self.hex_coord is not None:
            return_str += f'Hex Coordinates Vector : ({self._hex_coord_str()}) \n'
        if self.cartesian_coord_vector is not None:
            return_str += f'Cartesian Coordinates Vector : {self.cartesian_coord_vector} \n'
            return_str += f'Feature Vector : {self.feature} \n'

        return return_str

    @property
    def cartesian_coord(self):
        return self._cartesian_coord
     
    @cartesian_coord.setter
    def cartesian_coord(self, coords: List):
        self._cartesian_coord = coords

    def draw(self, axes, scale=False, **kwargs):
        if scale: 
            c0,c1 = self._cartesian_coord[0], self._cartesian_coord[1]
        else:
            c0,c1 = self.cartesian_coord_vector[0], self.cartesian_coord_vector[1]
        if self.free:
            colour = kwargs.pop('colour', None)
            marker = kwargs.pop('marker', None)
            if colour is not None and marker is not None:
                tag = colour+marker
            elif colour is not None and marker is None:
                tag = colour
            elif colour is None and marker is not None:
                tag = marker
            else:
                tag = self.tag
            axes.plot(c0, c1, tag)
        else:
            circle_color = self.config_file['palette']['wildlife'][self.token]
            circle = Ellipse((c0, c1), width=1*0.6, height=math.sqrt(3)*0.6, facecolor=circle_color, edgecolor = 'w', zorder=10)
            axes.add_patch(circle)
        
        return axes
    
    def __hash__(self):
        return hash((
                type(self), 
                self.hex_coord_system, 
                self.hex_coord[0], 
                self.hex_coord[1], 
                self.cartesian_coord_vector[0], 
                self.cartesian_coord_vector[1]))
    
# class HexagonCentre(Node):
#     def __init__(
#             self, 
#             hex_coordinate_system : str,
#             hex_coordinates : Tuple[int],
#             cartesian_coordinates : Tuple[int],
#             config_file, 
#             slot : str = None, **kwargs):
        
#         # Key to identify the HexagonCentre. 
#         # As Hexagons cannot overlap or share centres, using the hex coordinates is enough 
#         self.spatial_key = frozenset(hex_coordinates)

#         super().__init__(config_file, feature, **kwargs)

#     #### Methods ####

#     #### Dunder methods ####
#     def __eq__(self, other):
#         return (
#             isinstance(other, HexagonCentre) and 
#             self.spatial_key == other.spatial_key
#             )
    
#     def __hash__(self):
#         return hash((type(self), self.spatial_key))

#     def __repr__(self):
#         return f"HexagonCentre(x={self.x}, y={self.y})"
    
#     def __str__(self):
#         return super().__str__()
    
    

# class HexagonVertex(Node):
#     def __init__(self, config_file, feature = None, **kwargs):
#         super().__init__(config_file, feature, **kwargs)