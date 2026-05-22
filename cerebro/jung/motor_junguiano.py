"""
Motor Junguiano: clasifica nuevas neuronas contra los arquetipos preinstalados
y asigna el campo arquetipo_vinculado.

Lógica de afinidad:
  - Cada arquetipo tiene un vocabulario semántico asociado (palabras clave).
  - Se cuenta el overlap entre ese vocabulario y el contenido + significante de la neurona.
  - El arquetipo con mayor score gana y se vincula.
  - Si el score máximo es 0 (ningún match), se vincula a "self" por defecto
    (el integrador jungiano de la totalidad).
"""
import glob
import os
from pathlib import Path
from typing import Optional

from cerebro.core.neurona import Neurona


# Vocabulario semántico por arquetipo — configurable / expandible
VOCABULARIO_ARQUETIPOS = {
    "madre": {
        "nutrir", "proteger", "cuidar", "contener", "alimentar",
        "refugio", "hogar", "sostener", "calor", "suave",
        "agua", "tierra", "abrazo", "crecer", "origen",
    },
    "heroe": {
        "superar", "transformar", "vencer", "esfuerzo", "accion",
        "empujar", "agarrar", "lanzar", "golpear", "correr",
        "fuego", "fuerza", "batalla", "desafio", "logro",
        "escalar", "avanzar", "conquistar", "construir",
    },
    "sombra": {
        "conflicto", "tension", "rechazar", "desconocido", "oscuro",
        "miedo", "evitar", "negar", "ocultar", "peligro",
        "destruir", "perder", "caos", "ruptura", "amenaza",
    },
    "self": {
        "integrar", "totalidad", "centro", "equilibrio", "ser",
        "identidad", "unidad", "todo", "sintetizar", "comprender",
        "ver", "observar", "conocer", "pensar", "conectar",
    },
}


class MotorJunguiano:
    def __init__(self, vault_arquetipos: Optional[str] = None):
        """
        vault_arquetipos: ruta a la carpeta de arquetipos .md.
        Si es None usa el vocabulario interno por defecto.
        """
        self.arquetipos_path = Path(vault_arquetipos) if vault_arquetipos else None
        self._cache_arquetipos: dict = {}  # nombre → set de palabras clave

    def _vocabulario_de(self, nombre_arquetipo: str) -> set:
        """Combina el vocabulario interno con el contenido del .md del arquetipo."""
        base = set(VOCABULARIO_ARQUETIPOS.get(nombre_arquetipo, set()))

        if self.arquetipos_path:
            path = self.arquetipos_path / f"{nombre_arquetipo}.md"
            if path.exists():
                try:
                    n = Neurona.load(str(path))
                    palabras = set(
                        w.lower().strip(".,;:!?()[]")
                        for w in (n.post.content or "").split()
                        if len(w) > 3
                    )
                    tags = {str(t).lower() for t in n.post.metadata.get("tags", [])}
                    base |= palabras | tags
                except Exception:
                    pass

        return base

    def _score(self, neurona: Neurona, vocabulario: set) -> int:
        """Cuenta matches entre la neurona y el vocabulario del arquetipo."""
        texto = " ".join([
            neurona.post.metadata.get("significante", ""),
            neurona.post.content or "",
            " ".join(str(t) for t in neurona.post.metadata.get("tags", [])),
        ]).lower()

        palabras_neurona = {w.strip(".,;:!?()[]") for w in texto.split() if len(w) > 2}
        return len(palabras_neurona & vocabulario)

    def clasificar(self, neurona: Neurona) -> str:
        """
        Devuelve el nombre del arquetipo más afín.
        Si no hay match, devuelve "self" (integrador por defecto).
        """
        scores = {}
        for nombre in VOCABULARIO_ARQUETIPOS:
            vocab = self._vocabulario_de(nombre)
            scores[nombre] = self._score(neurona, vocab)

        mejor = max(scores, key=lambda k: scores[k])
        return mejor if scores[mejor] > 0 else "self"

    def vincular(self, neurona: Neurona) -> str:
        """Clasifica la neurona y escribe el campo arquetipo_vinculado en su metadata."""
        arquetipo = self.clasificar(neurona)
        neurona.post.metadata["arquetipo_vinculado"] = f"[[{arquetipo}.md]]"
        return arquetipo
