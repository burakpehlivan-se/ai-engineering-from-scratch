# MCP Autor en producción  Inscripción, JWKS Refresh, Tokens de audiencia

> La lección 16 puso en memoria la máquina de estado OAuth 2.1. Para 2026, cada servidor MCP que envíes a una organización real se encuentra detrás de la producción de autor: inscripción de clientes que se escala a una población de clientes ilimitada (documentos de metadatos de ID de cliente primero, registro dinámico de cliente como una retroceso compatible), descubrimiento de metadatos del servidor de autorización (RFC 8414 *o * OpenID Connect Discovery), actualización de caché de JWKS que no rompe una 3 a.m. validez de tokens y tokens de audiencia que rechazan la reproducción de recursos cruzados. Esta lección modela la superficie completa con tres funciones  un servidor de autorización, un servidor de recursos (el servidor MCP) y un cliente  para que pueda rastrear cada salto desde el descubrimiento hasta una llamada de herramienta validada.
>
> **Spec note (2025-11-25):**La especificación de autorización de MCP de noviembre de 2025 rebajó el registro de clientes dinámicos a partir de `SHOULD`¿ Qué ?`MAY`y hecha**Client ID Metadata Documents (CIMD)**Esta lección enseña tanto, en el orden de prioridad de la especificación, como el código mantiene DCR para el proceso de recorrido porque es totalmente autónomo en un proceso.

**Type:** Build
**Languages:** Python (stdlib)
**Prerequisites:** Phase 13 · 16 (OAuth 2.1 state machine), Phase 13 · 17 (gateways)
**Time:** ~90 minutes

## Objetivos de aprendizaje

- Descubra un servidor de autorización a través de los metadatos de RFC 8414 y verifique el contrato.
- Implementar el registro dinámico de clientes de RFC 7591 para que los clientes de MCP se inscriban sin intervención del administrador.
- Cache y actualice las claves JWKS en un horario para que la verificación de firma sobreviva al cambio de llave.
- Aplicar los tokens a un solo recurso de MCP utilizando indicadores de recursos de la RFC 8707 y rechazar la reutilización de los diputados confusos.
- Separar los tres papeles limpio  servidor de autorización, servidor de recursos, cliente  para que cada uno hace cumplir sólo los controles que le pertenecen.
- Lea una matriz de capacidad de IDP y rechaza desplegar cuando el IDP no pueda satisfacer el perfil de autor de MCP.

## El problema

El simulador de lección 16 ejecuta OAuth 2.1 en memoria. La producción tiene tres lagunas operativas que un simulador de solo memoria no ve.

La primera brecha es la inscripción. Una organización real ejecuta cientos de servidores MCP y miles de clientes MCP. Los operadores no registran a mano a cada usuario Cursor como cliente OAuth. La especificación 2025-11-25 da a los clientes un orden prioritario para resolver esto: usar un cliente pre-registrado `client_id`Si tiene uno, use un**Client ID Metadata Document**(el cliente se identifica con una URL HTTPS que controla y el servidor de autorización *tires* los metadatos), de lo contrario vuelve a **RFC 7591 dynamic client registration**(el cliente * empuja * una `POST /register`y recibe un `client_id`CIMD es el estándar recomendado porque elimina el registro por servidor por completo mientras se mantiene un modelo de confianza rooted en DNS; DCR se conserva para la compatibilidad hacia atrás.`client_id_metadata_document_supported`para la CIMD, `registration_endpoint`para DCR.

La segunda brecha es la rotación de la llave. La validación de JWT depende de las claves de firma del servidor de autorización, publicadas como un conjunto de claves web JSON (JWKS). El servidor de autorización gira estos en un horario (a menudo por hora, a veces más rápido bajo respuesta a incidentes). Un servidor MCP que recoge JWKS una vez en arranque valida bien hasta la ventana de rotación  luego cada solicitud falla hasta que se reinicie. Los cables de producción JWKS como un valor almacenado en caché con un trabajo de actualización que sobrescribe el caché antes de que expiran las claves anteriores, más una retroceso en la caché falta para el caso en que llegue un token firmado por una clave más nueva que el caché.

La tercera brecha es la vinculación de la audiencia. La lección 16 introdujo indicadores de recursos RFC 8707. En producción, ese indicador se convierte en un duro control de reclamaciones en cada solicitud.`token.aud`Esta es la única defensa contra un servidor MCP en alta corriente (o un cliente malicioso que sostiene un token destinado a un servidor) reproduciendo ese token contra otro servidor en la misma malla de confianza.

Esta lección mapea cada hueco en un pedazo de concreto de la superficie. El documento de metadatos es un punto final HTTP. La actualización de la caché JWKS es un trabajo programado más una caché de valor clave. La validación JWT es una rutina que el servidor de recursos ejecuta antes de enviar cualquier herramienta. Mantenga los tres roles separados y cada uno hace cumplir solo los controles que posee: el servidor de autorización emite y gira las claves, el servidor de recursos almacena y valida, el cliente descubre y se inscribe.

## El concepto

### RFC 8414  Metadatos del servidor de autorización OAuth

Un documento en `/.well-known/oauth-authorization-server`describe todo lo que un cliente necesita:

```json
{
  "issuer": "https://auth.example.com",
  "authorization_endpoint": "https://auth.example.com/authorize",
  "token_endpoint": "https://auth.example.com/token",
  "jwks_uri": "https://auth.example.com/.well-known/jwks.json",
  "registration_endpoint": "https://auth.example.com/register",
  "response_types_supported": ["code"],
  "grant_types_supported": ["authorization_code", "refresh_token"],
  "code_challenge_methods_supported": ["S256"],
  "scopes_supported": ["mcp:tools.read", "mcp:tools.invoke"],
  "token_endpoint_auth_methods_supported": ["none", "private_key_jwt"]
}
```

Un cliente que recibió una MCP de recursos URL cadenas de descubrimiento: `oauth-protected-resource`de la RFC 9728 (documento del servidor de recursos) nombra al emisor, luego `oauth-authorization-server`El cliente nunca codifica una URL de autorización.

El contrato que verifique antes de confiar en un IDP para MCP:

- `code_challenge_methods_supported`incluye `S256`La especificación es explícita: si este campo es **absent**, el servidor de autorización no admite PKCE y el cliente **MUST**rechazar continuar.
- `grant_types_supported`incluye `authorization_code`y rechaza.`password`y `implicit`¿ Qué ?
- Se anuncia al menos una ruta de inscripción: `client_id_metadata_document_supported: true`(CIMD, preferido) **or** `registration_endpoint`(RFC 7591 DCR, fallback) O cumple el contrato; ya no requiere DCR.
- `response_types_supported`Es exactamente`["code"]`para la OAuth 2.1.

Si ...`S256`Si el servidor MCP se niega a desplegar contra este IdP  no hay modo degradado para PKCE. Si *Ninguno de los dos* caminos de inscripción se anuncia y no tienes pre-registro `client_id`, también no puede inscribirse; el manifiesto de despliegue está equivocado, no el código.

### RFC 9728 (recapitulación)  Metadatos de recursos protegidos

La lección 16 cubría RFC 9728. El delta en producción: este documento es el único lugar donde un cliente busca para encontrar los servidores de autorización de confianza de *este * servidor MCP. Un solo servidor MCP puede aceptar tokens de múltiples IdPs (uno para el personal, uno para los socios).

```json
{
  "resource": "https://notes.example.com",
  "authorization_servers": ["https://auth.example.com", "https://partners.example.com"],
  "scopes_supported": ["mcp:tools.invoke"],
  "bearer_methods_supported": ["header"],
  "resource_documentation": "https://notes.example.com/docs"
}
```

### Documentación de metadatos de identificación de cliente (el estándar recomendado)

CIMD invierte el registro de *push* a *pull*. En lugar de pedir al servidor de autorización que acuente una `client_id`, el cliente utiliza una URL HTTPS que controla **as**su `client_id`. La URL se resuelve a un documento de metadatos JSON; el servidor de autorización lo recoge a pedido durante el flujo OAuth.`app.example.com`, confía en el cliente atendido de`https://app.example.com/client.json`No hay registro de ida y vuelta, no.`client_id`espacio de nombres para el escape, no hay estado por servidor para mantener en sincronización.

El documento de metadatos alojado por el cliente:

```json
{
  "client_id": "https://app.example.com/oauth/client.json",
  "client_name": "Example MCP Client",
  "client_uri": "https://app.example.com",
  "redirect_uris": ["http://127.0.0.1:7333/callback", "http://localhost:7333/callback"],
  "grant_types": ["authorization_code", "refresh_token"],
  "response_types": ["code"],
  "token_endpoint_auth_method": "none"
}
```

El `client_id`valor en el documento **MUST**igual a la URL desde la que se sirve (el servidor de autorización lo verifica; las incompatibilidades se rechazan).`client_id_metadata_document_supported: true`en sus metadatos de la RFC 8414.

Dos hechos de seguridad que la especificación es directa sobre:

- **SSRF.**El servidor de autorización recoge una URL proporcionada por el atacante. Debe defenderse contra la falsificación de las solicitudes del lado del servidor (no se recogen puntos finales internos / administradores).
- **localhost impersonation.**CIMD por sí solo no puede impedir que un atacante local reclame la URL de metadatos de un cliente legítimo y vincule cualquier `localhost`Redireccionar. El servidor de autorización **MUST**mostrar claramente el nombre de alojamiento de redirección URI durante el consentimiento y **SHOULD**Advertencia sobre `localhost`- Sólo redirecciones.

Como CIMD no necesita estado del lado del servidor, no hay registrador para mantenerse de la manera que requiere DCR. El lado del cliente es de lectura única: sirva su documento de metadatos desde un punto final HTTPS estático y deja que el servidor de autorización lo tire.

### RFC 7591  Registro de clientes dinámico (compatibilidad retroactiva)

DCR es ahora un`MAY`Sin él (y sin CIMD o registro previo), cada cliente MCP (Cursor, Claude Desktop, un agente personalizado) necesita un intercambio fuera de banda con el administrador IdP. Con DCR, los mensajes del cliente:

```json
POST /register
Content-Type: application/json

{
  "redirect_uris": ["http://127.0.0.1:7333/callback"],
  "grant_types": ["authorization_code", "refresh_token"],
  "response_types": ["code"],
  "token_endpoint_auth_method": "none",
  "scope": "mcp:tools.invoke",
  "client_name": "Cursor",
  "software_id": "com.cursor.cursor",
  "software_version": "0.42.0"
}
```

El servidor responde con `client_id`y un `registration_access_token`para actualizaciones posteriores:

```json
{
  "client_id": "c_3e7f1a",
  "client_id_issued_at": 1769472000,
  "redirect_uris": ["http://127.0.0.1:7333/callback"],
  "grant_types": ["authorization_code", "refresh_token"],
  "registration_access_token": "regt_b2...",
  "registration_client_uri": "https://auth.example.com/register/c_3e7f1a"
}
```

`token_endpoint_auth_method: none`es el estándar correcto para los clientes MCP que se ejecutan en el dispositivo del usuario.`client_id`Sólo  no `client_secret`PKCE proporciona la prueba de posesión que los clientes públicos necesitan.

Tres trampas de producción:

- El punto final de registro debe ser limitado por IP de origen.`client_id`Eche un control de límite de tarifas antes de que el registrador maneje la solicitud.
- `software_statement`La simulación de la lección lo omite; el cable de producción realiza un paso de verificación que rechaza los registros sin firmar de cualquier otra cosa que no sea redirigir URI localhost.
- El `registration_access_token`El robo de este token significa que el atacante puede reescribir los URI de redirección del cliente.

### RFC 8707 (recapitación)  Indicadores de recursos

La lección 16 estableció la forma. La regla de producción: cada solicitud de token incluye `resource=<canonical-mcp-url>`, y el servidor MCP verifica `token.aud`La URI canónica es el identificador más específico para el servidor: utiliza esquema en minúsculas y host, no hay fragmento y convencionalmente no hay slash.**not**La especificación se mantiene cuando se necesita para identificar un servidor MCP individual.`https://mcp.example.com`¿ Qué ?`https://mcp.example.com/mcp`¿ Qué ?`https://mcp.example.com:8443`, y `https://mcp.example.com/server/mcp`Todos son URI canónicos válidos.`aud`(La simulación de esta lección utiliza a los públicos de anfitrión desnudo como`https://notes.example.com`para ser breves; una implementación que alberga varios servidores MCP bajo un mismo origen los distingue por su trayectoria.)

### RFC 7636 (recapitación)  PKCE

El PKCE es obligatorio en OAuth 2.1.`code_challenge`y `code_verifier`El servidor rechaza cualquier solicitud de token sin un verificador o con un verificador que no hash al desafío almacenado.

### MCP Spec 2025-11-25 Perfil de autor

La especificación MCP (2025-11-25) es precisa sobre lo que debe hacer la capa de autorización de un servidor MCP:

- Implementar los metadatos de recursos protegidos de la RFC 9728, y proporcionar su ubicación a través de la `WWW-Authenticate: Bearer resource_metadata="..."`encabezado en un 401 **or**el conocido URI `/.well-known/oauth-protected-resource`(SEP-985 hizo que el encabezado fuera opcional con una caída conocida).`authorization_servers`campo **MUST**nombrar al menos un servidor.
- Solo acepta tokens a través de `Authorization: Bearer ...`En el**every**requisito  nunca en una cadena de consulta, nunca validado solo al inicio de la sesión.
- Validación`aud`¿ Qué ?`iss`¿ Qué ?`exp`, y los límites requeridos por solicitud.**MUST**validar que el token fue emitido específicamente para él (audiencia); una falta o falta de coincidencia `aud`se rechaza, nunca se trata como un cartón salvaje.
- En 401/403, regreso `WWW-Authenticate: Bearer`transporte `error=...`, el `resource_metadata="<PRM-URL>"`Parámetro (la URL del documento de metadatos, *no* el recurso desnudo), y `scope="..."`En el`insufficient_scope`(403). Nota: el parámetro es `resource_metadata`, un indicador de descubrimiento  no hay `resource`Parámetro en el reto.
- El servidor de autorización acepta el descubrimiento .**either**RFC 8414 Metadatos de la autoridad **or**OpenID Connect Discovery 1.0; los clientes deben probar ambos sufijos conocidos en orden de prioridad.
- El cliente (no el servidor) se defiende contra **mix-up attacks**: registra lo esperado `issuer`antes de redirigir y validar el `iss`El código de acceso de la base de datos de la base de datos de la base de datos de la base de datos de la base de datos de la base de datos de la base de datos de la base de datos de la base de datos de la base de datos de la base de datos de la base de datos de la base de datos de la base de datos de la base de datos de la base de datos de la base de datos de datos de la base de datos de datos de la base de datos de datos de la base de datos de datos de la base de datos de datos de datos de la base de datos de datos de datos de la base de datos de datos de datos de datos de la base de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos`code_verifier`a cualquiera que sea el punto final simbólico al que fue dirigido.

El borrador OAuth 2.1 es el sustrato; RFC 8414/7591/8707/9728/9207 + RFC 7636 + CIMD son la superficie; la especificación MCP es el perfil.

### Matriz de capacidad de IDP

No todos los IDP admiten el perfil completo de MCP. La matriz a continuación documenta las declaraciones de capacidad de hecho a partir de la especificación 2025-11-25. Es una *puerta de despliegue*, no una recomendación.

CIMD fue enviado en la especificación 2025-11-25 y el borrador subyacente de OAuth fue adoptado solo en octubre de 2025, por lo que el soporte de proveedores todavía está llegando  trate "CIMD" a continuación como "donde está hoy, verifique en su inquilino", no una declaración permanente.

| IdP category | AS metadata (8414/OIDC) | CIMD | RFC 7591 DCR | RFC 8707 resource | RFC 7636 S256 PKCE | Notes |
|---|---|---|---|---|---|---|
| Self-hosted (Keycloak) | yes | emerging | yes | yes (since 24.x) | yes | Reference IdP for the MCP profile in this lesson; full DCR path end-to-end, CIMD tracking the new spec. |
| Enterprise SSO (Microsoft Entra ID) | yes | emerging | yes (premium tiers) | yes | yes | DCR availability differs by tenant tier; verify in target tenant before deploying. |
| Enterprise SSO (Okta) | yes | emerging | yes (Okta CIC / Auth0) | yes | yes | DCR available on Auth0 (now Okta CIC); classic Okta orgs require admin pre-registration. |
| Social login IdPs (generic) | varies | no | rarely | rarely | yes | Most social IdPs treat clients as static partners; no self-service enrollment. Use as identity source only, layer your own MCP-aware authorization server on top. |
| Custom / homegrown | depends | depends | depends | depends | depends | If you ship your own, ship the full profile and prefer CIMD. Skipping PKCE or audience binding breaks the MCP auth contract. |

Regla de rechazo para el manifiesto de despliegue: si el IDP elegido no incluye `S256`En el`code_challenge_methods_supported`, el servidor MCP se niega a iniciar  PKCE no tiene modo degradado.`client_id`¿ Qué ?`client_id_metadata_document_supported: true`, o un `registration_endpoint`La ausencia de DCR por sí sola ya no es un factor de rechazo, ya que puede ser cubierta por la CIMD o por la preinscripción.

### Modelo de actualización de JWKS (rotar en el AS, actualizar en el servidor de recursos)

Mantenga dos verbos separados, porque mezclarlos es un verdadero error de producción:

- **Rotate**El servidor de recursos no tiene parte en esto y no puede hacerlo  no contiene las claves privadas del IDP.
- **Refresh**¿Es lo que hace el servidor de recursos?`GET`Es la única acción de JWKS que un servidor de recursos realiza.

El modo de falla de producción es un caché obsoleto. Resolva con un trabajo de actualización programado más un caché de valor clave. El servidor de recursos ejecuta un trabajo (cron, cron, lo que sea que su tiempo de ejecución ofrezca) que, en un intervalo fijo, trae `<issuer>/.well-known/jwks.json`y sobreescribe .`cache[issuer] = {keys, fetched_at}`El validador lee desde ese caché.`kid`se ha perdido en los gatilladores de caché **one**La actualización sincrónica como una retroceso, luego vuelve a comprobar. Esto maneja dos casos a la vez: la actualización programada y las ventanas de sobreposición de teclas donde un token firmado por una clave nueva llega antes de la próxima actualización programada.

El retroceso .**must be a re-fetch, never a rotate**Si se fija el camino de caché-miss a una rotación-y-minta, dos cosas se rompen: (1) la acuñación de una llave nueva produce un `kid`que *todavía* no coincide con el token, por lo que la búsqueda falla de todos modos; y (2) un atacante que rocía tokens con aleatorios `kid`Los valores forzan una serie ilimitada de creaciones clave  un autoinfligido DoS. Una re-recaudación es impotente, por lo que una falsa `kid`El precio de la compra es un gasto de una compra perdida.

La forma del caché:

```json
{
  "https://auth.example.com": {
    "keys": [
      {"kid": "k_2026_03", "kty": "RSA", "n": "...", "e": "AQAB", "alg": "RS256", "use": "sig"},
      {"kid": "k_2026_04", "kty": "RSA", "n": "...", "e": "AQAB", "alg": "RS256", "use": "sig"}
    ],
    "fetched_at": 1772668800
  }
}
```

Los servidores de autorización rotan introduciendo la siguiente tecla (`k_2026_04`) antes de retirarse del anterior (`k_2026_03`), por lo que los tokens emitidos bajo la vieja clave permanecen válidos hasta que expiran.`kid`¿ Qué ?

### El procedimiento de validación

El servidor MCP ejecuta la validación antes de enviar cualquier herramienta.`code/main.py`usos:

```python
result = server.validate(bearer_token, required_scope="mcp:tools.invoke")
if not result["valid"]:
    return {"status": result["status"], "WWW-Authenticate": result["www_authenticate"]}
```

`validate`Descifrar el JWT, resolver la clave de firma de la caché JWKS (refrenchar una vez en una falta), verificar la firma, luego comprobar `iss`contra la lista de permisos, `aud`contra el recurso canónico de este servidor,`exp`, y el alcance requerido  devolver un `WWW-Authenticate`El sistema de control de las herramientas de gestión de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de datos de

### Reproducción de audiencia (restricción de privilegios de acceso a los tokens)

Servicio A (`notes.example.com`) y el servidor B (`tasks.example.com`El servidor A está comprometido. El atacante toma el token de notas de un usuario y lo repite contra el servidor B.

El validador del servidor B:

1. Descifrar JWT, traer JWKS por `kid`, verifique la firma.
2. - ¿ Qué ?`iss`contra los metadatos de sus recursos protegidos `authorization_servers`. (Pasa  mismo IDP.)
3. - ¿ Qué ?`aud == "https://tasks.example.com"`. (Faltó el token                                                                                                                                                                                                                                                            `aud`¿ Es verdad ?`https://notes.example.com`(en inglés).
4. Regresa el 401 con `WWW-Authenticate: Bearer error="invalid_token", error_description="audience mismatch", resource_metadata="https://tasks.example.com/.well-known/oauth-protected-resource"`¿ Qué ?

La afirmación de la audiencia es la única defensa contra este ataque en la capa de protocolo. Saltarlo por rendimiento es el error de producción más común; el validador debe ejecutarse en cada solicitud, no solo al inicio de la sesión.**access-token privilege restriction**: un servidor MCP `MUST`rechazar cualquier token que no lo nombre en la audiencia.

> **Naming note.**La especificación reserva el término "dependiente confuso" para un problema relacionado pero distinto: un servidor de MCP que actúa como OAuth **proxy**a una API de terceros, utilizando un ID de cliente estático, que reenvía un token sin obtener el consentimiento del usuario por cliente. Audience binding corrige la repetición anterior; la solución de confusión-deputado es el consentimiento por cliente **plus**nunca pasar el token entrante a través de las API de aguas arriba (el servidor MCP `MUST`Obtenga su propio token upstream separado).

### Ataques mezclados (una defensa del lado del cliente que el servidor no puede proporcionar)

Un cliente habla con muchos servidores de autorización durante su vida. Un AS malicioso puede intentar que el cliente canjee el código de autorización de un AS honesto en el punto final de token del atacante.

1. Antes de redirigir, el cliente registra el esperado `issuer`de los metadatos de AS validados.
2. En la respuesta de autorización, el cliente compara los devueltos `iss`Parámetro frente a ese emisor registrado (comparación de cadenas sencillas, sin normalización) antes de enviar el código a cualquier lugar.
3. Desajuste (o `iss`ausente cuando el AS publicitó `authorization_response_iss_parameter_supported`) → rechazar, y ni siquiera mostrar la`error`los campos.

PKCE no deja de confundir, porque el cliente le entrega su`code_verifier`En el caso de los datos de la entidad de emisión, el valor de la entidad de emisión se calcula en el punto final de la marca de referencia.`state`¿ Qué ?

### Modo de falla

- **Stale JWKS.**El validador rechaza los tokens válidos después de que el AS gire una clave. La solución es el patrón cron-refresh + cache-miss-refetch arriba. Nunca cache JWKS sin un trabajo de actualización.
- **Rotate-as-fall-back.**El cableado de la ruta de caché-falta a una rotación-y-minta en lugar de una re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re-re`kid`, y se vuelve controlado por el atacante .`kid`Los valores de la base de datos deben ser introducidos en un sistema de gestión de datos de creación de claves.`refresh-jwks`¿ Qué ?
- **Missing `aud` claim.**Algunos IPs omiten por defecto `aud`a menos que`resource`El validador debe rechazar los tokens con falta `aud`, no tratar la ausencia como un juego salvaje.
- **Mix-up via missing `iss` check.**Un cliente que no valida la RFC 9207 `iss`El parámetro de respuesta de autorización contra el emisor que registró antes de redirigir puede ser dirigido a canjear el código de un AS honesto en el punto final de token de un atacante.
- **Scope upgrade race.**Dos flujos de incremento simultáneos para el mismo usuario pueden tener éxito y producir dos tokens de acceso con diferentes escalones. El validador debe usar el token presentado en la solicitud, no buscar "el alcance actual del usuario"  que crea una ventana TOCTOU.
- **Registration token theft.**Una filtrada .`registration_access_token`El usuario puede usar un dispositivo de redirección de URLs para que el atacante pueda reescribir los URLs.
- **`iss` not pinned.**Un validador que acepta cualquier`iss`permite a un atacante crear su propio servidor de autorización, registrar un cliente para el público objetivo y emitir tokens.`authorization_servers`lista es la lista de permisos; hacer cumplir.

```figure
t3-jwks-rotate
```

## Usalo

`code/main.py`camina el flujo de producción completo con stdlib Python y tres roles  `AuthorizationServer`¿ Qué ?`ResourceServer`, y `Client`El flujo:

1. El servidor de autorización publica los metadatos RFC 8414 en `/.well-known/oauth-authorization-server`¿ Qué ?
2. El cliente de MCP llama al punto final de metadatos y verifica sus opciones de inscripción (`client_id_metadata_document_supported`para la CIMD, `registration_endpoint`para DCR) y `S256`Apoyo de la PKCE.
3. El paseo recorre el camino de retrocesión de DCR: el cliente publica a `/register`(RFC 7591) y recibe una`client_id`(Un cliente de CIMD presentaría su propio HTTPS `client_id`URL y salte este paso.)
4. El cliente MCP ejecuta el flujo de código de autorización protegido por PKCE (RFC 7636) con `resource`Indicador (RFC 8707).
5. El cliente MCP llama a una herramienta en el servidor MCP con `Authorization: Bearer ...`¿ Qué ?
6. El servidor MCP se ejecuta `validate`, resolviendo la clave de firma de la caché JWKS.
7. El IDP gira una llave; la actualización programada vuelve a tirar de la JWKS en la caché.
8. La siguiente llamada se valida contra las teclas actualizadas sin reiniciar, y el token anterior sigue validando durante la ventana de superposición.
9. Un intento de reproducción de audiencia contra otro recurso de MCP obtiene 401 con`audience mismatch`y un `resource_metadata`- ¿Qué es eso?

La JWT aquí utiliza HS256 con un secreto compartido (así que la lección se ejecuta solo en stdlib). La producción utiliza RS256 o EdDSA con el patrón JWKS arriba; la lógica de validación es idéntica. Debido a que el servidor de recursos y el IdP viven en un proceso, `refresh_jwks`lee directamente la lista de claves del servidor de autorización; por cable es un HTTP `GET`¿ Qué ?`jwks_uri`¿ Qué ?

## Envío

Esta lección produce`outputs/skill-mcp-auth.md`. Dado una configuración de servidor MCP y un conjunto de capacidades de IdP, la habilidad emite la superficie de autor para mantenerse  los metadatos de recursos protegidos, la ruta de inscripción a utilizar (CIMD, pre-registro o retroceso de DCR), el horario de actualización de JWKS, el mapeo de alcance y las reglas de rechazo a aplicar cuando el IdP no admite el perfil completo de RFC.

## Los ejercicios

1. - ¿ Qué ?`code/main.py`Observe cómo el IDP gira una tecla en el paso 6, el programa `refresh_jwks`retira el conjunto publicado, y tanto el token antiguo (ventana de superposición) como un token nuevo se validan sin reiniciar.

2. Añadir un nuevo IDP a los metadatos de los recursos protegidos `authorization_servers`Emite un token firmado por el nuevo IDP y confirme que el validador lo acepta. Emite un token firmado por un IDP no listado y confirme que el validador lo rechaza con `WWW-Authenticate: Bearer error="invalid_token", error_description="iss not allowed"`¿ Qué ?

3. Añadir un control de límite de tarifas a `register_client`Utilice un token-bucket por IP fuente guardado en un pequeño dictado con teclado IP.

4. Lea RFC 7591 y identifique dos campos de la lección `/register`El controlador no valida. Añade la validación.`software_statement`y `redirect_uris`Sistema de URI.)

5. Añadir un camino de Metadatos de Documento de ID del Cliente.`client.json`cuyo `client_id`igual a su propia URL, y el servidor de autorización traiga y verifique (rechazar si `client_id`≠ URL). Confirmar que un cliente de CIMD se inscribe sin ningún `register_client`¿Qué pasa?

6. Prueba la corrección del Departamento de Servicios, envíe al validador un token con un aleatorio.`kid`y confirmar`refresh_jwks`se ejecuta como máximo una vez y el número de claves del servidor de autorización no crece. Luego volver a cablear deliberadamente la caída de vuelta a una rotación y ver el número de claves subir por token falso

7. Implementar el RFC 9207 del lado del cliente `iss`verificación desde la sección de mezcla: registrar el emisor esperado antes de la solicitud de autorización, luego rechazar una respuesta de autorización cuya `iss`No coincide.

## Términos clave

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| ASM | "OAuth metadata document" | RFC 8414 `/.well-known/oauth-authorization-server` JSON |
| CIMD | "Client metadata URL" | Client ID Metadata Document — an HTTPS URL used as the `client_id`; the AS pulls the JSON. Recommended default since 2025-11-25 |
| DCR | "Self-service client registration" | RFC 7591 `POST /register` flow; demoted to a `MAY` fallback in 2025-11-25 |
| JWKS | "Public keys for JWT validation" | JSON Web Key Set, fetched from `jwks_uri`, indexed by `kid` |
| Rotate vs refresh | "Updating the keys" | *Rotate* = AS mints/retires signing keys; *refresh* = resource server re-fetches the published set. Resource servers only ever refresh |
| Resource indicator | "Audience parameter" | RFC 8707 `resource` parameter pinning the token to one server |
| `aud` claim | "Audience" | JWT claim the validator compares against the canonical resource URL |
| Audience replay | "Token replay" | Token issued for Server A presented to Server B; defended by audience validation (spec: access-token privilege restriction) |
| Confused deputy | "Proxy token misuse" | An MCP proxy with a static client ID forwarding a token without per-client consent; distinct from audience replay |
| Mix-up attack | "Wrong token endpoint" | Client steered to redeem an honest AS's code at an attacker's endpoint; defended client-side via RFC 9207 `iss` |
| `iss` allow-list | "Trusted authorization servers" | The set named in protected-resource metadata's `authorization_servers` |
| `resource_metadata` | "Where to find the PRM doc" | `WWW-Authenticate` parameter naming the RFC 9728 metadata URL on a 401/403 |
| Public client | "Native or browser client" | OAuth client with no `client_secret`; PKCE compensates |
| `WWW-Authenticate` | "401/403 response header" | Carries `Bearer error=...` directives that drive client recovery |

## Leer más

- [MCP — Authorization spec (2025-11-25)](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization) el perfil de autor del MCP esta lección implementa
- [MCP blog — One Year of MCP: November 2025 Spec Release](https://blog.modelcontextprotocol.io/posts/2025-11-25-first-mcp-anniversary/) lo que cambió en 2025-11-25 (CIMD, XAA, reducción de la RDC)
- [Aaron Parecki — Client Registration in the November 2025 MCP Authorization Spec](https://aaronparecki.com/2025/11/25/1/mcp-authorization-spec-update) la razón de la CIMD sobre la DCR
- [OAuth Client ID Metadata Document (draft-ietf-oauth-client-id-metadata-document-00)](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-client-id-metadata-document-00) CIMD
- [RFC 8414 — OAuth 2.0 Authorization Server Metadata](https://datatracker.ietf.org/doc/html/rfc8414) contrato de descubrimiento
- [RFC 7591 — OAuth 2.0 Dynamic Client Registration Protocol](https://datatracker.ietf.org/doc/html/rfc7591) DCR (caminada de retroceso)
- [RFC 7636 — Proof Key for Code Exchange (PKCE)](https://datatracker.ietf.org/doc/html/rfc7636) Proveedor de posesión de un cliente público
- [RFC 8707 — Resource Indicators for OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc8707) Pinning de la audiencia
- [RFC 9728 — OAuth 2.0 Protected Resource Metadata](https://datatracker.ietf.org/doc/html/rfc9728) descubrimiento de servidores de recursos
- [RFC 9207 — OAuth 2.0 Authorization Server Issuer Identification](https://datatracker.ietf.org/doc/html/rfc9207) el `iss`Parámetro que se defiende contra ataques de mezcla
- [OAuth 2.1 draft](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1) el sustrato consolidado de OAuth
