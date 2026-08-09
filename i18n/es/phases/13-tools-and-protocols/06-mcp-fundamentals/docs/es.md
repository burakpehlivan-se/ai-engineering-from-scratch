# Fundamentos del MCP  Primitivos, Ciclo de Vida, Base JSON-RPC

> Cada integración antes de MCP fue una sola vez. El Protocolo Contextual Modelo, lanzado por primera vez por Anthropic en noviembre de 2024 y ahora administrado por la Fundación de Inteligencia Artificial Agentic de la Fundación Linux, estandariza el descubrimiento y la invocación para que cualquier cliente pueda hablar con cualquier servidor. La especificación 2025-11-25 nombra seis primitivas (tres servidores, tres clientes), un ciclo de vida de tres fases y un formato de cable JSON-RPC 2.0. Aprenda eso y el resto del capítulo del MCP de esta fase se convierte en lectura.

**Type:** Learn
**Languages:** Python (stdlib, JSON-RPC parser)
**Prerequisites:** Phase 13 · 01 through 05 (the tool interface and function calling)
**Time:** ~45 minutes

## Objetivos de aprendizaje

- Nombre de las seis primitivas de MCP (herramientas, recursos, instrucciones en el servidor; raíces, muestreo, elicitación en el cliente) y dar un caso de uso cada uno.
- Caminar a través del ciclo de vida de tres fases (iniciar, operar, cerrar) y indicar quién envía qué mensaje en cada fase.
- Analizar y emitir envelopes de solicitud, respuesta y notificación JSON-RPC 2.0.
- Explica qué capacidad negocia en `initialize`es y lo que rompe sin ella.

## El problema

Antes de MCP, cada agente que usaba herramientas tenía su propio protocolo. Cursor tenía un sistema de herramientas en forma de MCP pero incompatible. Claude Desktop se envió con otro. La extensión Copilot de VS Code tenía una tercera. Un equipo que construyó una herramienta de consulta Postgres escribió la misma herramienta tres veces, cada una a la API de un host diferente.

El resultado fue una explosión cámbrida de integraciones únicas y un techo en la velocidad del ecosistema.

MCP corrige esto estandarizando el formato de cable. Un solo servidor MCP funciona en cada cliente MCP: Claude Desktop, ChatGPT, Cursor, VS Code, Gemini, Goose, Zed, Windsurf, 300+ clientes para abril de 2026. 110M descargas mensuales de SDK. 10.000+ servidores públicos. La Fundación Linux tomó la administración en diciembre de 2025 bajo la nueva Fundación de IA Agentic.

La revisión de las especificaciones utilizada en esta fase es **2025-11-25**. Añade tareas de sincronización (SEP-1686), elicitación de modo URL (SEP-1036), muestreo con herramientas (SEP-1577), consentimiento de alcance incremental (SEP-835), y semántica de indicador de recursos OAuth 2.1.

## El concepto

### Tres servidores primitivos

1. **Tools.**Acciones de llamada. El mismo ciclo de cuatro pasos de la Fase 13 · 01.
2. **Resources.**Datos expuestos. Contenido de sólo lectura direccionable por URI: `file:///path`¿ Qué ?`db://query/...`, esquemas personalizados.
3. **Prompts.**Templates reutilizables. Slash-comandos en la interfaz de usuario del host; servidor suministra la plantilla, cliente llena argumentos.

### Tres primitivas de cliente

4. **Roots.**El servidor puede tocar el conjunto de URI. El cliente los declara; el servidor los respeta.
5. **Sampling.**El servidor solicita que el modelo del cliente realice una finalización. Habilita los bucles de agente alojados en el servidor sin claves API del lado del servidor.
6. **Elicitation.**El servidor pide al usuario del cliente una entrada estructurada en medio del vuelo.

Cada capacidad en el MCP pertenece exactamente a uno de estos seis.

### Formatos de cable: JSON-RPC 2.0

Cada mensaje es un objeto JSON con estos campos:

- Solicitudes: `{jsonrpc: "2.0", id, method, params}`¿ Qué ?
- Respuestas: `{jsonrpc: "2.0", id, result | error}`¿ Qué ?
- Notificaciones: `{jsonrpc: "2.0", method, params}`No , no .`id`No se espera respuesta.

La especificación base tiene ~15 métodos, agrupados por primitivos.

- `initialize`- ¿ Qué ?`initialized`¿Qué es eso ?
- `tools/list`¿ Qué ?`tools/call`
- `resources/list`¿ Qué ?`resources/read`¿ Qué ?`resources/subscribe`
- `prompts/list`¿ Qué ?`prompts/get`
- `sampling/createMessage`(servidor a cliente)
- `notifications/tools/list_changed`¿ Qué ?`notifications/resources/updated`¿ Qué ?`notifications/progress`

### Ciclo de vida de tres fases

**Phase 1: initialize.**

El cliente envía`initialize`con su `capabilities`y `clientInfo`El servidor responde con su propio .`capabilities`¿ Qué ?`serverInfo`, y la versión especifica que habla.`notifications/initialized`Desde ahora, cada lado puede enviar peticiones por las capacidades negociadas.

**Phase 2: operation.**

En bidirección. Llama el cliente.`tools/list`para descubrir, entonces `tools/call`El servidor puede enviar`sampling/createMessage`Si se declara esa capacidad. El servidor puede enviar`notifications/tools/list_changed`Cuando su conjunto de herramientas mude.`notifications/roots/list_changed`cuando el usuario cambia el alcance de la raíz.

**Phase 3: shutdown.**

En MCP no hay un método de cierre estructurado; el transporte (studio o Streamable HTTP, Fase 13 · 09) lleva la señal de fin de conexión.

### Negociación de la capacidad

`capabilities`en el `initialize`El contrato es el apretón de manos. Ejemplo de un servidor:

```json
{
  "tools": {"listChanged": true},
  "resources": {"subscribe": true, "listChanged": true},
  "prompts": {"listChanged": true}
}
```

El servidor declara que puede emitir .`tools/list_changed`notificaciones y apoyo `resources/subscribe`El cliente acepta declarando su propio:

```json
{
  "roots": {"listChanged": true},
  "sampling": {},
  "elicitation": {}
}
```

Si el cliente no declara `sampling`, el servidor no debe llamar`sampling/createMessage`. Simétrico: si el servidor no declara `resources.subscribe`, el cliente no debe intentar suscribirse.

Esto es lo que evita la deriva del ecosistema. Un cliente que no admite el muestreo sigue siendo un cliente MCP válido; un servidor que no llama `sampling`Es un servidor MCP válido, pero no lo usan juntos.

### Contenido estructurado y formas de error

`tools/call`devuelve un `content`conjunto de bloques tipografados: `text`¿ Qué ?`image`¿ Qué ?`resource`La fase 13 · 14 añade las aplicaciones de MCP (`ui://`La aplicación de la interfaz interactiva) a esa lista.

Los errores utilizan códigos de error JSON-RPC. Las adiciones definidas por especificaciones: `-32002`"Resource no encontrado",`-32603`"Erro interno", más datos de error específicos de MCP como `error.data`¿ Qué ?

### Capacidades del cliente frente a detalles de llamada de la herramienta

Una confusión común:`capabilities.tools`El cliente puede utilizar las herramientas de la lista de cambios de la lista de herramientas, pero no puede utilizar las herramientas de la lista de herramientas de la lista de herramientas.

### ¿Por qué JSON-RPC y no REST?

JSON-RPC 2.0 (2010) es un protocolo bidireccional ligero. REST es iniciado por el cliente. MCP necesitaba mensajes iniciados por el servidor (muestras, notificaciones), por lo que JSON-RPC con su forma de solicitud / respuesta simétrica era un ajuste natural. JSON-RPC también compone limpiamente sobre el estudio y WebSocket / HTTP en streaming sin reinventar la forma de solicitud de HTTP.

```figure
mcp-tool-call
```

## Usalo

`code/main.py`envían un parser y emisor JSON-RPC 2.0 mínimo, luego camina el `initialize`¿ Qué es esto ?`tools/list`¿ Qué es esto ?`tools/call`¿ Qué es esto ?`shutdown`Se trata de un sistema de información que permite a los usuarios de información de forma manual, imprimir cada mensaje.

Qué ver:

- `initialize`La respuesta ha sido `serverInfo`y `protocolVersion: "2025-11-25"`¿ Qué ?
- `tools/list`devuelve un `tools`array; cada entrada tiene `name`¿ Qué ?`description`¿ Qué ?`inputSchema`¿ Qué ?
- `tools/call`usos `params.name`y `params.arguments`¿ Qué ?
- La respuesta`content`es una matriz de `{type, text}`Bloques.

## Envío

Esta lección produce`outputs/skill-mcp-handshake-tracer.md`. Dado una transcripción de estilo pcap de una interacción cliente-servidor MCP, la habilidad anota cada mensaje con qué primitivo, qué fase del ciclo de vida y de qué capacidad depende.

## Los ejercicios

1. - ¿ Qué ?`code/main.py`. Identificar la línea donde se realiza la negociación de capacidades y describir lo que cambiaría si el servidor no declarara `tools.listChanged`¿ Qué ?

2. Extenda el parser para manejar`notifications/progress`. La forma del mensaje: `{method: "notifications/progress", params: {progressToken, progress, total}}`- Emírese mientras se está haciendo .`tools/call`está en progreso y confirme que el procesador del cliente mostraría una barra de progreso.

3. Lea la especificación MCP 2025-11-25 de arriba a abajo  el documento completo es de aproximadamente 80 páginas. Identifique la bandera de capacidad que la mayoría de los servidores NO necesitan.

4. Esbozo en papel el primitivo una característica hipotética "cron trabajo" pertenecería a. (Intenta: el servidor quiere que el cliente para invocarlo en un tiempo programado. Ninguno de los seis primitivos encajan hoy.)

5. Parsear un registro de sesión desde un servidor MCP abierto en GitHub. Cuente las solicitudes frente a la respuesta frente a los mensajes de notificación. Compute qué fracción del tráfico es ciclo de vida frente a la operación.

## Términos clave

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| MCP | "Model Context Protocol" | Open protocol for model-to-tool discovery and invocation |
| Server primitive | "What a server exposes" | tools (actions), resources (data), prompts (templates) |
| Client primitive | "What a client lets servers use" | roots (scope), sampling (LLM callbacks), elicitation (user input) |
| JSON-RPC 2.0 | "The wire format" | Symmetric request/response/notification envelopes |
| `initialize` handshake | "Capability negotiation" | First message pair; servers and clients declare features they support |
| `tools/list` | "Discovery" | Client asks server for its current tool set |
| `tools/call` | "Invocation" | Client asks server to execute a tool with arguments |
| `notifications/*_changed` | "Mutation events" | Server tells client that its primitive list has changed |
| Content block | "Typed result" | `{type: "text" \| "image" \| "resource" \| "ui_resource"}` in tool result |
| SEP | "Spec Evolution Proposal" | Named draft proposal (e.g. SEP-1686 for async Tasks) |

## Leer más

- [Model Context Protocol — Specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25) el documento de especificaciones canónicas
- [Model Context Protocol — Architecture concepts](https://modelcontextprotocol.io/docs/concepts/architecture) el modelo mental de seis primitivas
- [Anthropic — Introducing the Model Context Protocol](https://www.anthropic.com/news/model-context-protocol) Noviembre 2024 puesta en marcha
- [MCP blog — First MCP anniversary](https://blog.modelcontextprotocol.io/posts/2025-11-25-first-mcp-anniversary/) Retrospectiva de un año y cambios de especificaciones para 2025-11-25
- [WorkOS — MCP 2025-11-25 spec update](https://workos.com/blog/mcp-2025-11-25-spec-update) resumen de las SEP-1686, 1036, 1577, 835 y 1724
