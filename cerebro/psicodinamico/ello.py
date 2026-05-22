import glob
import os
import re

from cerebro.core.neurona import Neurona

LINK_RE = re.compile(r'\[\[.+?\]\]')


class Ello:
    def __init__(self, cerebro):
        self.cerebro = cerebro

    def _grado(self, neurona) -> int:
        """Cuenta links activos como proxy de integración en la red."""
        enlaces_cuerpo = len(LINK_RE.findall(neurona.post.content or ""))
        enlaces_meta = len(neurona.post.metadata.get("significados_diferenciales", []))
        return enlaces_cuerpo + enlaces_meta

    def proponer_enlace(self, neurona_origen):
        """
        Propone el destino con mayor score combinado: energía + novedad.
        La novedad favorece neuronas aún no integradas en la red.
        """
        archivos = glob.glob(os.path.join(self.cerebro.vault_path, "*.md"))
        origen_path = os.path.abspath(neurona_origen.filepath or "")
        candidatos = []

        for path in archivos:
            if os.path.abspath(path) == origen_path:
                continue
            try:
                n = Neurona.load(path)
                energia = float(n.post.metadata.get("estado_energetico", 0))
                novedad = 1.0 / (1.0 + self._grado(n))
                score = energia + novedad
                candidatos.append((n, score))
            except Exception:
                pass

        if not candidatos:
            return None

        candidatos.sort(key=lambda x: x[1], reverse=True)
        return candidatos[0][0]
