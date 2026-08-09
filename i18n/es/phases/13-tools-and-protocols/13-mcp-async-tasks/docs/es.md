# Las tareas de sincronización (SEP-1686)  Llamen ahora, traigan después para el trabajo de larga duración

> El trabajo de los agentes reales toma minutos o horas: operaciones de CI, síntesis de investigación profunda, exportaciones de lotes. La herramienta sincrónica llama a dejar caer las conexiones, a tiempo fuera o bloquear la interfaz de usuario. SEP-1686, fusionado en 2025-11-25, agrega una tarea primitiva: cualquier solicitud puede ser aumentada para convertirse en una tarea, y el resultado puede ser obtenido más tarde o transmitido a través de notificaciones estatales. Nota de riesgo de derivación: Las tareas son experimentales hasta el primer semestre de 2026; la superficie del SDK todavía se está diseñando alrededor de la especificación.

**Type:** Build
**Languages:** Python (stdlib, async task state machine)
**Prerequisites:** Phase 13 · 07 (MCP server), Phase 13 · 09 (transports)
**Time:** ~75 minutes

## Objetivos de aprendizaje

- Identificar cuándo promover una herramienta de sincrónica a tarea aumentada (> 30 segundos de trabajo en el lado del servidor).
- Siga el ciclo de vida de la tarea: `working`¿ Qué es esto ?`input_required`¿ Qué es esto ?`completed`- ¿ Qué ?`failed`- ¿ Qué ?`cancelled`¿ Qué ?
- Permanece en estado de tarea para que los accidentes no pierdan trabajo en vuelo.
- Encuestas`tasks/status`y traer .`tasks/result`- Sí, es cierto.

## El problema

¿ Qué es esto ?`generate_report`La herramienta ejecuta una tubería de extracción de varios minutos.

1. Mantenga la conexión abierta durante tres minutos.
2. Regresa inmediatamente con un marcador de lugar, requiere que el cliente encueste un punto final personalizado.
3. Fuego y olvido, sin resultado.

El SEP-1686 añade una cuarta: aumento de tareas.`tools/call`El servidor devuelve inmediatamente una identificación de tarea.`tasks/status`y trae.`tasks/result`El estado del lado del servidor sobrevive a los reinicios.

## El concepto

### Aumento de tareas

Una solicitud se convierte en una tarea al establecer `params._meta.task.required: true`(o `optional: true`El servidor responde inmediatamente con:

```json
{
  "jsonrpc": "2.0", "id": 1,
  "result": {
    "_meta": {
      "task": {
        "id": "tsk_9f7b...",
        "state": "working",
        "ttl": 900000
      }
    }
  }
}
```

`ttl`es la promesa del servidor de mantener el estado; después de ttl el resultado de la tarea se descarta.

### Opción por herramienta

Las anotaciones de herramientas pueden declarar soporte de tareas:

- `taskSupport: "forbidden"` esta herramienta siempre funciona sincrónicamente.
- `taskSupport: "optional"` el cliente puede solicitar un aumento de tarea.
- `taskSupport: "required"` el cliente DEVE utilizar el aumento de tareas.

¿ Qué es esto ?`generate_report`la herramienta sería `required`- ¿ Qué ?`notes_search`la herramienta sería `forbidden`¿ Qué ?

### Estados

```
working  -> input_required -> working  (loop via elicitation)
working  -> completed
working  -> failed
working  -> cancelled
```

La máquina de Estado sólo se añade: una vez `completed`¿ Qué ?`failed`, o`cancelled`, la tarea es terminal.

### Los métodos

- `tasks/status {taskId}` devuelve el estado actual y una pista de progreso.
- `tasks/result {taskId}` bloquea o devuelve 404 si aún no se ha hecho.
- `tasks/cancel {taskId}` Idempotente; estados terminales ignorar.
- `tasks/list` opcional; enumera las tareas activas y recientemente completadas.

### Cambios en el estado de transmisión

Cuando el servidor lo admite, el cliente puede suscribirse a las notificaciones del estado:

```
server -> notifications/tasks/updated {taskId, state, progress?}
```

Los clientes que transmiten en lugar de las encuestas obtienen una mejor experiencia.

### Estado duradero

La especificación requiere que los servidores que declaran que el soporte de tareas persiste en estado. Un error no debe perder resultados completos dentro de ttl. Las almacenes van desde SQLite a Redis hasta el sistema de archivos. El aprovechamiento de la lección 13 utiliza el sistema de archivos.

### Semántica de cancelación

`tasks/cancel`Si la tarea está en medio de ejecución, el servidor intenta detenerse (véase cancelación cooperativa de ejecutores).

### Recuperación de accidente

Cuando el proceso del servidor se reinicie:

1. Carga todos los estados de tarea persistentes.
2. Marca cualquiera .`working`tareas cuyo proceso se terminó como `failed`con error `CRASH_RECOVERY`¿ Qué ?
3. Preservación`completed`- ¿ Qué ?`failed`- ¿ Qué ?`cancelled`por su TTL.

### tareas de sincronización más muestreo

Una tarea puede llamarse por sí misma.`sampling/createMessage`. Así es como funcionan las tareas de investigación de larga duración: el hilo de tareas del servidor muestra el modelo del cliente según sea necesario, mientras que la interfaz de usuario del cliente muestra la tarea como `working`con actualizaciones periódicas del progreso.

### ¿Por qué es experimental?

SEP-1686 fue lanzado en 2025-11-25, pero la hoja de ruta más amplia plantea tres problemas abiertos: primitivas de suscripción duraderas, subtareas (relaciones de tareas padre-hijo) y estandarización de resultados-TTL.

```figure
tp-task-lifecycle
```

## Usalo

`code/main.py`Implementa un almacén de tareas duradero (con soporte de archivo) y un `generate_report`La herramienta que se ejecuta en un hilo de fondo. Los clientes llaman a la herramienta, obtienen un ID de tarea inmediatamente, encuesta `tasks/status`Mientras el trabajador actualiza el progreso, y trae `tasks/result`Cuando se hace. La cancelación funciona; la recuperación de accidente se simula matando el hilo del trabajador y el estado de recarga.

Qué ver:

- El estado de tarea JSON persistió hasta `/tmp/lesson-13-tasks/<id>.json`¿ Qué ?
- Actualizaciones de los hilos de trabajadores `progress`El campo de trabajo, la encuesta muestra que avanza.
- La cancelación por parte del cliente establece un evento; el trabajador verifica y sale temprano.
- El estado recarga en "crash" marca la tarea en vuelo como `failed`con`CRASH_RECOVERY`¿ Qué ?

## Envío

Esta lección produce`outputs/skill-task-store-designer.md`. Dado que una herramienta de larga duración (investigación, construcción, exportación), la habilidad diseña la almacenaje de tareas (forma de estado, ttl, durabilidad), elige la tarea correctaBandería de apoyo y esboza notificaciones de progreso.

## Los ejercicios

1. - ¿ Qué ?`code/main.py`- Empieza un tiro .`generate_report`tarea, estado de la encuesta, luego trae el resultado.

2. Añadir un`tasks/cancel`Verifique si el trabajador lo hace y el estado se convierte en un "proyecto de trabajo".`cancelled`¿ Qué ?

3. Simula la recuperación de accidente: apague el hilo de trabajo, reinicie el cargador y observa la`CRASH_RECOVERY`modo de falla.

4. Extenda la tienda a SQLite. Las ganancias de durabilidad son las mismas; se abren opciones de consulta (lista todas las tareas de la sesión X).

5. Lea la hoja de ruta del MCP para 2026. Identifique el tema abierto relacionado con las tareas que más probablemente afecte al diseño de API del SDK en el próximo año.

## Términos clave

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| Task | "Long-running tool call" | Request augmented with `_meta.task` for async execution |
| SEP-1686 | "Tasks spec" | Spec Evolution Proposal that added Tasks in 2025-11-25 |
| `_meta.task` | "Task envelope" | Per-request metadata containing id, state, ttl |
| taskSupport | "Tool flag" | `forbidden` / `optional` / `required` per tool |
| `tasks/status` | "Poll method" | Fetch current state and optional progress hint |
| `tasks/result` | "Fetch result" | Returns the completed payload or 404 if not yet done |
| `tasks/cancel` | "Stop it" | Idempotent cancellation request |
| ttl | "Retention budget" | Milliseconds the server promises to keep the task state |
| `notifications/tasks/updated` | "State push" | Server-initiated state-change event |
| Durable store | "Crash-safe state" | Filesystem / SQLite / Redis persistence layer |

## Leer más

- [MCP — GitHub SEP-1686 issue](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1686) la propuesta de origen y el debate completo
- [WorkOS — MCP async tasks for AI agent workflows](https://workos.com/blog/mcp-async-tasks-ai-agent-workflows) diseño de un proceso con racionalidad
- [DeepWiki — MCP task system and async operations](https://deepwiki.com/modelcontextprotocol/modelcontextprotocol/2.7-task-system-and-async-operations) Mecánica y máquina de estado
- [FastMCP — Tasks](https://gofastmcp.com/servers/tasks) Modelos de implementación de tareas a nivel de SDK
- [MCP blog — 2026 roadmap](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/) temas abiertos y prioridades para 2026, incluidas las subtareas
