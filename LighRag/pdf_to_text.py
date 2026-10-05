import re, sys
from pathlib import Path
from pypdf import PdfReader

BASE = Path(__file__).resolve().parent.parent          # the Airbus folder
PDF = BASE / "data" / "AC_A320_0624.pdf"

def extract(out_name, first=1, last=None):
    reader = PdfReader(PDF)
    last = last or len(reader.pages)
    chunks = []
    for i in range(first, last + 1):
        text = (reader.pages[i - 1].extract_text() or "").strip()
        if len(text) < 150 or "HIGHLIGHTS" in text[:400].upper():
            continue                                    # drawings / revision pages
        m = re.search(r"\b(\d{1,2}-\d{1,2}-\d{1,2})\b", text[:400])
        section = m.group(1) if m else "unknown"
        chunks.append(f"[A320 AC | Section {section} | PDF page {i}]\n{text}\n")
    out = BASE / "data" / out_name
    out.write_text("\n".join(chunks), encoding="utf-8")
    print(f"Kept {len(chunks)} pages -> {out}")

if __name__ == "__main__":
    name = sys.argv[1]
    first = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    last = int(sys.argv[3]) if len(sys.argv) > 3 else None
    extract(name, first, last)