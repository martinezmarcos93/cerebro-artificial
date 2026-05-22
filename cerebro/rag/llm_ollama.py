"""
Adaptador Ollama sin dependencias externas — usa urllib de la stdlib.
Requiere Ollama corriendo en localhost:11434.

Uso:
    from cerebro.rag.llm_ollama import crear_llm_ollama
    llm = crear_llm_ollama(modelo="llama3")
    respuesta = llm("¿Qué es un gato?")
"""
import json
import urllib.request
import urllib.error


def crear_llm_ollama(modelo: str = "llama3", host: str = "http://localhost:11434"):
    """Devuelve un callable(prompt) -> str que consulta Ollama localmente."""

    def llm(prompt: str) -> str:
        payload = json.dumps({
            "model": modelo,
            "prompt": prompt,
            "stream": False,
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{host}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("response", "").strip()
        except urllib.error.URLError as e:
            return f"[Error Ollama] No se pudo conectar a {host}: {e}"

    return llm
