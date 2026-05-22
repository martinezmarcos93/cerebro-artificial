import os
import re

import frontmatter

PATTERN_LINK = re.compile(r'\[\[.+?\]\]')


class Neurona:
    def __init__(self, filepath=None):
        self.filepath = filepath
        self.post = frontmatter.Post("")
        self.post.metadata = {
            "id": "",
            "etapa_creacion": "",
            "tipo": "",
            "arquetipo_vinculado": "",
            "significante": "",
            "significados_diferenciales": [],
            "estado_energetico": 0.0,
            "tags": []
        }

    def tiene_enlaces(self) -> bool:
        if PATTERN_LINK.search(self.post.metadata.get("arquetipo_vinculado", "")):
            return True
        for diff in self.post.metadata.get("significados_diferenciales", []):
            if PATTERN_LINK.search(str(diff)):
                return True
        return bool(PATTERN_LINK.search(self.post.content or ""))

    @classmethod
    def load(cls, filepath):
        neurona = cls(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            neurona.post = frontmatter.load(f)
        return neurona

    def save(self, vault_path=None):
        if not self.filepath and vault_path:
            filename = f"{self.post.metadata.get('significante', 'neurona_anonima').replace(' ', '_')}.md"
            self.filepath = os.path.join(vault_path, filename)
        if not self.filepath:
            raise ValueError("No se especificó un filepath o vault_path para guardar la Neurona.")
        with open(self.filepath, "wb") as f:
            frontmatter.dump(self.post, f)
