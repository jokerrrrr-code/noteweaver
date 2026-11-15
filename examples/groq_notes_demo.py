"""Generate a draft from a real PDF, then save a verified project JSON.

Live: python examples/groq_notes_demo.py
Offline test double: python examples/groq_notes_demo.py --offline
"""
from argparse import ArgumentParser
from getpass import getpass
import os
from pathlib import Path
import sys
import tempfile

from noteweaver import (
    ContractError, FakeNoteProvider, GenerationError, GroqProvider,
    create_project, generate_note, load_project, save_project,
)
from noteweaver.pdf_reader import PDFReader


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", type=Path, default=ROOT / "examples/data/sample_lecture_3p.pdf")
    parser.add_argument("--page", type=int, default=2)
    parser.add_argument("--question", default="Why can a free choice still have an opportunity cost?")
    parser.add_argument("--language", default="en")
    parser.add_argument("--offline", action="store_true", help="Use fixed fake content without an API call")
    args = parser.parse_args()
    try:
        source = args.source.resolve()
        reader = PDFReader(render_preview=False)
        project = create_project(reader.inspect(source), source)
        if args.offline:
            provider = FakeNoteProvider()
            print("OFFLINE DEMO: fixed test content, not a real AI answer.")
        else:
            key = None
            if not os.environ.get("GROQ_API_KEY"):
                if not sys.stdin.isatty():
                    raise GenerationError("Set GROQ_API_KEY for live generation, or pass --offline.")
                key = getpass("Enter your Groq API key (hidden): ")
                if not key.strip():
                    raise GenerationError("No key entered. No request was sent.")
            provider = GroqProvider(api_key=key)
            print("Sending the selected page text and question to Groq. Your account limits apply.")
        print("Generating a draft...")
        project = generate_note(project, original_page=args.page, question=args.question,
                                language=args.language, style="example", provider=provider)
        note = project.notes[-1]
        print(f"\n{note.title}\nStatus: {note.status} | Original page: {note.original_page}")
        for section in note.sections:
            print(f"\n[{section.origin} / {section.kind}]\n{section.content}")
        output = ROOT / "generated/groq-demo"
        output.mkdir(parents=True, exist_ok=True)
        run = Path(tempfile.mkdtemp(prefix="run-", dir=output))
        saved = save_project(project, run / "study.json")
        assert load_project(saved) == project
        print(f"\nSaved and verified: {saved}")
        print("Draft only: review before approval. No study PDF was exported.")
        return 0
    except (ContractError, GenerationError, OSError) as error:
        print(f"Could not generate/save the note: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
