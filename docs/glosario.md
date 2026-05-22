# Glosario Técnico-Psicológico

Este documento mapea los términos de las teorías psicológicas en las que se basa el Cerebro Artificial a sus correspondientes componentes y estructuras técnicas en Python y el entorno del software.

| Término Psicológico | Descripción | Contraparte Técnica |
| :--- | :--- | :--- |
| **Neurona** | Unidad básica de pensamiento/concepto. | Archivo `.md` en el Vault con frontmatter YAML que estructura sus atributos. |
| **Esquema Sensoriomotor** | Concepto primario, sin relación semántica. | Archivo `.md` donde `tipo: esquema_sensoriomotor` y sin enlaces `[[...]]`. |
| **Símbolo** | Concepto capaz de referenciar a otra idea. | Archivo `.md` de `tipo: simbolo` con al menos un enlace `[[...]]`. |
| **Significante** | Representación superficial del concepto. | El nombre del archivo `.md` (ej. `gato`). |
| **Significado** | Valor posicional en la red conceptual. | La suma de los enlaces entrantes/salientes (`networkx` edges) y metadatos. |
| **Valor Diferencial** | Oposición que le da identidad al concepto. | Campo en el YAML: `significados_diferenciales` (lista de rutas/enlaces). |
| **Estado Energético** | "Carga libidinal" o urgencia de un concepto. | Campo `estado_energetico` (float de 0.0 a 1.0) que indica cuán "activo" está el nodo. |
| **Motor Psicodinámico** | El aparato psíquico completo. | Clase `MotorPsicodinamico` que rige la creación de enlaces y resolución de conflictos. |
| **Ello (Id)** | Instinto que busca conexión inmediata. | Algoritmo heurístico que propone generar enlaces `(origen, destino)` maximizando el `estado_energetico`. |
| **Superyó (Superego)** | Reglas internalizadas que prohíben actos. | Ruleset o validador lógico (configuración JSON/YAML) que rechaza propuestas del Ello (ej. "no crear ciclos"). |
| **Yo (Ego)** | Árbitro de la realidad. Ejecutor. | Clase `Yo` que evalúa las propuestas del `Ello` contra las reglas del `Superyo`. |
| **Conflicto** | Tensión irreconciliable entre impulsos y reglas. | Nueva neurona `.md` de `tipo: conflicto` creada por el `Yo` al fallar una validación. |
| **Arquetipo** | Plantilla cognitiva innata (Jung). | Archivo `.md` en `arquetipos/` usado como plantilla y base para vecindad (RAG). |
| **Máquina de Estados** | El desarrollo cognitivo a lo largo del tiempo. | Patrón State en Python, orquestando las etapas piagetianas según el crecimiento del Vault. |
