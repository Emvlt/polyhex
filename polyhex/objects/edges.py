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
        return [
            self.encoding_assets["feature"][self.feature],
            self.encoding_assets["token"][self.token],
        ]

    def draw(self, save=True):
        """The draw function is a convenience function that wraps the `render` function. It is used for standalone drawing and generates a figure which is saaved based on the save boolean argument

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
        if kwargs == {}:
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
        triangle = [
            self.start.display_coordinates,
            self.end.display_coordinates,
            self.hexagon.centre.display_coordinates,
        ]
        render_params = self.render_assets["feature"][self.token]
        if kwargs == {}:
            axes.add_patch(plt.Polygon(xy=triangle, **render_params["triangle"]))
        else:
            axes.add_patch(plt.Polygon(xy=triangle, **render_params["triangle"]))
        return axes

    def render(self, axes: Artist, **kwargs):
        axes = self.render_line(axes, **kwargs)
        axes = self.render_triangle(axes, **kwargs)
        return axes

    def distance(self, other, kwd="path"):
        assert isinstance(other, HexagonEdge)
        if kwd == "path":
            return int(
                (self.start == other.start or self.start == other.end)
                or (self.end == other.end or self.end == other.start)
            )
        else:
            raise NotImplementedError

    ### __dunder__ nethods ###
    def __eq__(self, other):
        return isinstance(other, HexagonEdge) and self.feature_key == other.feature_key

    def __str__(self):
        return f"Edge: {self.start} -> {self.end} \n"
