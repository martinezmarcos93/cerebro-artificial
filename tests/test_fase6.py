"""
Tests Fase 6: perfil cognitivo + pedagogía + currículo dinámico.
"""
import os
import pytest

from cerebro.perfil.perfil_cognitivo import PerfilCognitivo, EJES
from cerebro.pedagogy.unidad_pedagogica import (
    UnidadPedagogica, TipoTransformacion,
    TRANSFORMACION_A_TIPO, TRANSFORMACION_ETAPA_MINIMA,
)
from cerebro.pedagogy.curriculo import CurriculoDinamico


# ---------------------------------------------------------------------------
# PerfilCognitivo — valores y API
# ---------------------------------------------------------------------------

class TestPerfilCognitivo:
    def test_ejes_completos(self):
        p = PerfilCognitivo()
        for eje in EJES:
            assert eje in p.valores

    def test_valores_por_defecto_son_05(self):
        p = PerfilCognitivo()
        for v in p.valores.values():
            assert v == 0.5

    def test_valores_custom(self):
        p = PerfilCognitivo(valores={"abstraccion": 0.9, "estabilidad": 0.1})
        assert p.valores["abstraccion"] == 0.9
        assert p.valores["estabilidad"] == 0.1
        assert p.valores["creatividad"] == 0.5  # resto por defecto

    def test_valores_se_clampean(self):
        p = PerfilCognitivo(valores={"abstraccion": 1.5, "estabilidad": -0.3})
        assert p.valores["abstraccion"] == 1.0
        assert p.valores["estabilidad"] == 0.0

    def test_persistencia_yaml(self, tmp_path):
        path = str(tmp_path / "perfil.yaml")
        p = PerfilCognitivo(valores={"creatividad": 0.8, "supervivencia": 0.2})
        p.guardar(path)
        p2 = PerfilCognitivo(path=path)
        assert p2.valores["creatividad"] == pytest.approx(0.8)
        assert p2.valores["supervivencia"] == pytest.approx(0.2)

    def test_tolerancia_conflicto(self):
        # alta adaptabilidad + baja estabilidad → tolerancia alta
        p = PerfilCognitivo(valores={"adaptabilidad": 1.0, "estabilidad": 0.0})
        assert p.tolerancia_conflicto() == pytest.approx(1.0)
        # baja adaptabilidad + alta estabilidad → tolerancia baja
        p2 = PerfilCognitivo(valores={"adaptabilidad": 0.0, "estabilidad": 1.0})
        assert p2.tolerancia_conflicto() == pytest.approx(0.0)

    def test_peso_arquetipo_rango(self):
        p = PerfilCognitivo()
        for nombre in ["madre", "heroe", "sombra", "self"]:
            peso = p.peso_arquetipo(nombre)
            assert 0.5 <= peso <= 1.5

    def test_umbral_conflictos_alto_vs_bajo(self):
        p_alta = PerfilCognitivo(valores={"adaptabilidad": 0.9})
        p_baja = PerfilCognitivo(valores={"adaptabilidad": 0.3})
        assert p_alta.umbral_conflictos() == 1
        assert p_baja.umbral_conflictos() == 2

    def test_umbral_conceptos_alto_vs_bajo(self):
        p_alta = PerfilCognitivo(valores={"abstraccion": 0.9})
        p_baja = PerfilCognitivo(valores={"abstraccion": 0.3})
        assert p_alta.umbral_conceptos() == 2
        assert p_baja.umbral_conceptos() == 3

    def test_eje_dominante_y_debil(self):
        p = PerfilCognitivo(valores={"creatividad": 0.95, "estabilidad": 0.05})
        assert p.eje_dominante() == "creatividad"
        assert p.eje_debil() == "estabilidad"

    def test_boost_ello_mayor_con_matching(self):
        from cerebro.core.neurona import Neurona
        p = PerfilCognitivo(valores={"supervivencia": 1.0})
        n = Neurona()
        n.post.metadata["tags"] = ["peligro", "amenaza"]
        n.post.content = "peligro inminente"
        boost = p.boost_ello(n)
        assert boost > 0.0

    def test_boost_ello_cero_sin_match(self):
        from cerebro.core.neurona import Neurona
        p = PerfilCognitivo(valores={"supervivencia": 0.0})
        n = Neurona()
        n.post.metadata["tags"] = []
        n.post.content = "algo irrelevante xyz"
        boost = p.boost_ello(n)
        assert boost == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# PerfilCognitivo — integración con Cerebro
# ---------------------------------------------------------------------------

class TestPerfilEnCerebro:
    def test_cerebro_crea_perfil_por_defecto(self, tmp_path):
        from cerebro.core.cerebro import Cerebro
        c = Cerebro(vault_path=str(tmp_path))
        assert hasattr(c, "perfil")
        assert isinstance(c.perfil, PerfilCognitivo)

    def test_cerebro_guarda_y_recarga_perfil(self, tmp_path):
        from cerebro.core.cerebro import Cerebro
        c = Cerebro(vault_path=str(tmp_path))
        c.perfil.valores["creatividad"] = 0.99
        c.guardar_perfil()
        c2 = Cerebro(vault_path=str(tmp_path))
        assert c2.perfil.valores["creatividad"] == pytest.approx(0.99)

    def test_umbral_conflictos_influye_en_transicion(self, tmp_path):
        from cerebro.core.cerebro import Cerebro
        from cerebro.core.etapas import EstadoPreoperacional, EstadoOperacionesConcretas
        # Con alta adaptabilidad el umbral baja a 1
        c = Cerebro(vault_path=str(tmp_path))
        c.perfil.valores["adaptabilidad"] = 0.9
        c.cambiar_etapa(EstadoPreoperacional(c))
        # Un solo conflicto debería bastar para transicionar
        # Forzamos creando una neurona de conflicto directamente
        from cerebro.core.neurona import Neurona
        n = Neurona()
        n.post.metadata.update({
            "id": "test_001", "tipo": "conflicto",
            "significante": "conflicto_a_vs_b", "estado_energetico": 0.5,
            "etapa_creacion": "preoperacional",
        })
        n.post.content = "# conflicto"
        c.guardar_neurona(n, validar=False)
        c.etapa_actual._verificar_transicion()
        assert isinstance(c.etapa_actual, EstadoOperacionesConcretas)


# ---------------------------------------------------------------------------
# UnidadPedagogica
# ---------------------------------------------------------------------------

class TestUnidadPedagogica:
    def test_significante(self):
        u = UnidadPedagogica("nutrir", "bebe")
        assert u.significante == "nutrir_bebe"

    def test_tipo_neurona_mapea_correctamente(self):
        assert UnidadPedagogica("a", "b", TipoTransformacion.CONTRADICCION).tipo_neurona() == "conflicto"
        assert UnidadPedagogica("a", "b", TipoTransformacion.JERARQUIA).tipo_neurona() == "concepto"
        assert UnidadPedagogica("a", "b", TipoTransformacion.PARADOJA).tipo_neurona() == "regla"

    def test_etapa_minima_paradoja_es_formal(self):
        u = UnidadPedagogica("a", "b", TipoTransformacion.PARADOJA)
        assert u.etapa_minima() == "operaciones_formales"

    def test_compatibilidad_con_etapa(self):
        u = UnidadPedagogica("a", "b", TipoTransformacion.ASOCIACION)
        assert u.es_compatible_con_etapa("EstadoPreoperacional")
        assert not u.es_compatible_con_etapa("EstadoSensoriomotor")

    def test_paradoja_solo_en_formal(self):
        u = UnidadPedagogica("a", "b", TipoTransformacion.PARADOJA)
        assert u.es_compatible_con_etapa("EstadoOperacionesFormales")
        assert not u.es_compatible_con_etapa("EstadoPreoperacional")
        assert not u.es_compatible_con_etapa("EstadoOperacionesConcretas")

    def test_todos_los_tipos_tienen_mapeo(self):
        for t in TipoTransformacion.TODOS:
            assert t in TRANSFORMACION_A_TIPO
            assert t in TRANSFORMACION_ETAPA_MINIMA


# ---------------------------------------------------------------------------
# CurriculoDinamico
# ---------------------------------------------------------------------------

class TestCurriculoDinamico:
    def _crear_vault_con_neuronas(self, tmp_path, tipos: list):
        from cerebro.core.neurona import Neurona
        from cerebro.core.cerebro import Cerebro
        c = Cerebro(vault_path=str(tmp_path))
        for i, tipo in enumerate(tipos):
            n = Neurona()
            n.post.metadata.update({
                "id": f"n_{i:03d}", "tipo": tipo,
                "significante": f"concept_{i}", "estado_energetico": 0.5,
                "etapa_creacion": "preoperacional",
            })
            n.post.content = f"# concept_{i}"
            c.guardar_neurona(n, validar=False)
        return c

    def test_analizar_vault_vacio(self, tmp_path):
        from cerebro.core.cerebro import Cerebro
        c = Cerebro(vault_path=str(tmp_path))
        curriculo = CurriculoDinamico(str(tmp_path), perfil=c.perfil)
        reporte = curriculo.analizar()
        assert reporte.total_neuronas == 0

    def test_detecta_sin_conflictos(self, tmp_path):
        self._crear_vault_con_neuronas(tmp_path, ["simbolo", "simbolo"])
        curriculo = CurriculoDinamico(str(tmp_path))
        reporte = curriculo.analizar()
        assert "sin_conflictos" in reporte.carencias

    def test_detecta_sin_jerarquias(self, tmp_path):
        # Para que se detecte sin_jerarquias la etapa debe ser concretas o formales.
        # Un solo concepto pone la etapa en operaciones_concretas.
        self._crear_vault_con_neuronas(tmp_path, ["concepto", "simbolo"])
        curriculo = CurriculoDinamico(str(tmp_path))
        reporte = curriculo.analizar()
        assert "sin_jerarquias" in reporte.carencias

    def test_recomendaciones_ordenadas_por_urgencia(self, tmp_path):
        self._crear_vault_con_neuronas(tmp_path, ["simbolo"])
        curriculo = CurriculoDinamico(str(tmp_path))
        reporte = curriculo.analizar()
        urgencias = [r.urgencia for r in reporte.recomendaciones]
        assert urgencias == sorted(urgencias, reverse=True)

    def test_necesidades_emergentes_muchos_conflictos(self, tmp_path):
        self._crear_vault_con_neuronas(tmp_path, ["conflicto"] * 5)
        curriculo = CurriculoDinamico(str(tmp_path))
        reporte = curriculo.analizar()
        assert any("integracion" in n.lower() for n in reporte.necesidades_emergentes)

    def test_perfil_alta_creatividad_detecta_carencia(self, tmp_path):
        self._crear_vault_con_neuronas(tmp_path, ["simbolo", "simbolo"])
        perfil = PerfilCognitivo(valores={"creatividad": 0.9})
        curriculo = CurriculoDinamico(str(tmp_path), perfil=perfil)
        reporte = curriculo.analizar()
        assert "creatividad_subdesarrollada" in reporte.carencias

    def test_perfil_alta_supervivencia_detecta_carencia(self, tmp_path):
        self._crear_vault_con_neuronas(tmp_path, ["simbolo"])
        perfil = PerfilCognitivo(valores={"supervivencia": 0.9})
        curriculo = CurriculoDinamico(str(tmp_path), perfil=perfil)
        reporte = curriculo.analizar()
        assert "poca_tension_supervivencia" in reporte.carencias

    def test_estima_etapa_correctamente(self, tmp_path):
        self._crear_vault_con_neuronas(tmp_path, ["regla", "simbolo"])
        curriculo = CurriculoDinamico(str(tmp_path))
        reporte = curriculo.analizar()
        assert reporte.etapa_actual == "operaciones_formales"
