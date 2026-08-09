# Capstone  Construir un ecosistema completo de herramientas

> La fase 13 enseñó cada pieza. Esta piedra angular las conecta en un sistema en forma de producción: un servidor MCP con herramientas + recursos + instrucciones + tareas + UI, OAuth 2.1 en el borde, una puerta de entrada RBAC, un cliente multi-servidor, una llamada de subagente A2A, rastreo de OTel en un colector, detección de intoxicación de herramientas en CI y un paquete AGENTS.md + SKILL.md. Al final puedes defender todas las opciones arquitectónicas.

**Type:** Build
**Languages:** Python (stdlib, end-to-end ecosystem harness)
**Prerequisites:** Phase 13 · 01 through 21
**Time:** ~120 minutes

## Objetivos de aprendizaje

- Componer un servidor MCP que exponga herramientas, recursos, instrucciones y una tarea con un `ui://`la aplicación.
- Frente al servidor con una puerta de entrada OAuth 2.1 que impone RBAC y hashes fijados.
- Escriba un cliente multi-servidor que rastrea con OTel GenAI atributos de extremo a extremo.
- Delegar parte de una carga de trabajo a un subagente A2A; comprobar que se conserva la opacidad.
- Envasar toda la pila con Agents.md + Skill.md para que otros agentes puedan conducirla.

## El problema

Enviar el sistema de "investigación e información":

- El usuario pregunta: "resumen los tres documentos más citados de 2026 de arXiv sobre protocolos de agentes".
- Sistema: búsqueda de arXiv a través de MCP; delegación de resumen de papel a un agente de escritores especializado a través de A2A; resultados agregados; rendir un informe interactivo como una aplicación MCP `ui://`Recursos; registro de cada paso a OTel.

Todos los primitivos de la Fase 13 aparecen. Este no es un juguete  sistemas de asistencia a la investigación de producción enviados en 2026 por Anthropic (el producto de Claude Research), OpenAI (GPTs con Apps SDK), y terceros tienen esta forma exacta.

## El concepto

### Arquitectura

```
[user] -> [client] -> [gateway (OAuth 2.1 + RBAC)] -> [research MCP server]
                                                      |
                                                      +- MCP tool: arxiv_search (pure)
                                                      +- MCP resource: notes://recent
                                                      +- MCP prompt: /research_topic
                                                      +- MCP task: generate_report (long)
                                                      +- MCP Apps UI: ui://report/current
                                                      +- A2A call: writer-agent (tasks/send)
                                                      |
                                                      +- OTel GenAI spans
```

### Jerarquía de rastro

```
agent.invoke_agent
 ├── llm.chat (kick off)
 ├── mcp.call -> tools/call arxiv_search
 ├── mcp.call -> resources/read notes://recent
 ├── mcp.call -> prompts/get research_topic
 ├── a2a.tasks/send -> writer-agent
 │    └── task transitions (opaque internals)
 ├── mcp.call -> tools/call generate_report (task-augmented)
 │    └── tasks/status polling
 │    └── tasks/result (completed, returns ui:// resource)
 └── llm.chat (final synthesis)
```

Un rastro de identificación.`gen_ai.*`Los atributos.

### Posición de seguridad

- OAuth 2.1 + PKCE con indicador de recursos fijando la audiencia en la puerta de entrada.
- Gateway tiene credenciales de aguas arriba; el usuario nunca las ve.
- RBAC: `alice`¿ Qué ?`research:read`¿ Qué ?`research:write`, puede llamar a todas las herramientas.`bob`¿ Qué ?`research:read`, no puede llamar .`generate_report`¿ Qué ?
- Manifiesto de descripción pinada: se dejó caer cualquier servidor cuyos hashes de herramienta cambiaron.
- Regla de la segunda auditoría: ninguna herramienta combina entradas no fiables, datos sensibles y acciones consecuentes.

### Rendering

La final .`generate_report`tarea devuelve bloques de contenido más un `ui://report/current`El host del cliente (Claude Desktop, etc.) hace que el panel interactivo en un iframe sandbox. El panel contiene una lista de papel ordenada, recuentos de citas y un botón que llama `host.callTool('summarize_paper', {arxiv_id})`para cualquier papel que el usuario haga clic.

### Envases

Todo se traduce en:

```
research-system/
  AGENTS.md                     # project conventions
  skills/
    run-research/
      SKILL.md                  # the top-level workflow
  servers/
    research-mcp/               # the MCP server
      pyproject.toml
      src/
  agents/
    writer/                     # the A2A agent
  gateway/
    config.yaml                 # RBAC + pinned manifest
```

Los usuarios se desplegan con `docker compose up`. Claude Code, Cursor, Codex y los usuarios de código abierto pueden manejar el sistema mediante la invocación de la`run-research`La habilidad.

### Lo que cada lección de la Fase 13 contribuyó

| Lesson | What the capstone uses |
|--------|------------------------|
| 01-05 | Tool interface, provider-portability, parallel calls, schemas, linting |
| 06-10 | MCP primitives, server, client, transports, resources + prompts |
| 11-14 | Sampling, roots + elicitation, async tasks, `ui://` apps |
| 15-17 | Tool poisoning, OAuth 2.1, gateway + registry |
| 18 | A2A sub-agent delegation |
| 19 | OTel GenAI tracing |
| 20 | Routing gateway for the LLM layer |
| 21 | SKILL.md + AGENTS.md packaging |

```figure
t3-capstone-chain
```

## Usalo

`code/main.py`Se ejecuta el flujo completo para el escenario de investigación e informe: apretón de manos con gateway, OAuth 2.1 simulado, herramientas/lista fusionadas, generar_reporte como tarea, llamada A2A al escritor, ui:// recurso devuelto, OTel se emite.

Qué ver:

- Un rastro de identificación a través de cada salto.
- La política de la puerta de entrada bloquea a un segundo usuario de escribir.
- El ciclo de vida de la tarea se vuelve a trabajar → completado y devuelve tanto el texto como el contenido ui://.
- El estado interno de la llamada A2A es opaco para el orquestrador.
- Agentes.md y SKILL.md son los únicos archivos que otro agente necesita para reproducir el flujo de trabajo.

## Envío

Esta lección produce`outputs/skill-ecosystem-blueprint.md`. Dado una necesidad de producto (investigación, resumen, automatización), la habilidad produce la arquitectura completa: qué primitivas MCP, qué control de puerta de enlace, qué A2A llama, qué telemetría, qué envasado.

## Los ejercicios

1. - ¿ Qué ?`code/main.py`Tenga en cuenta la identificación de la pista y la forma en que se anida. Cuenta cuántos primitivos de la Fase 13 toca la demostración.

2. Extensión de la demostración: añadir un segundo servidor de MCP backend (por ejemplo `bibliography`) y confirmar que la puerta de enlace fusiona sus herramientas en el mismo espacio de nombres.

3. Sustituye el agente de escritores A2A falso con uno real que se ejecuta en un subproceso.

4. Añadir un paso de redacción de PII en la puerta de enrutamiento entre el orquestrador y el LLM. Los correos electrónicos de confirmación en la consulta del usuario se borran.

5. Escriba un AGENTS.md para un compañero de equipo que mantenga este sistema.

## Términos clave

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| Capstone | "Phase-13 integration demo" | End-to-end system using every primitive |
| Research and report | "The scenario" | Search, summarize, render pattern |
| Ecosystem | "All the pieces together" | Server + client + gateway + sub-agent + telemetry + package |
| Trace hierarchy | "Single trace id" | Every hop's span shares the trace; parent-child via span ids |
| Gateway-issued token | "Transitive auth" | Client sees only gateway's token; gateway holds upstream creds |
| Merged namespace | "All tools in one flat list" | Multi-server merge at the gateway, prefix-on-collision |
| Opacity boundary | "A2A call hides internals" | Sub-agent's reasoning invisible to orchestrator |
| Three-layer stack | "AGENTS.md + SKILL.md + MCP" | Project context + workflow + tools |
| Defense-in-depth | "Multiple security layers" | Pinned hashes, OAuth, RBAC, Rule of Two, audit log |
| Spec compliance matrix | "What we ship that the spec requires" | Checklist mapping deliverables to 2025-11-25 requirements |

## Leer más

- [MCP — Specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25) Referencia consolidada
- [MCP blog — 2026 roadmap](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/) donde se dirige el protocolo
- [a2a-protocol.org](https://a2a-protocol.org/latest/) Referencia A2A v1.0
- [OpenTelemetry — GenAI semconv](https://opentelemetry.io/docs/specs/semconv/gen-ai/) Convenciones canónicas de rastreo
- [Anthropic — Claude Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview) patrones de tiempo de ejecución de los agentes de producción
