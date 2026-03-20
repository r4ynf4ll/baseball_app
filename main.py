from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from sqlmodel import Session, select
from models import engine, People, Teams, Batting

app = FastAPI()

@app.get("/years")
async def get_years():
    with Session(engine) as session:
        statement = select(Teams.yearid).distinct().order_by(Teams.yearid)
        years = session.exec(statement).all()
    return years

@app.get("/teams")
async def get_teams(year: int):
    with Session(engine) as session:
        statement = (
            select(Teams.name, Teams.lgid, Teams.divid)
            .where(Teams.yearid == year)
            .where(Teams.name.is_not(None))
            .order_by(Teams.name)
        )
        rows = session.exec(statement).all()
    teams = [
        {"name": name, "league": league, "division": division}
        for name, league, division in rows
    ]
    return teams

app.mount("/", StaticFiles(directory="static", html=True),name="static")