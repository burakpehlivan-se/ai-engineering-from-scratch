# MCP Transports  stdio vs transmisión HTTP vs SSE Migración

> El stdio funciona localmente y en ningún otro lugar. Streamable HTTP (2025-03-26) es el estándar remoto. El viejo transporte HTTP+SSE se desaprovecha y se elimina a mediados de 2026. Elegir el transporte equivocado cuesta una migración; elegir el correcto compra un servidor MCP remoto hospedable con continuidad de sesión y protección de redireccionamiento DNS.

**Type:** Learn
**Languages:** Python (stdlib, Streamable HTTP endpoint skeleton)
**Prerequisites:** Phase 13 · 07, 08 (MCP server and client)
**Time:** ~45 minutes

## Objetivos de aprendizaje

- Escoge entre stdio y Streamable HTTP basado en la forma de implementación (local vs remoto, un solo proceso vs flota).
- Implemente el patrón de punto final HTTP de transmisión: POST para las solicitudes, GET para el flujo de sesión.
- Hacer cumplir`Origin`validación y semántica de sesión para derrotar la re-indicación de DNS.
- Migra un servidor HTTP+SSE heredado a HTTP Streamable antes de las fechas límite de eliminación de mediados de 2026.

## El problema

El primer transporte remoto MCP (2024-11) fue HTTP+SSE: dos puntos finales, uno para los POST del cliente y un canal de Server-Sent-Events para el flujo de servidor a cliente. Funcionó. También fue torpe: dos puntos finales por sesión, caches rotos frente a algunos CDN, y una fuerte dependencia de las conexiones SSE de larga duración que algunos WAF terminan agresivamente.

La especificación 2025-03-26 la reemplazó con Streamable HTTP: un punto final, POST para las solicitudes del cliente, GET para establecer un flujo de sesión, ambos compartiendo una `Mcp-Session-Id`En el caso de los servidores de Internet, el sistema de acceso a Internet (SSE) se ha modificado en forma de header.

Y el estudio sigue siendo importante para los servidores locales. Claude Desktop, VS Code, y cada cliente en forma de IDE despierta servidores a través del estudio. El modelo mental correcto: estudio para "esta máquina", Streamable HTTP para "en la red". No hay cruce.

## El concepto

### estudio

- Transporte de procesamiento infantil. El cliente genera el servidor, se comunica a través de stdin/stdout.
- Un objeto JSON por línea.
- No hay ID de sesión; la identidad del proceso es la sesión.
- No se necesita autor (el niño hereda el límite de confianza del padre).
- Nunca utilice para servidores remotos  necesitaría SSH o socat para el túnel, en cuyo punto utilizar Streamable HTTP.

### HTTP en transmisión

Un solo punto final `/mcp`(o cualquier camino). Apoya tres métodos HTTP:

- **POST /mcp.**El cliente envía un mensaje JSON-RPC. El servidor responde con una sola respuesta JSON, o un flujo SSE de una o más respuestas (utiles para respuestas en lote y notificaciones relacionadas con esa solicitud).
- **GET /mcp.**El cliente abre un canal SSE de larga duración. El servidor lo utiliza para las solicitudes de servidor a cliente (muestras, notificaciones, elicitación).
- **DELETE /mcp.**El cliente termina explícitamente la sesión.

Las sesiones son identificadas por la `Mcp-Session-Id`El servidor establece la primera respuesta y el cliente hace eco en cada solicitud posterior. los ID de sesión DEBEN ser cifrados al azar (128 bits); los ID seleccionados por el cliente se rechazan por seguridad.

### Un solo punto final vs dos

El modo de dos puntos finales de la antigua especificación todavía es llamable en 2026  la especificación lo declara "compatible con el legado". Pero todos los nuevos servidores deben ser de un solo punto final.

### `Origin`validación y re-indicación de DNS

Los navegadores no son clientes MCP (hoy), pero un atacante puede crear una página web que convence a un navegador de POST a `localhost:1234/mcp` donde el servidor local de MCP del usuario escucha. Si el servidor no verifica `Origin`, la política de origen del navegador no lo guardará porque `Origin: http://evil.com`es de origen cruzado válido.

La especificación 2025-11-25 requiere que los servidores rechacen las solicitudes de los cuales `Origin`La lista de permisos normalmente contiene el host del cliente MCP (`https://claude.ai`¿ Qué ?`vscode-webview://*`) y las variantes localhost para las interfaces locales.

### Ciclo de vida de la sesión

1. El cliente envía la primera solicitud sin `Mcp-Session-Id`¿ Qué ?
2. El servidor asigna una identificación aleatoria, conjuntos `Mcp-Session-Id`en el encabezado de respuesta.
3. El cliente hace eco de ese encabezado en todas las solicitudes posteriores y en `GET /mcp`para el arroyo.
4. La sesión puede ser revocada por el servidor; el cliente ve 404 en las solicitudes posteriores y debe reiniciar.
5. El cliente puede EXPLICITAMENTE DELETAR la sesión para el cierre limpio.

### Mantener el dispositivo activo y volver a conectarlo

Las conexiones de SSE caen. El cliente restablece al volver a GET con el mismo `Mcp-Session-Id`. El servidor DEVE hacer cola de los eventos perdidos durante la interrupción (hasta una ventana razonable) y reproducirlos a través del `last-event-id`El cliente hace eco.

La fase 13 · 13 abarca las tareas, que permiten que el trabajo de larga duración sobreviva incluso una reconnección de sesión completa.

### Probe de compatibilidad hacia atrás

Un cliente que quiere soportar servidores viejos y nuevos:

1. Envía a`/mcp`¿ Qué ?
2. Si la respuesta es `200 OK`con JSON o SSE, esto es Streamable HTTP.
3. Si la respuesta es `200 OK`con`Content-Type: text/event-stream`Y un `Location`cabezal que apunta a un punto final secundario, esto es HTTP + SSE heredado; siga el `Location`¿ Qué ?

### Cloudflare, ngrok y alojamiento

Los servidores MCP remotos de producción en 2026 se ejecutan en Cloudflare Workers (con su MCP Agents SDK), Functions Vercel o Node / Python contenerizado. clave: su alojamiento debe admitir conexiones HTTP de larga duración para el SSE GET. Los límites de nivel gratuitos de Vercel se limitan a 10 segundos y no son adecuados. Cloudflare Workers soporta flujos indefinidos.

### Compuesto de la puerta de entrada

Cuando se enfrentan varios servidores MCP con una puerta de enlace (fase 13 · 17), la puerta de enlace es un único punto final HTTP que reescribe las identidades de sesión y multiplexes aguas arriba.

### Modo de falla del transporte

- **stdio SIGPIPE.**La muerte del niño en medio de la escritura aumenta el SIGPIPE; los servidores deben salir limpios.
- **HTTP 502 / 504.**Cloudflare, nginx y otros proxies emiten estos en fallas de aguas arriba. Los clientes HTTP transmitibles deben intentarlo una vez más después de una corta copia de seguridad.
- **SSE connection drop.**TCP RST, tiempo de espera de proxy, o cambio de red del cliente cierra la corriente.`Mcp-Session-Id`y opcionales `last-event-id`para reanudar.
- **Session revocation.**El servidor invalida un ID de sesión; el cliente ve 404 en la siguiente solicitud. El cliente debe dar la mano de nuevo.
- **Clock skew.**Los cálculos de recursos-TTL en el cliente difieren del servidor.

### Cuándo evitar el HTTP en transmisión

Algunas empresas despliegan servidores MCP detrás de gRPC o transporte de colas de mensajes dentro de sus propias redes. Esto no es estándar  La especificación de MCP no las define formalmente. Gateways pueden exponer una superficie HTTP en streaming a los clientes de MCP mientras usan gRPC internamente. Mantenga la superficie externa conforme a las especificaciones; la puerta de entrada es propietaria de la traducción.

```figure
tp-transport-handshake
```

## Usalo

`code/main.py`Implementa un punto final HTTP de transmisión mínimo utilizando `http.server`Se encarga de POST, GET y DELETE en`/mcp`, conjuntos `Mcp-Session-Id`en la primera respuesta, valida `Origin`El procesador reutiliza la lógica de envío del servidor de notas de la Lección 07.

Qué ver:

- El procesador POST lee el cuerpo JSON-RPC, envía y escribe una respuesta JSON (la variante de respuesta única; la variante SSE es estructuralmente similar).
- El `Origin`el control rechaza el defecto `http://evil.example`La sonda pero acepta.`http://localhost`¿ Qué ?
- Los ID de sesión son cadenas hexáticas aleatorias de 128 bits; el servidor mantiene el estado por sesión en la memoria.

## Envío

Esta lección produce`outputs/skill-mcp-transport-migrator.md`. Dado un servidor MCP HTTP+SSE (legacy), la habilidad produce un plan de migración a Streamable HTTP con continuidad de identificación de sesión, comprobaciones de origen y soporte de sonda compatible con retroceso.

## Los ejercicios

1. - ¿ Qué ?`code/main.py`. POST un`initialize`de la`curl`y observar el `Mcp-Session-Id`POST una segunda solicitud que se hace eco del encabezado y verifique la continuidad de la sesión.

2. Añadir un manipulador GET que abre una corriente SSE. Envía uno `notifications/progress`Reconecta al volver a GET con la misma identificación de sesión y confirma que el servidor la acepta.

3. Implementar el `last-event-id`En reconectar, reproducir cualquier evento generado desde esa identificación.

4. Extenderse`Origin`validación para apoyar un patrón de tarjeta salvaje (`https://*.example.com`) y confirmar que acepta `https://app.example.com`Pero rechaza.`https://evil.example.com.attacker.net`¿ Qué ?

5. Tome un servidor HTTP+SSE heredado del registro oficial (hay varios) y esboce la migración: qué cambios en el manejo de puntos finales, generación de id de sesión y semántica de encabezado.

## Términos clave

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| stdio transport | "Local child process" | JSON-RPC over stdin/stdout, newline-delimited |
| Streamable HTTP | "The remote transport" | Single-endpoint POST + GET + optional SSE, 2025-03-26 spec |
| HTTP+SSE | "Legacy" | Two-endpoint model being removed in mid-2026 |
| `Mcp-Session-Id` | "Session header" | Server-assigned random id echoed on every subsequent request |
| `Origin` allowlist | "DNS-rebinding defense" | Reject requests whose Origin is not approved |
| Single endpoint | "One URL" | `/mcp` handles POST / GET / DELETE for all session operations |
| `last-event-id` | "SSE replay" | Header used to resume a dropped stream without missing events |
| Backwards-compat probe | "Old vs new detection" | Client response-shape check that auto-selects transport |
| Long-lived HTTP | "SSE streaming" | Server pushes events for minutes or hours on one TCP connection |
| Session revocation | "Force re-init" | Server invalidates a session id; client must handshake again |

## Leer más

- [MCP — Basic transports spec 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports) referencia canónica para stdio y Streamable HTTP
- [MCP — Basic transports spec 2025-03-26](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports) la revisión que introdujo Streamable HTTP
- [Cloudflare — MCP transport](https://developers.cloudflare.com/agents/model-context-protocol/transport/) Modelos de HTTP en streaming alojados por los trabajadores
- [AWS — MCP transport mechanisms](https://builder.aws.com/content/35A0IphCeLvYzly9Sw40G1dVNzc/mcp-transport-mechanisms-stdio-vs-streamable-http) Comparación entre formas de despliegue
- [Atlassian — HTTP+SSE deprecation notice](https://community.atlassian.com/forums/Atlassian-Remote-MCP-Server/HTTP-SSE-Deprecation-Notice/ba-p/3205484) ejemplo concreto de fecha límite de migración
