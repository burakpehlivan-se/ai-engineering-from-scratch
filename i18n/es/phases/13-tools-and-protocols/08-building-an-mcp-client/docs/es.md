# Construir un cliente MCP  Descubrimiento, invocación, gestión de sesiones

> La mayoría de los contenidos de MCP envían tutoriales de servidor y agitan una mano al cliente. El código del cliente es donde vive la orquestación dura: desove de procesos, negociación de capacidades, lista de herramientas que se fusionan a través de múltiples servidores, muestreo de llamadas de regreso, reconexión y resolución de colisión en el espacio de nombres. Esta lección construye un cliente multi-servidor que eleva tres servidores MCP diferentes en un espacio de nombres de herramientas plano para el modelo.

**Type:** Build
**Languages:** Python (stdlib, multi-server MCP client)
**Prerequisites:** Phase 13 · 07 (building an MCP server)
**Time:** ~75 minutes

## Objetivos de aprendizaje

- Desarrollar un servidor MCP como un proceso infantil, completo `initialize`, y enviar un `notifications/initialized`¿ Qué ?
- Mantener el estado de sesión por servidor (capacidades, lista de herramientas, identificación de notificación vista por última vez).
- Combine listas de herramientas en múltiples servidores en un solo espacio de nombres con manejo de colisiones.
- Envía una llamada de herramienta al servidor que la posee y reajusta la respuesta.

## El problema

Un host de agente real (Claude Desktop, Cursor, Goose, Gemini CLI) carga varios servidores MCP a la vez. Un usuario puede tener un servidor del sistema de archivos, un servidor Postgres y un servidor GitHub que se ejecutan simultáneamente.

1. Descargar cada servidor.
2. Apetecen las manos de forma independiente.
3. Llamé`tools/list`en cada uno y aplanar el resultado.
4. Cuando el modelo emite `notes_search`, buscarlo en el espacio de nombres fusionado y la ruta al servidor correcto.
5. Manejar las notificaciones de cualquier servidor (`tools/list_changed`) sin bloquear.
6. Reconectarse en caso de fallas de transporte.

La rotación manual de todo eso es lo que separa "juego" de "utilizable". Los SDK oficiales envuelven esto, pero el modelo mental tiene que ser tuyo.

## El concepto

### Desove de procesos infantiles

`subprocess.Popen`con`stdin=PIPE, stdout=PIPE, stderr=PIPE`- El juego .`bufsize=1`y utilizar el modo de texto para las lecturas línea por línea. Cada servidor es un proceso; el cliente tiene uno `Popen`manejo por servidor.

### Estado de sesión por servidor

¿ Qué es esto ?`Session`Objeto por servidor contiene:

- `process` el mango Popen.
- `capabilities` lo que el servidor declaró en `initialize`¿ Qué ?
- `tools` el último `tools/list`el resultado.
- `pending` mapa de la identificación de la solicitud a una promesa/futuro esperando la respuesta.

Las solicitudes son sincronizadas por naturaleza;`tools/call`Envía a servidor A mientras el servidor B está en medio de la llamada no debe bloquear.

### Espacio de nombres fusionado

Cuando el cliente ve la lista de herramientas agregadas, los nombres pueden chocar.`search`El cliente tiene tres opciones:

1. **Prefix by server name.** `notes/search`¿ Qué ?`files/search`- Claros pero feos.
2. **Silent first-come.**Más tarde del servidor `search`Es peligroso, esconde colisiones.
3. **Collision rejection.**Rechazar la carga del segundo servidor, notificar al usuario.

Claude Desktop utiliza prefijo por servidor. Cursor utiliza rechazo de colisión con un error claro. VS Code MCP también adopta prefijo por servidor.

### Enrutamiento

Después de la fusión, un mapa de la mesa de envío `tool_name -> session`. El modelo emite una llamada por nombre; el cliente encuentra la sesión y escribe una `tools/call`mensaje al SDN de ese servidor, y luego espera la respuesta.

### Recuperación de muestras

Si el servidor declaró el `sampling`capacidad en `initialize`, puede enviar`sampling/createMessage`solicitar al cliente que ejecute su LLM. El cliente debe:

1. Bloquear las solicitudes adicionales a ese servidor hasta que se resuelva la muestra, o bloquear la tubería si su implementación admite la concurrencia.
2. Llame a su proveedor de LLM.
3. Envía la respuesta al servidor.

La lección 11 abarca el muestreo de extremo a extremo.

### Manejo de las notificaciones

`notifications/tools/list_changed`significa re-llamada `tools/list`- ¿ Qué ?`notifications/resources/updated`Las notificaciones no deben producir respuestas  no intentar acogerlos.

Un error común del cliente: bloquear el bucle de lectura en`tools/call`Mientras que una notificación se encuentra en la corriente. Utilice un hilo de lector de fondo que empuja cada mensaje a una cola; el hilo principal desguaza y envía.

### Reconexión

El transporte puede fallar: el servidor se ha estrellado, el sistema operativo ha matado el proceso, la tubería de estudio se ha roto. El cliente detecta EOF en el estado y trata la sesión como muerta. Opciones:

- Reinicie silenciosamente el servidor y vuelve a apretar la mano.
- Superficie el fallo al usuario. Está bien para servidores de estado con sesiones visibles por el usuario.

La fase 13 · 09 cubre la semántica de reconexión HTTP en transmisión; el estudio es más simple.

### Identificación de mantenimiento y sesión

El HTTP en streaming utiliza un `Mcp-Session-Id`El estudio no tiene un ID de sesión  la identidad del proceso ES la sesión. los ping de mantenimiento son opcionales; las tuberías de estudio no se rompen bajo inactividad.

```figure
tp-client-merge
```

## Usalo

`code/main.py`Los servidores de Python son otros procesos de Python que ejecutan los contestadores de juguetes (sin LLM real). ejecuta para ver:

- Tres inicializaciones, cada una con su propio conjunto de capacidades.
- Tres .`tools/list`los resultados se fusionaron en un espacio de nombres de 7 herramientas.
- Una decisión de enrutamiento basada en el nombre de la herramienta.
- Una colisión impedida por el prefijo del espacio de nombres.

Qué ver:

- El `Session`la clase de datos mantiene el estado por servidor limpio.
- El hilo lector de fondo desguaza cada línea en stdout sin bloquear el hilo principal.
- La mesa de envío es simple.`dict[str, Session]`¿ Qué ?
- El manejo de colisiones es explícito: cuando dos servidores declaran el mismo nombre, el último se renombre con un prefijo.

## Envío

Esta lección produce`outputs/skill-mcp-client-harness.md`. Dado una lista declarativa de servidores MCP (nombre, comando, args), la habilidad produce un arnés que los genera, fusiona listas de herramientas y envía una función de enrutamiento con resolución de colisión.

## Los ejercicios

1. - ¿ Qué ?`code/main.py`Matar uno de los procesos del servidor simulado con un SIGTERM y observar cómo el cliente detecta la EOF y marca esa sesión como muerta.

2. Implemente el prefijo de espacio de nombres. Cuando dos servidores exponen `search`, renombrar el segundo como `<server>/search`Actualizar la tabla de envío y verificar correctamente la ruta de las llamadas de la herramienta.

3. Añadir un backup de estilo pool de conexión para reiniciar el servidor: backup exponencial en fallas consecutivas, límite a 30 segundos, emitir una notificación al usuario después de tres fallas.

4. Esbozar un cliente que admita 100 servidores MCP simultáneos. ¿Qué estructura de datos reemplaza el simple dictado de envío? (sugerencia: trie para el espaciamiento de nombres de prefijos, más una métrica para el conteo de herramientas por servidor).

5. Portar el cliente al SDK oficial de MCP Python.`stdio_client`y `ClientSession`El código debe reducirse de ~ 200 líneas a ~ 40 líneas mientras se conserva el enrutamiento multi-servidor.

## Términos clave

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| MCP client | "The agent host" | Process that spawns servers and orchestrates tool calls |
| Session | "Per-server state" | Capabilities, tool list, and pending-request bookkeeping |
| Merged namespace | "One tool list" | Flat set of tool names across all active servers |
| Namespace collision | "Two servers same tool" | Client must prefix, reject, or first-come the duplicate |
| Routing | "Who gets this call?" | Dispatch from tool name to owning server |
| Background reader | "Non-blocking stdout" | Thread or task that drains server stdout into a queue |
| Sampling callback | "LLM-as-a-service" | Client handler for `sampling/createMessage` from server |
| `notifications/*_changed` | "Primitive mutated" | Signal the client must re-discover or re-read |
| Reconnection policy | "When server dies" | Restart semantics when transport fails |
| Stdio session | "Process = session" | No session id; child process lifetime is the session |

## Leer más

- [Model Context Protocol — Client spec](https://modelcontextprotocol.io/specification/2025-11-25/client) comportamiento canónico del cliente
- [MCP — Quickstart client guide](https://modelcontextprotocol.io/quickstart/client) tutorial de cliente de mundo hola con el SDK Python
- [MCP Python SDK — client module](https://github.com/modelcontextprotocol/python-sdk) referencia `ClientSession`y `stdio_client`
- [MCP TypeScript SDK — Client](https://github.com/modelcontextprotocol/typescript-sdk) TS paralelo
- [VS Code — MCP in extensions](https://code.visualstudio.com/api/extension-guides/ai/mcp) cómo VS Code multiplica múltiples servidores MCP en un único editor host
