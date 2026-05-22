"""
Indexador: escanea el vault completo y construye el grafo de conocimiento con networkx.
También provee búsqueda keyword para la recuperación RAG.
"""
import re
from pathlib import Path

import networkx as nx

from cerebro.core.neurona import Neurona

LINK_RE = re.compile(r'\[\[(.+?)\]\]')


class Indexador:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.grafo: nx.DiGraph = nx.DiGraph()
        self._neuronas: dict = {}  # significante → Neurona

    def indexar(self) -> nx.DiGraph:
        """Escanea vault completo (incluye arquetipos en subdirectorios) y construye el grafo."""
        self.grafo.clear()
        self._neuronas.clear()

        for path in self.vault_path.rglob("*.md"):
            try:
                n = Neurona.load(str(path))
                sig = n.post.metadata.get("significante") or path.stem
                self._neuronas[sig] = n
                self.grafo.add_node(sig, **self._atributos_nodo(n))
            except Exception:
                pass

        for sig, n in self._neuronas.items():
            self._agregar_edges(sig, n)

        return self.grafo

    def _atributos_nodo(self, n: Neurona) -> dict:
        return {
            "tipo": n.post.metadata.get("tipo", ""),
            "etapa_creacion": n.post.metadata.get("etapa_creacion", ""),
            "estado_energetico": float(n.post.metadata.get("estado_energetico", 0)),
            "tags": n.post.metadata.get("tags", []),
            "contenido": n.post.content or "",
        }

    def _agregar_edges(self, sig: str, n: Neurona):
        for link in LINK_RE.findall(n.post.content or ""):
            destino = link.replace(".md", "")
            if destino in self._neuronas:
                self.grafo.add_edge(sig, destino, tipo="enlace")

        for diff in n.post.metadata.get("significados_diferenciales", []):
            m = LINK_RE.search(str(diff))
            destino = m.group(1).replace(".md", "") if m else str(diff).strip()
            if destino in self._neuronas:
                self.grafo.add_edge(sig, destino, tipo="diferencial")

        relaciones = n.post.metadata.get("relaciones", {})
        if isinstance(relaciones, dict):
            for dest in relaciones.get("es_un", []):
                m = LINK_RE.search(str(dest))
                destino = m.group(1) if m else str(dest).strip()
                if destino in self._neuronas:
                    self.grafo.add_edge(sig, destino, tipo="es_un")
            for dest in relaciones.get("tiene", []):
                m = LINK_RE.search(str(dest))
                destino = m.group(1) if m else str(dest).strip()
                if destino in self._neuronas:
                    self.grafo.add_edge(sig, destino, tipo="tiene")

    def buscar(self, query: str, max_resultados: int = 5) -> list:
        """Recuperación keyword multi-término. Devuelve lista de Neurona por relevancia."""
        if not self._neuronas:
            return []
        terminos = query.lower().split()
        resultados = []
        for sig, n in self._neuronas.items():
            texto = " ".join([
                sig,
                n.post.content or "",
                " ".join(str(t) for t in n.post.metadata.get("tags", [])),
            ]).lower()
            score = sum(texto.count(t) for t in terminos)
            if score > 0:
                resultados.append((n, score))
        resultados.sort(key=lambda x: x[1], reverse=True)
        return [n for n, _ in resultados[:max_resultados]]

    def get_neurona(self, significante: str):
        return self._neuronas.get(significante)

    @property
    def total_neuronas(self) -> int:
        return len(self._neuronas)
