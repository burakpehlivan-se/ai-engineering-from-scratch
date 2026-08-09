# Construir un servidor MCP  Python + SDKs de tipoScript

> La mayoría de los tutoriales MCP sólo muestran mundos de saludos de estudio. Un servidor real expone herramientas más recursos más instrucciones, maneja la negociación de capacidades, emite errores estructurados y funciona de la misma manera en los SDK. Esta lección construye un servidor de notas de extremo a extremo: stdlib stdio transport, JSON-RPC despacho, los tres servidores primitivos, y un estilo de función pura que cae en el FastMCP del SDK Python o el SDK TypeScript cuando se gradúa.

**Type:** Build
**Languages:** Python (stdlib, stdio MCP server)
**Prerequisites:** Phase 13 · 06 (MCP fundamentals)
**Time:** ~75 minutes

## Objetivos de aprendizaje

- Implementación `initialize`¿ Qué ?`tools/list`¿ Qué ?`tools/call`¿ Qué ?`resources/list`¿ Qué ?`resources/read`¿ Qué ?`prompts/list`, y `prompts/get`Los métodos.
- Escriba un bucle de envío que lee mensajes JSON-RPC de stdin y escribe respuestas a stdout.
- Emite respuestas de errores estructuradas por la especificación JSON-RPC 2.0 y los códigos adicionales de MCP.
- Graduar una implementación de stdlib en FastMCP (Python SDK) o el SDK de TypeScript sin reescribir la lógica de la herramienta.

## El problema

Antes de poder utilizar un transporte remoto (fase 13 · 09) o una capa auth (fase 13 · 16), necesita un servidor local limpio. local significa stdio: el servidor es generado por el cliente como un proceso hijo, los mensajes fluyen sobre stdin/stdout newline-delimited.

La especificación 2025-11-25 prescribe que los mensajes de estudio se codifican como objetos JSON con una `\n`No hay SSE aquí; SSE era el viejo modo remoto y se está eliminando a mediados de 2026 (el servidor Rovo MCP de Atlassian lo depreció el 30 de junio de 2026; Keboola el 1 de abril de 2026).

Un servidor de notas es una buena forma porque ejerce las tres primitivas del servidor.`notes_create`Los recursos exponen los datos (`notes://{id}`Instrucciones de plantillas de buques (`review_note`La forma de esta lección se generaliza a cualquier dominio.

## El concepto

### Bucle de envío

```
loop:
  line = stdin.readline()
  msg = json.loads(line)
  if has id:
    handle request -> write response
  else:
    handle notification -> no response
```

Tres reglas:

- No imprima nada en stdout que no sea un envase JSON-RPC.
- Cada solicitud debe coincidir con una respuesta que contenga la misma`id`¿ Qué ?
- No se deben responder a las notificaciones.

### Implementación `initialize`

```python
def initialize(params):
    return {
        "protocolVersion": "2025-11-25",
        "capabilities": {
            "tools": {"listChanged": True},
            "resources": {"listChanged": True, "subscribe": False},
            "prompts": {"listChanged": False},
        },
        "serverInfo": {"name": "notes", "version": "1.0.0"},
    }
```

El cliente depende de la capacidad establecida para las funciones de la puerta.

### Implementación `tools/list`y `tools/call`

`tools/list`retorno `{tools: [...]}`con cada entrada que tenga `name`¿ Qué ?`description`¿ Qué ?`inputSchema`- ¿ Qué ?`tools/call`¿ Qué es ?`{name, arguments}`y los retornos `{content: [blocks], isError: bool}`¿ Qué ?

Los bloques de contenido se escriben.

```json
{"type": "text", "text": "Found 2 notes"}
{"type": "resource", "resource": {"uri": "notes://14", "text": "..."}}
{"type": "image", "data": "<base64>", "mimeType": "image/png"}
```

Los errores de herramienta vienen en dos formas. Los errores de nivel de protocolo (método desconocido, parámetros malos) son errores JSON-RPC. Los errores de nivel de herramienta (llamada válida pero la herramienta falló) se devuelven como `{content: [...], isError: true}`Eso permite al modelo ver el fracaso en su contexto.

### Recursos de ejecución

Los recursos son de lectura única por diseño. `resources/list`devuelve un manifiesto; `resources/read`Los URI pueden ser:`file://...`¿ Qué ?`http://...`, o un esquema de costumbre como `notes://`¿ Qué ?

Cuando expones datos como un recurso en lugar de una herramienta:

- El modelo no lo "llamará"; el cliente puede inyectarlo en contexto a petición del usuario.
- Las suscripciones permiten al servidor impulsar las actualizaciones cuando el recurso cambia (fase 13 · 10).
- La fase 13 · 14 se extiende con `ui://`para recursos interactivos.

### Instrucciones de ejecución

Las instrucciones son plantillas con argumentos nombrados. El anfitrión las muestra como comandos de corte.`review_note`¿ Cómo se puede hacer esto ?`note_id`argumentos y producir una plantilla de solicitud de mensajes múltiples que el cliente alimenta a su modelo.

### Las sutilezas del transporte de estudio

- JSON de línea nueva y limitada.
- No se haga un amortiguador.`sys.stdout.flush()`después de cada escrito.
- El cliente controla la vida útil. Cuando el stdin cierre (EOF), salga limpio.
- No maneje SIGPIPE en silencio; ingrese y salga.

### Anotadas

Cada herramienta puede llevar`annotations`que describe las propiedades de seguridad:

- `readOnlyHint: true` lectura pura, seguro para volver a intentarlo.
- `destructiveHint: true` efectos secundarios irreversibles; el cliente debe confirmarlo.
- `idempotentHint: true` las mismas entradas producen las mismas salidas.
- `openWorldHint: true` interactuar con sistemas externos.

El cliente utiliza estos para decidir UX (diálogos de confirmación, indicadores de estado) y enrutamiento (fase 13 · 17).

### Camino de graduación

El servidor de stdlib en `code/main.py`FastMCP (Python) desploma la misma lógica al estilo decorador:

```python
from fastmcp import FastMCP
app = FastMCP("notes")

@app.tool()
def notes_search(query: str, limit: int = 10) -> list[dict]:
    ...
```

El SDK TypeScript tiene una forma equivalente. El camino de graduación es de entrada cuando estás listo; los conceptos (capacidades, envío, bloques de contenido) son los mismos.

```figure
t3-dispatch-loop
```

## Usalo

`code/main.py`es un servidor completo de notas MCP sobre el estudio, sólo stdlib.`initialize`¿ Qué ?`tools/list`¿ Qué ?`tools/call`para tres herramientas (`notes_list`¿ Qué ?`notes_search`¿ Qué ?`notes_create`), `resources/list`y `resources/read`para cada nota, y un `review_note`Puede ejecutarlo mediante el envío de mensajes JSON-RPC:

```
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python main.py
```

Qué ver:

- El despachador es un`dict[str, Callable]`teclado por nombre del método.
- Cada ejecutor de herramientas devuelve una lista de bloques de contenido, no una cadena desnudo.
- `isError: true`se fija cuando el ejecutor levante.

## Envío

Esta lección produce`outputs/skill-mcp-server-scaffolder.md`. Dado un dominio (notas, entradas, archivos, base de datos), la habilidad se basa en un servidor MCP con las herramientas / recursos / instrucciones adecuadas para dividir y el camino de graduación de SDK.

## Los ejercicios

1. - ¿ Qué ?`code/main.py`y conducir con mensajes JSON-RPC construidos a mano.`notes_create`, entonces`resources/read`para recuperar la nueva nota.

2. Añadir un`notes_delete`herramienta con `annotations: {destructiveHint: true}`. Verificar que el cliente aparecería en un diálogo de confirmación (esto requiere un host real; Claude Desktop funciona).

3. Implementación `resources/subscribe`Así que el servidor empuja`notifications/resources/updated`Cuando se modifica una nota, añada una tarea de mantenimiento.

4. Portar el servidor a FastMCP. El archivo Python debe reducirse a menos de 80 líneas. El comportamiento del cable debe ser idéntico; verifique con el mismo arnés de prueba JSON-RPC.

5. Lea la especificación.`server/tools`Sección y identificar un campo de una definición de herramienta no implementada en el servidor de esta lección. (Intenta: hay varios; escoge uno y agregue).

## Términos clave

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| MCP server | "The thing that exposes tools" | Process that speaks MCP JSON-RPC over stdio or HTTP |
| stdio transport | "Child process model" | Server is spawned by client; communicates via stdin/stdout |
| Dispatcher | "Method router" | Map of JSON-RPC method name to handler function |
| Content block | "Tool result chunk" | Typed element in the `content` array of a tool response |
| `isError` | "Tool-level failure" | Signals the tool failed; distinguishes from JSON-RPC error |
| Annotations | "Safety hints" | readOnly / destructive / idempotent / openWorld flags |
| FastMCP | "Python SDK" | Decorator-based higher-level framework on top of the MCP protocol |
| Resource URI | "Addressable data" | `file://`, `db://`, or custom scheme identifying a resource |
| Prompt template | "Slash-command brief" | Server-supplied template with argument slots for host UIs |
| Capability declaration | "Feature toggle" | Per-primitive flags declared in `initialize` |

## Leer más

- [Model Context Protocol — Python SDK](https://github.com/modelcontextprotocol/python-sdk) la implementación de Python de referencia
- [Model Context Protocol — TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk) Implementación de las TS paralelas
- [FastMCP — server framework](https://gofastmcp.com/) API Python de estilo decorador para servidores MCP
- [MCP — Quickstart server guide](https://modelcontextprotocol.io/quickstart/server) Tutorial de extremo a extremo utilizando cualquiera de los SDK
- [MCP — Server tools spec](https://modelcontextprotocol.io/specification/2025-11-25/server/tools) referencia completa para las herramientas/* mensajes
