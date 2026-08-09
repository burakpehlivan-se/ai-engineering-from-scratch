# 根源和诱导 范围和飞行中用户输入

> 硬编码的路径在用户打开另一个项目时会破裂. 预填工具参数在用户未准确时会断裂. 根将服务器扩展到用户控制的URI集;调用工具中间停止调用,以便通过表格或URL请求用户进行结构化输入. 两个客户端原始,两个解决常见的MCP故障模式. 通过H1 2026 检查 SDK版本之前,SEP-1036 (URL模式启动,2025-11-25) 是实验性的.

**Type:** Build
**Languages:** Python (stdlib, roots + elicitation demo)
**Prerequisites:** Phase 13 · 07 (MCP server)
**Time:** ~45 minutes

## 学习目标

- 声明`roots`如何回应`notifications/roots/list_changed`现在,我们要去.
- 限制服务器文件操作在声明的根集合中的URI.
- 使用`elicitation/create`要求用户在工具调用中确认或结构化输入.
- 选择形式模式和URL模式的调用 (后者是实验性的;注明漂移风险).

## 问题

两次具体故障, MCP 服务器在生产中出现了故障.

**Broken path assumption.**服务器是写到的`~/notes`其他机器上的用户,`~/Documents/Notes`收到一个工具电话,它默默失败 (没有文件找到) 或更糟糕的是,写到错误的地方.

**Missing argument the user would know.**用户要求"删除旧的TPS报告说明".`notes_delete(title: "TPS report")`没有任何一个"模糊"的方法是令人烦的;在所有三个上运行是灾难性的.

根根固定第一:客户声明`initialize`发动器将第二个解决:服务器暂停工具调用并发送`elicitation/create`要求用户选择哪个.

## 概念

### 根源

客户端将根列表声明在`initialize`其他:

```json
{
  "capabilities": {"roots": {"listChanged": true}}
}
```

然后服务器可以打电话`roots/list`其他:

```json
{"roots": [{"uri": "file:///Users/alice/Documents/Notes", "name": "Notes"}]}
```

服务器必须把根作为边界:在根集合之外读取或写入任何文件都会被拒绝.这不是由客户端执行的 (服务器仍然是用户所信任的代码),但符合规范的服务器尊重它.

当用户添加或删除根时,客户端发送`notifications/roots/list_changed`服务器重新调用`roots/list`并且更新了它的边界.

### 为什么根源是客户端原始的

根由客户端声明,因为它们代表用户的同意模式.用户告诉Claude Desktop"给这个注释服务器访问这两个目录".服务器无法扩大这一范围.

### 发出:形式模式默认

`elicitation/create`采用形式方案加上自然语言提示:

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

客户端将表格传递,收集用户的答案,返回:

```json
{
  "action": "accept",
  "content": {"note_id": "note-14", "confirm": true}
}
```

可能采取的三项行动:`accept`(用户填写),`decline`(用户关闭了),`cancel`(用户终止了整个工具调用).

形式方案是平面的 嵌套物体在v1中不支持.SDK通常拒绝任何比单层更复杂的东西.

### 获取:URL模式 (SEP-1036,实验)

服务器将发送一个URL:

```json
{
  "method": "elicitation/create",
  "params": {
    "message": "Sign in to GitHub",
    "url": "https://github.com/login/oauth/authorize?client_id=..."
  }
}
```

客户端在浏览器中打开URL,等待完成,返回用户回来时. 有用于OAuth流,支付授权和文件签署,如果表格不够.

风险注意:SEP-1036响应形状仍然在定位;一些SDK返回回调用URL,其他返回完成代币.在使用URL模式之前阅读 SDK的发布说明.

### 当引发是正确的工具时

- 破坏性行动之前用户确认 (破坏性提示 +诱惑).
- 含义不一致 (选择N匹配中的一个).
- 首次运行设置 (API密钥,目录,偏好).
- 基于 OAuth 类型的流程 (URL 模式).

### 当发出错误时

- 填写模型可能在散文中要求的工具的必要参数. 使用正常的重复提示,而不是引发对话.
- 电话频率高. 发出电话会打断对话,不要在循环中开启.
- 验证,返回错误,让模型在文字中询问用户.

### 人在循环中的桥梁

调用和采样组合使MCP的"人在循环"模型成为可能.服务器的代理循环可以暂停用户输入 (调用) 或模型推理 (采样组合).13期11期涵盖采样组合;本课程涵盖调用.将它们组合在一起以实现完整的中循环控制.

```figure
t3-roots-boundary
```

## 用它

`code/main.py`扩展了备注服务器,使用:

- `roots/list`服务器在根列表变更通知后重新查询的响应.
- `notes_delete`使用的工具`elicitation/create`对于多个笔记的匹配,
- `notes_setup`使用URL模式引发开启首次运行配置页面的工具 (模拟).
- 边界检查,拒绝在声明的根以外的URI进行操作.

演示中包括三个场景:快乐道路 (一场比赛),解读 (三场比赛,引发火灾),出根写作 (拒绝).

## 运送它

这一课产生了`outputs/skill-elicitation-form-designer.md`鉴于可能需要用户确认或解读的工具,技能设计了发出表单的方案和消息模板.

## 运动

1. 跑步`code/main.py`启动解读路径;确认模拟用户答案将返回工具.

2. 添加一个新工具`notes_archive`检查UX:与模特在文本中重新请求相比?

3. 执行 URL 模式调整,以便在首次运行 OAuth 流动中实现. 注意漂移风险,并添加 SDK 版本保护器.

4. 延长时间`roots/list`处理:当通知到达时,服务器应自动重新阅读和重新扫描可能现在无法使用的开放文件处理器.

5. 在 GitHub 上阅读SEP-1036问题讨论线程. 确定一个影响服务器应如何处理URL模式回调的问题的开放问题.

## 关键词

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

## 进一步阅读

- [MCP — Client roots spec](https://modelcontextprotocol.io/specification/draft/client/roots)可信根引用
- [MCP — Client elicitation spec](https://modelcontextprotocol.io/specification/draft/client/elicitation)法典征求参考
- [Cisco — What's new in MCP elicitation, structured content, OAuth enhancements](https://blogs.cisco.com/developer/whats-new-in-mcp-elicitation-structured-content-and-oauth-enhancements) 2025-11-25 补充程序
- [MCP — GitHub SEP-1036](https://github.com/modelcontextprotocol/modelcontextprotocol) URL模式调试建议 (实验性,漂移风险)
- [The New Stack — How elicitation brings human-in-the-loop to AI tools](https://thenewstack.io/how-elicitation-in-mcp-brings-human-in-the-loop-to-ai-tools/) 经历经历
