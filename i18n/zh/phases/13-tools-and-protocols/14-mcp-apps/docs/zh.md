# 通过MCP应用程序 互动UI资源 `ui://`

> 仅仅使用文字的工具输出限制了代理能显示的内容.MCP Apps (SEP-1724,官方于2026年1月26日) 允许工具返回在Cloed Desktop,ChatGPT,Cursor,Goose和VS代码中呈现的沙盒互动HTML.仪表板,表格,地图,3D场景,所有通过一个扩展.`ui://`资源计划,`text/html;profile=mcp-app`通过MIME,iframe-sandbox后消息协议,以及允许服务器染HTML的安全表面.

**Type:** Build
**Languages:** Python (stdlib, UI resource emitter), HTML (sample app)
**Prerequisites:** Phase 13 · 07 (MCP server), Phase 13 · 10 (resources)
**Time:** ~75 minutes

## 学习目标

- 返回一个`ui://`工具调用资源,并设置正确的MIME和元数据.
- 声明工具的相关UI`_meta.ui.resourceUri`现在`_meta.ui.csp`其他`_meta.ui.permissions`现在,我们要去.
- 实现iframe沙箱邮件JSON-RPC用于UI-to-host通信.
- 应用基于UI的攻击的CSP和权限政策默认设置.

## 问题

未来的2025年`visualize_timeline`工具可以返回"这里有14个按时间序列排列的笔记: ...". 这是一个段落.用户实际上想要互动时间表. 在MCP Apps之前,选项是:客户端特定的小工具API (Claude文物,OpenAI Custom GPT HTML),或者根本没有UI.

根据MCP应用程序 (SEP-1724,发货于2026年1月26日),该协议标准化.`resource`哪个 URI 是`ui://...`谁的MIME是`text/html;profile=mcp-app`服务器将其转载到一个带沙盒的iframe中,只有经过限制的CSP,并且没有网络访问,除非明确授权.

每个兼容的客户端 (Claude Desktop, ChatGPT, Goose, VS Code) 都会呈现相同的效果.`ui://`一个服务器,一个HTML包,一个通用UI.

## 概念

### 其他`ui://`资源计划

一个工具返回:

```json
{
  "content": [
    {"type": "text", "text": "Here is your notes timeline:"},
    {"type": "ui_resource", "uri": "ui://notes/timeline"}
  ],
  "_meta": {
    "ui": {
      "resourceUri": "ui://notes/timeline",
      "csp": {
        "defaultSrc": "'self'",
        "scriptSrc": "'self' 'unsafe-inline'",
        "connectSrc": "'self'"
      },
      "permissions": []
    }
  }
}
```

然后主机打电话`resources/read`在`ui://notes/timeline`染后,

```json
{
  "contents": [{
    "uri": "ui://notes/timeline",
    "mimeType": "text/html;profile=mcp-app",
    "text": "<!doctype html>..."
  }]
}
```

### 形砂箱

宿主将HTML转化为一个沙盒`<iframe>`含有:

- `sandbox="allow-scripts allow-same-origin"`(或每服务器声明更严格)
- 通过响应标题应用服务器声明的CSP.
- 没有饼干,没有来自主机的本地存储.
- 网络访问限于`connectSrc`在CSP.

### 邮件后协议

通过 iframe 与主机通信`window.postMessage`简单的JSON-RPC2.0方言:

总是着`targetOrigin`根据同龄人确切的来源,并通过收件证实`event.origin`任何有效载荷处理前,请不要使用`"*"`机体携带工具调用和资源阅读.

```js
// iframe to host  (pin to host origin)
window.parent.postMessage({
  jsonrpc: "2.0",
  id: 1,
  method: "host.callTool",
  params: { name: "notes_update", arguments: { id: "note-14", title: "..." } }
}, "https://host.example.com");

// host to iframe  (pin to iframe origin)
iframe.contentWindow.postMessage({
  jsonrpc: "2.0",
  id: 1,
  result: { content: [...] }
}, "https://iframe.example.com");

// receiver on both sides
window.addEventListener("message", (event) => {
  if (event.origin !== "https://expected-peer.example.com") return;
  // safe to process event.data
});
```

接口用户界面可以调用可用的主机侧方法:

- `host.callTool(name, arguments)`调用服务器工具.
- `host.readResource(uri)`读取MCP资源.
- `host.getPrompt(name, arguments)` 获取一个提示模板.
- `host.close()` 驳回了UI.

每次通话都通过MCP协议,并继承服务器的权限.

### 许可证

其他`_meta.ui.permissions`列表要求额外的功能:

- `camera`访问用户的相机 (用于扫描文件的UI).
- `microphone`语音输入.
- `geolocation`位置
- `network:*`比 更多的网络访问`connectSrc`只有一个人能做到.

每个许可都是用户在UI呈现之前看到的提示.

### 安全风险

在iframe中的HTML仍然是HTML. 新的攻击表面:

- **Prompt-injection via UI.**恶意服务器UI可以显示像系统消息的文本,并欺骗用户.主机染应该显著区分服务器UI与主机UI.
- **Exfiltration via `connectSrc`.**如果CSP允许`connect-src: *`默认应该是严格的.
- **Clickjacking.**接口面对面覆盖主机的色.主机必须防止z指数操纵并执行模糊性规则.
- **Steal focus.**接待者必须拦截.

阶段13·15将这些内容作为MCP安全的一部分详细介绍,本课程将介绍它们.

### `ui/initialize`握手

电脑系统的运输后,它发送了`ui/initialize`通过邮件:

```json
{"jsonrpc": "2.0", "id": 0, "method": "ui/initialize",
 "params": {"theme": "dark", "locale": "en-US", "sessionId": "..."}}
```

接待者使用功能和会议代币来响应.

### 应用程序 / AppFrame SDK原始

扩展应用程序SDK揭示了两个便利性原始:

- `AppRenderer`包裹一个 React / Vue / Solid 组件,并发出一个`ui://`资源具有正确的MIME和元数据.
- `AppFrame`接收资源,安装iframe,并调解邮件.

您可以使用这些或手动滚动HTML和JSON-RPC.

### 生态系统状况

2026年4月至2020年4月,MCP应用程序发行于2026年1月26日.

- **Claude Desktop.**自2026年1月起全面支持.
- **ChatGPT.**通过应用程序SDK (相同的MCP应用程序协议) 提供完整支持.
- **Cursor.**通过设置启用.
- **VS Code.**内部人员只能建造.
- **Goose.**完全支持.
- **Zed, Windsurf.**路线图.

服务器在生产中:仪表板,地图可视化,数据表,图表构建器,沙盒IDE预览.

```figure
t3-ui-sandbox
```

## 用它

`code/main.py`扩展了笔记服务器`visualize_timeline`返回一个工具`ui://notes/timeline`资源,加上一个处理器`resources/read`在那个URI中返回一个小但完整的HTML捆绑,并带有SVG时间线.HTML是stdlib模板的.

什么要看:

- `_meta.ui`工具响应载有资源Uri,CSP,权限.
- 无需网络访问,所有数据都被插入.
- 杰斯打电话`host.callTool`通过`window.parent.postMessage`(但在本DDLB演示中没有记录).

## 运送它

这一课产生了`outputs/skill-mcp-apps-spec.md`由于使用互动UI可以获得益处的工具,这项技能产生了MCP Apps的全部合同: `ui://`通过"URI",CSP,权限,邮件输入点,以及安全检查清单.

## 运动

1. 跑步`code/main.py`直接在浏览器中打开HTML,验证SVG染.然后绘制用户界面将使用的邮件后合同`host.callTool("notes_update", ...)`现在,我们要去.

2. 紧紧部: 移除`'unsafe-inline'`基于非基于脚本的政策.HTML生成代码的变化是什么?

3. 添加第二个UI资源`ui://notes/editor`通过 iframe 进行编辑,`host.callTool("notes_update", ...)`现在,我们要去.

4. 检查用户界面的攻击表面. 恶意服务器可以在哪里注入内容?

5. 阅读SEP-1724规格并确定MCP Apps SDK中没有使用的功能. (提示:组件级状态同步)

## 关键词

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| MCP Apps | "Interactive UI resources" | SEP-1724 extension shipped 2026-01-26 |
| `ui://` | "App URI scheme" | Resource scheme for UI bundles |
| `text/html;profile=mcp-app` | "The MIME" | Content-type for MCP App HTML |
| Iframe sandbox | "Render container" | Browser sandboxing of the UI with CSP and permissions |
| postMessage JSON-RPC | "UI-to-host wire" | Tiny JSON-RPC-over-postMessage dialect for host calls |
| `_meta.ui` | "Tool-UI binding" | Metadata linking a tool result to a UI resource |
| CSP | "Content-Security-Policy" | Declares allowed sources for scripts, network, styles |
| AppRenderer | "Server SDK primitive" | Converts a framework component into a `ui://` resource |
| AppFrame | "Client SDK primitive" | Iframe mount helper that mediates postMessage |
| `ui/initialize` | "Handshake" | First postMessage from UI to host |

## 进一步阅读

- [MCP ext-apps — GitHub](https://github.com/modelcontextprotocol/ext-apps)参考实施和SDK
- [MCP Apps specification 2026-01-26](https://github.com/modelcontextprotocol/ext-apps/blob/main/specification/2026-01-26/apps.mdx)正式的规范文件
- [MCP — Apps extension overview](https://modelcontextprotocol.io/extensions/apps/overview)高层文件
- [MCP blog — MCP Apps launch](https://blog.modelcontextprotocol.io/posts/2026-01-26-mcp-apps/)2026年1月发射时间
- [MCP Apps API reference](https://apps.extensions.modelcontextprotocol.io/api/) JSDoc 类型的 SDK 参考
