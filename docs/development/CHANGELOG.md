# Changelog

## 0.1.0 — Unreleased

First functional beta release candidate. This version has not been uploaded to PyPI.
The earlier `0.0.1.dev0` version was used for checkout-based development tests.

- License original project code and documentation under AGPL-3.0-only, with
  third-party notices retained.
- Read text-based lecture PDFs and preview original pages.
- Create, edit, review, approve, filter, and delete page-linked notes.
- Generate structured drafts with configurable OpenAI-compatible providers,
  including Groq and OpenRouter; keep manual and fake-provider modes API-free.
- Save and reload project JSON with source fingerprint verification.
- Export approved supplementary notes after their original PDF pages, with
  English/Chinese text, pagination, bookmarks, and page maps.
- Provide English script and notebook examples and school JupyterHub evidence.
- Validate built distributions on Python 3.10–3.14 in GitHub Actions and support
  manual PyPI Trusted Publishing from `main`.

Scanned PDFs/OCR, handwriting, rich Markdown/LaTeX rendering, and automatic
multi-document topic search are outside this release. Live AI requires a
user-supplied provider key, network access, and available provider quota.
