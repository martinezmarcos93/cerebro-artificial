from abc import ABC, abstractmethod


class EtapaPiagetiana(ABC):
    def __init__(self, cerebro):
        self.cerebro = cerebro

    @abstractmethod
    def procesar_interaccion(self, accion, objeto):
        pass

    @abstractmethod
    def tipos_permitidos(self) -> frozenset:
        pass

    @abstractmethod
    def permite_enlaces(self) -> bool:
        pass

    def validar_neurona(self, neurona) -> list:
        errores = []
        tipo = neurona.post.metadata.get("tipo")
        if tipo not in self.tipos_permitidos():
            errores.append(
                f"Tipo '{tipo}' no permitido en etapa '{self.__class__.__name__}'. "
                f"Permitidos: {sorted(self.tipos_permitidos())}"
            )
        if not self.permite_enlaces() and neurona.tiene_enlaces():
            errores.append(
                f"La etapa '{self.__class__.__name__}' no permite enlaces semánticos [[...]]"
            )
        return errores


class EstadoSensoriomotor(EtapaPiagetiana):
    def tipos_permitidos(self) -> frozenset:
        return frozenset(["esquema_sensoriomotor"])

    def permite_enlaces(self) -> bool:
        return False

    def procesar_interaccion(self, accion, objeto):
        significante = f"{accion}_{objeto}"
        from cerebro.core.neurona import Neurona

        neurona = Neurona()
        neurona.post.metadata["id"] = self.cerebro.generar_id()
        neurona.post.metadata["etapa_creacion"] = "sensoriomotora"
        neurona.post.metadata["tipo"] = "esquema_sensoriomotor"
        neurona.post.metadata["significante"] = significante
        neurona.post.metadata["estado_energetico"] = 0.1
        neurona.post.content = f"# {significante}\n\nEsquema sensoriomotor creado por interacción física."

        self.cerebro.guardar_neurona(neurona)
        print(f"[Sensoriomotor] Nuevo esquema creado: {significante}.md")
        self._verificar_transicion()

    def _verificar_transicion(self):
        import glob, os
        archivos = glob.glob(os.path.join(self.cerebro.vault_path, "*.md"))
        if len(archivos) >= 3:
            print("[Transición] El cerebro evolucionó a Estado Preoperacional.")
            self.cerebro.cambiar_etapa(EstadoPreoperacional(self.cerebro))


class EstadoPreoperacional(EtapaPiagetiana):
    def __init__(self, cerebro):
        super().__init__(cerebro)
        from cerebro.psicodinamico.motor import MotorPsicodinamico
        from cerebro.jung.motor_junguiano import MotorJunguiano
        self.motor = MotorPsicodinamico(cerebro)
        import os as _os
        vault_arq = _os.path.join(cerebro.vault_path, "arquetipos")
        self.motor_jung = MotorJunguiano(vault_arquetipos=vault_arq)

    def tipos_permitidos(self) -> frozenset:
        return frozenset(["esquema_sensoriomotor", "simbolo", "conflicto"])

    def permite_enlaces(self) -> bool:
        return True

    def procesar_interaccion(self, accion, objeto):
        significante = f"{accion}_{objeto}"
        from cerebro.core.neurona import Neurona

        neurona = Neurona()
        neurona.post.metadata["id"] = self.cerebro.generar_id()
        neurona.post.metadata["etapa_creacion"] = "preoperacional"
        neurona.post.metadata["tipo"] = "simbolo"
        neurona.post.metadata["significante"] = significante
        neurona.post.metadata["estado_energetico"] = 0.3

        if "agua" in objeto and accion == "tocar":
            neurona.post.metadata["significados_diferenciales"] = ["agarrar_fuego"]

        neurona.post.content = f"# {significante}\n\nSímbolo creado en etapa preoperacional."
        arquetipo = self.motor_jung.vincular(neurona)
        self.cerebro.guardar_neurona(neurona)
        print(f"[Preoperacional] Nuevo símbolo creado: {significante}.md (arquetipo: {arquetipo})")
        self.motor.procesar_nacimiento(neurona)
        self._verificar_transicion()

    def _verificar_transicion(self):
        conflictos = self.cerebro._contar_por_tipo("conflicto")
        if conflictos >= 2:
            print("[Transición] Conflictos acumulados → Operaciones Concretas.")
            self.cerebro.cambiar_etapa(EstadoOperacionesConcretas(self.cerebro))


class EstadoOperacionesConcretas(EtapaPiagetiana):
    def __init__(self, cerebro):
        super().__init__(cerebro)
        from cerebro.psicodinamico.motor import MotorPsicodinamico
        from cerebro.jung.motor_junguiano import MotorJunguiano
        self.motor = MotorPsicodinamico(cerebro)
        import os as _os
        vault_arq = _os.path.join(cerebro.vault_path, "arquetipos")
        self.motor_jung = MotorJunguiano(vault_arquetipos=vault_arq)

    def tipos_permitidos(self) -> frozenset:
        return frozenset(["esquema_sensoriomotor", "simbolo", "concepto", "regla", "conflicto"])

    def permite_enlaces(self) -> bool:
        return True

    def procesar_interaccion(self, accion, objeto):
        significante = f"{accion}_{objeto}"
        from cerebro.core.neurona import Neurona

        neurona = Neurona()
        neurona.post.metadata["id"] = self.cerebro.generar_id()
        neurona.post.metadata["etapa_creacion"] = "operaciones_concretas"
        neurona.post.metadata["tipo"] = "concepto"
        neurona.post.metadata["significante"] = significante
        neurona.post.metadata["estado_energetico"] = 0.5
        neurona.post.metadata["relaciones"] = {"es_un": [], "tiene": []}

        neurona.post.content = (
            f"# {significante}\n\n"
            f"Concepto generado en etapa de Operaciones Concretas.\n\n"
            f"## Relaciones\n"
            f"- **es_un:** *(pendiente de clasificar)*\n"
            f"- **tiene:** *(pendiente de clasificar)*"
        )

        arquetipo = self.motor_jung.vincular(neurona)
        self.cerebro.guardar_neurona(neurona)
        print(f"[Operaciones Concretas] Nuevo concepto: {significante}.md (arquetipo: {arquetipo})")
        self.motor.procesar_nacimiento(neurona)
        self._verificar_transicion()

    def _verificar_transicion(self):
        conceptos = self.cerebro._contar_por_tipo("concepto")
        if conceptos >= 3:
            print("[Transición] Razonamiento abstracto disponible → Operaciones Formales.")
            self.cerebro.cambiar_etapa(EstadoOperacionesFormales(self.cerebro))


class EstadoOperacionesFormales(EtapaPiagetiana):
    def __init__(self, cerebro):
        super().__init__(cerebro)
        from cerebro.psicodinamico.motor import MotorPsicodinamico
        from cerebro.jung.motor_junguiano import MotorJunguiano
        self.motor = MotorPsicodinamico(cerebro)
        import os as _os
        vault_arq = _os.path.join(cerebro.vault_path, "arquetipos")
        self.motor_jung = MotorJunguiano(vault_arquetipos=vault_arq)

    def tipos_permitidos(self) -> frozenset:
        return frozenset(["esquema_sensoriomotor", "simbolo", "concepto", "arquetipo", "conflicto", "regla"])

    def permite_enlaces(self) -> bool:
        return True

    def procesar_interaccion(self, accion, objeto):
        significante = f"hipotesis_{accion}_{objeto}"
        from cerebro.core.neurona import Neurona

        neurona = Neurona()
        neurona.post.metadata["id"] = self.cerebro.generar_id()
        neurona.post.metadata["etapa_creacion"] = "operaciones_formales"
        neurona.post.metadata["tipo"] = "regla"
        neurona.post.metadata["significante"] = significante
        neurona.post.metadata["estado_energetico"] = 0.7

        neurona.post.content = (
            f"# {significante}\n\n"
            f"Hipótesis formal sobre '{accion}' aplicado a '{objeto}'.\n\n"
            f"**Premisa:** *Por establecer mediante razonamiento abstracto.*\n"
            f"**Conclusión tentativa:** *Pendiente de validación.*"
        )

        arquetipo = self.motor_jung.vincular(neurona)
        self.cerebro.guardar_neurona(neurona)
        print(f"[Operaciones Formales] Nueva hipótesis: {significante}.md (arquetipo: {arquetipo})")
        self.motor.procesar_nacimiento(neurona)
