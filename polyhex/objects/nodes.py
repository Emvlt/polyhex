"""Base module for the nodes of a polyhex"""

# pylint: disable=line-too-long
# pylint: disable=possibly-used-before-assignment

from abc import ABC
from dataclasses import dataclass
from typing import List
from math import sqrt

from numpy.typing import ArrayLike
from scipy.spatial import distance
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from matplotlib.artist import Artist

from polyhex.objects.hexagons import Hexagon
from polyhex.objects.decorators import top_dependent

__all__ = ("HexagonCentre", "HexagonVertex")


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
    def encoding(self) -> List:
        """The encoding is an attribute of a node: it turns the string representation of the `feature` and the `token` into a list.

        Returns:
            (list): vector encoding of the node's representation
        """
        return [
            self.encoding_assets["feature"][self.feature],
            self.encoding_assets["token"][self.token],
        ]

    @property
    def name(self):
        """The name attribute is a string representation of the class' name. Example: HexagonCentre, HexagonVertex...

        Returns:
            _type_: _description_
        """
        return self._name

    @name.setter
    def name(self, name):
        """setter method for the name attribute"""
        self._name = name

    @property
    def x(self):
        """The x attribute is the second coordinate of the node on a cartesian grid."""
        return self._x

    @x.setter
    def x(self, x):
        """setter method for the x attribute"""
        self._x = x

    @property
    def y(self):
        """The y attribute is the second coordinate of the node on a cartesian grid."""
        return self._y

    @y.setter
    def y(self, y):
        """setter method for the y attribute"""
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
        """The `_render` method is a private method of the `Node` abstract class. It differs from the `render` public method as it is only implemented in the children classes.
        Args:
            axes (Artist): matplotlib.Artist on which to draw

        Raises:
            NotImplementedError: It is not implement for the abstract `Node` class.
        """
        raise NotImplementedError(
            "The _render() Method is not implemented for the abstract `Node` class."
        )

    def render(self, axes: Artist, **kwargs):
        """The `render` method is a public method of the `Node` abstract class.
        It differs from ``draw`` as it requires a matplotlib.axe and returns a matplotlib.axe
        Args:
            axes (Artist): matplotlib.Artist on which to draw
            kwargs : keyword dict that can replace the default rendering options defined in the assets.
        """
        if not kwargs:
            p = self.render_assets["feature"][f"{self.token}"]
            axes = self._render(axes, **p)
        else:
            axes = self._render(axes, **kwargs)
        return axes

    def add_token(self, new_token: str):
        """Method to add a token on a node.

        Args:
            new_token (str): str identifier of the token. Think 'settlement' in CATAN.
        """
        assert (
            new_token in self.compat_assets[self.feature]
        ), f"The token {new_token} is not compatible with the slot {self.feature} for {self.name} nodes"
        self.token = new_token


class HexagonCentre(Node):
    """
    ``HexagonCentre`` class which represents the centre of an hexagon
    It is created using:
        an hexagon (``polyhex.Hexagon``),
        a feature (``ArrayLike``)
    """

    def __init__(self, hexagon: Hexagon, feature: ArrayLike = "placeholder"):
        """Constructor of the ``HexagonCentre`` class

        Notes:
            The constructor adds the following attributes to the Node class
            [x,y] : defined as the cartesian coordinates of the ``HexagonCentre``
            spatial_key : defined as the hex coordinates of the ``HexagonCentre``

        Args:
            hexagon (Hexagon): Hexagon the ``HexagonCentre`` is the centre of.
            feature (ArrayLike, optional): Feature of the ``HexagonCentre``
        """
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
    def distance(self, other, kwd="euclidian"):
        """Method to compute the distance between two ``HexagonCentre``

        Args:
            other (_type_): other ``HexagonCentre``
            kwd (str, optional): Identifier of the distance. Defaults to "euclidian".

        Raises:
            NotImplementedError: This method is currently only implemented for the `euclidian` distance.

        Returns:
            np.ndarray: float distance value
        """
        assert isinstance(other, HexagonCentre)
        if kwd == "euclidian":
            return distance.euclidean(self.hex_coordinates, other.hex_coordinates)

        raise NotImplementedError(
            f"The distance function for {self.name} is not implemented for distance keyword {kwd}. It can only be `euclidian`."
        )


class HexagonVertex(Node):
    """
    ``HexagonVertex`` class which represents the centre of an hexagon
    It is created using:
        an hexagon (``polyhex.Hexagon``)
        the index of the vertex on the considered ``Hexagon``
        a feature (``ArrayLike``)
    It defines an extra `feature_key` attribute that combines the spatial and feature attributes of the HexagonVertex.

    Note:
        Unlike ``HexagonCentre``, vertices can spatially coincide hence they need more information to be distinguished from one another.
    """

    def __init__(
        self,
        hexagon: Hexagon,
        index: int = 0,
        feature: str = "placeholder",
    ):
        """Constructor of the ``HexagonVertex`` class

        Notes:
            The constructor adds the following attributes to the Node class
            [x,y] : defined as the cartesian coordinates of the ``HexagonVertex``
            spatial_key : defined as the cartesian coordinates of the ``HexagonVertex``
            feature_key : combines the spatial and feature attributes of the HexagonVertex.

        Args:
            hexagon (Hexagon): Hexagon the ``HexagonVertex`` is part of.
            feature (ArrayLike, optional): Feature of the ``HexagonVertex``
            index (int) : the index of the vertex in the considered Hexagon
        """
        cartesian_coordinates = hexagon._vertex_coord_factory()[index]
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
    def distance(self, other, kwd="euclidian"):
        """Method to compute the distance between two ``HexagonVertex``

        Args:
            other (_type_): other ``HexagonVertex``
            kwd (str, optional): Identifier of the distance. Defaults to "euclidian".

        Raises:
            NotImplementedError: This is currently not implemented for any distance but the `euclidian`.

        Returns:
            np.ndarray: float distance value
        """
        assert isinstance(other, HexagonVertex)
        if kwd == "euclidian":
            return distance.euclidean(self.spatial_key, other.spatial_key)

        raise NotImplementedError(
            f"The distance function for {self.name} is not implemented for distance keyword {kwd}. It can only be `euclidian`."
        )
