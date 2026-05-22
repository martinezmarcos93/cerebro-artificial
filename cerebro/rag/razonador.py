"""
Razonador: consultas lógicas sobre el grafo de conocimiento (networkx).
Provee es_un, tiene, vecinos, camino y expansión de contexto para el RAG.
"""
from typing import List, Optional

import networkx as nx


class Razonador:
    def __init__(self, grafo: nx.DiGraph):
        self.grafo = grafo

    def es_un(self, concepto: str, transitivo: bool = True) -> List[str]:
        """Supertipos de concepto siguiendo la cadena es_un."""
        if concepto not in self.grafo:
            return []
        supertipos, cola, visitados = [], [concepto], set()
        while cola:
            actual = cola.pop()
            if actual in visitados:
                continue
            visitados.add(actual)
            for _, dest, datos in self.grafo.out_edges(actual, data=True):
                if datos.get("tipo") == "es_un" and dest not in visitados:
                    supertipos.append(dest)
                    if transitivo:
                        cola.append(dest)
        return supertipos

    def tiene(self, concepto: str) -> List[str]:
        """Propiedades de concepto (relación tiene)."""
        if concepto not in self.grafo:
            return []
        return [
            dest for _, dest, d in self.grafo.out_edges(concepto, data=True)
            if d.get("tipo") == "tiene"
        ]

    def vecinos(self, concepto: str, n_hops: int = 1) -> List[str]:
        """Nodos alcanzables en n saltos (ignora dirección de los edges)."""
        if concepto not in self.grafo:
            return []
        try:
            sub = nx.ego_graph(self.grafo.to_undirected(), concepto, radius=n_hops)
            return [n for n in sub.nodes if n != concepto]
        except Exception:
            return []

    def camino(self, origen: str, destino: str) -> Optional[List[str]]:
        """Camino más corto entre dos conceptos, o None si no existe."""
        try:
            return nx.shortest_path(self.grafo, origen, destino)
        except Exception:
            return None

    def conceptos_con_conflicto(self) -> List[str]:
        return [n for n, d in self.grafo.nodes(data=True) if d.get("tipo") == "conflicto"]

    def expandir_contexto(self, significantes: List[str], n_hops: int = 1) -> List[str]:
        """Amplía una lista de conceptos con sus vecinos para enriquecer el contexto RAG."""
        expandidos: set = set(significantes)
        for sig in significantes:
            expandidos.update(self.vecinos(sig, n_hops))
        return list(expandidos)
