"""
Tests Fase 4: motor junguiano + experimento A/B.
"""
import os
import pytest

from cerebro.core.neurona import Neurona
from cerebro.jung.motor_junguiano import MotorJunguiano, VOCABULARIO_ARQUETIPOS
from cerebro.jung.experimento_ab import ExperimentoAB


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _neurona_con(significante: str, content: str = "", tags=None) -> Neurona:
    n = Neurona()
    n.post.metadata["significante"] = significante
    n.post.metadata["tipo"] = "simbolo"
    n.post.content = content
    if tags:
        n.post.metadata["tags"] = tags
    return n


# ---------------------------------------------------------------------------
# MotorJunguiano — vocabulario interno
# ---------------------------------------------------------------------------

class TestMotorJunguianoVocabulario:
    def test_vocabulario_presente_para_todos_los_arquetipos(self):
        for nombre in ["madre", "heroe", "sombra", "self"]:
            assert nombre in VOCABULARIO_ARQUETIPOS
            assert len(VOCABULARIO_ARQUETIPOS[nombre]) > 0

    def test_clasificar_madre(self):
        motor = MotorJunguiano()
        n = _neurona_con("nutrir_bebe", content="nutrir proteger cuidar hogar")
        assert motor.clasificar(n) == "madre"

    def test_clasificar_heroe(self):
        motor = MotorJunguiano()
        n = _neurona_con("escalar_montana", content="escalar avanzar conquistar fuerza")
        assert motor.clasificar(n) == "heroe"

    def test_clasificar_sombra(self):
        motor = MotorJunguiano()
        n = _neurona_con("evitar_peligro", content="miedo conflicto oscuro destruir")
        assert motor.clasificar(n) == "sombra"

    def test_clasificar_self(self):
        motor = MotorJunguiano()
        n = _neurona_con("integrar_todo", content="integrar totalidad centro equilibrio")
        assert motor.clasificar(n) == "self"

    def test_sin_match_cae_en_self(self):
        motor = MotorJunguiano()
        n = _neurona_con("xyz_abc", content="")
        assert motor.clasificar(n) == "self"

    def test_score_usa_tags(self):
        motor = MotorJunguiano()
        n = _neurona_con("algo", tags=["nutrir", "cuidar", "proteger"])
        assert motor.clasificar(n) == "madre"


# ---------------------------------------------------------------------------
# MotorJunguiano — vincular escribe metadata
# ---------------------------------------------------------------------------

class TestMotorJunguianoVincular:
    def test_vincular_escribe_campo(self):
        motor = MotorJunguiano()
        n = _neurona_con("heroe_test", content="superar vencer conquistar fuerza")
        arq = motor.vincular(n)
        assert arq == "heroe"
        assert n.post.metadata.get("arquetipo_vinculado") == "[[heroe.md]]"

    def test_vincular_devuelve_nombre_arquetipo(self):
        motor = MotorJunguiano()
        n = _neurona_con("sombra_test", content="miedo oscuro rechazar peligro")
        resultado = motor.vincular(n)
        assert resultado in VOCABULARIO_ARQUETIPOS

    def test_vincular_formato_wikilink(self):
        motor = MotorJunguiano()
        n = _neurona_con("prueba", content="")
        motor.vincular(n)
        valor = n.post.metadata.get("arquetipo_vinculado", "")
        assert valor.startswith("[[") and valor.endswith(".md]]")


# ---------------------------------------------------------------------------
# MotorJunguiano — con vault de arquetipos en disco
# ---------------------------------------------------------------------------

class TestMotorJunguianoConVault:
    def test_carga_vocabulario_desde_md(self, tmp_path):
        arq_dir = tmp_path / "arquetipos"
        arq_dir.mkdir()
        md = arq_dir / "heroe.md"
        md.write_bytes(
            b"---\ntipo: arquetipo\nsignificante: heroe\ntags: [batallar]\n---\n"
            b"batallar valientemente en cada desafio\n"
        )
        motor = MotorJunguiano(vault_arquetipos=str(arq_dir))
        n = _neurona_con("guerrero", content="batallar valientemente")
        assert motor.clasificar(n) == "heroe"

    def test_vault_inexistente_no_rompe(self, tmp_path):
        motor = MotorJunguiano(vault_arquetipos=str(tmp_path / "no_existe"))
        n = _neurona_con("test", content="nutrir cuidar proteger")
        # debe usar vocabulario interno sin lanzar excepcion
        resultado = motor.clasificar(n)
        assert resultado in VOCABULARIO_ARQUETIPOS


# ---------------------------------------------------------------------------
# Integración: MotorJunguiano actúa en etapas Piagetanas
# ---------------------------------------------------------------------------

class TestIntegracionEtapas:
    def test_preoperacional_asigna_arquetipo(self, tmp_path):
        from cerebro.core.cerebro import Cerebro
        from cerebro.core.etapas import EstadoPreoperacional
        c = Cerebro(vault_path=str(tmp_path))
        c.cambiar_etapa(EstadoPreoperacional(c))
        c.interactuar("nutrir", "bebe")
        neuronas = c.listar_neuronas()
        assert len(neuronas) == 1
        arq = neuronas[0].post.metadata.get("arquetipo_vinculado", "")
        assert arq != ""
        assert "[[" in arq

    def test_operaciones_concretas_asigna_arquetipo(self, tmp_path):
        from cerebro.core.cerebro import Cerebro
        from cerebro.core.etapas import EstadoOperacionesConcretas
        c = Cerebro(vault_path=str(tmp_path))
        c.cambiar_etapa(EstadoOperacionesConcretas(c))
        c.interactuar("escalar", "montana")
        neuronas = c.listar_neuronas()
        assert len(neuronas) == 1
        arq = neuronas[0].post.metadata.get("arquetipo_vinculado", "")
        assert "[[" in arq

    def test_operaciones_formales_asigna_arquetipo(self, tmp_path):
        from cerebro.core.cerebro import Cerebro
        from cerebro.core.etapas import EstadoOperacionesFormales
        c = Cerebro(vault_path=str(tmp_path))
        c.cambiar_etapa(EstadoOperacionesFormales(c))
        c.interactuar("integrar", "conocimiento")
        neuronas = c.listar_neuronas()
        assert len(neuronas) == 1
        arq = neuronas[0].post.metadata.get("arquetipo_vinculado", "")
        assert "[[" in arq


# ---------------------------------------------------------------------------
# ExperimentoAB
# ---------------------------------------------------------------------------

ESTIMULOS_BASICOS = [
    ("nutrir", "bebe"),
    ("escalar", "montana"),
    ("evitar", "peligro"),
    ("integrar", "todo"),
    ("nutrir", "nino"),
    ("superar", "obstaculo"),
]


class TestExperimentoAB:
    def test_ejecutar_devuelve_reporte(self, tmp_path):
        exp = ExperimentoAB(str(tmp_path), ESTIMULOS_BASICOS)
        reporte = exp.ejecutar()
        assert "cerebro_a_con_arquetipos" in reporte
        assert "cerebro_b_tabula_rasa" in reporte
        assert "diferencias" in reporte

    def test_reporte_tiene_metricas_esperadas(self, tmp_path):
        exp = ExperimentoAB(str(tmp_path), ESTIMULOS_BASICOS)
        reporte = exp.ejecutar()
        for clave in ["cerebro_a_con_arquetipos", "cerebro_b_tabula_rasa"]:
            m = reporte[clave]
            assert "total_neuronas" in m
            assert "tipos" in m
            assert "arquetipos_vinculados" in m
            assert "conflictos" in m
            assert "diversidad_arquetipos" in m

    def test_ambos_cerebros_reciben_mismos_estimulos(self, tmp_path):
        exp = ExperimentoAB(str(tmp_path), ESTIMULOS_BASICOS)
        reporte = exp.ejecutar()
        # mismos estímulos -> mismo total de neuronas base
        total_a = reporte["cerebro_a_con_arquetipos"]["total_neuronas"]
        total_b = reporte["cerebro_b_tabula_rasa"]["total_neuronas"]
        assert total_a == total_b

    def test_cerebro_a_tiene_arquetipos_vinculados(self, tmp_path):
        exp = ExperimentoAB(str(tmp_path), ESTIMULOS_BASICOS)
        reporte = exp.ejecutar()
        # cerebro A tiene motor junguiano -> diversidad > 0
        assert reporte["cerebro_a_con_arquetipos"]["diversidad_arquetipos"] > 0

    def test_limpiar_borra_vaults_anteriores(self, tmp_path):
        exp = ExperimentoAB(str(tmp_path), ESTIMULOS_BASICOS[:2])
        exp.ejecutar()
        # segunda ejecución limpia los anteriores sin error
        exp2 = ExperimentoAB(str(tmp_path), ESTIMULOS_BASICOS[:2])
        reporte2 = exp2.ejecutar()
        assert reporte2["cerebro_a_con_arquetipos"]["total_neuronas"] == 2

    def test_diferencias_son_numeros(self, tmp_path):
        exp = ExperimentoAB(str(tmp_path), ESTIMULOS_BASICOS)
        reporte = exp.ejecutar()
        diffs = reporte["diferencias"]
        for v in diffs.values():
            assert isinstance(v, (int, float))
