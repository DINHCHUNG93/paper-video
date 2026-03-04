"""DNA strand and double helix representations."""

from manim import *
import numpy as np
from manim_banim.nucleotides import Nucleotide
from manim_banim.base_pairs import BasePair, COMPLEMENTARY
from manim_banim.colors import BACKBONE_COLOR

__all__ = ["DNAStrand", "DNADoubleHelix", "DNAHelix3D"]


class DNAStrand(VGroup):
    """A single strand of DNA as a vertical sequence of nucleotides.

    Parameters
    ----------
    sequence : str
        Nucleotide sequence, e.g. "ATCGATCG".
    spacing : float
        Vertical spacing between nucleotides.
    """

    def __init__(self, sequence: str = "ATCGATCG", spacing: float = 0.6, **kwargs):
        super().__init__(**kwargs)
        self.sequence = sequence
        self.nucleotides = VGroup()

        for i, base in enumerate(sequence):
            nt = Nucleotide(base_type=base)
            nt.shift(DOWN * i * spacing)
            self.nucleotides.add(nt)

        # Backbone connecting sugars
        self.backbone_line = VGroup()
        for i in range(len(self.nucleotides) - 1):
            line = Line(
                self.nucleotides[i].sugar.get_bottom(),
                self.nucleotides[i + 1].phosphate.get_top(),
                stroke_width=3,
                color=BACKBONE_COLOR,
            )
            self.backbone_line.add(line)

        self.add(self.nucleotides, self.backbone_line)


class DNADoubleHelix(VGroup):
    """Double-stranded DNA with complementary base pairing.

    Parameters
    ----------
    sequence : str
        Sequence of the sense strand (5' to 3').
    spacing : float
        Vertical spacing between base pairs.
    """

    def __init__(self, sequence: str = "ATCGATCG", spacing: float = 0.7, **kwargs):
        super().__init__(**kwargs)
        self.sequence = sequence
        self.base_pairs = VGroup()

        for i, base in enumerate(sequence):
            bp = BasePair(left_base=base)
            bp.shift(DOWN * i * spacing)
            self.base_pairs.add(bp)

        self.add(self.base_pairs)

    def unzip_anim(
        self, start: int = 0, end: int | None = None, run_time: float = 2
    ) -> LaggedStart:
        """Animate DNA unzipping (helicase action).

        Parameters
        ----------
        start, end : int
            Range of base pairs to unzip.
        run_time : float
            Total animation duration.
        """
        if end is None:
            end = len(self.base_pairs)

        anims = []
        for i in range(start, end):
            bp = self.base_pairs[i]
            anims.append(
                AnimationGroup(
                    bp.left_nt.animate.shift(LEFT * 0.5),
                    bp.right_nt.animate.shift(RIGHT * 0.5),
                    FadeOut(bp.h_bonds),
                    lag_ratio=0.3,
                )
            )
        return LaggedStart(*anims, lag_ratio=0.15, run_time=run_time)

    def zip_anim(
        self, start: int = 0, end: int | None = None, run_time: float = 2
    ) -> LaggedStart:
        """Animate DNA zipping back together."""
        if end is None:
            end = len(self.base_pairs)

        anims = []
        for i in range(start, end):
            bp = self.base_pairs[i]
            anims.append(
                AnimationGroup(
                    bp.left_nt.animate.shift(RIGHT * 0.5),
                    bp.right_nt.animate.shift(LEFT * 0.5),
                    FadeIn(bp.h_bonds),
                    lag_ratio=0.3,
                )
            )
        return LaggedStart(*anims, lag_ratio=0.15, run_time=run_time)


class DNAHelix3D(VGroup):
    """3D double helix representation using parametric curves.

    Parameters
    ----------
    n_turns : float
        Number of helix turns.
    radius : float
        Helix radius.
    pitch : float
        Vertical distance per radian.
    color_1, color_2 : ManimColor
        Colors for the two strands.
    """

    def __init__(
        self,
        n_turns: float = 3,
        radius: float = 1,
        pitch: float = 0.5,
        color_1=BLUE,
        color_2=RED,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.n_turns = n_turns
        self.radius = radius
        self.pitch = pitch

        t_range = [0, n_turns * TAU, 0.1]

        self.strand_1 = ParametricFunction(
            lambda t: np.array(
                [radius * np.cos(t), radius * np.sin(t), pitch * t]
            ),
            t_range=t_range,
            color=color_1,
            stroke_width=4,
        )
        self.strand_2 = ParametricFunction(
            lambda t: np.array(
                [radius * np.cos(t + PI), radius * np.sin(t + PI), pitch * t]
            ),
            t_range=t_range,
            color=color_2,
            stroke_width=4,
        )

        # Rungs (base pairs) at regular intervals
        self.rungs = VGroup()
        for t in np.arange(0, n_turns * TAU, PI / 2):
            p1 = np.array(
                [radius * np.cos(t), radius * np.sin(t), pitch * t]
            )
            p2 = np.array(
                [
                    radius * np.cos(t + PI),
                    radius * np.sin(t + PI),
                    pitch * t,
                ]
            )
            rung = Line3D(start=p1, end=p2, color=GREEN_A)
            self.rungs.add(rung)

        self.add(self.strand_1, self.strand_2, self.rungs)
