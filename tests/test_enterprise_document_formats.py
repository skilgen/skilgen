from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from skilgen.core.document_ingestion import PdfReader
from skilgen.enterprise_skills import generate_enterprise_skill


def _write_pdf(path: Path, text: str) -> None:
    objects = [
        "1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        "2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        "3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 144] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n",
    ]
    stream = f"BT\n/F1 18 Tf\n36 96 Td\n({text}) Tj\nET\n"
    objects.append(f"4 0 obj\n<< /Length {len(stream.encode('latin-1'))} >>\nstream\n{stream}endstream\nendobj\n")
    objects.append("5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")

    header = "%PDF-1.4\n"
    offsets: list[int] = []
    body = ""
    current = len(header.encode("latin-1"))
    for obj in objects:
        offsets.append(current)
        body += obj
        current += len(obj.encode("latin-1"))
    xref_offset = current
    xref = ["xref\n", f"0 {len(objects) + 1}\n", "0000000000 65535 f \n"]
    xref.extend(f"{offset:010d} 00000 n \n" for offset in offsets)
    trailer = (
        "trailer\n"
        f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        "startxref\n"
        f"{xref_offset}\n"
        "%%EOF\n"
    )
    path.write_bytes((header + body + "".join(xref) + trailer).encode("latin-1"))


@unittest.skipUnless(PdfReader is not None, "PDF extraction extras are not installed")
class EnterpriseDocumentFormatTests(unittest.TestCase):
    def test_generate_enterprise_skill_uses_document_extractors(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            pdf_path = root / "runbook.pdf"
            _write_pdf(pdf_path, "Use Jira and Confluence during incidents")
            html_path = root / "guide.html"
            html_path.write_text("<html><body><p>Terraform applies production infrastructure.</p></body></html>", encoding="utf-8")

            payload = generate_enterprise_skill(
                root,
                name="incident operations",
                source_paths=[pdf_path, html_path],
                kind="runbook",
            )

            skill_path = Path(payload["skill_path"])
            skill_text = skill_path.read_text(encoding="utf-8")
            self.assertIn("Use Jira and Confluence during incidents", skill_text)
            self.assertIn("Terraform applies production infrastructure.", skill_text)


if __name__ == "__main__":
    unittest.main()
