"""Nucleotide building blocks: phosphate, sugar, nitrogenous base."""

from manim import *
from manim_banim.colors import BASE_COLORS, PHOSPHATE_COLOR, SUGAR_COLOR, BACKBONE_COLOR

__all__ = ["Nucleotide"]


class Nucleotide(VGroup):
    """A single nucleotide with phosphate group, sugar, and nitrogenous base.

    Parameters
    ----------
    base_type : str
        One of "A", "T", "G", "C", "U".
    sugar_type : str
        "deoxyribose" for DNA, "ribose" for RNA.
    show_labels : bool
        Whether to show letter labels on components.
    """

    def __init__(
        self,
        base_type: str = "A",
        sugar_type: str = "deoxyribose",
        show_labels: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.base_type = base_type
        self.sugar_type = sugar_type

        base_color = BASE_COLORS.get(base_type, WHITE)

        # Phosphate group
        self.phosphate = Circle(radius=0.15, color=PHOSPHATE_COLOR, fill_opacity=0.8)
        if show_labels:
            self.phosphate_label = Text("P", font_size=14, color=WHITE).move_to(
                self.phosphate
            )
        else:
            self.phosphate_label = VMobject()

        # Sugar (pentagon)
        self.sugar = RegularPolygon(
            n=5, radius=0.2, color=SUGAR_COLOR, fill_opacity=0.6
        )
        self.sugar.next_to(self.phosphate, DOWN, buff=0.1)

        # Nitrogenous base (rounded rect, color-coded)
        self.base = RoundedRectangle(
            width=0.5,
            height=0.35,
            corner_radius=0.05,
            color=base_color,
            fill_opacity=0.8,
        )
        self.base.next_to(self.sugar, RIGHT, buff=0.1)

        if show_labels:
            self.base_label = Text(base_type, font_size=16, color=WHITE).move_to(
                self.base
            )
        else:
            self.base_label = VMobject()

        # Backbone connector
        self.backbone = Line(
            self.phosphate.get_bottom(),
            self.sugar.get_top(),
            stroke_width=2,
            color=BACKBONE_COLOR,
        )

        self.add(
            self.phosphate,
            self.phosphate_label,
            self.backbone,
            self.sugar,
            self.base,
            self.base_label,
        )

    def get_base_center(self) -> np.ndarray:
        """Return center of the nitrogenous base (for hydrogen bond connections)."""
        return self.base.get_center()

    def get_base_right(self) -> np.ndarray:
        return self.base.get_right()

    def get_base_left(self) -> np.ndarray:
        return self.base.get_left()
