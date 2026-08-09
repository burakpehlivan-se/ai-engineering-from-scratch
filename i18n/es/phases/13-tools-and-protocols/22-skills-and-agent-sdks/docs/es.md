# Habilidades y SDKs de agentes  Habilidades antropológicas, AGENTS.md, OpenAI Apps SDK

> MCP dice "qué herramientas existen". Habilidades dicen "cómo hacer una tarea". La pila de 2026 está en ambas capas. Las habilidades de agentes de Anthropic (estándar abierto, diciembre 2025) se envían como SKILL.md con divulgación progresiva. El SDK de aplicaciones de OpenAI es MCP más metadatos de widget. AGENTS.md (ahora en más de 60,000 repos) se encuentra en la raíz de los repos como contexto de agente a nivel de proyecto. Esta lección nombra lo que cubre cada uno y construye un paquete mínimo de SKILL.md + AGENTS.md que viaja entre agentes.

**Type:** Learn
**Languages:** Python (stdlib, SKILL.md parser and loader)
**Prerequisites:** Phase 13 · 07 (MCP server)
**Time:** ~45 minutes

## Objetivos de aprendizaje

- Se distinguen las tres capas: AGENTS.md (contexto del proyecto), SKILL.md (conocimiento reutilizable) y MCP (herramientas).
- Escriba un SKILL.md con la materia frontal de YAML y la divulgación progresiva.
- Cargar habilidades de archivos de estilo de un agente en tiempo de ejecución.
- Componer una habilidad con un servidor MCP y un AGENTS.md para que un paquete funcione en Claude Code, Cursor y Codex.

## El problema

Un ingeniero destila un flujo de trabajo de publicación de notas en un pedido de varios pasos: "Lea las últimas relaciones públicas fusionadas. Grupo por área. Resume cada una. Escriba una entrada de cambio siguiendo el estilo del equipo. Publica en Slack draft". Lo ponen en un documento de Noción para su equipo.

Ahora quieren usar este flujo de trabajo de Claude Code, Cursor y Codex CLI. Cada agente tiene una forma diferente de cargar instrucciones: Claude Code slash-commandos, reglas de Cursor, Codex `.codex.md`El ingeniero copia el flujo de trabajo tres veces y mantiene tres copias.

Agentes.md y Skill.md juntos arreglan esto:

- **AGENTS.md**Cada agente compatible lo lee al inicio de la sesión. "¿Cómo funciona este proyecto? ¿Cuáles son las convenciones? ¿Qué comandos ejecutan pruebas?"
- **SKILL.md**El programa de trabajo de la empresa es un paquete portátil: YAML frontmatter (nombre, descripción) + cuerpo de marcaje + recursos opcionales.
- **MCP**(Fase 13 · 06-14) maneja las herramientas que la habilidad necesita invocar.

Tres capas, un artefacto portátil.

## El concepto

### Agentes.md (agentes.md)

Lanzado a finales de 2025, adoptado por más de 60,000 repos en abril de 2026. Un archivo en repo root.

```markdown
# Project: my-service

## Conventions
- TypeScript with strict mode.
- Use Pydantic for models on the Python side.
- Tests run with `pnpm test`.

## Build and run
- `pnpm dev` for local dev server.
- `pnpm build` for production bundle.
```

Los agentes leen esto al inicio de la sesión y lo usan para calibrar su comportamiento para ese proyecto.

### Formación SKILL.md

Habilidades de agentes de Anthropic (difundido como estándar abierto en diciembre de 2025):

```markdown
---
name: release-notes-writer
description: Write a changelog entry for the latest merged PRs following this project's style.
---

# Release notes writer

When invoked, run these steps:

1. List PRs merged since the last tag. Use `gh pr list --base main --state merged`.
2. Group by label: feature, fix, chore, docs.
3. For each PR in each group, write one line: `- <title> (#<num>)`.
4. Draft the release notes and stage them in CHANGELOG.md.

If the user says "ship", run `git tag vX.Y.Z` and `gh release create`.

## Notes

- Never include commits without a PR.
- Skip "chore" entries from the public changelog.
```

La materia frontal declara la identidad de la habilidad. El cuerpo es el aviso que se muestra al modelo cuando la habilidad se carga.

### Divulgación progresiva

Las habilidades pueden referirse a sub-recursos que el agente sólo recoge cuando sea necesario. Ejemplo:

```
skills/
  release-notes-writer/
    SKILL.md
    style-guide.md
    template.md
    scripts/
      generate.sh
```

SKILL.md dice "ver style-guide.md para las reglas de estilo". El agente tira style-guide.md sólo cuando la habilidad está funcionando activamente. Esto evita hinchar el prompt con detalles que el modelo no puede necesitar.

### Descubrimiento del sistema de archivos

Los tiempos de ejecución del agente escanean directorios conocidos para archivos SKILL.md:

- `~/.anthropic/skills/*/SKILL.md`
- Proyecto `./skills/*/SKILL.md`
- `~/.claude/skills/*/SKILL.md`

Cargar es por nombre de carpeta y material frontal `name`Claude Code, el SDK del agente antropico Claude y SkillKit siguen este patrón.

### SDK de Agente Claude

`@anthropic-ai/claude-agent-sdk`(TypeScript) y `claude-agent-sdk`(Python) carga habilidades al inicio de la sesión, exponerlos como llamados "agentes" dentro del tiempo de ejecución.

### SDK de aplicaciones de OpenAI

Lanzado en octubre de 2025, construido directamente en MCP. Unifica los conectores anteriores de OpenAI y las acciones GPT personalizadas bajo una sola superficie de desarrollador.

- Un servidor MCP (herramientas, recursos, instrucciones).
- Además de metadatos de widget para la interfaz de usuario de ChatGPT.
- Además de una opción de aplicaciones MCP `ui://`recurso para superficies interactivas.

El mismo protocolo, una experiencia más rica.

### Portabilidad entre agentes a través de SkillKit

Herramientas como SkillKit y capas similares de distribución entre agentes traducen un solo SKILL.md al formato nativo de cada uno de los 32+ agentes de IA (Claude Code, Cursor, Codex, Gemini CLI, OpenCode, etc.). Una fuente de verdad; muchos consumidores.

### La pila de tres capas

| Layer | File | Loaded when | Purpose |
|-------|------|-------------|---------|
| AGENTS.md | repo root | session start | project-level conventions |
| SKILL.md | skills directory | skill invoked | reusable workflow |
| MCP server | external process | tools needed | callable actions |

Los tres componen: el agente lee AGENTS.md al inicio de la sesión, el usuario invoca una habilidad, las instrucciones de la habilidad incluyen llamadas a herramientas MCP, el agente envía a través de un cliente MCP.

```figure
t3-skill-layers
```

## Usalo

`code/main.py`El programa de trabajo de la empresa de investigación y desarrollo de la tecnología de la información (Study Science) ofrece una serie de capacidades para la investigación y el desarrollo de la tecnología de la información.`./skills/`, analiza la materia frontal de YAML más el cuerpo de marcación, y produce un dictado con teclado de nombre de habilidad.`release-notes-writer`por nombre.

Qué ver:

- El material frontal de YAML analizado con un analizador de menor tamaño (no `pyyaml`la dependencia).
- El cuerpo de habilidades almacenado literalmente; el agente lo prepende al sistema en la llamada.
- La divulgación progresiva demostrada a través de un `read_subresource`función que extrae archivos referenciados a pedido.

## Envío

Esta lección produce`outputs/skill-agent-bundle.md`. Dado un flujo de trabajo, la habilidad produce el paquete combinado SKILL.md + AGENTS.md + MCP-servidor-printa-plan, portátil entre agentes.

## Los ejercicios

1. - ¿ Qué ?`code/main.py`Añadir una segunda habilidad en el sub`skills/`y confirmar que el cargador lo recoge.

2. Escriba un AGENTS.md para este curso repo. Incluye comandos de prueba, convenciones de estilo y el modelo mental de la Fase 13.

3. Portar un flujo de trabajo de varios pasos desde los documentos internos de su equipo a un SKILL.md. Verificar que se carga en código Claude.

4. Traducir la habilidad en los formatos nativos de reglas de Cursor y Codex a mano. Cuente la diferencia entre los formatos  esta es la superficie de traducción de SkillKit automáticas.

5. Lea la publicación de blog de las habilidades de agente antropico. Identifique una característica en el SDK de agente Claude que el cargador de esta lección no cubre.

## Términos clave

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| SKILL.md | "The skill file" | YAML frontmatter plus markdown body, loaded by agent runtime |
| AGENTS.md | "Repo-root agent context" | Project-level conventions file read on session start |
| Progressive disclosure | "Lazy-load sub-resources" | Skill body references files pulled only when needed |
| Frontmatter | "YAML block at top" | Metadata (name, description) in `---` delimiters |
| Claude Agent SDK | "Anthropic's skill runtime" | `@anthropic-ai/claude-agent-sdk`, loads skills and routes |
| OpenAI Apps SDK | "MCP + widget meta" | OpenAI's dev surface built on MCP plus ChatGPT UI hooks |
| Skill discovery | "Filesystem scan" | Walk known dirs for SKILL.md, key by name |
| Cross-agent portability | "One skill many agents" | Translate one SKILL.md to 32+ agents via SkillKit-style tools |
| Agent Skill | "Portable know-how" | Reusable task template outside MCP's tool concept |
| Apps SDK | "MCP plus ChatGPT UI" | Connectors and Custom GPTs unified on MCP |

## Leer más

- [Anthropic — Agent Skills announcement](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) Lanzamiento en diciembre de 2025
- [Anthropic — Agent Skills docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) Referencia al formato SKILL.md
- [OpenAI — Apps SDK](https://developers.openai.com/apps-sdk) Plataforma de desarrollo basada en MCP para ChatGPT
- [agents.md](https://agents.md/) formato AGENTS.md y lista de adopción
- [Anthropic — anthropics/skills GitHub](https://github.com/anthropics/skills) ejemplos de habilidades oficiales
