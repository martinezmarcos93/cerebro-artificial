from cerebro.psicodinamico.ello import Ello
from cerebro.psicodinamico.superyo import Superyo
from cerebro.psicodinamico.yo import Yo

class MotorPsicodinamico:
    def __init__(self, cerebro):
        self.ello = Ello(cerebro)
        self.superyo = Superyo()
        self.yo = Yo(cerebro)

    def procesar_nacimiento(self, neurona_nueva):
        """
        Cuando nace una neurona o esquema nuevo, el motor intenta integrarla 
        generando un enlace de forma automática si las reglas lo permiten.
        """
        destino_propuesto = self.ello.proponer_enlace(neurona_nueva)
        if not destino_propuesto:
            return
            
        print(f"[Motor] Ello propone enlazar '{neurona_nueva.post.metadata.get('significante')}' con '{destino_propuesto.post.metadata.get('significante')}'.")
        
        aprobado, razon = self.superyo.evaluar(neurona_nueva, destino_propuesto)
        
        if aprobado:
            self.yo.ejecutar_enlace(neurona_nueva, destino_propuesto)
        else:
            self.yo.crear_conflicto(neurona_nueva, destino_propuesto, razon)
