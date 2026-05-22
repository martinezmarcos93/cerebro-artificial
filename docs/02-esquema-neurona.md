# Esquema YAML de la Neurona (Versión 1.0)

Cada archivo `.md` (neurona) en el sistema debe seguir un formato estricto en su *frontmatter* YAML. Este frontmatter almacena los metadatos que el Motor Psicodinámico y el Indexador leen para construir el grafo de conocimiento.

## Estructura Base

```yaml
---
id: "neurona_00001"
etapa_creacion: "sensoriomotora"
tipo: "esquema_sensoriomotor"
arquetipo_vinculado: ""
significante: ""
significados_diferenciales: []
estado_energetico: 0.0
tags: []
---
```

## Diccionario de Datos

| Campo | Tipo de Dato | Opciones Válidas / Restricciones | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | String | `neurona_[0-9]{5}` | Identificador único del concepto. |
| `etapa_creacion` | String | `sensoriomotora`, `preoperacional`, `operaciones_concretas`, `operaciones_formales` | Momento piagetiano en que se originó el archivo. |
| `tipo` | String | `esquema_sensoriomotor`, `simbolo`, `concepto`, `arquetipo`, `conflicto`, `regla` | Categoría funcional de la neurona en el modelo freudiano/junguiano. |
| `arquetipo_vinculado` | String | Enlaces Obsidian (ej. `"[[madre.md]]"`) | (Opcional) Referencia a la plantilla arquetípica de Jung para heredar su rol. |
| `significante` | String | Texto libre (suele ser el nombre del archivo) | Representación nominal del concepto. |
| `significados_diferenciales` | Array de Strings | Lista de enlaces (ej. `["[[perro.md]]"]`) | Implementación de Saussure. Enlaces a conceptos de los que este archivo se distingue de manera explícita y directa. |
| `estado_energetico` | Float | `0.0` a `1.0` | "Carga" del Ello. Aumenta con las interacciones o búsquedas frecuentes. Determina la urgencia de ser enlazado. |
| `tags` | Array de Strings | Textos sin espacios | Para agrupación convencional y filtros rápidos en el indexador. |

## Ejemplo de un Concepto Maduro

```yaml
---
id: neurona_00582
etapa_creacion: operaciones_concretas
tipo: concepto
arquetipo_vinculado: "[[animal.md]]"
significante: "gato"
significados_diferenciales: 
  - "[[perro.md]]"
  - "[[roedor.md]]"
estado_energetico: 0.72
tags: [mamifero, mascota, felino]
---
# [[gato]]

El gato es un [[mamifero]] y una [[mascota]] común.
Se diferencia de un [[perro]] en su comportamiento independiente y de caza sigilosa.
```
