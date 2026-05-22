"""
Experimento A/B: compara la evolución de dos cerebros —
  A (con arquetipos): herencia junguiana activa
  B (tabula rasa): sin sustrato arquetípico

Ambos reciben exactamente los mismos estímulos. Al final se comparan
sus grafos de conocimiento: densidad, tipos de neuronas, diversidad
de arquetipos vinculados, número de conflictos.
"""
import os
import shutil
from pathlib import Path
from typing import List, Tuple

from cerebro.core.cerebro import Cerebro


class ExperimentoAB:
    def __init__(self, base_path: str, estimulos: List[Tuple[str, str]]):
        """
        base_path: directorio donde se crean los vaults del experimento.
        estimulos: lista de (accion, objeto) que reciben ambos cerebros.
        """
        self.base_path = Path(base_path)
        self.estimulos = estimulos
        self._vault_a = str(self.base_path / "vault_con_arquetipos")
        self._vault_b = str(self.base_path / "vault_tabula_rasa")

    def ejecutar(self) -> dict:
        """Corre el experimento y devuelve el reporte comparativo."""
        self._limpiar()

        cerebro_a = Cerebro(vault_path=self._vault_a)
        cerebro_b = Cerebro(vault_path=self._vault_b)

        # Cerebro B: desactivar el motor junguiano eliminando arquetipos del vault
        # (No hay arquetipos en su vault, así que la clasificación siempre cae en "self")

        print(f"[Experimento A/B] Enviando {len(self.estimulos)} estímulos a cada cerebro...")
        for accion, objeto in self.estimulos:
            try:
                cerebro_a.interactuar(accion, objeto)
            except Exception as e:
                print(f"  [A] Error en ({accion},{objeto}): {e}")
            try:
                cerebro_b.interactuar(accion, objeto)
            except Exception as e:
                print(f"  [B] Error en ({accion},{objeto}): {e}")

        return self._comparar(cerebro_a, cerebro_b)

    def _limpiar(self):
        for vault in [self._vault_a, self._vault_b]:
            if os.path.exists(vault):
                shutil.rmtree(vault)

    def _metricas(self, cerebro: Cerebro) -> dict:
        neuronas = cerebro.listar_neuronas()
        conteo_tipos: dict = {}
        conteo_arquetipos: dict = {}

        for n in neuronas:
            tipo = n.post.metadata.get("tipo", "?")
            conteo_tipos[tipo] = conteo_tipos.get(tipo, 0) + 1

            arq = n.post.metadata.get("arquetipo_vinculado", "")
            if arq:
                conteo_arquetipos[arq] = conteo_arquetipos.get(arq, 0) + 1

        return {
            "total_neuronas": len(neuronas),
            "tipos": conteo_tipos,
            "arquetipos_vinculados": conteo_arquetipos,
            "conflictos": conteo_tipos.get("conflicto", 0),
            "diversidad_arquetipos": len(conteo_arquetipos),
        }

    def _comparar(self, cerebro_a: Cerebro, cerebro_b: Cerebro) -> dict:
        metricas_a = self._metricas(cerebro_a)
        metricas_b = self._metricas(cerebro_b)

        reporte = {
            "cerebro_a_con_arquetipos": metricas_a,
            "cerebro_b_tabula_rasa": metricas_b,
            "diferencias": {
                "delta_neuronas": metricas_a["total_neuronas"] - metricas_b["total_neuronas"],
                "delta_conflictos": metricas_a["conflictos"] - metricas_b["conflictos"],
                "delta_diversidad_arquetipos": (
                    metricas_a["diversidad_arquetipos"] - metricas_b["diversidad_arquetipos"]
                ),
            },
        }

        self._imprimir_reporte(reporte)
        return reporte

    @staticmethod
    def _imprimir_reporte(reporte: dict):
        print("\n" + "=" * 60)
        print("RESULTADO EXPERIMENTO A/B")
        print("=" * 60)
        for nombre, metricas in [
            ("A (con arquetipos)", reporte["cerebro_a_con_arquetipos"]),
            ("B (tabula rasa)", reporte["cerebro_b_tabula_rasa"]),
        ]:
            print(f"\n  Cerebro {nombre}:")
            print(f"    Neuronas totales : {metricas['total_neuronas']}")
            print(f"    Conflictos       : {metricas['conflictos']}")
            print(f"    Tipos            : {metricas['tipos']}")
            print(f"    Arquetipos vinc. : {metricas['arquetipos_vinculados']}")

        diffs = reporte["diferencias"]
        print(f"\n  Diferencias A - B:")
        print(f"    Neuronas        : {diffs['delta_neuronas']:+d}")
        print(f"    Conflictos      : {diffs['delta_conflictos']:+d}")
        print(f"    Diversidad arq. : {diffs['delta_diversidad_arquetipos']:+d}")
        print("=" * 60)
