# 多智能体可观测性系统

通过全面的钩子事件跟踪，为 Claude Code 智能体提供实时监控和可视化。你可以在[这里观看完整介绍](https://youtu.be/9ijnN985O_c)。

## 🎯 概述

该系统通过实时捕获、存储和可视化 Claude Code [钩子事件](https://docs.anthropic.com/en/docs/claude-code/hooks)，提供对 Claude Code 智能体行为的完整可观测性。支持会话跟踪、事件过滤和实时更新的多并发智能体监控。

<img src="images/app.png" alt="多智能体可观测性仪表板" style="max-width: 800px; width: 100%;">

## 🏗️ 架构

```
Claude 智能体 → 钩子脚本 → HTTP POST → Bun 服务器 → SQLite → WebSocket → Vue 客户端
```

![智能体数据流动画](images/AgentDataFlowV2.gif)

## 📋 安装要求

开始之前，请确保已安装以下软件：

- **[Claude Code](https://docs.anthropic.com/en/docs/claude-code)** - Anthropic 官方 Claude CLI
- **[Astral uv](https://docs.astral.sh/uv/)** - 快速 Python 包管理器（钩子脚本必需）
- **[Bun](https://bun.sh/)**、**npm** 或 **yarn** - 用于运行服务器和客户端
- **Anthropic API 密钥** - 设置为 `ANTHROPIC_API_KEY` 环境变量
- **OpenAI API 密钥**（可选）- 用于与 just-prompt MCP 工具的多模型支持
- **ElevenLabs API 密钥**（可选）- 用于音频功能

### 配置 .claude 目录

为了在您的仓库中设置可观测性，我们需要将 .claude 目录复制到您的项目根目录。

要将可观测性钩子集成到您的项目中：

1. **将整个 `.claude` 目录复制到您的项目根目录：**
   ```bash
   cp -R .claude /path/to/your/project/
   ```

2. **更新 `settings.json` 配置：**
   
   在您的项目中打开 `.claude/settings.json` 并修改 `source-app` 参数以标识您的项目：
   
   ```json
   {
     "hooks": {
       "PreToolUse": [{
         "matcher": "",
         "hooks": [
           {
             "type": "command",
             "command": "uv run .claude/hooks/pre_tool_use.py"
           },
           {
             "type": "command",
             "command": "uv run .claude/hooks/send_event.py --source-app YOUR_PROJECT_NAME --event-type PreToolUse --summarize"
           }
         ]
       }],
       "PostToolUse": [{
         "matcher": "",
         "hooks": [
           {
             "type": "command",
             "command": "uv run .claude/hooks/post_tool_use.py"
           },
           {
             "type": "command",
             "command": "uv run .claude/hooks/send_event.py --source-app YOUR_PROJECT_NAME --event-type PostToolUse --summarize"
           }
         ]
       }],
       "UserPromptSubmit": [{
         "hooks": [
           {
             "type": "command",
             "command": "uv run .claude/hooks/user_prompt_submit.py --log-only"
           },
           {
             "type": "command",
             "command": "uv run .claude/hooks/send_event.py --source-app YOUR_PROJECT_NAME --event-type UserPromptSubmit --summarize"
           }
         ]
       }]
       // ... (Notification、Stop、SubagentStop、PreCompact 的类似模式)
     }
   }
   ```
   
   将 `YOUR_PROJECT_NAME` 替换为您项目的唯一标识符（如 `my-api-server`、`react-app` 等）。

3. **确保可观测性服务器正在运行：**
   ```bash
   # 从可观测性项目目录（这个代码库）
   ./scripts/start-system.sh
   ```

现在您的项目将在 Claude Code 执行操作时向可观测性系统发送事件。

## 🚀 快速开始

您可以通过运行此仓库的 .claude 设置来快速查看其工作原理。

```bash
# 1. 同时启动服务器和客户端
./scripts/start-system.sh

# 2. 在浏览器中打开 http://localhost:5173

# 3. 打开 Claude Code 并运行以下命令：
运行 git ls-files 来理解代码库。

# 4. 观察事件在客户端中的流式传输

# 5. 将 .claude 文件夹复制到您想要发出事件的其他项目。
cp -R .claude <您想要发出事件的代码库目录>
```

## 📁 项目结构

```
claude-code-hooks-multi-agent-observability/
│
├── apps/                    # 应用程序组件
│   ├── server/             # Bun TypeScript 服务器
│   │   ├── src/
│   │   │   ├── index.ts    # 带有 HTTP/WebSocket 端点的主服务器
│   │   │   ├── db.ts       # SQLite 数据库管理和迁移
│   │   │   └── types.ts    # TypeScript 接口
│   │   ├── package.json
│   │   └── events.db       # SQLite 数据库（gitignored）
│   │
│   └── client/             # Vue 3 TypeScript 客户端
│       ├── src/
│       │   ├── App.vue     # 主应用，带主题和 WebSocket 管理
│       │   ├── components/
│       │   │   ├── EventTimeline.vue      # 带自动滚动的事件列表
│       │   │   ├── EventRow.vue           # 单个事件显示
│       │   │   ├── FilterPanel.vue        # 多选过滤器
│       │   │   ├── ChatTranscriptModal.vue # 聊天历史查看器
│       │   │   ├── StickScrollButton.vue  # 滚动控制
│       │   │   └── LivePulseChart.vue     # 实时活动图表
│       │   ├── composables/
│       │   │   ├── useWebSocket.ts        # WebSocket 连接逻辑
│       │   │   ├── useEventColors.ts      # 颜色分配系统
│       │   │   ├── useChartData.ts        # 图表数据聚合
│       │   │   └── useEventEmojis.ts      # 事件类型表情映射
│       │   ├── utils/
│       │   │   └── chartRenderer.ts       # Canvas 图表渲染
│       │   └── types.ts    # TypeScript 接口
│       ├── .env.sample     # 环境配置模板
│       └── package.json
│
├── .claude/                # Claude Code 集成
│   ├── hooks/             # 钩子脚本（Python with uv）
│   │   ├── send_event.py  # 通用事件发送器
│   │   ├── pre_tool_use.py    # 工具验证和阻止
│   │   ├── post_tool_use.py   # 结果记录
│   │   ├── notification.py    # 用户交互事件
│   │   ├── user_prompt_submit.py # 用户提示记录和验证
│   │   ├── stop.py           # 会话完成
│   │   └── subagent_stop.py  # 子智能体完成
│   │
│   └── settings.json      # 钩子配置
│
├── scripts/               # 实用脚本
│   ├── start-system.sh   # 启动服务器和客户端
│   ├── reset-system.sh   # 停止所有进程
│   └── test-system.sh    # 系统验证
│
└── logs/                 # 应用程序日志（gitignored）
```

## 🔧 组件详情

### 1. 钩子系统（`.claude/hooks/`）

> 如果您想掌握 claude code 钩子，请观看[此视频](https://github.com/disler/claude-code-hooks-mastery)

钩子系统拦截 Claude Code 生命周期事件：

- **`send_event.py`**：将事件数据发送到可观测性服务器的核心脚本
  - 支持 `--add-chat` 标志以包含对话历史
  - 发送前验证服务器连接
  - 通过适当的错误处理处理所有事件类型

- **特定事件钩子**：每个都实现验证和数据提取
  - `pre_tool_use.py`：阻止危险命令，验证工具使用
  - `post_tool_use.py`：捕获执行结果和输出
  - `notification.py`：跟踪用户交互点
  - `user_prompt_submit.py`：记录用户提示，支持验证（v1.0.54+）
  - `stop.py`：记录会话完成和可选的聊天历史
  - `subagent_stop.py`：监控子智能体任务完成

### 2. 服务器（`apps/server/`）

基于 Bun 的 TypeScript 服务器，具有实时功能：

- **数据库**：SQLite with WAL 模式，支持并发访问
- **端点**：
  - `POST /events` - 从智能体接收事件
  - `GET /events/recent` - 分页事件检索和过滤
  - `GET /events/filter-options` - 可用过滤器值
  - `WS /stream` - 实时事件广播
- **功能**：
  - 自动架构迁移
  - 事件验证
  - 向所有客户端广播 WebSocket
  - 聊天记录存储

### 3. 客户端（`apps/client/`）

Vue 3 应用程序，具有实时可视化：

- **视觉设计**：
  - 双色系统：应用颜色（左边框）+ 会话颜色（第二边框）
  - 梯度指示器用于视觉区分
  - 深色/浅色主题支持
  - 响应式布局和流畅动画

- **功能**：
  - 实时 WebSocket 更新
  - 多条件过滤（应用、会话、事件类型）
  - 带会话颜色条和事件类型指示器的实时脉冲图表
  - 时间范围选择（1分钟、3分钟、5分钟）和适当的数据聚合
  - 带语法高亮的聊天记录查看器
  - 带手动覆盖的自动滚动
  - 事件限制（通过 `VITE_MAX_EVENTS_TO_DISPLAY` 配置）

- **实时脉冲图表**：
  - 基于 Canvas 的实时可视化
  - 每个条形的会话特定颜色
  - 条形上显示的事件类型表情
  - 流畅动画和发光效果
  - 响应过滤器变化

## 🔄 数据流

1. **事件生成**：Claude Code 执行操作（工具使用、通知等）
2. **钩子激活**：基于 `settings.json` 配置运行相应的钩子脚本
3. **数据收集**：钩子脚本收集上下文（工具名称、输入、输出、会话 ID）
4. **传输**：`send_event.py` 通过 HTTP POST 向服务器发送 JSON 有效负载
5. **服务器处理**：
   - 验证事件结构
   - 存储在 SQLite 中并添加时间戳
   - 广播到 WebSocket 客户端
6. **客户端更新**：Vue 应用接收事件并实时更新时间线

## 🎨 事件类型和可视化

| 事件类型   | 表情 | 用途               | 颜色编码  | 特殊显示 |
| ------------ | ----- | --------------------- | ------------- | --------------- |
| PreToolUse   | 🔧     | 工具执行前 | 基于会话 | 工具名称和详情 |
| PostToolUse  | ✅     | 工具完成后 | 基于会话 | 工具名称和结果 |
| Notification | 🔔     | 用户交互     | 基于会话 | 通知消息 |
| Stop         | 🛑     | 响应完成   | 基于会话 | 摘要和聊天记录 |
| SubagentStop | 👥     | 子智能体完成     | 基于会话 | 子智能体详情 |
| PreCompact   | 📦     | 上下文压缩    | 基于会话 | 压缩详情 |
| UserPromptSubmit | 💬 | 用户提示提交 | 基于会话 | 提示：_"用户消息"_（斜体） |

### UserPromptSubmit 事件（v1.0.54+）

`UserPromptSubmit` 钩子在 Claude 处理之前捕获每个用户提示。在 UI 中：
- 显示为斜体文本 `提示："用户消息"`
- 内联显示实际提示内容（截断到 100 个字符）
- 启用 AI 摘要时，摘要显示在右侧
- 用于跟踪用户意图和对话流程

## 🔌 集成

### 对于新项目

1. 复制事件发送器：
   ```bash
   cp .claude/hooks/send_event.py YOUR_PROJECT/.claude/hooks/
   ```

2. 添加到您的 `.claude/settings.json`：
   ```json
   {
     "hooks": {
       "PreToolUse": [{
         "matcher": ".*",
         "hooks": [{
           "type": "command",
           "command": "uv run .claude/hooks/send_event.py --source-app YOUR_APP --event-type PreToolUse"
         }]
       }]
     }
   }
   ```

### 对于此项目

已集成！钩子同时运行验证和可观测性：
```json
{
  "type": "command",
  "command": "uv run .claude/hooks/pre_tool_use.py"
},
{
  "type": "command", 
  "command": "uv run .claude/hooks/send_event.py --source-app cc-hooks-observability --event-type PreToolUse"
}
```

## 🧪 测试

```bash
# 系统验证
./scripts/test-system.sh

# 手动事件测试
curl -X POST http://localhost:4000/events \
  -H "Content-Type: application/json" \
  -d '{
    "source_app": "test",
    "session_id": "test-123",
    "hook_event_type": "PreToolUse",
    "payload": {"tool_name": "Bash", "tool_input": {"command": "ls"}}
  }'
```

## ⚙️ 配置

### 环境变量

将 `.env.sample` 复制到项目根目录中的 `.env` 并填入您的 API 密钥：

**应用程序根目录**（`.env` 文件）：
- `ANTHROPIC_API_KEY` – Anthropic Claude API 密钥（必需）
- `ENGINEER_NAME` – 您的姓名（用于日志记录/标识）
- `GEMINI_API_KEY` – Google Gemini API 密钥（可选）
- `OPENAI_API_KEY` – OpenAI API 密钥（可选）
- `ELEVEN_API_KEY` – ElevenLabs API 密钥（可选）

**客户端**（`apps/client/.env` 中的 `.env` 文件）：
- `VITE_MAX_EVENTS_TO_DISPLAY=100` – 要显示的最大事件数（超出时删除最旧的）

### 服务器端口

- 服务器：`4000`（HTTP/WebSocket）
- 客户端：`5173`（Vite 开发服务器）

## 🛡️ 安全功能

- 阻止危险命令（`rm -rf` 等）
- 防止访问敏感文件（`.env`、私钥）
- 在执行前验证所有输入
- 核心功能无外部依赖

## 📊 技术栈

- **服务器**：Bun、TypeScript、SQLite
- **客户端**：Vue 3、TypeScript、Vite、Tailwind CSS
- **钩子**：Python 3.8+、Astral uv、TTS（ElevenLabs 或 OpenAI）、LLMs（Claude 或 OpenAI）
- **通信**：HTTP REST、WebSocket

## 🔧 故障排除

### 钩子脚本无法正常工作

如果您的钩子脚本没有正确执行，可能是由于 `.claude/settings.json` 中的相对路径问题。Claude Code 文档建议对命令脚本使用绝对路径。

**解决方案**：使用自定义 Claude Code 斜杠命令自动将所有相对路径转换为绝对路径：

```bash
# 在 Claude Code 中，只需运行：
/convert_paths_absolute
```

此命令将：
- 在您的钩子命令脚本中查找所有相对路径
- 基于您当前的工作目录将它们转换为绝对路径
- 创建原始 settings.json 的备份
- 显示具体进行了哪些更改

这确保您的钩子无论从哪里执行 Claude Code 都能正确工作。

## 掌握 AI 编码
> 为代理工程做准备

通过基础[AI 编码原则](https://agenticengineer.com/principled-ai-coding?y=cchookobvs)学习使用 AI 编码

关注 [IndyDevDan YouTube 频道](https://www.youtube.com/@indydevdan)获取更多 AI 编码技巧和窍门。