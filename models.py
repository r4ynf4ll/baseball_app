from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from sqlalchemy import ForeignKeyConstraint, event
from sqlalchemy.engine import Engine
from sqlmodel import Field, SQLModel, create_engine


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


BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = f"sqlite:///{BASE_DIR / 'baseball.db'}"


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection: Any, _: Any) -> None:
	cursor = dbapi_connection.cursor()
	cursor.execute("PRAGMA foreign_keys=ON")
	cursor.close()


engine = create_engine(
	DATABASE_URL,
	connect_args={"check_same_thread": False},
)


def create_db_and_tables() -> None:
	SQLModel.metadata.create_all(engine)
