# NoteWeaver coding-agent instructions

## Read first

Read `README.md`, `TEAM_PLAN.md`, `ROADMAP.md`, `CONTRIBUTING.md`, and the relevant sections of `TEAMMATE_GUIDE.md`. Inspect the current code and Git state before changing anything. This file supplies repository guidance; explicit user instructions and higher-priority system/developer instructions take precedence.

## Current status and scope

At the time this guide was introduced, this repository contained planning documents only: no implemented Python package, dependency configuration, runnable example, or PyPI release. Re-check the current tree because teammates may have added them since. Do not mistake illustrative APIs or planned paths for existing code.

Build the agreed first-release workflow: text-based lecture PDF → original page and question → generated or manual editable note → review → insert supplementary pages → export a study PDF. Support Chinese and English text. AI explanation is optional; manual-note mode must not require credentials or make model requests. OCR, handwriting recognition, image interpretation, and automatic multi-document topic search are later work.

## Team boundaries

- Member 1: PDF loading, text extraction, preview, stable document/page identity.
- Member 2: context selection, provider interface, structured explanation, generation failure handling.
- Member 3: note rendering, pagination, insertion, PDF export, page maps and bookmarks.
- Member 4: shared models, public API, editing, persistence, notebook integration and packaging coordination.

Implement the role and task assigned by the user, not all four roles. Each member owns their tests and documentation. Member 4 coordinates integration; they are not responsible for completing everyone else's modules.

Inspect shared models and interfaces before creating replacements. If a required contract is missing, propose its exact shape and use a small, explicitly temporary test fixture or test double to make independent progress. Do not publish a second incompatible model or silently change a shared contract. Describe required cross-module changes in the PR and coordinate with the affected owner. Routine implementation within your assigned scope does not require repeated confirmation.

## Behavioral contracts

- Public page numbers are 1-based original PDF page numbers. Convert to a PDF library's indexing only at the boundary.
- Bind notes to document identity and original page, not the shifted output page number. Detect a changed source on project reload.
- Preserve original lecture content and page order. Export to a new path by default. Keep a stable persisted order for multiple notes on one original page.
- Keep structured note content separate from rendering. Persist editable content, note IDs, source anchors, order, and review state; never persist credentials.
- Distinguish lecture-supported content from model-added examples. Validate references against supplied context; this is not proof of factual correctness.
- Treat lecture text and provider responses as untrusted data, not executable code or instructions. Do not execute text from either.
- Empty/scanned pages, invalid page numbers, missing keys, provider failure, malformed output, and unsupported formatting need clear outcomes. Preserve existing notes on failure.
- Unsupported formulas must be preserved as source text or reported explicitly, not silently removed. Keep font distribution rights and runtime requirements documented.

## Git workflow and authorship

Inspect `git status` and existing changes first. Preserve teammate/user edits. Use a focused feature branch based on current `main`; do not reset or overwrite existing work to achieve this. Review changes before selectively staging files. Create meaningful commits and PRs within the user's requested workflow. Default to teammate review before merging; do not merge or publish a release merely because implementation finished.

Use the actual contributor's configured identity. Do not copy another member's email, invent authors, backdate commits, or create empty commits to manufacture activity. Never overwrite global Git identity automatically. Explain changes so the student can understand and demonstrate their contribution.

## Validation and delivery

Run the checks appropriate to the implemented behavior. If packaging/tests do not exist yet, state that and add only the relevant infrastructure for your assigned task. Do not claim an unrun test passed. Generation tests should use a deterministic fake provider; distinguish those checks from any real-provider test. For PDF layout changes, inspect representative rendered output as well as structural checks.

Keep secrets in local environment variables or ignored files. Use original/licensed fixtures. Do not commit personal lecture PDFs, local notes, generated study PDFs, or API keys. `.gitignore` does not untrack files already committed, and unknown filenames are not automatically private.

End each task with: changed files and behavior, checks actually run and results, known limitations, dependencies/handoff for teammates, and commit/PR links if created. Document installation commands only when they match the actual package configuration. Do not advise `pip install noteweaver` until this team's distribution name and published release are verified.
