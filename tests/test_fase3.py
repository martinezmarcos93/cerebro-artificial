import pytest
from pathlib import Path

pytest.importorskip("networkx")

from cerebro.core.neurona import Neurona
from cerebro.core.cerebro import Cerebro
from cerebro.core.etapas import EstadoOperacionesConcretas, EstadoOperacionesFormales
from cerebro.rag.indexador import Indexador
from cerebro.rag.razonador import Razonador
from cerebro.rag.comunicador import ComunicadorRAG


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def cerebro(tmp_path):
    return Cerebro(vault_path=str(tmp_path / "vault"))


@pytest.fixture
def vault_poblado(tmp_path):
    """Vault con neuronas relacionadas por es_un, tiene y enlaces directos."""
    vault = tmp_path / "vault"
    vault.mkdir()

    def _escribir(sig, tipo, contenido, diferenciales=None, relaciones=None, energia=0.5):
        n = Neurona()
        n.post.metadata.update({
            "id": f"id_{sig}",
            "etapa_creacion": "preoperacional",
            "tipo": tipo,
            "significante": sig,
            "estado_energetico": energia,
            "significados_diferenciales": diferenciales or [],
            "arquetipo_vinculado": "",
            "tags": [],
        })
        if relaciones:
            n.post.metadata["relaciones"] = relaciones
        n.post.content = contenido
        n.save(str(vault))

    _escribir(
        "gato", "concepto",
        "# gato\n\nAnimal doméstico felino.\n- Relacionado: [[mamifero]]",
        relaciones={"es_un": ["[[mamifero]]"], "tiene": ["[[patas]]"]},
    )
    _escribir(
        "mamifero", "concepto",
        "# mamifero\n\nVértebrado de sangre caliente.",
        relaciones={"es_un": ["[[animal]]"]},
    )
    _escribir("animal", "concepto", "# animal\n\nSer vivo con capacidad de movimiento.")
    _escribir("patas", "esquema_sensoriomotor", "# patas\n\nApéndices locomotores.")
    _escribir(
        "conflicto_fuego_vs_agua", "conflicto",
        "# conflicto\n\nTensión entre [[fuego]] y [[agua]].",
    )
    return vault


@pytest.fixture
def indexador(vault_poblado):
    idx = Indexador(str(vault_poblado))
    idx.indexar()
    return idx


@pytest.fixture
def razonador(indexador):
    return Razonador(indexador.grafo)


# ── Indexador ──────────────────────────────────────────────────────────────────

class TestIndexador:
    def test_carga_todas_las_neuronas(self, indexador):
        assert indexador.total_neuronas >= 5

    def test_nodos_en_grafo(self, indexador):
        assert "gato" in indexador.grafo.nodes
        assert "mamifero" in indexador.grafo.nodes
        assert "animal" in indexador.grafo.nodes

    def test_edge_enlace_desde_contenido(self, indexador):
        assert indexador.grafo.has_edge("gato", "mamifero")

    def test_edge_es_un(self, indexador):
        tipos = {d.get("tipo") for _, _, d in indexador.grafo.edges("gato", data=True)}
        assert "es_un" in tipos

    def test_edge_tiene(self, indexador):
        tipos = {d.get("tipo") for _, _, d in indexador.grafo.edges("gato", data=True)}
        assert "tiene" in tipos

    def test_buscar_por_significante(self, indexador):
        sigs = [n.post.metadata["significante"] for n in indexador.buscar("gato")]
        assert "gato" in sigs

    def test_buscar_por_contenido(self, indexador):
        sigs = [n.post.metadata["significante"] for n in indexador.buscar("felino")]
        assert "gato" in sigs

    def test_buscar_sin_resultados(self, indexador):
        assert indexador.buscar("XXXXXX_inexistente") == []

    def test_get_neurona_existente(self, indexador):
        assert indexador.get_neurona("gato") is not None

    def test_get_neurona_inexistente(self, indexador):
        assert indexador.get_neurona("dragon_inexistente") is None


# ── Razonador ─────────────────────────────────────────────────────────────────

class TestRazonador:
    def test_es_un_directo(self, razonador):
        assert "mamifero" in razonador.es_un("gato", transitivo=False)

    def test_es_un_transitivo(self, razonador):
        supertipos = razonador.es_un("gato", transitivo=True)
        assert "mamifero" in supertipos
        assert "animal" in supertipos

    def test_tiene(self, razonador):
        assert "patas" in razonador.tiene("gato")

    def test_vecinos_incluye_conectados(self, razonador):
        vecinos = razonador.vecinos("gato", n_hops=1)
        assert "mamifero" in vecinos or "patas" in vecinos

    def test_camino_existe(self, razonador):
        camino = razonador.camino("gato", "animal")
        assert camino is not None
        assert camino[0] == "gato"
        assert camino[-1] == "animal"

    def test_camino_no_existe(self, razonador):
        assert razonador.camino("gato", "concepto_xyz_inexistente") is None

    def test_conceptos_con_conflicto(self, razonador):
        assert len(razonador.conceptos_con_conflicto()) >= 1

    def test_expandir_contexto_agranda_lista(self, razonador):
        expandidos = razonador.expandir_contexto(["gato"], n_hops=1)
        assert len(expandidos) > 1
        assert "gato" in expandidos

    def test_es_un_nodo_inexistente(self, razonador):
        assert razonador.es_un("nodo_xyz") == []

    def test_tiene_nodo_sin_propiedades(self, razonador):
        assert razonador.tiene("animal") == []


# ── ComunicadorRAG ────────────────────────────────────────────────────────────

class TestComunicadorRAG:
    def test_sin_conocimiento_devuelve_mensaje(self, indexador, razonador):
        comunicador = ComunicadorRAG(indexador, razonador)
        respuesta = comunicador.consultar("XYZXYZ_tema_absolutamente_desconocido")
        assert "no tiene conocimiento" in respuesta

    def test_consultar_incluye_fragmento_relevante(self, indexador, razonador):
        comunicador = ComunicadorRAG(indexador, razonador)
        respuesta = comunicador.consultar("gato")
        assert "gato" in respuesta.lower()

    def test_consultar_con_llm_mock(self, indexador, razonador):
        llm_mock = lambda prompt: f"[MOCK] {len(prompt)} chars procesados"
        comunicador = ComunicadorRAG(indexador, razonador, llm=llm_mock)
        respuesta = comunicador.consultar("gato")
        assert "[MOCK]" in respuesta

    def test_autoindexar_si_vacio(self, vault_poblado):
        idx = Indexador(str(vault_poblado))
        raz = Razonador(idx.grafo)  # grafo vacío
        comunicador = ComunicadorRAG(idx, raz)
        respuesta = comunicador.consultar("animal")
        # Después de consultar, el índice debe estar poblado
        assert idx.total_neuronas > 0

    def test_modo_sin_llm_muestra_fragmentos(self, indexador, razonador):
        comunicador = ComunicadorRAG(indexador, razonador)
        respuesta = comunicador.consultar("mamifero")
        assert "Sin LLM" in respuesta
        assert "Fragmentos recuperados" in respuesta


# ── EstadoOperacionesFormales ─────────────────────────────────────────────────

class TestEstadoOperacionesFormales:
    def test_acepta_regla_y_arquetipo(self, cerebro):
        cerebro.cambiar_etapa(EstadoOperacionesFormales(cerebro))
        tipos = cerebro.etapa_actual.tipos_permitidos()
        assert "regla" in tipos
        assert "arquetipo" in tipos

    def test_interactuar_crea_hipotesis_tipo_regla(self, cerebro):
        cerebro.cambiar_etapa(EstadoOperacionesFormales(cerebro))
        cerebro.interactuar("relacionar", "fuego")
        n = cerebro.cargar_neurona("hipotesis_relacionar_fuego")
        assert n is not None
        assert n.post.metadata["tipo"] == "regla"
        assert n.post.metadata["etapa_creacion"] == "operaciones_formales"

    def test_hipotesis_tiene_estructura_premisa(self, cerebro):
        cerebro.cambiar_etapa(EstadoOperacionesFormales(cerebro))
        cerebro.interactuar("analizar", "agua")
        n = cerebro.cargar_neurona("hipotesis_analizar_agua")
        assert "Premisa" in n.post.content
        assert "Conclusión tentativa" in n.post.content


# ── Transición Concretas → Formales ───────────────────────────────────────────

class TestTransicionFormales:
    def test_tres_conceptos_disparan_transicion(self, cerebro):
        cerebro.cambiar_etapa(EstadoOperacionesConcretas(cerebro))
        cerebro.interactuar("ver", "alpha")
        cerebro.interactuar("ver", "beta")
        cerebro.interactuar("ver", "gamma")
        assert isinstance(cerebro.etapa_actual, EstadoOperacionesFormales)

    def test_dos_conceptos_no_transicionan(self, cerebro):
        cerebro.cambiar_etapa(EstadoOperacionesConcretas(cerebro))
        cerebro.interactuar("ver", "alpha")
        cerebro.interactuar("ver", "beta")
        assert isinstance(cerebro.etapa_actual, EstadoOperacionesConcretas)


# ── Cerebro.consultar (método de alto nivel) ──────────────────────────────────

class TestCerebroConsultar:
    def test_vault_vacio_no_lanza_excepcion(self, cerebro):
        respuesta = cerebro.consultar("cualquier cosa")
        assert isinstance(respuesta, str)
        assert "no tiene conocimiento" in respuesta

    def test_consultar_con_llm_mock(self, cerebro):
        cerebro.cambiar_etapa(EstadoOperacionesConcretas(cerebro))
        cerebro.interactuar("ver", "sol")
        llm_mock = lambda p: "[MOCK_CEREBRO] OK"
        respuesta = cerebro.consultar("sol", llm=llm_mock)
        assert "[MOCK_CEREBRO]" in respuesta
