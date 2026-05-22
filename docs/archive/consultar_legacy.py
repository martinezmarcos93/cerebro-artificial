"""
CLI de consulta al cerebro.

Uso:
    python consultar.py "qué es un gato"
    python consultar.py --ollama "cómo se relacionan fuego y agua"
    python consultar.py --ollama --modelo llama3.2 "qué conflictos existen"
    python consultar.py --hops 2 "qué tiene en común gato y mamifero"
"""
import sys
import os
import argparse

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cerebro.rag.indexador import Indexador
from cerebro.rag.razonador import Razonador
from cerebro.rag.comunicador import ComunicadorRAG


def main():
    parser = argparse.ArgumentParser(description="Consulta al Cerebro Artificial")
    parser.add_argument("pregunta", help="Pregunta al cerebro")
    parser.add_argument("--vault", default="vault", help="Ruta al vault")
    parser.add_argument("--ollama", action="store_true", help="Usar Ollama como LLM")
    parser.add_argument("--modelo", default="llama3", help="Modelo Ollama (default: llama3)")
    parser.add_argument("--hops", type=int, default=1, help="Profundidad de expansión en grafo")
    parser.add_argument("--fragmentos", type=int, default=5, help="Fragmentos a recuperar")
    args = parser.parse_args()

    indexador = Indexador(args.vault)
    indexador.indexar()
    razonador = Razonador(indexador.grafo)

    llm = None
    if args.ollama:
        from cerebro.rag.llm_ollama import crear_llm_ollama
        llm = crear_llm_ollama(modelo=args.modelo)
        print(f"[LLM] Ollama · modelo '{args.modelo}'\n")

    comunicador = ComunicadorRAG(indexador, razonador, llm=llm)

    print(f"Vault: {args.vault} · {indexador.total_neuronas} neuronas indexadas")
    print(f"Grafo: {indexador.grafo.number_of_nodes()} nodos · {indexador.grafo.number_of_edges()} edges")
    print(f"Pregunta: {args.pregunta}\n" + "-" * 60)

    respuesta = comunicador.consultar(args.pregunta, n_fragmentos=args.fragmentos, n_hops=args.hops)
    print(respuesta)


if __name__ == "__main__":
    main()
