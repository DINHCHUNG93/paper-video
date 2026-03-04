"""Protein secondary and tertiary structure representations."""

from manim import *
import numpy as np

__all__ = ["AlphaHelix", "BetaSheet", "ProteinBlob"]


class AlphaHelix(VGroup):
    """Alpha helix representation as a coiled ribbon.

    Parameters
    ----------
    n_turns : float
        Number of helix turns.
    height : float
        Total height of the helix.
    radius : float
        Helix radius.
    color : ManimColor
        Ribbon color.
    """

    def __init__(
        self,
        n_turns: float = 3,
        height: float = 3,
        radius: float = 0.4,
        color=PURPLE_B,
        **kwargs,
    ):
        super().__init__(**kwargs)
        pitch = height / (n_turns * TAU)

        self.ribbon = ParametricFunction(
            lambda t: np.array(
                [radius * np.cos(t), pitch * t - height / 2, radius * np.sin(t)]
            ),
            t_range=[0, n_turns * TAU, 0.1],
            color=color,
            stroke_width=6,
        )
        self.add(self.ribbon)

        # Label
        self.label = Text("\u03b1-helix", font_size=16, color=color)
        self.label.next_to(self, RIGHT, buff=0.2)


class BetaSheet(VGroup):
    """Beta sheet representation as parallel arrows.

    Parameters
    ----------
    n_strands : int
        Number of beta strands.
    strand_length : float
        Length of each strand.
    parallel : bool
        If True, parallel sheet; if False, antiparallel.
    color : ManimColor
        Sheet color.
    """

    def __init__(
        self,
        n_strands: int = 4,
        strand_length: float = 2,
        parallel: bool = False,
        color=YELLOW_D,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.strands = VGroup()

        for i in range(n_strands):
            direction = RIGHT if (parallel or i % 2 == 0) else LEFT
            start = LEFT * strand_length / 2 + DOWN * i * 0.5
            end = RIGHT * strand_length / 2 + DOWN * i * 0.5
            if direction is LEFT:
                start, end = end, start

            arrow = Arrow(
                start, end, color=color, stroke_width=8, buff=0, max_tip_length_to_length_ratio=0.1
            )
            self.strands.add(arrow)

        # H-bonds between strands
        self.h_bonds = VGroup()
        for i in range(n_strands - 1):
            for x in np.linspace(-strand_length / 3, strand_length / 3, 4):
                bond = DashedLine(
                    np.array([x, -i * 0.5 - 0.1, 0]),
                    np.array([x, -i * 0.5 - 0.4, 0]),
                    dash_length=0.03,
                    color=BLUE_A,
                    stroke_width=1,
                )
                self.h_bonds.add(bond)

        self.add(self.strands, self.h_bonds)

        self.label = Text("\u03b2-sheet", font_size=16, color=color)
        self.label.next_to(self, RIGHT, buff=0.2)


class ProteinBlob(VGroup):
    """Simplified tertiary protein structure as an irregular blob.

    Parameters
    ----------
    name : str
        Protein name for labeling.
    width, height : float
        Blob dimensions.
    color : ManimColor
        Blob color.
    """

    def __init__(
        self,
        name: str = "Protein",
        width: float = 2,
        height: float = 1.5,
        color=TEAL_D,
        **kwargs,
    ):
        super().__init__(**kwargs)

        # Irregular blob using a rounded ellipse with slight perturbation
        self.body = Ellipse(
            width=width, height=height, color=color, fill_opacity=0.4, stroke_width=3
        )
        self.name_label = Text(name, font_size=18, color=WHITE).move_to(self.body)

        self.add(self.body, self.name_label)

    def binding_site(self, position=RIGHT) -> Dot:
        """Return a small dot at a binding site location."""
        site = Dot(radius=0.06, color=RED).move_to(
            self.body.point_at_angle(
                {"RIGHT": 0, "UP": PI / 2, "LEFT": PI, "DOWN": 3 * PI / 2}.get(
                    str(position), 0
                )
            )
        )
        self.add(site)
        return site
