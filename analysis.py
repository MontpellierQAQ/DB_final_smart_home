import io
import matplotlib.pyplot as plt
import pandas as pd
from fastapi import Depends, APIRouter, Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import SessionLocal
import models
import matplotlib
from matplotlib import font_manager
from matplotlib.font_manager import FontProperties
import os

router = APIRouter()

# 自动检测/下载并强制使用SimHei等中文字体
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
    # 自动下载SimHei字体（仅首次）
    simhei_url = 'https://github.com/owent-utils/font/raw/master/simhei.ttf'
    font_path = os.path.join(os.path.dirname(__file__), 'simhei.ttf')
    if not os.path.exists(font_path):
        import requests
        r = requests.get(simhei_url)
        with open(font_path, 'wb') as f:
            f.write(r.content)
font_prop = FontProperties(fname=font_path)
matplotlib.rcParams['font.sans-serif'] = [font_prop.get_name()]
matplotlib.rcParams['axes.unicode_minus'] = False

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/device_usage_frequency")
def device_usage_frequency(db: Session = Depends(get_db)):
    records = db.query(models.DeviceUsage).all()
    if not records:
        return {"error": "No device usage data."}
    df = pd.DataFrame([{
        "device_id": r.device_id,
        "start_time": r.start_time,
        "end_time": r.end_time
    } for r in records])
    freq = df["device_id"].value_counts().sort_index()
    device_map = {d.id: d.name for d in db.query(models.Device).all()}
    freq.index = [device_map.get(i, f"设备{i}") for i in freq.index]
    n = len(freq)
    plt.figure(figsize=(max(8, 0.5*n), 5))
    bars = plt.bar(freq.index, freq.values, color="#36b9cc", edgecolor="#1890ff", linewidth=1.5)
    plt.title("设备使用频率", fontsize=18, color="#17a673", weight="bold", fontproperties=font_prop)
    plt.xlabel("设备", fontsize=14, fontproperties=font_prop)
    plt.ylabel("使用次数", fontsize=14, fontproperties=font_prop)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.xticks(rotation=60, fontsize=10, fontproperties=font_prop)
    for bar, label in zip(bars, freq.index):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), int(bar.get_height()), ha='center', va='bottom', fontsize=10, color="#333", fontproperties=font_prop)
    plt.tight_layout()
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return Response(content=buf.read(), media_type="image/png")

@router.get("/user_habits")
def user_habits(db: Session = Depends(get_db)):
    """
    分析设备同时使用的情况。
    通过SQL查询高效计算重叠时间，并根据结果的复杂度返回JSON表格或PNG热力图。
    """
    sql_query = """
    SELECT
        LEAST(t1.device_id, t2.device_id) AS device_a_id,
        GREATEST(t1.device_id, t2.device_id) AS device_b_id,
        SUM(
            EXTRACT(EPOCH FROM (
                LEAST(COALESCE(t1.end_time, NOW() at time zone 'utc'), COALESCE(t2.end_time, NOW() at time zone 'utc')) -
                GREATEST(t1.start_time, t2.start_time)
            )) / 60
        ) AS total_overlap_minutes
    FROM
        device_usages t1
    JOIN
        device_usages t2 ON t1.user_id = t2.user_id AND t1.id < t2.id
    WHERE
        t1.start_time < COALESCE(t2.end_time, NOW() at time zone 'utc') AND t2.start_time < COALESCE(t1.end_time, NOW() at time zone 'utc')
        AND t1.device_id != t2.device_id
    GROUP BY
        device_a_id,
        device_b_id
    HAVING
        SUM(EXTRACT(EPOCH FROM (LEAST(COALESCE(t1.end_time, NOW() at time zone 'utc'), COALESCE(t2.end_time, NOW() at time zone 'utc')) - GREATEST(t1.start_time, t2.start_time)))) > 0
    ORDER BY
        total_overlap_minutes DESC
    LIMIT 20;
    """
    try:
        results = db.execute(text(sql_query)).mappings().all()
    except Exception as e:
        return {"error": f"数据库查询失败: {e}"}

    if not results:
        return {"error": "未发现任何设备存在同时使用的情况。"}

    device_map = {d.id: d.name for d in db.query(models.Device).all()}

    # 如果结果较少，直接返回JSON表格，信息更清晰
    if len(results) <= 6:
        table_data = []
        for row in results:
            table_data.append({
                "设备A": device_map.get(row['device_a_id'], f"设备{row['device_a_id']}"),
                "设备B": device_map.get(row['device_b_id'], f"设备{row['device_b_id']}"),
                "同时使用总分钟数": round(row['total_overlap_minutes'], 2)
            })
        return {"data": table_data}

    # 如果结果较多，生成热力图
    device_ids = sorted(set(row['device_a_id'] for row in results) | set(row['device_b_id'] for row in results))
    matrix = pd.DataFrame(0.0, index=device_ids, columns=device_ids)
    
    for row in results:
        matrix.loc[row['device_a_id'], row['device_b_id']] = row['total_overlap_minutes']
        matrix.loc[row['device_b_id'], row['device_a_id']] = row['total_overlap_minutes']

    matrix.index = [device_map.get(i, f"设备{i}") for i in matrix.index]
    matrix.columns = [device_map.get(i, f"设备{i}") for i in matrix.columns]

    import seaborn as sns
    plt.figure(figsize=(10, 8))
    # 使用 set_theme 并传入字体参数，避免全局设置被覆盖
    sns.set_theme(style="whitegrid", font=font_prop.get_name())
    # 使用 .1f 格式化浮点数，显示一位小数
    ax = sns.heatmap(matrix, annot=True, fmt=".1f", cmap="YlGnBu", linewidths=.5, cbar_kws={"shrink": .8})
    plt.title("设备同时使用总时长热力图 (分钟)", fontsize=18, color="#17a673", weight="bold", fontproperties=font_prop)
    plt.xlabel("设备", fontsize=14, fontproperties=font_prop)
    plt.ylabel("设备", fontsize=14, fontproperties=font_prop)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return Response(content=buf.read(), media_type="image/png")

@router.get("/area_impact")
def area_impact(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    records = db.query(models.DeviceUsage).all()
    if not users or not records:
        return {"error": "No user or device usage data."}
    user_df = pd.DataFrame([{
        "user_id": u.id,
        "house_area": u.house_area
    } for u in users])
    usage_df = pd.DataFrame([{
        "user_id": r.user_id,
        "device_id": r.device_id
    } for r in records])
    df = pd.merge(usage_df, user_df, on="user_id", how="left")
    bins = [0, 80, 120, float("inf")]
    labels = ["小户型", "中户型", "大户型"]
    df["area_group"] = pd.cut(df["house_area"], bins=bins, labels=labels, right=False)
    area_usage = df.groupby("area_group").size()
    plt.figure(figsize=(7, 4.5))
    bars = plt.bar(area_usage.index, area_usage.values, color=["#36b9cc", "#17a673", "#f6c23e"], edgecolor="#1890ff", linewidth=1.5)
    plt.title("房屋面积对设备使用次数的影响", fontsize=18, color="#17a673", weight="bold", fontproperties=font_prop)
    plt.xlabel("房屋面积分组", fontsize=14, fontproperties=font_prop)
    plt.ylabel("设备使用次数", fontsize=14, fontproperties=font_prop)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    for bar in bars:
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), int(bar.get_height()), ha='center', va='bottom', fontsize=12, color="#333", fontproperties=font_prop)
    plt.tight_layout()
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return Response(content=buf.read(), media_type="image/png")

# 各设备类型的使用次数统计
@router.get("/device_type_usage")
def device_type_usage(db: Session = Depends(get_db)):
    records = db.query(models.DeviceUsage).all()
    devices = db.query(models.Device).all()
    if not records or not devices:
        return {"error": "No device usage or device data."}
    df = pd.DataFrame([{ "device_id": r.device_id } for r in records])
    device_map = {d.id: d.type or "未知类型" for d in devices}
    df["type"] = df["device_id"].map(device_map)
    type_usage = df["type"].value_counts().sort_values(ascending=False)
    plt.figure(figsize=(8, 5))
    bars = plt.bar(type_usage.index, type_usage.values, color="#f6c23e", edgecolor="#1890ff", linewidth=1.5)
    plt.title("各设备类型的使用次数统计", fontsize=18, color="#e67e22", weight="bold", fontproperties=font_prop)
    plt.xlabel("设备类型", fontsize=14, fontproperties=font_prop)
    plt.ylabel("使用次数", fontsize=14, fontproperties=font_prop)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    for bar in bars:
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), int(bar.get_height()), ha='center', va='bottom', fontsize=12, color="#333", fontproperties=font_prop)
    plt.tight_layout()
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return Response(content=buf.read(), media_type="image/png")

# 每个房间下设备的总能耗分布
@router.get("/room_energy")
def room_energy(db: Session = Depends(get_db)):
    usages = db.query(models.DeviceUsage).all()
    devices = db.query(models.Device).all()
    rooms = db.query(models.Room).all()
    if not usages or not devices or not rooms:
        return {"error": "No usage, device or room data."}
    usage_df = pd.DataFrame([
        {"device_id": u.device_id, "energy": u.energy_consumed or 0} for u in usages
    ])
    device_map = {d.id: d.room_id for d in devices}
    room_map = {r.id: r.name for r in rooms}
    usage_df["room_id"] = usage_df["device_id"].map(device_map)
    usage_df["room_name"] = usage_df["room_id"].map(room_map)
    room_energy = usage_df.groupby("room_name")["energy"].sum().sort_values(ascending=False)
    plt.figure(figsize=(8, 5))
    bars = plt.bar(room_energy.index, room_energy.values, color="#17a673", edgecolor="#1890ff", linewidth=1.5)
    plt.title("每个房间下设备的总能耗分布", fontsize=18, color="#17a673", weight="bold", fontproperties=font_prop)
    plt.xlabel("房间", fontsize=14, fontproperties=font_prop)
    plt.ylabel("总能耗 (kWh)", fontsize=14, fontproperties=font_prop)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    for bar in bars:
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{bar.get_height():.2f}", ha='center', va='bottom', fontsize=12, color="#333", fontproperties=font_prop)
    plt.tight_layout()
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return Response(content=buf.read(), media_type="image/png")

# 用户活跃度排行
@router.get("/user_activity")
def user_activity(db: Session = Depends(get_db)):
    usages = db.query(models.DeviceUsage).all()
    users = db.query(models.User).all()
    if not usages or not users:
        return {"error": "No usage or user data."}
    usage_df = pd.DataFrame([{ "user_id": u.user_id } for u in usages])
    user_map = {u.id: u.name for u in users}
    usage_df["user_name"] = usage_df["user_id"].map(user_map)
    activity = usage_df["user_name"].value_counts().sort_values(ascending=False)
    plt.figure(figsize=(8, 5))
    bars = plt.bar(activity.index, activity.values, color="#36b9cc", edgecolor="#1890ff", linewidth=1.5)
    plt.title("用户活跃度排行", fontsize=18, color="#36b9cc", weight="bold", fontproperties=font_prop)
    plt.xlabel("用户", fontsize=14, fontproperties=font_prop)
    plt.ylabel("使用次数", fontsize=14, fontproperties=font_prop)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    for bar in bars:
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), int(bar.get_height()), ha='center', va='bottom', fontsize=12, color="#333", fontproperties=font_prop)
    plt.tight_layout()
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return Response(content=buf.read(), media_type="image/png")

# 各房间安防事件数量分布
@router.get("/room_event_count")
def room_event_count(db: Session = Depends(get_db)):
    events = db.query(models.SecurityEvent).all()
    devices = db.query(models.Device).all()
    rooms = db.query(models.Room).all()
    if not events or not devices or not rooms:
        return {"error": "No event, device or room data."}
    event_df = pd.DataFrame([{ "device_id": e.device_id } for e in events])
    device_map = {d.id: d.room_id for d in devices}
    room_map = {r.id: r.name for r in rooms}
    event_df["room_id"] = event_df["device_id"].map(device_map)
    event_df["room_name"] = event_df["room_id"].map(room_map)
    room_event = event_df["room_name"].value_counts().sort_values(ascending=False)
    plt.figure(figsize=(8, 5))
    bars = plt.bar(room_event.index, room_event.values, color="#e74c3c", edgecolor="#1890ff", linewidth=1.5)
    plt.title("各房间安防事件数量分布", fontsize=18, color="#e74c3c", weight="bold", fontproperties=font_prop)
    plt.xlabel("房间", fontsize=14, fontproperties=font_prop)
    plt.ylabel("安防事件数", fontsize=14, fontproperties=font_prop)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    for bar in bars:
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), int(bar.get_height()), ha='center', va='bottom', fontsize=12, color="#333", fontproperties=font_prop)
    plt.tight_layout()
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return Response(content=buf.read(), media_type="image/png")

# 2024年6月每天的设备使用次数趋势
@router.get("/daily_device_usage")
def daily_device_usage(db: Session = Depends(get_db)):
    usages = db.query(models.DeviceUsage).all()
    if not usages:
        return {"error": "No device usage data."}
    df = pd.DataFrame([{ "start_time": u.start_time } for u in usages if u.start_time is not None])
    if df.empty:
        return {"error": "No valid usage data."}
    df["date"] = pd.to_datetime(df["start_time"]).dt.date
    # 仅统计2024年6月
    df = df[(df["date"] >= pd.to_datetime("2024-06-01").date()) & (df["date"] <= pd.to_datetime("2024-06-30").date())]
    daily = df["date"].value_counts().sort_index()
    plt.figure(figsize=(10, 5))
    plt.plot(daily.index.astype(str), daily.values, marker="o", color="#1890ff", linewidth=2)
    plt.title("2024年6月每天的设备使用次数趋势", fontsize=18, color="#1890ff", weight="bold", fontproperties=font_prop)
    plt.xlabel("日期", fontsize=14, fontproperties=font_prop)
    plt.ylabel("使用次数", fontsize=14, fontproperties=font_prop)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    for x, y in zip(daily.index, daily.values):
        plt.text(str(x), y, int(y), ha='center', va='bottom', fontsize=12, color="#333", fontproperties=font_prop)
    plt.tight_layout()
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return Response(content=buf.read(), media_type="image/png")