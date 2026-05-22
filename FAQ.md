# FAQ — Cerebro Artificial

---

## Propósito y filosofía

### 1. ¿Qué es el Cerebro Artificial?

Es un sistema de gestión de conocimiento inspirado en cuatro tradiciones teóricas: la epistemología genética de Piaget, la semiótica de Saussure, el psicoanálisis de Freud y la psicología analítica de Jung. A diferencia de una base de datos o un RAG convencional, el sistema **aprende por etapas**, **forma sus propios enlaces por impulso interno** y **materializa sus conflictos como conocimiento de orden superior**.

La memoria vive en archivos `.md` legibles en Obsidian. No hay caja negra: cada decisión del sistema es auditable como texto plano.

---

### 2. ¿Qué problema resuelve que no resuelven otras herramientas?

Las herramientas estándar de gestión del conocimiento (Notion, Obsidian puro, bases vectoriales) son **pasivas**: almacenan lo que el usuario les dice y recuperan lo que se les pregunta. Este cerebro es **activo**: cuando llega un estímulo, decide qué conectar, qué prohibir y qué conflicto formalizar, siguiendo una lógica propia que puede estudiarse y modificarse.

---

### 3. ¿Funciona sin internet?

Sí, completamente. El stack es 100 % local: Python nativo, archivos Markdown, Ollama (LLM local), networkx (grafo en memoria). No se realiza ninguna llamada a APIs externas. El único requisito es que Ollama esté corriendo si se desea respuestas en lenguaje natural.

---

### 4. ¿Es esto una IA?

Depende de cómo se defina "IA". El sistema **no aprende por gradientes ni por ajuste de pesos**. Su "aprendizaje" es determinista: reglas, vocabularios, energía de activación y validación lógica. Lo que tiene de IA es Ollama (un LLM local) que genera las respuestas narrativas en lenguaje natural; el resto es ingeniería de software inspirada en teoría psicológica.

---

### 5. ¿Por qué Piaget, Saussure, Freud y Jung?

Cada uno resuelve un problema específico de la arquitectura:

| Teórico  | Problema que resuelve |
|----------|-----------------------|
| Piaget   | ¿Cómo madura el sistema? → máquina de estados de desarrollo cognitivo |
| Saussure | ¿Qué significa un concepto? → red de diferencias, no definiciones aisladas |
| Freud    | ¿Por qué se forman los enlaces? → impulso energético + censura + árbitro |
| Jung     | ¿De dónde viene el sustrato inicial? → arquetipos preinstalados como herencia |

---

## Mecanismos internos

### 6. ¿Qué es una neurona en este sistema?

Un archivo `.md` con frontmatter YAML. Contiene:
- `id`: identificador único
- `tipo`: esquema_sensoriomotor | simbolo | concepto | regla | conflicto | arquetipo
- `significante`: el nombre del concepto (= nombre del archivo)
- `significados_diferenciales`: lista de conceptos opuestos o relacionados con oposición
- `estado_energetico`: float 0.0–1.0, proxy de activación
- `arquetipo_vinculado`: enlace wiki al arquetipo junguiano más afín
- `etapa_creacion`: en qué etapa piagetiana nació
- `tags`: etiquetas semánticas

---

### 7. ¿Cómo funciona la máquina de estados piagetiana?

El cerebro avanza por cuatro etapas, cada una con sus propias reglas de qué puede crear y cómo:

1. **Sensoriomotora** (0–2 neuronas): solo esquemas de acción, sin enlaces simbólicos.
2. **Preoperacional** (3+ neuronas): primeros símbolos, primeros enlaces, motor psicodinámico activo.
3. **Operaciones Concretas** (2+ conflictos): conceptos con jerarquías (`es_un`, `tiene`).
4. **Operaciones Formales** (3+ conceptos): hipótesis abstractas, razonamiento cadena.

La transición es irreversible y automática: cuando se alcanza el umbral de la etapa, el cerebro cambia de estado.

---

### 8. ¿Qué hacen el Ello, el Superyó y el Yo?

Son tres módulos del motor psicodinámico que se activan con cada nueva neurona:

- **Ello** (`ello.py`): propone un enlace a la neurona más energizada y menos conectada del vault. Actúa sin filtro.
- **Superyó** (`superyo.py`): evalúa el enlace propuesto contra un ruleset YAML. Reglas actuales: no autoenlace, no contradicción directa, no enlace duplicado.
- **Yo** (`yo.py`): árbitro final. Si el Superyó aprueba, escribe el enlace en el `.md`. Si rechaza, crea una **neurona de conflicto** (`tipo: conflicto`) que formaliza la tensión.

Cada decisión del Yo queda registrada en `vault/.yo_log.jsonl`, visible en el dashboard.

---

### 9. ¿Qué es una neurona de conflicto?

Un archivo `.md` de orden superior que formaliza una tensión irreconciliable. Por ejemplo, si el Ello propone enlazar `fuego.md` con `agua.md` y el Superyó lo rechaza por contradicción directa, el Yo crea `conflicto_fuego_vs_agua.md` con energía elevada (promedio de ambos + 0.2). El conflicto no desaparece: se convierte en conocimiento.

---

### 10. ¿Cómo funciona el motor junguiano?

Cuando nace una neurona (en etapa Preoperacional o superior), el `MotorJunguiano` la compara con el vocabulario semántico de cada arquetipo:

- **madre**: nutrir, proteger, cuidar, contener, refugio...
- **héroe**: superar, conquistar, fuerza, avanzar, transformar...
- **sombra**: conflicto, miedo, oscuro, rechazar, destruir...
- **self**: integrar, totalidad, equilibrio, observar, conectar...

El arquetipo con más palabras en común gana y se escribe en `arquetipo_vinculado`. Si no hay ningún match, se asigna `self` como integrador por defecto. El vocabulario puede extenderse editando los `.md` del vault `arquetipos/`.

---

### 11. ¿Qué es el estado energético y para qué sirve?

Es un float (0.0–1.0) que representa la "carga de activación" de una neurona. El Ello lo usa para priorizar qué neurona proponer como destino de enlace: mayor energía = más probable de ser seleccionada. La energía crece cuando se reciben enlaces (+0.05) o cuando se es el origen de uno (+0.15). Es el proxy computacional de la "carga libidinal" freudiana.

---

### 12. ¿Cómo funciona el sistema RAG?

Tres módulos encadenados:

1. **Indexador**: escanea el vault con `rglob("*.md")`, construye un grafo networkx con edges tipados (`enlace`, `es_un`, `tiene`, `diferencial`) y un índice de búsqueda por palabras clave.
2. **Razonador**: navega el grafo para inferencias (`es_un` transitivo, `tiene`, vecinos a N hops, camino más corto entre conceptos).
3. **ComunicadorRAG**: recupera fragmentos relevantes → expande por grafo → construye un prompt con restricción estricta ("usa solo los fragmentos recuperados, sin conocimiento externo") → envía a Ollama o responde con fragmentos directos.

---

## Uso práctico

### 13. ¿Cómo se arranca todo?

```bash
python main.py           # menú interactivo
python main.py status    # diagnóstico del sistema
python main.py dashboard # abre Streamlit en localhost:8501
```

Para interacción directa:
```bash
python main.py interactuar --accion nutrir --objeto bebe
python main.py consultar "¿qué conflictos existen?"
```

---

### 14. ¿Qué es el experimento A/B?

Una prueba comparativa que envía los mismos estímulos a dos instancias del cerebro:
- **Cerebro A**: con arquetipos junguianos preinstalados.
- **Cerebro B**: tabula rasa, sin arquetipos.

Al final compara: neuronas totales, tipos, diversidad de arquetipos vinculados y cantidad de conflictos. Permite medir cuantitativamente el impacto del sustrato junguiano en la formación del conocimiento.

```bash
python main.py experimento
```

---

### 15. ¿Puedo editar las neuronas directamente en Obsidian?

Sí, y es la idea. El watcher (`python main.py watcher`) detecta cambios en el vault y activa el motor psicodinámico sobre los archivos modificados. Editar una neurona en Obsidian y guardarla es equivalente a un estímulo externo. La transparencia total es un principio de diseño, no un accidente.

---

### 16. ¿Cómo se añaden reglas al Superyó?

Editando `cerebro/psicodinamico/superyo_rules.yaml`:

```yaml
reglas:
  - nombre: mi_nueva_regla
    descripcion: "Descripcion para el log del Yo"
```

El código de `superyo.py` lee el archivo en cada instanciación. Puedes añadir lógica en el método `evaluar()` que interprete el nuevo nombre de regla.

---

## Potencialidades y límites

### 17. ¿Puede el sistema generar nuevo conocimiento real?

Genera **conocimiento emergente** dentro de su propio grafo: detecta relaciones implícitas entre conceptos, formaliza tensiones que no estaban etiquetadas como conflictos, y construye hipótesis abstractas en la etapa formal. No inventa hechos sobre el mundo exterior; razona sobre lo que fue alimentado. Es un sistema de síntesis, no de percepción.

---

### 18. ¿Cuántas neuronas puede manejar antes de degradarse?

El cuello de botella actual es el indexador (carga todos los `.md` en memoria al consultar) y el dibujo del grafo en el dashboard. En pruebas locales, vaults de hasta ~5.000 neuronas funcionan sin problemas notables. Para vaults más grandes conviene activar el índice por lotes o persistir el grafo serializado con `pickle`. Esto es trabajo pendiente para una Fase 6.

---

### 19. ¿Qué sesgos tiene el sistema?

El principal sesgo documentado es el **sustrato junguiano**: los cuatro arquetipos (madre, héroe, sombra, self) responden a una tipología cultural occidental y masculina del siglo XX. Todo concepto que llegue al sistema es clasificado en uno de estos cuatro moldes. Si el vocabulario no incluye la palabra, cae en `self` por defecto, que también es un sesgo (hacia la integración).

El sistema lo registra en el log del Yo y en el campo `arquetipo_vinculado` de cada neurona, haciendo el sesgo **auditable y reemplazable**: basta con editar los archivos `.md` de `vault/arquetipos/` o ampliar `VOCABULARIO_ARQUETIPOS` en `motor_junguiano.py`.

---

### 21. ¿Qué es el perfil cognitivo y por qué existe?

El perfil cognitivo resuelve el problema de la teleología: sin un principio organizador, el cerebro crece pero no *hacia* ningún lugar. En vez de fijar un objetivo rígido ("quiero que sea un científico"), el perfil define **tensiones evolutivas** — 10 ejes de intensidad que inclinan el comportamiento del motor sin determinarlo.

Los ejes son: `abstraccion`, `adaptabilidad`, `dominio_social`, `exploracion`, `estabilidad`, `creatividad`, `supervivencia`, `trascendencia`, `especializacion`, `integracion`.

Cada eje influye en tres puntos concretos del motor:
- **Ello**: qué neuronas propone con más frecuencia (alta `creatividad` → favorece neuronas con tags de simbolo, metáfora, analogía)
- **Motor junguiano**: qué arquetipo "gana" cuando hay empate de score (alta `supervivencia` → amplifica sombra y héroe)
- **Umbrales de transición**: cuántos conflictos o conceptos se necesitan para madurar de etapa (alta `adaptabilidad` → basta 1 conflicto para pasar a Operaciones Concretas; alta `abstraccion` → basta 2 conceptos para pasar a Operaciones Formales)

Con 10 ejes continuos existen miles de perfiles emergentes distintos, sin necesidad de presets rígidos.

---

### 22. ¿Qué son las unidades pedagógicas y los tipos de transformación?

Una **unidad pedagógica** no es un dato: es una *transformación cognitiva* con metadatos que describen qué tipo de cambio produce en el grafo. En vez de "enseñarle que el fuego es caliente", le enseñás "una contradicción sobre el fuego respecto al agua, con dificultad 0.3, en el dominio de supervivencia".

Los 10 tipos de transformación y qué producen:

| Tipo | Qué produce | Etapa mínima |
|---|---|---|
| Asociación | Enlace entre dos conceptos | Preoperacional |
| Contradicción | Neurona de conflicto | Preoperacional |
| Metáfora | Símbolo con significado transferido | Preoperacional |
| Analogía | Concepto por semejanza estructural | Operaciones Concretas |
| Jerarquía | Concepto con `es_un` / `tiene` | Operaciones Concretas |
| Excepción | Regla que rompe un patrón | Operaciones Concretas |
| Secuencia | Concepto de causalidad temporal | Operaciones Concretas |
| Agente | Concepto con teoría de la mente | Operaciones Concretas |
| Paradoja | Regla que fuerza abstracción formal | Operaciones Formales |
| Ciclo | Regla de sistema que vuelve al origen | Operaciones Formales |

Desde el dashboard (tab **Entrenamiento**) podés enviar estímulos seleccionando el tipo de transformación sin necesidad de terminal.

---

### 23. ¿Cómo funciona el currículo dinámico?

El `CurriculoDinamico` analiza el estado actual del vault y devuelve recomendaciones concretas sobre qué enseñarle al cerebro. No prescribe contenido: recomienda *tipos de transformación* que el cerebro necesita según su etapa, su perfil y lo que ya tiene.

El proceso es:
1. **Detecta carencias**: compara lo que hay contra lo que el perfil y la etapa requieren. Ejemplos: `sin_conflictos`, `sin_jerarquias`, `creatividad_subdesarrollada`, `poca_tension_supervivencia`.
2. **Genera recomendaciones** ordenadas por urgencia, cada una con ejemplos de comandos listos para copiar.
3. **Detecta necesidades emergentes**: lo que el propio grafo "pide" sin que el usuario lo haya pedido. Ejemplo: si hay más de 3 conflictos sin resolver, el sistema detecta que el cerebro "busca integración". Si hay muchos símbolos sin categorizar, "busca estructura jerárquica".

Este tercer punto es la teleología emergente: la dirección de desarrollo nace del propio sistema, coherente con Piaget (desequilibrio → acomodación) y con Jung (tensión → integración).

---

### 20. ¿Hacia dónde puede evolucionar el proyecto?

Líneas abiertas con fundamento en la arquitectura actual:

| Potencial | Fundamento |
|-----------|------------|
| **Memoria distribuida multi-vault** | El Indexador ya hace `rglob`; ampliar a múltiples directorios es trivial |
| **Aprendizaje por retroalimentación humana** | El Superyó puede recibir nuevas reglas desde la UI del dashboard |
| **Exportación como grafo de conocimiento estándar** | networkx soporta exportación a GraphML, GML, JSON |
| **Múltiples idiomas** | El vocabulario junguiano es un diccionario Python; traducirlo es cambiar 40 palabras |
| **Arquetipos personalizados** | Crear nuevos `.md` en `vault/arquetipos/` con sus propios tags ya funciona |
| **Comparación entre vaults** | El experimento A/B es la semilla; extendible a N cerebros con distintos sesgos |
| **Interfaz de voz** | El ComunicadorRAG ya devuelve texto; conectarlo a TTS local (piper, coqui) es un wrapper |
| **Persistencia vectorial** | Sustituir el índice de palabras clave por ChromaDB o FAISS para búsqueda semántica real |
