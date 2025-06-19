from contextlib import asynccontextmanager
from fastapi import FastAPI, Response, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src import models, schemas
from src.database import init_db, get_db


INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>KubSU API</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }
        h1 { color: #2c3e50; }
        a { color: #3498db; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .endpoint { background: #f5f5f5; padding: 10px; border-radius: 5px; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>Welcome to KUBSU User API!</h1>
    <p>Available endpoints:</p>

    <div class="endpoint">
        <strong>GET /users/</strong> - Get list of users<br>
        Example: <a href="/users/" target="_blank">/users/</a>
    </div>

    <div class="endpoint">
        <strong>POST /users/</strong> - Create new user<br>
        Use Swagger for testing: <a href="/docs" target="_blank">/docs</a>
    </div>

    <div class="endpoint">
        <strong>GET /users/{id}</strong> - Get user by ID<br>
        Example: <a href="/users/1" target="_blank">/users/1</a>
    </div>

    <p>For full API interface visit <a href="/docs" target="_blank">Swagger UI</a> or <a href="/redoc" target="_blank">ReDoc</a>.</p>
</body>
</html>
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting KubSU API")
    await init_db()
    yield


app = FastAPI(
    title="KubSU API",
    description="KubSU API For User Management",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "kubsu-api",
        "version": "1.0.0",
        "message": "All systems operational!"
    }


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def read_root():
    return HTMLResponse(content=INDEX_HTML, status_code=200)


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return Response(status_code=204)


@app.post("/users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    user = models.User(name=user.name)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@app.get("/users/", response_model=list[schemas.User])
async def read_users(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).offset(skip).limit(limit))
    users = result.scalars().all()
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.patch("/users/{user_id}", response_model=schemas.User)
async def update_user(user_id: int, user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    db_user = result.scalar_one_or_none()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.name = user.name
    await db.commit()
    
    return db_user


@app.delete("/users/{user_id}", response_model=dict)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    db_user = result.scalar_one_or_none()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(db_user)
    await db.commit()
    
    return {"detail": "User deleted"}
