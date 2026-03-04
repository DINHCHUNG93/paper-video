"""Example: DNA Replication animation using banim primitives."""

from manim import *
from manim_banim import *


class DNAReplicationDemo(Scene):
    def construct(self):
        # Title
        title = Text("DNA Replication", font_size=36, color=WHITE)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait()

        # Create DNA double helix
        dna = DNADoubleHelix(sequence="ATCGATCG")
        dna.scale(0.65).shift(LEFT * 2)
        label = BioLabel("Double-stranded DNA", target=dna, direction=UP, font_size=18)
        self.play(Create(dna), run_time=2)
        self.play(FadeIn(label))
        self.wait()

        # Helicase arrives
        helicase = VGroup(
            Circle(radius=0.3, color=YELLOW, fill_opacity=0.7),
            Text("Helicase", font_size=10, color=WHITE),
        )
        helicase[1].move_to(helicase[0])
        helicase.next_to(dna, UP, buff=0.2)
        self.play(FadeIn(helicase, shift=DOWN))
        self.wait(0.5)

        # Unzip
        self.play(FadeOut(label))
        self.play(dna.unzip_anim(run_time=3))
        self.play(FadeOut(helicase))

        # Show daughter strands
        note = AnnotationBox("Each strand serves as a template")
        note.to_edge(RIGHT).shift(UP)
        self.play(FadeIn(note))
        self.wait()

        # New complementary bases appear
        new_dna1 = DNADoubleHelix(sequence="ATCGATCG")
        new_dna1.scale(0.45).shift(RIGHT * 2 + UP * 1.2)
        new_dna2 = DNADoubleHelix(sequence="ATCGATCG")
        new_dna2.scale(0.45).shift(RIGHT * 2 + DOWN * 1.2)

        l1 = Text("Daughter 1", font_size=14, color=WHITE).next_to(new_dna1, RIGHT)
        l2 = Text("Daughter 2", font_size=14, color=WHITE).next_to(new_dna2, RIGHT)

        self.play(
            FadeIn(new_dna1, shift=RIGHT),
            FadeIn(new_dna2, shift=RIGHT),
            Write(l1), Write(l2),
            run_time=2,
        )

        result = Text("Semi-conservative replication", font_size=22, color=REPLICATION_COLOR)
        result.to_edge(DOWN)
        self.play(Write(result))
        self.wait(2)
