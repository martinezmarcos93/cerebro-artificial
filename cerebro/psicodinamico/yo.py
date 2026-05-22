import json
import os
import datetime

from cerebro.core.neurona import Neurona

_LOG_FILE = ".yo_log.jsonl"


class Yo:
    def __init__(self, cerebro):
        self.cerebro = cerebro

    def _log(self, tipo: str, origen: str, destino: str, resultado: str, razon: str):
        entrada = {
            "ts": datetime.datetime.now().isoformat(timespec="seconds"),
            "tipo": tipo,
            "origen": origen,
            "destino": destino,
            "resultado": resultado,
            "razon": razon,
        }
        log_path = os.path.join(self.cerebro.vault_path, _LOG_FILE)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entrada, ensure_ascii=False) + "\n")

    def ejecutar_enlace(self, origen, destino):
        """
        Escribe el enlace en el contenido del origen y refuerza la energía de ambos.
        """
        sig_destino = destino.post.metadata.get("significante", "")
        enlace = f"[[{sig_destino}]]"

        origen.post.content += f"\n- Relacionado: {enlace}"
        origen.post.metadata["estado_energetico"] = min(
            1.0, float(origen.post.metadata.get("estado_energetico", 0)) + 0.15
        )

        destino.post.metadata["estado_energetico"] = min(
            1.0, float(destino.post.metadata.get("estado_energetico", 0)) + 0.05
        )

        self.cerebro.guardar_neurona(origen)
        self.cerebro.guardar_neurona(destino)

        sig_origen = origen.post.metadata.get("significante", "")
        self._log("enlace", sig_origen, sig_destino, "ejecutado", "Superyo aprobado")
        print(f"[Yo] Enlace ejecutado: {sig_origen} -> {sig_destino}")

    def crear_conflicto(self, origen, destino, razon):
        """
        Materializa la tensión irreconciliable como neurona de orden superior.
        """
        sig_origen = origen.post.metadata.get("significante", "")
        sig_destino = destino.post.metadata.get("significante", "")
        energia_origen = float(origen.post.metadata.get("estado_energetico", 0))
        energia_destino = float(destino.post.metadata.get("estado_energetico", 0))

        significante_conflicto = f"conflicto_{sig_origen}_vs_{sig_destino}"

        neurona = Neurona()
        neurona.post.metadata["id"] = self.cerebro.generar_id()
        neurona.post.metadata["etapa_creacion"] = self.cerebro.etapa_actual.__class__.__name__
        neurona.post.metadata["tipo"] = "conflicto"
        neurona.post.metadata["significante"] = significante_conflicto
        neurona.post.metadata["estado_energetico"] = min(
            1.0, (energia_origen + energia_destino) / 2 + 0.2
        )
        neurona.post.metadata["significados_diferenciales"] = [
            f"[[{sig_origen}]]", f"[[{sig_destino}]]"
        ]

        neurona.post.content = (
            f"# {significante_conflicto}\n\n"
            f"Tensión irreconciliable entre [[{sig_origen}]] (energía: {energia_origen:.2f}) "
            f"y [[{sig_destino}]] (energía: {energia_destino:.2f}).\n\n"
            f"**Razón del Superyó:** {razon}"
        )

        self.cerebro.guardar_neurona(neurona)
        self._log("conflicto", sig_origen, sig_destino, "creado", razon)
        print(f"[Yo] Conflicto materializado: {significante_conflicto}.md")
