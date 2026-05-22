import argparse
import sys
import os

# Aseguramos que el directorio raíz esté en el path para importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cerebro.core.cerebro import Cerebro

def main():
    parser = argparse.ArgumentParser(description='Interacción con el Cerebro Artificial.')
    parser.add_argument('--accion', type=str, required=True, help='La acción a realizar (ej. empujar, observar).')
    parser.add_argument('--objeto', type=str, required=True, help='El objeto de la acción (ej. pelota, fuego).')

    args = parser.parse_args()

    # Inicializar el cerebro (esto creará la carpeta vault/ si no existe)
    mi_cerebro = Cerebro(vault_path="vault")

    # Enviar estímulo
    print(f"Enviando estímulo al Cerebro: Acción='{args.accion}', Objeto='{args.objeto}'")
    mi_cerebro.interactuar(args.accion, args.objeto)

if __name__ == "__main__":
    main()
