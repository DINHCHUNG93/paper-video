"""Example: CRISPR-Cas9 gene editing overview."""

from manim import *
from manim_banim import *


class CRISPRDemo(Scene):
    """Simplified overview of CRISPR-Cas9 mechanism."""

    def construct(self):
        title = Text("CRISPR-Cas9: Gene Editing", font_size=34)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait()

        # Step 1: Target DNA
        dna = DNADoubleHelix(sequence="ATCGATCG")
        dna.scale(0.6).shift(LEFT * 2 + DOWN * 0.5)
        dna_label = BioLabel("Target DNA", target=dna, direction=UP, font_size=16)
        self.play(Create(dna), FadeIn(dna_label), run_time=1.5)
        self.wait()

        # Step 2: Guide RNA
        guide_rna = VGroup(
            RoundedRectangle(width=2, height=0.4, color=GREEN, fill_opacity=0.6, corner_radius=0.05),
            Text("Guide RNA", font_size=12, color=WHITE),
        )
        guide_rna[1].move_to(guide_rna[0])
        guide_rna.next_to(dna, RIGHT, buff=1.5).shift(UP * 1)

        self.play(FadeIn(guide_rna, shift=LEFT))
        self.wait(0.5)

        # Step 3: Cas9 protein
        cas9 = ProteinBlob(name="Cas9", width=1.5, height=1, color=ORANGE)
        cas9.next_to(guide_rna, DOWN, buff=0.3)
        self.play(FadeIn(cas9, shift=UP))
        self.wait(0.5)

        # Step 4: Complex binds to DNA
        complex_group = VGroup(guide_rna, cas9)
        self.play(complex_group.animate.move_to(dna.get_center() + RIGHT * 0.5), run_time=1.5)
        self.wait(0.5)

        # Step 5: DNA cut
        cut_label = Text("Double-strand break!", font_size=20, color=RED)
        cut_label.next_to(dna, DOWN, buff=0.5)

        # Scissors effect
        scissors = Text("✂", font_size=36, color=RED)
        scissors.move_to(dna.get_center())
        self.play(FadeIn(scissors, scale=0.5), Write(cut_label), run_time=0.8)
        self.play(dna.unzip_anim(start=3, end=5, run_time=1))
        self.wait()

        # Step 6: Repair options
        self.play(
            FadeOut(scissors), FadeOut(complex_group), FadeOut(cut_label),
        )

        repair_title = Text("Repair Pathways", font_size=22, color=WHITE)
        repair_title.shift(UP * 0.5)

        nhej = AnnotationBox("NHEJ: Quick but error-prone\n→ Gene knockout", width=3)
        nhej.shift(LEFT * 2.5 + DOWN * 1.5)

        hdr = AnnotationBox("HDR: Precise with template\n→ Gene correction", width=3)
        hdr.shift(RIGHT * 2.5 + DOWN * 1.5)

        self.play(Write(repair_title))
        self.play(FadeIn(nhej, shift=UP), FadeIn(hdr, shift=UP))
        self.wait(2)
