# 智能家居 AI Agent 查询系统 🏠🤖

## 一、项目简介 📚

本项目旨在创建一个智能家居管理与分析系统，包含21个功能选项。查询的核心为一个具备 **思考**、**行动** 和 **记忆** 能力的 AI 代理（AI Agent），可接入deepseekR1/V3和qwen3大语言模型。该系统基于 FastAPI 框架与 PostgreSQL 数据库，通过命令行客户端 `client_cli.py` 提供服务。用户可以使用自然语言与 AI agent进行多轮对话，实现复杂的数据库查询、数据分析与可视化任务（功能选项19自然语言查询、20智能分析与可视化）。同时提供了基础数据管理（选项1-10）、预设定的数据分析查询（11-18），可以帮助新用户快速上手项目，同时提供了高阶的SQL直接查询功能（选项21），从而实现多元的数据查询功能。

### 与传统问答机器人相比，本项目的 AI Agent 具备以下特点：

* **工具调用 (Tool Using)**: AI 大脑 (`nlp_query.py`) 能够智能判断用户意图。若是分析或可视化需求，大脑会生成包含 `title` 和 `sql` 的 `generate_visualization` 工具调用指令。
* **指令执行 (Action Execution)**: 客户端 (`client_cli.py`) 作为 AI 的执行端，解析指令并执行 SQL 查询，生成图表或展示表格。
* **上下文记忆 (Context Memory)**: 在多轮对话中，客户端会将每次查询的结果（表格数据或图表）反馈给大脑，从而形成记忆，进一步优化后续的分析任务。

---

## 二、技术架构 ⚙️

系统采用现代化的分层架构，融合了 Web 后端、AI 代理、数据分析与强大的命令行交互。

### 1. 技术栈 🧑‍💻

* **后端框架**: FastAPI (Python 3.10+)
* **数据库**: PostgreSQL (推荐13+)
* **ORM**: SQLAlchemy
* **数据分析与可视化**: Pandas, Matplotlib, Seaborn
* **AI 代理核心**:

  * **大脑 (Brain)**: `nlp_query.py` - 集成大模型（如 DeepSeek, Qwen），负责理解意图、生成 SQL 或工具调用指令。
  * **身体 (Body/Actor)**: `client_cli.py` - 负责用户交互、指令分发、本地绘图、结果反馈。
* **命令行客户端**: Rich, prompt-toolkit (支持 SQL 自动补全)
* **依赖管理**: pip + `requirements.txt`
* **打包**: PyInstaller

---

### 2. 系统工作流 (AI Agent Workflow) 🔄

1. **用户输入**: 用户在 `client_cli.py` 中输入自然语言指令 (例如: "帮我分析一下各类设备的使用次数图表")。
2. **请求大脑**: 客户端将对话历史发送给 AI 大脑 (`/nlp/query/`)。
3. **大脑思考**: AI 大脑分析用户意图并生成相应的 SQL 或工具调用指令。
4. **指令执行**: 客户端解析大脑响应，执行相应操作（SQL 查询或图表生成）。
5. **记忆存储**: 包含最新"观察结果"的对话历史准备好，等待用户的下一轮指令。

---

## 三、数据库设计 🗄️

### 1. 用户表 (users)

| 字段名         | 类型                 | 说明    |
| ----------- | ------------------ | ----- |
| id          | SERIAL PRIMARY KEY | 用户 ID |
| name        | VARCHAR(50)        | 用户名   |
| house\_area | FLOAT              | 房屋面积  |

### 2. 房间表 (rooms)

| 字段名  | 类型                 | 说明    |
| ---- | ------------------ | ----- |
| id   | SERIAL PRIMARY KEY | 房间 ID |
| name | VARCHAR(50)        | 房间名   |

### 3. 设备表 (devices)

| 字段名      | 类型                       | 说明    |
| -------- | ------------------------ | ----- |
| id       | SERIAL PRIMARY KEY       | 设备 ID |
| name     | VARCHAR(50)              | 设备名   |
| type     | VARCHAR(30)              | 设备类型  |
| room\_id | INT REFERENCES rooms(id) | 所属房间  |

### 4. 设备使用记录表 (device\_usages)

| 字段名              | 类型                         | 说明    |
| ---------------- | -------------------------- | ----- |
| id               | SERIAL PRIMARY KEY         | 记录 ID |
| user\_id         | INT REFERENCES users(id)   | 用户 ID |
| device\_id       | INT REFERENCES devices(id) | 设备 ID |
| start\_time      | TIMESTAMP                  | 开始时间  |
| end\_time        | TIMESTAMP                  | 结束时间  |
| usage\_type      | VARCHAR(20)                | 使用方式  |
| energy\_consumed | FLOAT                      | 能耗    |
| device\_type     | VARCHAR(30)                | 设备类型  |
| user\_name       | VARCHAR(50)                | 用户名   |

---

## 四、API 设计 🌐

### 1. 核心 AI 代理接口

* **`POST /nlp/query/`**: 这是 AI 大脑的核心入口，接收包含多轮对话历史的 `messages`，返回 SQL 或工具调用指令的 JSON 响应。

### 2. CRUD 接口

* `/users/`, `/rooms/`, `/devices/`, `/device_usages/`, `/security_events/`, `/feedbacks/`: 提供对六个表的标准增删改查 (CRUD) 功能。

### 3. 数据分析接口

* `/analysis/device_usage_frequency`: 设备使用频率分析。
* `/analysis/user_habits`: 用户设备联动习惯分析。
* `/analysis/area_impact`: 房屋面积对设备使用的影响。

---

## 五、命令行客户端 (`client_cli.py`) 🎮

### 主要功能:

* **多种交互模式**: 支持数据管理、固定分析、自然语言问答、智能分析与可视化等。
* **UI**: 使用 `rich` 库构建现代化、色彩丰富的终端界面。
* **SQL 自动补全**: 自动提示表名和列名，提升 SQL 编写效率。
* **本地绘图**: 客户端负责图表生成与显示。

---

## 六、打包与分发 📦

项目支持使用 `PyInstaller` 打包成可执行文件，简化分发与部署。

1. **打包**:

   ```bash
   pyinstaller SmartHomeCLI.spec
   ```
2. **运行**: `.exe` 文件位于 `dist` 目录，直接运行即可启动应用。

---

## 七、项目总结 🎯

本系统通过将 **意图理解**（大脑）和 **任务执行**（身体）分离，并引入 **记忆反馈** 机制，展现了更高的智能和灵活性。通过客户端，用户与 AI Agent 之间的交互变得更加智能、便捷和富有表现力。

