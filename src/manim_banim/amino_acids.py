"""Amino acid representations with backbone and R-group variants."""

from manim import *
from manim_banim.colors import AA_TYPE_COLORS

__all__ = ["AminoAcid", "AA_PROPERTIES"]

AA_PROPERTIES = {
    "Ala": {"abbrev": "A", "color": "#FF6B6B", "type": "nonpolar"},
    "Arg": {"abbrev": "R", "color": "#4ECDC4", "type": "positive"},
    "Asn": {"abbrev": "N", "color": "#45B7D1", "type": "polar"},
    "Asp": {"abbrev": "D", "color": "#96CEB4", "type": "negative"},
    "Cys": {"abbrev": "C", "color": "#FFEAA7", "type": "polar"},
    "Glu": {"abbrev": "E", "color": "#DDA0DD", "type": "negative"},
    "Gly": {"abbrev": "G", "color": "#98D8C8", "type": "nonpolar"},
    "His": {"abbrev": "H", "color": "#F7DC6F", "type": "positive"},
    "Ile": {"abbrev": "I", "color": "#BB8FCE", "type": "nonpolar"},
    "Leu": {"abbrev": "L", "color": "#85C1E9", "type": "nonpolar"},
    "Lys": {"abbrev": "K", "color": "#F1948A", "type": "positive"},
    "Met": {"abbrev": "M", "color": "#82E0AA", "type": "nonpolar"},
    "Phe": {"abbrev": "F", "color": "#F8C471", "type": "nonpolar"},
    "Pro": {"abbrev": "P", "color": "#D7BDE2", "type": "nonpolar"},
    "Ser": {"abbrev": "S", "color": "#AED6F1", "type": "polar"},
    "Thr": {"abbrev": "T", "color": "#A3E4D7", "type": "polar"},
    "Trp": {"abbrev": "W", "color": "#E59866", "type": "nonpolar"},
    "Tyr": {"abbrev": "Y", "color": "#D5F5E3", "type": "polar"},
    "Val": {"abbrev": "V", "color": "#FADBD8", "type": "nonpolar"},
}


class AminoAcid(VGroup):
    """Single amino acid with central carbon, amino group, carboxyl group, and R-group.

    Parameters
    ----------
    name : str
        Three-letter amino acid code (e.g. "Ala", "Gly").
    show_full : bool
        If True, show full structural detail (future use).
    """

    def __init__(self, name: str = "Ala", show_full: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.aa_name = name
        props = AA_PROPERTIES.get(name, {"abbrev": "?", "color": "#888888", "type": "unknown"})

        # Central alpha carbon
        self.c_alpha = Dot(radius=0.08, color=WHITE)

        # Amino group (left)
        amino_circle = Circle(radius=0.12, color=BLUE, fill_opacity=0.7)
        amino_label = Text("NH\u2082", font_size=8, color=WHITE).move_to(amino_circle)
        self.amino = VGroup(amino_circle, amino_label).shift(LEFT * 0.4)

        # Carboxyl group (right)
        carboxyl_circle = Circle(radius=0.12, color=RED, fill_opacity=0.7)
        carboxyl_label = Text("COOH", font_size=7, color=WHITE).move_to(carboxyl_circle)
        self.carboxyl = VGroup(carboxyl_circle, carboxyl_label).shift(RIGHT * 0.4)

        # R-group (below, color-coded)
        r_rect = RoundedRectangle(
            width=0.4,
            height=0.3,
            corner_radius=0.05,
            color=props["color"],
            fill_opacity=0.8,
        )
        r_label = Text(props["abbrev"], font_size=14, color=WHITE).move_to(r_rect)
        self.r_group = VGroup(r_rect, r_label).shift(DOWN * 0.35)

        # Bonds
        self.bonds = VGroup(
            Line(self.c_alpha.get_center(), self.amino[0].get_center(), stroke_width=2),
            Line(self.c_alpha.get_center(), self.carboxyl[0].get_center(), stroke_width=2),
            Line(self.c_alpha.get_center(), self.r_group[0].get_center(), stroke_width=2),
        )

        self.add(self.bonds, self.c_alpha, self.amino, self.carboxyl, self.r_group)
