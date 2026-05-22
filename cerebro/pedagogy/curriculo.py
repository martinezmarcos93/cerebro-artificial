"""
Currículo Dinámico — analiza el estado del vault y recomienda
qué enseñarle al cerebro a continuación.

El currículo no prescribe datos: recomienda transformaciones cognitivas
basadas en lo que falta, el perfil del cerebro y su etapa actual.
"""
import glob
import os
from collections import Counter
from dataclasses import dataclass, field
from typing import List, Optional

from cerebro.pedagogy.unidad_pedagogica import TipoTransformacion, UnidadPedagogica


@dataclass
class Recomendacion:
    tipo: str                                   # TipoTransformacion
    razon: str                                  # por qué se recomienda
    ejemplos: List[UnidadPedagogica] = field(default_factory=list)
    urgencia: float = 0.5                       # 0.0 opcional → 1.0 bloqueante


@dataclass
class ReporteCarencias:
    etapa_actual: str
    total_neuronas: int
    por_tipo: dict
    carencias: List[str]
    recomendaciones: List[Recomendacion]
    necesidades_emergentes: List[str]           # lo que el propio grafo "pide"


class CurriculoDinamico:
    def __init__(self, vault_path: str, perfil=None):
        self.vault_path = vault_path
        self.perfil = perfil

    # ------------------------------------------------------------------
    # API principal
    # ------------------------------------------------------------------

    def analizar(self) -> ReporteCarencias:
        """Devuelve un reporte completo con carencias y recomendaciones."""
        from cerebro.core.neurona import Neurona

        neuronas = []
        for path in glob.glob(os.path.join(self.vault_path, "*.md")):
            try:
                neuronas.append(Neurona.load(path))
            except Exception:
                pass

        por_tipo = dict(Counter(n.post.metadata.get("tipo", "?") for n in neuronas))
        etapa = self._estimar_etapa(por_tipo)
        carencias = self._detectar_carencias(neuronas, por_tipo, etapa)
        recomendaciones = self._generar_recomendaciones(carencias, etapa)
        emergentes = self._necesidades_emergentes(neuronas, por_tipo)

        return ReporteCarencias(
            etapa_actual=etapa,
            total_neuronas=len(neuronas),
            por_tipo=por_tipo,
            carencias=carencias,
            recomendaciones=recomendaciones,
            necesidades_emergentes=emergentes,
        )

    # ------------------------------------------------------------------
    # Análisis interno
    # ------------------------------------------------------------------

    def _estimar_etapa(self, por_tipo: dict) -> str:
        if por_tipo.get("regla", 0) >= 1:
            return "operaciones_formales"
        if por_tipo.get("concepto", 0) >= 1:
            return "operaciones_concretas"
        if por_tipo.get("simbolo", 0) >= 1:
            return "preoperacional"
        return "sensoriomotora"

    def _detectar_carencias(self, neuronas, por_tipo: dict, etapa: str) -> List[str]:
        carencias = []

        # Sin ninguna tensión
        if por_tipo.get("conflicto", 0) == 0:
            carencias.append("sin_conflictos")

        # Muy pocos símbolos para la etapa
        if etapa in ("preoperacional", "operaciones_concretas"):
            if por_tipo.get("simbolo", 0) < 3:
                carencias.append("pocos_simbolos")

        # Sin categorías jerárquicas
        if etapa in ("operaciones_concretas", "operaciones_formales"):
            if por_tipo.get("concepto", 0) < 2:
                carencias.append("sin_jerarquias")

        # Sin hipótesis abstractas en etapa formal
        if etapa == "operaciones_formales":
            if por_tipo.get("regla", 0) < 2:
                carencias.append("pocas_hipotesis")

        # Perfil pide creatividad pero pocos símbolos
        if self.perfil and self.perfil.valores.get("creatividad", 0.5) > 0.7:
            if por_tipo.get("simbolo", 0) < 5:
                carencias.append("creatividad_subdesarrollada")

        # Perfil pide integración pero pocos conceptos relacionados
        if self.perfil and self.perfil.valores.get("integracion", 0.5) > 0.7:
            total = len(neuronas)
            if total < 8:
                carencias.append("red_muy_escasa")

        # Perfil pide dominio social pero nada sobre agentes
        if self.perfil and self.perfil.valores.get("dominio_social", 0.5) > 0.7:
            tags_sociales = {"persona", "relacion", "agente", "grupo", "comunidad"}
            tiene_social = any(
                tags_sociales & {str(t).lower() for t in n.post.metadata.get("tags", [])}
                for n in neuronas
            )
            if not tiene_social:
                carencias.append("sin_agentes_sociales")

        # Perfil pide supervivencia pero nada sobre amenazas
        if self.perfil and self.perfil.valores.get("supervivencia", 0.5) > 0.7:
            if por_tipo.get("conflicto", 0) < 2:
                carencias.append("poca_tension_supervivencia")

        return carencias

    def _generar_recomendaciones(self, carencias: List[str], etapa: str) -> List[Recomendacion]:
        recs = []

        _mapeo = {
            "sin_conflictos": Recomendacion(
                tipo=TipoTransformacion.CONTRADICCION,
                razon="El cerebro no ha experimentado tension cognitiva. "
                      "Sin conflicto no puede desarrollar pensamiento de orden superior.",
                urgencia=0.9,
                ejemplos=[
                    UnidadPedagogica("tocar", "fuego", TipoTransformacion.CONTRADICCION,
                                     "supervivencia", 0.3, 0.6, contradicciones=["agua"]),
                    UnidadPedagogica("evitar", "oscuridad", TipoTransformacion.CONTRADICCION,
                                     "supervivencia", 0.4, 0.5),
                ],
            ),
            "pocos_simbolos": Recomendacion(
                tipo=TipoTransformacion.METAFORA,
                razon="Faltan simbolos para que el cerebro pueda formar asociaciones ricas.",
                urgencia=0.7,
                ejemplos=[
                    UnidadPedagogica("sentir", "calor", TipoTransformacion.METAFORA,
                                     "exploracion", 0.2, 0.4),
                    UnidadPedagogica("observar", "luna", TipoTransformacion.METAFORA,
                                     "trascendencia", 0.3, 0.5),
                ],
            ),
            "sin_jerarquias": Recomendacion(
                tipo=TipoTransformacion.JERARQUIA,
                razon="Sin categorias el conocimiento es plano. "
                      "Necesita relaciones es_un y tiene para estructurarse.",
                urgencia=0.8,
                ejemplos=[
                    UnidadPedagogica("clasificar", "animal", TipoTransformacion.JERARQUIA,
                                     "abstraccion", 0.4, 0.5,
                                     requiere=["mamifero", "reptil"]),
                    UnidadPedagogica("categorizar", "planta", TipoTransformacion.JERARQUIA,
                                     "abstraccion", 0.3, 0.4),
                ],
            ),
            "pocas_hipotesis": Recomendacion(
                tipo=TipoTransformacion.PARADOJA,
                razon="En operaciones formales el cerebro deberia construir hipotesis. "
                      "Las paradojas fuerzan ese nivel de abstraccion.",
                urgencia=0.6,
                ejemplos=[
                    UnidadPedagogica("comprender", "silencio", TipoTransformacion.PARADOJA,
                                     "trascendencia", 0.8, 0.7),
                    UnidadPedagogica("resolver", "contradiccion", TipoTransformacion.PARADOJA,
                                     "abstraccion", 0.9, 0.8),
                ],
            ),
            "creatividad_subdesarrollada": Recomendacion(
                tipo=TipoTransformacion.ANALOGIA,
                razon="El perfil pide alta creatividad pero faltan simbolos y analogias.",
                urgencia=0.6,
                ejemplos=[
                    UnidadPedagogica("imaginar", "vuelo", TipoTransformacion.ANALOGIA,
                                     "creatividad", 0.5, 0.6),
                    UnidadPedagogica("comparar", "mente_oceano", TipoTransformacion.METAFORA,
                                     "creatividad", 0.6, 0.7),
                ],
            ),
            "red_muy_escasa": Recomendacion(
                tipo=TipoTransformacion.ASOCIACION,
                razon="La red de conocimiento es demasiado escasa para la "
                      "alta integracion que pide el perfil.",
                urgencia=0.7,
                ejemplos=[
                    UnidadPedagogica("conectar", "opuestos", TipoTransformacion.ASOCIACION,
                                     "integracion", 0.5, 0.5),
                    UnidadPedagogica("relacionar", "todo", TipoTransformacion.ASOCIACION,
                                     "integracion", 0.4, 0.5),
                ],
            ),
            "sin_agentes_sociales": Recomendacion(
                tipo=TipoTransformacion.AGENTE,
                razon="El perfil pide dominio social pero no hay conceptos sobre agentes o relaciones.",
                urgencia=0.65,
                ejemplos=[
                    UnidadPedagogica("observar", "otro", TipoTransformacion.AGENTE,
                                     "social", 0.5, 0.5),
                    UnidadPedagogica("entender", "intencion", TipoTransformacion.AGENTE,
                                     "social", 0.6, 0.6),
                ],
            ),
            "poca_tension_supervivencia": Recomendacion(
                tipo=TipoTransformacion.CONTRADICCION,
                razon="Perfil de supervivencia alto pero pocas tensiones registradas.",
                urgencia=0.75,
                ejemplos=[
                    UnidadPedagogica("enfrentar", "peligro", TipoTransformacion.CONTRADICCION,
                                     "supervivencia", 0.5, 0.7, contradicciones=["seguridad"]),
                    UnidadPedagogica("evaluar", "amenaza", TipoTransformacion.CONTRADICCION,
                                     "supervivencia", 0.4, 0.6),
                ],
            ),
        }

        for c in carencias:
            if c in _mapeo:
                recs.append(_mapeo[c])

        # Ordenar por urgencia
        recs.sort(key=lambda r: r.urgencia, reverse=True)
        return recs

    def _necesidades_emergentes(self, neuronas, por_tipo: dict) -> List[str]:
        """
        Lo que el propio grafo 'pide' basado en su historia.
        La teleología emerge del sistema, no del usuario.
        """
        necesidades = []
        conflictos = por_tipo.get("conflicto", 0)
        simbolos = por_tipo.get("simbolo", 0)
        total = len(neuronas)

        if conflictos > 3:
            necesidades.append("El cerebro tiene muchos conflictos sin resolver — busca integracion.")
        if simbolos > 8 and por_tipo.get("concepto", 0) == 0:
            necesidades.append("Muchos simbolos sin categorizar — busca estructura jerarquica.")
        if total > 15 and conflictos == 0:
            necesidades.append("Red grande pero sin tension — el crecimiento puede estar estancado.")
        if por_tipo.get("regla", 0) > 5:
            necesidades.append("Muchas reglas formales — el cerebro busca sintesis o metacognicion.")

        return necesidades
