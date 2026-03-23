from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from sqlalchemy import func
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
            select(Teams.teamid, Teams.name, Teams.lgid, Teams.divid, Teams.w)
            .where(Teams.yearid == year)
            .where(Teams.name.is_not(None))
            .order_by(func.coalesce(Teams.w, -1).desc(), Teams.name)
        )
        rows = session.exec(statement).all()
    teams = [
        {
            "team_id": team_id,
            "name": name,
            "league": league,
            "division": division,
            "wins": wins,
        }
        for team_id, name, league, division, wins in rows
    ]
    return teams

@app.get("/players")
async def get_players(year: int, team: str):
    with Session(engine) as session:
        statement = (
            select(
                People.playerid,
                People.namefirst,
                People.namelast,
                func.coalesce(func.sum(Batting.hr), 0).label("home_runs"),
            )
            .join(Batting, Batting.playerid == People.playerid)
            .join(Teams, (Teams.yearid == Batting.yearid) & (Teams.teamid == Batting.teamid))
            .where(Teams.yearid == year)
            .where(Teams.name == team)
            .where(People.namefirst.is_not(None))
            .where(People.namelast.is_not(None))
            .group_by(People.playerid, People.namefirst, People.namelast)
            .order_by(func.coalesce(func.sum(Batting.hr), 0).desc(), People.namelast, People.namefirst)
        )
        rows = session.exec(statement).all()

    players = [
        {
            "first_name": first_name,
            "last_name": last_name,
            "home_runs": home_runs,
        }
        for _, first_name, last_name, home_runs in rows
    ]
    return players


app.mount("/", StaticFiles(directory="static", html=True),name="static")