# Contributing

[Repository home](README.md) · [Team guide](TEAMMATE_GUIDE.md) · [Responsibilities](TEAM_PLAN.md)

Read [AGENTS.md](AGENTS.md), the [shared contracts](docs/DATA_CONTRACTS.md), and
the relevant [API guide](docs/README.md) before editing. Inspect existing code
and local changes; coordinate shared interfaces instead of creating duplicates.

## Develop and verify

Follow [Quick start](docs/QUICKSTART.md) to create an environment. From the root:

```bash
python -m pip install -e ".[preview,export]"
python -m unittest discover -s tests -v
python -m pip check
```

Run the affected [examples](examples/README.md) as well. Tests are offline by
default; keep live requests separate and explicitly authorized. Use mocked
responses for service error tests. For PDF layout changes, visually inspect
rendered pages in addition to structural checks.

For documentation changes, check relative links and execute changed runnable
commands/snippets. For notebooks, restart and execute in order, then clear
outputs and execution counts before committing. Keep generated verification
artifacts under ignored `generated/`.

## Submit focused changes

1. Use your own GitHub account and configured contributor identity.
2. Create a feature branch from current `main`, preserving local work.
3. Make meaningful commits with the implementation, relevant tests, and English documentation.
4. Inspect `git diff --check`, staged files, and the diff before pushing.
5. Open a PR describing final behavior, actual validation, limitations, and dependencies.
6. Obtain team review before merging; publication is a separate release decision.

Do not rewrite another member's history or manufacture contribution counts.
AI-assisted contributions are welcome; contributors must understand and be able
to demonstrate their changes. Label fake, mocked, and live results accurately.

## Keep the repository usable

- Update the README status table and roadmap when a capability becomes available.
- Link new guides from `docs/README.md` and new examples from `examples/README.md`.
- Keep instructions, comments, and PR descriptions in English. Chinese content is
  appropriate in deliberate bilingual fixtures and examples.
- Store personal inputs in `local_data/` and generated results in `generated/`.
  Do not commit API keys, personal lecture PDFs, local notes, or notebook outputs.
- A `.env` file is ignored, but NoteWeaver does not automatically load it.
  Use an environment variable or the documented hidden key prompt.
- Document fixture licensing. The included font subset is not a general-purpose
  font for arbitrary Chinese note rendering.
- Do not remove `Private :: Do Not Upload` or publish a release until license,
  distribution name, and release readiness are agreed.

For a release, follow [the release checklist](docs/RELEASING.md). The single
version source is `src/noteweaver/_version.py`; keep the changelog synchronized.
