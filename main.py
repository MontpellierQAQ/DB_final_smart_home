from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
import schemas
import crud
from database import engine, Base, get_db
from analysis import router as analysis_router
from nlp_query import router as nlp_router

# 创建表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="智能家居数据管理与分析系统API",
    description="提供对智能家居系统数据的CRUD操作、数据分析和自然语言查询功能。",
    version="1.2.0",
)

app.include_router(analysis_router, prefix="/analysis", tags=["数据分析与可视化"])
app.include_router(nlp_router, prefix="/nlp", tags=["智能问答(NLP)"])

# 依赖项：获取数据库会话 - 已移至 database.py


# 用户相关API


@app.post("/users/", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)


@app.get("/users/", response_model=list[schemas.UserOut])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_users(db, skip=skip, limit=limit)


@app.get("/users/{user_id}", response_model=schemas.UserOut)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.put("/users/{user_id}", response_model=schemas.UserOut)
def create_or_update_user(
    user_id: int, user: schemas.UserCreate, db: Session = Depends(get_db)
):
    return crud.create_or_update_user(db, user_id=user_id, user=user)


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return crud.delete_user(db, user_id)

# 房间相关API


@app.post("/rooms/", response_model=schemas.Room)
def create_room(room: schemas.RoomCreate, db: Session = Depends(get_db)):
    return crud.create_room(db, room)


@app.get("/rooms/", response_model=list[schemas.RoomOut])
def read_rooms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_rooms(db, skip=skip, limit=limit)


@app.get("/rooms/{room_id}", response_model=schemas.RoomOut)
def read_room(room_id: int, db: Session = Depends(get_db)):
    db_room = crud.get_room(db, room_id)
    if db_room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    return db_room


@app.delete("/rooms/{room_id}")
def delete_room(room_id: int, db: Session = Depends(get_db)):
    return crud.delete_room(db, room_id)

# 设备相关API


@app.post("/devices/", response_model=schemas.Device)
def create_device(device: schemas.DeviceCreate, db: Session = Depends(get_db)):
    return crud.create_device(db, device)


@app.get("/devices/", response_model=list[schemas.DeviceOut])
def read_devices(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)):
    return crud.get_devices(db, skip=skip, limit=limit)


@app.get("/devices/{device_id}", response_model=schemas.DeviceOut)
def read_device(device_id: int, db: Session = Depends(get_db)):
    db_device = crud.get_device(db, device_id)
    if db_device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return db_device


@app.delete("/devices/{device_id}")
def delete_device(device_id: int, db: Session = Depends(get_db)):
    return crud.delete_device(db, device_id)

# 设备使用记录API


@app.post("/device_usages/", response_model=schemas.DeviceUsage)
def create_device_usage(
    usage: schemas.DeviceUsageCreate, db: Session = Depends(get_db)
):
    return crud.create_device_usage(db, usage)


@app.get("/device_usages/", response_model=list[schemas.DeviceUsage])
def read_device_usages(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return crud.get_device_usages(db, skip=skip, limit=limit)


@app.get("/device_usages/{usage_id}", response_model=schemas.DeviceUsage)
def read_device_usage(usage_id: int, db: Session = Depends(get_db)):
    db_usage = crud.get_device_usage(db, usage_id)
    if db_usage is None:
        raise HTTPException(status_code=404, detail="DeviceUsage not found")
    return db_usage


@app.delete("/device_usages/{usage_id}")
def delete_device_usage(usage_id: int, db: Session = Depends(get_db)):
    return crud.delete_device_usage(db, usage_id)

# 安防事件API


@app.post("/security_events/", response_model=schemas.SecurityEvent)
def create_security_event(
    event: schemas.SecurityEventCreate, db: Session = Depends(get_db)
):
    return crud.create_security_event(db, event)


@app.get("/security_events/", response_model=list[schemas.SecurityEvent])
def read_security_events(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return crud.get_security_events(db, skip=skip, limit=limit)


@app.get("/security_events/{event_id}", response_model=schemas.SecurityEvent)
def read_security_event(event_id: int, db: Session = Depends(get_db)):
    db_event = crud.get_security_event(db, event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="SecurityEvent not found")
    return db_event


@app.delete("/security_events/{event_id}")
def delete_security_event(event_id: int, db: Session = Depends(get_db)):
    return crud.delete_security_event(db, event_id)

# 用户反馈API


@app.post("/feedbacks/", response_model=schemas.Feedback)
def create_feedback(
        feedback: schemas.FeedbackCreate,
        db: Session = Depends(get_db)):
    return crud.create_feedback(db, feedback)


@app.get("/feedbacks/", response_model=list[schemas.Feedback])
def read_feedbacks(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)):
    return crud.get_feedbacks(db, skip=skip, limit=limit)


@app.get("/feedbacks/{feedback_id}", response_model=schemas.Feedback)
def read_feedback(feedback_id: int, db: Session = Depends(get_db)):
    db_feedback = crud.get_feedback(db, feedback_id)
    if db_feedback is None:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return db_feedback


@app.delete("/feedbacks/{feedback_id}", tags=["用户反馈"])
def delete_feedback(feedback_id: int, db: Session = Depends(get_db)):
    return crud.delete_feedback(db, feedback_id)


@app.get("/api/schema_for_completion", tags=["高级功能"])
def get_schema_for_completion(db: Session = Depends(get_db)):
    """
    获取数据库的schema，用于前端自动补全。
    返回一个包含所有表名及其列名的字典。
    """
    try:
        inspector = inspect(engine)
        schema = {}
        table_names = inspector.get_table_names()
        for table_name in table_names:
            columns = inspector.get_columns(table_name)
            schema[table_name] = [col['name'] for col in columns]
        return schema
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取schema失败: {e}")


@app.post("/api/sql_query", tags=["高级功能"])
async def sql_query(payload: dict, db: Session = Depends(get_db)):
    sql = payload.get("sql", "")
    # 只允许SELECT，防止危险操作
    if not sql.strip().lower().startswith("select"):
        return JSONResponse(
            content={"success": False, "error": "只允许SELECT查询！"}
        )
    try:
        result = db.execute(text(sql))
        rows = result.mappings().all()
        return {"success": True, "data": rows}
    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)})


@app.get("/", tags=["系统"])
def read_root():
    return {"message": "欢迎使用智能家居数据管理与分析系统API。请访问 /docs 查看API文档。"}
