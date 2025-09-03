"""Module for the Hexagons."""

# pylint: disable=line-too-long
# pylint: disable=attribute-defined-outside-init
# pylint: disable=import-outside-toplevel
# pylint: disable=too-many-instance-attributes
# pylint: disable=inconsistent-return-statements

from typing import List, Dict, Tuple
import math
from dataclasses import dataclass, field

from numpy.typing import ArrayLike
import matplotlib.pyplot as plt
from scipy.spatial import distance

from polyhex.assets import loaders
from polyhex.utilities import replicate_vector
from polyhex.objects.decorators import (
    hex_coord_system_dependent,
    top_dependent,
    vertex_orientation_dependent,
)

__all__ = ("Hexagon",)

# Pointy top, axial ordering blablabla
ADJENCY_TO_ROTATIONS_FUNCTIONS = {
    # Edge index : N rotations of the neighbour hexagon to math edges.
    # Example: consider a hexagon at (q,r) with a pointy top and clockwise vertex ordering and its first neighbour, at position (q+1, r-1). In order to match the first edge of (q,r) to the first edge of (q+1, r-1), the latter has to be rotated 3 times
    0: [3, 2, 1, 0, 5, 4],
    1: [4, 3, 2, 1, 0, 5],
    2: [5, 4, 3, 2, 1, 0],
    3: [0, 5, 4, 3, 2, 1],
    4: [1, 0, 5, 4, 3, 2],
    5: [2, 1, 0, 5, 4, 3],
}


@dataclass
class Hexagon:
    """Base class for creating a Hexagon.
    See https://www.redblobgames.com/grids/hexagons/ for a great explanation

    Arguments:
        hex_coord_system (str) : The hexagonal coordinate system. It can be `offset`, `cube`, `axial` or `doubled`Defaults to `axial`.
        hex_coord (List[int])  : The coordinates of the Hexagon in the given hexagonal coordinate system. Defaults to the centre coordinate `[0,0]`.
        top (str) : The top of the hexagon. Can only be `pointy` of `flat`. Defaults to `pointy`.
        radius (int|float) : The radius' value. For PolyHex, the `radius` refers to the radius of the circle to which all the hexagon's vertices belong.Defaults to `1`.
        vertex_orientation (str) : The vertex orientation. It is can be `clockwise` or `couterclockwise`. Important note: For hexagons with `pointy` top, We start counting the vertices by starting with the one at 12.00. For hexagons with `flat` top, We start counting the vertices by starting with the one at 3.00 Defaults to `clockwise`.
        assets (Dict) : A big dictionnary holding all the information about rendering, token compatibility, etc, etc. Defaults to the defaults_assets.json file.
        hexagon_feature   (ArrayLike) : The feature of the hexagon as an entity. Defaults to 0.
        vertex_feature (ArrayLike) : The feature of the vertices Note: there is a bit of a misnomer here. There are 6 vertices per hexagon, so the attribute name should be 'vertices_feature' and an ArrayLike of size 6 should be the default. For ease of use, we deliberately offer to define all the vertices' feature by providing a single default argument, replicated accross all edges. However, if an ArrayLike is provided, the features will be allocated in the order defined by `vertex_orientation`. It also MUST be hashable by a `frozenset`. Defaults to 0.
        edge_feature   (ArrayLike) : The feature of the edges Note: there is a bit of a misnomer here. There are 6 edges per hexagon, so the attribute name should be 'edges_feature' and an ArrayLike of size 6 should be the default. For ease of use, we deliberately offer to define all the edges' feature by providing a single default argument, replicated accross all edges. However, if an ArrayLike is provided, the features will be allocated in the order defined by `vertex_orientation`. It also MUST be hashable by a `frozenset`. Defaults to 0.
    """

    hex_coord_system: str = "axial"
    hex_coord: Tuple[int] = (0, 0)
    top: str = "pointy"
    radius: int | float = 1
    vertex_orientation: str = "clockwise"
    assets: Dict = field(
        default_factory=lambda: loaders.load_assets("default_assets.json")
    )
    hexagon_feature: ArrayLike = "placeholder"
    vertex_feature: ArrayLike = "placeholder"
    edge_feature: ArrayLike = "placeholder"

    def __post_init__(self):
        # Attributes' sanity check
        self._check_attributes()
        # Computation of the useful dimensions of the hexagon, its width and height, based on its `top` and `radius`.
        self._compute_dimensions()
        # Get the centre coordinate on the cartesian grid
        self._hex_coord_to_cartesian()
        # Create centre node
        # Lazy imports to avoir Circular Import Error
        from polyhex.objects.nodes import HexagonCentre

        self.centre = HexagonCentre(self, self.hexagon_feature)
        # Create vertices
        self._create_vertices()
        # Create edges
        self._create_edges()
        # Allocate spatial_key, an alias of hex_coord for Hexagons
        self.spatial_key = self.hex_coord

    ######### Checking the variables passed to the class constructor #########
    ######### Called in the __post_init__ method #########
    def _check_attributes(self):
        self._check_hex_coord_system()
        self._check_hex_centre_coord()
        self._check_top()
        self._check_vertex_orientation()
        self._check_assets()

    def _check_vertex_orientation(self):
        assert self.vertex_orientation in [
            "clockwise",
            "counterclockwise",
        ], f"The angle orientation of an hexagon can only be 'clockwise' or 'counterclockwise', got { self.vertex_orientation}"

    def _check_hex_centre_coord(self):
        if self.hex_coord_system in ["offset", "axial", "doubled"]:
            assert len(self.hex_coord) == 2
            self.q = self.hex_coord[0]
            self.r = self.hex_coord[1]
        else:
            assert len(self.hex_coord) == 3
            self.q = self.hex_coord[0]
            self.r = self.hex_coord[1]
            self.s = self.hex_coord[2]

    @hex_coord_system_dependent
    def _check_hex_coord_system(self):
        pass

    @top_dependent
    def _check_top(self):
        pass

    def _check_assets(
        self,
    ):
        assert "render" in self.assets, "Please provide a `render` dict"
        assert "compatibility" in self.assets, "Please provide a `compatibility` dict"

    @top_dependent
    def _compute_dimensions(self):
        if self.top == "pointy":
            self.height = 2 * self.radius
            self.width = math.sqrt(3) * self.radius
            self.min_h = self.radius / 2
            self.min_w = self.width

    @hex_coord_system_dependent
    @top_dependent
    def _hex_coord_to_cartesian(self):
        if self.hex_coord_system == "axial" and self.top == "pointy":
            self.x = 2 * self.q + self.r
            self.y = -3 * self.r

    @top_dependent
    @vertex_orientation_dependent
    def _vertex_coord_factory(self):
        if self.top == "pointy" and self.vertex_orientation == "clockwise":
            return [
                (self.x, self.y + 2),
                (self.x + 1, self.y + 1),
                (self.x + 1, self.y - 1),
                (self.x, self.y - 2),
                (self.x - 1, self.y - 1),
                (self.x - 1, self.y + 1),
            ]

    @staticmethod
    def _parse_feature(feature):
        if isinstance(feature, (int, str, float, complex)):
            feature = [feature for _ in range(6)]
        elif isinstance(feature, (tuple, List)):
            if len(feature) == 1:
                feature = replicate_vector(feature, 6)
            elif len(feature) == 6:
                pass
            else:
                raise ValueError(
                    f"Length of feature can only be 1 or 6, got {len(feature)}"
                )
        else:
            raise NotImplementedError(
                f"Currently, only int, str, float, complex, tuple and list objects are supported, got {type(feature)}"
            )
        return feature

    def _create_vertices(self):
        # Lazy import
        from polyhex.objects.nodes import HexagonVertex

        vertex_features = self._parse_feature(self.vertex_feature)
        self.vertices_list = []
        self.vertices_dict = {}
        for index, feature in enumerate(vertex_features):
            vertex = HexagonVertex(self, index, feature)
            self.vertices_dict[vertex.spatial_key] = vertex
            self.vertices_list.append(vertex)

    def _create_edges(self):
        edge_features = self._parse_feature(self.edge_feature)
        self.edges_list = []
        self.edges_dict = {}
        self.edges_to_rotations = {}
        from polyhex.objects.edges import HexagonEdge

        for index, feature in enumerate(edge_features):
            edge = HexagonEdge(
                self,
                self.vertices_list[index],
                self.vertices_list[(index + 1) % 6],
                index,
                feature,
            )
            self.edges_dict[edge.spatial_key] = edge
            self.edges_list.append(edge)
            self.edges_to_rotations[edge.spatial_key] = ADJENCY_TO_ROTATIONS_FUNCTIONS[
                index
            ]

    ######### Properties #########
    @property
    def adjency(self) -> List[Tuple[int]]:
        """Get a hexagon adjency, i.e the coordinates of neighbouring hexagons.

        Raises:
            NotImplementedError: is only implemented for the `axial` coordinates system.
            NotImplementedError: is only implemented for the `clockwise` vertex ordering.

        Returns:
            List[Tuple[int]] : [(coord_hex_0), ..., (coord_hex_5)]
        """
        if self.hex_coord_system == "axial":
            if self.vertex_orientation == "clockwise":
                return [
                    (self.q + 1, self.r - 1),
                    (self.q + 1, self.r),
                    (self.q, self.r + 1),
                    (self.q - 1, self.r + 1),
                    (self.q - 1, self.r),
                    (self.q, self.r - 1),
                ]

            raise NotImplementedError(
                f"The `adjency` attribute is not implemented for {self.vertex_orientation}. Please use `clockwise` orientation instead."
            )

        raise NotImplementedError(
            f"The `adjency` attribute is not implemented for {self.hex_coord_system}. Please use `axial` coordinate system instead."
        )

    @property
    def encoding(self):
        """Returns the Hexagon's encoding.
        The default version returns the HexagonCentre's encoding

        Returns:
            List: vector representation of the Hexagon's attribute
        """
        return self.centre.encoding

    @property
    def token(self):
        """Returns the hexagon's token
        Under the hood, it returns the HexagonCentre's token

        Returns:
            List: vector representation of the Hexagon's attribute
        """
        return self.centre.token

    ######### Methods #########
    def add_token(self, new_token: str):
        """Method to add a token on a Hexagon.
        Under the hood, it adds the token to the HexagonCentre's

        Args:
            new_token (str): str identifier of the token.
        """
        self.centre.add_token(new_token)

    def is_compatible(self, other) -> bool:
        """Method to assess if the properties of a Hexagon are compatible with the properties of another.

        Args:
            other (Hexagon): Other Hexagon to compare it with

        Returns:
            bool: Boolean result of the compatibility assessment
        """
        return (
            isinstance(other, Hexagon)
            and self.hex_coord_system == other.hex_coord_system
            and self.radius == other.radius
            and self.top == other.top
            and self.vertex_orientation == other.vertex_orientation
        )

    @top_dependent
    @vertex_orientation_dependent
    def get_vertex_adjency(self, vertex):
        """Method to get the vertex adjency, i.e the neighbouring vertices, in and outside of the ``Hexagon``

        Args:
            vertex (HexagonVertex): vertex to get the adjency of.

        Returns:
            List[Tuple[int]]: length-3 size adjency coordinates
        """
        if self.vertex_orientation == "clockwise" and self.top == "pointy":
            x, y = (
                self.vertices_list[vertex.index].x,
                self.vertices_list[vertex.index].y,
            )
            if vertex.index % 2 == 0:
                adj = [(x, y + 2), (x + 1, y - 1), (x - 1, y - 1)]
            else:
                adj = [(x + 1, y + 1), (x, y - 2), (x - 1, y + 1)]
        assert len(adj) == 3
        return adj

    def get_edge_adjency(self, edge):
        """Method to get the edge adjency, i.e the neighbouring edges, in and outside of the ``Hexagon``

        Args:
            vertex (HexagonEdge): edge to get the adjency of.

        Returns:
            List[Tuple[int]]: length-4 size adjency coordinates
        """
        # 1 We get the edge's index and define the adjency list
        edge = self.edges_list[edge.index]
        adj = []
        # We iterate on the
        for root in [edge.start, edge.end]:
            adjency = self.get_vertex_adjency(root)
            for coord in adjency:
                candidate_key = frozenset((root.spatial_key, coord))
                if candidate_key != edge.spatial_key:
                    adj.append(candidate_key)
        assert len(adj) == 4
        return adj

    def render(self, axes):
        """Method to render a hexagon.

        Unlike ``draw``, it requires a matplotlib axis object.

        """
        axes = self.centre.render(axes)
        for edge in self.edges_list:
            axes = edge.render(axes)
        return axes

    def draw(self, buffer_object):
        """Method to draw a hexagon.

        Creates a matplotlib.axis and calls ``render`` on it.

        Args:
            buffer_object: savepath or buffer for image saving
        """
        fig = plt.figure()
        axes = fig.gca()
        axes.axis("off")
        axes = self.render(axes)
        plt.savefig(buffer_object, format="png", dpi=150, bbox_inches="tight")
        plt.clf()
        plt.close(fig)

    def distance(self, other, kwd="euclidian"):
        """Method to compute the distance between two ``Hexagon``

        Args:
            other (_type_): other ``Hexagon``
            kwd (str, optional): Identifier of the distance. Defaults to "euclidian".

        Raises:
            NotImplementedError: This method is currently only implemented for the `euclidian` distance.

        Returns:
            np.ndarray: float distance value
        """
        assert isinstance(other, Hexagon)
        if kwd == "euclidian":
            return distance.euclidean(self.spatial_key, other.spatial_key)
        raise NotImplementedError(
            f"The distance method is only implemented for the `euclidian` distance. Got {kwd}"
        )

    ######### Dunder methods #########
    def __str__(self):
        return f"{self.hex_coord} \n"

    def __eq__(self, other):
        return self.is_compatible(other) and self.centre == other.centre

    def __hash__(self):
        return hash((type(self), self.centre))
