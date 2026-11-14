from dataclasses import replace
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from noteweaver import (
    ContractError, DocumentInfo, ProjectState, add_manual_note, approve_note,
    create_project, document_id_for_file, load_project, save_project, update_note,
)


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.source = self.root / "lecture.pdf"
        # Synthetic bytes test identity only; this module does not parse PDFs.
        self.source.write_bytes(b"Synthetic lecture bytes for persistence tests")
        document = DocumentInfo(document_id_for_file(self.source), self.source.name, 3)
        self.project = create_project(document, self.source)
        for language, content in (("en", "The next-best alternative."), ("zh-Hant", "機會成本也包括時間。")):
            self.project = add_manual_note(
                self.project, original_page=2, title="Opportunity cost",
                content=content, language=language,
            )
        self.project = approve_note(self.project, self.project.notes[0].note_id)
        self.folder = self.root / "projects"
        self.folder.mkdir()
        self.path = self.folder / "study.json"

    def test_round_trip_preserves_content_identity_order_and_review_state(self):
        before = self.project.to_json()
        result = save_project(self.project, self.path)
        self.assertEqual(result, self.path)
        loaded = load_project(result)
        self.assertEqual(loaded, self.project)
        self.assertEqual([note.status for note in loaded.notes], ["approved", "draft"])
        self.assertEqual([note.original_page for note in loaded.notes], [2, 2])
        self.assertEqual(self.project.to_json(), before)
        text = self.path.read_text(encoding="utf-8")
        self.assertIn("機會成本", text)
        self.assertEqual(json.loads(text)["source_path"], "../lecture.pdf")
        self.assertEqual(json.loads(text)["schema_version"], 1)
        self.assertEqual(set(self.folder.iterdir()), {self.path})

    def test_generated_request_history_and_sections_survive(self):
        fixture = Path(__file__).resolve().parents[1] / "examples/data/project.json"
        data = json.loads(fixture.read_text(encoding="utf-8"))
        identity = self.project.document.document_id
        data["document"]["document_id"] = identity
        data["source_path"] = str(self.source)
        for item in data["requests"] + data["notes"]:
            item["document_id"] = identity
        project = ProjectState.from_dict(data)
        save_project(project, self.path)
        self.assertEqual(load_project(self.path), project)

    def test_relative_source_is_resolved_against_json_directory_not_cwd(self):
        project = replace(self.project, source_path="../lecture.pdf")
        save_project(project, self.path)
        original_cwd = Path.cwd()
        elsewhere = self.root / "unrelated"
        elsewhere.mkdir()
        try:
            os.chdir(elsewhere)
            self.assertEqual(load_project(self.path), self.project)
        finally:
            os.chdir(original_cwd)
        self.assertEqual(project.source_path, "../lecture.pdf")

    def test_loading_absolute_source_path_is_supported(self):
        self.path.write_text(self.project.to_json(), encoding="utf-8")
        self.assertEqual(load_project(self.path), self.project)

    def test_loaded_project_can_be_saved_elsewhere_without_reanchoring(self):
        save_project(self.project, self.path)
        loaded = load_project(self.path)
        other = self.root / "other"
        other.mkdir()
        new_path = other / "copy.json"
        save_project(loaded, new_path)
        self.assertEqual(load_project(new_path), self.project)
        self.assertEqual(json.loads(new_path.read_text())["source_path"], "../lecture.pdf")

    def test_moving_project_folder_with_source_retains_relative_link(self):
        save_project(self.project, self.path)
        with tempfile.TemporaryDirectory() as moved:
            destination = Path(moved) / "bundle"
            shutil.copytree(self.root, destination)
            self.source.unlink()
            loaded = load_project(destination / "projects/study.json")
            self.assertEqual(loaded.notes, self.project.notes)
            self.assertEqual(loaded.source_path, str((destination / "lecture.pdf").resolve()))

    def test_moved_source_can_be_relinked_only_with_matching_fingerprint(self):
        save_project(self.project, self.path)
        before = self.path.read_bytes()
        relocated = self.folder / "renamed.pdf"
        self.source.rename(relocated)
        with self.assertRaises(FileNotFoundError):
            load_project(self.path)
        loaded = load_project(self.path, source_path="renamed.pdf")
        self.assertEqual(loaded.source_path, str(relocated))
        self.assertEqual(loaded.notes, self.project.notes)
        self.assertEqual(load_project(self.path, source_path=relocated), loaded)
        self.assertEqual(self.path.read_bytes(), before)
        relocated.write_bytes(b"Different lecture")
        with self.assertRaisesRegex(ContractError, "source document changed"):
            load_project(self.path, source_path=relocated)

    def test_changed_source_blocks_load_and_save_without_touching_old_json(self):
        save_project(self.project, self.path)
        before = self.path.read_bytes()
        self.source.write_bytes(b"Changed content at the same filename")
        with self.assertRaisesRegex(ContractError, "source document changed"):
            load_project(self.path)
        with self.assertRaisesRegex(ContractError, "source document changed"):
            save_project(self.project, self.path, overwrite=True)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(set(self.folder.iterdir()), {self.path})

    def test_missing_source_blocks_save_without_creating_project(self):
        self.source.unlink()
        with self.assertRaises(FileNotFoundError):
            save_project(self.project, self.path)
        self.assertFalse(self.path.exists())
        self.assertEqual(list(self.folder.iterdir()), [])

    def test_edit_save_and_reopen_retains_draft_after_previous_approval(self):
        save_project(self.project, self.path)
        loaded = load_project(self.path)
        edited = update_note(loaded, loaded.notes[0].note_id, content="Revised explanation")
        with self.assertRaises(FileExistsError):
            save_project(edited, self.path)
        self.assertEqual(load_project(self.path), self.project)
        save_project(edited, self.path, overwrite=True)
        self.assertEqual(load_project(self.path), edited)
        self.assertEqual(load_project(self.path).notes[0].status, "draft")

    def test_invalid_json_encoding_schema_and_fields_are_rejected(self):
        cases = [b"not JSON", b"\xff\xfe", b"[]", b'{"schema_version":1,"schema_version":1}']
        for changes in ({"schema_version": 99}, {"schema_version": "1"}, {"extra": "field"}):
            data = self.project.to_dict()
            data.update(changes)
            cases.append(json.dumps(data).encode())
        missing = self.project.to_dict()
        del missing["schema_version"]
        cases.append(json.dumps(missing).encode())
        nested = self.project.to_dict()
        nested["notes"][0]["original_page"] = 4
        cases.append(json.dumps(nested).encode())
        for payload in cases:
            with self.subTest(payload=payload[:50]):
                self.path.write_bytes(payload)
                with self.assertRaises(ContractError):
                    load_project(self.path)
                self.assertEqual(self.path.read_bytes(), payload)

    def test_missing_project_parent_and_directory_errors_are_explicit(self):
        with self.assertRaises(FileNotFoundError):
            load_project(self.path)
        with self.assertRaises(FileNotFoundError):
            save_project(self.project, self.root / "missing/study.json")
        with self.assertRaises(IsADirectoryError):
            save_project(self.project, self.folder, overwrite=True)
        with self.assertRaises(IsADirectoryError):
            load_project(self.folder)

    def test_source_file_and_hardlink_alias_cannot_be_overwritten(self):
        before = self.source.read_bytes()
        alias = self.root / "alias.json"
        os.link(self.source, alias)
        for path in (self.source, alias, self.folder / "../lecture.pdf"):
            with self.subTest(path=path), self.assertRaises(ContractError):
                save_project(self.project, path, overwrite=True)
        self.assertEqual(self.source.read_bytes(), before)

    def test_symlink_destination_is_rejected_and_load_uses_resolved_file_directory(self):
        save_project(self.project, self.path)
        alias = self.root / "linked.json"
        alias.symlink_to(self.path)
        self.assertEqual(load_project(alias), self.project)
        with self.assertRaises(ContractError):
            save_project(self.project, alias, overwrite=True)
        dangling = self.root / "dangling.json"
        dangling.symlink_to(self.root / "absent.json")
        with self.assertRaises(ContractError):
            save_project(self.project, dangling)

    def test_failed_publication_preserves_existing_file_and_cleans_temporary(self):
        save_project(self.project, self.path)
        before = self.path.read_bytes()
        with patch("noteweaver.persistence.os.replace", side_effect=PermissionError("replace denied")):
            with self.assertRaises(PermissionError):
                save_project(self.project, self.path, overwrite=True)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(set(self.folder.iterdir()), {self.path})

    def test_failed_flush_preserves_existing_file_and_cleans_temporary(self):
        save_project(self.project, self.path)
        before = self.path.read_bytes()
        with patch("noteweaver.persistence.os.fsync", side_effect=OSError("disk failure")):
            with self.assertRaises(OSError):
                save_project(self.project, self.path, overwrite=True)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(set(self.folder.iterdir()), {self.path})

    def test_exclusive_publication_does_not_clobber_a_concurrent_file(self):
        original_link = os.link

        def competing_link(source, destination):
            Path(destination).write_text("Another writer's file", encoding="utf-8")
            original_link(source, destination)

        with patch("noteweaver.persistence.os.link", side_effect=competing_link):
            with self.assertRaises(FileExistsError):
                save_project(self.project, self.path)
        self.assertEqual(self.path.read_text(), "Another writer's file")
        self.assertEqual(set(self.folder.iterdir()), {self.path})

    def test_invalid_arguments_are_rejected(self):
        for path in ("", "  ", None, 4, "bad\0path"):
            with self.subTest(path=path):
                with self.assertRaises(ContractError):
                    save_project(self.project, path)
                with self.assertRaises(ContractError):
                    load_project(path)
        for overwrite in (1, "yes", None):
            with self.subTest(overwrite=overwrite), self.assertRaises(ContractError):
                save_project(self.project, self.path, overwrite=overwrite)
        with self.assertRaises(ContractError):
            save_project({}, self.path)
        save_project(self.project, self.path)
        with self.assertRaises(ContractError):
            load_project(self.path, source_path=" ")


if __name__ == "__main__":
    unittest.main()
