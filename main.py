"""
Llave maestra del Cerebro Artificial.
Gestiona el ciclo de vida completo: servicios, vault e interfaz.

Uso rapido:
    python main.py                         -- menu interactivo
    python main.py status                  -- estado del sistema
    python main.py interactuar             -- enviar estimulo al cerebro
    python main.py consultar               -- hacer una pregunta al cerebro
    python main.py watcher                 -- modo observacion continua del vault
    python main.py dashboard               -- abrir panel Streamlit
    python main.py experimento             -- experimento A/B junguiano
"""
import sys
import os
import subprocess
import argparse

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

VAULT_DEFAULT = os.path.join(ROOT, "vault")
DASHBOARD_APP = os.path.join(ROOT, "cerebro", "dashboard", "app.py")
SCRIPTS = os.path.join(ROOT, "scripts")


# ---------------------------------------------------------------------------
# Chequeos de sistema
# ---------------------------------------------------------------------------

def _check_ollama() -> bool:
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:11434", timeout=2)
        return True
    except Exception:
        return False


def _check_streamlit() -> bool:
    try:
        import streamlit  # noqa: F401
        return True
    except ImportError:
        return False


def _check_watchdog() -> bool:
    try:
        import watchdog  # noqa: F401
        return True
    except ImportError:
        return False


def _check_matplotlib() -> bool:
    try:
        import matplotlib  # noqa: F401
        return True
    except ImportError:
        return False


def cmd_status(args):
    """Imprime el estado de todos los componentes del sistema."""
    from cerebro.core.cerebro import Cerebro

    print("=" * 55)
    print("  CEREBRO ARTIFICIAL — Estado del sistema")
    print("=" * 55)

    vault = getattr(args, "vault", VAULT_DEFAULT)
    cerebro = Cerebro(vault_path=vault)
    neuronas = cerebro.listar_neuronas()
    etapa = cerebro.etapa_actual.__class__.__name__

    print(f"\n  Vault          : {vault}")
    print(f"  Etapa actual   : {etapa}")
    print(f"  Neuronas       : {len(neuronas)}")

    tipos: dict = {}
    for n in neuronas:
        t = n.post.metadata.get("tipo", "?")
        tipos[t] = tipos.get(t, 0) + 1
    for t, c in sorted(tipos.items()):
        print(f"    - {t:20s}: {c}")

    print()
    ok = lambda v: "[OK]" if v else "[--]"
    print(f"  {ok(_check_ollama())}  Ollama            (http://localhost:11434)")
    print(f"  {ok(_check_streamlit())}  Streamlit         (pip install streamlit)")
    print(f"  {ok(_check_watchdog())}  Watchdog          (pip install watchdog)")
    print(f"  {ok(_check_matplotlib())}  Matplotlib        (pip install matplotlib)")
    print("=" * 55)


# ---------------------------------------------------------------------------
# Subcomandos delegados a scripts/
# ---------------------------------------------------------------------------

def cmd_interactuar(args):
    accion = args.accion or input("Accion: ").strip()
    objeto = args.objeto or input("Objeto: ").strip()
    vault = getattr(args, "vault", VAULT_DEFAULT)

    from cerebro.core.cerebro import Cerebro
    cerebro = Cerebro(vault_path=vault)
    print(f"Etapa: {cerebro.etapa_actual.__class__.__name__}")
    cerebro.interactuar(accion, objeto)


def cmd_consultar(args):
    pregunta = args.pregunta or input("Pregunta: ").strip()
    vault = getattr(args, "vault", VAULT_DEFAULT)

    from cerebro.rag.indexador import Indexador
    from cerebro.rag.razonador import Razonador
    from cerebro.rag.comunicador import ComunicadorRAG

    idx = Indexador(vault)
    idx.indexar()

    llm = None
    if args.ollama:
        if not _check_ollama():
            print("[!] Ollama no esta corriendo en localhost:11434")
            print("    Inicialo con: ollama serve")
            sys.exit(1)
        from cerebro.rag.llm_ollama import crear_llm_ollama
        llm = crear_llm_ollama(modelo=args.modelo)
        print(f"[LLM] Ollama - modelo '{args.modelo}'")

    comunicador = ComunicadorRAG(idx, Razonador(idx.grafo), llm=llm)
    print(f"\nVault: {idx.total_neuronas} neuronas - {idx.grafo.number_of_nodes()} nodos")
    print("-" * 55)
    print(comunicador.consultar(pregunta, n_fragmentos=args.fragmentos, n_hops=args.hops))


def cmd_watcher(args):
    import time
    vault = getattr(args, "vault", VAULT_DEFAULT)

    if not _check_watchdog():
        print("[!] watchdog no esta instalado.")
        print("    Instalar con: pip install watchdog")
        sys.exit(1)

    from cerebro.core.cerebro import Cerebro
    from cerebro import watcher

    cerebro = Cerebro(vault_path=vault)
    print(f"Etapa: {cerebro.etapa_actual.__class__.__name__}")
    observer = watcher.iniciar(cerebro)
    print(f"Observando vault: {vault}")
    print("Presiona Ctrl+C para detener.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    print("[Watcher] Detenido.")


def cmd_dashboard(args):
    if not _check_streamlit():
        print("[!] Streamlit no esta instalado.")
        print("    Instalar con: pip install streamlit matplotlib")
        sys.exit(1)
    vault = getattr(args, "vault", VAULT_DEFAULT)
    print(f"Abriendo dashboard para vault: {vault}")
    print(f"URL: http://localhost:8501")
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", DASHBOARD_APP,
         "--", "--vault", vault],
        check=False,
    )


def cmd_experimento(args):
    from cerebro.jung.experimento_ab import ExperimentoAB

    estimulos_demo = [
        ("nutrir", "bebe"), ("proteger", "hogar"),
        ("escalar", "montana"), ("superar", "obstaculo"),
        ("evitar", "peligro"), ("rechazar", "miedo"),
        ("integrar", "conocimiento"), ("observar", "totalidad"),
        ("equilibrar", "fuerzas"), ("conquistar", "desafio"),
    ]
    base = getattr(args, "base_path", "experimento_ab")
    print(f"Iniciando experimento A/B con {len(estimulos_demo)} estimulos...")
    exp = ExperimentoAB(base_path=base, estimulos=estimulos_demo)
    exp.ejecutar()


# ---------------------------------------------------------------------------
# Menu interactivo
# ---------------------------------------------------------------------------

def menu_interactivo():
    opciones = {
        "1": ("Estado del sistema", lambda: cmd_status(argparse.Namespace(vault=VAULT_DEFAULT))),
        "2": ("Enviar estimulo", lambda: cmd_interactuar(
            argparse.Namespace(accion=None, objeto=None, vault=VAULT_DEFAULT))),
        "3": ("Consultar al cerebro", lambda: cmd_consultar(
            argparse.Namespace(pregunta=None, vault=VAULT_DEFAULT,
                               ollama=False, modelo="llama3", fragmentos=5, hops=1))),
        "4": ("Modo watcher (Ctrl+C para salir)", lambda: cmd_watcher(
            argparse.Namespace(vault=VAULT_DEFAULT))),
        "5": ("Abrir dashboard Streamlit", lambda: cmd_dashboard(
            argparse.Namespace(vault=VAULT_DEFAULT))),
        "6": ("Experimento A/B junguiano", lambda: cmd_experimento(
            argparse.Namespace(base_path="experimento_ab"))),
        "0": ("Salir", lambda: sys.exit(0)),
    }

    while True:
        print("\n" + "=" * 45)
        print("  CEREBRO ARTIFICIAL — Menu principal")
        print("=" * 45)
        for k, (label, _) in opciones.items():
            print(f"  [{k}] {label}")
        print("=" * 45)

        eleccion = input("  Opcion: ").strip()
        if eleccion in opciones:
            print()
            try:
                opciones[eleccion][1]()
            except KeyboardInterrupt:
                print("\n[interrumpido]")
            except SystemExit:
                break
        else:
            print("  Opcion no valida.")


# ---------------------------------------------------------------------------
# CLI principal
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Cerebro Artificial — llave maestra",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--vault", default=VAULT_DEFAULT, help="Ruta al vault (default: vault/)")

    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("status", help="Estado del sistema")

    p_i = sub.add_parser("interactuar", help="Enviar estimulo al cerebro")
    p_i.add_argument("--accion", default=None)
    p_i.add_argument("--objeto", default=None)

    p_c = sub.add_parser("consultar", help="Hacer una pregunta al cerebro")
    p_c.add_argument("pregunta", nargs="?", default=None)
    p_c.add_argument("--ollama", action="store_true")
    p_c.add_argument("--modelo", default="llama3")
    p_c.add_argument("--fragmentos", type=int, default=5)
    p_c.add_argument("--hops", type=int, default=1)

    sub.add_parser("watcher", help="Observacion continua del vault")
    sub.add_parser("dashboard", help="Panel Streamlit")

    p_exp = sub.add_parser("experimento", help="Experimento A/B junguiano")
    p_exp.add_argument("--base-path", default="experimento_ab", dest="base_path")

    args = parser.parse_args()

    dispatch = {
        "status": cmd_status,
        "interactuar": cmd_interactuar,
        "consultar": cmd_consultar,
        "watcher": cmd_watcher,
        "dashboard": cmd_dashboard,
        "experimento": cmd_experimento,
    }

    if args.cmd and args.cmd in dispatch:
        dispatch[args.cmd](args)
    else:
        menu_interactivo()


if __name__ == "__main__":
    main()
