# Third-party notices

NoteWeaver's own license decision is recorded in [release preparation](docs/RELEASING.md).
Third-party works retain their own licenses. Dependencies are installed separately
by pip; their code and license texts are not copied into the NoteWeaver wheel.

| Component | Use | License information |
| --- | --- | --- |
| pypdf | PDF reading | BSD-3-Clause in the inspected 7.1.0 distribution |
| PyMuPDF / MuPDF | Optional `export` extra | GNU AGPL v3 or a separate Artifex commercial license; no commercial license is supplied by this project |
| pypdfium2 / PDFium | Optional `preview` extra | pypdfium2 identifies BSD-3-Clause / Apache-2.0 plus dependency licenses; preserve the notices supplied with its binary distribution |
| Pillow | Optional preview image handling | MIT-CMU in the inspected 13.0.0 distribution; consult the installed distribution for bundled component notices |
| NoteWeaver Demo font subset | Bundled sample PDF and fixture generator | SIL Open Font License 1.1; derived from Noto Sans TC, with original notices retained |

The font subset, its provenance, and the full OFL text are included in the source
distribution at `examples/data/fonts/`. The subset is embedded in the sample PDF.
It is not distributed as a general-purpose font for arbitrary lecture notes.
The exporter uses the CJK fallback supplied by MuPDF, not this small sample subset.

Installing an optional dependency does not replace its license with NoteWeaver's
license. In particular, the exporter must be used and distributed consistently
with PyMuPDF/MuPDF's AGPL terms unless separately licensed from Artifex. Preserve
upstream notices and applicable PDF producer metadata. Dependencies and their
bundled components may change between versions; inspect the exact distributions
used for each release. The summary above is not their complete license text.

Sources:

- [PyMuPDF licensing](https://pymupdf.readthedocs.io/en/latest/about.html#license-and-copyright)
- [Artifex licensing options](https://pymupdf.io/licensing)
- [pypdf license](https://github.com/py-pdf/pypdf/blob/main/LICENSE)
- [pypdfium2 licensing](https://github.com/pypdfium2-team/pypdfium2#licensing)
- [Pillow license](https://github.com/python-pillow/Pillow/blob/main/LICENSE)
- [Bundled font provenance](examples/data/fonts/README.md) and [OFL text](examples/data/fonts/OFL.txt)
