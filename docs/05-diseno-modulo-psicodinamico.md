# 05 - Diseño del Módulo Psicodinámico (Fase 2)

En la Fase 2, el Cerebro Artificial supera la Etapa Sensoriomotora y entra en la **Etapa Preoperacional**, en la cual despierta su Motor Psicodinámico. El sistema ya no solo graba pasivamente, sino que **intenta activamente conectar** sus memorias usando la teoría psicoanalítica de Freud.

## Los Tres Agentes del Motor

El `MotorPsicodinamico` orquesta la interacción entre tres entidades cada vez que nace un nuevo "símbolo" (neurona):

### 1. El Ello (Id)
- Representa los instintos primitivos y la urgencia de conexión.
- **Lógica:** Al recibir una neurona nueva, el Ello escanea todo el Vault buscando la neurona con el mayor `estado_energetico` (el objeto de deseo más fuerte). Propone un enlace bidireccional de manera impulsiva, sin importarle la coherencia.

### 2. El Superyó (Superego)
- Representa las reglas internalizadas, la lógica estricta y las prohibiciones.
- **Lógica:** Recibe la propuesta del Ello y la evalúa contra una lista de reglas configurables (guardadas en `superyo_rules.yaml`). 
  - Regla 1: No autoenlaces (evita redundancia estructural).
  - Regla 2: No contradicciones (evita enlazar algo con aquello de lo que busca diferenciarse semánticamente - Saussure).
- Si la regla se rompe, el Superyó **veta** el enlace.

### 3. El Yo (Ego)
- Representa la mediación y el principio de realidad. Es el ejecutor material.
- **Lógica:** 
  - Si el Superyó aprueba, el Yo escribe físicamente el enlace `[[...]]` en el archivo `.md`.
  - **Manejo del Conflicto:** Si el Superyó rechaza, la tensión entre el impulso del Ello y la prohibición del Superyó no se borra. El Yo crea una neurona nueva, de orden superior, llamada `conflicto_X_vs_Y.md` que documenta esta tensión y le asigna una gran carga energética. Así nace el conocimiento complejo.

## La Regla de Transición
El cerebro avanza de `EstadoSensoriomotor` a `EstadoPreoperacional` automáticamente cuando ha acumulado suficiente experiencia base (ej. 3 esquemas sensoriomotores). A partir de ese momento, toda nueva interacción es procesada como símbolo por el Motor Psicodinámico.
