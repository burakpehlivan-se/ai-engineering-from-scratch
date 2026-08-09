# MCP Security II  OAuth 2.1, Indicadores de recursos, objetivos incremental

> Los servidores MCP remotos necesitan autorización, no solo autenticación. La especificación 2025-11-25 se alinea con OAuth 2.1 + PKCE + indicadores de recursos (RFC 8707) + metadatos de recursos protegidos (RFC 9728). SEP-835 agrega el consentimiento de alcance incremental con autorización de incremento en 403 WWW-Authenticate. Esta lección implementa el flujo de incremento como máquina de estado para que pueda ver cada salto.

**Type:** Build
**Languages:** Python (stdlib, OAuth state machine simulator)
**Prerequisites:** Phase 13 · 09 (transports), Phase 13 · 15 (security I)
**Time:** ~75 minutes

## Objetivos de aprendizaje

- Distinguir entre servidor de recursos y responsabilidades del servidor de autorización.
- Siga el flujo de código de autorización OAuth 2.1 protegido por PKCE.
- Usar`resource`(RFC 8707) y metadatos de recursos protegidos (RFC 9728) para prevenir ataques de subcontratación confusa.
- Implementar la autorización de incremento: el servidor responde 403 con WWW-Authenticate solicitando un mayor alcance; el cliente re-pide el consentimiento del usuario y retenta.

## El problema

El MCP temprano (antes de 2025) envió servidores remotos con claves de API ad-hoc o incluso sin auth.

Tres necesidades del mundo real:

- **Ordinary remote servers.**El usuario instala un servidor MCP remoto que accede a su Notion / GitHub / Gmail. OAuth 2.1 con PKCE es la forma correcta.
- **Scope escalation.**Un servidor de notas otorgado `notes:read`puede necesitar más tarde `notes:write`En lugar de repetir todo el flujo, el incremento (SEP-835) pide el alcance adicional.
- **Confused deputy prevention.**El cliente tiene un token de audiencia para el servidor A. El servidor A es malicioso y trata de presentar el token al servidor B. Los indicadores de recursos (RFC 8707) pinan el token a su público previsto.

OAuth 2.1 no es nuevo. Lo nuevo es el perfil de MCP: flujos requeridos específicos (código de autorización + PKCE solamente; no implícito, no credenciales de cliente por defecto), indicadores de recursos obligatorios para cada solicitud de token, y metadatos de recursos protegidos publicados para que los clientes sepan a dónde ir.

## El concepto

### Roles

- **Client.**El cliente MCP (Claude Desktop, Cursor, etc.).
- **Resource server.**El servidor MCP (notaciones, GitHub, Postgres, lo que sea).
- **Authorization server.**Puede ser el mismo servicio que el servidor de recursos o un IDP separado (Auth0, Keycloak, Cognito).

En el perfil de MCP, los servidores de recursos y autorización PUEDEN ser el mismo host pero DEBEN ser distinguidos por URL.

### Código de autorización + PKCE

El flujo:

1. El cliente genera `code_verifier`(a azar) y `code_challenge`(SHA256).
2. El cliente redirige al usuario a `/authorize?response_type=code&client_id=...&redirect_uri=...&scope=notes:read&code_challenge=...&resource=https://notes.example.com`¿ Qué ?
3. El servidor de autorización redirige a `redirect_uri?code=...`¿ Qué ?
4. Los clientes envían mensajes a `/token?grant_type=authorization_code&code=...&code_verifier=...&resource=...`¿ Qué ?
5. El servidor de autorización valida el hash del verificador contra el desafío almacenado y emite un token de acceso.
6. El cliente utiliza el token: `Authorization: Bearer ...`en cada solicitud al servidor de recursos.

PKCE evita los ataques de interceptación de código de autorización. Los indicadores de recursos impiden que el token sea válido en otros lugares.

### Metadatos de recursos protegidos (RFC 9728)

El servidor de recursos publica una `.well-known/oauth-protected-resource`Documento:

```json
{
  "resource": "https://notes.example.com",
  "authorization_servers": ["https://auth.example.com"],
  "scopes_supported": ["notes:read", "notes:write", "notes:delete"]
}
```

El cliente descubre el servidor de autorización desde el servidor de recursos. Reduce la configuración  el cliente solo necesita la URL del recurso.

### Indicadores de recursos (RFC 8707)

`resource`Parámetro en el token de solicitud pines de la audiencia prevista del token.`aud: "https://notes.example.com"`Otro servidor de MCP recibiendo estos cheques de tokens .`aud`y lo rechaza.

### Modelo de alcance

Los espacios son cadenas separadas por el espacio.

- `notes:read`¿ Qué ?`notes:write`¿ Qué ?`notes:delete`
- `admin:*`para capacidades de administración (utilización reducida)
- `profile:read`para la identidad

La selección del alcance debe ser el menor privilegio: pedir lo que necesita ahora, dar un paso cuando necesita más.

### Autorización de incremento (SEP-835)

Subvenciones de los usuarios `notes:read`Luego le piden al agente que borre una nota.

```
HTTP/1.1 403 Forbidden
WWW-Authenticate: Bearer error="insufficient_scope",
    scope="notes:delete", resource="https://notes.example.com"
```

El cliente ve el error insufficient_scope, le pide al usuario un diálogo de consentimiento para el alcance adicional, realiza un mini flujo OAuth para él, retoma la solicitud con el nuevo token.

### Validación de la audiencia de los tokens

Cada solicitud: controles del servidor `token.aud == self.resource_url`Desajuste = 401. Esto detiene el reutilización de tokens entre servidores.

### Tokens de corta duración y rotación

Los tokens de acceso DEVEN ser de corta duración (1 hora por defecto).

### No hay pasaportes simbólicos

Los servidores de muestreo (fase 13 · 11) NO DEBEN pasar el token del cliente a otros servicios.

### Prevención de los diputados

El token se une a `aud`. El cliente se obliga a`client_id`La especificación prohíbe explícitamente el viejo patrón de "pasar el token" que era común en los ecosistemas de herramientas remotas anteriores a MCP.

### Descubrimiento de la identificación del cliente

Cada cliente MCP publica sus metadatos en una URL fija. Los servidores de autorización pueden recoger el documento de metadatos del cliente para descubrir los URIs de redirección e información de contacto. Esto elimina el registro manual del cliente.

### Puertas de entrada y OAuth

La fase 13 · 17 muestra cómo una puerta de enlace empresarial maneja OAuth: la puerta de enlace retiene credenciales para servidores upstream, los tokens para el cliente son emitidos por puerta de enlace y los tokens upstream nunca salen de la puerta de enlace. Esto cambia el modelo de confianza  los usuarios autentican con la puerta de enlace una vez; la puerta de enlace maneja N autorizaciones de servidor.

```figure
t3-scope-stepup
```

## Usalo

`code/main.py`simula el flujo de incremento completo de OAuth 2.1 como máquina de estado. Implementa:

- Verificador de código PKCE / generación de desafíos.
- Flujo de código de autorización con indicador de recursos.
- punto final de metadatos de recursos protegidos.
- Validación de tokens con verificación de audiencia.
- Un paso adelante .`insufficient_scope`¿ Qué ?

No hay servidor HTTP en esta lección; la máquina de estado se ejecuta en la memoria para que pueda rastrear cada salto.

## Envío

Esta lección produce`outputs/skill-oauth-scope-planner.md`. Dado que un servidor MCP remoto con herramientas, la habilidad diseña el conjunto de alcance, las reglas de fijación y la política de incremento.

## Los ejercicios

1. - ¿ Qué ?`code/main.py`- Rastrear el flujo de aumento de dos escopo.

2. Añadir la rotación de los tokens de actualización: cada actualización emite un nuevo token de actualización e invalida el antiguo. Simula un token de actualización robado que se utiliza después de la rotación y confirma que falla.

3. Implemente el metafinante de metadatos de recursos protegidos como una respuesta HTTP real utilizando stdlib http.server. Reflejar el punto final /mcp de la Lección 09.

4. Diseñar una jerarquía de alcance para un servidor MCP de GitHub: leer repo, escribir relaciones públicas, aprobar relaciones públicas, fusionar relaciones públicas, administrar.

5. Lea RFC 8707 y RFC 9728. Identifique el campo en 9728 que MCP utiliza de manera diferente al ejemplo de la RFC.`scopes_supported`(en inglés).

## Términos clave

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| OAuth 2.1 | "Modern OAuth" | Consolidated RFC that mandates PKCE and forbids implicit flow |
| PKCE | "Proof-of-possession" | Code verifier + challenge defeating authorization-code interception |
| Resource indicator | "Token audience" | RFC 8707 `resource` parameter pinning token to one server |
| Protected-resource metadata | "Discovery doc" | RFC 9728 `.well-known/oauth-protected-resource` |
| Step-up authorization | "Incremental consent" | SEP-835 flow for adding scopes on demand |
| `insufficient_scope` | "403 with WWW-Authenticate" | Server signal to re-consent for a larger scope |
| Confused deputy | "Token reuse across services" | Attack where a trusted holder forwards a token inappropriately |
| Short-lived token | "Access token TTL" | Bearer that expires quickly; refresh token renews |
| Scope hierarchy | "Least privilege stack" | Graduated scope set with step-up between levels |
| Client ID metadata | "Client discovery doc" | URL at which the client publishes its own OAuth metadata |

## Leer más

- [MCP — Authorization spec](https://modelcontextprotocol.io/specification/draft/basic/authorization) perfil de MCP OAuth canónico
- [den.dev — MCP November authorization spec](https://den.dev/blog/mcp-november-authorization-spec/) la transición de los cambios de 2025 a 2021
- [RFC 8707 — Resource indicators for OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc8707) el RFC de afición de audiencia
- [RFC 9728 — OAuth 2.0 protected resource metadata](https://datatracker.ietf.org/doc/html/rfc9728) el documento de descubrimiento RFC
- [Aembit — MCP OAuth 2.1, PKCE and the future of AI authorization](https://aembit.io/blog/mcp-oauth-2-1-pkce-and-the-future-of-ai-authorization/) Acceso a la práctica, flujo de progreso, paso a paso
