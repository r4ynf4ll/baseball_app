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
            "player_id": player_id,
            "first_name": first_name,
            "last_name": last_name,
            "home_runs": home_runs,
        }
        for player_id, first_name, last_name, home_runs in rows
    ]
    return players


@app.get("/player-profile")
async def get_player_profile(player_id: str):
    with Session(engine) as session:
        person_statement = select(People).where(People.playerid == player_id)
        person = session.exec(person_statement).first()

        if person is None:
            return {"bio": None, "career_stats": []}

        stats_statement = (
            select(
                Batting.yearid,
                func.group_concat(func.distinct(Teams.name)).label("teams"),
                func.coalesce(func.sum(Batting.g), 0).label("games"),
                func.coalesce(func.sum(Batting.ab), 0).label("at_bats"),
                func.coalesce(func.sum(Batting.r), 0).label("runs"),
                func.coalesce(func.sum(Batting.h), 0).label("hits"),
                func.coalesce(func.sum(Batting.doubles), 0).label("doubles"),
                func.coalesce(func.sum(Batting.triples), 0).label("triples"),
                func.coalesce(func.sum(Batting.hr), 0).label("home_runs"),
                func.coalesce(func.sum(Batting.rbi), 0).label("rbi"),
                func.coalesce(func.sum(Batting.bb), 0).label("walks"),
                func.coalesce(func.sum(Batting.so), 0).label("strikeouts"),
                func.coalesce(func.sum(Batting.sb), 0).label("stolen_bases"),
            )
            .join(Teams, (Teams.yearid == Batting.yearid) & (Teams.teamid == Batting.teamid))
            .where(Batting.playerid == player_id)
            .group_by(Batting.yearid)
            .order_by(Batting.yearid)
        )
        stat_rows = session.exec(stats_statement).all()

    full_name = " ".join(
        part for part in [person.namefirst, person.namelast] if isinstance(part, str) and part.strip()
    )

    bio = {
        "player_id": person.playerid,
        "full_name": full_name or person.playerid,
        "birth_year": person.birthyear,
        "birth_month": person.birthmonth,
        "birth_day": person.birthday,
        "birth_city": person.birthcity,
        "birth_state": person.birthstate,
        "birth_country": person.birthcountry,
        "bats": person.bats,
        "throws": person.throws,
        "height": person.height,
        "weight": person.weight,
        "debut": person.debut.isoformat() if person.debut else None,
        "final_game": person.finalgame.isoformat() if person.finalgame else None,
    }

    career_stats = [
        {
            "year": year,
            "teams": teams,
            "games": games,
            "at_bats": at_bats,
            "runs": runs,
            "hits": hits,
            "doubles": doubles,
            "triples": triples,
            "home_runs": home_runs,
            "rbi": rbi,
            "walks": walks,
            "strikeouts": strikeouts,
            "stolen_bases": stolen_bases,
        }
        for (
            year,
            teams,
            games,
            at_bats,
            runs,
            hits,
            doubles,
            triples,
            home_runs,
            rbi,
            walks,
            strikeouts,
            stolen_bases,
        ) in stat_rows
    ]

    return {"bio": bio, "career_stats": career_stats}


app.mount("/", StaticFiles(directory="static", html=True),name="static")