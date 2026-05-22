import os
import glob

from cerebro.core.etapas import EstadoSensoriomotor


class Cerebro:
    def __init__(self, vault_path="vault"):
        self.vault_path = vault_path
        os.makedirs(self.vault_path, exist_ok=True)
        self.contador_ids = self._inicializar_contador()

        if self.contador_ids > 3:
            from cerebro.core.etapas import EstadoPreoperacional
            self.etapa_actual = EstadoPreoperacional(self)
        else:
            self.etapa_actual = EstadoSensoriomotor(self)

    def _inicializar_contador(self):
        archivos = glob.glob(os.path.join(self.vault_path, "*.md"))
        return len(archivos) + 1

    def generar_id(self):
        nuevo_id = f"neurona_{self.contador_ids:05d}"
        self.contador_ids += 1
        return nuevo_id

    def cambiar_etapa(self, nueva_etapa):
        self.etapa_actual = nueva_etapa

    def interactuar(self, accion, objeto):
        self.etapa_actual.procesar_interaccion(accion, objeto)

    def guardar_neurona(self, neurona, validar=True):
        if validar:
            errores = self.etapa_actual.validar_neurona(neurona)
            if errores:
                raise ValueError("\n".join(errores))
        neurona.save(self.vault_path)

    def consultar(self, pregunta: str, llm=None, **kwargs) -> str:
        """Atajo de alto nivel: indexa el vault y responde la pregunta."""
        from cerebro.rag.indexador import Indexador
        from cerebro.rag.razonador import Razonador
        from cerebro.rag.comunicador import ComunicadorRAG
        indexador = Indexador(self.vault_path)
        indexador.indexar()
        razonador = Razonador(indexador.grafo)
        comunicador = ComunicadorRAG(indexador, razonador, llm=llm)
        return comunicador.consultar(pregunta, **kwargs)

    # --- CRUD ---

    def cargar_neurona(self, significante):
        from cerebro.core.neurona import Neurona
        path = os.path.join(self.vault_path, f"{significante}.md")
        if not os.path.exists(path):
            return None
        return Neurona.load(path)

    def listar_neuronas(self):
        from cerebro.core.neurona import Neurona
        archivos = sorted(glob.glob(os.path.join(self.vault_path, "*.md")))
        neuronas = []
        for path in archivos:
            try:
                neuronas.append(Neurona.load(path))
            except Exception:
                pass
        return neuronas

    def eliminar_neurona(self, significante):
        path = os.path.join(self.vault_path, f"{significante}.md")
        if os.path.exists(path):
            os.remove(path)
            return True
        return False

    def _contar_por_tipo(self, tipo) -> int:
        from cerebro.core.neurona import Neurona
        count = 0
        for path in glob.glob(os.path.join(self.vault_path, "*.md")):
            try:
                n = Neurona.load(path)
                if n.post.metadata.get("tipo") == tipo:
                    count += 1
            except Exception:
                pass
        return count
