"""
Modo de observación continua del vault.
Arranca el motor psicodinámico cada vez que Obsidian modifica un archivo.

Uso:
    python scripts/watcher_cli.py
    python scripts/watcher_cli.py --vault mi_vault/
"""
import sys
import os
import time
import argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from cerebro.core.cerebro import Cerebro
from cerebro import watcher


def main():
    parser = argparse.ArgumentParser(description="Watcher del Vault - Cerebro Artificial")
    parser.add_argument("--vault", default="vault", help="Ruta al vault de Obsidian")
    args = parser.parse_args()

    cerebro = Cerebro(vault_path=args.vault)
    print(f"Cerebro inicializado en etapa: {cerebro.etapa_actual.__class__.__name__}")

    observer = watcher.iniciar(cerebro)
    print("Presiona Ctrl+C para detener.\n")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    print("\n[Watcher] Detenido.")


if __name__ == "__main__":
    main()
