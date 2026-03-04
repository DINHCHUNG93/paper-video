"""Biology-standard color palette following textbook conventions."""

from manim import ManimColor

# --- Nucleotide bases ---
ADENINE_COLOR = ManimColor("#FF6B6B")
THYMINE_COLOR = ManimColor("#4ECDC4")
GUANINE_COLOR = ManimColor("#45B7D1")
CYTOSINE_COLOR = ManimColor("#96CEB4")
URACIL_COLOR = ManimColor("#FFEAA7")

BASE_COLORS = {
    "A": ADENINE_COLOR,
    "T": THYMINE_COLOR,
    "G": GUANINE_COLOR,
    "C": CYTOSINE_COLOR,
    "U": URACIL_COLOR,
}

# --- Structural ---
PHOSPHATE_COLOR = ManimColor("#FF8C42")
SUGAR_COLOR = ManimColor("#FFD166")
BACKBONE_COLOR = ManimColor("#6C757D")

# --- Amino acid property types ---
AA_NONPOLAR_COLOR = ManimColor("#E8927C")
AA_POLAR_COLOR = ManimColor("#7EC8E3")
AA_POSITIVE_COLOR = ManimColor("#5B8DEF")
AA_NEGATIVE_COLOR = ManimColor("#EF5B5B")

AA_TYPE_COLORS = {
    "nonpolar": AA_NONPOLAR_COLOR,
    "polar": AA_POLAR_COLOR,
    "positive": AA_POSITIVE_COLOR,
    "negative": AA_NEGATIVE_COLOR,
}

# --- Organelles ---
MEMBRANE_COLOR = ManimColor("#2E86AB")
NUCLEUS_COLOR = ManimColor("#7B2D8E")
MITOCHONDRIA_COLOR = ManimColor("#D32F2F")
ER_COLOR = ManimColor("#388E3C")
RIBOSOME_COLOR = ManimColor("#7B1FA2")
GOLGI_COLOR = ManimColor("#F57C00")

# --- Processes ---
REPLICATION_COLOR = ManimColor("#1E88E5")
TRANSCRIPTION_COLOR = ManimColor("#43A047")
TRANSLATION_COLOR = ManimColor("#E53935")

# Convenience dict for all biology colors
BIO_COLORS = {
    "adenine": ADENINE_COLOR,
    "thymine": THYMINE_COLOR,
    "guanine": GUANINE_COLOR,
    "cytosine": CYTOSINE_COLOR,
    "uracil": URACIL_COLOR,
    "phosphate": PHOSPHATE_COLOR,
    "sugar": SUGAR_COLOR,
    "backbone": BACKBONE_COLOR,
    "nonpolar": AA_NONPOLAR_COLOR,
    "polar": AA_POLAR_COLOR,
    "positive": AA_POSITIVE_COLOR,
    "negative": AA_NEGATIVE_COLOR,
    "membrane": MEMBRANE_COLOR,
    "nucleus": NUCLEUS_COLOR,
    "mitochondria": MITOCHONDRIA_COLOR,
    "er": ER_COLOR,
    "ribosome": RIBOSOME_COLOR,
    "golgi": GOLGI_COLOR,
    "replication": REPLICATION_COLOR,
    "transcription": TRANSCRIPTION_COLOR,
    "translation": TRANSLATION_COLOR,
}
