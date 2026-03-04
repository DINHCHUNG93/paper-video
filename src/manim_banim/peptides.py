"""Peptide chains: amino acids connected by peptide bonds."""

from manim import *
import numpy as np
from manim_banim.amino_acids import AminoAcid

__all__ = ["PeptideChain"]


class PeptideChain(VGroup):
    """Chain of amino acids connected by peptide bonds.

    Parameters
    ----------
    sequence : list[str]
        List of three-letter amino acid codes.
    spacing : float
        Horizontal spacing between amino acids.
    """

    def __init__(
        self,
        sequence: list[str] | None = None,
        spacing: float = 1.0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        if sequence is None:
            sequence = ["Ala", "Gly", "Ser", "Met"]

        self.sequence = sequence
        self.amino_acids = VGroup()
        self.peptide_bonds = VGroup()

        for i, aa_name in enumerate(sequence):
            aa = AminoAcid(name=aa_name)
            aa.shift(RIGHT * i * spacing)
            self.amino_acids.add(aa)

            if i > 0:
                bond = Line(
                    self.amino_acids[i - 1].carboxyl.get_right(),
                    aa.amino.get_left(),
                    stroke_width=3,
                    color=YELLOW,
                )
                self.peptide_bonds.add(bond)

        self.add(self.amino_acids, self.peptide_bonds)

    def build_anim(self, run_time: float = 2) -> LaggedStart:
        """Animate the peptide chain being built one amino acid at a time."""
        anims = []
        for i, aa in enumerate(self.amino_acids):
            group = [FadeIn(aa, shift=DOWN * 0.3)]
            if i < len(self.peptide_bonds):
                group.append(Create(self.peptide_bonds[i]))
            anims.append(AnimationGroup(*group))
        return LaggedStart(*anims, lag_ratio=0.4, run_time=run_time)

    def fold_anim(self, fold_type: str = "alpha_helix", run_time: float = 2) -> Animation:
        """Animate protein folding into secondary structure.

        Parameters
        ----------
        fold_type : str
            "alpha_helix" or "beta_sheet".
        """
        if fold_type == "alpha_helix":
            target = self.amino_acids.copy()
            for i, aa in enumerate(target):
                angle = i * PI / 4
                radius = 0.5
                aa.move_to(
                    np.array(
                        [
                            radius * np.cos(angle),
                            radius * np.sin(angle),
                            0,
                        ]
                    )
                )
            return Transform(self.amino_acids, target, run_time=run_time)

        elif fold_type == "beta_sheet":
            target = self.amino_acids.copy()
            for i, aa in enumerate(target):
                row = i // 4
                col = i % 4
                direction = 1 if row % 2 == 0 else -1
                aa.move_to(np.array([direction * col * 0.6, -row * 0.8, 0]))
            return Transform(self.amino_acids, target, run_time=run_time)

        return Wait(run_time)
