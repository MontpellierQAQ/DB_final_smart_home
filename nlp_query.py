import httpx
from fastapi import APIRouter, Request, Depends
import os
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import re
from typing import Optional

router = APIRouter()

# --- 全局变量，用于缓存数据库Schema ---
DB_SCHEMA_PROMPT_CACHE = None

def get_db_schema_prompt():
    """
    动态生成并缓存数据库的Schema描述，用于注入到LLM的Prompt中。
    """
    global DB_SCHEMA_PROMPT_CACHE
    if DB_SCHEMA_PROMPT_CACHE:
        return DB_SCHEMA_PROMPT_CACHE

    try:
        inspector = inspect(engine)
        schema_info = []
        table_names = inspector.get_table_names()

        for table_name in table_names:
            columns = inspector.get_columns(table_name)
            column_names = [f"{col['name']} ({col['type']})" for col in columns]
            schema_info.append(f"-- Table: {table_name}\n-- Columns: {', '.join(column_names)}")

        # 将所有表信息合并成一个字符串
        full_schema_str = "\n".join(schema_info)

        # 提示词
        schema_prompt = (
            "你是一名专业的智能家居数据分析师助手。请根据用户的自然语言需求和下方提供的数据库表结构，严格遵循规则，生成SQL或调用工具。\n\n"
            "【数据库表结构】:\n"
            f"{full_schema_str}\n\n"
            "【重要指导原则】:\n"
            "1. **利用上下文**: 请务必利用之前的对话历史（包括之前的查询结果）来理解上下文。\n"
            "2. **忠于表结构**: 只能使用上方【数据库表结构】中存在的表和字段，不要猜测不存在的字段。\n\n"
            "【可用工具】:\n"
            "1. `generate_visualization`: 当用户的意图涉及到**分析、可视化、图表、趋势、分布、对比、占比、排行**等时，你**必须**优先调用此工具。此工具需要一个`title`（图表标题）和一条用于生成数据的`sql`查询。\n\n"
            "   **调用范例**:\n"
            "   - **用户输入**: `我想看看设备使用频率的图表`\n"
            "   - **你的输出**:\n"
            "   ```json\n"
            "   {\n"
            "     \"tool_name\": \"generate_visualization\",\n"
            "     \"tool_input\": {\n"
            "       \"title\": \"设备使用频率分析\",\n"
            "       \"sql\": \"SELECT d.name, COUNT(u.id) AS usage_count FROM device_usages u JOIN devices d ON u.device_id = d.id GROUP BY d.name ORDER BY usage_count DESC;\"\n"
            "     }\n"
            "   }\n"
            "   ```\n\n"
            "【生成要求】:\n"
            "1. 如果决定调用工具，你的**全部回答**必须严格遵循上述JSON格式，**只能**输出JSON代码块，禁止包含任何额外的解释或文字。\n"
            "2. **仅当**用户进行简单的、非分析性的数据查询时（如'张三的id是多少？'），才直接生成SQL语句，并以分号结尾。\n"
            "3. 不允许生成任何DROP/TRUNCATE/ALTER等危险操作。\n"
            "4. 如果无法生成SQL或调用工具，请只用简洁中文说明原因。"
        )

        DB_SCHEMA_PROMPT_CACHE = schema_prompt
        print("[INFO] Successfully generated and cached DB schema prompt.")
        return schema_prompt
    except Exception as e:
        print(f"[ERROR] Failed to generate DB schema: {e}")
        # 如果生成失败，返回一个降级的、不包含Schema的Prompt
        return (
            "你是一名专业的智能家居数据分析师助手。请根据用户的自然语言需求，严格生成一条可在PostgreSQL数据库直接执行的SQL语句。请注意以下要求：\n"
            "1. 只输出SQL语句本身，不要输出任何解释、注释或自然语言说明。\n"
            "2. 你可以自由进行多表关联、聚合、分组、嵌套、排序、模糊查询、统计分析等复杂SQL操作。\n"
            "3. 只生成一条SQL，结尾必须加分号。\n"
            "4. 不允许生成任何DROP/TRUNCATE/ALTER等危险操作，只允许SELECT、INSERT、UPDATE、DELETE。\n"
            "5. 如无法生成SQL，请只用简洁中文说明原因。"
        )

# --- 模型配置 ---
# DeepSeek (默认)
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY") # 从环境变量加载

# 通义千问 (Qwen) - 使用OpenAI兼容模式
QWEN_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
# !! 请在环境变量中设置您的通义千问API Key, 变量名为 QWEN_API_KEY
QWEN_API_KEY = os.getenv("QWEN_API_KEY") # 从环境变量加载


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.on_event("startup")
def on_startup():
    # 在服务启动时，预热并缓存Schema Prompt
    get_db_schema_prompt()

@router.post("/")
async def nlp_query(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    # 兼容旧版和新版：优先读取messages，如果不存在，则读取question并包装
    messages = data.get("messages")
    if not messages:
        question = data.get("question")
        if not question:
            return {"error": "缺少问题内容"}
        messages = [{"role": "user", "content": question}]

    model_provider = data.get("model", "deepseek")  # 默认为 deepseek
    
    # 获取包含最新DB Schema的系统指令
    system_prompt = get_db_schema_prompt()

    # 将系统指令插入到消息列表的开头
    final_messages = [{"role": "system", "content": system_prompt}] + messages
    
    # 根据模型提供商构造请求
    if model_provider == "deepseek":
        api_url = DEEPSEEK_API_URL
        api_key = DEEPSEEK_API_KEY
        payload = {
            "model": "deepseek-reasoner",
            "messages": final_messages,
            "stream": False
        }
    elif model_provider == "qwen":
        api_url = QWEN_API_URL
        api_key = QWEN_API_KEY
        # 使用OpenAI兼容模式的payload
        payload = {
            "model": "qwen-max-longcontext",
            "messages": final_messages
        }
    else:
        return {"error": f"不支持的模型提供商: {model_provider}"}

    if not api_key:
        return {"error": f"未能找到模型 '{model_provider}' 的API Key。请确保您已在 .env 文件中配置了 {model_provider.upper()}_API_KEY。"}

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(api_url, json=payload, headers=headers, timeout=60)
            resp.raise_for_status()
            result = resp.json()
        except httpx.RequestError as e:
            return {"error": f"请求大模型API失败: {e}"}

    # 根据模型提供商解析响应
    try:
        if model_provider == "deepseek":
            answer = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        elif model_provider == "qwen":
            # 检查通义千问是否返回了包含在200 OK响应中的错误信息
            if "code" in result and result["code"]:
                error_msg = result.get('message', '无详细错误信息。')
                return {"error": f"通义千问API返回错误: {error_msg}", "raw_result": result}
            # 按照OpenAI兼容模式解析
            answer = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        else:
            answer = ""
    except (IndexError, KeyError, TypeError) as e:
        return {"error": "解析大模型返回内容失败", "exception": str(e), "raw_result": result}

    # --- 调度中心逻辑 ---
    # 优先检查是否是调用可视化工具
    try:
        tool_call_match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', answer)
        if tool_call_match:
            import json
            tool_call_data = json.loads(tool_call_match.group(1))
            if tool_call_data.get("tool_name") == "generate_visualization":
                tool_input = tool_call_data.get("tool_input", {})
                sql = tool_input.get("sql")
                title = tool_input.get("title", "AI生成图表")
                if sql:
                    rows = db.execute(text(sql)).mappings().all()
                    # 向客户端返回明确的可视化指令
                    return {"action": "visualize", "data": rows, "title": title, "answer": answer}
    except Exception:
        # JSON解析失败或格式不符，继续执行后续逻辑
        pass

    # 如果不是工具调用，则执行旧的SQL提取逻辑
    sql_match = re.search(r'((select|insert|update|delete)[\s\S]+?;)', answer, re.IGNORECASE)
    if sql_match:
        sql = sql_match.group(1).strip()
        try:
            sql_type = sql.strip().split()[0].lower()
            if sql_type == 'select':
                rows = db.execute(text(sql)).mappings().all()

                # --- Safety Net Logic ---
                # Get the last user question from the conversation history.
                user_messages = [m for m in messages if m.get("role") == "user"]
                last_user_question = user_messages[-1].get("content", "").lower() if user_messages else ""

                visualization_keywords = ["图表", "可视化", "分析", "趋势", "分布", "对比", "占比", "排行", "chart", "visualize", "analysis", "trend", "distribution", "comparison", "ranking"]
                
                # If the user's query contained visualization keywords and we have data,
                # we override the LLM's formatting failure and force a visualization.
                if any(keyword in last_user_question for keyword in visualization_keywords) and rows:
                     return {
                        "action": "visualize",
                        "data": rows,
                        "title": last_user_question.capitalize(),
                        "answer": answer
                    }
                
                # If no keywords are found, proceed as normal.
                return {"sql": sql, "data": rows, "answer": answer}
            else:
                result2 = db.execute(text(sql))
                db.commit()
                return {"sql": sql, "rowcount": result2.rowcount, "message": f"{sql_type.upper()} 执行成功", "answer": answer}
        except Exception as e:
            db.rollback()
            return {"sql": sql, "error": str(e), "raw": answer, "answer": answer}
    else:
        return {"suggestion": answer, "error": "未能识别出SQL语句", "raw": answer, "answer": answer}