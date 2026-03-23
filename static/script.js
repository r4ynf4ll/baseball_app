const yearSelect = document.getElementById("year-select");
const yearPill = document.getElementById("year-pill");
const statusText = document.getElementById("status");
const teamList = document.getElementById("team-list");
const teamsStatusText = document.getElementById("teams-status");
const playerList = document.getElementById("player-list");
const playersStatusText = document.getElementById("players-status");
const selectedTeamText = document.getElementById("selected-team");
let activeTeamsRequest = 0;
let activePlayersRequest = 0;
let currentTeams = [];
let selectedTeamName = null;

function normalizeNumber(value, fallback = 0) {
	if (typeof value === "number" && Number.isFinite(value)) {
		return value;
	}

	if (typeof value === "string") {
		const parsed = Number.parseInt(value, 10);
		if (Number.isFinite(parsed)) {
			return parsed;
		}
	}

	return fallback;
}

const LEAGUE_LABELS = {
	AL: "American League",
	NL: "National League",
	AA: "American Association",
	FL: "Federal League",
	PL: "Players League",
	UA: "Union Association",
};

const DIVISION_LABELS = {
	E: "East Division",
	C: "Central Division",
	W: "West Division",
};

const LEAGUE_ORDER = ["AL", "NL", "AA", "FL", "PL", "UA", "UNKNOWN"];
const DIVISION_ORDER = ["E", "C", "W", "NONE"];

function setStatus(message, isError = false) {
	statusText.textContent = message;
	statusText.classList.toggle("error", isError);
}

function setSelectedYear(year) {
	yearPill.textContent = year || "-";
}

function setTeamsStatus(message, isError = false) {
	teamsStatusText.textContent = message;
	teamsStatusText.classList.toggle("error", isError);
}

function setPlayersStatus(message, isError = false) {
	playersStatusText.textContent = message;
	playersStatusText.classList.toggle("error", isError);
}

function setSelectedTeam(teamName) {
	selectedTeamName = teamName;
	selectedTeamText.textContent = teamName
		? `Selected team: ${teamName}`
		: "Select a team to load players.";
}

function formatLeagueLabel(leagueCode) {
	if (!leagueCode) {
		return "Unknown League";
	}

	const normalized = leagueCode.trim().toUpperCase();
	return LEAGUE_LABELS[normalized] || normalized;
}

function formatDivisionLabel(divisionCode) {
	if (!divisionCode) {
		return "No Division";
	}

	const normalized = divisionCode.trim().toUpperCase();
	return DIVISION_LABELS[normalized] || normalized;
}

function normalizeCode(value, fallback) {
	if (typeof value !== "string") {
		return fallback;
	}

	const normalized = value.trim().toUpperCase();
	return normalized || fallback;
}

function codeRank(code, preferredOrder) {
	const rank = preferredOrder.indexOf(code);
	return rank === -1 ? preferredOrder.length : rank;
}

function fillPlayerList(players, emptyMessage = "No players found for this team in that season.") {
	playerList.replaceChildren();

	if (players.length === 0) {
		const placeholder = document.createElement("li");
		placeholder.className = "placeholder";
		placeholder.textContent = emptyMessage;
		playerList.appendChild(placeholder);
		return;
	}

	for (const player of players) {
		const playerItem = document.createElement("li");
		playerItem.className = "player-item";
		playerItem.textContent = `${player.first_name} ${player.last_name} (${player.home_runs} HR)`;
		playerList.appendChild(playerItem);
	}
}

function resetPlayersPanel() {
	activePlayersRequest += 1;
	setSelectedTeam(null);
	fillPlayerList([], "No team selected.");
	setPlayersStatus("Waiting for team selection...");
}

function fillTeamList(teams) {
	teamList.replaceChildren();

	if (teams.length === 0) {
		const placeholder = document.createElement("p");
		placeholder.className = "placeholder";
		placeholder.textContent = "No teams found for this season.";
		teamList.appendChild(placeholder);
		return;
	}

	const grouped = new Map();

	for (const team of teams) {
		const leagueCode = normalizeCode(team.league, "UNKNOWN");
		const divisionCode = normalizeCode(team.division, "NONE");

		if (!grouped.has(leagueCode)) {
			grouped.set(leagueCode, new Map());
		}

		const divisions = grouped.get(leagueCode);
		if (!divisions.has(divisionCode)) {
			divisions.set(divisionCode, []);
		}

		divisions.get(divisionCode).push(team);
	}

	const leagueCodes = [...grouped.keys()].sort((a, b) => {
		const rankDelta = codeRank(a, LEAGUE_ORDER) - codeRank(b, LEAGUE_ORDER);
		if (rankDelta !== 0) {
			return rankDelta;
		}

		return formatLeagueLabel(a).localeCompare(formatLeagueLabel(b));
	});

	for (const leagueCode of leagueCodes) {
		const leagueSection = document.createElement("section");
		leagueSection.className = "league-group";

		const leagueTitle = document.createElement("h3");
		leagueTitle.className = "league-title";
		leagueTitle.textContent = formatLeagueLabel(leagueCode === "UNKNOWN" ? null : leagueCode);
		leagueSection.appendChild(leagueTitle);

		const divisionGrid = document.createElement("div");
		divisionGrid.className = "division-grid";

		const divisions = grouped.get(leagueCode);
		const divisionCodes = [...divisions.keys()].sort((a, b) => {
			const rankDelta = codeRank(a, DIVISION_ORDER) - codeRank(b, DIVISION_ORDER);
			if (rankDelta !== 0) {
				return rankDelta;
			}

			return formatDivisionLabel(a).localeCompare(formatDivisionLabel(b));
		});

		for (const divisionCode of divisionCodes) {
			const divisionSection = document.createElement("section");
			divisionSection.className = "division-group";

			const divisionTitle = document.createElement("h4");
			divisionTitle.className = "division-title";
			divisionTitle.textContent = formatDivisionLabel(divisionCode === "NONE" ? null : divisionCode);

			const teamsInDivision = [...divisions.get(divisionCode)].sort((a, b) => {
				const winsDelta = b.wins - a.wins;
				if (winsDelta !== 0) {
					return winsDelta;
				}

				return a.name.localeCompare(b.name);
			});
			const divisionTeamList = document.createElement("ul");
			divisionTeamList.className = "division-teams";

			for (const team of teamsInDivision) {
				const teamItem = document.createElement("li");
				teamItem.className = "division-team-item";

				const teamButton = document.createElement("button");
				teamButton.type = "button";
				teamButton.className = "team-button";
				if (team.name === selectedTeamName) {
					teamButton.classList.add("is-selected");
				}
				teamButton.textContent = `${team.name} (${team.wins} W)`;
				teamButton.addEventListener("click", () => {
					handleTeamSelection(team.name);
				});

				teamItem.appendChild(teamButton);
				divisionTeamList.appendChild(teamItem);
			}

			divisionSection.appendChild(divisionTitle);
			divisionSection.appendChild(divisionTeamList);
			divisionGrid.appendChild(divisionSection);
		}

		leagueSection.appendChild(divisionGrid);
		teamList.appendChild(leagueSection);
	}
}

async function loadPlayers(year, teamName) {
	const requestId = ++activePlayersRequest;

	if (!year || !teamName) {
		setPlayersStatus("Waiting for team selection...");
		fillPlayerList([]);
		return;
	}

	playerList.replaceChildren();
	const loadingItem = document.createElement("li");
	loadingItem.className = "placeholder";
	loadingItem.textContent = "Loading players...";
	playerList.appendChild(loadingItem);
	setPlayersStatus(`Loading players for ${teamName}...`);

	try {
		const response = await fetch(
			`/players?year=${encodeURIComponent(year)}&team=${encodeURIComponent(teamName)}`,
			{ cache: "no-store" },
		);

		if (!response.ok) {
			throw new Error(`Request failed with status ${response.status}`);
		}

		const players = await response.json();

		if (requestId !== activePlayersRequest) {
			return;
		}

		if (!Array.isArray(players)) {
			throw new Error("Invalid players list returned from server");
		}

		const normalizedPlayers = players.map((player) => {
			if (
				!player ||
				typeof player !== "object" ||
				typeof player.first_name !== "string" ||
				typeof player.last_name !== "string"
			) {
				throw new Error("Invalid player entry returned from server");
			}

			return {
				first_name: player.first_name,
				last_name: player.last_name,
				home_runs: normalizeNumber(player.home_runs),
			};
		});

		fillPlayerList(normalizedPlayers);
		setPlayersStatus(`${normalizedPlayers.length} players loaded for ${teamName}`);
	} catch (error) {
		if (requestId !== activePlayersRequest) {
			return;
		}

		console.error(error);
		fillPlayerList([]);
		setPlayersStatus("Could not load players for that selection.", true);
	}
}

async function loadTeams(year) {
	const requestId = ++activeTeamsRequest;

	currentTeams = [];
	resetPlayersPanel();

	if (!year) {
		fillTeamList([]);
		setTeamsStatus("Choose a season to see teams.");
		return;
	}

	teamList.replaceChildren();
	const loadingItem = document.createElement("p");
	loadingItem.className = "placeholder";
	loadingItem.textContent = "Loading teams...";
	teamList.appendChild(loadingItem);
	setTeamsStatus(`Loading teams for ${year}...`);

	try {
		const response = await fetch(`/teams?year=${encodeURIComponent(year)}`, {
			cache: "no-store",
		});

		if (!response.ok) {
			throw new Error(`Request failed with status ${response.status}`);
		}

		const teams = await response.json();

		if (requestId !== activeTeamsRequest) {
			return;
		}

		if (!Array.isArray(teams)) {
			throw new Error("Invalid team list returned from server");
		}

		const normalizedTeams = teams.map((team) => {
			if (!team || typeof team !== "object" || typeof team.name !== "string") {
				throw new Error("Invalid team entry returned from server");
			}

			return {
				team_id: typeof team.team_id === "string" ? team.team_id : null,
				name: team.name,
				league: typeof team.league === "string" ? team.league : null,
				division: typeof team.division === "string" ? team.division : null,
				wins: normalizeNumber(team.wins),
			};
		});

		currentTeams = normalizedTeams;
		fillTeamList(currentTeams);
		setTeamsStatus(`${normalizedTeams.length} teams loaded for ${year}`);
		setPlayersStatus("Select a team from above to load players.");
	} catch (error) {
		if (requestId !== activeTeamsRequest) {
			return;
		}

		console.error(error);
		fillTeamList([]);
		setTeamsStatus("Could not load teams. Try a different season.", true);
		setPlayersStatus("Players are unavailable because teams could not be loaded.", true);
	}
}

async function handleTeamSelection(teamName) {
	if (!teamName) {
		return;
	}

	setSelectedTeam(teamName);
	fillTeamList(currentTeams);
	await loadPlayers(yearSelect.value, teamName);
}

async function handleYearSelection() {
	setSelectedYear(yearSelect.value);
	await loadTeams(yearSelect.value);
}

function fillYearOptions(years) {
	yearSelect.replaceChildren();

	for (const year of years) {
		const option = document.createElement("option");
		option.value = String(year);
		option.textContent = String(year);
		yearSelect.appendChild(option);
	}
}

async function loadYears() {
	try {
		const response = await fetch("/years");

		if (!response.ok) {
			throw new Error(`Request failed with status ${response.status}`);
		}

		const years = await response.json();

		if (!Array.isArray(years) || years.length === 0) {
			throw new Error("No years returned from server");
		}

		fillYearOptions(years);

		const latestYear = String(years[years.length - 1]);
		yearSelect.value = latestYear;
		setSelectedYear(latestYear);

		yearSelect.disabled = false;
		setStatus(`${years.length} seasons loaded`);
		await loadTeams(latestYear);
	} catch (error) {
		console.error(error);
		yearSelect.disabled = true;
		setSelectedYear("");
		currentTeams = [];
		fillTeamList([]);
		resetPlayersPanel();
		setTeamsStatus("Teams are unavailable because years could not be loaded.", true);
		setPlayersStatus("Players are unavailable because years could not be loaded.", true);
		setStatus("Could not load years. Please refresh and try again.", true);
	}
}

yearSelect.addEventListener("change", () => {
	handleYearSelection();
});

yearSelect.addEventListener("input", () => {
	handleYearSelection();
});

document.addEventListener("DOMContentLoaded", loadYears);
