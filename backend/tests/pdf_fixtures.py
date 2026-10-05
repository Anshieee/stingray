"""Deterministic minimal-PDF builders for ingestion tests (test-only, no secrets)."""

from __future__ import annotations


def escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_pdf(pages: list[list[str]]) -> bytes:
    """Build a tiny deterministic PDF; each page holds the given text lines."""
    count = len(pages)
    objects: list[bytes] = [b"<< /Type /Catalog /Pages 2 0 R >>"]
    kids = " ".join(f"{3 + 2 * i} 0 R" for i in range(count))
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {count} >>".encode("ascii"))
    for i, lines in enumerate(pages):
        content_num = 4 + 2 * i
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Contents {content_num} 0 R "
            f"/Resources << /Font << /F1 {3 + 2 * count} 0 R >> >> >>".encode("ascii")
        )
        ops = ["BT /F1 12 Tf 72 720 Td"]
        for position, line in enumerate(lines):
            if position:
                ops.append("0 -14 Td")
            ops.append(f"({escape_pdf_text(line)}) Tj")
        ops.append("ET")
        stream = ("\n".join(ops) + "\n").encode("latin-1")
        objects.append(
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream
        + b"endstream"
    )
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{number} 0 obj\n".encode("ascii") + body + b"\nendobj\n"
    xref_pos = len(out)
    total = len(objects) + 1
    out += f"xref\n0 {total}\n".encode("ascii")
    out += b"0000000000 65535 f \n"
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n".encode("ascii")
    out += f"trailer\n<< /Size {total} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode(
        "ascii"
    )
    return bytes(out)


ATLAS_LINES = [
    "Project Atlas begins on 5 November 2026.",
    "The programme includes 12 research groups.",
    "A compliance review is required before launch.",
]


def build_atlas_pdf() -> bytes:
    """Three-page Atlas fixture, one line per page."""
    return build_pdf([[line] for line in ATLAS_LINES])
