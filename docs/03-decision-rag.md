# Decisión del Stack RAG Local: LlamaIndex vs LangChain

El objetivo es implementar la recuperación de conocimiento del Cerebro Artificial garantizando **Localidad Total**: nada sale de la máquina del usuario y el razonamiento se realiza consultando puramente la memoria de Obsidian.

## Análisis de las Opciones

### LangChain
- **Ventajas:** Extremadamente flexible, ecosistema masivo, ideal para orquestar flujos de trabajo multi-agente complejos.
- **Desventajas:** Curva de aprendizaje empinada, abstracciones a veces innecesariamente complejas y propensas a sobrecargar procesos sencillos de recuperación.

### LlamaIndex
- **Ventajas:** Optimizado específicamente para *Retrieval-Augmented Generation* (RAG). Posee abstracciones nativas para indexar carpetas de texto, lidiar con nodos de información y estructurar grafos y bases vectoriales de manera muy rápida y performante.
- **Desventajas:** Menos enfocado en "agents" generalistas, aunque para este caso de uso el "razonador" y el "comunicador" son roles RAG estrictos.

## Decisión: **LlamaIndex**

Dado que la función del RAG en este sistema (el "Aparato de Comunicación" que aparece a partir de la Fase 3) es **consultar el Vault y responder exclusivamente desde el contexto interno**, LlamaIndex es la herramienta correcta para el trabajo.

### Justificación:
1. **Manejo de Markdown:** LlamaIndex tiene cargadores nativos muy eficientes para Markdown y frontmatter YAML, lo cual es crítico, pues nuestro "Cerebro" depende completamente de propiedades YAML y enlaces Obsidian.
2. **Soporte Local Integral:** LlamaIndex integra de forma fluida Ollama (para correr LLaMA 3 localmente) y ChromaDB/FAISS (para los embeddings vectoriales).
3. **Eficiencia:** Las consultas puras al sistema de conocimiento, restringiendo alucinaciones mediante un prompt estricto, son el caso de uso central por el cual LlamaIndex fue diseñado.

## Stack Aprobado para el RAG (Fase 3):
- **Orquestador:** LlamaIndex
- **Base Vectorial:** ChromaDB
- **LLM Local:** Ollama (LLaMA 3)
- **Embeddings:** Modelos de embeddings de HuggingFace descargados localmente (ej: `all-MiniLM-L6-v2` u `Ollama embeddings`).
