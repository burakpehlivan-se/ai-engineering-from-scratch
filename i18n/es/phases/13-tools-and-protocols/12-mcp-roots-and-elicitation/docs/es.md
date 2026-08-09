# Raíces y Elicitación  Entrada de usuario en alcance y en medio del vuelo

> Los caminos codificados se rompen en el momento en que un usuario abre un proyecto diferente. Los argumentos de herramienta pre-rellenados se rompen cuando el usuario especifica poco. Roots abarca el servidor a un conjunto de URI controlados por el usuario; la elicitación se detiene a mitad de la llamada de herramienta para pedirle al usuario una entrada estructurada a través de un formulario o URL. Dos primitivas del cliente, dos correcciones para los modos comunes de falla de MCP. SEP-1036 (URL-mode elicitation, 2025-11-25) es experimental a través de H1 2026  verifique versiones de SDK antes de depender de él.

**Type:** Build
**Languages:** Python (stdlib, roots + elicitation demo)
**Prerequisites:** Phase 13 · 07 (MCP server)
**Time:** ~45 minutes

## Objetivos de aprendizaje

- Declarar`roots`y responder a`notifications/roots/list_changed`¿ Qué ?
- Restringir las operaciones de archivos del servidor a las URI dentro del conjunto de raíces declarado.
- Usar`elicitation/create`solicitar al usuario una confirmación o una entrada estructurada en medio de la llamada de la herramienta.
- Elegir entre la elicitación en modo de formulario y en modo URL (esta última es experimental; se nota el riesgo de deriva).

## El problema

Dos fallas concretas un servidor MCP notas golpes en la producción.

**Broken path assumption.**El servidor está escrito contra `~/notes`Un usuario en una máquina diferente con notas en `~/Documents/Notes`recibe una llamada de herramienta que falla silenciosamente (no se encuentra archivo) o peor, escribió en el lugar equivocado.

**Missing argument the user would know.**El usuario pide "borrar la vieja nota del informe TPS". El modelo llama `notes_delete(title: "TPS report")`Pero hay tres notas que coinciden con las de 2023, 2024 y 2025. La herramienta no puede adivinar. No conseguir "ambiguo" es molesto; correr en las tres es catastrófico.

Las raíces fijan la primera: el cliente declara en `initialize`El servidor detiene la llamada de la herramienta y envía `elicitation/create`para pedirle al usuario que elija cuál.

## El concepto

### Las raíces

El cliente declara una lista raíz en `initialize`¿Qué es esto ?

```json
{
  "capabilities": {"roots": {"listChanged": true}}
}
```

El servidor puede entonces llamar `roots/list`¿Qué es esto ?

```json
{"roots": [{"uri": "file:///Users/alice/Documents/Notes", "name": "Notes"}]}
```

Los servidores deben tratar las raíces como el límite: cualquier archivo leído o escrito fuera del conjunto de raíces es rechazado. Esto no es aplicado por el cliente (el servidor sigue siendo el código en el que confía el usuario), pero los servidores que cumplen con las especificaciones lo honran.

Cuando el usuario agrega o elimina una raíz, el cliente envía `notifications/roots/list_changed`El servidor vuelve a llamar .`roots/list`y actualiza sus límites.

### ¿Por qué las raíces son un cliente primitivo

Los raíces son declarados por el cliente porque representan el modelo de consentimiento del usuario. El usuario le dijo a Claude Desktop "dar acceso a este servidor de notas a estos dos directorios". El servidor no puede ampliar ese alcance.

### Elicitación: el modo de formulario por defecto

`elicitation/create`toma un esquema de forma más un mensaje de lenguaje natural:

```json
{
  "method": "elicitation/create",
  "params": {
    "message": "Delete 'TPS report'? Multiple notes match; pick one.",
    "requestedSchema": {
      "type": "object",
      "properties": {
        "note_id": {
          "type": "string",
          "enum": ["note-3", "note-7", "note-14"]
        },
        "confirm": {"type": "boolean"}
      },
      "required": ["note_id", "confirm"]
    }
  }
}
```

El cliente entrega un formulario, recoge la respuesta del usuario, devuelve:

```json
{
  "action": "accept",
  "content": {"note_id": "note-14", "confirm": true}
}
```

Tres acciones posibles:`accept`(el usuario lo llenó), `decline`(el usuario lo cerró), `cancel`(el usuario abortó toda la llamada de herramienta).

Los esquemas de forma son planos  objetos anidados no son compatibles en v1. los SDK suelen rechazar cualquier cosa más compleja que una sola capa.

### Elicitación: modo URL (SEP-1036, experimental)

Nuevo en 2025-11-25. En lugar de un esquema, el servidor envía una URL:

```json
{
  "method": "elicitation/create",
  "params": {
    "message": "Sign in to GitHub",
    "url": "https://github.com/login/oauth/authorize?client_id=..."
  }
}
```

El cliente abre la URL en un navegador, espera que se complete, regresa cuando el usuario regresa.

Nota de riesgo de derivación: la forma de respuesta de SEP-1036 todavía se está estableciendo; algunos SDK devuelven la URL de devolución, otros devuelven un token de finalización. Lea las notas de liberación de su SDK antes de usar el modo URL en producción.

### Cuando la elicitación es la herramienta correcta

- Confirmación del usuario antes de las acciones destructivas (indicio destructivo + elicitación).
- Desambiguación (escolle uno de N coincidencias).
- Configuración de ejecución inicial (claves API, directorios, preferencias).
- Flujos de estilo OAuth (modo URL).

### Cuando la elicitación es incorrecta

- Rellenar los argumentos requeridos de una herramienta que el modelo podría haber pedido en prosa.
- Las llamadas de alta frecuencia. La llamada interrumpe la conversación; no lo dispares dentro de un bucle.
- Cualquier cosa que el servidor pueda validar después del hecho. Valida, devuelve un error, deja que el modelo le pregunte al usuario en texto.

### Puente humano en el circuito

La elicitación más la muestreo juntos permiten el modelo "humano en el bucle" de MCP. El bucle de agente de un servidor puede pausar para la entrada del usuario (elicitación) o el razonamiento del modelo (muestreo).

```figure
t3-roots-boundary
```

## Usalo

`code/main.py`extiende el servidor de notas con:

- `roots/list`respuesta que el servidor vuelve a solicitar después de las notificaciones modificadas de la lista raíz.
- ¿ Qué es esto ?`notes_delete`herramienta que utiliza `elicitation/create`para desambiguar cuando coincidan varias notas.
- ¿ Qué es esto ?`notes_setup`herramienta que utiliza la elicitación de modo URL para abrir una página de configuración de primera ejecución (simulada).
- Una verificación de límites que niegue operaciones en URI fuera de las raíces declaradas.

La demostración tiene tres escenarios: happy path (un partido), desambiguación (tres partidos, incendios de elicitación), escritura fuera de raíz (rechazada).

## Envío

Esta lección produce`outputs/skill-elicitation-form-designer.md`. Dado una herramienta que podría necesitar una confirmación o desambiguación del usuario, la habilidad diseña el esquema de formulario de solicitud y la plantilla de mensaje.

## Los ejercicios

1. - ¿ Qué ?`code/main.py`.Activa la ruta de desambiguación; confirma que la respuesta del usuario simulada se envía de nuevo a la herramienta.

2. Añadir una nueva herramienta `notes_archive`¿Cómo se compara esto con el modelo de re-petición en texto?

3. Implemente la elicitación de modo URL para un flujo OAuth de primera ejecución.

4. Extenderse`roots/list`manipulación: cuando llega una notificación, el servidor debe volver a leer y revisar automáticamente los manuales de archivos abiertos que ahora podrían estar fuera de su alcance.

5. Lea el hilo de discusión del tema SEP-1036 en GitHub. Identifique una pregunta abierta que afecte a cómo los servidores deben manejar las llamadas de retroceso en modo URL.

## Términos clave

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| Root | "Consent boundary" | URI the client has allowed the server to touch |
| `roots/list` | "Server asks for scope" | Client returns the current root set |
| `notifications/roots/list_changed` | "User changed scope" | Client signals the root set has mutated |
| Elicitation | "Ask the user mid-call" | Server-initiated request for structured user input |
| `elicitation/create` | "The method" | JSON-RPC method for elicitation requests |
| Form mode | "Schema-driven form" | Flat JSON Schema rendered as a form in the client UI |
| URL mode | "Browser redirect" | SEP-1036 experimental; opens a URL and waits |
| `accept` / `decline` / `cancel` | "User response outcomes" | Three branches the server handles |
| Disambiguation | "Pick one" | Common elicitation use case when a tool has N candidates |
| Flat form | "Top-level properties only" | Elicitation schemas cannot nest |

## Leer más

- [MCP — Client roots spec](https://modelcontextprotocol.io/specification/draft/client/roots) Referencia a las raíces canónicas
- [MCP — Client elicitation spec](https://modelcontextprotocol.io/specification/draft/client/elicitation) referencia canónica de la obtención
- [Cisco — What's new in MCP elicitation, structured content, OAuth enhancements](https://blogs.cisco.com/developer/whats-new-in-mcp-elicitation-structured-content-and-oauth-enhancements) 2025-11-25 adiciones de paso por paso
- [MCP — GitHub SEP-1036](https://github.com/modelcontextprotocol/modelcontextprotocol) Proposición de obtención de datos en modo URL (experimentales, riesgo de deriva)
- [The New Stack — How elicitation brings human-in-the-loop to AI tools](https://thenewstack.io/how-elicitation-in-mcp-brings-human-in-the-loop-to-ai-tools/) UX de paso
