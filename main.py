from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from sqlalchemy import select
from sqlmodel import Session
from models import engine, People, Teams, Batting

app = FastAPI()

@app.get("/years")
async def get_years():
    with Session(engine) as session:
        statement = select(Teams.yearid).distinct().order_by(Teams.yearid)
        years = session.exec(statement).all()
        return years


app.mount("/", StaticFiles(directory="static", html=True),name="static")