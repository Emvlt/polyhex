"""Module for the Polyhexes."""

# pylint: disable=line-too-long

from typing import List, Dict
from dataclasses import dataclass, field
import numpy as np
import matplotlib.pyplot as plt

from polyhex.assets import loaders
from polyhex.objects.decorators import hex_coord_system_dependent
from polyhex.objects.hexagons import Hexagon

__all__ = ("Polyhex",)


@dataclass
class Polyhex:
    """Polyhex Class.

    From a software engineering perspective, a Polyhex is an Orchestrator.
    It provides convenience functions to: <br>
        -> create a polyhex <br>
        -> display/draw a polyhex <br>
        -> orchestrate the recording of the graphs for later export <br>
    """
    hex_coord_system: str = "axial"
    top: str = "pointy"
    radius: int | float = 1
    vertex_orientation: str = "clockwise"
    assets: Dict = field(
        default_factory=lambda: loaders.load_assets("default_assets.json")
    )

    def __post_init__(
        self,
    ):
        self.random_generator = np.random.default_rng()

    def _check_iterable_consistency(self, hexagons: List[Hexagon]):
        if len(hexagons) == 1:
            return True
        first_hex = hexagons[0]
        return all(
            first_hex.is_compatible(other_hex) for other_hex in hexagons[1:]
        ) and len(hexagons) == len(set(hexagons))

    def _create_from_list(self, hexagons: List[Hexagon], hypergraph):
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
    def create_from_iterable(cls, hexagons: List[Hexagon], hypergraph):
        """Class method to create a polyhex from a number of hexagons

        Args:
            n_hexagons (List): List of hexagons to put in the polyhex
            hypergraph (Dict): Graphs to be recorded. 

        Raises:
            NotImplementedError: A NotImplementedError is raised when the ``hexagons`` argument is not a list.

        Returns:
            polyhex: Polyhex
        """
        polyhex = cls()
        # 1) We check that the Hexagon list is consistent
        if isinstance(hexagons, List):
            assert polyhex._check_iterable_consistency(hexagons), 'The hexagons are not consistent with each other.'
            polyhex._create_from_list(hexagons, hypergraph)
        else:
            raise NotImplementedError(f'Expected a list of hexagons, got {type(hexagons)}')
        return polyhex

    @classmethod
    def create_from_number(cls, n_hexagons: int, hypergraph: Dict):
        """Class method to create a polyhex from a number of hexagons

        Args:
            n_hexagons (int): number of hexagons in the polyhex
            hypergraph (Dict): Graphs to be recorded. It requires the HexagonBorderGraph to be recorded.

        Raises:
            ValueError: A valueError is raised when the hypergraph does not have a ``HexagonBorderGraph`` key

        Returns:
            polyhex: Polyhex
        """
        if not "HexagonBorderGraph" in hypergraph:
            raise ValueError("To use the ``create_from_number`` method, it is necessary to record a HexagonBorderGraph, but none were not found")
        polyhex = cls()
        assert isinstance(n_hexagons, int)
        polyhex._create_from_list([Hexagon()], hypergraph)
        for _ in range(n_hexagons - 1):
            hexagon = polyhex.random_generator.choice(
                list(hypergraph["HexagonBorderGraph"].nodes.values())
            )
            polyhex.append_hex(hexagon, hypergraph)
        return polyhex

    @classmethod
    def create_spiral(cls, radius: int, hypergraph: Dict):
        """Class method to create a polyhex tiling with a spiral shape.
        (Think of CATAN's board)

        Args:
            radius (int): Radius of the spiral tiling
            hypergraph (Dict): Graphs to be recorded. It requires the HexagonBorderGraph to be recorded.

        Raises:
            ValueError: A valueError is raised when the hypergraph does not have a ``HexagonBorderGraph`` key

        Returns:
            polyhex: Polyhex
        """
        if not "HexagonBorderGraph" in hypergraph:
            raise ValueError("To use the ``create_spiral`` method, it is necessary to record a HexagonBorderGraph, but none were not found")
        polyhex = cls()
        assert isinstance(radius, int)
        polyhex._create_from_list([Hexagon()], hypergraph)
        for _ in range(1, radius + 1):
            # We create a list out of the border because a simple reference to it points to the actual border, which would be changed during the process of appending tiles, which is not good.
            border = list(hypergraph["HexagonBorderGraph"].nodes.values())
            for hexagon in border:
                polyhex.append_hex(hexagon, hypergraph)
        return polyhex

    @classmethod
    def create_tiling(cls, n: int, m: int, name: str, hypergraph: Dict, **kwargs):
        """Class method to create a polyhex tiling of size n*m

        Args:
            n (int): Number of rows
            m (int): Number of columns
            name (str): Name of the tiling
            hypergraph (Dict): Graphs to be recorded

        Raises:
            ValueError: A valueError is raised when the offset ``kwarg`` is not `even-r` or `odd-r`. See Offset Coordinates in https://www.redblobgames.com/grids/hexagons/
            NotImplementedError: The tiling can only be rectangular or tilted. 

        Returns:
            polyhex: Polyhex tiling (hextille) (see https://en.wikipedia.org/wiki/Hexagonal_tiling)
        """
        coordinates = []
        if name == "rectangular":
            offset = kwargs.pop("offset", "odd-r")
            for r in range(m):
                if offset == "even-r":
                    offset_val = -(r // 2 + r % 2)
                elif offset == "odd-r":
                    offset_val = -(r // 2)
                else:
                    raise ValueError(
                        f"The offset can only be `even-r` or `odd-r`, got {offset}"
                    )
                for q in range(n):
                    coordinates.append((q + offset_val, r))

        elif name == "tilted":
            for i in range(1, n):
                for j in range(1, m):
                    coordinates.append((i, j))
        else:
            raise NotImplementedError(
                f"The tiling can only be `rectangular` or `tilted`, not {name}."
            )

        polyhex = cls()
        polyhex._create_from_list(
            [Hexagon(hex_coord=c) for c in coordinates], hypergraph
        )

        return polyhex

    @hex_coord_system_dependent
    def __str__(self):
        return_str = ""
        return_str += f"Coordinates System: {self.hex_coord_system} \n"
        return_str += f"Radius: {self.radius} \n"
        return_str += f"Top-orientation: {self.top} \n"
        return_str += f"Vertex Orientation: {self.vertex_orientation} \n"
        return_str += f"N Hexagons: {len(self)} \n"
        return return_str

    def placeholder_hex(self, **kwargs):
        """The placeholder hexagon is a convenience function used to create a hexagon with attributes similar to the ones already found in the Polyhex. It is used to create the HexagonBorderGraph.

        Returns:
            Hexagon: a placeholder hexagon
        """
        return Hexagon(
            hex_coord_system=self.hex_coord_system,
            hex_coord=kwargs.pop("hex_coord", (0, 0)),
            top=self.top,
            radius=self.radius,
            vertex_orientation=self.vertex_orientation,
            assets=self.assets,
            hexagon_feature=kwargs.pop("hexagon_feature", "placeholder"),
            vertex_feature=kwargs.pop("vertex_feature", "placeholder"),
            edge_feature=kwargs.pop("edge_feature", ("placeholder")),
        )

    def append_hex(self, hexagon: Hexagon, hypergraph: Dict):
        """Method to append a hexagon to a polyhex. 

        The Polyhex being an Orchestrator, it is its role to read the graph to record, make sure that all graphs are recorded using the right ``graph.append()`` calls.

        Args:
            hexagon (Hexagon): The hexagon to append to the polyhex
            hypergraph (Dict): The dict of graphs

        Returns:
            dict: updated graph
        """
        for name, graph in hypergraph.items():
            if name == "HexagonBorderGraph":
                assert "HexagonGraph" in hypergraph
                graph.append(hexagon, hypergraph["HexagonGraph"], self)
            else:
                graph.append(hexagon)
        return graph

    def render(self, axes, hypergraph:Dict):
        """The method to render a polyhex using a hypergraph. 

        Note:
            It is a bit of an abuse to put it as a ``polyhex`` method, but it fits the polyhex Orchestrator role

        Args:            
            axes (matplotlib.axis): axis on which to render the figure
            hypergraph (Dict): dict of recorded graphs 
        """
        if "HexagonGraph" in hypergraph:
            for hexagon in hypergraph["HexagonGraph"].nodes.values():
                axes = hexagon.render(axes)

        if "HexagonBorderGraph" in hypergraph:
            for hexagon in hypergraph["HexagonBorderGraph"].nodes.values():
                axes = hexagon.centre.render(axes)

        if "EdgeBorderGraph" in hypergraph:
            for edge in hypergraph["EdgeBorderGraph"].nodes.values():
                axes = edge.render_line(axes, color="black", linewidth="3")

        return axes

    def draw(self, hypergraph :Dict, save_path="./image.png", buffer=False):
        """The method to draw a polyhex using a hypergraph. 

        Note:
            It is a bit of an abuse to put it as a ``polyhex`` method, but it fits the polyhex Orchestrator role

        Args:
            hypergraph (Dict): dict of recorded graphs 
            save_path (str, optional): Where to save the drawn image. Defaults to "./image.png".
            buffer (bool, optional): Useful for pygame dynamic rendering. Defaults to False.
        """
        fig = plt.figure()
        axes = fig.gca()
        axes.axis("off")

        axes = self.render(axes, hypergraph)

        if buffer:
            plt.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
        else:
            plt.savefig(save_path)
            plt.clf()
            plt.close(fig)
