# Recursos y instrucciones de MCP  Exposición de contexto más allá de las herramientas

> Las herramientas obtienen el 90% de la atención de MCP. Las otras dos primitivas del servidor resuelven diferentes problemas. Los recursos exponen los datos para la lectura; las instrucciones exponen las plantillas reutilizables como comandos de corte. Muchos servidores deben usar recursos en lugar de envolver las lecturas en herramientas, y las instrucciones en lugar de flujos de trabajo de codificación dura en las instrucciones del cliente. Esta lección nombra la regla de decisión y recorre el proceso de la instrucción.`resources/*`y `prompts/*`mensajes.

**Type:** Build
**Languages:** Python (stdlib, resource + prompt handler)
**Prerequisites:** Phase 13 · 07 (MCP server)
**Time:** ~45 minutes

## Objetivos de aprendizaje

- Decide entre exponer una capacidad como herramienta, recurso o una solicitud para un dominio determinado.
- Implementación `resources/list`¿ Qué ?`resources/read`¿ Qué ?`resources/subscribe`y manejar .`notifications/resources/updated`¿ Qué ?
- Implementación `prompts/list`y `prompts/get`con plantillas de discusión.
- Reconocer cuando el host aparece las instrucciones como comandos de corte vs contexto de inyección automática.

## El problema

Un servidor MCP ingenuo para una aplicación de notas expone todo como herramientas: `notes_read`¿ Qué ?`notes_list`¿ Qué ?`notes_search`Esto envuelve todos los datos de acceso en una llamada de herramienta basada en el modelo.

- El modelo debe decidir si debe llamar o no.`notes_read`para cada consulta que pueda beneficiarse del contexto.
- El contenido de lectura única no puede ser suscrito o transmitido al panel lateral del host.
- Las interfaces de usuario del cliente (el panel de adjuntos de recursos de Claude Desktop, el seleccionador de "Incluir archivos" de Cursor) no pueden mostrar los datos.

La división derecha: exponer datos como recurso, exponer acciones mutantes o computadas como herramientas, exponer flujos de trabajo reutilizables en múltiples pasos como instrucciones.

## El concepto

### Herramientas vs recursos vs instrucciones  la regla de decisión

| Capability | Primitive |
|------------|-----------|
| User wants to search, filter, or transform data | tool |
| User wants the host to include this data as context | resource |
| User wants a templated workflow they can re-run | prompt |

Guía: si el modelo se beneficiaría de llamarlo en cada consulta relacionada, es una herramienta. Si el usuario se beneficiaría de unirse a una conversación, es un recurso. Si un flujo de trabajo completo de varios pasos es la unidad que el usuario quiere reutilizar, es un prompt.

### Recursos

`resources/list`retorno `{resources: [{uri, name, mimeType, description?}]}`- ¿ Qué ?`resources/read`¿ Qué es ?`{uri}`y los retornos `{contents: [{uri, mimeType, text | blob}]}`¿ Qué ?

Las URI pueden ser cualquier cosa que pueda ser dirigida:

- `file:///Users/alice/notes/mcp.md`
- `postgres://my-db/query/SELECT ...`
- `notes://note-14`(regimen aduanero)
- `memory://session-2026-04-22/recent`(específico para el servidor)

`contents[]`soporta tanto texto como binario.`blob`como una cadena codificada base64 más un `mimeType`¿ Qué ?

### Suscripciones a los recursos

Declarar`{resources: {subscribe: true}}`En las capacidades. Llamadas del cliente.`resources/subscribe {uri}`El servidor envía .`notifications/resources/updated {uri}`Cuando el recurso cambia, el cliente vuelve a leer.

Caso de uso: un servidor de notas cuyos recursos son archivos en disco; un monitor de archivos activa las notificaciones de actualización; Claude Desktop vuelve a colocar el archivo en contexto cuando se edita fuera del host.

### Modelos de recursos (2025-11-25 añadido)

`resourceTemplates`dejar que exponga un patrón de URI parametrizado: `notes://{id}`con`id`El cliente puede completar automáticamente las identidades en el selector de recursos.

### Las instrucciones

`prompts/list`retorno `{prompts: [{name, description, arguments?}]}`- ¿ Qué ?`prompts/get`¿ Qué es ?`{name, arguments}`y los retornos `{description, messages: [{role, content}]}`¿ Qué ?

Un prompt es una plantilla que llena una lista de mensajes que el host alimenta su modelo. Por ejemplo, un `code_review`¿ Qué es lo que hace?`file_path`argumentos y devuelve una secuencia de tres mensajes: un mensaje del sistema, un mensaje del usuario con el cuerpo de archivo y un asistente de inicio con una plantilla de razonamiento.

### Anfitriones y avisos

Claude Desktop, VS Code y Cursor exponen las instrucciones como comandos de corte en la interfaz de usuario de chat.`/code_review`El servidor de la solicitud es el contrato entre "cortoacto de usuario" y "interrumpto completo enviado al modelo".

No todos los clientes admiten las instrucciones todavía. Un servidor con capacidad de instrucción declarada pero un cliente sin apoyo inmediato simplemente no verá los comandos de slash.

### La notificación de "cambio de lista"

Tanto los recursos como las instrucciones emiten`notifications/list_changed`Cuando el conjunto mueve, un servidor de notas que acaba de importar 20 notas nuevas emite.`notifications/resources/list_changed`El cliente vuelve a llamar.`resources/list`para recoger las adiciones.

### Convenciones sobre el tipo de contenido

Para texto: `mimeType: "text/plain"`¿ Qué ?`text/markdown`¿ Qué ?`application/json`¿ Qué ?
Para binario: `image/png`¿ Qué ?`application/pdf`, más el `blob`campo.
Para las aplicaciones MCP (lección 14): `text/html;profile=mcp-app`en un `ui://`- ¿Qué es eso?

### Recursos dinámicos

Un URI de recurso no tiene que corresponder a un archivo estático. `notes://recent`puede devolver las últimas cinco notas en cada lectura. `db://query/users/active`El servidor es libre de calcular el contenido dinámicamente.

Regla: si el cliente puede almacenar en caché por URI, el URI debe ser estable. Si el cálculo es de una sola toma, el URI debe incluir un sello de tiempo o nonce para que el caché del cliente no se desprenda.

### Suscripciones frente a encuestas

Los clientes con suscripción pueden recibir el push del servidor a través de `notifications/resources/updated`Los clientes de pre-subscripción o hosts que no lo admiten sondeo por re-lectura. Ambos son conformes con las especificaciones. La declaración de capacidad del servidor le dice al cliente a la que admite.

Costo de suscripciones: estado por sesión en el servidor (quién está suscrito a qué). Mantenga el conjunto de suscripciones limitado; los clientes desconectados deben terminar el tiempo.

### Las instrucciones vs instrucciones del sistema

Las instrucciones en MCP no son instrucciones del sistema. Las instrucciones del sistema del host (sus propias instrucciones de operación) y las instrucciones de MCP (plantillas suministradas por el servidor invocadas por el usuario) viven lado a lado. Un cliente bien comportado nunca permite que una instrucción del servidor anule su propia instrucción del sistema; las coloca.

```figure
t3-primitive-sort
```

## Usalo

`code/main.py`Extenderá el servidor de notas de la lección 07 con:

- Recursos por nota (`notes://note-1`, etc.) con `resources/subscribe`apoyo.
- ¿ Qué es esto ?`review_note`una llamada que se hace a una plantilla de tres mensajes.
- Una simulación de archivo-observador que emite `notifications/resources/updated`cuando se modifique una nota.
- ¿ Qué es esto ?`notes://recent`un recurso dinámico que siempre devuelve las últimas cinco notas.

Ejecutar la demostración para ver el flujo completo.

## Envío

Esta lección produce`outputs/skill-primitive-splitter.md`Dado un servidor MCP propuesto, la habilidad clasifica cada capacidad como herramienta / recurso / prompt con una justificación.

## Los ejercicios

1. - ¿ Qué ?`code/main.py`. Observa la lista inicial de recursos, luego activa una edición de nota y verifica la `notifications/resources/updated`el evento de incendios.

2. Añadir un`resources/list_changed`emisor: cuando se crea una nueva nota, envíe la notificación para que los clientes vuelvan a descubrirla.

3. Diseñar tres instrucciones para un servidor MCP de GitHub: `summarize_pr`¿ Qué ?`triage_issue`¿ Qué ?`release_notes`Cada uno con esquemas de argumentos. El cuerpo de respuesta debe ser ejecutable sin más modificaciones.

4. Tome una herramienta existente en el servidor de la Lección 07 y clasifique si debe permanecer como una herramienta o dividirse en un par de recursos más herramientas.

5. Lea la especificación.`server/resources`y `server/prompts`Secciones. Identificar el campo en `resources/read`que rara vez está poblada pero se apoya en la especificación.`_meta`sobre el contenido de los recursos.

## Términos clave

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| Resource | "Exposed data" | URI-addressable content the host can read |
| Resource URI | "Pointer to data" | Scheme-prefixed identifier (`file://`, `notes://`, etc.) |
| `resources/subscribe` | "Watch for changes" | Client-opt-in server-push updates for a specific URI |
| `notifications/resources/updated` | "Resource changed" | Signal to client that a subscribed resource has new content |
| Resource template | "Parameterized URI" | URI pattern with completion hints for the host picker |
| Prompt | "Slash-command template" | Named multi-message template with argument slots |
| Prompt arguments | "Template inputs" | Typed parameters the host collects before rendering |
| `prompts/get` | "Render template" | Server returns the filled-in message list |
| Content block | "Typed chunk" | `{type: text \| image \| resource \| ui_resource}` |
| Slash-command UX | "User shortcut" | Host surfaces prompts as commands starting with `/` |

## Leer más

- [MCP — Concepts: Resources](https://modelcontextprotocol.io/docs/concepts/resources) URI de recursos, suscripciones y plantillas
- [MCP — Concepts: Prompts](https://modelcontextprotocol.io/docs/concepts/prompts) plantillas rápidas e integración de comandos de corte
- [MCP — Server resources spec 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/server/resources) lleno `resources/*`referencia del mensaje
- [MCP — Server prompts spec 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/server/prompts) lleno `prompts/*`referencia del mensaje
- [MCP — Protocol info site: resources](https://modelcontextprotocol.info/docs/concepts/resources/) Guía comunitaria en expansión en los documentos oficiales
