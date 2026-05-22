import os
import pytest

from cerebro.core.neurona import Neurona
from cerebro.core.cerebro import Cerebro
from cerebro.core.etapas import EstadoSensoriomotor, EstadoPreoperacional


@pytest.fixture
def cerebro(tmp_path):
    return Cerebro(vault_path=str(tmp_path / "vault"))


def _neurona(tipo="esquema_sensoriomotor", contenido="", diferenciales=None, arquetipo=""):
    n = Neurona()
    n.post.metadata.update({
        "id": "test_001",
        "etapa_creacion": "sensoriomotora",
        "tipo": tipo,
        "significante": "test",
        "estado_energetico": 0.0,
        "significados_diferenciales": diferenciales or [],
        "arquetipo_vinculado": arquetipo,
    })
    n.post.content = contenido
    return n


# ── Neurona.tiene_enlaces ──────────────────────────────────────────────────────

class TestTieneEnlaces:
    def test_sin_contenido_ni_enlaces(self):
        assert not _neurona().tiene_enlaces()

    def test_enlace_en_cuerpo(self):
        assert _neurona(contenido="Es un [[juguete]]").tiene_enlaces()

    def test_enlace_en_diferencial(self):
        assert _neurona(diferenciales=["[[perro.md]]"]).tiene_enlaces()

    def test_enlace_en_arquetipo(self):
        assert _neurona(arquetipo="[[madre.md]]").tiene_enlaces()

    def test_corchetes_simples_no_son_enlace(self):
        assert not _neurona(contenido="[no es un enlace]").tiene_enlaces()


# ── EstadoSensoriomotor: validaciones ─────────────────────────────────────────

class TestValidacionSensoriomotora:
    def test_tipo_valido_sin_errores(self, cerebro):
        n = _neurona(tipo="esquema_sensoriomotor")
        assert cerebro.etapa_actual.validar_neurona(n) == []

    def test_tipo_invalido_genera_error(self, cerebro):
        n = _neurona(tipo="simbolo")
        errores = cerebro.etapa_actual.validar_neurona(n)
        assert errores
        assert "simbolo" in errores[0]

    def test_enlace_en_cuerpo_genera_error(self, cerebro):
        n = _neurona(contenido="Veo el [[sol]]")
        errores = cerebro.etapa_actual.validar_neurona(n)
        assert any("enlace" in e.lower() for e in errores)

    def test_no_permite_enlaces(self, cerebro):
        assert not cerebro.etapa_actual.permite_enlaces()

    def test_solo_acepta_esquema_sensoriomotor(self, cerebro):
        assert cerebro.etapa_actual.tipos_permitidos() == frozenset(["esquema_sensoriomotor"])


# ── Cerebro: CRUD ─────────────────────────────────────────────────────────────

class TestCerebroCRUD:
    def test_guardar_y_cargar(self, cerebro):
        n = _neurona()
        n.post.metadata["significante"] = "pelota_roja"
        cerebro.guardar_neurona(n)
        cargada = cerebro.cargar_neurona("pelota_roja")
        assert cargada is not None
        assert cargada.post.metadata["significante"] == "pelota_roja"

    def test_listar_vacio(self, cerebro):
        assert cerebro.listar_neuronas() == []

    def test_listar_multiples(self, cerebro):
        for sig in ["alpha", "beta", "gamma"]:
            n = _neurona()
            n.post.metadata["significante"] = sig
            cerebro.guardar_neurona(n)
        assert len(cerebro.listar_neuronas()) == 3

    def test_eliminar_existente(self, cerebro):
        n = _neurona()
        n.post.metadata["significante"] = "pelota"
        cerebro.guardar_neurona(n)
        assert cerebro.eliminar_neurona("pelota")
        assert cerebro.cargar_neurona("pelota") is None

    def test_eliminar_inexistente_devuelve_false(self, cerebro):
        assert not cerebro.eliminar_neurona("no_existe")

    def test_cargar_inexistente_devuelve_none(self, cerebro):
        assert cerebro.cargar_neurona("no_existe") is None


# ── Cerebro: validación en guardar ────────────────────────────────────────────

class TestGuardarValidacion:
    def test_tipo_invalido_lanza_error(self, cerebro):
        n = _neurona(tipo="simbolo")
        with pytest.raises(ValueError):
            cerebro.guardar_neurona(n)

    def test_enlace_en_sensoriomotora_lanza_error(self, cerebro):
        n = _neurona(contenido="El sol es una [[estrella]]")
        with pytest.raises(ValueError, match="enlace"):
            cerebro.guardar_neurona(n)

    def test_validar_false_omite_restricciones(self, cerebro):
        n = _neurona(tipo="simbolo")
        n.post.metadata["significante"] = "bypass"
        cerebro.guardar_neurona(n, validar=False)
        assert cerebro.cargar_neurona("bypass") is not None


# ── Cerebro: interactuar y transición de etapa ────────────────────────────────

class TestInteractuarYTransicion:
    def test_interactuar_crea_neurona(self, cerebro):
        cerebro.interactuar("empujar", "pelota")
        n = cerebro.cargar_neurona("empujar_pelota")
        assert n is not None
        assert n.post.metadata["tipo"] == "esquema_sensoriomotor"

    def test_tres_interacciones_transicionan_etapa(self, cerebro):
        cerebro.interactuar("ver", "cubo")
        cerebro.interactuar("tocar", "esfera")
        cerebro.interactuar("empujar", "cilindro")
        assert isinstance(cerebro.etapa_actual, EstadoPreoperacional)

    def test_dos_interacciones_no_transicionan(self, cerebro):
        cerebro.interactuar("ver", "cubo")
        cerebro.interactuar("tocar", "esfera")
        assert isinstance(cerebro.etapa_actual, EstadoSensoriomotor)
