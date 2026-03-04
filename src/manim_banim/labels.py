"""Smart labeling utilities for biology diagrams."""

from manim import *

__all__ = ["BioLabel", "LeaderLine", "AnnotationBox"]


class BioLabel(VGroup):
    """A label with optional background and leader line to a target.

    Parameters
    ----------
    text : str
        Label text.
    target : Mobject or None
        Object to point the leader line at.
    direction : np.ndarray
        Direction to place label relative to target.
    font_size : int
        Font size.
    color : ManimColor
        Text color.
    """

    def __init__(
        self,
        text: str,
        target: "Mobject | None" = None,
        direction=UP,
        font_size: int = 20,
        color=WHITE,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.text_mob = Text(text, font_size=font_size, color=color)

        # Background
        bg = SurroundingRectangle(
            self.text_mob, color=color, fill_opacity=0.1, buff=0.1, corner_radius=0.05,
        )
        self.add(bg, self.text_mob)

        if target is not None:
            self.next_to(target, direction, buff=0.5)
            self.leader = Line(
                self.text_mob.get_edge_center(-direction),
                target.get_edge_center(direction),
                stroke_width=1.5,
                color=GREY_B,
            )
            self.add(self.leader)


class LeaderLine(VGroup):
    """A line from a label to a target with an optional elbow.

    Parameters
    ----------
    start : Mobject
        Label or start point.
    end : Mobject
        Target to point at.
    elbow : bool
        If True, use an L-shaped line.
    """

    def __init__(
        self,
        start: "Mobject",
        end: "Mobject",
        elbow: bool = True,
        color=GREY_B,
        **kwargs,
    ):
        super().__init__(**kwargs)

        s = start.get_center() if hasattr(start, "get_center") else np.array(start)
        e = end.get_center() if hasattr(end, "get_center") else np.array(end)

        if elbow:
            mid = np.array([s[0], e[1], 0])
            self.line = VGroup(
                Line(s, mid, stroke_width=1.5, color=color),
                Line(mid, e, stroke_width=1.5, color=color),
            )
        else:
            self.line = Line(s, e, stroke_width=1.5, color=color)

        # Small dot at endpoint
        self.dot = Dot(e, radius=0.03, color=color)
        self.add(self.line, self.dot)


class AnnotationBox(VGroup):
    """A boxed annotation with text, useful for callouts.

    Parameters
    ----------
    text : str
        Annotation content.
    width : float
        Box width.
    color : ManimColor
        Border and text color.
    """

    def __init__(
        self,
        text: str,
        width: float = 3,
        color=YELLOW,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.text_mob = Text(text, font_size=16, color=color)
        self.text_mob.width = min(self.text_mob.width, width - 0.3)

        self.box = SurroundingRectangle(
            self.text_mob, color=color, fill_opacity=0.05, buff=0.15, corner_radius=0.08,
        )
        self.add(self.box, self.text_mob)
