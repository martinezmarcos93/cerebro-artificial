"""
Módulo watchdog: observa el vault de Obsidian y activa el motor psicodinámico
cuando el usuario edita o crea archivos .md manualmente.
"""
import time
from pathlib import Path

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    _WATCHDOG_DISPONIBLE = True
except ImportError:
    _WATCHDOG_DISPONIBLE = False


class VaultHandler:
    DEBOUNCE_SEGUNDOS = 0.5

    def __init__(self, cerebro):
        self.cerebro = cerebro
        self._ultimos_eventos: dict = {}

    def on_modified(self, event):
        if getattr(event, "is_directory", False):
            return
        path = Path(event.src_path)
        if path.suffix != ".md":
            return
        ahora = time.time()
        if ahora - self._ultimos_eventos.get(str(path), 0) < self.DEBOUNCE_SEGUNDOS:
            return
        self._ultimos_eventos[str(path)] = ahora
        self._procesar_cambio(path)

    def _procesar_cambio(self, path: Path):
        from cerebro.core.neurona import Neurona
        motor = getattr(self.cerebro.etapa_actual, "motor", None)
        if motor is None:
            print(f"[Watcher] {path.name} cambiado — etapa sin motor activo, sin acción.")
            return
        try:
            neurona = Neurona.load(str(path))
            print(f"[Watcher] Cambio detectado: {path.name}")
            motor.procesar_nacimiento(neurona)
        except Exception as e:
            print(f"[Watcher] Error procesando {path.name}: {e}")


if _WATCHDOG_DISPONIBLE:
    class _WatchdogHandler(FileSystemEventHandler, VaultHandler):
        def __init__(self, cerebro):
            FileSystemEventHandler.__init__(self)
            VaultHandler.__init__(self, cerebro)


def iniciar(cerebro):
    if not _WATCHDOG_DISPONIBLE:
        raise ImportError(
            "El módulo 'watchdog' no está instalado. "
            "Ejecutá: pip install watchdog"
        )
    handler = _WatchdogHandler(cerebro)
    observer = Observer()
    observer.schedule(handler, path=cerebro.vault_path, recursive=False)
    observer.start()
    print(f"[Watcher] Observando vault: {cerebro.vault_path}")
    return observer
