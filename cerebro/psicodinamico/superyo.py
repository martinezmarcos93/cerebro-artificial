import yaml
import os
import re
from pathlib import Path

LINK_RE = re.compile(r'\[\[(.+?)\]\]')
_DEFAULT_CONFIG = str(Path(__file__).parent / "superyo_rules.yaml")


def _extraer_significante(valor: str) -> str:
    """Extrae el significante de un enlace [[sig]] o devuelve el valor limpio."""
    m = LINK_RE.match(valor.strip())
    return m.group(1).replace(".md", "") if m else valor.strip()


class Superyo:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = _DEFAULT_CONFIG
        self.reglas = self._cargar_reglas(config_path)

    def _cargar_reglas(self, config_path):
        if not os.path.exists(config_path):
            return []
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data.get("reglas", [])

    def evaluar(self, neurona_origen, neurona_destino):
        """
        Evalúa si el enlace propuesto viola alguna regla.
        Devuelve (aprobado: bool, razon: str).
        """
        sig_origen = neurona_origen.post.metadata.get("significante", "")
        sig_destino = neurona_destino.post.metadata.get("significante", "")

        for regla in self.reglas:
            nombre = regla.get("nombre")
            descripcion = regla.get("descripcion", nombre)

            if nombre == "no_autoenlace":
                if neurona_origen.post.metadata.get("id") == neurona_destino.post.metadata.get("id"):
                    return False, descripcion

            elif nombre == "no_contradiccion_directa":
                diferenciales = neurona_origen.post.metadata.get("significados_diferenciales", [])
                normalizados = {_extraer_significante(d) for d in diferenciales}
                if sig_destino in normalizados:
                    return False, descripcion

            elif nombre == "no_enlace_existente":
                enlace_esperado = f"[[{sig_destino}]]"
                if enlace_esperado in (neurona_origen.post.content or ""):
                    return False, descripcion

        return True, "Enlace permitido."
