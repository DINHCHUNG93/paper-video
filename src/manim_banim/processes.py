"""Pre-built animated biological processes: transcription, translation, replication."""

from manim import *
from manim_banim.dna import DNADoubleHelix, DNAStrand
from manim_banim.rna import MRNA, TRNA, Codon, CODON_TABLE
from manim_banim.cell import Ribosome
from manim_banim.peptides import PeptideChain
from manim_banim.amino_acids import AminoAcid
from manim_banim.base_pairs import COMPLEMENTARY
from manim_banim.colors import *

__all__ = ["TranscriptionScene", "TranslationScene", "ReplicationScene"]

# DNA -> RNA complement (transcription)
DNA_TO_RNA = {"A": "U", "T": "A", "G": "C", "C": "G"}


class TranscriptionScene(Scene):
    """Ready-to-use scene: DNA -> mRNA transcription.

    Shows DNA unzipping, RNA polymerase moving along, and mRNA being synthesized.
    """

    def construct(self):
        title = Text("Transcription: DNA \u2192 mRNA", font_size=28, color=WHITE)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        # DNA double helix
        dna_seq = "ATCGATCG"
        dna = DNADoubleHelix(sequence=dna_seq)
        dna.scale(0.7).to_edge(LEFT, buff=1)
        self.play(Create(dna), run_time=2)
        self.wait()

        # RNA Polymerase
        rnap = RoundedRectangle(
            width=1.2, height=0.6, color=ORANGE, fill_opacity=0.7, corner_radius=0.1,
        )
        rnap_label = Text("RNA Pol II", font_size=11, color=WHITE).move_to(rnap)
        rnap_group = VGroup(rnap, rnap_label)
        rnap_group.next_to(dna, UP, buff=0.3)
        self.play(FadeIn(rnap_group, shift=DOWN))
        self.wait(0.5)

        # DNA unzips
        self.play(dna.unzip_anim(run_time=2))
        self.wait(0.5)

        # mRNA synthesized
        rna_seq = "".join(DNA_TO_RNA[b] for b in dna_seq)
        mrna = MRNA(sequence=rna_seq)
        mrna.scale(0.6).next_to(dna, RIGHT, buff=1.5)
        self.play(Create(mrna), run_time=2)

        # Arrow
        arrow = Arrow(dna.get_right(), mrna.get_left(), color=TRANSCRIPTION_COLOR)
        arrow_label = Text("transcription", font_size=14, color=TRANSCRIPTION_COLOR)
        arrow_label.next_to(arrow, UP, buff=0.1)
        self.play(Create(arrow), Write(arrow_label))
        self.wait(2)


class TranslationScene(Scene):
    """Ready-to-use scene: mRNA -> protein translation.

    Shows ribosome reading mRNA codons, tRNAs delivering amino acids,
    and a peptide chain growing.
    """

    def construct(self):
        title = Text("Translation: mRNA \u2192 Protein", font_size=28, color=WHITE)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        # mRNA
        mrna_seq = "AUGGGCUAA"
        mrna = MRNA(sequence=mrna_seq)
        mrna.scale(0.7).shift(UP * 1)
        self.play(Create(mrna), run_time=1.5)
        self.wait(0.5)

        # Ribosome assembles
        ribo = Ribosome()
        ribo.scale(0.7)
        ribo.move_to(mrna.codons[0].get_center() + DOWN * 0.3)
        self.play(ribo.assemble_anim())
        self.wait(0.5)

        # Translation: tRNA delivers amino acids
        codons_text = [mrna_seq[i : i + 3] for i in range(0, len(mrna_seq), 3)]
        aa_names = [CODON_TABLE.get(c, "?") for c in codons_text if CODON_TABLE.get(c) != "Stop"]

        built_aas = VGroup()
        for i, aa_name in enumerate(aa_names):
            # tRNA arrives
            anticodon = codons_text[i][::-1]  # simplified
            trna = TRNA(anticodon=anticodon, amino_acid=aa_name)
            trna.scale(0.5)
            trna.move_to(ribo.get_center() + DOWN * 2)
            self.play(FadeIn(trna, shift=UP), run_time=0.5)
            self.play(trna.animate.move_to(ribo.get_center() + DOWN * 0.5), run_time=0.5)

            # Add amino acid to chain
            aa = AminoAcid(name=aa_name)
            aa.scale(0.6)
            aa.move_to(ribo.get_center() + RIGHT * (1 + i * 0.8) + DOWN * 0.3)
            self.play(FadeIn(aa, shift=LEFT * 0.3), run_time=0.3)
            built_aas.add(aa)

            # tRNA leaves
            self.play(FadeOut(trna, shift=DOWN), run_time=0.3)

            # Ribosome advances
            if i < len(aa_names) - 1 and i < len(mrna.codons) - 1:
                self.play(
                    ribo.animate.move_to(
                        mrna.codons[i + 1].get_center() + DOWN * 0.3
                    ),
                    run_time=0.5,
                )

        # Peptide bond lines
        peptide_bonds = VGroup()
        for i in range(len(built_aas) - 1):
            bond = Line(
                built_aas[i].get_right(),
                built_aas[i + 1].get_left(),
                stroke_width=3,
                color=YELLOW,
            )
            peptide_bonds.add(bond)
        self.play(Create(peptide_bonds), run_time=0.5)

        # Stop codon label
        stop_label = Text("Stop codon (UAA)", font_size=16, color=RED)
        stop_label.next_to(mrna.codons[-1], DOWN, buff=0.8)
        self.play(Write(stop_label))
        self.wait(2)


class ReplicationScene(Scene):
    """Ready-to-use scene: DNA replication.

    Shows helicase unwinding, leading/lagging strand synthesis.
    """

    def construct(self):
        title = Text("DNA Replication", font_size=28, color=WHITE)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        # Original DNA
        dna = DNADoubleHelix(sequence="ATCGATCG")
        dna.scale(0.7).shift(LEFT * 2)
        original_label = Text("Original DNA", font_size=16, color=WHITE)
        original_label.next_to(dna, UP, buff=0.3)
        self.play(Create(dna), Write(original_label), run_time=2)
        self.wait()

        # Helicase
        helicase = VGroup(
            Circle(radius=0.25, color=YELLOW, fill_opacity=0.7),
            Text("Helicase", font_size=8, color=WHITE),
        )
        helicase[1].move_to(helicase[0])
        helicase.next_to(dna, UP, buff=0.1)
        self.play(FadeIn(helicase, shift=DOWN))

        # Unzip
        self.play(dna.unzip_anim(run_time=2))
        self.play(FadeOut(helicase))
        self.wait(0.5)

        # New complementary strands appear
        new_strand_label = Text(
            "Semi-conservative replication", font_size=18, color=REPLICATION_COLOR,
        )
        new_strand_label.to_edge(DOWN, buff=0.5)
        self.play(Write(new_strand_label))

        # Show two new double-stranded DNAs
        dna2 = DNADoubleHelix(sequence="ATCGATCG")
        dna2.scale(0.5).shift(RIGHT * 2 + UP * 1)
        dna3 = DNADoubleHelix(sequence="ATCGATCG")
        dna3.scale(0.5).shift(RIGHT * 2 + DOWN * 1.5)

        label2 = Text("Daughter 1", font_size=14, color=WHITE).next_to(dna2, RIGHT)
        label3 = Text("Daughter 2", font_size=14, color=WHITE).next_to(dna3, RIGHT)

        self.play(
            FadeIn(dna2, shift=RIGHT),
            FadeIn(dna3, shift=RIGHT),
            Write(label2),
            Write(label3),
            run_time=2,
        )
        self.wait(2)
