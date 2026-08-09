# Aplicaciones de MCP  Recursos interactivos de interfaz de usuario a través de `ui://`

> Las aplicaciones MCP (SEP-1724, oficial 26 de enero de 2026) permiten que una herramienta devuelva un HTML interactivo sandboxed renderizado en línea en Claude Desktop, ChatGPT, Cursor, Goose y VS Code.`ui://`El programa de recursos, el `text/html;profile=mcp-app`MIME, el protocolo de postMessage iframe-sandbox, y la superficie de seguridad que viene con dejar que un servidor haga HTML.

**Type:** Build
**Languages:** Python (stdlib, UI resource emitter), HTML (sample app)
**Prerequisites:** Phase 13 · 07 (MCP server), Phase 13 · 10 (resources)
**Time:** ~75 minutes

## Objetivos de aprendizaje

- Regresa una`ui://`Recursos de una llamada de herramienta y establecer el MIME y los metadatos correctos.
- Declarar la interfaz de usuario asociada de una herramienta con `_meta.ui.resourceUri`¿ Qué ?`_meta.ui.csp`, y `_meta.ui.permissions`¿ Qué ?
- Implementar el iframe sandbox postMessage JSON-RPC para la comunicación de interfaz de usuario a host.
- Aplicar las configuraciones por defecto de CSP y de las políticas de permisos que se defienden contra los ataques de UI.

## El problema

Una era de 2025 `visualize_timeline`La herramienta puede devolver "Aquí hay 14 notas organizadas cronológicamente: ...". Ese es un párrafo. Los usuarios realmente quieren la línea de tiempo interactiva. Antes de MCP Apps, las opciones eran: API de widget específicos para el cliente (artefactos Claude, OpenAI Custom GPT HTML), o ninguna interfaz de usuario en absoluto.

MCP Apps (SEP-1724, lanzado el 26 de enero de 2026) estandariza el contrato.`resource`cuya URI es `ui://...`y cuyo MIME es `text/html;profile=mcp-app`El host lo hace en un iframe sandbox con un CSP limitado y ningún acceso a la red a menos que se le conceda explícitamente.

Cada cliente compatible (Claude Desktop, ChatGPT, Goose, VS Code) hace lo mismo `ui://`Un servidor, un paquete HTML, UI universal.

## El concepto

### El `ui://`plan de recursos

Una herramienta devuelve:

```json
{
  "content": [
    {"type": "text", "text": "Here is your notes timeline:"},
    {"type": "ui_resource", "uri": "ui://notes/timeline"}
  ],
  "_meta": {
    "ui": {
      "resourceUri": "ui://notes/timeline",
      "csp": {
        "defaultSrc": "'self'",
        "scriptSrc": "'self' 'unsafe-inline'",
        "connectSrc": "'self'"
      },
      "permissions": []
    }
  }
}
```

El anfitrión llama entonces .`resources/read`en el `ui://notes/timeline`URI y vuelve:

```json
{
  "contents": [{
    "uri": "ui://notes/timeline",
    "mimeType": "text/html;profile=mcp-app",
    "text": "<!doctype html>..."
  }]
}
```

### Cuadro de arena de cuadro de cuadro

El host hace que el HTML esté en una caja de arena.`<iframe>`con:

- `sandbox="allow-scripts allow-same-origin"`(o más estricta por declaración de servidor)
- Los CSP declarados por el servidor se aplican a través de encabezados de respuesta.
- No hay galletas, no hay almacenamiento local del origen del anfitrión.
- Acceso a la red limitado a `connectSrc`en el CSP.

### protocolo de mensaje

El iframe se comunica con el host vía `window.postMessage`Un pequeño dialecto JSON-RPC 2.0.

Siempre pin .`targetOrigin`en el lado receptor validar el origen exacto del igual.`event.origin`No se debe utilizar una carga útil.`"*"`para ambos lados de este canal  el cuerpo lleva llamadas de herramientas y lecturas de recursos.

```js
// iframe to host  (pin to host origin)
window.parent.postMessage({
  jsonrpc: "2.0",
  id: 1,
  method: "host.callTool",
  params: { name: "notes_update", arguments: { id: "note-14", title: "..." } }
}, "https://host.example.com");

// host to iframe  (pin to iframe origin)
iframe.contentWindow.postMessage({
  jsonrpc: "2.0",
  id: 1,
  result: { content: [...] }
}, "https://iframe.example.com");

// receiver on both sides
window.addEventListener("message", (event) => {
  if (event.origin !== "https://expected-peer.example.com") return;
  // safe to process event.data
});
```

Los métodos disponibles en el lado del host que la interfaz de usuario puede llamar:

- `host.callTool(name, arguments)` invoca una herramienta de servidor.
- `host.readResource(uri)` se lee un recurso de MCP.
- `host.getPrompt(name, arguments)` trae una plantilla de solicitud.
- `host.close()` desestima la interfaz de usuario.

Cada llamada sigue pasando por el protocolo MCP y hereda los permisos del servidor.

### Permisos

El `_meta.ui.permissions`lista de solicitudes de capacidades adicionales:

- `camera` acceso a la cámara del usuario (utilizada para las interfaces de exploración de un documento).
- `microphone` Entrada de voz.
- `geolocation` ubicación.
- `network:*` acceso a la red más amplio que `connectSrc`sólo permite.

Cada permiso es una solicitud que el usuario ve antes de que la interfaz de usuario se haga.

### Riesgos de seguridad

HTML en un iframe sigue siendo HTML. Nueva superficie de ataque:

- **Prompt-injection via UI.**Una interfaz de usuario de servidor malicioso puede mostrar texto que se parece a un mensaje del sistema y engaña al usuario.
- **Exfiltration via `connectSrc`.**Si el CSP lo permite `connect-src: *`, la interfaz de usuario puede enviar datos a cualquier lugar.
- **Clickjacking.**La interfaz de usuario superpone al host Chrome. Los hosts deben evitar la manipulación del índice z y hacer cumplir las reglas de opacidad.
- **Steal focus.**La interfaz de usuario toma el enfoque del teclado y captura el siguiente mensaje.

La fase 13 · 15 cubre estos en profundidad como parte de la seguridad de los PCM; esta lección los introduce.

### `ui/initialize`el apretón de manos

Después de que el iframe se carga, envía `ui/initialize`por correoMensaje:

```json
{"jsonrpc": "2.0", "id": 0, "method": "ui/initialize",
 "params": {"theme": "dark", "locale": "en-US", "sessionId": "..."}}
```

El host responde con capacidades y un token de sesión. La interfaz de usuario utiliza el token de sesión en cada llamada del host posterior.

### Primitivas de la SDK AppRenderer / AppFrame

El ext-apps SDK expone dos primitivas de conveniencia:

- `AppRenderer`(lado del servidor)  envuelve un componente React / Vue / Solid y emite un `ui://`recurso con el MIME y metadatos adecuados.
- `AppFrame`(cliente lado)  recibe el recurso, monta el iframe, y mediación postMessage.

Puedes usar estos o rodar manualmente el HTML y JSON-RPC.

### Estado del ecosistema

MCP Apps se envió el 26 de enero de 2026.

- **Claude Desktop.**Apoyo total desde enero de 2026.
- **ChatGPT.**Apoyo completo a través del SDK de aplicaciones (el mismo protocolo subyacente de MCP Apps).
- **Cursor.**Beta; habilitar a través de la configuración.
- **VS Code.**Sólo construye el interior.
- **Goose.**Apoyo total.
- **Zed, Windsurf.**- El mapa de la carretera.

Servidores en producción: tablas de control, visualizaciones de mapas, tablas de datos, constructores de gráficos, vistas previas de IDE sandbox.

```figure
t3-ui-sandbox
```

## Usalo

`code/main.py`extiende el servidor de notas con un `visualize_timeline`herramienta que devuelve un `ui://notes/timeline`recurso, más un manipulador para `resources/read`En ese URI que devuelve un pequeño pero completo paquete de HTML con una línea de tiempo SVG. El HTML está templado stdlib  no hay sistema de construcción. postMessage se esboza en comentarios JS ya que stdlib no puede ejecutar un navegador.

Qué ver:

- `_meta.ui`En la respuesta de la herramienta se incluyen recursosUri, CSP, permisos.
- El HTML se renderiza sin acceso a la red; todos los datos están en línea.
- JS llama .`host.callTool`por medio de`window.parent.postMessage`(documentado pero inerte en esta demo de la SDLIB).

## Envío

Esta lección produce`outputs/skill-mcp-apps-spec.md`. Dado que una herramienta que se beneficiaría de una interfaz de usuario interactiva, la habilidad produce el contrato completo de MCP Apps: `ui://`URI, CSP, permisos, puntos de entrada de mensajes y una lista de verificación de seguridad.

## Los ejercicios

1. - ¿ Qué ?`code/main.py`y inspeccionar el HTML emitido. Abra el HTML directamente en un navegador; verifique los renders SVG. Luego esboza el contrato de postMessage que la interfaz de usuario usaría para llamar `host.callTool("notes_update", ...)`¿ Qué ?

2. Apegue el CSP: retire `'unsafe-inline'`¿Qué cambios hay en el código de generación de HTML?

3. Añadir un segundo recurso de interfaz de usuario `ui://notes/editor`Cuando el usuario envía, el iframe llama `host.callTool("notes_update", ...)`¿ Qué ?

4. ¿Dónde puede un servidor malicioso inyectar contenido? ¿De qué se defiende la caja de arena iframe y qué no?

5. Lea la especificación de SEP-1724 e identifique una capacidad en el SDK de MCP Apps que esta implementación de juguetes no utiliza. (Punta: sincronización de estado a nivel de componentes).

## Términos clave

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| MCP Apps | "Interactive UI resources" | SEP-1724 extension shipped 2026-01-26 |
| `ui://` | "App URI scheme" | Resource scheme for UI bundles |
| `text/html;profile=mcp-app` | "The MIME" | Content-type for MCP App HTML |
| Iframe sandbox | "Render container" | Browser sandboxing of the UI with CSP and permissions |
| postMessage JSON-RPC | "UI-to-host wire" | Tiny JSON-RPC-over-postMessage dialect for host calls |
| `_meta.ui` | "Tool-UI binding" | Metadata linking a tool result to a UI resource |
| CSP | "Content-Security-Policy" | Declares allowed sources for scripts, network, styles |
| AppRenderer | "Server SDK primitive" | Converts a framework component into a `ui://` resource |
| AppFrame | "Client SDK primitive" | Iframe mount helper that mediates postMessage |
| `ui/initialize` | "Handshake" | First postMessage from UI to host |

## Leer más

- [MCP ext-apps — GitHub](https://github.com/modelcontextprotocol/ext-apps) Implementación de referencia y KDD
- [MCP Apps specification 2026-01-26](https://github.com/modelcontextprotocol/ext-apps/blob/main/specification/2026-01-26/apps.mdx) Documento de especificación formal
- [MCP — Apps extension overview](https://modelcontextprotocol.io/extensions/apps/overview) Documentación de alto nivel
- [MCP blog — MCP Apps launch](https://blog.modelcontextprotocol.io/posts/2026-01-26-mcp-apps/) Enero 2026 puesta en marcha
- [MCP Apps API reference](https://apps.extensions.modelcontextprotocol.io/api/) Referencia de SDK al estilo JSDoc
