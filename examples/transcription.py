"""Example: Transcription — DNA to mRNA."""

from manim import *
from manim_banim import *


class TranscriptionDemo(Scene):
    """Demonstrates the transcription process step by step."""

    def construct(self):
        title = Text("Transcription: DNA → mRNA", font_size=32)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait()

        # Step 1: Show DNA
        dna = DNADoubleHelix(sequence="TACGAT")
        dna.scale(0.7).to_edge(LEFT, buff=1.5)
        step1 = Text("1. DNA template", font_size=18, color=GREY_B).to_edge(DOWN)
        self.play(Create(dna), Write(step1), run_time=2)
        self.wait()

        # Step 2: RNA Polymerase binds
        rnap = VGroup(
            RoundedRectangle(width=1, height=0.5, color=ORANGE, fill_opacity=0.7, corner_radius=0.1),
            Text("RNA Pol", font_size=10, color=WHITE),
        )
        rnap[1].move_to(rnap[0])
        rnap.next_to(dna, UP, buff=0.2)

        step2 = Text("2. RNA Polymerase binds", font_size=18, color=GREY_B).to_edge(DOWN)
        self.play(FadeOut(step1), FadeIn(rnap, shift=DOWN), Write(step2))
        self.wait()

        # Step 3: DNA unzips
        step3 = Text("3. Helicase unwinds DNA", font_size=18, color=GREY_B).to_edge(DOWN)
        self.play(FadeOut(step2), Write(step3))
        self.play(dna.unzip_anim(run_time=2))
        self.wait()

        # Step 4: mRNA is synthesized
        mrna = MRNA(sequence="AUGCUA", show_cap=True, show_polya=True)
        mrna.scale(0.6).next_to(dna, RIGHT, buff=1.5)

        step4 = Text("4. mRNA synthesized (complementary)", font_size=18, color=GREY_B).to_edge(DOWN)
        self.play(FadeOut(step3), Write(step4))

        arrow = Arrow(dna.get_right() + RIGHT * 0.2, mrna.get_left(), color=TRANSCRIPTION_COLOR)
        self.play(Create(arrow), Create(mrna), run_time=2)
        self.wait()

        # Step 5: mRNA leaves nucleus
        step5 = Text("5. mRNA exits nucleus → cytoplasm", font_size=18, color=GREY_B).to_edge(DOWN)
        self.play(FadeOut(step4), Write(step5))
        self.play(mrna.animate.shift(RIGHT * 2), run_time=1.5)
        self.wait(2)
