import requests
import sys
from datetime import datetime
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.font_manager import FontProperties

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, IntPrompt
from rich.live import Live
from rich.spinner import Spinner
from rich.align import Align
from rich.console import Group

# Import for autocompletion
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document

console = Console()
BASE_URL = "http://127.0.0.1:8000"

# --- 中文字体配置 (与analysis.py保持一致) ---
try:
    font_path = None
    font_list = ['SimHei', 'Microsoft YaHei', 'SimSun', 'Arial Unicode MS']
    for font in font_list:
        for f in font_manager.fontManager.ttflist:
            if font == f.name:
                font_path = f.fname
                break
        if font_path:
            break
    if not font_path:
        console.print("[yellow]未找到中文字体, 正在尝试下载 SimHei.ttf...[/yellow]")
        simhei_url = 'https://github.com/owent-utils/font/raw/master/simhei.ttf'
        font_path = os.path.join(os.path.dirname(__file__), 'simhei.ttf')
        if not os.path.exists(font_path):
            r = requests.get(simhei_url)
            with open(font_path, 'wb') as f:
                f.write(r.content)
        # 将新字体添加到matplotlib的字体管理器
        font_manager.fontManager.addfont(font_path)

    font_prop = FontProperties(fname=font_path)
    plt.rcParams['font.sans-serif'] = [font_prop.get_name()]
    plt.rcParams['axes.unicode_minus'] = False
except Exception as e:
    console.print(f"[bold red]加载中文字体失败: {e}[/bold red]")
    console.print("[yellow]图表中的中文可能无法正常显示。[/yellow]")
# --- 字体配置结束 ---

# 颜色代码
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
ENDC = '\033[0m'
BOLD = '\033[1m'
MAGENTA = '\033[95m'

# 清屏
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_welcome_message():
    """打印欢迎标题"""
    grid = Table.grid(expand=True)
    grid.add_column(justify="center", ratio=1)
    grid.add_row("\n🤖 [bold magenta]智能家居数据管理与分析系统[/bold magenta] 🤖")
    grid.add_row("[dim cyan]一个集CRUD、数据可视化与AI智能问答于一体的CLI工具[/dim cyan]\n")

    title_panel = Panel(
        grid,
        title="[bold yellow]✨ Welcome ✨[/bold yellow]",
        subtitle="[bold green]v1.3.0-AI-Agent[/bold green]",
        border_style="bold yellow",
        padding=(1, 2),
    )
    console.print(title_panel)

def print_menu():
    menu_layout = """
[bold blue]👤 用户管理[/bold blue]
  [cyan]1.[/cyan] 查询所有用户      [cyan]2.[/cyan] 新增用户

[bold yellow]📦 设备管理[/bold yellow]
  [cyan]3.[/cyan] 查询所有设备      [cyan]4.[/cyan] 新增设备

[bold green]📋 设备使用记录[/bold green]
  [cyan]5.[/cyan] 查询所有设备使用记录
  [cyan]6.[/cyan] 新增设备使用记录

[bold red]🛡️ 安防与📝反馈[/bold red]
  [cyan]7.[/cyan] 查询所有安防事件  [cyan]8.[/cyan] 新增安防事件
  [cyan]9.[/cyan] 查询所有用户反馈  [cyan]10.[/cyan] 新增用户反馈
    """
    analysis_menu = """
[bold magenta]📊 数据分析与可视化[/bold magenta]
  [cyan]11.[/cyan] 设备使用频率分析
  [cyan]12.[/cyan] 用户习惯分析
  [cyan]13.[/cyan] 房屋面积影响分析
  [cyan]14.[/cyan] 各设备类型使用次数
  [cyan]15.[/cyan] 各房间设备总能耗
  [cyan]16.[/cyan] 用户活跃度排行
  [cyan]17.[/cyan] 各房间安防事件数
  [cyan]18.[/cyan] 每日设备使用趋势
    """
    ai_menu = """
[bold yellow]🤖 智能问答与分析[/bold yellow]
  [cyan]19.[/cyan] 自然语言智能问答
  [cyan]20.[/cyan] 智能分析与可视化
    """
    sql_menu = """
[bold cyan]📝 SQL查询功能[/bold cyan]
  [cyan]21.[/cyan] 自定义SQL查询
    """

    menu_panel = Panel(
        menu_layout,
        title="[bold]数据管理[/bold]",
        border_style="cyan",
        padding=(1, 2)
    )
    analysis_panel = Panel(
        analysis_menu,
        title="[bold]数据分析[/bold]",
        border_style="magenta",
        padding=(1, 2)
    )
    ai_panel = Panel(
        ai_menu,
        title="[bold]智能功能[/bold]",
        border_style="yellow",
        padding=(1, 2)
    )
    sql_panel = Panel(
        sql_menu,
        title="[bold]高级功能[/bold]",
        border_style="green",
        padding=(1, 2)
    )

    console.print(menu_panel, analysis_panel, ai_panel, sql_panel)
    console.print("[bold yellow]0. 退出 🏠[/bold yellow]")


def print_table(data, title="查询结果"):
    if not data:
        console.print("[yellow]无数据可供展示。[/yellow]")
        return
    if isinstance(data, dict):
        data = [data]

    table = Table(title=f"[bold green]{title}[/bold green]", show_header=True, header_style="bold magenta", border_style="dim")

    if not data:
        console.print(table)
        return

    keys = data[0].keys()
    for key in keys:
        table.add_column(key, style="dim" if "id" in key.lower() else "")

    for row in data:
        table.add_row(*(str(row.get(k, '')) for k in keys))

    console.print(table)


def display_dataframe(df: pd.DataFrame, title: str = "查询结果"):
    """Renders a pandas DataFrame as a rich Table."""
    if df.empty:
        console.print("[yellow]无数据可供展示。[/yellow]")
        return

    table = Table(title=f"[bold green]{title}[/bold green]", show_header=True, header_style="bold magenta", border_style="dim")

    # Add columns from DataFrame
    for column in df.columns:
        table.add_column(str(column), style="dim" if "id" in str(column).lower() else "")

    # Add rows from DataFrame
    for _, row in df.iterrows():
        table.add_row(*(str(item) for item in row))

    console.print(table)


def is_suitable_for_chart(df: pd.DataFrame) -> bool:
    """A simple heuristic to decide if a DataFrame is suitable for plotting a chart."""
    if df.empty or len(df.columns) < 2 or len(df) > 50:
        return False
    # Check for at least one numeric column (that is not an ID column)
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]) and 'id' not in str(col).lower():
            return True
    return False

def plot_data(df: pd.DataFrame, title: str):
    """Tries to plot a sensible chart from a DataFrame."""
    try:
        plt.figure(figsize=(10, 6))

        x_col = df.columns[0]
        y_col = df.columns[1]

        if not pd.api.types.is_numeric_dtype(df[y_col]):
             console.print(f"[yellow]无法绘图: 第二列 '{y_col}' 不是数值类型。将显示为表格。[/yellow]")
             display_dataframe(df, title)
             return

        plt.bar(df[x_col].astype(str), df[y_col])

        plt.title(title, fontsize=16)
        plt.xlabel(x_col, fontsize=12)
        plt.ylabel(y_col, fontsize=12)
        plt.xticks(rotation=45, ha="right")
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()

        filename = "nlp_analysis_plot.png"
        plt.savefig(filename)
        plt.close()

        console.print(f"[bold green]✔ 分析图表已生成并保存为 [underline]{filename}[/underline][/bold green]")

        if os.name == "nt":
            os.startfile(filename)
        elif sys.platform == "darwin":
            os.system(f"open {filename}")
        else:
            os.system(f"xdg-open {filename}")

    except Exception as e:
        console.print(f"[bold red]绘图时发生错误: {e}[/bold red]")
        console.print("[yellow]将以表格形式显示数据:[/yellow]")
        display_dataframe(df, title)


def get_all_users():
    with console.status("[bold green]正在查询所有用户...[/bold green]", spinner="dots"):
        try:
            resp = requests.get(f"{BASE_URL}/users/")
            resp.raise_for_status()
            print_table(resp.json(), title="所有用户")
        except requests.exceptions.RequestException as e:
            console.print(f"[bold red]请求错误: {e}[/bold red]")

def add_user():
    name = Prompt.ask("[cyan]请输入用户名[/cyan]")
    area = Prompt.ask("[cyan]请输入房屋面积[/cyan]", default="100.0")
    with console.status("[bold green]正在添加用户...[/bold green]", spinner="dots"):
        try:
            resp = requests.post(f"{BASE_URL}/users/", json={"name": name, "house_area": float(area)})
            resp.raise_for_status()
            console.print("[bold green]✔ 用户添加成功！[/bold green]")
            print_table(resp.json(), title="新增用户")
        except requests.exceptions.RequestException as e:
            console.print(f"[bold red]添加失败: {e.response.text if e.response else e}[/bold red]")


def get_all_devices():
    with console.status("[bold green]正在查询所有设备...[/bold green]", spinner="dots"):
        try:
            resp = requests.get(f"{BASE_URL}/devices/")
            resp.raise_for_status()
            print_table(resp.json(), title="所有设备")
        except requests.exceptions.RequestException as e:
            console.print(f"[bold red]请求错误: {e}[/bold red]")


def add_device():
    name = Prompt.ask("[cyan]请输入设备名称[/cyan]")
    dtype = Prompt.ask("[cyan]请输入设备类型[/cyan]")
    room_id = IntPrompt.ask("[cyan]请输入所属房间ID (可选)[/cyan]", default=None)
    with console.status("[bold green]正在添加设备...[/bold green]", spinner="dots"):
        try:
            payload = {"name": name, "type": dtype}
            if room_id is not None:
                payload["room_id"] = room_id
            resp = requests.post(f"{BASE_URL}/devices/", json=payload)
            resp.raise_for_status()
            console.print("[bold green]✔ 设备添加成功！[/bold green]")
            print_table(resp.json(), title="新增设备")
        except requests.exceptions.RequestException as e:
            console.print(f"[bold red]添加失败: {e.response.text if e.response else e}[/bold red]")

def get_all_usages():
    with console.status("[bold green]查询设备使用记录...[/bold green]", spinner="dots"):
        try:
            resp = requests.get(f"{BASE_URL}/device_usages/")
            resp.raise_for_status()
            print_table(resp.json(), title="所有设备使用记录")
        except requests.exceptions.RequestException as e:
            console.print(f"[bold red]请求错误: {e}[/bold red]")

def add_usage():
    user_id = IntPrompt.ask("[cyan]用户ID[/cyan]")
    device_id = IntPrompt.ask("[cyan]设备ID[/cyan]")
    start_time = Prompt.ask("[cyan]开始时间 (YYYY-MM-DD HH:MM:SS)[/cyan]")
    end_time = Prompt.ask("[cyan]结束时间 (可留空)[/cyan]", default="")
    with console.status("[bold green]正在添加记录...[/bold green]", spinner="dots"):
        try:
            data = {
                "user_id": user_id,
                "device_id": device_id,
                "start_time": datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S").isoformat(),
                "end_time": datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S").isoformat() if end_time else None
            }
            resp = requests.post(f"{BASE_URL}/device_usages/", json=data)
            resp.raise_for_status()
            console.print("[bold green]✔ 设备使用记录添加成功！[/bold green]")
            print_table(resp.json())
        except (requests.exceptions.RequestException, ValueError) as e:
            console.print(f"[bold red]添加失败: {e}[/bold red]")

def get_all_events():
    with console.status("[bold green]查询安防事件...[/bold green]", spinner="dots"):
        try:
            resp = requests.get(f"{BASE_URL}/security_events/")
            resp.raise_for_status()
            print_table(resp.json(), title="所有安防事件")
        except requests.exceptions.RequestException as e:
            console.print(f"[bold red]请求错误: {e}[/bold red]")

def add_event():
    user_id = IntPrompt.ask("[cyan]用户ID[/cyan]")
    device_id = IntPrompt.ask("[cyan]设备ID[/cyan]")
    event_type = Prompt.ask("[cyan]事件类型[/cyan]")
    timestamp = Prompt.ask("[cyan]事件时间 (YYYY-MM-DD HH:MM:SS)[/cyan]")
    with console.status("[bold green]正在添加事件...[/bold green]", spinner="dots"):
        try:
            data = { "user_id": user_id, "device_id": device_id, "event_type": event_type, "timestamp": datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").isoformat() }
            resp = requests.post(f"{BASE_URL}/security_events/", json=data)
            resp.raise_for_status()
            console.print("[bold green]✔ 安防事件添加成功！[/bold green]")
            print_table(resp.json())
        except (requests.exceptions.RequestException, ValueError) as e:
            console.print(f"[bold red]添加失败: {e}[/bold red]")


def get_all_feedbacks():
    with console.status("[bold green]查询用户反馈...[/bold green]", spinner="dots"):
        try:
            resp = requests.get(f"{BASE_URL}/feedbacks/")
            resp.raise_for_status()
            print_table(resp.json(), title="所有用户反馈")
        except requests.exceptions.RequestException as e:
            console.print(f"[bold red]请求错误: {e}[/bold red]")

def add_feedback():
    user_id = IntPrompt.ask("[cyan]用户ID[/cyan]")
    content = Prompt.ask("[cyan]反馈内容[/cyan]")
    with console.status("[bold green]正在添加反馈...[/bold green]", spinner="dots"):
        try:
            data = {"user_id": user_id, "content": content}
            resp = requests.post(f"{BASE_URL}/feedbacks/", json=data)
            resp.raise_for_status()
            console.print("[bold green]✔ 反馈添加成功！[/bold green]")
            print_table(resp.json())
        except requests.exceptions.RequestException as e:
            console.print(f"[bold red]添加失败: {e}[/bold red]")

def get_analysis(endpoint, filename):
    url = f"{BASE_URL}/analysis/{endpoint}"
    with console.status(f"[bold green]正在获取分析结果: {endpoint}...[/bold green]", spinner="dots"):
        try:
            resp = requests.get(url)
            resp.raise_for_status()

            content_type = resp.headers.get("content-type", "")

            if "image/png" in content_type:
                with open(filename, "wb") as f:
                    f.write(resp.content)
                console.print(f"[bold green]✔ 分析图片已保存为 [underline]{filename}[/underline][/bold green]")
                # 自动打开图片
                try:
                    if os.name == "nt":
                        os.startfile(filename)
                    elif sys.platform == "darwin":
                        os.system(f"open {filename}")
                    else:
                        os.system(f"xdg-open {filename}")
                except Exception:
                    console.print(f"[yellow]无法自动打开图片, 请手动查看。[/yellow]")
            elif "application/json" in content_type:
                data = resp.json()
                if "data" in data and data["data"]:
                    df = pd.DataFrame(data["data"])
                    display_dataframe(df, title=f"分析结果: {endpoint}")
                elif "error" in data:
                    console.print(f"[bold red]分析出错: {data['error']}[/bold red]")
                else:
                    console.print(f"收到JSON数据，但格式无法解析或为空: {data}")
            else:
                console.print(f"[bold red]错误: 收到未知的响应类型 ({content_type})。[/bold red]")
                console.print(resp.text)

        except requests.exceptions.RequestException as e:
            console.print(f"[bold red]请求失败: {e}[/bold red]")

def choose_model():
    """让用户选择使用哪个大模型"""
    console.print(Panel("[bold cyan]请选择要使用的大语言模型[/bold cyan]"))
    model = Prompt.ask(
        "选择模型",
        choices=["deepseek", "qwen"],
        default="deepseek"
    )
    console.print(f"[green]已选择模型: [bold]{model}[/bold][/green]")
    return model

def nlp_query_mode(model_provider: str):
    """进入自然语言问答模式"""
    console.print(Panel(
        f"您已进入 [bold green]智能问答模式[/bold green] (模型: [cyan]{model_provider}[/cyan])\n"
        "在此模式下，您可以连续提问。\n"
        "输入 'exit' 或 'quit' 退出此模式。",
        title="[bold blue]NLP Query Mode[/bold blue]",
        border_style="blue"
    ))

    # 初始化对话历史
    messages = []

    while True:
        try:
            user_input = Prompt.ask("\n[bold]🤔 请输入您的问题[/bold]")

            if user_input.lower() in ["exit", "quit"]:
                console.print("[yellow]已退出智能问答模式。[/yellow]")
                break

            # 将用户输入添加到历史记录
            messages.append({"role": "user", "content": user_input})

            payload = {"messages": messages, "model": model_provider}

            with console.status("[cyan]大模型正在思考中，请稍候...", spinner="bouncingBall") as status:
                resp = requests.post(f"{BASE_URL}/nlp/", json=payload, timeout=60)
                resp.raise_for_status()
                result = resp.json()

            console.print("\n" + "="*50)

            # --- 核心修改在这里 ---
            # 1. 获取并记录模型的自然语言回答
            raw_answer = result.get("answer", "模型未提供可读的回答。")
            messages.append({"role": "assistant", "content": raw_answer})

            # 2. 检查是否有SQL和数据结果
            sql = result.get("sql")
            data = result.get("data")

            if sql:
                console.print(Panel(sql, title="[green]执行的SQL查询[/green]", border_style="dim green", expand=False))

            if data:
                # 3. 将数据结果也加入记忆系统
                data_str = str(data) # 转换为紧凑的字符串格式
                # 为了防止过长，可以进行截断
                if len(data_str) > 1000:
                    data_str = data_str[:1000] + "... (结果已截断)"

                # 用一个特殊的格式告诉LLM这是工具的返回结果
                observation_message = f"【系统查询结果】:\n{data_str}"
                messages.append({"role": "assistant", "content": observation_message})

                console.print(Panel(f"已将查询结果加入到短期记忆中，您可以继续追问。", title="[cyan]记忆增强[/cyan]", style="dim"))

                df = pd.DataFrame(data)
                display_dataframe(df, "查询结果")

            elif result.get("suggestion"):
                console.print(Panel(result["suggestion"], title="[yellow]模型建议[/yellow]", border_style="yellow"))

            elif result.get("error"):
                 console.print(Panel(
                    f"[bold]错误详情:[/bold] {result.get('error')}\n"
                    f"[bold]原始返回:[/bold] {result.get('raw')}",
                    title="[bold red]执行出错[/bold red]",
                    border_style="red"
                ))

            console.print("="*50 + "\n")

        except requests.RequestException as e:
            console.print(f"\n[bold red]请求失败: {e}[/bold red]")
        except Exception as e:
            console.print(f"\n[bold red]发生未知错误: {e}[/bold red]")
            import traceback
            traceback.print_exc()

def nlp_analysis_mode(model_provider: str):
    """自然语言分析模式，由大模型决定是否生成图表"""
    console.print(Panel(
        f"您已进入 [bold magenta]智能分析模式[/bold magenta] (模型: [cyan]{model_provider}[/cyan])\n"
        "您可以提出分析性问题，AI将自主决定是否生成图表。\n"
        "输入 'exit' 或 'quit' 退出此模式。",
        title="[bold blue]AI-Powered Analysis Mode[/bold blue]",
        border_style="magenta"
    ))

    messages = []

    while True:
        try:
            user_input = Prompt.ask("\n[bold]📊 请输入您想分析的内容[/bold]")
            if user_input.lower() in ['exit', 'quit']:
                console.print("[yellow]已退出智能分析模式。[/yellow]")
                break

            messages.append({"role": "user", "content": user_input})
            payload = {"messages": messages, "model": model_provider}

            with console.status("[cyan]AI正在深度分析并决策中...", spinner="bouncingBall") as status:
                resp = requests.post(f"{BASE_URL}/nlp/", json=payload, timeout=60)
                resp.raise_for_status()
                result = resp.json()

            console.print("\n" + "="*50)

            # --- 智能记忆与行动逻辑 ---
            raw_answer = result.get("answer", "模型未提供可读的回答。")
            messages.append({"role": "assistant", "content": raw_answer})

            data = result.get("data")
            title = result.get("title", user_input)

            # 新增: 用于存储数据供后续解读
            dataframe_for_explanation = None

            if data:
                df = pd.DataFrame(data)
                dataframe_for_explanation = df # 存储起来，供后续AI解读

                # 在模式20(智能分析)中，我们总是优先尝试可视化
                if is_suitable_for_chart(df):
                    console.print(Panel(f"数据分析完成, [bold green]尝试生成可视化图表[/bold green]\n标题: [cyan]{title}[/cyan]", title="[bold]分析结果[/bold]"))
                    plot_data(df, title)
                else:
                    console.print(Panel("[bold blue]数据不适合图表展示, 将以表格形式显示[/bold blue]", title="[bold]分析结果[/bold]"))
                    display_dataframe(df, title)

            elif result.get("suggestion"):
                console.print(Panel(result["suggestion"], title="[yellow]模型建议[/yellow]", border_style="yellow"))
            elif result.get("error"):
                console.print(Panel(
                    f"[bold]错误详情:[/bold] {result.get('error')}\n"
                    f"[bold]原始返回:[/bold] {result.get('raw')}",
                    title="[bold red]执行出错[/bold red]",
                    border_style="red"
                ))

            if data:
                data_str = str(data)
                if len(data_str) > 1000: data_str = data_str[:1000] + "... (结果已截断)"
                messages.append({"role": "assistant", "content": f"【系统查询结果】:\n{data_str}"})

            # --- 按需AI解读 ---
            if dataframe_for_explanation is not None and not dataframe_for_explanation.empty:
                ask_for_explanation = Prompt.ask("\n[bold yellow]需要AI为您进一步解读这份数据吗？(Y/n)[/bold yellow]", default="y", choices=["y", "n"], show_choices=False)
                if ask_for_explanation.lower() == 'y':
                    with console.status("[bold green]🤖 AI数据分析师正在撰写解读报告...[/bold green]", spinner="bouncingBall"):
                        try:
                            # 为AI解读创建独立的上下文，避免与主对话混淆
                            explain_messages = [
                                {"role": "system", "content": "你是一名专业的数据分析师。请根据下方给出的数据表和分析背景，提炼出主要结论、趋势、异常和建议。请用简洁、专业的中文自然语言输出，不要输出SQL或代码。"},
                                {"role": "user", "content": f"【分析背景】\n{user_input}\n\n【数据表】\n{dataframe_for_explanation.head(20).to_csv(index=False)}"}
                            ]
                            resp2 = requests.post(f"{BASE_URL}/nlp/", json={"messages": explain_messages, "model": model_provider})
                            explanation = resp2.json().get("suggestion") or resp2.json().get("answer") or "未能获取AI解读。"
                            console.print(Panel(explanation, title="[bold green]🤖 AI数据分析师解读[/bold green]", border_style="green", expand=True))
                        except Exception as e:
                             console.print(f"[dim]获取AI解读失败: {e}[/dim]")

            console.print("="*50 + "\n")

        except requests.RequestException as e:
            console.print(f"\n[bold red]请求失败: {e}[/bold red]")
        except Exception as e:
            console.print(f"\n[bold red]发生未知错误: {e}[/bold red]")
            import traceback
            traceback.print_exc()

def sql_query_cli():
    """进入自定义SQL查询模式，并提供自动补全功能"""
    # --- SQL自动补全 ---
    SQL_KEYWORDS = [
        'SELECT', 'FROM', 'WHERE', 'INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET',
        'DELETE', 'CREATE', 'TABLE', 'DATABASE', 'ALTER', 'DROP', 'INDEX',
        'PRIMARY', 'KEY', 'FOREIGN', 'REFERENCES', 'NULL', 'NOT', 'AND', 'OR',
        'LIMIT', 'ORDER', 'BY', 'ASC', 'DESC', 'GROUP', 'HAVING', 'COUNT',
        'SUM', 'AVG', 'MIN', 'MAX', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'ON',
        'AS', 'DISTINCT', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'IN'
    ]

    class SQLCompleter(Completer):
        """一个具备上下文感知能力的SQL补全器"""
        def __init__(self, schema: dict):
            self.schema = schema if isinstance(schema, dict) else {}
            self.tables = list(self.schema.keys())
            self.columns = [col for cols in self.schema.values() for col in cols]
            self.all_keywords = [kw.lower() for kw in SQL_KEYWORDS]

        def get_completions(self, document: Document, complete_event):
            text_before_cursor = document.text_before_cursor.lower()
            word_before_cursor = document.get_word_before_cursor(WORD=True).lower()

            # 基于上下文决定补全内容
            suggestions = self._get_contextual_suggestions(text_before_cursor)

            # 过滤并生成补全项
            for suggestion in sorted(list(set(suggestions))):
                if suggestion.lower().startswith(word_before_cursor):
                    yield Completion(
                        suggestion,
                        start_position=-len(word_before_cursor),
                        display_meta=self.get_meta(suggestion)
                    )

        def _get_contextual_suggestions(self, text: str) -> list:
            """根据上下文返回建议列表"""
            words = text.split()
            if not words:
                return self.all_keywords

            last_word = words[-1]
            # 如果光标不在最后一个词的末尾，则认为最后一个词也在被补全
            if not text.endswith(' '):
                 # 弹出最后一个词，分析它前面的上下文
                 last_word = words.pop() if len(words) > 1 else ''

            # 默认建议是关键字
            suggestions = self.all_keywords

            if last_word in ['from', 'join', 'update']:
                # 在 FROM, JOIN, UPDATE 后，主要建议表名
                suggestions = self.tables
            elif last_word in ['where', 'on', 'and', 'or', 'by', 'set', 'select']:
                 # 在 WHERE, ON 等后面，建议列名和关键字
                 suggestions = self.columns + self.all_keywords
            elif last_word in self.tables:
                 # 在表名后，建议列名
                 suggestions = self.schema.get(last_word, [])

            return suggestions

        def get_meta(self, word: str) -> str:
            if word.upper() in SQL_KEYWORDS:
                return 'Keyword'
            if word in self.tables:
                return 'Table'
            if word in self.columns:
                return 'Column'
            return ''

    # 启动时获取schema
    completer = None
    session = PromptSession(complete_while_typing=True) # Fallback session
    try:
        with console.status("[dim]正在加载SQL自动补全数据...[/dim]"):
            resp = requests.get(f"{BASE_URL}/api/schema_for_completion")
            resp.raise_for_status()
            schema = resp.json()
        if "error" in schema:
            console.print(f"[yellow]无法加载SQL自动补全: {schema['error']}[/yellow]")
        else:
            completer = SQLCompleter(schema)
            session = PromptSession(completer=completer, complete_while_typing=True)
            console.print("[green]✔ SQL自动补全已启用。在输入时按Tab键或等待片刻即可看到提示。[/green]")
    except Exception as e:
        console.print(f"[yellow]无法加载SQL自动补全: {e}[/yellow]")
    # --- 自动补全结束 ---

    console.print(Panel("[bold yellow]进入SQL查询模式, 输入 'exit' 或 'quit' 返回。[/bold yellow]\n[dim]示例: SELECT * FROM users LIMIT 5;[/dim]"))
    while True:
        try:
            sql = session.prompt("SQL > ").strip()

            if sql.lower() in ['exit', 'quit']:
                console.print("[cyan]已退出SQL查询模式。[/cyan]")
                break
            if not sql:
                continue

            with console.status(f"[bold green]正在执行SQL...[/bold green]"):
                resp = requests.post(f"{BASE_URL}/api/sql_query", json={"sql": sql})
                data = resp.json()
                if data.get("success"):
                    print_table(data["data"], title="SQL查询结果")
                else:
                    console.print(f"[bold red]查询失败: {data.get('error', '未知错误')}[/bold red]")
        except requests.exceptions.RequestException as e:
            console.print(f"[bold red]请求出错: {e}[/bold red]")
        except KeyboardInterrupt:
            # 在Prompt中按Ctrl+C会触发此异常，需要优雅退出
            console.print("\n[cyan]已退出SQL查询模式。[/cyan]")
            break

def main():
    clear()
    print_welcome_message()
    while True:
        print_menu()
        choice = Prompt.ask(f"[bold]请选择操作[/bold]", choices=[str(i) for i in range(22)], show_choices=False)

        actions = {
            "1": get_all_users, "2": add_user, "3": get_all_devices, "4": add_device,
            "5": get_all_usages, "6": add_usage, "7": get_all_events, "8": add_event,
            "9": get_all_feedbacks, "10": add_feedback,
            "11": lambda: get_analysis("device_usage_frequency", "device_usage_frequency.png"),
            "12": lambda: get_analysis("user_habits", "user_habits.png"),
            "13": lambda: get_analysis("area_impact", "area_impact.png"),
            "14": lambda: get_analysis("device_type_usage", "device_type_usage.png"),
            "15": lambda: get_analysis("room_energy", "room_energy.png"),
            "16": lambda: get_analysis("user_activity", "user_activity.png"),
            "17": lambda: get_analysis("room_event_count", "room_event_count.png"),
            "18": lambda: get_analysis("daily_device_usage", "daily_device_usage.png"),
            "19": lambda: nlp_query_mode(choose_model()),
            "20": lambda: nlp_analysis_mode(choose_model()),
            "21": sql_query_cli,
            "0": lambda: sys.exit(console.print("[bold cyan]感谢使用, 再见！[/bold cyan]"))
        }

        action = actions.get(choice)
        if action:
            action()
            Prompt.ask("\n[dim]按回车键返回主菜单...[/dim]")
            clear()
            print_welcome_message()
        else:
            console.print("[bold red]无效选择, 请重试。[/bold red]")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]程序被用户中断。[/bold yellow]")
        sys.exit(0) 
