"""Base module for the nodes of a polyhex"""
from abc import ABC
from dataclasses import dataclass
from typing import Tuple
from math import sqrt

from numpy.typing import ArrayLike
from scipy.spatial import distance
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from matplotlib.artist import Artist

from polyhex.objects.hexagons import Hexagon
from polyhex.objects.decorators import top_dependent

__all__ = ('HexagonCentre', 'HexagonVertex')

@dataclass
class Node(ABC):
    """Node Abstract class.
    The HexagonCentre and HexagonVertex inherit from it.

    Args:
        hexagon (Hexagon): The Hexagon to which the nodes belonrg.
        feature (ArrayLike): The feature identifies what can be placed on the node or what it is compatible with. Defaults to 0.
        free (bool): Identifies if there is something on the node. Defaults to False.
        token (ArrayLike): Identifies what is on the node. Defaults to None
    """
    # pylint: disable=too-many-instance-attributes
    hexagon: Hexagon
    feature: ArrayLike = "placeholder"

    def __post_init__(self):
        # Unpack useful hexagon attributes
        self.top = self.hexagon.top
        # Assets
        self.render_assets = self.hexagon.assets["render"][self.name]
        self.compat_assets = self.hexagon.assets["compatibility"][self.name]
        self.encoding_assets = self.hexagon.assets["encoding"][self.name]
        # Current token
        self.token = "placeholder"
        # Display coordinates on the cartesian grid
        if self.top == "pointy":
            self.display_coordinates = [
                self.x * (self.hexagon.radius * sqrt(3) / 2),
                self.y / (self.hexagon.radius * 2),
            ]
        else:
            raise NotImplementedError
        
    @property
    def encoding(self):
        return [
            self.encoding_assets['feature'][self.feature], 
            self.encoding_assets['token'][self.token]
            ]

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        self._x = x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        self._y = y

    def draw(self, save=True):
        """The draw function is a convenience function that wraps the `render` function. It is used for standalone drawing and generates a figure which is saved based on the save boolean argument

        Args:
            save (bool, optional): _description_. Defaults to True.
        """
        fig = plt.figure(figsize=(2, 2))
        axes = fig.gca()
        axes.axis("off")
        axes = self.render(axes)
        if save:
            plt.savefig(f"{self.name}", bbox_inches="tight")
            plt.clf()
            plt.close(fig)
        else:
            plt.show(axes)

    def _render(self, axes: Artist):
        raise NotImplementedError(
            "The _render() Method is not implemented for the  Node class."
        )

    def render(self, axes: Artist, **kwargs):
        if not kwargs:
            p = self.render_assets["feature"][f"{self.token}"]
            axes = self._render(axes, **p)
        else:
            axes = self._render(axes, **kwargs)
        return axes

    def add_token(self, new_token):
        assert (
            new_token in self.compat_assets[self.feature]
        ), f"The token {new_token} is not compatible with the slot {self.feature} for {self.name} nodes"
        self.token = new_token

class HexagonCentre(Node):
    def __init__(self, hexagon: Hexagon, feature: ArrayLike = "placeholder"):
        self.hex_coordinates = hexagon.hex_coord
        self.x, self.y = hexagon.x, hexagon.y
        self.name = "HexagonCentre"
        # Spatial key, used to uniquely identify the location of the hexagon's centre, coincides with the hexagon's spatial key
        self.spatial_key = hexagon.hex_coord

        super().__init__(hexagon, feature)

    #### Private Methods ####
    @top_dependent
    def _render(self, axes: Artist, **kwargs):
        scaling = 0.1
        if self.top == "pointy":
            circle = Ellipse(
                self.display_coordinates, width=scaling, height=scaling, **kwargs
            )
        axes.add_patch(circle)
        return axes

    #### Dunder methods ####
    def __eq__(self, other):
        return (
            isinstance(other, HexagonCentre)
            and self.hex_coordinates == other.hex_coordinates
        )

    def __repr__(self):
        return f"{self.name} : {self.spatial_key}"
    
    def __hash__(self):
        return hash((type(self), self.spatial_key))
    
    ### Public method ### 
    def distance(self, other, kwd='euclidian'):
        assert isinstance(other, HexagonCentre)
        if kwd == 'euclidian':
            return distance.euclidean(self.hex_coordinates, other.hex_coordinates)
        else:
            raise NotImplementedError 


class HexagonVertex(Node):
    def __init__(
        self,
        hexagon: Hexagon,
        cartesian_coordinates: Tuple[int] = (0, 0),
        index: int = 0,
        feature: str = "placeholder",
    ):
        self.x, self.y = cartesian_coordinates
        self.index = index
        self.name = "HexagonVertex"
        # Unlike the HexagonCentre, the spatial key of a HexagonVertex is its cartesian coordinates vector
        self.spatial_key = cartesian_coordinates
        self.feature_key = (cartesian_coordinates, feature)
        super().__init__(hexagon, feature)

    #### Private Methods ####
    @top_dependent
    def _render(self, axes: Artist, **kwargs):
        scaling = 0.2
        if self.top == "pointy":
            circle = Ellipse(
                self.display_coordinates, width=scaling, height=scaling, **kwargs
            )
        else:
            raise NotImplementedError
        axes.add_patch(circle)
        return axes

    #### Dunder methods ####
    def __eq__(self, other):
        return (
            isinstance(other, HexagonVertex) and self.feature_key == other.feature_key
        )

    def __hash__(self):
        return hash((type(self), self.feature_key))

    def __repr__(self):
        return f"{self.name} : {self.feature_key}"
    
    ### Public method ### 
    def distance(self, other, kwd = 'euclidian'):
        assert isinstance(other, HexagonVertex)
        if kwd == 'euclidian':
            return distance.euclidean(self.spatial_key, other.spatial_key)
        else:
            raise NotImplementedError
