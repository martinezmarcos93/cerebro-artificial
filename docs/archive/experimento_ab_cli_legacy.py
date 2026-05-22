"""
CLI para el Experimento A/B Junguiano.

Compara dos cerebros con los mismos estímulos:
  A: herencia junguiana activa (arquetipos preinstalados)
  B: tabula rasa (sin sustrato arquetípico)

Uso:
    python experimento_ab_cli.py
    python experimento_ab_cli.py --estimulos nutrir:bebe escalar:montana evitar:peligro
    python experimento_ab_cli.py --base-path mi_experimento
"""
import sys
import os
import argparse

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cerebro.jung.experimento_ab import ExperimentoAB

ESTIMULOS_DEMO = [
    ("nutrir", "bebe"),
    ("nutrir", "nino"),
    ("proteger", "hogar"),
    ("escalar", "montana"),
    ("superar", "obstaculo"),
    ("conquistar", "desafio"),
    ("evitar", "peligro"),
    ("rechazar", "miedo"),
    ("destruir", "amenaza"),
    ("integrar", "conocimiento"),
    ("observar", "totalidad"),
    ("equilibrar", "fuerzas"),
]


def parsear_estimulo(s: str):
    partes = s.split(":", 1)
    if len(partes) != 2:
        raise argparse.ArgumentTypeError(
            f"Estímulo mal formado: '{s}'. Usa el formato accion:objeto"
        )
    return (partes[0].strip(), partes[1].strip())


def main():
    parser = argparse.ArgumentParser(
        description="Experimento A/B: cerebro con arquetipos vs tabula rasa"
    )
    parser.add_argument(
        "--estimulos",
        nargs="+",
        metavar="accion:objeto",
        help="Estímulos en formato accion:objeto (default: demo de 12 estímulos)",
    )
    parser.add_argument(
        "--base-path",
        default="experimento_ab",
        help="Directorio base donde se crean los vaults (default: experimento_ab)",
    )
    args = parser.parse_args()

    if args.estimulos:
        try:
            estimulos = [parsear_estimulo(e) for e in args.estimulos]
        except argparse.ArgumentTypeError as exc:
            print(f"Error: {exc}")
            sys.exit(1)
    else:
        estimulos = ESTIMULOS_DEMO
        print(f"Usando demo con {len(estimulos)} estímulos predefinidos.")

    print(f"Base path : {args.base_path}")
    print(f"Estimulos : {len(estimulos)}")
    print()

    exp = ExperimentoAB(base_path=args.base_path, estimulos=estimulos)
    exp.ejecutar()


if __name__ == "__main__":
    main()
