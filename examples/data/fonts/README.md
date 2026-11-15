# Bilingual fixture font

`NoteWeaverDemo-Regular.ttf` is a renamed, weight-400 subset of Noto Sans TC.
It contains only the glyphs used by `examples/build_sample_pdf.py`; it is not a
complete font for arbitrary user notes. The sample PDF embeds this font so its
Chinese glyphs do not depend on fonts installed on the reader's computer.

- Upstream: https://github.com/google/fonts/tree/main/ofl/notosanstc
- Source: https://raw.githubusercontent.com/google/fonts/main/ofl/notosanstc/NotoSansTC%5Bwght%5D.ttf
- Source SHA-256: `864727d210d54f2537bbe23b3a839436c3992af72de9322af5270897246bd44f`
- License: SIL Open Font License 1.1, reproduced in `OFL.txt`.
- Original copyright and license name records are retained in the subset.
- Derivative family name: NoteWeaver Demo; PostScript name: NoteWeaverDemo-Regular.

From the repository root, rebuild the PDF offline with the bundled subset:

```bash
python -m pip install reportlab fonttools
python examples/build_sample_pdf.py
```

To recreate the subset as well, download the upstream source, verify its hash,
and run:

```bash
python examples/build_sample_pdf.py --source-font /path/to/NotoSansTC.ttf
```

The committed fixture was generated with ReportLab 5.1.0 and fontTools 4.68.0.
The generator uses fixed PDF metadata timestamps. Dependency versions may still
change PDF bytes. These tools are development-only dependencies; reading PDFs
and running the tests do not require them.
