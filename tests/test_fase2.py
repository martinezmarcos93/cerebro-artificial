import os
import pytest
from pathlib import Path

from cerebro.core.neurona import Neurona
from cerebro.core.cerebro import Cerebro
from cerebro.core.etapas import (
    EstadoSensoriomotor,
    EstadoPreoperacional,
    EstadoOperacionesConcretas,
)
from cerebro.psicodinamico.ello import Ello
from cerebro.psicodinamico.superyo import Superyo, _extraer_significante
from cerebro.psicodinamico.yo import Yo


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def vault(tmp_path):
    return tmp_path / "vault"


@pytest.fixture
def cerebro(vault):
    return Cerebro(vault_path=str(vault))


@pytest.fixture
def cerebro_preop(vault):
    """Cerebro ya en estado Preoperacional."""
    c = Cerebro(vault_path=str(vault))
    from cerebro.core.etapas import EstadoPreoperacional
    c.cambiar_etapa(EstadoPreoperacional(c))
    return c


def _neurona(significante="test", tipo="simbolo", contenido="", diferenciales=None, energia=0.5):
    n = Neurona()
    n.post.metadata.update({
        "id": f"test_{significante}",
        "etapa_creacion": "preoperacional",
        "tipo": tipo,
        "significante": significante,
        "estado_energetico": energia,
        "significados_diferenciales": diferenciales or [],
        "arquetipo_vinculado": "",
        "tags": [],
    })
    n.post.content = contenido
    return n


# ── Ello: scoring con novedad ──────────────────────────────────────────────────

class TestElloNovedad:
    def test_prefiere_menos_conectada_igual_energia(self, cerebro_preop, vault):
        # neuron A: misma energía pero sin links (más novedosa)
        a = _neurona("sin_links", energia=0.5)
        cerebro_preop.guardar_neurona(a)

        # neuron B: misma energía pero ya tiene un link (menos novedosa)
        b = _neurona("con_links", contenido="Relacionado: [[algo]]", energia=0.5)
        cerebro_preop.guardar_neurona(b)

        ello = Ello(cerebro_preop)
        origen = _neurona("origen", energia=0.3)
        origen.filepath = str(vault / "origen_ficticio.md")

        propuesta = ello.proponer_enlace(origen)
        assert propuesta is not None
        assert propuesta.post.metadata["significante"] == "sin_links"

    def test_devuelve_none_vault_vacio(self, cerebro_preop, vault):
        ello = Ello(cerebro_preop)
        origen = _neurona("origen")
        origen.filepath = str(vault / "origen.md")
        assert ello.proponer_enlace(origen) is None

    def test_no_propone_a_si_mismo(self, cerebro_preop, vault):
        n = _neurona("solitario")
        cerebro_preop.guardar_neurona(n)
        ello = Ello(cerebro_preop)
        n.filepath = str(vault / "solitario.md")
        # Sólo hay una neurona y es la misma → no puede proponerse a sí misma
        propuesta = ello.proponer_enlace(n)
        assert propuesta is None


# ── Superyo: validación de reglas ─────────────────────────────────────────────

class TestSuperyoReglas:
    def test_aprueba_enlace_valido(self):
        superyo = Superyo()
        a = _neurona("gato")
        b = _neurona("perro")
        aprobado, _ = superyo.evaluar(a, b)
        assert aprobado

    def test_rechaza_autoenlace(self):
        superyo = Superyo()
        a = _neurona("gato")
        a.post.metadata["id"] = "mismo_id"
        b = _neurona("gato_copia")
        b.post.metadata["id"] = "mismo_id"
        aprobado, razon = superyo.evaluar(a, b)
        assert not aprobado
        assert "sí misma" in razon or "misma" in razon or "autoenlace" in razon.lower()

    def test_rechaza_contradiccion_directa(self):
        superyo = Superyo()
        a = _neurona("fuego", diferenciales=["[[agua]]"])
        b = _neurona("agua")
        aprobado, _ = superyo.evaluar(a, b)
        assert not aprobado

    def test_rechaza_contradiccion_con_formato_simple(self):
        superyo = Superyo()
        a = _neurona("fuego", diferenciales=["agua"])
        b = _neurona("agua")
        aprobado, _ = superyo.evaluar(a, b)
        assert not aprobado

    def test_rechaza_enlace_existente(self):
        superyo = Superyo()
        a = _neurona("gato", contenido="Relacionado: [[perro]]")
        b = _neurona("perro")
        aprobado, _ = superyo.evaluar(a, b)
        assert not aprobado

    def test_extrae_significante_con_corchetes(self):
        assert _extraer_significante("[[agua.md]]") == "agua"

    def test_extrae_significante_sin_corchetes(self):
        assert _extraer_significante("agua") == "agua"


# ── Yo: ejecución de enlaces y conflictos ─────────────────────────────────────

class TestYo:
    def test_ejecutar_enlace_escribe_en_contenido(self, cerebro_preop):
        yo = Yo(cerebro_preop)
        a = _neurona("gato")
        b = _neurona("mamifero")
        b.post.metadata["significante"] = "mamifero"
        cerebro_preop.guardar_neurona(b)  # necesita estar en disco para guardar destino
        b_cargado = cerebro_preop.cargar_neurona("mamifero")
        cerebro_preop.guardar_neurona(a)
        a_cargado = cerebro_preop.cargar_neurona("gato")

        yo.ejecutar_enlace(a_cargado, b_cargado)

        actualizado = cerebro_preop.cargar_neurona("gato")
        assert "[[mamifero]]" in actualizado.post.content

    def test_ejecutar_enlace_aumenta_energia_origen(self, cerebro_preop):
        yo = Yo(cerebro_preop)
        a = _neurona("gato", energia=0.3)
        b = _neurona("mamifero", energia=0.2)
        cerebro_preop.guardar_neurona(a)
        cerebro_preop.guardar_neurona(b)
        a_c = cerebro_preop.cargar_neurona("gato")
        b_c = cerebro_preop.cargar_neurona("mamifero")

        yo.ejecutar_enlace(a_c, b_c)

        assert float(cerebro_preop.cargar_neurona("gato").post.metadata["estado_energetico"]) > 0.3

    def test_ejecutar_enlace_aumenta_energia_destino(self, cerebro_preop):
        yo = Yo(cerebro_preop)
        a = _neurona("gato", energia=0.3)
        b = _neurona("mamifero", energia=0.2)
        cerebro_preop.guardar_neurona(a)
        cerebro_preop.guardar_neurona(b)
        a_c = cerebro_preop.cargar_neurona("gato")
        b_c = cerebro_preop.cargar_neurona("mamifero")

        yo.ejecutar_enlace(a_c, b_c)

        assert float(cerebro_preop.cargar_neurona("mamifero").post.metadata["estado_energetico"]) > 0.2

    def test_crear_conflicto_genera_archivo(self, cerebro_preop):
        yo = Yo(cerebro_preop)
        a = _neurona("fuego", energia=0.7)
        b = _neurona("agua", energia=0.6)
        yo.crear_conflicto(a, b, "contradicción ontológica")
        conflicto = cerebro_preop.cargar_neurona("conflicto_fuego_vs_agua")
        assert conflicto is not None
        assert conflicto.post.metadata["tipo"] == "conflicto"

    def test_crear_conflicto_tiene_links(self, cerebro_preop):
        yo = Yo(cerebro_preop)
        a = _neurona("fuego")
        b = _neurona("agua")
        yo.crear_conflicto(a, b, "razon_test")
        conflicto = cerebro_preop.cargar_neurona("conflicto_fuego_vs_agua")
        assert "[[fuego]]" in conflicto.post.content
        assert "[[agua]]" in conflicto.post.content


# ── EstadoOperacionesConcretas ────────────────────────────────────────────────

class TestEstadoOperacionesConcretas:
    def test_acepta_concepto(self, cerebro):
        cerebro.cambiar_etapa(EstadoOperacionesConcretas(cerebro))
        assert "concepto" in cerebro.etapa_actual.tipos_permitidos()

    def test_no_acepta_arquetipo(self, cerebro):
        cerebro.cambiar_etapa(EstadoOperacionesConcretas(cerebro))
        assert "arquetipo" not in cerebro.etapa_actual.tipos_permitidos()

    def test_permite_enlaces(self, cerebro):
        cerebro.cambiar_etapa(EstadoOperacionesConcretas(cerebro))
        assert cerebro.etapa_actual.permite_enlaces()

    def test_interactuar_crea_concepto(self, cerebro):
        cerebro.cambiar_etapa(EstadoOperacionesConcretas(cerebro))
        cerebro.interactuar("clasificar", "mamifero")
        n = cerebro.cargar_neurona("clasificar_mamifero")
        assert n is not None
        assert n.post.metadata["tipo"] == "concepto"
        assert n.post.metadata["etapa_creacion"] == "operaciones_concretas"

    def test_concepto_tiene_relaciones_en_metadata(self, cerebro):
        cerebro.cambiar_etapa(EstadoOperacionesConcretas(cerebro))
        cerebro.interactuar("es", "animal")
        n = cerebro.cargar_neurona("es_animal")
        assert "relaciones" in n.post.metadata


# ── Transición Preoperacional → Operaciones Concretas ─────────────────────────

class TestTransicionConcretas:
    def test_un_conflicto_no_transiciona(self, cerebro_preop):
        yo = Yo(cerebro_preop)
        yo.crear_conflicto(_neurona("a"), _neurona("b"), "test")
        assert isinstance(cerebro_preop.etapa_actual, EstadoPreoperacional)

    def test_dos_conflictos_transicionan(self, cerebro_preop):
        yo = Yo(cerebro_preop)
        yo.crear_conflicto(_neurona("fuego"), _neurona("agua"), "contradiccion")
        yo.crear_conflicto(_neurona("luz"), _neurona("oscuridad"), "opuestos")
        # La transición se verifica en procesar_interaccion; la forzamos manualmente
        cerebro_preop.etapa_actual._verificar_transicion()
        assert isinstance(cerebro_preop.etapa_actual, EstadoOperacionesConcretas)

    def test_contar_por_tipo_conflicto(self, cerebro_preop):
        yo = Yo(cerebro_preop)
        yo.crear_conflicto(_neurona("fuego"), _neurona("agua"), "test")
        assert cerebro_preop._contar_por_tipo("conflicto") == 1

    def test_contar_por_tipo_vacio(self, cerebro_preop):
        assert cerebro_preop._contar_por_tipo("conflicto") == 0


# ── Watcher (opcional: requiere watchdog instalado) ───────────────────────────

class TestWatcher:
    def test_watcher_importable(self):
        from cerebro import watcher
        assert hasattr(watcher, "VaultHandler")

    def test_handler_ignora_archivos_no_md(self, cerebro_preop, tmp_path):
        from cerebro.watcher import VaultHandler
        handler = VaultHandler(cerebro_preop)

        class FakeEvent:
            is_directory = False
            src_path = str(tmp_path / "archivo.txt")

        handler.on_modified(FakeEvent())  # no debe lanzar excepción

    def test_handler_procesa_md_existente(self, cerebro_preop, vault):
        from cerebro.watcher import VaultHandler
        handler = VaultHandler(cerebro_preop)

        # crear una neurona de referencia en el vault
        n = _neurona("hola_watcher")
        cerebro_preop.guardar_neurona(n)
        md_path = Path(str(vault)) / "hola_watcher.md"

        handler._procesar_cambio(md_path)  # no debe lanzar excepción

    def test_handler_sin_motor_no_falla(self, cerebro, vault):
        """En EstadoSensoriomotor no hay motor; el handler debe ignorar silenciosamente."""
        from cerebro.watcher import VaultHandler
        assert isinstance(cerebro.etapa_actual, EstadoSensoriomotor)
        handler = VaultHandler(cerebro)

        n = _neurona("sin_motor", tipo="esquema_sensoriomotor")
        cerebro.guardar_neurona(n)
        md_path = Path(str(vault)) / "sin_motor.md"
        handler._procesar_cambio(md_path)  # debe salir silenciosamente
