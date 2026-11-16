"""Utilidades compartidas por las etapas del colector. Solo biblioteca estándar."""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RUTA_REGLAS = RAIZ / "docs" / "data" / "reglas.json"
DIR_CONSULTAS = RAIZ / "docs" / "data" / "consultas"
RUTA_INDICE = RAIZ / "docs" / "data" / "indice.json"
DIR_RAW = RAIZ / "data" / "raw"
DIR_MANIFESTS = RAIZ / "manifests"
DIR_LOGS = RAIZ / "logs"

PALABRAS_VACIAS = {"de", "del", "la", "el", "los", "las", "en", "y", "para", "con", "por", "un", "una", "que", "a", "o"}


def cargar_reglas() -> dict:
    return json.loads(RUTA_REGLAS.read_text(encoding="utf-8"))


def normalizar(texto: str) -> str:
    """Minúsculas, sin tildes, espacios simples. Igual que normalizar() en docs/assets/nucleo.js."""
    sin_tildes = unicodedata.normalize("NFD", texto.lower())
    sin_tildes = "".join(c for c in sin_tildes if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", sin_tildes).strip()


def limpiar_tema(crudo: str) -> str:
    """El tema llega de una persona (formulario o issue): se trata como dato no confiable."""
    tema = re.sub(r"^\s*consulta\s*:\s*", "", crudo, flags=re.I)
    tema = re.sub(r"[^0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ \-]", " ", tema)
    tema = re.sub(r"\s+", " ", tema).strip().lower()
    if not 3 <= len(tema) <= 60:
        raise ValueError(f"El tema debe tener entre 3 y 60 caracteres (letras, números, espacios). Recibido: {len(tema)}")
    return tema


def slug(tema: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", normalizar(tema)).strip("-")


def tokens_tema(tema: str) -> list[str]:
    return [t for t in normalizar(tema).split() if t not in PALABRAS_VACIAS and len(t) >= 3]
