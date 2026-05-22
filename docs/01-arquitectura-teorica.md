# 01 - Arquitectura Teórica a Software

Este documento traduce las cuatro tradiciones teóricas de la psicología y la lingüística en componentes concretos de software dentro del Cerebro Artificial.

## 1. Jean Piaget: El Desarrollo Cognitivo como Máquina de Estados

Piaget propuso que la inteligencia evoluciona a través de etapas cualitativamente distintas. En nuestro sistema, esto se traduce en una **Máquina de Estados Finitos (FSM)**.

- **Componente Técnico:** Patrón de diseño *State* (Estado).
- **Implementación:** Clase base `EtapaPiagetiana` y subclases para cada etapa.
- **Transiciones:** El "Cerebro" cambia de estado según el número de neuronas, umbrales de energía y reglas definidas.

**Etapas:**
1. **Sensoriomotora (`EstadoSensoriomotor`):**
   - Acción permitida: Crear archivos `.md` de tipo `esquema_sensoriomotor`.
   - Restricción: No se permiten enlaces semánticos `[[...]]`.
2. **Preoperacional (`EstadoPreoperacional`):**
   - Acción permitida: Crear `simbolos` e iniciar la formación de los primeros enlaces.
3. **Operaciones Concretas (`EstadoOperacionesConcretas`):**
   - Acción permitida: Crear jerarquías (`es_un`, `tiene`), categorización.
4. **Operaciones Formales (`EstadoOperacionesFormales`):**
   - Acción permitida: Generar inferencias, plantear hipótesis ("qué pasaría si").

---

## 2. Ferdinand de Saussure: Semántica Diferencial

Saussure estableció que el valor de un signo (palabra/concepto) no reside en sí mismo, sino en su diferencia con los demás signos de la red.

- **Componente Técnico:** Grafo de conocimiento explícito y metadatos de exclusión.
- **Implementación:** 
  - Librería `networkx` para la topología del conocimiento.
  - Atributo `significados_diferenciales` en el frontmatter (YAML) que define explícitamente "qué NO es" este concepto.
  - Los enlaces bidireccionales en Obsidian crean la vecindad semántica.

---

## 3. Sigmund Freud: El Motor Psicodinámico

El psicoanálisis freudiano aporta el motor de la acción y la tensión interna del cerebro, que decide *cómo* y *cuándo* se conectan los conceptos.

- **Componente Técnico:** Sistema de agentes/reglas que negocian la escritura en el grafo.
- **Implementación:** Clase orquestadora `MotorPsicodinamico` con tres subcomponentes:
  - **Ello:** Un algoritmo heurístico basado en energía/novedad que propone enlazar conceptos de alta "carga" de manera impulsiva.
  - **Superyó:** Un ruleset estricto (posiblemente definido en YAML/JSON) que rechaza enlaces ilógicos (ej: evitar ciclos, evitar paradojas lógicas directas).
  - **Yo:** El ejecutor final. Si el Ello propone y el Superyó rechaza, el Yo no borra el impulso, sino que **crea una neurona de conflicto** (ej. `conflicto_fuego_agua.md`).

---

## 4. Carl Jung: Arquetipos Innatos

Jung teorizó el inconsciente colectivo: estructuras mentales preexistentes (arquetipos) que moldean nuestra percepción del mundo. 

- **Componente Técnico:** Archivos semilla inmutables (plantillas) y "Herencia" en recuperación RAG.
- **Implementación:** 
  - Un subdirectorio en el Vault llamado `arquetipos/` con archivos pre-creados (`madre.md`, `heroe.md`, `sombra.md`).
  - Cada concepto nuevo puede enlazarse a un arquetipo (vía `arquetipo_vinculado`), heredando sus patrones de relación estructural para interactuar con otros nodos.
