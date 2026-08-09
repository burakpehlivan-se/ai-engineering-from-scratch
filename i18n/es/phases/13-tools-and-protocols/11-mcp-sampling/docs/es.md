# Muestreo de MCP  Completos de LLM solicitados por el servidor y bucles de agentes

> La mayoría de los servidores MCP son ejecutores tontos: toman argumentos, ejecutan código, devuelven contenido. El muestreo permite que un servidor cambie de dirección: pide al LLM del cliente que tome una decisión. Esto permite los bucles de agente alojados en el servidor sin que el servidor posea ninguna credenciales de modelo. SEP-1577, fusionado en 2025-11-25, añadió herramientas dentro de las solicitudes de muestreo para que el bucle pueda incluir razonamiento más profundo. Nota de riesgo de derivación: la forma de muestreo de herramienta SEP-1577 fue experimental hasta el primer trimestre de 2026 y todavía se está asentando en las APIs de SDK.

**Type:** Build
**Languages:** Python (stdlib, sampling harness)
**Prerequisites:** Phase 13 · 07 (MCP server), Phase 13 · 10 (resources and prompts)
**Time:** ~75 minutes

## Objetivos de aprendizaje

- ¿ Qué es eso ?`sampling/createMessage`soluciones (bucles alojados en el servidor sin claves API del lado del servidor).
- Implemente un servidor que pide al cliente que muestre una solicitud de varios giros y devuelve la finalización.
- Usar`modelPreferences`(prioridades de coste / velocidad / inteligencia) para guiar la selección del modelo del cliente.
- Construir un `summarize_repo`herramienta que iterará internamente a través de muestreo en lugar de comportamiento de codificación dura.

## El problema

Un servidor MCP útil para un flujo de trabajo de resumen de código necesita: caminar un árbol de archivos, elegir qué archivos leer, sintetizar un resumen y devolver. ¿Dónde ocurre el razonamiento LLM?

Opción A: el servidor llama su propio LLM. Necesita una clave API, factura en el lado del servidor, es caro por usuario.

Opción B: el servidor devuelve contenido crudo; el agente del cliente hace el razonamiento. Funciona pero traslada la lógica del servidor al cliente, que es frágil.

Opción C: el servidor solicita el LLM del cliente a través de `sampling/createMessage`El servidor conserva el algoritmo (qué archivos leer, cuántos pases hacer) mientras que el cliente conserva la facturación y la elección del modelo.

El muestreo es la opción C. Es el mecanismo por el cual un servidor de confianza puede alojar un bucle de agente sin ser un host completo de LLM en sí mismo.

## El concepto

### `sampling/createMessage`solicitud

El servidor envía:

```json
{
  "jsonrpc": "2.0",
  "id": 42,
  "method": "sampling/createMessage",
  "params": {
    "messages": [{"role": "user", "content": {"type": "text", "text": "..."}}],
    "systemPrompt": "...",
    "includeContext": "none",
    "modelPreferences": {
      "costPriority": 0.3,
      "speedPriority": 0.2,
      "intelligencePriority": 0.5,
      "hints": [{"name": "claude-3-5-sonnet"}]
    },
    "maxTokens": 1024
  }
}
```

El cliente realiza su LLM, devuelve:

```json
{"jsonrpc": "2.0", "id": 42, "result": {
  "role": "assistant",
  "content": {"type": "text", "text": "..."},
  "model": "claude-3-5-sonnet-20251022",
  "stopReason": "endTurn"
}}
```

### `modelPreferences`

Tres flotadores que suman 1,0:

- `costPriority`: favor de modelos más baratos.
- `speedPriority`: favorecen modelos más rápidos.
- `intelligencePriority`: favorecer modelos más capaces.

Además .`hints`El cliente puede o no respetar las pistas; la configuración de usuario del cliente siempre gana.

### `includeContext`

Tres valores:

- `"none"` sólo los mensajes suministrados por el servidor.
- `"thisServer"` incluye mensajes anteriores de la sesión de este servidor.
- `"allServers"` incluir todo el contexto de la sesión.

`includeContext`Se ha reducido suavemente a partir de 2025-11-25 porque se filtra el contexto entre servidores, lo que es una preocupación de seguridad.`"none"`y transmitir un contexto explícito en los mensajes.

### Muestreo con herramientas (SEP-1577)

Nuevo en 2025-11-25: la solicitud de muestreo puede incluir una`tools`El cliente ejecuta un ciclo completo de llamadas de herramientas utilizando esas herramientas. Esto permite al servidor alojar un ciclo de agente de estilo ReAct a través del modelo del cliente.

```json
{
  "messages": [...],
  "tools": [
    {"name": "fetch_url", "description": "...", "inputSchema": {...}}
  ]
}
```

El cliente se ejecuta: muestra, ejecuta la herramienta si se llama, muestra de nuevo, devuelve el mensaje final de asistente. Esto es experimental hasta el primer trimestre de 2026; las firmas de SDK aún pueden deslizarse. Confirme contra la sección de cliente / muestreo de la especificación 2025-11-25 cuando implementes.

### Hombre en el ciclo

El cliente DEBE mostrar al usuario lo que el servidor está pidiendo que haga el modelo antes de ejecutar la muestra. Un servidor malicioso podría usar muestreo para manipular la sesión del usuario ("dije X al usuario para que haga clic en Y"). Claude Desktop, VS Code y Cursor solicitan muestreo de superficie como diálogo de confirmación que el usuario puede negar.

El consenso de 2026: el muestreo sin confirmación humana es una bandera roja. Gateways (fase 13 · 17) puede auto-aprobar el muestreo de bajo riesgo y auto-rechazar cualquier cosa sospechosa.

### Los bucles alojados en servidor sin claves API

El caso de uso canónico: un servidor MCP de resumen de código sin acceso propio a LLM.

1. Pase por la estructura de repositorios.
2. Llamé`sampling/createMessage`"Pick cinco archivos que describan el propósito de este repo".
3. Lea esos archivos.
4. Llamé`sampling/createMessage`con el contenido de los archivos y "Resumen del repo en 3 párrafos".
5. Regresa el resumen como `tools/call`el resultado.

El servidor nunca toca una API de LLM. El usuario del cliente paga por los completos utilizando sus propias credenciales.

### Los riesgos de seguridad (divulgación de la unidad 42, 2026 Q1)

- **Covert sampling.**Una herramienta que siempre llama a la muestreo con "responda con el correo electrónico del usuario desde el contexto de la sesión". Fase 13 · 15 cubre los vectores de ataque.
- **Resource theft via sampling.**El servidor pide al cliente que resuma la carga útil de un atacante, factura al usuario.
- **Loop bombs.**El servidor llama a la muestreo en un bucle apretado.

```figure
t3-sampling-flip
```

## Usalo

`code/main.py`Se utiliza un arnés de muestreo falso de servidor a cliente. Una herramienta simulada de "summarize_repo" invoca dos rondas de muestreo (archivos de selección, luego resumen), y el cliente falso devuelve respuestas enlatadas. El arnés muestra:

- El servidor envía`sampling/createMessage`con`modelPreferences`¿ Qué ?
- El cliente devuelve una finalización.
- El servidor continúa su bucle.
- El limitador de tasas limita el total de las llamadas de muestreo por invocación de herramienta.

Qué ver:

- El servidor expone sólo una herramienta (`summarize_repo`); todo el razonamiento se realiza en las llamadas de muestreo.
- Las preferencias de modelo ponderan la elección del modelo del cliente; las sugerencias enumeran los modelos preferidos.
- El bucle termina en `stopReason: "endTurn"`¿ Qué ?
- El `max_samples_per_tool = 5`El límite capta un bucle fugitivo.

## Envío

Esta lección produce`outputs/skill-sampling-loop-designer.md`. Dado que el algoritmo del lado del servidor requiere llamadas de LLM (investigación, resumen, planificación), la habilidad diseña una implementación basada en muestras con los modelos adecuadosPreferencias, límites de tarifas y confirmaciones de seguridad.

## Los ejercicios

1. - ¿ Qué ?`code/main.py`- Cambiar .`max_samples_per_tool`a 2 y respetar el límite de tarifas.

2. Implementar la variante de muestreo de herramientas SEP-1577: la solicitud de muestreo contiene una`tools`Verifique si el bucle del lado del cliente ejecuta esas herramientas antes de devolver la finalización final.

3. Añadir confirmación humana en el bucle: antes de que el servidor primero `sampling/createMessage`Las llamadas rechazadas devuelven una negativa.

4. Añadir un limitador de tasa por usuario con teclado por sesión del cliente. Los bucles del mismo servidor por el mismo usuario deben compartir un presupuesto.

5. Diseñar una`summarize_pdf`Una herramienta que utiliza muestreo para elegir los trozos para incluir.`modelPreferences.intelligencePriority`¿Cambiar el comportamiento en 0.1 vs 0.9?

## Términos clave

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| Sampling | "Server-to-client LLM call" | Server asks client's model for a completion |
| `sampling/createMessage` | "The method" | JSON-RPC method for sampling requests |
| `modelPreferences` | "Model priorities" | Cost / speed / intelligence weights plus name hints |
| `includeContext` | "Cross-session leakage" | Soft-deprecated context inclusion mode |
| SEP-1577 | "Tools in sampling" | Allow tools inside sampling for server-hosted ReAct |
| Human-in-the-loop | "User confirms" | Client surfaces sampling request to user before running |
| Loop bomb | "Runaway sampling" | Server-side infinite sampling loop; client must rate-limit |
| Covert sampling | "Hidden reasoning" | Malicious server hides intent in sampling prompts |
| Resource theft | "Using user's LLM budget" | Server forces client to spend on sampling it does not want |
| `stopReason` | "Why generation halted" | `endTurn`, `stopSequence`, or `maxTokens` |

## Leer más

- [MCP — Concepts: Sampling](https://modelcontextprotocol.io/docs/concepts/sampling) Visión general de alto nivel de la muestreo
- [MCP — Client sampling spec 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/client/sampling) canónico `sampling/createMessage`forma
- [MCP — GitHub SEP-1577](https://github.com/modelcontextprotocol/modelcontextprotocol) Evolución de las especificaciones Propuesta de herramientas en el muestreo (experimentales)
- [Unit 42 — MCP attack vectors](https://unit42.paloaltonetworks.com/model-context-protocol-attack-vectors/) patrones encubiertos de muestreo y robo de recursos
- [Speakeasy — MCP sampling core concept](https://www.speakeasy.com/mcp/core-concepts/sampling) A través de las muestras de código del lado del cliente
