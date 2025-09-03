from typing import List, Dict, Tuple
from dataclasses import dataclass, field
import numpy as np
import matplotlib.pyplot as plt 

from polyhex.assets import loaders
from polyhex.objects.decorators import hex_coord_system_dependent
from polyhex.objects.hexagons import Hexagon

__all__ = ('Polyhex',)

@dataclass
class Polyhex(object):
    hex_coord_system : str = 'axial'
    top : str = 'pointy'
    radius : int | float = 1 
    vertex_orientation : str = 'clockwise'
    assets : Dict = field(default_factory=lambda: loaders.load_assets('default_assets.json'))
    def __post_init__(
        self,
        ):
        # self.hexes_in_area = {}
        self.random_generator = np.random.default_rng()
        
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

    def _create_from_list(self, hexagons:List[Hexagon], hypergraph):
        # Extract the properties of the polyhex from the first hexagon
        self.hex_coord_system = hexagons[0].hex_coord_system 
        self.radius = hexagons[0].radius 
        self.top = hexagons[0].top 
        self.vertex_orientation = hexagons[0].vertex_orientation
        self.assets = hexagons[0].assets
        for hexagon in hexagons:
            # Add the hexagon to the list of polyhexes
            self.append_hex(hexagon, hypergraph)

    @classmethod
    def create_from_iterable(
        cls, hexagons :List[Hexagon], hypergraph
        ):
        polyhex = cls()
        # 1) We check that the Hexagon list is consistent
        assert polyhex._check_iterable_consistency(hexagons)
        if isinstance (hexagons, List):
            polyhex._create_from_list(hexagons, hypergraph)
        else:
            raise NotImplementedError
        return polyhex
        
    @classmethod
    def create_from_number(cls, n_hexagons:int, hypergraph:Dict):
        assert 'HexagonBorderGraph' in hypergraph
        polyhex = cls()
        assert isinstance(n_hexagons, int)
        polyhex._create_from_list([Hexagon()], hypergraph)
        for i in range(n_hexagons-1):
            hex = polyhex.random_generator.choice(
                list(hypergraph['HexagonBorderGraph'].nodes.values())
                )
            polyhex.append_hex(
                hex, 
                hypergraph
                )
        return polyhex
    
    @classmethod
    def create_spiral(cls, radius:int, hypergraph:Dict):
        assert 'HexagonBorderGraph' in hypergraph
        polyhex = cls()
        assert isinstance(radius, int)
        polyhex._create_from_list([Hexagon()], hypergraph)
        for i in range(1,radius+1):
            # We create a list out of the border because a simple reference to it points to the actual border, which would be changed during the process of appending tiles, which is not good.
            border=list(
                hypergraph['HexagonBorderGraph'].nodes.values()
                )            
            for hex in border: 
                polyhex.append_hex(
                    hex, 
                    hypergraph
                    )
        return polyhex
    
    @classmethod
    def create_tiling(cls, n:int, m:int, name:str, hypergraph:Dict, **kwargs):
        coordinates = []
        if name == 'rectangular':
            offset = kwargs.pop('offset', 'odd-r')
            for r in range(m):
                if offset == 'even-r':
                    offset_val = -(r//2 + r %2)
                elif offset == 'odd-r':
                    offset_val = -(r//2)
                else:
                    raise ValueError(f'The offset can only be `even-r` or `odd-r`, got {offset}')
                for q in range(n):
                    coordinates.append((q+offset_val, r))
            
        elif name == 'tilted':
            for i in range(1,n):
                for j in range(1,m):
                    coordinates.append((i,j))
        else:
            raise NotImplementedError(f'The tiling can only be `rectangular` or `tilted`, not {name}.')

        polyhex = cls()
        print(coordinates)
        polyhex._create_from_list([Hexagon(hex_coord=c) for c in coordinates], hypergraph)
        
        return polyhex
    
    def __len__(self):
        return len(self.hexagons)
    
    @hex_coord_system_dependent
    def __str__(self):
        return_str = ""
        return_str += f"Coordinates System: {self.hex_coord_system} \n"
        return_str += f"Radius: {self.radius} \n"
        return_str += f"Top-orientation: {self.top} \n"
        return_str += f"Vertex Orientation: {self.vertex_orientation} \n"
        return_str += f"N Hexagons: {len(self)} \n"
        return_str += f"Hexagons: \n"
        return return_str
    
    def placeholder_hex(self, **kwargs):
        return Hexagon(
                    hex_coord_system=self.hex_coord_system,
                    hex_coord=kwargs.pop('hex_coord', (0,0)),
                    top = self.top,
                    radius = self.radius,                    
                    vertex_orientation=self.vertex_orientation,
                    assets = self.assets,
                    hexagon_feature=kwargs.pop('hexagon_feature', "placeholder"),
                    vertex_feature=kwargs.pop('vertex_feature', "placeholder"),
                    edge_feature=kwargs.pop('edge_feature', ("placeholder")),
                    
            )

    def append_hex(self, hexagon:Hexagon, hypergraph:Dict):
        for name, graph in hypergraph.items():
            if name == 'HexagonBorderGraph':
                assert 'HexagonGraph' in hypergraph
                graph.append(hexagon, hypergraph['HexagonGraph'], self)
            else:
                graph.append(hexagon)
        return graph

    def render(self, axes, hypergraph):
        if 'HexagonGraph' in hypergraph:
            for hex in hypergraph['HexagonGraph'].nodes.values():
                axes = hex.render(axes)

        if 'HexagonBorderGraph' in hypergraph:
            for hex in hypergraph['HexagonBorderGraph'].nodes.values():
                axes = hex.centre.render(axes)

        if 'EdgeBorderGraph' in hypergraph:
            for edge in hypergraph['EdgeBorderGraph'].nodes.values():
                axes = edge.render_line(axes, color='black', linewidth='3')

        return axes

    def draw(self, 
        hypergraph,
        save_path = './image.png',
        buffer = False
        ):
        fig = plt.figure()
        axes = fig.gca()
        axes.axis('off')
        
        axes = self.render(axes, hypergraph)
            
        if buffer:
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        else:
            plt.savefig(save_path)
            plt.clf()
            plt.close(fig)
    