# 技术和代理SDK 人类技能,AGENTS.md,OpenAI应用SDK

> 技能说"如何完成任务". 2026年堆层都包含了两层. 据了解,在此之前,该公司的代理技能 (开放标准,2025年12月) 已被将作为 SKILL.md 运送到该公司. 开放AI的应用程序SDK是MCP加上小工具元数据. 作为项目级代理背景,Agents.md (现在有60,000多个备忘录) 位于备忘录根. 这一课标明了每个课程的内容,并构建了一个最小的SKILL.md + AGENTS.md包,

**Type:** Learn
**Languages:** Python (stdlib, SKILL.md parser and loader)
**Prerequisites:** Phase 13 · 07 (MCP server)
**Time:** ~45 minutes

## 学习目标

- 区分三个层次:AGENTS.md (项目背景),SKILL.md (可重复使用的技术) 和MCP (工具).
- 写一个SKILL.md,用YAML前线和逐步披露.
- 运载技能文件系统到代理运行时间.
- 编写一个技能,使用MCP服务器和AGENTS.md,以便一个包在Cloed Code,Cursor和Codex中运行.

## 问题

一位工程师将发布笔记写作工作流程分成多步骤提示:"阅读最新的合并 PR.按区域组.总结每个.按照团队的风格写一个变更日志.将其发布到 Slack草案. "他们把它放在他们的团队的Notion文档中.

现在他们想使用从克劳德代码,库尔索和Codex CLI的工作流程.每个代理都有不同的方式来加载指令:克劳德代码切片命令,库尔索规则,Codex `.codex.md`工程师将工作流程复制三次,并保留三份复制.

代理和技能共同解决问题:

- **AGENTS.md**任何兼容的代理都会在会议开始时读到它. "这个项目是如何运作的?
- **SKILL.md**具有可移植的包装:YAML前面材料 (名称,描述) +标记体 +可选资源.支持技能的代理人在要求上按名称加载它们.
- **MCP**技术需要使用的工具.

只有一个可携带的文物.

## 概念

### 代理商.md (agents.md)

于2025年底推出,到2026年4月被6万多个备忘录所采用.

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

经纪人在会议开始时阅读这篇文章,并使用它来校准他们的项目行为. 2026 年的每个编码代理都支持 AGENTS.md:Claude Code,Cursor,Codex,Copilot Workspace,opencode,Windsurf,Zed.

### 技术.md格式

果公司的代理技能 (于2025年12月发布为开放标准):

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

机体是模型在技能负载时所显示的提示.

### 逐步披露

技能可以引用代理只需要获得的子资源.

```
skills/
  release-notes-writer/
    SKILL.md
    style-guide.md
    template.md
    scripts/
      generate.sh
```

经纪人只会拉动style-guide.md当技能正在积极运行时. 这避免把提示器充满模型可能不需要的细节.

### 文件系统发现

经理运行时间扫描已知目录,查找SKILL.md文件:

- `~/.anthropic/skills/*/SKILL.md`
- 项目`./skills/*/SKILL.md`
- `~/.claude/skills/*/SKILL.md`

按文件名称和前列列进行加载`name`克劳德代码,人类克劳德代理SDK和SkillKit都遵循这个模式.

### 人类克劳德代理 SDK

`@anthropic-ai/claude-agent-sdk`,我知道.`claude-agent-sdk`运行时间内,将它们作为可调用的"代理"暴露在执行时间内.

### 开放AI应用程序 SDK

发布于2025年10月;直接基于MCP. 统一了OpenAI之前的连接器和自定义GPT操作在一个开发者表面下.

- 服务器 (工具,资源,提示)
- 另外,我们还可以使用ChatGPT的用户界面.
- 另外还有一个可选的MCP应用程序`ui://`互动表面的资源.

同样的协议,更丰富的实验.

### 通过SkillKit进行跨代理可移植性

像SkillKit这样的工具和类似的跨代理分销层将单个SKILL.md转化为32多个AI代理 (Claude Code,Cursor,Codex,Gemini CLI,OpenCode等) 的原生格式.

### 子的三层

| Layer | File | Loaded when | Purpose |
|-------|------|-------------|---------|
| AGENTS.md | repo root | session start | project-level conventions |
| SKILL.md | skills directory | skill invoked | reusable workflow |
| MCP server | external process | tools needed | callable actions |

所有三种组成:在会议开始时,代理阅读AGENTS.md,用户调用技能,技能的指示包括MCP工具调用,代理通过MCP客户端发送.

```figure
t3-skill-layers
```

## 用它

`code/main.py`通过SDLIBSKILL.md分析器和加载器,它可以发现`./skills/`通过分析YAML前列和标记体,并生成一个按技能名称键键的字符.`release-notes-writer`通过名字.

什么要看:

- 通过最小的stdlib解析器解析YAML前材料 (没有`pyyaml`其他类型
- 技能体是文字存储的; 代理在调用时将其预备到系统提示.
- 通过一个 `read_subresource`需要的引用文件.

## 运送它

这一课产生了`outputs/skill-agent-bundle.md`鉴于工作流程,技能产生了结合的SKILL.md + AGENTS.md + MCP-server-blueprint包,可通过代理进行移植.

## 运动

1. 跑步`code/main.py`加入第二个技能`skills/`确认载荷器接收了它.

2. 写一个AGENTS.md,包括测试命令,风格公约和第13阶段的心理模型.

3. 通过你的团队内部文件将多步骤的工作流转载到Skill.md.

4. 通过手动将技能转化为Cursor和Codex的本土规则格式. 计算格式之间的差异.

5. 阅读人类代理技能博客文章. 确定克劳德代理SDK中一个特征,这个课程的载体不涵盖. (提示:代理子调用).

## 关键词

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

## 进一步阅读

- [Anthropic — Agent Skills announcement](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) 2025年12月发射
- [Anthropic — Agent Skills docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) SKILL.md格式参考
- [OpenAI — Apps SDK](https://developers.openai.com/apps-sdk)基于MCP的ChatGPT开发平台
- [agents.md](https://agents.md/) AGENTS.md格式和采用列表
- [Anthropic — anthropics/skills GitHub](https://github.com/anthropics/skills)官方技能示例
