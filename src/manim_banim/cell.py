"""Cell components: membrane, organelles, ribosome."""

from manim import *
import numpy as np
from manim_banim.colors import *

__all__ = ["CellMembrane", "Ribosome", "Cell", "Mitochondrion", "Nucleus"]


class CellMembrane(VGroup):
    """Phospholipid bilayer section.

    Parameters
    ----------
    width : float
        Width of the membrane section.
    n_lipids : int
        Number of lipid molecules per layer.
    """

    def __init__(self, width: float = 6, n_lipids: int = 12, **kwargs):
        super().__init__(**kwargs)
        self.lipids_top = VGroup()
        self.lipids_bottom = VGroup()

        spacing = width / n_lipids
        for i in range(n_lipids):
            x = -width / 2 + i * spacing + spacing / 2

            # Top layer
            head_t = Circle(radius=0.08, color=MEMBRANE_COLOR, fill_opacity=0.8)
            head_t.move_to([x, 0.3, 0])
            tail_t = Line([x, 0.22, 0], [x, -0.1, 0], stroke_width=1.5, color=SUGAR_COLOR)
            self.lipids_top.add(VGroup(head_t, tail_t))

            # Bottom layer
            head_b = Circle(radius=0.08, color=MEMBRANE_COLOR, fill_opacity=0.8)
            head_b.move_to([x, -0.3, 0])
            tail_b = Line([x, -0.22, 0], [x, 0.1, 0], stroke_width=1.5, color=SUGAR_COLOR)
            self.lipids_bottom.add(VGroup(head_b, tail_b))

        self.add(self.lipids_top, self.lipids_bottom)


class Ribosome(VGroup):
    """Ribosome with large and small subunits.

    Parameters
    ----------
    prokaryotic : bool
        If True, use 50S/30S labels; if False, use 60S/40S (eukaryotic).
    """

    def __init__(self, prokaryotic: bool = False, **kwargs):
        super().__init__(**kwargs)
        large_label = "50S" if prokaryotic else "60S"
        small_label = "30S" if prokaryotic else "40S"

        self.large_subunit = Ellipse(
            width=1.2, height=0.8, color=RIBOSOME_COLOR, fill_opacity=0.6
        )
        self.large_label = Text(large_label, font_size=12, color=WHITE).move_to(
            self.large_subunit
        )

        self.small_subunit = Ellipse(
            width=0.9, height=0.5, color=PURPLE_C, fill_opacity=0.6
        )
        self.small_subunit.next_to(self.large_subunit, DOWN, buff=-0.1)
        self.small_label = Text(small_label, font_size=10, color=WHITE).move_to(
            self.small_subunit
        )

        self.channel = Line(
            self.small_subunit.get_left() + RIGHT * 0.1,
            self.small_subunit.get_right() + LEFT * 0.1,
            stroke_width=2,
            color=YELLOW,
        )

        self.add(
            self.large_subunit, self.large_label,
            self.small_subunit, self.small_label,
            self.channel,
        )

    def assemble_anim(self, run_time: float = 1) -> AnimationGroup:
        """Animate subunits coming together."""
        self.large_subunit.shift(UP * 1)
        self.small_subunit.shift(DOWN * 1)
        return AnimationGroup(
            self.large_subunit.animate.shift(DOWN * 1),
            self.small_subunit.animate.shift(UP * 1),
            run_time=run_time,
        )

    def disassemble_anim(self, run_time: float = 1) -> AnimationGroup:
        """Animate subunits separating."""
        return AnimationGroup(
            self.large_subunit.animate.shift(UP * 1),
            self.small_subunit.animate.shift(DOWN * 1),
            run_time=run_time,
        )


class Nucleus(VGroup):
    """Cell nucleus with nuclear envelope and optional DNA inside.

    Parameters
    ----------
    width, height : float
        Dimensions of the nucleus.
    show_nucleolus : bool
        Whether to show a nucleolus inside.
    """

    def __init__(
        self,
        width: float = 2,
        height: float = 1.5,
        show_nucleolus: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.envelope = Ellipse(
            width=width, height=height, color=NUCLEUS_COLOR,
            fill_opacity=0.15, stroke_width=2.5,
        )

        # Nuclear pores (small gaps)
        self.pores = VGroup()
        for angle in [0, PI / 3, 2 * PI / 3, PI, 4 * PI / 3, 5 * PI / 3]:
            pore = Dot(
                self.envelope.point_at_angle(angle),
                radius=0.04, color=NUCLEUS_COLOR,
            )
            self.pores.add(pore)

        self.add(self.envelope, self.pores)

        if show_nucleolus:
            self.nucleolus = Circle(
                radius=0.3, color=PURPLE_A, fill_opacity=0.3, stroke_width=1.5,
            )
            self.nucleolus.shift(UP * 0.1 + RIGHT * 0.15)
            nucleolus_label = Text("Nucleolus", font_size=8, color=WHITE).move_to(
                self.nucleolus
            )
            self.add(self.nucleolus, nucleolus_label)

        self.label = Text("Nucleus", font_size=14, color=WHITE)
        self.label.next_to(self.envelope, DOWN, buff=0.1)
        self.add(self.label)


class Mitochondrion(VGroup):
    """Mitochondrion with outer membrane, inner membrane, and cristae.

    Parameters
    ----------
    width, height : float
        Dimensions.
    """

    def __init__(self, width: float = 1.2, height: float = 0.6, **kwargs):
        super().__init__(**kwargs)

        self.outer = Ellipse(
            width=width, height=height, color=MITOCHONDRIA_COLOR,
            fill_opacity=0.3, stroke_width=2,
        )

        # Cristae (inner membrane folds)
        self.cristae = VGroup()
        n_cristae = max(2, int(width / 0.3))
        for i in range(n_cristae):
            x = -width / 3 + i * (width * 0.6 / n_cristae)
            crista = Line(
                [x, height * 0.3, 0],
                [x, -height * 0.15, 0],
                stroke_width=1.5, color=RED_B,
            )
            self.cristae.add(crista)

        self.add(self.outer, self.cristae)


class Cell(VGroup):
    """Eukaryotic cell with configurable organelles.

    Parameters
    ----------
    show_nucleus, show_er, show_mitochondria, show_ribosomes : bool
        Toggle organelle visibility.
    """

    def __init__(
        self,
        show_nucleus: bool = True,
        show_er: bool = True,
        show_mitochondria: bool = True,
        show_ribosomes: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)

        # Cell membrane
        self.membrane = Ellipse(
            width=6, height=4, color=MEMBRANE_COLOR,
            fill_opacity=0.05, stroke_width=3,
        )
        self.add(self.membrane)

        if show_nucleus:
            self.nucleus = Nucleus(width=2, height=1.5)
            self.add(self.nucleus)

        if show_mitochondria:
            self.mitochondria = VGroup()
            positions = [RIGHT * 2 + UP * 0.5, RIGHT * 1.5 + DOWN * 1]
            for pos in positions:
                mito = Mitochondrion()
                mito.move_to(pos)
                self.mitochondria.add(mito)
            self.add(self.mitochondria)

        if show_er:
            # Endoplasmic reticulum (simplified wavy lines)
            self.er = VGroup()
            for y_off in [0.3, 0, -0.3]:
                er_line = FunctionGraph(
                    lambda x: 0.15 * np.sin(3 * x) + y_off,
                    x_range=[-1.5, -0.3, 0.05],
                    color=ER_COLOR,
                    stroke_width=2,
                )
                self.er.add(er_line)
            self.er.shift(LEFT * 0.8 + DOWN * 0.3)
            er_label = Text("ER", font_size=10, color=ER_COLOR)
            er_label.next_to(self.er, DOWN, buff=0.05)
            self.add(self.er, er_label)

        if show_ribosomes:
            self.ribosomes = VGroup()
            ribo_positions = [
                LEFT * 1.8 + UP * 1.2,
                LEFT * 2.2 + UP * 0.6,
                LEFT * 0.5 + DOWN * 1.5,
            ]
            for pos in ribo_positions:
                ribo = Dot(radius=0.06, color=RIBOSOME_COLOR).move_to(pos)
                self.ribosomes.add(ribo)
            self.add(self.ribosomes)
