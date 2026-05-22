"""
Perfil Cognitivo — define la teleología del cerebro.

No es un objetivo fijo sino un conjunto de tensiones evolutivas:
10 ejes de intensidad (0.0–1.0) que inclinan qué conocimiento
acepta, qué enlaces favorece y qué arquetipos predominan.
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Optional

EJES = [
    "abstraccion",      # pensamiento simbólico y conceptual
    "adaptabilidad",    # plasticidad ante contradicciones
    "dominio_social",   # lectura de agentes y relaciones
    "exploracion",      # curiosidad y expansión semántica
    "estabilidad",      # coherencia interna y baja entropía
    "creatividad",      # conexiones improbables
    "supervivencia",    # priorización de amenazas
    "trascendencia",    # metacognición y síntesis
    "especializacion",  # profundidad temática
    "integracion",      # conexión entre dominios
]

# Mapeo arquetipo → ejes que lo amplifican
_ARQUETIPO_EJES = {
    "madre":   ["dominio_social", "integracion"],
    "heroe":   ["supervivencia", "adaptabilidad"],
    "sombra":  ["supervivencia", "exploracion"],
    "self":    ["trascendencia", "integracion"],
}

# Mapeo dominio de estímulo → eje del perfil
_DOMINIO_EJES = {
    "supervivencia": "supervivencia",
    "abstraccion":   "abstraccion",
    "social":        "dominio_social",
    "exploracion":   "exploracion",
    "integracion":   "integracion",
    "creatividad":   "creatividad",
    "estabilidad":   "estabilidad",
    "trascendencia": "trascendencia",
}


class PerfilCognitivo:
    def __init__(self, valores: Optional[Dict] = None, path: Optional[str] = None):
        self.path = path
        self.valores: Dict[str, float] = {e: 0.5 for e in EJES}
        if path and os.path.exists(path):
            self._cargar(path)
        if valores:
            for k, v in valores.items():
                if k in self.valores:
                    self.valores[k] = float(max(0.0, min(1.0, v)))

    # ------------------------------------------------------------------
    # Persistencia
    # ------------------------------------------------------------------

    def guardar(self, path: Optional[str] = None) -> None:
        destino = path or self.path
        if not destino:
            raise ValueError("No se especificó ruta para guardar el perfil.")
        os.makedirs(os.path.dirname(destino), exist_ok=True) if os.path.dirname(destino) else None
        with open(destino, "w", encoding="utf-8") as f:
            yaml.dump({"perfil_cognitivo": self.valores}, f, allow_unicode=True, sort_keys=True)

    def _cargar(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        for k, v in data.get("perfil_cognitivo", {}).items():
            if k in self.valores:
                self.valores[k] = float(max(0.0, min(1.0, v)))

    # ------------------------------------------------------------------
    # API de influencia sobre el motor
    # ------------------------------------------------------------------

    def energia_para(self, dominio: str) -> float:
        """Boost de energía (0.0–0.5) que el perfil da a estímulos de ese dominio."""
        eje = _DOMINIO_EJES.get(dominio)
        return self.valores.get(eje, 0.5) * 0.5 if eje else 0.0

    def tolerancia_conflicto(self) -> float:
        """Alta adaptabilidad y baja estabilidad → más tolerancia al conflicto."""
        return (self.valores["adaptabilidad"] + (1.0 - self.valores["estabilidad"])) / 2

    def peso_arquetipo(self, nombre: str) -> float:
        """Multiplicador (0.5–1.5) para el score del arquetipo en la clasificación."""
        ejes = _ARQUETIPO_EJES.get(nombre, [])
        if not ejes:
            return 1.0
        promedio = sum(self.valores.get(e, 0.5) for e in ejes) / len(ejes)
        return 0.5 + promedio

    def umbral_conflictos(self) -> int:
        """Cuántos conflictos se necesitan para pasar a Operaciones Concretas."""
        return 1 if self.valores["adaptabilidad"] > 0.75 else 2

    def umbral_conceptos(self) -> int:
        """Cuántos conceptos se necesitan para pasar a Operaciones Formales."""
        return 2 if self.valores["abstraccion"] > 0.75 else 3

    def boost_ello(self, neurona) -> float:
        """Boost extra al score del Ello según qué tan afín es la neurona al perfil."""
        tags = {str(t).lower() for t in neurona.post.metadata.get("tags", [])}
        tipo = neurona.post.metadata.get("tipo", "")
        contenido = (neurona.post.content or "").lower()
        texto = " ".join(tags) + " " + tipo + " " + contenido

        boost = 0.0
        patrones = {
            "supervivencia": ["peligro", "amenaza", "conflicto", "destruir", "miedo"],
            "abstraccion":   ["hipotesis", "regla", "teoria", "concepto", "principio"],
            "creatividad":   ["simbolo", "metafora", "analogia", "imagen", "sueno"],
            "integracion":   ["totalidad", "sintesis", "equilibrio", "integrar", "unidad"],
            "exploracion":   ["nuevo", "descubrir", "explorar", "buscar", "curiosidad"],
            "trascendencia": ["meta", "observar", "reflexion", "conciencia", "ser"],
        }
        for eje, palabras in patrones.items():
            if any(p in texto for p in palabras):
                boost += self.valores.get(eje, 0.5) * 0.2
        return min(0.5, boost)

    # ------------------------------------------------------------------
    # Diagnóstico
    # ------------------------------------------------------------------

    def eje_dominante(self) -> str:
        return max(self.valores, key=lambda k: self.valores[k])

    def eje_debil(self) -> str:
        return min(self.valores, key=lambda k: self.valores[k])

    def resumen(self) -> str:
        dom = self.eje_dominante()
        deb = self.eje_debil()
        return f"Dominante: {dom} ({self.valores[dom]:.2f}) | Debil: {deb} ({self.valores[deb]:.2f})"
