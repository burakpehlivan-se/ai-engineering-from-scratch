# Puertas de acceso y registros de MCP  Planes de control de empresas

> Las empresas no pueden permitir que cada desarrollador instale servidores MCP aleatorios. Una puerta de entrada centraliza auth, RBAC, auditoría, limitación de velocidad, almacenamiento en caché y detección de intoxicación de herramientas, luego expone la superficie de la herramienta fusionada como un único punto final de MCP. El Registro Oficial de MCP (Antropic + GitHub + PulseMCP + Microsoft, verificado por el espacio de nombres) es el canónico upstream. Esta lección nombra dónde encaja una puerta de entrada, realiza una implementación mínima y analiza el panorama de los proveedores en 2026.

**Type:** Learn
**Languages:** Python (stdlib, minimal gateway)
**Prerequisites:** Phase 13 · 15 (tool poisoning), Phase 13 · 16 (OAuth 2.1)
**Time:** ~45 minutes

## Objetivos de aprendizaje

- Explicar dónde se encuentra una puerta de entrada MCP (entre los clientes MCP y varios servidores MCP backend).
- Implementar las cinco responsabilidades de la puerta de entrada: auth, RBAC, auditoría, límite de tasas y política.
- Aplique un manifiesto de herramienta en la capa de la puerta de entrada.
- Diferenciar el Registro Oficial de MCP de los metaregistros (Glama, MCPMarket, MCP.so, Smithery, LobeHub).

## El problema

Un Fortune 500 tiene 30 servidores MCP aprobados, 5000 desarrolladores, requisitos de cumplimiento y auditoría, y un equipo de seguridad que quiere políticas centralizadas.

El patrón de la puerta de entrada:

1. Gateway se ejecuta como un solo desarrollador de endpoint HTTP Streamable se conecta a.
2. Gateway tiene credenciales para cada servidor MCP de backend.
3. Cada solicitud del desarrollador se autentica y se escoge a través de la propia OAuth de la puerta de entrada.
4. Gateway envía la llamada al servidor de backend, aplicando la política.
5. Todas las llamadas registradas para auditoría.

Portais MCP de Cloudflare, Kong AI Gateway, IBM ContextForge, MintMCP, TrueFoundry, Envoy AI Gateway  todos los gateways o características de gateway enviados en 2025-2026.

Mientras tanto, el Registro Oficial de MCP se lanzó como el canónico upstream: servidores curados, verificados por el espacio de nombres, con nombres DNS inverso de los que la puerta de entrada puede extraer.

## El concepto

### Cinco responsabilidades de la puerta de entrada

1. **Auth.**OAuth 2.1 para identificar al desarrollador; mapas de los roles de los usuarios.
2. **RBAC.**Política por usuario: qué servidores, qué herramientas, qué ámbitos.
3. **Audit.**Cada llamada registrada con quién, qué, cuándo, resultado.
4. **Rate limit.**Capas por usuario / herramienta / servidor para evitar el abuso.
5. **Policy.**Rechazar descripciones envenenadas, hacer cumplir la regla de dos, redactar PII.

### Puerta de entrada como un único punto final

Para los desarrolladores, la puerta de enlace se parece a un servidor MCP. Internamente se rúa a N backends.

### El vaulting de credenciales

Los desarrolladores nunca ven tokens de backend. La puerta de enlace los mantiene (o los proxies a un proveedor de identidad que lo hace).`notes:read`en la puerta de entrada puede acceder de forma transitoria al servidor de notas MCP con las propias credenciales de backend de la puerta de entrada  pero sólo bajo la política que vincule el acceso transitorio.

### Pinificación de herramientas en la puerta

La puerta de entrada contiene un manifiesto de descripciones de herramientas aprobadas (hashes SHA256).`tools/list`, compara hashes con el manifiesto, y elimina cualquier herramienta cuya descripción ha mutado. Esta es la defensa de tirón de alfombra de la fase 13 · 15 aplicada de forma central.

### Política como código

Las puertas de entrada avanzadas expresan la política en OPA/Rego, Kyverno o Styra. Reglas como "usuario `alice`puede llamar`github.open_pr`sólo en repos en org`acme`" se codifican declarativamente. Puertas de acceso simples utilizan Python codificado a mano. Ambas formas son válidas.

### Enrutamiento consciente de la sesión

Cuando la sesión de un usuario incluye una mezcla de servidores, los multiplexes de puerta de enlace: la sesión MCP única del desarrollador tiene N sesiones de backend, una por servidor. Notificaciones de cualquier ruta de backend a través de la puerta de enlace a la sesión del desarrollador.

### Fusión de espacio de nombres

Gateways fusionan espacios de nombres de herramientas de todos los fondos, típicamente con prefijo en colisión. `github.open_pr`¿ Qué ?`notes.search`Esto hace que el enrutamiento sea inequívoco.

### Registros

- **Official MCP Registry (`registry.modelcontextprotocol.io`).**Lanzado bajo la administración de Anthropic, GitHub, PulseMCP, Microsoft.`io.github.user/server`), pre-filtrado para la calidad básica.
- **Glama.**Metaregistros centrados en la búsqueda que agrupan muchas fuentes.
- **MCPMarket.**Directorio de inclinación comercial con listados de vendedores.
- **MCP.so.**Directorio comunitario; presentaciones abiertas.
- **Smithery.**Flujo de instalación de estilo de paquete de gestión.
- **LobeHub.**Registro integrado en la interfaz de usuario en su aplicación LobeChat.

Las pasarelas de la empresa se extraen del Registro Oficial por defecto, permiten adiciones administradas por los metaregistros y rechazan cualquier cosa sin fijar.

### Nombramiento de DNS inverso

El Registro Oficial exige nombres de DNS invertidos para servidores públicos: `io.github.alice/notes`Los espacios de nombres evitan las agachadas y hacen más clara la delegación de confianza.

### Encuesta de proveedores, abril 2026

| Vendor | Strength |
|--------|----------|
| Cloudflare MCP Portals | Edge-hosted; OAuth integrated; free tier |
| Kong AI Gateway | K8s-native; fine-grained policy; logs to OpenTelemetry |
| IBM ContextForge | Enterprise IAM; compliance; audit export |
| TrueFoundry | DevOps-leaning; metrics-first |
| MintMCP | Developer-platform oriented |
| Envoy AI Gateway | Open-source; customizable filters |

La fase 17 (infraestructura de producción) profundiza en las operaciones de la puerta de entrada.

```figure
t3-gateway-funnel
```

## Usalo

`code/main.py`Envía una puerta de enlace mínima en ~ 150 líneas: autentica a los usuarios con un token Bearer falso, mantiene una política RBAC por usuario, envía solicitudes a dos servidores MCP backend, escribe cada llamada a un registro de auditoría, impone un límite de tasas y rechaza cualquier herramienta backend cuya descripción hash no coincide con un manifiesto fijado.

Qué ver:

- `RBAC`dictado por `user_id`con permitido `server_tool`las entradas.
- `AUDIT_LOG`es una lista de eventos sólo en apéndice.
- El límite de tasa utiliza un cubo de tokens por usuario.
- El manifiesto en fijación es un dictado de `server::tool -> hash`¿ Qué ?

## Envío

Esta lección produce`outputs/skill-gateway-bootstrap.md`. Dado un plan de MCP empresarial (usuarios, backends, cumplimiento), la habilidad produce una especificación de configuración de puerta de enlace.

## Los ejercicios

1. - ¿ Qué ?`code/main.py`. Llamen como un usuario autorizado, luego como un usuario no autorizado, luego una explosión excediendo el límite de tarifa.

2. Añadir una política que redacta PII de los resultados antes de regresar al cliente. Utilice un simple pase de regex para cadenas en forma de SSN; note la brecha ( correos electrónicos, números de teléfono).

3. Extensión del registro de auditoría para emitir extensiones de OpenTelemetry GenAI. La fase 13 · 20 cubre los atributos exactos.

4. Diseñar una política RBAC para un equipo de 50 desarrolladores con cinco backends (notas, github, postgres, jira, slack). ¿Quién recibe sólo lectura en cada uno? ¿Quién recibe escribir?

5. Lea el post MCP de Cloudflare Enterprise de arriba a abajo. Identifique una característica que Cloudflare navega que esta puerta de enlace stdlib no tiene.

## Términos clave

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| Gateway | "MCP proxy" | Centralizing server between clients and backends |
| Credential vaulting | "Backend tokens stay server-side" | Developers never see upstream tokens |
| Session-aware routing | "Multi-backend session" | Gateway multiplexes N backend sessions per developer session |
| Tool-hash pinning | "Approved manifest" | SHA256 of every approved tool description; blocks rug-pulls centrally |
| RBAC | "Per-user policy" | Role-based access control for tools and servers |
| Policy-as-code | "Declarative rules" | OPA/Rego, Kyverno, Styra policies enforced at gateway |
| Audit log | "Who, what, when" | Append-only event log for compliance |
| Rate limit | "Per-user token bucket" | Per-minute caps to prevent abuse |
| Official MCP Registry | "Canonical upstream" | `registry.modelcontextprotocol.io`, namespace-verified |
| Reverse-DNS naming | "Registry namespace" | `io.github.user/server` convention |

## Leer más

- [Official MCP Registry](https://registry.modelcontextprotocol.io/) canónica en aguas arriba, verificada por el espacio de nombres
- [Cloudflare — Enterprise MCP](https://blog.cloudflare.com/enterprise-mcp/) Modelo de entrada con OAuth y política
- [agentic-community — MCP gateway registry](https://github.com/agentic-community/mcp-gateway-registry) Puerta de referencia de código abierto
- [TrueFoundry — What is an MCP gateway?](https://www.truefoundry.com/blog/what-is-mcp-gateway) artículo de comparación de características
- [IBM — MCP context forge](https://github.com/IBM/mcp-context-forge) Puerta de entrada empresarial de IBM
