"""RNA representations: mRNA, tRNA, codons."""

from manim import *
from manim_banim.nucleotides import Nucleotide
from manim_banim.colors import *

__all__ = ["Codon", "MRNA", "TRNA"]

# Standard genetic code (codon -> amino acid)
CODON_TABLE = {
    "UUU": "Phe", "UUC": "Phe", "UUA": "Leu", "UUG": "Leu",
    "CUU": "Leu", "CUC": "Leu", "CUA": "Leu", "CUG": "Leu",
    "AUU": "Ile", "AUC": "Ile", "AUA": "Ile", "AUG": "Met",
    "GUU": "Val", "GUC": "Val", "GUA": "Val", "GUG": "Val",
    "UCU": "Ser", "UCC": "Ser", "UCA": "Ser", "UCG": "Ser",
    "CCU": "Pro", "CCC": "Pro", "CCA": "Pro", "CCG": "Pro",
    "ACU": "Thr", "ACC": "Thr", "ACA": "Thr", "ACG": "Thr",
    "GCU": "Ala", "GCC": "Ala", "GCA": "Ala", "GCG": "Ala",
    "UAU": "Tyr", "UAC": "Tyr", "UAA": "Stop", "UAG": "Stop",
    "CAU": "His", "CAC": "His", "CAA": "Gln", "CAG": "Gln",
    "AAU": "Asn", "AAC": "Asn", "AAA": "Lys", "AAG": "Lys",
    "GAU": "Asp", "GAC": "Asp", "GAA": "Glu", "GAG": "Glu",
    "UGU": "Cys", "UGC": "Cys", "UGA": "Stop", "UGG": "Trp",
    "CGU": "Arg", "CGC": "Arg", "CGA": "Arg", "CGG": "Arg",
    "AGU": "Ser", "AGC": "Ser", "AGA": "Arg", "AGG": "Arg",
    "GGU": "Gly", "GGC": "Gly", "GGA": "Gly", "GGG": "Gly",
}


class Codon(VGroup):
    """A triplet of RNA bases forming a codon.

    Parameters
    ----------
    sequence : str
        Three-letter RNA sequence, e.g. "AUG".
    """

    def __init__(self, sequence: str = "AUG", **kwargs):
        super().__init__(**kwargs)
        self.sequence = sequence
        self.amino_acid = CODON_TABLE.get(sequence, "?")

        self.bases = VGroup()
        for i, base in enumerate(sequence):
            nt = Nucleotide(base_type=base, sugar_type="ribose")
            nt.scale(0.7)
            nt.shift(RIGHT * i * 0.35)
            self.bases.add(nt)

        self.bracket = Brace(self.bases, DOWN, buff=0.05)
        self.aa_label = Text(self.amino_acid, font_size=12, color=WHITE)
        self.aa_label.next_to(self.bracket, DOWN, buff=0.05)

        self.add(self.bases, self.bracket, self.aa_label)


class MRNA(VGroup):
    """Messenger RNA with 5' cap, coding region, and poly-A tail.

    Parameters
    ----------
    sequence : str
        RNA sequence (length should be multiple of 3 for codons).
    show_cap : bool
        Show the 5' cap structure.
    show_polya : bool
        Show the poly-A tail.
    """

    def __init__(
        self,
        sequence: str = "AUGCGA",
        show_cap: bool = True,
        show_polya: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.sequence = sequence

        # 5' cap
        if show_cap:
            self.cap = Circle(radius=0.2, color=PURPLE, fill_opacity=0.7)
            cap_label = Text("5' cap", font_size=12).next_to(self.cap, UP, buff=0.05)
            self.add(self.cap, cap_label)

        # Codons
        self.codons = VGroup()
        x_offset = 0.6 if show_cap else 0
        for i in range(0, len(sequence), 3):
            codon_seq = sequence[i : i + 3]
            if len(codon_seq) < 3:
                break
            codon = Codon(codon_seq)
            codon.shift(RIGHT * (x_offset + (i // 3) * 1.2))
            self.codons.add(codon)
        self.add(self.codons)

        # Poly-A tail
        if show_polya:
            self.polya = Text("AAAA...", font_size=14, color=URACIL_COLOR)
            self.polya.next_to(self.codons, RIGHT, buff=0.3)
            self.add(self.polya)


class TRNA(VGroup):
    """Transfer RNA with anticodon loop and amino acid attachment.

    Parameters
    ----------
    anticodon : str
        Three-letter anticodon sequence.
    amino_acid : str
        Three-letter amino acid abbreviation carried by this tRNA.
    """

    def __init__(
        self, anticodon: str = "UAC", amino_acid: str = "Met", **kwargs
    ):
        super().__init__(**kwargs)
        self.anticodon_seq = anticodon
        self.aa_name = amino_acid

        # L-shaped body
        self.body = RoundedRectangle(
            width=0.8,
            height=1.2,
            corner_radius=0.1,
            color=GREEN_D,
            fill_opacity=0.5,
        )

        # Anticodon loop (bottom)
        self.anticodon_loop = Arc(
            radius=0.3, angle=PI, color=GREEN_D, stroke_width=3
        )
        self.anticodon_loop.next_to(self.body, DOWN, buff=0)
        self.anticodon_text = Text(anticodon, font_size=14, color=WHITE)
        self.anticodon_text.next_to(self.anticodon_loop, DOWN, buff=0.05)

        # Amino acid attachment (top)
        aa_circle = Circle(radius=0.15, color=RED_D, fill_opacity=0.8)
        aa_circle.next_to(self.body, UP, buff=0.05)
        aa_label = Text(amino_acid, font_size=10, color=WHITE).move_to(aa_circle)
        self.amino_acid = VGroup(aa_circle, aa_label)

        self.add(
            self.body,
            self.anticodon_loop,
            self.anticodon_text,
            self.amino_acid,
        )

    def detach_aa_anim(self, direction=UP, run_time: float = 0.5) -> Animation:
        """Animate the amino acid detaching from the tRNA."""
        return self.amino_acid.animate(run_time=run_time).shift(direction * 0.5)
