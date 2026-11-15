"""Replaceable note-generation providers (fake offline + optional live)."""

from .base import GenerationError, NoteProvider
from .fake import FakeNoteProvider
from .groq import GroqProvider
from .openai_compatible import OpenAICompatibleProvider

__all__ = [
    "GenerationError",
    "NoteProvider",
    "FakeNoteProvider",
    "GroqProvider",
    "OpenAICompatibleProvider",
]
