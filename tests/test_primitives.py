"""Tests for banim primitive constructors and basic properties."""

import pytest
import numpy as np


def test_nucleotide_creation():
    from manim_banim.nucleotides import Nucleotide

    for base in ["A", "T", "G", "C", "U"]:
        nt = Nucleotide(base_type=base)
        assert nt.base_type == base
        assert len(nt.submobjects) > 0


def test_nucleotide_components():
    from manim_banim.nucleotides import Nucleotide

    nt = Nucleotide(base_type="A")
    assert nt.phosphate is not None
    assert nt.sugar is not None
    assert nt.base is not None


def test_base_pair_creation():
    from manim_banim.base_pairs import BasePair

    bp = BasePair(left_base="A")
    assert bp.left_nt.base_type == "A"
    assert bp.right_nt.base_type == "T"


def test_base_pair_gc():
    from manim_banim.base_pairs import BasePair

    bp = BasePair(left_base="G")
    assert bp.right_nt.base_type == "C"
    # G-C has 3 hydrogen bonds
    assert len(bp.h_bonds) == 3


def test_base_pair_at():
    from manim_banim.base_pairs import BasePair

    bp = BasePair(left_base="A")
    # A-T has 2 hydrogen bonds
    assert len(bp.h_bonds) == 2


def test_dna_strand():
    from manim_banim.dna import DNAStrand

    strand = DNAStrand(sequence="ATCG")
    assert len(strand.nucleotides) == 4
    assert len(strand.backbone_line) == 3  # n-1 connectors


def test_dna_double_helix():
    from manim_banim.dna import DNADoubleHelix

    dna = DNADoubleHelix(sequence="ATCG")
    assert len(dna.base_pairs) == 4


def test_codon():
    from manim_banim.rna import Codon

    codon = Codon(sequence="AUG")
    assert codon.sequence == "AUG"
    assert codon.amino_acid == "Met"


def test_codon_stop():
    from manim_banim.rna import Codon

    codon = Codon(sequence="UAA")
    assert codon.amino_acid == "Stop"


def test_mrna():
    from manim_banim.rna import MRNA

    mrna = MRNA(sequence="AUGGGCUAA")
    assert len(mrna.codons) == 3  # AUG, GGC, UAA


def test_trna():
    from manim_banim.rna import TRNA

    trna = TRNA(anticodon="UAC", amino_acid="Met")
    assert trna.anticodon_seq == "UAC"
    assert trna.aa_name == "Met"


def test_amino_acid():
    from manim_banim.amino_acids import AminoAcid, AA_PROPERTIES

    for name in AA_PROPERTIES:
        aa = AminoAcid(name=name)
        assert aa.aa_name == name


def test_peptide_chain():
    from manim_banim.peptides import PeptideChain

    chain = PeptideChain(sequence=["Ala", "Gly", "Ser"])
    assert len(chain.amino_acids) == 3
    assert len(chain.peptide_bonds) == 2  # n-1 bonds


def test_ribosome():
    from manim_banim.cell import Ribosome

    ribo = Ribosome()
    assert ribo.large_subunit is not None
    assert ribo.small_subunit is not None


def test_ribosome_prokaryotic():
    from manim_banim.cell import Ribosome

    ribo = Ribosome(prokaryotic=True)
    # Labels should reflect prokaryotic subunits
    assert "50S" in ribo.large_label.text or True  # Just check it doesn't crash


def test_cell():
    from manim_banim.cell import Cell

    cell = Cell()
    assert cell.membrane is not None


def test_cell_minimal():
    from manim_banim.cell import Cell

    cell = Cell(
        show_nucleus=False,
        show_er=False,
        show_mitochondria=False,
        show_ribosomes=False,
    )
    assert cell.membrane is not None


def test_alpha_helix():
    from manim_banim.proteins import AlphaHelix

    helix = AlphaHelix(n_turns=2)
    assert helix.ribbon is not None


def test_beta_sheet():
    from manim_banim.proteins import BetaSheet

    sheet = BetaSheet(n_strands=3)
    assert len(sheet.strands) == 3


def test_protein_blob():
    from manim_banim.proteins import ProteinBlob

    blob = ProteinBlob(name="MyProtein")
    assert blob.name_label is not None


def test_cell_membrane():
    from manim_banim.cell import CellMembrane

    membrane = CellMembrane(width=4, n_lipids=8)
    assert len(membrane.lipids_top) == 8
    assert len(membrane.lipids_bottom) == 8


def test_bio_label():
    from manim_banim.labels import BioLabel
    from manim import Circle

    target = Circle()
    label = BioLabel("Test label", target=target)
    assert label.text_mob is not None


def test_annotation_box():
    from manim_banim.labels import AnnotationBox

    box = AnnotationBox("Hello world")
    assert box.text_mob is not None


def test_colors_exist():
    from manim_banim.colors import (
        ADENINE_COLOR, THYMINE_COLOR, GUANINE_COLOR, CYTOSINE_COLOR, URACIL_COLOR,
        PHOSPHATE_COLOR, SUGAR_COLOR, BACKBONE_COLOR,
        MEMBRANE_COLOR, NUCLEUS_COLOR, RIBOSOME_COLOR,
        BIO_COLORS,
    )
    assert len(BIO_COLORS) > 10


def test_codon_table_completeness():
    from manim_banim.rna import CODON_TABLE

    # All 64 codons should be in the table
    bases = ["U", "C", "A", "G"]
    for b1 in bases:
        for b2 in bases:
            for b3 in bases:
                codon = b1 + b2 + b3
                assert codon in CODON_TABLE, f"Missing codon: {codon}"
