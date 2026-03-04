"""Example: Translation — mRNA to protein."""

from manim import *
from manim_banim import *


class TranslationDemo(Scene):
    """Demonstrates the translation process with ribosome, tRNA, and peptide chain."""

    def construct(self):
        title = Text("Translation: mRNA → Protein", font_size=32)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait()

        # mRNA
        mrna = MRNA(sequence="AUGGGCGCU", show_cap=True, show_polya=False)
        mrna.scale(0.65).shift(UP * 1.5)
        self.play(Create(mrna), run_time=1.5)

        # Ribosome
        ribo = Ribosome()
        ribo.scale(0.6).move_to(mrna.codons[0].get_center() + DOWN * 0.5)
        self.play(ribo.assemble_anim())
        self.wait(0.5)

        # Translate each codon
        amino_acids = ["Met", "Gly", "Ala"]
        anticodons = ["UAC", "CCG", "CGA"]
        built = VGroup()

        for i, (aa_name, ac) in enumerate(zip(amino_acids, anticodons)):
            # tRNA arrives
            trna = TRNA(anticodon=ac, amino_acid=aa_name)
            trna.scale(0.45).move_to(ribo.get_center() + DOWN * 2.5)

            self.play(FadeIn(trna, shift=UP * 0.5), run_time=0.5)
            self.play(trna.animate.move_to(ribo.get_center() + DOWN * 0.3), run_time=0.4)
            self.wait(0.3)

            # Amino acid joins chain
            aa = AminoAcid(name=aa_name)
            aa.scale(0.5).move_to(
                ribo.get_right() + RIGHT * (0.5 + i * 0.7) + DOWN * 0.3
            )
            self.play(FadeIn(aa, shift=LEFT * 0.2), run_time=0.3)

            if built:
                bond = Line(built[-1].get_right(), aa.get_left(), stroke_width=2, color=YELLOW)
                self.play(Create(bond), run_time=0.2)

            built.add(aa)
            self.play(FadeOut(trna, shift=DOWN * 0.5), run_time=0.3)

            # Ribosome advances
            if i < len(amino_acids) - 1 and i + 1 < len(mrna.codons):
                self.play(
                    ribo.animate.move_to(mrna.codons[i + 1].get_center() + DOWN * 0.5),
                    run_time=0.4,
                )

        # Label the peptide
        peptide_label = Text("Peptide chain", font_size=18, color=TRANSLATION_COLOR)
        peptide_label.next_to(built, DOWN, buff=0.3)
        self.play(Write(peptide_label))
        self.wait(2)
