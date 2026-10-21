"""The white paper's mechanical checks (scripts/check_white_paper.py).

No database needed. The first test checks the real document; the others
prove that the checker catches each kind of error, by breaking a copy.
"""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "docs" / "dataset" / "white_paper.md"

spec = importlib.util.spec_from_file_location("check_white_paper", ROOT / "scripts" / "check_white_paper.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

TEXT = PAPER.read_text(encoding="utf-8")


def broken(old, new):
    """A copy of the paper with one change (everywhere it occurs); the change must apply."""
    assert old in TEXT, f"test setup: {old!r} not in the paper"
    return checker.check(TEXT.replace(old, new))


def test_white_paper_passes():
    assert checker.check(TEXT) == []


def test_citation_without_reference():
    assert "citation [99] has no reference" in broken("[12, 13, 14]", "[12, 13, 14, 99]")


def test_reference_never_cited():
    errors = broken("Levenshtein [24]", "Levenshtein")
    assert "reference [24] is never cited" in errors


def test_latex_brackets_refused():
    errors = broken("$$\n\\text{Precision}", "\\[\n\\text{Precision}")
    assert any("\\[" in e for e in errors)


def test_undefined_defect_code():
    errors = broken("`phone:fmt.phone`", "`phone:fmt.telephone`")
    assert "defect code fmt.telephone (section 4) is not defined in section 8" in errors


def test_missing_annotation():
    """The v0.3 error: the newsletter name lost its accent, but nothing said so."""
    errors = broken("; `full_name:var.accent_dropped`", "")
    assert any("NL2019-B8421F full_name" in e and "var.accent_dropped" in e for e in errors)


def test_annotation_without_defect():
    errors = broken("Nom: Trembaly", "Nom: Tremblay")
    assert any("annotated but absent: ['typo.transposition']" in e for e in errors)


def test_record_id_leaks_the_person():
    """The v0.4 draft error: RP000123 and RD000123 both pointed at P000123."""
    errors = broken("RP-7F3A91", "RP000123")
    assert "record_id RP000123 contains the person number 000123" in errors
    errors = broken("RD-C42E08", "RD-C4F3A91")
    assert any("share the ending 3A91" in e for e in errors)


def test_unexplained_difference():
    errors = broken("Nom: Trembaly", "Nom: Tremblett")
    assert any("not explained by any defect" in e for e in errors)
