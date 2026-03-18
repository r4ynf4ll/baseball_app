const yearSelect = document.getElementById("year-select");
const yearPill = document.getElementById("year-pill");
const statusText = document.getElementById("status");

function setStatus(message, isError = false) {
	statusText.textContent = message;
	statusText.classList.toggle("error", isError);
}

function setSelectedYear(year) {
	yearPill.textContent = year || "-";
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
	} catch (error) {
		console.error(error);
		yearSelect.disabled = true;
		setSelectedYear("");
		setStatus("Could not load years. Please refresh and try again.", true);
	}
}

yearSelect.addEventListener("change", () => {
	setSelectedYear(yearSelect.value);
});

document.addEventListener("DOMContentLoaded", loadYears);
