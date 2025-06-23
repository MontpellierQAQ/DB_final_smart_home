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
from rich.prompt import Prompt

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
        console.print(
            "[yellow]未找到中文字体, 正在尝试下载 SimHei.ttf...[/yellow]"
        )
        simhei_url = (
            'https://github.com/owent-utils/font/raw/master/simhei.ttf'
        )
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
MAGENTA = '\033[95m'
GREEN = '\033[92m'


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_welcome_message():
    """打印更炫酷的欢迎标题"""
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

    table = Table(
        title=f"[bold green]{title}[/bold green]",
        show_header=True,
        header_style="bold magenta",
        border_style="dim"
    )

    if not data:
        console.print(table)
        return

    keys = data[0].keys()
    for key in keys:
        table.add_column(
            key, style="dim" if "id" in key.lower() else ""
        )

    for row in data:
        table.add_row(*(str(row.get(k, '')) for k in keys))

    console.print(table)


def display_dataframe(df: pd.DataFrame, title: str = "查询结果"):
    """Renders a pandas DataFrame as a rich Table."""
    if df.empty:
        console.print("[yellow]无数据可供展示。[/yellow]")
        return

    table = Table(
        title=f"[bold green]{title}[/bold green]",
        show_header=True,
        header_style="bold magenta",
        border_style="dim"
    )

    # Add columns from DataFrame
    for column in df.columns:
        table.add_column(
            str(column), style="dim" if "id" in str(column).lower() else ""
        )

    # Add rows from DataFrame
    for _, row in df.iterrows():
        table.add_row(*(str(item) for item in row))

    console.print(table)


def is_suitable_for_chart(df: pd.DataFrame) -> bool:
    """A simple heuristic to decide if a DataFrame is suitable for plotting."""
    if df.empty or len(df.columns) < 2 or len(df) > 50:
        return False
    # Check for at least one numeric column (that is not an ID column)
    for col in df.columns:
        if (pd.api.types.is_numeric_dtype(df[col]) and
                'id' not in str(col).lower()):
            return True
    return False


def plot_data(df: pd.DataFrame, title: str):
    """Tries to plot a sensible chart from a DataFrame."""
    try:
        plt.figure(figsize=(10, 6))

        x_col = df.columns[0]
        y_col = df.columns[1]

        if not pd.api.types.is_numeric_dtype(df[y_col]):
            console.print(
                f"[yellow]无法绘图: 第二列 '{y_col}' 不是数值类型。"
                "将显示为表格。[/yellow]"
            )
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

        console.print(
            f"[bold green]✔ 分析图表已生成并保存为 "
            f"[underline]{filename}[/underline][/bold green]"
        )

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
    with console.status(
        "[bold green]正在查询所有用户...[/bold green]", spinner="dots"
    ):
        try:
            resp = requests.get(f"{BASE_URL}/users/")
            resp.raise_for_status()
            print_table(resp.json(), "所有用户")
        except requests.RequestException as e:
            console.print(f"[bold red]查询失败: {e}[/bold red]")


def add_user():
    try:
        name = Prompt.ask("[cyan]请输入用户名[/cyan]")
        area = Prompt.ask("[cyan]请输入房屋面积[/cyan]")
        with console.status("[bold green]正在添加用户...[/bold green]"):
            resp = requests.post(
                f"{BASE_URL}/users/",
                json={"name": name, "house_area": float(area)}
            )
            resp.raise_for_status()
            print_table(resp.json(), "新增用户成功")
    except requests.RequestException as e:
        console.print(
            f"[bold red]添加失败: "
            f"{e.response.text if e.response else e}[/bold red]"
        )
    except ValueError:
        console.print("[bold red]输入错误: 房屋面积必须是数字。[/bold red]")


def get_all_devices():
    with console.status(
        "[bold green]正在查询所有设备...[/bold green]", spinner="dots"
    ):
        try:
            resp = requests.get(f"{BASE_URL}/devices/")
            resp.raise_for_status()
            print_table(resp.json(), "所有设备")
        except requests.RequestException as e:
            console.print(f"[bold red]查询失败: {e}[/bold red]")


def add_device():
    try:
        name = Prompt.ask("[cyan]请输入设备名[/cyan]")
        dtype = Prompt.ask("[cyan]请输入设备类型[/cyan]")
        room_id = Prompt.ask("[cyan]请输入所属房间ID[/cyan]")
        with console.status("[bold green]正在添加设备...[/bold green]"):
            resp = requests.post(
                f"{BASE_URL}/devices/",
                json={"name": name, "type": dtype, "room_id": int(room_id)}
            )
            resp.raise_for_status()
            print_table(resp.json(), "新增设备成功")
    except requests.RequestException as e:
        console.print(
            f"[bold red]添加失败: "
            f"{e.response.text if e.response else e}[/bold red]"
        )
    except ValueError:
        console.print("[bold red]输入错误: 房间ID必须是数字。[/bold red]")


def get_all_usages():
    with console.status(
        "[bold green]查询设备使用记录...[/bold green]", spinner="dots"
    ):
        try:
            resp = requests.get(f"{BASE_URL}/device_usages/")
            resp.raise_for_status()
            print_table(resp.json(), "所有设备使用记录")
        except requests.RequestException as e:
            console.print(f"[bold red]查询失败: {e}[/bold red]")


def add_usage():
    try:
        user_id = Prompt.ask("[cyan]请输入用户ID[/cyan]")
        device_id = Prompt.ask("[cyan]请输入设备ID[/cyan]")
        start_time = Prompt.ask("[cyan]请输入开始时间 (YYYY-MM-DD HH:MM:SS)[/cyan]")
        end_time = Prompt.ask("[cyan]请输入结束时间 (可留空)[/cyan]")
        usage_type = Prompt.ask("[cyan]请输入使用方式[/cyan]")
        energy = Prompt.ask("[cyan]请输入能耗[/cyan]")
        with console.status("[bold green]正在添加记录...[/bold green]"):
            start_iso = datetime.strptime(
                start_time, "%Y-%m-%d %H:%M:%S"
            ).isoformat()
            end_iso = datetime.strptime(
                end_time, "%Y-%m-%d %H:%M:%S"
            ).isoformat() if end_time else None

            payload = {
                "user_id": int(user_id),
                "device_id": int(device_id),
                "start_time": start_iso,
                "end_time": end_iso,
                "usage_type": usage_type,
                "energy_consumed": float(energy)
            }
            resp = requests.post(f"{BASE_URL}/device_usages/", json=payload)
            resp.raise_for_status()
            print_table(resp.json(), "新增记录成功")
    except requests.RequestException as e:
        console.print(
            f"[bold red]添加失败: "
            f"{e.response.text if e.response else e}[/bold red]"
        )
    except (ValueError, TypeError):
        console.print(
            "[bold red]输入错误: 请检查ID和能耗是否为数字, "
            "日期格式是否为 YYYY-MM-DD HH:MM:SS。[/bold red]"
        )


def get_all_events():
    with console.status(
        "[bold green]正在查询安防事件...[/bold green]", spinner="dots"
    ):
        try:
            resp = requests.get(f"{BASE_URL}/security_events/")
            resp.raise_for_status()
            print_table(resp.json(), "所有安防事件")
        except requests.RequestException as e:
            console.print(f"[bold red]查询失败: {e}[/bold red]")


def add_event():
    try:
        user_id = Prompt.ask("[cyan]请输入用户ID[/cyan]")
        device_id = Prompt.ask("[cyan]请输入设备ID[/cyan]")
        event_type = Prompt.ask("[cyan]请输入事件类型[/cyan]")
        timestamp = Prompt.ask("[cyan]请输入事件时间 (YYYY-MM-DD HH:MM:SS)[/cyan]")
        with console.status("[bold green]正在添加事件...[/bold green]"):
            data = {
                "user_id": int(user_id),
                "device_id": int(device_id),
                "event_type": event_type,
                "timestamp": datetime.strptime(
                    timestamp, "%Y-%m-%d %H:%M:%S"
                ).isoformat()
            }
            resp = requests.post(f"{BASE_URL}/security_events/", json=data)
            resp.raise_for_status()
            print_table(resp.json(), "新增事件成功")
    except requests.RequestException as e:
        console.print(
            f"[bold red]添加失败: "
            f"{e.response.text if e.response else e}[/bold red]"
        )
    except (ValueError, TypeError):
        console.print(
            "[bold red]输入错误: 请检查ID是否为数字, "
            "日期格式是否为 YYYY-MM-DD HH:MM:SS。[/bold red]"
        )


def get_all_feedbacks():
    with console.status(
        "[bold green]正在查询用户反馈...[/bold green]", spinner="dots"
    ):
        try:
            resp = requests.get(f"{BASE_URL}/feedbacks/")
            resp.raise_for_status()
            print_table(resp.json(), "所有用户反馈")
        except requests.RequestException as e:
            console.print(f"[bold red]查询失败: {e}[/bold red]")


def add_feedback():
    try:
        user_id = Prompt.ask("[cyan]请输入用户ID[/cyan]")
        content = Prompt.ask("[cyan]请输入反馈内容[/cyan]")
        feedback_type = Prompt.ask("[cyan]请输入反馈类型[/cyan]")
        device_id = Prompt.ask("[cyan]请输入关联设备ID (可留空)[/cyan]")
        with console.status("[bold green]正在添加反馈...[/bold green]"):
            payload = {
                "user_id": int(user_id),
                "content": content,
                "feedback_type": feedback_type,
                "device_id": int(device_id) if device_id else None,
                "timestamp": datetime.now().isoformat()
            }
            resp = requests.post(f"{BASE_URL}/feedbacks/", json=payload)
            resp.raise_for_status()
            print_table(resp.json(), "新增反馈成功")
    except requests.RequestException as e:
        console.print(
            f"[bold red]添加失败: "
            f"{e.response.text if e.response else e}[/bold red]"
        )
    except ValueError:
        console.print("[bold red]输入错误: 用户ID和设备ID必须是数字。[/bold red]")


def get_analysis(endpoint, filename):
    with console.status(
        f"[bold green]正在获取分析结果: {endpoint}...[/bold green]",
        spinner="dots"
    ):
        try:
            resp = requests.get(f"{BASE_URL}/analysis/{endpoint}")
            resp.raise_for_status()
            content_type = resp.headers.get('content-type', '')

            if "image" in content_type:
                with open(filename, 'wb') as f:
                    f.write(resp.content)
                console.print(
                    f"[bold green]✔ 分析图片已保存为 "
                    f"[underline]{filename}[/underline][/bold green]"
                )
                try:
                    if os.name == "nt":
                        os.startfile(filename)
                    elif sys.platform == "darwin":
                        os.system(f"open {filename}")
                    else:
                        os.system(f"xdg-open {filename}")
                except Exception:
                    console.print("[yellow]无法自动打开图片, 请手动查看。[/yellow]")
            elif "application/json" in content_type:
                data = resp.json()
                if 'data' in data:
                    print_table(data['data'], title=f"分析结果: {endpoint}")
                else:
                    console.print(
                        f"[bold red]分析出错: "
                        f"{data.get('error', '未知错误')}[/bold red]"
                    )
            else:
                console.print(
                    f"[bold red]错误: 收到未知的响应类型 "
                    f"({content_type})。[/bold red]"
                )

        except requests.RequestException as e:
            console.print(f"[bold red]请求分析接口失败: {e}[/bold red]")


def choose_model():
    console.print("\n[bold]请选择要使用的AI模型:[/bold]")
    console.print("[cyan]1.[/cyan] DeepSeek (默认, 推荐)")
    console.print("[cyan]2.[/cyan] Qwen (通义千问)")
    choice = Prompt.ask(
        "[bold]请输入选项[/bold]", choices=["1", "2"], default="1"
    )
    return "deepseek" if choice == "1" else "qwen"


def nlp_query_mode(model_provider: str):
    clear()
    console.print(
        f"您已进入 [bold green]智能问答模式[/bold green] "
        f"(模型: [cyan]{model_provider}[/cyan])\n"
        "[dim]此模式拥有短期记忆，可进行多轮对话。[/dim]\n"
        "[dim]输入 'exit' 或 'quit' 返回主菜单。[/dim]\n"
    )

    messages = []

    while True:
        try:
            user_input = Prompt.ask(f"[bold {MAGENTA}]You[/bold {MAGENTA}]")
            if user_input.lower() in ["exit", "quit"]:
                break
            if not user_input.strip():
                continue

            messages.append({"role": "user", "content": user_input})

            payload = {"messages": messages, "model": model_provider}

            with console.status(
                "[cyan]大模型正在思考中，请稍候...", spinner="bouncingBall"
            ):
                resp = requests.post(
                    f"{BASE_URL}/nlp/", json=payload, timeout=60
                )
                resp.raise_for_status()
                result = resp.json()

            # --- AI Response Processing ---
            answer = result.get("answer", "")
            data = result.get("data")
            sql = result.get("sql")

            console.print(
                f"\n[bold {GREEN}]AI Agent[/bold {GREEN}]"
                f"[dim] (SQL: {sql or 'N/A'})[/dim]"
            )

            if data is not None:
                # If we get data, display it and add to memory
                print_table(data, title="查询结果")
                data_str = str(data)
                if len(data_str) > 500:
                    data_str = data_str[:500] + "...(结果已截断)"
                observation_message = f"【系统查询结果】:\n{data_str}"
                messages.append(
                    {"role": "assistant", "content": observation_message}
                )
                console.print(
                    Panel(
                        "已将查询结果加入到短期记忆中，您可以继续追问。",
                        title="[cyan]记忆增强[/cyan]",
                        style="dim"
                    )
                )

            elif result.get("suggestion"):
                # If it's a suggestion from the LLM
                console.print(
                    Panel(
                        result["suggestion"],
                        title="[yellow]模型建议[/yellow]",
                        border_style="yellow"
                    )
                )

            elif result.get("error"):
                console.print(Panel(
                    f"执行时发生错误: {result.get('error')}",
                    title="[bold red]错误[/bold red]",
                    border_style="red",
                    subtitle=f"Raw: {result.get('raw')}"
                ))

            else:
                # Fallback for any other response
                console.print(Panel(answer, title="[green]AI回复[/green]"))

            console.print("")

        except requests.RequestException as e:
            console.print(f"\n[bold red]请求AI服务失败: {e}[/bold red]")
        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"\n[bold red]发生未知错误: {e}[/bold red]")


def nlp_analysis_mode(model_provider: str):
    clear()
    console.print(
        f"您已进入 [bold magenta]智能分析模式[/bold magenta] "
        f"(模型: [cyan]{model_provider}[/cyan])\n"
        "[dim]此模式是更强大的AI代理, 会自主决策生成图表或返回数据。[/dim]\n"
        "[dim]输入 'exit' 或 'quit' 返回主菜单。[/dim]\n"
    )
    messages = []

    while True:
        try:
            user_input = Prompt.ask(f"[bold {MAGENTA}]You[/bold {MAGENTA}]")
            if user_input.lower() in ["exit", "quit"]:
                break
            if not user_input.strip():
                continue

            # Add user message to history
            messages.append({"role": "user", "content": user_input})
            payload = {"messages": messages, "model": model_provider}
            dataframe_for_explanation = None

            with console.status(
                "[cyan]AI正在深度分析并决策中...", spinner="bouncingBall"
            ):
                resp = requests.post(
                    f"{BASE_URL}/nlp/", json=payload, timeout=60
                )
                resp.raise_for_status()
                result = resp.json()

            # --- AI Response Processing ---
            action = result.get("action")
            data = result.get("data")
            title = result.get("title", "AI分析结果")

            console.print(f"\n[bold {GREEN}]AI Agent[/bold {GREEN}]")

            # Case 1: AI decided to visualize
            if action == "visualize" and data:
                df = pd.DataFrame(data)
                dataframe_for_explanation = df
                if is_suitable_for_chart(df):
                    console.print(Panel(
                        f"数据分析完成, [bold green]尝试生成可视化图表[/bold green]\n"
                        f"标题: [cyan]{title}[/cyan]",
                        title="[bold]分析结果[/bold]"
                    ))
                    plot_data(df, title)
                else:
                    console.print(Panel(
                        "[bold blue]数据不适合图表展示, 将以表格形式显示[/bold blue]",
                        title="[bold]分析结果[/bold]"
                    ))
                    display_dataframe(df, title)

            # Case 2: AI returned a suggestion or simple data (not for vis)
            elif result.get("suggestion"):
                console.print(
                    Panel(
                        result["suggestion"],
                        title="[yellow]模型建议[/yellow]",
                        border_style="yellow"
                    )
                )

            # Case 3: Error occurred
            elif result.get("error"):
                console.print(Panel(
                    f"执行时发生错误: {result.get('error')}",
                    title="[bold red]错误[/bold red]",
                    border_style="red"
                ))

            # Add observation to memory for next turn
            if action == "visualize":
                messages.append({"role": "assistant",
                                 "content": f"【系统观察结果】: "
                                 f"已为用户生成标题为'{title}'的图表。"})
            elif data:
                data_str = str(data)
                if len(data_str) > 1000:
                    data_str = data_str[:1000] + "... (结果已截断)"
                messages.append(
                    {"role": "assistant",
                     "content": f"【系统查询结果】:\n{data_str}"}
                )

            # Ask for text-based explanation if a chart was produced
            if dataframe_for_explanation is not None and \
               not dataframe_for_explanation.empty:
                ask_for_explanation = Prompt.ask(
                    "\n[bold yellow]需要AI为您进一步解读这份数据吗？(Y/n)[/bold yellow]",
                    default="y", choices=["y", "n"], show_choices=False
                )
                if ask_for_explanation.lower() == 'y':
                    with console.status(
                        "[bold green]🤖 AI数据分析师正在撰写解读报告...[/bold green]",
                        spinner="bouncingBall"
                    ):
                        try:
                            # Create a new, specific request for explanation
                            df_for_csv = dataframe_for_explanation.head(20)
                            df_csv_string = df_for_csv.to_csv(index=False)
                            explain_messages = [
                                {
                                    "role": "system",
                                    "content": (
                                        "你是一名专业的数据分析师。请根据下方给出的数据表和分析背景，"
                                        "提炼出主要结论、趋势、异常和建议。请用简洁、"
                                        "专业的中文自然语言输出，不要输出SQL或代码。"
                                    )
                                },
                                {
                                    "role": "user",
                                    "content": (
                                        f"【分析背景】\n{user_input}\n\n"
                                        f"【数据表】\n{df_csv_string}"
                                    )
                                }
                            ]
                            resp2 = requests.post(
                                f"{BASE_URL}/nlp/",
                                json={"messages": explain_messages,
                                      "model": model_provider}
                            )
                            explanation = resp2.json().get(
                                "suggestion") or resp2.json().get(
                                "answer") or "未能获取AI解读。"
                            console.print(Panel(
                                explanation,
                                title="[bold green]🤖 AI数据分析师解读[/bold green]",
                                border_style="green",
                                expand=True
                            ))
                        except Exception as e:
                            console.print(f"[dim]获取AI解读失败: {e}[/dim]")

            console.print("")

        except requests.RequestException as e:
            console.print(f"\n[bold red]请求AI服务失败: {e}[/bold red]")
        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"\n[bold red]发生未知错误: {e}[/bold red]")


class SQLCompleter(Completer):
    def __init__(self, schema: dict):
        self.schema = schema
        self.all_keywords = [
            'SELECT', 'FROM', 'WHERE', 'INSERT', 'INTO', 'VALUES', 'UPDATE',
            'SET', 'DELETE', 'LIMIT', 'ORDER', 'BY', 'GROUP', 'ASC', 'DESC',
            'JOIN', 'ON', 'AS', 'AND', 'OR', 'NOT', 'IN', 'LIKE', 'IS', 'NULL'
        ]
        self.tables = list(self.schema.keys())
        self.columns = [col for cols in self.schema.values() for col in cols]

    def get_completions(self, document: Document, complete_event):
        text = document.text_before_cursor.upper()
        word_before_cursor = document.get_word_before_cursor(WORD=True).upper()

        suggestions = self._get_contextual_suggestions(text)

        for keyword in suggestions:
            if keyword.upper().startswith(word_before_cursor):
                yield Completion(
                    keyword,
                    start_position=-len(word_before_cursor),
                    display_meta=self.get_meta(keyword)
                )

    def _get_contextual_suggestions(self, text: str) -> list:
        words = text.split()
        if not words:
            return self.all_keywords

        # Very simple context detection
        try:
            # Pop the last word and analyze context from the one before it
            if len(words) > 1:
                context_word = words[-2]
            else:
                context_word = ''

            if context_word in ['FROM', 'JOIN', 'UPDATE', 'INTO']:
                # After FROM/JOIN etc., suggest table names
                return self.tables
            elif context_word in ['WHERE', 'ON', 'AND', 'OR', 'BY', 'SET',
                                  'SELECT']:
                # After WHERE, ON etc., suggest column names and keywords
                suggestions = self.columns + self.all_keywords
                return suggestions
            elif context_word in self.tables:
                # After a table name, suggest column names
                return self.schema.get(context_word, [])
            else:
                return self.all_keywords
        except IndexError:
            return self.all_keywords

    def get_meta(self, word: str) -> str:
        if word.upper() in self.all_keywords:
            return 'Keyword'
        if word in self.tables:
            return 'Table'
        if word in self.columns:
            return 'Column'
        return ''


def sql_query_cli():
    """CLI for direct SQL queries with autocompletion."""
    schema = {}
    completer = None
    session = PromptSession(complete_while_typing=True)  # Fallback session

    try:
        with console.status("[bold green]正在获取数据库Schema用于自动补全..."):
            resp = requests.get(f"{BASE_URL}/api/schema_for_completion")
            if resp.status_code == 200:
                schema = resp.json()
                completer = SQLCompleter(schema)
                session = PromptSession(
                    completer=completer, complete_while_typing=True
                )
                console.print("[bold green]✔ Schema获取成功, SQL自动补全已激活。")
            else:
                console.print(
                    f"[yellow]无法获取Schema (HTTP {resp.status_code}), "
                    "自动补全不可用。[/yellow]"
                )
    except requests.RequestException as e:
        console.print(f"[yellow]无法连接到服务器 ({e}), 自动补全不可用。[/yellow]")

    console.print(Panel(
        "[bold yellow]进入SQL查询模式, 输入 'exit' 或 'quit' 返回。[/bold yellow]\n"
        "[dim]示例: SELECT * FROM users LIMIT 5;[/dim]"
    ))

    while True:
        try:
            sql = session.prompt("SQL> ")
            if sql.lower().strip() in ["exit", "quit"]:
                break
            if not sql.strip():
                continue

            with console.status("[bold green]正在执行SQL..."):
                resp = requests.post(
                    f"{BASE_URL}/api/sql_query", json={"sql": sql}
                )
                resp.raise_for_status()
            data = resp.json()

            if data.get("success"):
                print_table(data.get("data", []), "SQL查询结果")
            else:
                console.print(
                    f"[bold red]查询失败: "
                    f"{data.get('error', '未知错误')}[/bold red]"
                )

        except requests.RequestException as e:
            console.print(f"[bold red]请求失败: {e}[/bold red]")
        except KeyboardInterrupt:
            break
        except EOFError:
            break


def main():
    try:
        while True:
            clear()
            print_welcome_message()
            print_menu()
            try:
                choice = Prompt.ask(
                    "[bold]请选择操作[/bold]",
                    choices=[str(i) for i in range(22)],
                    show_choices=False
                )
            except KeyboardInterrupt:
                break

            actions = {
                "1": get_all_users, "2": add_user, "3": get_all_devices,
                "4": add_device, "5": get_all_usages, "6": add_usage,
                "7": get_all_events, "8": add_event, "9": get_all_feedbacks,
                "10": add_feedback,
                "11": lambda: get_analysis(
                    "device_usage_frequency", "device_usage_frequency.png"
                ),
                "12": lambda: get_analysis("user_habits", "user_habits.png"),
                "13": lambda: get_analysis("area_impact", "area_impact.png"),
                "14": lambda: get_analysis(
                    "device_type_usage", "device_type_usage.png"
                ),
                "15": lambda: get_analysis("room_energy", "room_energy.png"),
                "16": lambda: get_analysis(
                    "user_activity", "user_activity.png"
                ),
                "17": lambda: get_analysis(
                    "room_event_count", "room_event_count.png"
                ),
                "18": lambda: get_analysis(
                    "daily_device_usage", "daily_device_usage.png"
                ),
                "19": lambda: nlp_query_mode(choose_model()),
                "20": lambda: nlp_analysis_mode(choose_model()),
                "21": sql_query_cli,
                "0": lambda: sys.exit(
                    console.print("[bold cyan]感谢使用, 再见！[/bold cyan]")
                )
            }

            action = actions.get(choice)
            if action:
                clear()
                action()
                if choice != '0':
                    console.print("\n[bold cyan]继续操作或输入 '0' 退出...[/bold cyan]")
                    Prompt.ask("按 Enter 继续...")
            else:
                console.print(f"[bold red]无效选项: {choice}[/bold red]")

    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        console.print("\n[bold cyan]程序已退出。[/bold cyan]")
        sys.exit(0)


if __name__ == "__main__":
    main()
