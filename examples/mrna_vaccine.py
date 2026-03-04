"""Example: How mRNA Vaccines Work."""

from manim import *
from manim_banim import *


class MRNAVaccineDemo(Scene):
    """Simplified explanation of mRNA vaccine mechanism."""

    def construct(self):
        title = Text("How mRNA Vaccines Work", font_size=34)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait()

        # Scene 1: The problem — virus
        virus = VGroup(
            Circle(radius=0.5, color=RED, fill_opacity=0.5),
            Text("Virus", font_size=14, color=WHITE),
        )
        virus[1].move_to(virus[0])
        # Spike proteins on virus
        spikes = VGroup()
        for angle in range(0, 360, 45):
            spike = Triangle(fill_opacity=0.7, color=RED_D).scale(0.1)
            spike.move_to(virus[0].point_at_angle(angle * DEGREES))
            spike.rotate(angle * DEGREES)
            spikes.add(spike)
        virus.add(spikes)
        virus.shift(LEFT * 3)

        self.play(FadeIn(virus))
        spike_label = BioLabel("Spike proteins", target=spikes, direction=DOWN, font_size=14)
        self.play(FadeIn(spike_label))
        self.wait()

        # Scene 2: mRNA in lipid nanoparticle
        lnp = VGroup(
            Circle(radius=0.6, color=BLUE_D, fill_opacity=0.2, stroke_width=2),
            Text("LNP", font_size=10, color=BLUE_D),
        )
        lnp[1].move_to(lnp[0].get_center() + UP * 0.3)

        mrna_inside = MRNA(sequence="AUGCGA", show_cap=False, show_polya=False)
        mrna_inside.scale(0.25).move_to(lnp[0])

        lnp_group = VGroup(lnp, mrna_inside)
        lnp_group.move_to(ORIGIN)

        self.play(FadeOut(virus), FadeOut(spike_label))
        self.play(FadeIn(lnp_group))

        lnp_label = Text("Lipid nanoparticle\nwith mRNA inside", font_size=14, color=WHITE)
        lnp_label.next_to(lnp_group, DOWN, buff=0.3)
        self.play(Write(lnp_label))
        self.wait()

        # Scene 3: Enter cell
        cell = Cell(show_nucleus=False, show_er=False, show_mitochondria=False, show_ribosomes=False)
        cell.scale(0.8).shift(RIGHT * 2)

        self.play(FadeOut(lnp_label))
        self.play(FadeIn(cell))
        self.play(lnp_group.animate.move_to(cell.membrane.get_center()), run_time=1.5)
        self.wait(0.5)

        # Scene 4: Ribosome reads mRNA
        self.play(FadeOut(lnp_group), FadeOut(cell))

        mrna = MRNA(sequence="AUGCGA", show_cap=True, show_polya=True)
        mrna.scale(0.55).shift(UP * 1)
        self.play(Create(mrna))

        ribo = Ribosome()
        ribo.scale(0.5).move_to(mrna.codons[0].get_center() + DOWN * 0.4)
        self.play(ribo.assemble_anim())

        ribo_label = Text("Ribosome reads mRNA\n→ builds spike protein", font_size=16, color=WHITE)
        ribo_label.to_edge(DOWN, buff=0.5)
        self.play(Write(ribo_label))
        self.wait()

        # Scene 5: Immune response
        self.play(*[FadeOut(m) for m in [mrna, ribo, ribo_label]])

        spike = VGroup(
            Triangle(fill_opacity=0.7, color=RED_D).scale(0.3),
            Text("Spike", font_size=12, color=WHITE),
        )
        spike[1].next_to(spike[0], DOWN, buff=0.05)
        spike.shift(LEFT * 1)
        self.play(FadeIn(spike))

        # Antibodies
        antibodies = VGroup()
        for pos in [RIGHT * 1 + UP * 0.5, RIGHT * 1.5, RIGHT * 1 + DOWN * 0.5]:
            ab = Text("Y", font_size=28, color=GREEN).move_to(pos)
            antibodies.add(ab)

        ab_label = Text("Antibodies", font_size=16, color=GREEN)
        ab_label.next_to(antibodies, RIGHT, buff=0.3)

        self.play(LaggedStart(*[FadeIn(ab, shift=LEFT * 0.3) for ab in antibodies], lag_ratio=0.2))
        self.play(Write(ab_label))

        # Arrow showing recognition
        recognition = Arrow(antibodies.get_left(), spike.get_right(), color=GREEN)
        self.play(Create(recognition))
        self.wait()

        # Final message
        self.play(*[FadeOut(m) for m in self.mobjects if m is not title])
        summary = Text(
            "Your immune system learns to\nrecognize the real virus",
            font_size=24,
            color=WHITE,
        )
        self.play(Write(summary))
        self.wait(2)
