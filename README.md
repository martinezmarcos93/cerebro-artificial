# Cerebro Artificial

Un sistema de gestión de conocimiento que aprende por etapas, forma sus propios enlaces por impulso interno y materializa sus conflictos como conocimiento de orden superior. La memoria vive en archivos Markdown legibles en Obsidian. No hay caja negra.

Inspirado en cuatro tradiciones teóricas:

| Teórico | Rol en el sistema |
|---|---|
| **Jean Piaget** | Máquina de estados del aprendizaje (Sensoriomotora → Operaciones Formales) |
| **Ferdinand de Saussure** | Semántica diferencial — el significado emerge de la red de diferencias |
| **Sigmund Freud** | Motor psicodinámico Ello / Yo / Superyó que decide qué conectar |
| **Carl Jung** | Arquetipos preinstalados como sustrato heredado del conocimiento |

---

## Inicio rápido

```bash
git clone https://github.com/tu-usuario/cerebro-artificial.git
cd cerebro-artificial

pip install -r requirements.txt

python main.py          # menú interactivo
python main.py status   # diagnóstico del sistema
```

> **Requisito opcional:** [Ollama](https://ollama.com) corriendo localmente para respuestas en lenguaje natural.
> ```bash
> ollama serve
> ollama pull llama3
> ```

---

## Arquitectura

### La neurona — unidad mínima de conocimiento

Cada concepto es un archivo `.md` con frontmatter YAML:

```yaml
---
id: neurona_00042
etapa_creacion: preoperacional
tipo: simbolo                        # esquema_sensoriomotor | simbolo | concepto | regla | conflicto | arquetipo
significante: agua
significados_diferenciales:
  - "[[fuego.md]]"
estado_energetico: 0.72              # proxy de activación del Ello (0.0 – 1.0)
arquetipo_vinculado: "[[madre.md]]"  # asignado automáticamente por el motor junguiano
tags: [liquido, elemento, vida]
---

# agua

Símbolo creado en etapa preoperacional.
- Relacionado: [[tierra.md]]
```

### Máquina de estados piagetiana

```
[Sensoriomotora] ──3 esquemas──> [Preoperacional] ──2 conflictos──> [Operaciones Concretas] ──3 conceptos──> [Operaciones Formales]
```

| Etapa | Tipos permitidos | Motor activo |
|---|---|---|
| Sensoriomotora | `esquema_sensoriomotor` | — |
| Preoperacional | `simbolo`, `conflicto` | Ello + Superyó + Yo |
| Operaciones Concretas | `concepto`, `regla` + anteriores | Ello + Superyó + Yo |
| Operaciones Formales | `arquetipo` + todos | Ello + Superyó + Yo |

### Motor psicodinámico (Freud)

Cada vez que nace una neurona:

```
Ello  →  propone enlace (mayor energía, menor conectividad)
  ↓
Superyó  →  valida contra reglas YAML (no autoenlace, no contradicción, no duplicado)
  ↓
Yo  →  ejecuta el enlace  ──o──  crea neurona de conflicto
```

El Yo registra cada decisión en `vault/.yo_log.jsonl`, visible en el dashboard.

### Motor junguiano (Jung)

Al nacer en etapa Preoperacional o superior, cada neurona se clasifica contra cuatro vocabularios semánticos:

- **madre** — nutrir, proteger, cuidar, refugio, hogar…
- **héroe** — superar, conquistar, fuerza, transformar, avanzar…
- **sombra** — conflicto, miedo, oscuro, rechazar, destruir…
- **self** — integrar, totalidad, equilibrio, observar, conectar…

El arquetipo con más palabras en común se escribe en `arquetipo_vinculado`. Vocabulario extensible editando `vault/arquetipos/*.md`.

### Pipeline RAG

```
Indexador  →  grafo networkx con edges tipados (enlace, es_un, tiene, diferencial)
    ↓
Razonador  →  inferencias sobre el grafo (es_un transitivo, vecinos a N hops, camino más corto)
    ↓
ComunicadorRAG  →  recupera fragmentos + expande por grafo + prompt estricto + Ollama
```

El prompt es deliberadamente restrictivo: *"usa únicamente los fragmentos recuperados, sin conocimiento externo"*.

---

## Uso

### Enviar estímulos al cerebro

```bash
python main.py interactuar --accion nutrir --objeto bebe
python main.py interactuar --accion escalar --objeto montana
```

O desde el menú interactivo:

```bash
python main.py
```

### Consultar al cerebro

```bash
# Sin LLM — devuelve fragmentos directos
python main.py consultar "que conflictos existen"

# Con Ollama
python main.py consultar --ollama "como se relacionan fuego y agua"
python main.py consultar --ollama --modelo llama3.2 --hops 2 "que tiene en comun gato y mamifero"
```

### Dashboard de observabilidad

```bash
python main.py dashboard
# Abre http://localhost:8501
```

Vistas disponibles: **Resumen** · **Neuronas** · **Grafo de conocimiento** · **Log del Yo** · **Arquetipos**

### Modo watcher (integración con Obsidian)

```bash
python main.py watcher
```

Detecta cambios en el vault y activa el motor psicodinámico automáticamente. Editar una neurona en Obsidian y guardarla equivale a un estímulo externo.

### Experimento A/B junguiano

Compara un cerebro con arquetipos heredados contra uno tabula rasa:

```bash
python main.py experimento

# Con estímulos personalizados
python scripts/experimento_ab_cli.py --estimulos nutrir:bebe escalar:montana evitar:peligro
```

---

## Estructura del proyecto

```
cerebro-artificial/
├── main.py                        # llave maestra — menú + subcomandos
├── requirements.txt
├── FAQ.md                         # 20 preguntas sobre el sistema
│
├── cerebro/
│   ├── core/
│   │   ├── cerebro.py             # CRUD + ciclo de vida
│   │   ├── etapas.py              # máquina de estados piagetiana
│   │   └── neurona.py             # modelo de archivo .md
│   ├── psicodinamico/
│   │   ├── ello.py                # propuesta de enlaces por energía/novedad
│   │   ├── superyo.py             # validación contra ruleset YAML
│   │   ├── yo.py                  # árbitro: ejecuta enlace o crea conflicto
│   │   ├── motor.py               # orquesta Ello + Superyó + Yo
│   │   └── superyo_rules.yaml     # reglas configurables del Superyó
│   ├── rag/
│   │   ├── indexador.py           # escanea vault → grafo networkx
│   │   ├── razonador.py           # inferencias sobre el grafo
│   │   ├── comunicador.py         # pipeline RAG completo
│   │   └── llm_ollama.py          # adaptador Ollama (sin requests)
│   ├── jung/
│   │   ├── motor_junguiano.py     # clasificación por vocabulario arquetípico
│   │   └── experimento_ab.py      # comparación cerebro A vs B
│   ├── dashboard/
│   │   └── app.py                 # Streamlit — observabilidad en tiempo real
│   └── watcher.py                 # watchdog — reacciona a cambios en el vault
│
├── scripts/                       # CLIs individuales
│   ├── interaccion.py
│   ├── consultar.py
│   ├── watcher_cli.py
│   └── experimento_ab_cli.py
│
├── vault/                         # memoria viva (Obsidian vault)
│   └── arquetipos/
│       ├── madre.md
│       ├── heroe.md
│       ├── sombra.md
│       └── self.md
│
├── tests/
│   ├── test_fase1.py              # CRUD, validación, transición sensoriomotora
│   ├── test_fase2.py              # Ello, Superyó, Yo, watcher
│   ├── test_fase3.py              # Indexador, Razonador, RAG, etapa formal
│   └── test_fase4.py              # motor junguiano, experimento A/B
│
└── docs/
    ├── cerebro_artificial.md      # visión y arquitectura teórica completa
    └── archive/                   # scripts legados
```

---

## Instalación detallada

```bash
# 1. Clonar el repo
git clone https://github.com/tu-usuario/cerebro-artificial.git
cd cerebro-artificial

# 2. Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate        # Linux / Mac
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. (Opcional) Instalar Ollama y descargar un modelo
#    https://ollama.com/download
ollama pull llama3

# 5. Verificar estado
python main.py status
```

> **Python 3.9+** requerido. Testeado en Python 3.9.12 (Windows 11) y Python 3.11 (Linux).

---

## Configuración

### Agregar reglas al Superyó

Editar `cerebro/psicodinamico/superyo_rules.yaml` y agregar lógica en `superyo.py`:

```yaml
reglas:
  - nombre: no_autoenlace
    descripcion: "Una neurona no puede enlazarse a sí misma."
  - nombre: no_contradiccion_directa
    descripcion: "No se puede enlazar a una neurona ya definida como opuesta."
  - nombre: no_enlace_existente
    descripcion: "El enlace ya existe en el contenido de la neurona."
  # Agregar nuevas reglas aquí
```

### Ampliar el vocabulario arquetípico

Editar `cerebro/jung/motor_junguiano.py`:

```python
VOCABULARIO_ARQUETIPOS = {
    "madre": {"nutrir", "proteger", ...},
    "heroe": {"superar", "conquistar", ...},
    # Agregar nuevo arquetipo:
    "sabio": {"conocer", "ensenar", "guiar", "iluminar", ...},
}
```

O ampliar el vocabulario de un arquetipo existente editando su `.md` en `vault/arquetipos/`:

```markdown
---
tipo: arquetipo
significante: heroe
tags: [batallar, resistir, perseverar]
---
El héroe persevera donde otros abandonan...
```

### Cambiar el vault

```bash
python main.py --vault /ruta/a/mi/vault status
python main.py --vault /ruta/a/mi/vault dashboard
```

---

## Tests

```bash
pytest tests/ -v
# 103 tests — fases 1 a 4
```

---

## Estado del proyecto

| Fase | Estado | Descripción |
|---|---|---|
| 1 — Sensoriomotora | ✅ Completa | CRUD de neuronas, máquina de estados, validación |
| 2 — Psicodinámica | ✅ Completa | Ello / Yo / Superyó, watcher, conflictos |
| 3 — RAG | ✅ Completa | Indexador, Razonador, ComunicadorRAG, etapa formal |
| 4 — Jung | ✅ Completa | Motor junguiano, experimento A/B |
| 5 — Observabilidad | ✅ Completa | Dashboard Streamlit, log del Yo |
| 6 — Futuro | 🔲 Pendiente | Persistencia vectorial, multi-vault, voz |

---

## Notas éticas

1. **El sistema no siente ni desea.** El Ello, el Yo y el Superyó son módulos algorítmicos, no entidades conscientes.
2. **Los arquetipos junguianos codifican una visión cultural específica.** Esta elección está documentada, es auditable y puede modificarse.
3. **Transparencia total.** Cualquier persona puede abrir el vault en Obsidian y leer exactamente qué "piensa" el sistema y cómo llegó a eso.
4. **El conflicto es productivo.** No se suprime; se modela como conocimiento de orden superior.

---

## Licencia

MIT
