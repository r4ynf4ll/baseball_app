from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
from typing import Any, Callable

from sqlalchemy import ForeignKeyConstraint, event
from sqlalchemy.engine import Engine
from sqlmodel import Field, SQLModel, create_engine


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "baseball.db"
PEOPLE_CSV = BASE_DIR / "people.csv"
TEAMS_CSV = BASE_DIR / "teams.csv"
BATTING_CSV = BASE_DIR / "batting.csv"
Parser = Callable[[str], Any]


def parse_str(value: str) -> str | None:
    value = value.strip()
    return value or None


def parse_int(value: str) -> int | None:
    value = value.strip()
    return int(value) if value else None


def parse_float(value: str) -> float | None:
    value = value.strip()
    return float(value) if value else None


def parse_date(value: str) -> date | None:
    value = value.strip()
    return date.fromisoformat(value) if value else None


PEOPLE_COLUMNS: list[tuple[str, str, Parser]] = [
    ("ID", "id", parse_int),
    ("playerID", "playerid", parse_str),
    ("birthYear", "birthyear", parse_int),
    ("birthMonth", "birthmonth", parse_int),
    ("birthDay", "birthday", parse_int),
    ("birthCity", "birthcity", parse_str),
    ("birthCountry", "birthcountry", parse_str),
    ("birthState", "birthstate", parse_str),
    ("deathYear", "deathyear", parse_int),
    ("deathMonth", "deathmonth", parse_int),
    ("deathDay", "deathday", parse_int),
    ("deathCountry", "deathcountry", parse_str),
    ("deathState", "deathstate", parse_str),
    ("deathCity", "deathcity", parse_str),
    ("nameFirst", "namefirst", parse_str),
    ("nameLast", "namelast", parse_str),
    ("nameGiven", "namegiven", parse_str),
    ("weight", "weight", parse_int),
    ("height", "height", parse_int),
    ("bats", "bats", parse_str),
    ("throws", "throws", parse_str),
    ("debut", "debut", parse_date),
    ("bbrefID", "bbrefid", parse_str),
    ("finalGame", "finalgame", parse_date),
    ("retroID", "retroid", parse_str),
]

TEAMS_COLUMNS: list[tuple[str, str, Parser]] = [
    ("yearID", "yearid", parse_int),
    ("lgID", "lgid", parse_str),
    ("teamID", "teamid", parse_str),
    ("franchID", "franchid", parse_str),
    ("divID", "divid", parse_str),
    ("Rank", "rank", parse_int),
    ("G", "g", parse_int),
    ("Ghome", "ghome", parse_int),
    ("W", "w", parse_int),
    ("L", "l", parse_int),
    ("DivWin", "divwin", parse_str),
    ("WCWin", "wcwin", parse_str),
    ("LgWin", "lgwin", parse_str),
    ("WSWin", "wswin", parse_str),
    ("R", "r", parse_int),
    ("AB", "ab", parse_int),
    ("H", "h", parse_int),
    ("2B", "doubles", parse_int),
    ("3B", "triples", parse_int),
    ("HR", "hr", parse_int),
    ("BB", "bb", parse_int),
    ("SO", "so", parse_int),
    ("SB", "sb", parse_int),
    ("CS", "cs", parse_int),
    ("HBP", "hbp", parse_int),
    ("SF", "sf", parse_int),
    ("RA", "ra", parse_int),
    ("ER", "er", parse_int),
    ("ERA", "era", parse_float),
    ("CG", "cg", parse_int),
    ("SHO", "sho", parse_int),
    ("SV", "sv", parse_int),
    ("IPouts", "ipouts", parse_int),
    ("HA", "ha", parse_int),
    ("HRA", "hra", parse_int),
    ("BBA", "bba", parse_int),
    ("SOA", "soa", parse_int),
    ("E", "e", parse_int),
    ("DP", "dp", parse_int),
    ("FP", "fp", parse_float),
    ("name", "name", parse_str),
    ("park", "park", parse_str),
    ("attendance", "attendance", parse_int),
    ("BPF", "bpf", parse_int),
    ("PPF", "ppf", parse_int),
    ("teamIDBR", "teamidbr", parse_str),
    ("teamIDlahman45", "teamidlahman45", parse_str),
    ("teamIDretro", "teamidretro", parse_str),
]

BATTING_COLUMNS: list[tuple[str, str, Parser]] = [
    ("playerID", "playerid", parse_str),
    ("yearID", "yearid", parse_int),
    ("stint", "stint", parse_int),
    ("teamID", "teamid", parse_str),
    ("lgID", "lgid", parse_str),
    ("G", "g", parse_int),
    ("AB", "ab", parse_int),
    ("R", "r", parse_int),
    ("H", "h", parse_int),
    ("2B", "doubles", parse_int),
    ("3B", "triples", parse_int),
    ("HR", "hr", parse_int),
    ("RBI", "rbi", parse_int),
    ("SB", "sb", parse_int),
    ("CS", "cs", parse_int),
    ("BB", "bb", parse_int),
    ("SO", "so", parse_int),
    ("IBB", "ibb", parse_int),
    ("HBP", "hbp", parse_int),
    ("SH", "sh", parse_int),
    ("SF", "sf", parse_int),
    ("GIDP", "gidp", parse_int),
]


class People(SQLModel, table=True):
    __tablename__ = "people"

    playerid: str = Field(primary_key=True)
    id: int | None = None
    birthyear: int | None = None
    birthmonth: int | None = None
    birthday: int | None = None
    birthcity: str | None = None
    birthcountry: str | None = None
    birthstate: str | None = None
    deathyear: int | None = None
    deathmonth: int | None = None
    deathday: int | None = None
    deathcountry: str | None = None
    deathstate: str | None = None
    deathcity: str | None = None
    namefirst: str | None = None
    namelast: str | None = None
    namegiven: str | None = None
    weight: int | None = None
    height: int | None = None
    bats: str | None = None
    throws: str | None = None
    debut: date | None = None
    bbrefid: str | None = None
    finalgame: date | None = None
    retroid: str | None = None


class Teams(SQLModel, table=True):
    __tablename__ = "teams"

    yearid: int = Field(primary_key=True)
    teamid: str = Field(primary_key=True)
    lgid: str | None = None
    franchid: str | None = None
    divid: str | None = None
    rank: int | None = None
    g: int | None = None
    ghome: int | None = None
    w: int | None = None
    l: int | None = None
    divwin: str | None = None
    wcwin: str | None = None
    lgwin: str | None = None
    wswin: str | None = None
    r: int | None = None
    ab: int | None = None
    h: int | None = None
    doubles: int | None = None
    triples: int | None = None
    hr: int | None = None
    bb: int | None = None
    so: int | None = None
    sb: int | None = None
    cs: int | None = None
    hbp: int | None = None
    sf: int | None = None
    ra: int | None = None
    er: int | None = None
    era: float | None = None
    cg: int | None = None
    sho: int | None = None
    sv: int | None = None
    ipouts: int | None = None
    ha: int | None = None
    hra: int | None = None
    bba: int | None = None
    soa: int | None = None
    e: int | None = None
    dp: int | None = None
    fp: float | None = None
    name: str | None = None
    park: str | None = None
    attendance: int | None = None
    bpf: int | None = None
    ppf: int | None = None
    teamidbr: str | None = None
    teamidlahman45: str | None = None
    teamidretro: str | None = None


class Batting(SQLModel, table=True):
    __tablename__ = "batting"
    __table_args__ = (
        ForeignKeyConstraint(["yearid", "teamid"], ["teams.yearid", "teams.teamid"]),
    )

    playerid: str = Field(foreign_key="people.playerid", primary_key=True)
    yearid: int = Field(primary_key=True)
    stint: int = Field(primary_key=True)
    teamid: str
    lgid: str | None = None
    g: int | None = None
    ab: int | None = None
    r: int | None = None
    h: int | None = None
    doubles: int | None = None
    triples: int | None = None
    hr: int | None = None
    rbi: int | None = None
    sb: int | None = None
    cs: int | None = None
    bb: int | None = None
    so: int | None = None
    ibb: int | None = None
    hbp: int | None = None
    sh: int | None = None
    sf: int | None = None
    gidp: int | None = None


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection: Any, _: Any) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def parsed_row(raw_row: dict[str, str], columns: list[tuple[str, str, Parser]]) -> dict[str, Any]:
    return {attribute: parser(raw_row[csv_name]) for csv_name, attribute, parser in columns}


def import_csv(
    engine: Engine,
    model: type[SQLModel],
    csv_path: Path,
    columns: list[tuple[str, str, Parser]],
    batch_size: int = 5000,
) -> int:
    total_rows = 0
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        batch: list[dict[str, Any]] = []
        with engine.begin() as connection:
            for raw_row in reader:
                batch.append(parsed_row(raw_row, columns))
                if len(batch) >= batch_size:
                    connection.execute(model.__table__.insert(), batch)
                    total_rows += len(batch)
                    batch.clear()

            if batch:
                connection.execute(model.__table__.insert(), batch)
                total_rows += len(batch)

    return total_rows


def main() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()

    engine = create_engine(f"sqlite:///{DB_PATH}")
    SQLModel.metadata.create_all(engine)

    counts = {
        "people": import_csv(engine, People, PEOPLE_CSV, PEOPLE_COLUMNS),
        "teams": import_csv(engine, Teams, TEAMS_CSV, TEAMS_COLUMNS),
        "batting": import_csv(engine, Batting, BATTING_CSV, BATTING_COLUMNS),
    }

    print(f"Created {DB_PATH.name}")
    for table_name, row_count in counts.items():
        print(f"{table_name}: {row_count}")


if __name__ == "__main__":
    main()