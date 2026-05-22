"""
ComunicadorRAG: pipeline completo de recuperación + razonamiento + respuesta.

Funciona en dos modos:
  - Con LLM (Ollama u otro callable): genera texto en lenguaje natural.
  - Sin LLM: devuelve los fragmentos recuperados con formato legible.

El prompt garantiza que el LLM use solo el conocimiento interno del cerebro.
"""
from cerebro.rag.razonador import Razonador


PROMPT_SISTEMA = (
    "Eres la voz de este cerebro artificial. "
    "Basa tu respuesta única y exclusivamente en los fragmentos recuperados que se te proveen. "
    "No uses conocimiento externo. "
    "Si el cerebro no sabe algo, di explícitamente: "
    "'Este cerebro no tiene conocimiento sobre eso aún.'"
)


class ComunicadorRAG:
    def __init__(self, indexador, razonador: Razonador, llm=None):
        self.indexador = indexador
        self.razonador = razonador
        self.llm = llm  # callable(prompt: str) -> str, o None

    def consultar(self, pregunta: str, n_fragmentos: int = 5, n_hops: int = 1) -> str:
        """Pipeline: pregunta → recuperación → expansión → (LLM o fragmentos)."""
        if not self.indexador._neuronas:
            self.indexador.indexar()
            self.razonador = Razonador(self.indexador.grafo)

        neuronas_base = self.indexador.buscar(pregunta, max_resultados=n_fragmentos)
        if not neuronas_base:
            return "Este cerebro no tiene conocimiento sobre eso aún."

        sigs_base = [n.post.metadata.get("significante", "") for n in neuronas_base]
        expandidos = self.razonador.expandir_contexto(sigs_base, n_hops=n_hops)

        fragmentos = []
        for sig in expandidos:
            n = self.indexador.get_neurona(sig)
            if n and n.post.content:
                tipo = n.post.metadata.get("tipo", "?")
                fragmentos.append(f"[{tipo}: {sig}]\n{n.post.content.strip()}")

        if not fragmentos:
            return "Este cerebro no tiene conocimiento sobre eso aún."

        if self.llm:
            contexto = "\n\n---\n\n".join(fragmentos)
            prompt = (
                f"{PROMPT_SISTEMA}\n\n"
                f"Fragmentos del cerebro:\n\n{contexto}\n\n"
                f"Pregunta: {pregunta}\n\nRespuesta:"
            )
            return self.llm(prompt)

        return self._modo_fragmentos(pregunta, fragmentos)

    def _modo_fragmentos(self, pregunta: str, fragmentos: list) -> str:
        cabecera = f"[Sin LLM] Pregunta: {pregunta}\nFragmentos recuperados: {len(fragmentos)}\n"
        cuerpo = "\n\n--- --- ---\n\n".join(fragmentos)
        return f"{cabecera}\n{cuerpo}"
