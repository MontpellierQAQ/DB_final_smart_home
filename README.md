# 智能家居 AI agent 查询系统

## 一、项目简介

本项目为智能家居管理与分析系统，其核心是一个具备**思考**、**行动**和**记忆**能力的AI代理（AI Agent）。系统基于 FastAPI 框架和 PostgreSQL 数据库，通过命令行客户端 `client_cli.py` 提供服务。用户可以使用自然语言与 AI 代理进行多轮对话，完成复杂的数据库查询、数据分析和可视化任务。

与传统的问答机器人不同，本项目的 AI 代理具备以下特点：

- **工具调用 (Tool Using)**: AI 大脑 (`nlp_query.py`) 能够智能判断用户意图。当识别到分析或可视化需求时，它不会直接生成数据，而是生成一个包含 `title` 和 `sql` 的 `generate_visualization` 工具调用指令。
- **指令执行 (Action Execution)**: 客户端 (`client_cli.py`) 作为 AI 的身体和执行者，接收并解析来自大脑的指令。当接收到 `visualize` 指令后，它会在本地执行 SQL、获取数据，并调用 `matplotlib` 生成和展示图表。
- **上下文记忆 (Context Memory)**: 在多轮对话中，客户端会将每次查询的结果（无论是表格数据还是"已生成图表"的观察结果）反馈给大脑，形成闭环的上下文记忆，使 agent 能够基于先前的交互进行更深入的分析。

## 二、技术架构

系统采用现代化的分层架构，融合了 Web 后端、AI 代理、数据分析和强大的命令行交互。

### 1. 技术栈
- **后端框架**: FastAPI (Python 3.10+)
- **数据库**: PostgreSQL (推荐13+)
- **ORM**: SQLAlchemy
- **数据分析与可视化**: Pandas, Matplotlib, Seaborn
- **AI 代理核心**:
    - **大脑 (Brain)**: `nlp_query.py` - 集成大模型（如 DeepSeek, Qwen），负责理解意图、生成 SQL 或工具调用指令。
    - **身体 (Body/Actor)**: `client_cli.py` - 负责用户交互、指令分发、本地绘图、结果反馈。
- **命令行客户端**: Rich, prompt-toolkit (支持 SQL 自动补全)
- **依赖管理**: pip + `requirements.txt`
- **打包**: PyInstaller

### 2. 系统工作流 (AI Agent Workflow)
1. **用户输入**: 用户在 `client_cli.py` 中输入自然语言指令 (例如 "帮我分析一下各类设备的使用次数图表")。
2. **请求大脑**: 客户端将完整的对话历史（包含用户问题和过往的"观察结果"）发送到后端的 AI 大脑 (`/nlp/query/`)。
3. **大脑思考**:
    - AI 大脑根据最新的用户问题和上下文，判断用户意图。
    - 若为分析性问题，大脑生成一个 `generate_visualization` 的 JSON 工具调用指令。
    - 若为简单查询，大脑直接生成 SQL 语句。
4. **大脑响应**: 大脑将生成的指令 (JSON 或 SQL) 返回给客户端。
5. **指令执行**:
    - 客户端解析大脑的响应。
    - 如果是 `visualize` 指令，客户端提取 SQL，在本地执行，并调用 `plot_data` 函数生成图表。然后将 `Observation: [CHART_GENERATED]` 添加到对话历史中。
    - 如果是 SQL 数据，客户端直接用 `rich` 库渲染成表格。然后将 `Observation: [TABLE_DATA]` 添加到对话历史中。
6. **记忆存储**: 包含新"观察结果"的对话历史准备就绪，等待用户的下一轮指令。

### 3. 数据库 E-R 图
- 采用标准E-R建模，实体（矩形）、属性（椭圆，主键下划线）、联系（菱形）、连线标注1/N，详见下方E-R图规范与Mermaid代码
- 支持房间（rooms）与设备、用户与行为、事件、反馈等多维度关联

## 三、数据库设计

### 1. users（用户表）
| 字段名      | 类型         | 说明         |
| ----------- | ------------ | ------------ |
| id          | SERIAL PRIMARY KEY | 用户ID      |
| name        | VARCHAR(50)  | 用户名       |
| house_area  | FLOAT        | 房屋面积     |

### 2. rooms（房间表）
| 字段名      | 类型         | 说明         |
| ----------- | ------------ | ------------ |
| id          | SERIAL PRIMARY KEY | 房间ID      |
| name        | VARCHAR(50)  | 房间名       |

### 3. devices（设备表）
| 字段名      | 类型         | 说明         |
| ----------- | ------------ | ------------ |
| id          | SERIAL PRIMARY KEY | 设备ID      |
| name        | VARCHAR(50)  | 设备名       |
| type        | VARCHAR(30)  | 设备类型     |
| room_id     | INT REFERENCES rooms(id) | 所属房间 |

### 4. device_usages（设备使用记录表）
| 字段名         | 类型         | 说明         |
| -------------- | ------------ | ------------ |
| id             | SERIAL PRIMARY KEY | 记录ID      |
| user_id        | INT REFERENCES users(id) | 用户ID  |
| device_id      | INT REFERENCES devices(id) | 设备ID |
| start_time     | TIMESTAMP    | 开始时间     |
| end_time       | TIMESTAMP    | 结束时间     |
| usage_type     | VARCHAR(20)  | 使用方式（自动/手动/定时）|
| energy_consumed| FLOAT        | 能耗        |
| device_type    | VARCHAR(30)  | 设备类型（冗余）|
| user_name      | VARCHAR(50)  | 用户名（冗余）|

### 5. security_events（安防事件表）
| 字段名      | 类型         | 说明         |
| ----------- | ------------ | ------------ |
| id          | SERIAL PRIMARY KEY | 事件ID      |
| user_id     | INT REFERENCES users(id) | 用户ID  |
| device_id   | INT REFERENCES devices(id) | 设备ID |
| event_type  | VARCHAR(30)  | 事件类型     |
| event_level | VARCHAR(10)  | 事件等级     |
| location    | VARCHAR(50)  | 发生位置     |
| status      | VARCHAR(20)  | 处理状态     |
| timestamp   | TIMESTAMP    | 事件时间     |

### 6. feedbacks（用户反馈表）
| 字段名      | 类型         | 说明         |
| ----------- | ------------ | ------------ |
| id          | SERIAL PRIMARY KEY | 反馈ID      |
| user_id     | INT REFERENCES users(id) | 用户ID  |
| content     | TEXT         | 反馈内容     |
| feedback_type| VARCHAR(20) | 反馈类型     |
| status      | VARCHAR(20)  | 处理状态     |
| device_id   | INT REFERENCES devices(id) | 关联设备 |
| timestamp   | TIMESTAMP    | 反馈时间     |

## 四、API 设计

系统的核心交互通过命令行客户端完成：

### 1. 核心 AI 代理接口
- **`POST /nlp/query/`**: **AI 大脑的核心入口**。接收包含多轮对话历史的 `messages`，返回包含 SQL 或工具调用指令的 JSON 响应。

### 2. CRUD 接口
- `/users/`, `/rooms/`, `/devices/`, `/device_usages/`, `/security_events/`, `/feedbacks/`: 提供对所有六个表的标准增删改查 (CRUD) 功能。

### 3. 数据分析接口 (固定图表)
- `/analysis/device_usage_frequency`: 设备使用频率分析。
- `/analysis/user_habits`: 用户设备联动习惯分析 (热力图)。
- `/analysis/area_impact`: 房屋面积对设备使用的影响。
- `/analysis/device_type_usage`: 各设备类型使用次数统计。
- `/analysis/room_energy`: 各房间总能耗分布。
- `/analysis/user_activity`: 用户活跃度排行。
- `/analysis/room_event_count`: 各房间安防事件数。
- `/analysis/daily_device_usage`: 每日设备使用趋势。

### 4. 高级功能接口
- **`GET /api/schema_for_completion`**: 获取数据库的完整 schema (表名和列名)，专用于客户端的 SQL 自动补全功能。
- **`POST /api/sql_query`**: 直接执行原始 SQL 查询语句 (仅限 `SELECT`)。

## 五、命令行客户端 (`client_cli.py`)

客户端是本项目的精髓，是用户与 AI 代理交互的唯一界面。

### 1. 主要功能
- **多种交互模式**:
    - **数据管理 (1-10)**: 执行基本的增删查改。
    - **固定分析 (11-18)**: 调用后端的固定分析接口并显示图表。
    - **自然语言问答 (19)**: 单轮的、无记忆的 "Text-to-SQL" 模式。
    - **智能分析与可视化 (20)**: **核心 AI 代理模式**。支持多轮对话、工具调用、上下文记忆和自主绘图。
    - **SQL 查询 (21)**: 支持自动补全的 SQL 输入模式。
- **炫酷的 UI**: 使用 `rich` 库构建现代化、色彩丰富的终端界面。
- **SQL 自动补全**: 在 SQL 模式 (21) 下，自动提示表名和列名，极大提升编写 SQL 的效率。
- **本地绘图**: 客户端自身负责图表的生成和显示
- **配置化**: 通过 `.env` 文件管理 API 密钥，安全方便。

### 2. 启动与运行
1. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```
2. **配置环境变量**:
   - 复制或重命名 `.env.example` 为 `.env`。
   - 在 `.env` 文件中填入你的 `DEEPSEEK_API_KEY` 和/或 `QWEN_API_KEY`。
   - 检查 `database.py` 中的数据库连接字符串。
3. **一键启动**:
   - 直接运行 `start_all.bat` (Windows) 或对应的脚本。该脚本会同时启动 FastAPI 后端服务和客户端。
4. **手动启动**:
   - **启动后端**: `uvicorn main:app --reload`
   - **启动客户端**: `python client_cli.py`

## 六、打包与分发

项目支持使用 `PyInstaller` 打包成单个可执行文件。

1.  **打包**:
    ```bash
    pyinstaller SmartHomeCLI.spec
    ```
2.  **运行**: 生成的 `.exe` 文件位于 `dist` 目录下。直接运行即可启动整个应用。

> **注意**: `SmartHomeCLI.spec` 文件经过特殊配置，包含了 `simhei.ttf` 字体文件和 `.env` 配置文件，确保打包后的程序能正常工作。

## 七、项目总结

本系统通过将**意图理解**（大脑）和**任务执行**（身体）分离，并建立**记忆反馈**机制，系统展现了更高的智能和灵活性。客户端成为 AI Agent 的执行端，负责了绘图、记忆管理等关键任务，实现了 "AI-Powered" 的应用体验。
