# 🧠 Cerebro Artificial — Sistema de Conocimiento Psicodinámico

> Un cerebro artificial construido sobre archivos Markdown, donde cada neurona vive en Obsidian y el conocimiento emerge de la tensión entre impulso, restricción y estructura simbólica.

---

## Visión del Proyecto

Este proyecto fusiona cuatro tradiciones teóricas en una arquitectura de software concreta:

- **Jean Piaget** — el ciclo de vida del aprendizaje como máquina de estados
- **Ferdinand de Saussure** — el conocimiento como red de signos diferenciales
- **Sigmund Freud** — la dinámica Ello/Yo/Superyó como motor de formación de enlaces
- **Carl Jung** — arquetipos preinstalados como sustrato del conocimiento heredado

La memoria del sistema es completamente transparente: cada pensamiento es un archivo `.md` legible en Obsidian. No hay caja negra.

---

## Principios de Diseño

| Principio | Descripción |
|---|---|
| **Caja de cristal** | Toda la memoria es texto auditable en Obsidian |
| **Conflicto como valor** | Las tensiones no se suprimen, se modelan como neuronas de orden superior |
| **Localidad total** | Sin dependencias de APIs externas; todo corre en la máquina del usuario |
| **Sesgo documentado** | Los arquetipos jungnianos son una elección cultural; se registra y se puede contrastar |

---

## Arquitectura Teórica

### La Neurona (archivo `.md`)

Cada archivo Markdown tiene esta estructura mínima:

```yaml
---
id: neurona_00001
etapa_creacion: sensoriomotora       # Etapa piagetiana
tipo: esquema_sensoriomotor          # esquema | simbolo | concepto | arquetipo | conflicto | regla
arquetipo_vinculado: "[[madre.md]]"  # Opcional. Enlace junguiano
significante: "gato"
significados_diferenciales:
  - "[[perro.md]]"
  - "[[roedor.md]]"
estado_energetico: 0.72              # Proxy de "carga libidinal" del Ello (0.0–1.0)
tags: [mamifero, mascota, felino]
---
```

### Las Etapas Piagetianas como Máquina de Estados

```
[SENSORIOMOTORA] ──N esquemas──> [PREOPERACIONAL] ──umbral simbólico──> [OPERACIONES_CONCRETAS] ──razonamiento lógico──> [OPERACIONES_FORMALES]
```

| Estado | Operaciones permitidas | Motor activo |
|---|---|---|
| Sensoriomotora | Crear esquemas de acción sin enlaces | — |
| Preoperacional | Crear símbolos, primeros enlaces | Ello (descontrolado) |
| Operaciones Concretas | Categorías, jerarquías, taxonomías | Ello + Superyó + Yo |
| Operaciones Formales | Hipótesis, cadenas de razonamiento abstracto | Yo completo |

### El Motor Psicodinámico (Freud)

```
   [ELLO]  →  propone enlace sin filtro
      ↓
   [SUPERYÓ]  →  valida contra reglas lógicas
      ↓
   [YO]  →  ejecuta el enlace o crea neurona de conflicto
```

Cuando hay tensión irreconciliable (ej. `fuego.md` ↔ `agua.md`), el Yo no bloquea: **crea** `conflicto_fuego_agua.md`. El conflicto es una neurona de orden superior.

### La Semántica Diferencial (Saussure)

El significado de una neurona no está en su contenido aislado, sino en su posición relativa en la red.

```
arbol.md   ←→   arbusto.md   (oposición explícita)
    ↓
planta.md, madera.md, hoja.md   (vecindad semántica)
```

El campo `significados_diferenciales` en el frontmatter implementa esta oposición de forma explícita y consultable.

### Los Arquetipos (Jung)

El cerebro no nace como tabla rasa. Se preinstala con plantillas de procesamiento:

| Arquetipo | Función | Archivo |
|---|---|---|
| Madre | Procesa entidades que nutren/protegen | `madre.md` |
| Héroe | Procesa entidades que superan/transforman | `heroe.md` |
| Sombra | Procesa lo desconocido/rechazado | `sombra.md` |
| Yo (Self) | Integrador de la totalidad | `self.md` |

Los conceptos concretos se enlazan a estos arquetipos y heredan sus patrones de relación.

---

## Stack Tecnológico

| Módulo | Tecnología |
|---|---|
| Almacenamiento de neuronas | Obsidian vault (archivos `.md`) |
| Lógica del núcleo | Python — `pathlib`, `python-frontmatter` |
| Observación de cambios | `watchdog` |
| Grafo de conocimiento | `networkx` |
| Base vectorial | `ChromaDB` o `FAISS` |
| LLM local | `Ollama` + LLaMA 3 |
| Orquestación RAG | `LlamaIndex` o `LangChain` |
| Documentación | `MkDocs` |

---

## Roadmap

### Fase 0 — Investigación y Documentación *(actual)*
**Objetivo:** documentar antes de codificar.

- [x] Síntesis teórica: Piaget + Saussure + Freud + Jung + Lógica Computacional
- [ ] `docs/01-arquitectura-teorica.md` — traducción de cada teoría a componentes de software
- [ ] `docs/glosario.md` — mapa de términos psicológicos → clases Python
- [ ] Diseño del esquema YAML de la neurona (versión 1.0)
- [ ] Decisión: ¿LlamaIndex o LangChain? Benchmarks locales con Ollama

---

### Fase 1 — Cerebro Sensoriomotor *(prototipo mínimo)*
**Objetivo:** un cerebro que crea archivos y no hace nada más.

- [ ] Clase `Cerebro` — CRUD de neuronas en el vault
- [ ] Clase `EtapaPiagetiana` — patrón State (base)
- [ ] Subclase `EstadoSensoriomotor` — solo esquemas, sin enlaces semánticos
- [ ] Script `interaccion.py` — simula el mundo exterior
  ```bash
  python interaccion.py --accion "empujar" --objeto "pelota_roja"
  ```
- [ ] Tests: el cerebro no puede crear enlaces en esta etapa
- [ ] `docs/02-diseno-modulo-sensoriomotor.md`

---

### Fase 2 — Simbolismo y Conflicto *(Freud + Saussure)*
**Objetivo:** el cerebro forma símbolos y experimenta su primera tensión interna.

- [ ] Clase `MotorPsicodinamico` con instancias de `Ello`, `Yo`, `Superyo`
- [ ] `Ello` — algoritmo de propuesta de enlaces por energía/novedad
- [ ] `Superyo` — ruleset lógico de restricciones (config en YAML)
- [ ] `Yo` — árbitro: ejecuta o crea neurona de conflicto
- [ ] Subclase `EstadoPreoperacional` — primeros símbolos y enlaces
- [ ] Subclase `EstadoOperacionesConcretas` — taxonomías y jerarquías
- [ ] Módulo `watchdog` para reaccionar a cambios en el vault
- [ ] `docs/03-diseno-modulo-psicodinamico.md`

---

### Fase 3 — Razonamiento y RAG *(Lógica + "El Habla")*
**Objetivo:** el cerebro responde preguntas usando únicamente su propio conocimiento.

- [ ] Módulo `Indexador` — escanea el vault y construye ChromaDB + grafo `networkx`
- [ ] Módulo `Razonador` — lógica formal sobre el grafo (`es_un`, `tiene_propiedad`)
- [ ] Clase `ComunicadorRAG` — pipeline completo con prompt estricto:
  > *"Eres la voz de este cerebro. Basa tu respuesta única y exclusivamente en los fragmentos recuperados. No uses conocimiento externo."*
- [ ] Subclase `EstadoOperacionesFormales` — hipótesis y razonamiento abstracto
- [ ] `docs/04-diseno-modulo-rag-logico.md`

---

### Fase 4 — Arquetipos y Sustrato Junguiano
**Objetivo:** preinstalar el sustrato heredado y medir su impacto en el aprendizaje.

- [ ] Crear vault de arquetipos base (`madre.md`, `heroe.md`, `sombra.md`, `self.md`, ...)
- [ ] Lógica de herencia arquetípica al crear nuevas neuronas
- [ ] **Experimento A/B:** criar dos instancias — una con arquetipos, una tabula rasa — y comparar la evolución de sus redes de conocimiento
- [ ] `docs/05-diseno-modulo-junguiano.md`

---

### Fase 5 — Observabilidad y Ética
**Objetivo:** construir la "caja de cristal" y documentar los sesgos.

- [ ] Dashboard de visualización del grafo en tiempo real
- [ ] Log de decisiones del Yo (qué enlaces propuso el Ello, qué vetó el Superyó, qué se creó)
- [ ] `docs/06-sesgos-y-etica.md` — registro de sesgos arquetípicos codificados
- [ ] Guía de uso responsable: el sistema no siente ni desea; el Ello/Yo/Superyó son algoritmos

---

## Estructura de Carpetas

```
cerebro-artificial/
├── docs/
│   ├── 01-arquitectura-teorica.md
│   ├── 02-diseno-modulo-sensoriomotor.md
│   ├── 03-diseno-modulo-psicodinamico.md
│   ├── 04-diseno-modulo-rag-logico.md
│   ├── 05-diseno-modulo-junguiano.md
│   ├── 06-sesgos-y-etica.md
│   └── glosario.md
├── cerebro/
│   ├── core/
│   │   ├── cerebro.py
│   │   ├── etapas.py           # Máquina de estados piagetiana
│   │   └── neurona.py          # Modelo de archivo .md
│   ├── psicodinamico/
│   │   ├── ello.py
│   │   ├── yo.py
│   │   └── superyo.py
│   ├── rag/
│   │   ├── indexador.py
│   │   ├── razonador.py
│   │   └── comunicador.py
│   └── jung/
│       └── arquetipos/
│           ├── madre.md
│           ├── heroe.md
│           ├── sombra.md
│           └── self.md
├── vault/                      # Obsidian vault (la memoria viva)
├── interaccion.py
├── tests/
└── README.md
```

---

## Glosario Rápido

| Término psicológico | Contraparte técnica |
|---|---|
| Neurona | Archivo `.md` con frontmatter YAML |
| Esquema sensoriomotor | Archivo `tipo: esquema_sensoriomotor` sin enlaces `[[]]` |
| Símbolo | Archivo `tipo: simbolo` con primer enlace semántico |
| Significante | Nombre del archivo |
| Significado | Red de enlaces y metadatos |
| Valor diferencial | Campo `significados_diferenciales` |
| Ello | Algoritmo de propuesta de enlaces por energía |
| Superyó | Ruleset YAML de restricciones lógicas |
| Yo | Árbitro; crea enlace o neurona de conflicto |
| Arquetipo junguiano | Archivo `.md` preinstalado como plantilla de procesamiento |
| Estado energético | `estado_energetico: float` — proxy de activación del Ello |
| Neurona de conflicto | Archivo `tipo: conflicto` — pensamiento de orden superior |

---

## Notas Éticas

1. **El sistema no siente ni desea.** El Ello, el Yo y el Superyó son módulos algorítmicos que modelan una dinámica, no entidades conscientes.
2. **Los arquetipos jungnianos codifican una visión cultural específica.** Esta elección está documentada y puede modificarse o eliminarse.
3. **Transparencia total.** Cualquier persona puede abrir el vault en Obsidian y leer exactamente qué "piensa" el sistema y cómo llegó a eso.
4. **El conflicto es productivo.** No se suprime; se modela como conocimiento de orden superior.

---

*Proyecto en Fase 0 — Investigación activa.*
