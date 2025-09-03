"""Base module for the edges of a polyhex"""

# pylint: disable=line-too-long
# pylint: disable=too-many-instance-attributes

from dataclasses import dataclass

import matplotlib.pyplot as plt
from numpy.typing import ArrayLike
from matplotlib.artist import Artist

from polyhex.objects.nodes import HexagonVertex
from polyhex.objects.hexagons import Hexagon

__all__ = ("HexagonEdge",)


@dataclass
class HexagonEdge:
    """HexagonEdge class.

    Args:
        hexagon (Hexagon) : the hexagon to which the edge's belong
        start (HexagonVertex) : the start vertex
        end (HexagonVertex) : the end  vertex
        index (int) : the edge's index in the hexagon (0 to 5)
        feature (ArrayLike) : the edge's feature
        free (bool): Identifies if there is something on the edge. Defaults to False.
        token (ArrayLike): Identifies what is on the edge. Defaults to None
    """

    hexagon: Hexagon
    start: HexagonVertex
    end: HexagonVertex
    index: int
    feature: ArrayLike = "placeholder"

    def __post_init__(self):
        self.spatial_key = frozenset((self.start.spatial_key, self.end.spatial_key))
        self.feature_key = frozenset((self.spatial_key, self.feature))
        self.name = "HexagonEdge"
        self.render_assets = self.hexagon.assets["render"][self.name]
        self.compat_assets = self.hexagon.assets["compatibility"][self.name]
        self.encoding_assets = self.hexagon.assets["encoding"][self.name]

        self.token = "placeholder"

    @property
    def encoding(self):
        """The encoding is an attribute of an edge: it turns the string representation of the `feature` and the `token` into a list.

        Returns:
            (list): vector encoding of the edge's representation
        """
        return [
            self.encoding_assets["feature"][self.feature],
            self.encoding_assets["token"][self.token],
        ]

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

    def render_line(self, axes, **kwargs):
        """Method to render the body of an edge. It is used in conjunction with `render_triangle` that draws the background of an hexagon, in the triangle in the edge's end, start and Hexagon's centre node.

        Args:
            axes (Artist): matplotlib.Artist on which to draw

        Returns:
            axes (Artist): matplotlib.Artist on which the edge was rendered
        """
        if not kwargs:
            render_params = self.render_assets["feature"][self.token]
            axes.plot(
                [self.start.display_coordinates[0], self.end.display_coordinates[0]],
                [self.start.display_coordinates[1], self.end.display_coordinates[1]],
                **render_params["line"],
            )
        else:
            axes.plot(
                [self.start.display_coordinates[0], self.end.display_coordinates[0]],
                [self.start.display_coordinates[1], self.end.display_coordinates[1]],
                **kwargs,
            )
        return axes

    def render_triangle(self, axes, **kwargs):
        """Method to render the background of an hexagon, in the triangle in the edge's end, start and Hexagon's centre node. It is used in conjunction with `render_line` that draws the edge's body

        Args:
            axes (Artist): matplotlib.Artist on which to draw

        Returns:
            axes (Artist): matplotlib.Artist on which the edge was rendered
        """
        triangle = [
            self.start.display_coordinates,
            self.end.display_coordinates,
            self.hexagon.centre.display_coordinates,
        ]
        render_params = self.render_assets["feature"][self.token]
        if not kwargs:
            axes.add_patch(plt.Polygon(xy=triangle, **render_params["triangle"]))
        else:
            axes.add_patch(plt.Polygon(xy=triangle, **render_params["triangle"]))
        return axes

    def render(self, axes: Artist, **kwargs):
        """The `render` method is a public method.
        It is used for display and differs from ``draw`` as it requires a matplotlib.axe and returns a matplotlib.axe
        Args:
            axes (Artist): matplotlib.Artist on which to draw
            kwargs : keyword dict that can replace the default rendering options defined in the assets.

        Returns:
            axes (Artist): matplotlib.Artist on which the edge was rendered
        """
        axes = self.render_line(axes, **kwargs)
        axes = self.render_triangle(axes, **kwargs)
        return axes

    def distance(self, other, kwd="path"):
        """Method to compute the distance between two edges.

        Args:
            other (HexagonEdge): other HexagonEdge
            kwd (str, optional): kwd identifier of the distance. Defaults to "path".

        Raises:
            NotImplementedError: f'The distance method is only implemented for the kwd `path`.

        Returns:
            int: 0 or 1
        """
        assert isinstance(other, HexagonEdge)
        if kwd == "path":
            return int(
                (self.start in [other.start, other.end])
                or (self.end in [other.start, other.end])
            )
        raise NotImplementedError(
            f"The distance method is only implemented for the kwd `path`. Got {kwd}"
        )

    ### __dunder__ nethods ###
    def __eq__(self, other):
        return isinstance(other, HexagonEdge) and self.feature_key == other.feature_key

    def __str__(self):
        return f"Edge: {self.start} -> {self.end} \n"
