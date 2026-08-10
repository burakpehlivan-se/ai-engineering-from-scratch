# Capstone 13  MCP Server con registro y gobierno

> El Protocolo Contextual Modelo dejó de ser el futuro y se convirtió en la especificación de uso de herramientas predeterminada en 2026. Anthropic, OpenAI, Google y todos los principales clientes de IDE envían MCP. Pinterest publicó su ecosistema interno de servidores MCP.`.well-known`. AWS ECS publicó la implementación sin estado de referencia. El agente de ganso de Block colocó el mismo protocolo dentro de un asistente alojado. La forma de producción 2026 es: transporte StreamableHTTP, escopo OAuth 2.1, puertas de política OPA y un registro que permite a los equipos de la plataforma descubrir, validar y habilitar servidores. Construye ese final hasta el final.

**Type:** Capstone
**Languages:** Python (server, via FastMCP) or TypeScript (@modelcontextprotocol/sdk), Go (registry service)
**Prerequisites:** Phase 11 (LLM engineering), Phase 13 (tools and MCP), Phase 14 (agents), Phase 17 (infrastructure), Phase 18 (safety)
**Phases exercised:**P11 · P13 · P14 · P17 · P18
**Time:** 25 hours

## El problema

MCP se convirtió en la lengua franca de uso de herramientas. Claude Code, Cursor 3, Amp, OpenCode, Gemini CLI, y todos los agentes administrados ahora consumen servidores MCP. Los desafíos de producción no son la creación de servidores (FastMCP lo hace fácil) sino su implementación a escala con los requisitos de la empresa: alcance de OAuth por inquilino, política de OPA sobre herramientas destructivas, escalación sin estado de StreamableHTTP, un registro para el descubrimiento, registros de auditoría por llamada de herramienta. El ecosistema interno de MCP de Pinterest y la especificación del Registro AAIF establecen la barra de 2026.

Se construirá un servidor MCP que exponga 10 herramientas internas (Postgres solo para lectura, listado S3, Jira, Linear, Datadog, etc.), una interfaz de usuario de registro para el descubrimiento de la plataforma y una puerta de aprobación humana para herramientas destructivas. La prueba de carga demuestra la escala horizontal de StreamableHTTP.

## Concepto

MCP 2026 revisión manda StreamableHTTP como el transporte predeterminado. A diferencia de la forma anterior de stdio-y-SSE, StreamableHTTP es estatal por defecto: un único punto final HTTP acepta solicitudes JSON-RPC, transmite respuestas y admite conexiones de larga duración para notificaciones.

La autorización es OAuth 2.1 con escalones por herramienta.`jira:read`¿ Qué ?`s3:list`¿ Qué ?`postgres:query:readonly`El servidor MCP verifica los escalones en el momento de la llamada de la herramienta, no solo en el inicio de la sesión.`approved:by:human`En los últimos N minutos  esa elevación proviene de una tarjeta de revisión Slack.

El registro es un servicio separado.`.well-known/mcp-capabilities`El documento con su manifiesto de herramientas, URL de transporte, requisitos de autor. Las encuestas de registro, validaciones e índices.

## Arquitectura

```
MCP client (Claude Code, Cursor 3, ...)
          |
          v
StreamableHTTP over HTTPS (JSON-RPC + streaming)
          |
          v
MCP server (FastMCP) behind load balancer
          |
   +------+------+---------+----------+------------+
   v             v         v          v            v
Postgres    S3 listing  Jira       Linear     Datadog
(read-only) (paged)     (read)     (read)     (query)
          |
   +------+-------------+
   v                    v
 OPA policy gate   destructive tool MCP (separate server)
                        |
                        v
                   human approval via Slack
                        |
                        v
                   audit log (append-only, per-tenant)

  registry service
     |
     v  GET /.well-known/mcp-capabilities from each server
     v
     UI: search / validate / enable-disable / ownership
```

## El establo

- Framework de servidor: FastMCP (Python) o `@modelcontextprotocol/sdk`¿Qué es eso ?
- Transporte: StreamableHTTP por HTTPS (sin estado)
- Autorización: Autorización 2.1 con identidad de carga de trabajo a través de SPIFFE / SPIRE
- Política: Reglas de la OPA y de la Rego por herramienta; servicio de decisión de política por solicitud
- Registro: auto-hosted, consuma `.well-known/mcp-capabilities`Manifiestos
- Aprobación humana: Mensaje interactivo de Slack para herramientas destructivas
- Despliegue: AWS ECS Fargate o Fly.io, un servidor por inquilino o compartido con el alcance de los inquilinos
- Auditoría: cubo estructurado JSONL por inquilino con linaje por llamada

```figure
cf-mcp-gate
```

## Construye el mismo

1. **Tool surface.**Exponer 10 herramientas internas: consulta de lectura única de Postgres, objetos de lista S3, búsqueda/recuperada de Jira, búsqueda/recuperada de Linear, consulta métrica Datadog, búsqueda de datos en llamada de PagerDuty, consulta de lectura única de GitHub, búsqueda de nociones, búsqueda Slack, lectura de Salesforce. Cada herramienta tiene un esquema de tipografía y una etiqueta de alcance.

2. **FastMCP server.**Montar las herramientas. Configurar el transporte de StreamableHTTP. Agregar un middleware para la introspección de tokens OAuth y la aplicación del alcance.

3. **OPA policy.**Política de reglas por herramienta: qué ámbitos permiten la invocación, qué redacción de PII se aplica, qué límites de tamaño de carga útil se aplican.

4. **Registry service.**Servicio separado de Go o TS que realiza encuestas `.well-known/mcp-capabilities`de servidores registrados, se valida con JSON Schema, y expone una lista / búsqueda / validación / desactivar UI.

5. **Capability manifest.**Cada servidor expone `.well-known/mcp-capabilities`con: lista de herramientas, requisitos de autor, URL de transporte, equipo de propietarios, SLO.

6. **Destructive tool separation.**Las herramientas que mutan estado (Jira crear, Linear crear, Postgres escribir) viven en un segundo servidor MCP con un flujo de autor más estricto: los tokens deben tener un `approved:by:human`alcance elevado a través de la tarjeta Slack en un plazo de 15 minutos.

7. **Audit log.**JSONL sólo para añadir por inquilino: `{timestamp, user, tool, args_redacted, response_redacted, outcome}`- La información se redacta a través de Presidio antes de escribir.

8. **Load test.**100 clientes simultáneos en StreamableHTTP. Demostrar escala horizontal añadiendo una segunda réplica; mostrar el balanceador de carga redistribuyendo sin pegajidad de sesión.

9. **Conformance tests.**Ejecutar la suite oficial de conformidad MCP contra ambos servidores.

## Usalo

```
$ curl -H "Authorization: Bearer eyJhbGc..." \
       -X POST https://mcp.internal.example.com/ \
       -d '{"jsonrpc":"2.0","method":"tools/call",
            "params":{"name":"postgres.readonly","arguments":{"sql":"SELECT 1"}}}'
[registry]   capability validated: postgres.readonly v1.2
[policy]    scope postgres:query:readonly present; allowed
[audit]     logged: user=u42 tool=postgres.readonly outcome=ok
response:    { "result": { "rows": [[1]] } }
```

## Envío

`outputs/skill-mcp-server.md`Describe el producto entregado. Un servidor MCP de nivel de producción + registro + capa de auditoría para herramientas internas con escopo OAuth 2.1 y gateing OPA.

| Weight | Criterion | How it is measured |
|:-:|---|---|
| 25 | Spec conformance | StreamableHTTP + capability manifest passes MCP conformance tests |
| 20 | Security | Scope enforcement, OPA coverage across every tool, secret hygiene |
| 20 | Observability | Per-tool-call audit log with PII redaction |
| 20 | Scale | 100-client load test horizontal scale demonstration |
| 15 | Registry UX | Discover / validate / enable-disable workflow |
| **100** | | |

## Los ejercicios

1. Añadir una nueva herramienta (Confluence search). Enviar a través del flujo de validación del registro sin tocar el servidor central.

2. Escriba una política de OPA que redacte los resultados de la consulta Postgres que contienen columnas con nombres `email`¿ Qué ?`ssn`, o`phone`- Ejercicio con una consulta de sonda.

3. Indique el índice de latencia local de StreamableHTTP vs. stdio.

4. Implementar la cuota por inquilino: N llamadas por minuto por herramienta por inquilino.

5. Ejecutar la suite de conformidad MCP desde [mcp-conformance-tests](https://github.com/modelcontextprotocol/conformance)y arreglar cada falla.

## Términos clave

| Term | What people say | What it actually means |
|------|-----------------|------------------------|
| StreamableHTTP | "2026 MCP transport" | Stateless HTTP + streaming; replaces SSE + stdio for networked servers |
| Capability manifest | "Well-known doc" | `.well-known/mcp-capabilities` with tool list, auth, transport URL |
| OPA / Rego | "Policy engine" | Open Policy Agent for authorizing tool calls against external rules |
| Scope elevation | "Approved-by-human" | Short-lived scope granted via Slack approval, required for destructive tools |
| Registry | "Tool discovery" | Service that indexes MCP servers from their capability manifests |
| Workload identity | "SPIFFE / SPIRE" | Cryptographic service identity for OAuth token issuance |
| Conformance suite | "Spec tests" | Official MCP test battery for StreamableHTTP + tool manifest correctness |

## Leer más

- [Model Context Protocol 2026 Roadmap](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/) StreamableHTTP, metadatos de capacidad, registro
- [AAIF MCP Registry spec](https://github.com/modelcontextprotocol/registry) la especificación del registro de 2026
- [AWS ECS reference deployment](https://aws.amazon.com/blogs/containers/deploying-model-context-protocol-mcp-servers-on-amazon-ecs/) Desarrollo de la producción de referencia
- [Pinterest internal MCP ecosystem](https://www.infoq.com/news/2026/04/pinterest-mcp-ecosystem/) el despliegue interno de referencia
- [Block `goose` MCP usage](https://block.github.io/goose/) patrón de consumo de agentes de referencia
- [FastMCP](https://github.com/jlowin/fastmcp) Framework de servidores Python
- [Open Policy Agent](https://www.openpolicyagent.org/) Referencia de motor de política
- [SPIFFE / SPIRE](https://spiffe.io) Referencia de identidad de la carga de trabajo
