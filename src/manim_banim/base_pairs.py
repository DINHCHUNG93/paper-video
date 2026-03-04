"""Base pair representations with hydrogen bonds."""

from manim import *
from manim_banim.nucleotides import Nucleotide

__all__ = ["BasePair"]

COMPLEMENTARY = {"A": "T", "T": "A", "G": "C", "C": "G", "U": "A"}
H_BOND_COUNT = {"AT": 2, "TA": 2, "GC": 3, "CG": 3, "AU": 2, "UA": 2}


class BasePair(VGroup):
    """Two complementary nucleotides connected by hydrogen bonds.

    Parameters
    ----------
    left_base : str
        Base type for the left nucleotide.
    right_base : str or None
        Base type for the right nucleotide. Auto-determined if None.
    """

    def __init__(self, left_base: str = "A", right_base: str | None = None, **kwargs):
        super().__init__(**kwargs)
        if right_base is None:
            right_base = COMPLEMENTARY[left_base]

        self.left_nt = Nucleotide(base_type=left_base)
        self.right_nt = Nucleotide(base_type=right_base)
        self.right_nt.flip(axis=RIGHT)
        self.right_nt.next_to(self.left_nt, RIGHT, buff=0.8)

        # Hydrogen bonds
        pair_key = left_base + right_base
        n_bonds = H_BOND_COUNT.get(pair_key, 2)
        self.h_bonds = VGroup()
        for i in range(n_bonds):
            offset = (i - (n_bonds - 1) / 2) * 0.08
            bond = DashedLine(
                self.left_nt.get_base_right() + UP * offset,
                self.right_nt.get_base_left() + UP * offset,
                dash_length=0.05,
                color=BLUE_A,
                stroke_width=1.5,
            )
            self.h_bonds.add(bond)

        self.add(self.left_nt, self.h_bonds, self.right_nt)

    def creation_anim(self, run_time: float = 1.5) -> Succession:
        """Animate nucleotides appearing, then hydrogen bonds forming."""
        return Succession(
            AnimationGroup(FadeIn(self.left_nt), FadeIn(self.right_nt)),
            Create(self.h_bonds, run_time=0.5),
        )

    def break_bonds_anim(self, run_time: float = 0.5) -> Animation:
        """Animate hydrogen bonds breaking."""
        return FadeOut(self.h_bonds, run_time=run_time)
