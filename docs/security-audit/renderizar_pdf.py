"""Rasteriza o PDF da auditoria para inspeção visual com pypdfium2."""

from __future__ import annotations

from pathlib import Path

import pypdfium2 as pdfium


ROOT = Path(__file__).resolve().parent
PDF_PATH = ROOT / "relatorio-auditoria-seguranca.pdf"
OUTPUT_DIR = ROOT.parents[1] / "tmp" / "pdfs" / "security-audit"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for stale in OUTPUT_DIR.glob("pagina-*.png"):
        stale.unlink()
    document = pdfium.PdfDocument(PDF_PATH)
    for index in range(len(document)):
        page = document[index]
        bitmap = page.render(scale=1.8)
        image = bitmap.to_pil()
        output = OUTPUT_DIR / f"pagina-{index + 1:02d}.png"
        image.save(output)
        print(output)


if __name__ == "__main__":
    main()
