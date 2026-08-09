# 无同步任务 (SEP-1686)  现在打电话,为长期工作而提前提前

> 实际代理工作需要几分钟到几个小时: 同步工具调用,放弃连接,停机或阻止用户界面. 通过SEP-1686,在2025-11-25年合并,增加了一个任务原始:任何请求都可以增加成为任务,结果可以稍后获取或通过国家通知流媒体. 风险注意:任务在2026年1月进行实验; SDK表面仍在围绕规格设计.

**Type:** Build
**Languages:** Python (stdlib, async task state machine)
**Prerequisites:** Phase 13 · 07 (MCP server), Phase 13 · 09 (transports)
**Time:** ~75 minutes

## 学习目标

- 确定何时将工具从同步推广到增强任务 (>30秒服务器侧工作).
- 完成任务的生命周期: `working`其他`input_required`其他`completed`现在,`failed`现在,`cancelled`现在,我们要去.
- 保持任务状态,使毁不会失去飞行工作.
- 调查`tasks/status`带来一个`tasks/result`没有错.

## 问题

`generate_report`工具运行多分钟的提取管道.

1. 连接保持开放3分钟. 远程运输将它放下,客户端时间停下来,UI结.
2. 要求客户查询一个定制端点. 打破MCP统一性.
3. 放弃,没有结果.

任何请求 (通常是通过其他程序进行加大任务)`tools/call`服务器立即返回任务ID. 客户端进行了调查.`tasks/status`子和子`tasks/result`服务器侧状态存活了重启.

## 概念

### 任务增强

通过设置一个请求成为一个任务`params._meta.task.required: true`(或`optional: true`服务器立即回应:

```json
{
  "jsonrpc": "2.0", "id": 1,
  "result": {
    "_meta": {
      "task": {
        "id": "tsk_9f7b...",
        "state": "working",
        "ttl": 900000
      }
    }
  }
}
```

`ttl`是服务器承诺保留状态; ttl后任务结果被丢弃.

### 按工具选择

工具注释可以声明任务支持:

- `taskSupport: "forbidden"`这款工具始终同步运行.
- `taskSupport: "optional"`客户可以要求增加任务.
- `taskSupport: "required"`客户端必须使用任务增强.

`generate_report`工具是`required` `notes_search`工具是`forbidden`现在,我们要去.

### 国家

```
working  -> input_required -> working  (loop via elicitation)
working  -> completed
working  -> failed
working  -> cancelled
```

只有一个次`completed`现在`failed`其他`cancelled`任务是终极的.

### 方法

- `tasks/status {taskId}`返回当前状态和进展线索.
- `tasks/result {taskId}`如果尚未完成,则会阻止或返回404.
- `tasks/cancel {taskId}`无力;终端状态无视.
- `tasks/list`可选;列出了已完成和最近完成的任务.

### 流动状态变化

如果服务器支持,客户端可以订阅状态通知:

```
server -> notifications/tasks/updated {taskId, state, progress?}
```

投资者在投资时,会获得更好的体验.

### 耐用状态

规格要求声明任务支持的服务器保持状态.一个崩不应该在 ttl 内部丢失完成的结果.存储范围从SQLite到Redis到文件系统.教训13利用文件系统.

### 取消语义

`tasks/cancel`如果任务正在执行中,服务器会试图停止 (检查执行者合作取消).如果已经终端,请求是无运行.

### 事故恢复

当服务器进程重启时:

1. 输入所有持续任务状态.
2. 标记任何一个`working`工作过程已结束`failed`错误`CRASH_RECOVERY`现在,我们要去.
3. 保护`completed`现在,`failed`现在,`cancelled`为了他们的特利.

### 异步任务加样

任务本身可以召唤`sampling/createMessage`长期的研究任务是这样的:服务器的任务线程根据需要采样客户端的模型,而客户端的UI显示任务为`working`定期更新进展情况.

### 为什么这是一项实验

SEP-1686 在2025年1月25日发货,但更广泛的路线图提出了三个开放的问题:持久订阅原始,子任务 (父母-孩子任务关系) 和结果-TTL标准化.预计到2026年,规格将演变.生产代码应该只适用于普通情况下将任务视为稳定,并防止未来的SDK变化.

```figure
tp-task-lifecycle
```

## 用它

`code/main.py`实现一个持久的任务存储 (支持文件系统) 和一个`generate_report`客户端打电话给工具,立即获取任务识别,投票`tasks/status`工作人员更新进展,`tasks/result`取消工作; 机恢复通过打死工人线程和重新加载状态进行模拟.

什么要看:

- 任务状态 JSON 持续到`/tmp/lesson-13-tasks/<id>.json`现在,我们要去.
- 工作者线程更新`progress`调查显示,
- 客户取消会设定事件; 工人检查并提前离开.
- 机动系统的重载标志着飞行任务.`failed`随着`CRASH_RECOVERY`现在,我们要去.

## 运送它

这一课产生了`outputs/skill-task-store-designer.md`鉴于一个长期运行的工具 (研究,构建,出口),技能设计任务存储器 (状态形状, ttl,耐用性),选择正确的任务支持标志,并绘制进展通知.

## 运动

1. 跑步`code/main.py`开始一个`generate_report`调查结果,然后查询结果.

2. 添加一个`tasks/cancel`检查工人尊重它,国家成为`cancelled`现在,我们要去.

3. 模拟崩恢复:打死工作线,重新启动加载器,并观察 `CRASH_RECOVERY`失败模式.

4. 扩展存储到SQLite. 耐用性获取相同;查询选项打开 (从会议X列出所有任务).

5. 阅读2026年MCP路线图. 确定一个与任务相关的开放问题,最有可能影响SDK API设计在下一年.

## 关键词

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| Task | "Long-running tool call" | Request augmented with `_meta.task` for async execution |
| SEP-1686 | "Tasks spec" | Spec Evolution Proposal that added Tasks in 2025-11-25 |
| `_meta.task` | "Task envelope" | Per-request metadata containing id, state, ttl |
| taskSupport | "Tool flag" | `forbidden` / `optional` / `required` per tool |
| `tasks/status` | "Poll method" | Fetch current state and optional progress hint |
| `tasks/result` | "Fetch result" | Returns the completed payload or 404 if not yet done |
| `tasks/cancel` | "Stop it" | Idempotent cancellation request |
| ttl | "Retention budget" | Milliseconds the server promises to keep the task state |
| `notifications/tasks/updated` | "State push" | Server-initiated state-change event |
| Durable store | "Crash-safe state" | Filesystem / SQLite / Redis persistence layer |

## 进一步阅读

- [MCP — GitHub SEP-1686 issue](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1686)起始提案和全面讨论
- [WorkOS — MCP async tasks for AI agent workflows](https://workos.com/blog/mcp-async-tasks-ai-agent-workflows)设计经历,合理化
- [DeepWiki — MCP task system and async operations](https://deepwiki.com/modelcontextprotocol/modelcontextprotocol/2.7-task-system-and-async-operations)机械和机械
- [FastMCP — Tasks](https://gofastmcp.com/servers/tasks) SDK级任务执行模式
- [MCP blog — 2026 roadmap](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/)开放问题和2026年优先事项,包括子任务
