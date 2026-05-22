"""
Envía un estímulo al cerebro desde la línea de comandos.

Uso:
    python scripts/interaccion.py --accion empujar --objeto pelota
    python scripts/interaccion.py --accion nutrir --objeto bebe --vault mi_vault
"""
import argparse
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from cerebro.core.cerebro import Cerebro


def main():
    parser = argparse.ArgumentParser(description="Interacción con el Cerebro Artificial.")
    parser.add_argument("--accion", type=str, required=True, help="La acción a realizar (ej. empujar, observar).")
    parser.add_argument("--objeto", type=str, required=True, help="El objeto de la acción (ej. pelota, fuego).")
    parser.add_argument("--vault", default="vault", help="Ruta al vault (default: vault/)")
    args = parser.parse_args()

    cerebro = Cerebro(vault_path=args.vault)
    print(f"Etapa actual: {cerebro.etapa_actual.__class__.__name__}")
    print(f"Enviando estimulo: accion='{args.accion}', objeto='{args.objeto}'")
    cerebro.interactuar(args.accion, args.objeto)


if __name__ == "__main__":
    main()
