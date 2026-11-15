"""Optional live provider for OpenAI-compatible chat completions.

Requires environment variables (never written to project files):
  NOTEWEAVER_API_KEY   or OPENAI_API_KEY
  NOTEWEAVER_BASE_URL  (default https://api.openai.com/v1)
  NOTEWEAVER_MODEL     (default gpt-4o-mini)

This module is isolated so the rest of the package works offline with the
fake provider. It uses only the Python standard library.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from uuid import uuid4

from noteweaver.models import (
    DocumentInfo,
    GeneratedNote,
    NoteRequest,
    NoteSection,
    PageContent,
)

from .base import GenerationError, NoteProvider


def _api_key() -> str | None:
    return os.environ.get("NOTEWEAVER_API_KEY") or os.environ.get("OPENAI_API_KEY")


def _base_url() -> str:
    return os.environ.get("NOTEWEAVER_BASE_URL", "https://api.openai.com/v1").rstrip("/")


def _model() -> str:
    return os.environ.get("NOTEWEAVER_MODEL", "gpt-4o-mini")


class OpenAICompatibleProvider:
    """Call an OpenAI-compatible chat endpoint and map the reply to GeneratedNote.

    On any network, auth, or parsing failure raises GenerationError. Does not
    write credentials or responses to disk.
    """

    def generate(
        self,
        document: DocumentInfo,
        request: NoteRequest,
        context: tuple[PageContent, ...],
    ) -> GeneratedNote:
        key = _api_key()
        if not key:
            raise GenerationError(
                "no API key in environment (set NOTEWEAVER_API_KEY or OPENAI_API_KEY)"
            )

        context_text = "\n\n".join(
            f"[page {p.original_page}]\n{p.text}" for p in context
        )
        system = (
            "You are a careful study assistant. Reply with a single JSON object only, "
            "no markdown fences. Schema: "
            '{"title": str, "sections": [{"kind": "explanation|steps|comparison|example|quiz|answer", '
            '"content": str, "origin": "lecture|ai"}]}. '
            "Use origin=lecture only for content that paraphrases the supplied lecture text. "
            "Use origin=ai for extra examples, quizzes, or elaborations. "
            "Keep language matching the request. Do not invent page numbers outside the given context."
        )
        user = (
            f"Document: {document.filename} (id={document.document_id})\n"
            f"Target page: {request.original_page}\n"
            f"Language: {request.language}\n"
            f"Level: {request.level}\n"
            f"Style: {request.style}\n"
            f"Question: {request.question}\n"
            f"Selected text: {request.selected_text or '(none)'}\n\n"
            f"Lecture context:\n{context_text}"
        )

        body = {
            "model": _model(),
            "temperature": 0.3,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "response_format": {"type": "json_object"},
        }
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            f"{_base_url()}/chat/completions",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {key}",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            # Do not leak response body or key material.
            raise GenerationError(f"provider HTTP error: {exc.code}") from None
        except urllib.error.URLError as exc:
            raise GenerationError(f"provider network error: {exc.reason}") from None
        except TimeoutError:
            raise GenerationError("provider request timed out") from None
        except json.JSONDecodeError:
            raise GenerationError("provider returned non-JSON response") from None

        try:
            content = payload["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            title = str(parsed["title"]).strip()
            raw_sections = parsed["sections"]
        except (KeyError, TypeError, IndexError, json.JSONDecodeError) as exc:
            raise GenerationError("provider returned malformed note payload") from None

        sections: list[NoteSection] = []
        try:
            for item in raw_sections:
                sections.append(
                    NoteSection(
                        kind=item["kind"],
                        content=str(item["content"]).strip(),
                        origin=item["origin"],
                    )
                )
        except (KeyError, TypeError, ValueError) as exc:
            raise GenerationError("provider sections failed contract checks") from None

        if not sections:
            raise GenerationError("provider returned empty sections")

        source_pages = tuple(sorted({p.original_page for p in context}))
        return GeneratedNote(
            note_id=str(uuid4()),
            document_id=document.document_id,
            original_page=request.original_page,
            title=title,
            sections=tuple(sections),
            source_pages=source_pages,
            request_id=request.request_id,
            language=request.language,
            status="draft",
        )


_: NoteProvider = OpenAICompatibleProvider()
