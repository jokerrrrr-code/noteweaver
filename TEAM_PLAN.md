# NoteWeaver Four-Member Team Plan

The reader, structured generation, Groq integration, manual-note operations, and
verified save/load are implemented. Supplementary-page rendering/export are also implemented; notebook export cells and
course/release acceptance remain pending. See [current scope](README.md#current-scope),
[the roadmap](ROADMAP.md), and [recorded contribution evidence](docs/EVALUATION.md).
Member numbers identify responsibilities, not a claim that all listed work is complete.

## Shared objective

Demonstrate this workflow in JupyterHub:

> Import a lecture PDF → select an original page and ask a question → generate or manually enter a note → review and edit → insert supplementary pages → export a study PDF.

The first release targets PDFs with selectable text, Chinese and English note content, and stable original-page references. OCR, handwriting recognition, image interpretation, and automatic cross-document topic search are deferred. Agree on formula support; preserve unsupported formulas as source text or report them explicitly rather than silently dropping them.

Repository documentation, code explanations, and presentation instructions must be in English. Chinese sample content remains appropriate for bilingual tests and demonstrations.

## Member 1: PDF reading and page identification

**Responsibility: identify the student's original page and provide its content.**

- Load PDFs, retrieve page counts, and identify source documents.
- Extract text from a selected page and provide a page preview.
- Preserve original-page identity so notes remain traceable after insertion.
- Handle missing files, out-of-range pages, and text extraction failures.
- Supply selected and neighboring page content for member 2's context selection.

Suggested files: `src/noteweaver/pdf_reader.py`, `tests/test_pdf_reader.py`, original PDF fixtures, and reader documentation.

Initial milestone completed: the bilingual three-page fixture, page 2 extraction/preview, and invalid-input checks are implemented. Maintain the reader and its failure behavior as integration evolves.

Acceptance: return the correct original-page content or explicit extraction status for empty/scanned pages, without changing the source file.

## Member 2: Explanation generation and source handling

**Responsibility: turn page content and a student's question into editable structured notes.**

- Select lecture context using the target page, selected text, and question.
- Implement a provider interface and a deterministic offline fake provider.
- Support language, learning level, and explanation styles such as comparison, simple explanation, or step-by-step guidance.
- Return a title, explanation, examples, self-check material, and source pages, distinguishing lecture-based content from supplemental content.
- Validate response shape and reference bounds without claiming this proves factual accuracy.
- Handle missing credentials, timeouts, and malformed responses. Treat lecture text as reference data, not system instructions.

Suggested files: `src/noteweaver/generation.py`, `src/noteweaver/providers/`, `tests/test_generation.py`, and provider configuration documentation.

Initial milestone completed: the fake provider, structured drafts, validation, and live-provider transport are implemented. Reader/project integration and one real English Groq request have been verified. Broader quality and bilingual live evaluation remain ongoing.

Acceptance: return structured notes without modifying PDFs; failures allow retry; credentials never enter project files or Git.

## Member 3: Supplementary-page layout and PDF export

**Responsibility: render readable notes and insert them in the correct positions.**

- Lay out titles, sections, examples, and source references.
- Support Chinese and English, wrapping, long content, and pagination.
- Insert one or more notes after their original page while preserving original content and page order.
- Label note pages with their original-page association, such as “Original page 7, supplementary note 1”.
- Build page maps and bookmarks, exporting to a new file.
- Inspect representative rendered PDF pages as well as running structural/text checks.

Implementation: `src/noteweaver/exporters.py`, `tests/test_pdf_exporter.py`, `examples/export_demo.py`, and `docs/EXPORT.md`.

Initial milestone completed: approved-note insertion, shared page maps, bilingual pagination, bookmarks, and source protection are implemented. See [PDF export](docs/EXPORT.md).

Acceptance: short, long, and multiple notes export correctly; Chinese glyphs render; content is not clipped or overlapping; original pages retain their order.

## Member 4: Public API, editing, persistence, and integration

**Responsibility: connect the modules into a package students can operate.**

- Coordinate shared models and public operations for loading, questions, manual notes, editing, insertion, and export.
- Manage note IDs, draft/approved state, order, deletion, and regeneration.
- Save and reload projects while verifying that the original PDF is unchanged.
- Provide Jupyter examples; interactive controls may follow the basic API.
- Maintain package entry points and integration tests, and coordinate dependencies, builds, and release checks.

Suggested files: `src/noteweaver/project.py`, `src/noteweaver/__init__.py`, project and integration tests, and `examples/`. Coordinate shared changes to `models.py` and `pyproject.toml` rather than replacing them.

Current progress: in-memory manual-note creation, editing, approval, deletion, filtering, and JSON file save/load with source verification are implemented. The [English notebook demo](docs/NOTEBOOK_DEMO.md) now integrates the real PDF reader with editing, approval, and verified save/load. The [Groq generation workflow](docs/GROQ_SETUP.md) also connects the reader and generator to editable drafts and request history. The export API and script are available; next add notebook export cells and complete course/release checks. Reuse ProjectState and the existing model definitions.

Acceptance: the public API supports the complete workflow; content and anchors survive save/reload; manual mode works without AI credentials.

Member 4 coordinates integration, not the completion of everyone else's modules, tests, or documentation.

## Shared interfaces

This table is an overview. Exact fields, defaults, constraints, and serialization are defined in the [data contract](docs/DATA_CONTRACTS.md) and `models.py`. All four members reuse DocumentInfo, NoteSection, ProjectState, and the page-map models.

| Data | Main fields | Producer and consumers |
| --- | --- | --- |
| PageContent | document_id, original_page, text, extraction_status; optional preview_path | Member 1 produces; members 2 and 4 consume |
| NoteRequest | document_id, original_page, question, context_pages, selected_text, language, level, style | Member 4 creates; member 2 consumes |
| GeneratedNote | note_id, original_page, title, sections, source_pages, status | Member 2 or manual workflow produces; members 3 and 4 consume |
| ExportResult | output_path, original_to_output_pages, note_to_output_pages | Member 3 produces; member 4 displays |

- Public page numbers are 1-based and always refer to the original PDF. Convert library-specific indexing at module boundaries.
- Document identity must detect changed source bytes; filenames alone are insufficient.
- Persist the order of multiple notes on the same page and keep each note's rendered pages together.
- Note sections are serializable data, not rendered PDF output from the generator.
- Use common fixtures so members 2, 3, and 4 can develop independently.
- Coordinate shared format changes with affected members instead of creating incompatible alternatives.

## Collaboration and delivery stages

| Stage | Member 1 | Member 2 | Member 3 | Member 4 | Team acceptance |
| --- | --- | --- | --- | --- | --- |
| First | Reading and previews | Fake generation | Fake-note rendering | Shared models and manual API | Manual note can be inserted and exported |
| Second | Real lectures and error handling | Real provider and explanation styles | Long, Chinese, and multiple notes | Editing, persistence, integration | Complete question-to-export workflow |
| Third | Reader tests and documentation | Generation tests and documentation | Visual validation and export documentation | Installation and JupyterHub verification | Release checks and demonstration |

Use individual GitHub accounts and feature branches. Submit meaningful increments regularly and request teammate review; do not wait for an entire module before integrating.

Suggested review pairs: members 1 and 3 check page references and source preservation; members 2 and 4 check formats, editing state, and error handling. Shared-model changes involve all affected members.

Each feature owner maintains the relevant README sections. Member 4 coordinates installation and release work, while tests, documentation, and presentation remain shared responsibilities.

## Planned final team demonstration

- Member 1: about 10 seconds to show the lecture and page selection.
- Member 2: about 15 seconds to ask a question and show structured notes; continue explaining while generation runs.
- Member 4: about 15 seconds to preview, edit, and confirm the note.
- Member 3: about 20 seconds to export and show original pages, supplementary pages, and the page map.

The export segment can use examples/export_demo.py or the public export API. For a runnable demonstration of the current version, use [the evaluator guide](docs/EVALUATION.md).

Rehearse and prepare clearly labeled pre-generated backup notes. Do not describe backup output as live generation. Verify installation in advance and keep installation/version evidence available.
