const yearSelect = document.getElementById("year-select");
const yearPill = document.getElementById("year-pill");
const statusText = document.getElementById("status");
const teamList = document.getElementById("team-list");
const teamsStatusText = document.getElementById("teams-status");
let activeTeamsRequest = 0;

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

function fillTeamList(teamNames) {
	teamList.replaceChildren();

	if (teamNames.length === 0) {
		const item = document.createElement("li");
		item.className = "placeholder";
		item.textContent = "No teams found for this season.";
		teamList.appendChild(item);
		return;
	}

	for (const teamName of teamNames) {
		const item = document.createElement("li");
		item.textContent = teamName;
		teamList.appendChild(item);
	}
}

async function loadTeams(year) {
	const requestId = ++activeTeamsRequest;

	if (!year) {
		fillTeamList([]);
		setTeamsStatus("Choose a season to see teams.");
		return;
	}

	teamList.replaceChildren();
	const loadingItem = document.createElement("li");
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

		const teamNames = await response.json();

		if (requestId !== activeTeamsRequest) {
			return;
		}

		if (!Array.isArray(teamNames)) {
			throw new Error("Invalid team list returned from server");
		}

		fillTeamList(teamNames);
		setTeamsStatus(`${teamNames.length} teams loaded for ${year}`);
	} catch (error) {
		if (requestId !== activeTeamsRequest) {
			return;
		}

		console.error(error);
		fillTeamList([]);
		setTeamsStatus("Could not load teams. Try a different season.", true);
	}
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
		fillTeamList([]);
		setTeamsStatus("Teams are unavailable because years could not be loaded.", true);
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
