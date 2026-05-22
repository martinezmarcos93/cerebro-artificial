# 04 - Diseño del Módulo Sensoriomotor (Fase 1)

Este documento explica el diseño de la primera fase de construcción del Cerebro Artificial, la cual emula la Etapa Sensoriomotora de Piaget.

## Principios de la Etapa

En esta fase, un infante humano (o nuestro sistema) percibe el mundo y actúa sobre él, pero aún no tiene la capacidad de usar representaciones mentales complejas (símbolos) o de conectar ideas de forma abstracta. Solo graba esquemas físicos de acción-reacción.

Técnicamente, esto impone una **restricción estricta de base de datos**:
El Cerebro puede insertar nuevos registros (`Neuronas`), pero los registros no pueden tener claves foráneas (enlaces `[[...]]`) a otros registros.

## Arquitectura de Clases (Patrón State)

Para modelar que el cerebro crece y cambia de comportamiento, usamos el Patrón State.
El `Cerebro` delega su comportamiento (cómo reaccionar a una interacción) a su `etapa_actual`.

### `Cerebro`
- Mantiene la referencia al directorio físico `vault/`.
- Gestiona el contador de IDs (ej. `neurona_00001`).
- Orquesta las interacciones delegándolas a la etapa activa.

### `EstadoSensoriomotor` (implementa `EtapaPiagetiana`)
- Recibe un estímulo (`acción`, `objeto`).
- Combina ambos en un **esquema** (ej. `empujar_pelota`).
- Crea un archivo `.md` de tipo `esquema_sensoriomotor`.
- Guarda el archivo sin establecer lazos.

### `Neurona`
- Utiliza la librería `python-frontmatter` para modelar el esquema YAML propuesto en la Fase 0 y el texto interno.

## Flujo de Ejecución

1. El mundo exterior dispara `python interaccion.py --accion "agarrar" --objeto "dedo"`.
2. El script instancia el `Cerebro`.
3. El `Cerebro` está en `EstadoSensoriomotor`, y se le pide procesar la acción.
4. El Estado instancia una `Neurona` y la configura con el significante `agarrar_dedo` y carga energética inicial de `0.1`.
5. Se escribe físicamente en `vault/agarrar_dedo.md`.
6. Si la cantidad de archivos crece lo suficiente, el Estado podrá promover al Cerebro a la Etapa Preoperacional en el futuro.
