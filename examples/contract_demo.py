"""Offline contract demonstration, not a PDF or AI implementation."""

from dataclasses import replace
from pathlib import Path

from noteweaver import ExportResult, PageContent, ProjectState, validate_export, validate_generation


def main() -> None:
    data = Path(__file__).parent / "data"
    project = ProjectState.from_json((data / "project.json").read_text(encoding="utf-8"))
    page = PageContent.from_json((data / "page.json").read_text(encoding="utf-8"))
    export = ExportResult.from_json((data / "export.json").read_text(encoding="utf-8"))

    # Simulate the pre-review boundary: real providers must return drafts.
    draft = replace(project.notes[0], status="draft")
    validate_generation(project.document, project.requests[0], (page,), draft)
    validate_export(project, export)
    assert ProjectState.from_json(project.to_json()) == project

    print("Contract v1 validated; no PDF generated and no AI called.")
    print(f"Question: {project.requests[0].question}")
    print(f"Note: {draft.title}")
    print("Example mapping: original pages 1, 2, 3 -> output pages 1, 2, 4")
    print("Approved note-001 -> output page 3; draft note-002 remains unexported.")
    print("Project JSON round trip preserved original anchors, IDs and note order.")


if __name__ == "__main__":
    main()
