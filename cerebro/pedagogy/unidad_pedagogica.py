"""
Unidades Pedagógicas y Tipos de Transformación Cognitiva.

En vez de enseñar "datos", se enseñan transformaciones:
cada tipo produce un efecto diferente en el grafo de conocimiento.
"""
from dataclasses import dataclass, field
from typing import List, Optional


class TipoTransformacion:
    ASOCIACION    = "asociacion"     # crea enlaces entre conceptos
    CONTRADICCION = "contradiccion"  # genera conflicto cognitivo
    ANALOGIA      = "analogia"       # crea abstracción por semejanza
    JERARQUIA     = "jerarquia"      # crea categorías (es_un / tiene)
    EXCEPCION     = "excepcion"      # rompe una regla existente
    PARADOJA      = "paradoja"       # fuerza razonamiento formal
    METAFORA      = "metafora"       # expande simbolización
    SECUENCIA     = "secuencia"      # genera causalidad temporal
    CICLO         = "ciclo"          # genera comprensión de sistemas
    AGENTE        = "agente"         # genera teoría de la mente

    TODOS = [
        ASOCIACION, CONTRADICCION, ANALOGIA, JERARQUIA, EXCEPCION,
        PARADOJA, METAFORA, SECUENCIA, CICLO, AGENTE,
    ]


# Qué tipo de neurona produce cada transformación
TRANSFORMACION_A_TIPO = {
    TipoTransformacion.ASOCIACION:    "simbolo",
    TipoTransformacion.CONTRADICCION: "conflicto",
    TipoTransformacion.ANALOGIA:      "concepto",
    TipoTransformacion.JERARQUIA:     "concepto",
    TipoTransformacion.EXCEPCION:     "regla",
    TipoTransformacion.PARADOJA:      "regla",
    TipoTransformacion.METAFORA:      "simbolo",
    TipoTransformacion.SECUENCIA:     "concepto",
    TipoTransformacion.CICLO:         "regla",
    TipoTransformacion.AGENTE:        "concepto",
}

# Qué etapa mínima requiere cada transformación
TRANSFORMACION_ETAPA_MINIMA = {
    TipoTransformacion.ASOCIACION:    "preoperacional",
    TipoTransformacion.CONTRADICCION: "preoperacional",
    TipoTransformacion.ANALOGIA:      "operaciones_concretas",
    TipoTransformacion.JERARQUIA:     "operaciones_concretas",
    TipoTransformacion.EXCEPCION:     "operaciones_concretas",
    TipoTransformacion.PARADOJA:      "operaciones_formales",
    TipoTransformacion.METAFORA:      "preoperacional",
    TipoTransformacion.SECUENCIA:     "operaciones_concretas",
    TipoTransformacion.CICLO:         "operaciones_formales",
    TipoTransformacion.AGENTE:        "operaciones_concretas",
}

DESCRIPCIONES_TRANSFORMACION = {
    TipoTransformacion.ASOCIACION:    "Conecta dos conceptos por proximidad semantica.",
    TipoTransformacion.CONTRADICCION: "Introduce tension entre dos ideas opuestas.",
    TipoTransformacion.ANALOGIA:      "Relaciona dos dominios diferentes por estructura comun.",
    TipoTransformacion.JERARQUIA:     "Establece relaciones es_un y tiene entre conceptos.",
    TipoTransformacion.EXCEPCION:     "Un caso que rompe una regla existente.",
    TipoTransformacion.PARADOJA:      "Una afirmacion que se contradice a si misma y fuerza abstraccion.",
    TipoTransformacion.METAFORA:      "Transfiere significado de un dominio a otro.",
    TipoTransformacion.SECUENCIA:     "Establece causalidad temporal entre eventos.",
    TipoTransformacion.CICLO:         "Revela que una secuencia vuelve a su punto de partida.",
    TipoTransformacion.AGENTE:        "Introduce la nocion de que otro ser tiene estados internos.",
}


@dataclass
class UnidadPedagogica:
    """
    Unidad mínima de enseñanza con metadatos cognitivos.
    En vez de un estímulo crudo (accion, objeto), incluye
    contexto sobre el tipo de transformación que produce.
    """
    accion: str
    objeto: str
    tipo_transformacion: str = TipoTransformacion.ASOCIACION
    dominio: str = "exploracion"          # eje del perfil que activa
    dificultad: float = 0.5               # 0.0 trivial → 1.0 muy complejo
    energia: float = 0.5                  # energía inicial de la neurona
    contradicciones: List[str] = field(default_factory=list)   # significantes opuestos
    requiere: List[str] = field(default_factory=list)           # significantes previos necesarios
    notas: Optional[str] = None

    @property
    def significante(self) -> str:
        return f"{self.accion}_{self.objeto}"

    def tipo_neurona(self) -> str:
        return TRANSFORMACION_A_TIPO.get(self.tipo_transformacion, "simbolo")

    def etapa_minima(self) -> str:
        return TRANSFORMACION_ETAPA_MINIMA.get(self.tipo_transformacion, "preoperacional")

    def es_compatible_con_etapa(self, etapa_clase: str) -> bool:
        orden = [
            "EstadoSensoriomotor",
            "EstadoPreoperacional",
            "EstadoOperacionesConcretas",
            "EstadoOperacionesFormales",
        ]
        minima = self.etapa_minima()
        mapeo = {
            "sensoriomotora":       "EstadoSensoriomotor",
            "preoperacional":       "EstadoPreoperacional",
            "operaciones_concretas":"EstadoOperacionesConcretas",
            "operaciones_formales": "EstadoOperacionesFormales",
        }
        etapa_min_clase = mapeo.get(minima, "EstadoPreoperacional")
        try:
            return orden.index(etapa_clase) >= orden.index(etapa_min_clase)
        except ValueError:
            return True
