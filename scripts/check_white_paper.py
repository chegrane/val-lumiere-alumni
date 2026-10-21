#!/usr/bin/env python3
"""Mechanical checks of the dataset white paper (docs/dataset/white_paper.md).

A reviewer reads for meaning; this script catches what a reader misses:

1. every numeric citation [n] points to an existing reference, and every
   reference is cited at least once;
2. maths use $...$ or $$...$$ (GitHub does not render \\[ \\] or \\( \\));
3. every defect code of the worked example (section 4) is defined in the
   error model (section 8);
4. the worked example is consistent: each name in a messy record differs
   from the clean record only by the defects annotated in the ground truth;
5. its record identifiers do not leak the answer: none contains the person's
   number, and no two records of one person share an ending.

It cannot check that a citation supports its sentence: that stays a human
review. Usage: python3 scripts/check_white_paper.py [path]  (exit code 1 on errors)
"""

import re
import sys
import unicodedata
from pathlib import Path

DEFAULT = Path(__file__).resolve().parent.parent / "docs" / "dataset" / "white_paper.md"

# [3] or [6, 7] or [12–14], but not a Markdown link [text](url).
CITATION = re.compile(r"\[(\d+(?:\s*[,–-]\s*\d+)*)\](?!\()")
REFERENCE = re.compile(r"^\[(\d+)\] ", re.MULTILINE)
CODE = r"(?:typo|var|fmt|email|rec)\.[a-z_]+"


def section(text, number):
    """The text of section `number` ('## 4. ...'), up to the next '## ' heading."""
    match = re.search(rf"^## {number}\. .*?(?=^## )", text, re.MULTILINE | re.DOTALL)
    return match.group(0) if match else ""


def without_code(text):
    """Remove fenced blocks and `inline code`, where brackets are not citations."""
    text = re.sub(r"^```.*?^```", "", text, flags=re.MULTILINE | re.DOTALL)
    return re.sub(r"`[^`]*`", "", text)


def cited_numbers(body):
    numbers = set()
    for group in CITATION.findall(without_code(body)):
        for part in re.split(r"\s*,\s*", group):
            if re.search(r"[–-]", part):
                low, high = (int(n) for n in re.split(r"\s*[–-]\s*", part))
                numbers.update(range(low, high + 1))
            else:
                numbers.add(int(part))
    return numbers


def check_citations(text):
    body, _, references = text.partition("## References")
    defined = {int(n) for n in REFERENCE.findall(references)}
    cited = cited_numbers(body)
    errors = [f"citation [{n}] has no reference" for n in sorted(cited - defined)]
    errors += [f"reference [{n}] is never cited" for n in sorted(defined - cited)]
    return errors


def check_math(text):
    prose = re.sub(r"^```.*?^```", "", text, flags=re.MULTILINE | re.DOTALL)
    return [f"math delimiter {d} found: use $...$ or $$...$$"
            for d in (r"\[", r"\]", r"\(", r"\)") if d in prose]


def check_codes(text):
    defined = set(re.findall(rf"^\| `({CODE})` \|", section(text, 8), re.MULTILINE))
    used = set(re.findall(rf"\w+:({CODE})", section(text, 4)))
    return [f"defect code {c} (section 4) is not defined in section 8"
            for c in sorted(used - defined)]


# --- The worked example -------------------------------------------------------

def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def fold(s):
    """Accents, case and hyphens removed: what is left must match."""
    return strip_accents(s).lower().replace("-", " ")


def one_transposition(a, b):
    diff = [i for i in range(len(a)) if i < len(b) and a[i] != b[i]]
    return (len(a) == len(b) and len(diff) == 2 and diff[1] == diff[0] + 1
            and a[diff[0]] == b[diff[1]] and a[diff[1]] == b[diff[0]])


def detect(clean, messy):
    """The defect codes that turn `clean` into `messy`, or None if unexplained."""
    codes = set()
    if strip_accents(clean) != clean and strip_accents(messy) == messy:
        codes.add("var.accent_dropped")
    if "-" in clean and "-" not in messy:
        codes.add("var.hyphen")
    if messy != clean and (messy.isupper() or messy.islower()):
        codes.add("var.case")
    a, b = fold(clean), fold(messy)
    if a == b:
        return codes
    if one_transposition(a, b):
        return codes | {"typo.transposition"}
    return None


def detect_full_name(first, last, messy):
    parts = messy.split(" ", 1)
    if len(parts) != 2:
        return None
    for order, extra in (((first, last), set()), ((last, first), {"var.order_swapped"})):
        found = [detect(c, m) for c, m in zip(order, parts)]
        if None not in found:
            return set().union(extra, *found)
    return None


def check_example(text):
    example = section(text, 4)
    clean = re.search(r"record_id: [\w-]+ · \w+, ([^,]+), ([^,]+), \d{4}-\d{2}-\d{2}", example)
    if not clean:
        return ["worked example: registrar_people.csv row not found"]
    first, last = clean.groups()

    # Annotations of the ground-truth table: {record_id: {field: {codes}}}
    annotated = {}
    for record_id, codes in re.findall(r"^\| `[^`]+` \| `(\w[\w-]*)` \| `P\d+` \| (.*) \|$",
                                       example, re.MULTILINE):
        fields = annotated.setdefault(record_id, {})
        for field, code in re.findall(rf"(\w+):({CODE})", codes):
            fields.setdefault(field, set()).add(code)

    rendered = []  # (record_id, field, clean value or None, messy value)
    for line in example.splitlines():
        rid = re.search(r"record_id: ([\w-]+)", line)
        if not rid:
            continue
        rid = rid.group(1)
        if m := re.search(r"\bNom: ([^·`]+?) ·", line):
            rendered.append((rid, "last_name", last, m.group(1)))
        if m := re.search(r"\bPrénom: ([^·`]+?) ·", line):
            rendered.append((rid, "first_name", first, m.group(1)))
        if m := re.search(r"\bNom complet: ([^·`]+)", line):
            rendered.append((rid, "full_name", None, m.group(1).strip()))

    errors = []
    for rid, field, clean_value, messy in rendered:
        found = (detect_full_name(first, last, messy) if field == "full_name"
                 else detect(clean_value, messy))
        given = {c for c in annotated.get(rid, {}).get(field, set())
                 if c.startswith(("typo.", "var."))}
        if found is None:
            errors.append(f"{rid} {field} '{messy}': difference not explained by any defect")
        elif found != given:
            if found - given:
                errors.append(f"{rid} {field} '{messy}': not annotated: {sorted(found - given)}")
            if given - found:
                errors.append(f"{rid} {field} '{messy}': annotated but absent: {sorted(given - found)}")
    if not rendered:
        errors.append("worked example: no messy name found")
    return errors


def check_identifiers(text):
    """A record_id must say nothing about the person behind it."""
    rows = re.findall(r"^\| `[^`]+` \| `([\w-]+)` \| `P(\d+)` \|", section(text, 4), re.MULTILINE)
    errors = [f"record_id {rid} contains the person number {number}"
              for rid, number in rows if number in rid]
    by_person = {}
    for rid, number in rows:
        by_person.setdefault(number, []).append(rid)
    for rids in by_person.values():
        for i, a in enumerate(rids):
            for b in rids[i + 1:]:
                if a[-4:] == b[-4:]:
                    errors.append(f"record_ids {a} and {b} of one person share the ending {a[-4:]}")
    return errors


def check(text):
    return (check_citations(text) + check_math(text) + check_codes(text)
            + check_example(text) + check_identifiers(text))


def main(argv):
    path = Path(argv[1]) if len(argv) > 1 else DEFAULT
    errors = check(path.read_text(encoding="utf-8"))
    for error in errors:
        print(f"{path.name}: {error}")
    print(f"{path.name}: {len(errors)} error(s)" if errors else f"{path.name}: OK")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
