const statusMessage = document.querySelector("#status-message");
const summaryCards = document.querySelector("#summary-cards");
const entryList = document.querySelector("#entry-list");
const trendList = document.querySelector("#trend-list");
const form = document.querySelector("#wellness-form");

async function fetchJson(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return response.json();
}

function formatValue(value) {
  return value === null || value === undefined ? "—" : value;
}

function renderSummary(summary) {
  const cards = [
    { label: "Entries", value: summary.count },
    { label: "Mood", value: summary.average_mood?.toFixed(1) },
    { label: "Sleep", value: summary.average_sleep_hours?.toFixed(1) },
    { label: "Exercise", value: summary.average_exercise_minutes?.toFixed(0) },
    { label: "Water", value: summary.average_water_glasses?.toFixed(1) },
    { label: "Meditation", value: summary.average_meditation_minutes?.toFixed(1) },
    { label: "Stress", value: summary.average_stress_level?.toFixed(1) },
  ];

  summaryCards.innerHTML = cards
    .map(
      ({ label, value }) =>
        `<div class="stat-item"><strong>${label}</strong><span>${formatValue(value)}</span></div>`,
    )
    .join("");
}

function renderEntries(entries) {
  if (!entries.length) {
    entryList.innerHTML = "<div class=\"entry-card\">No entries yet. Add one above.</div>";
    return;
  }

  entryList.innerHTML = entries
    .slice(0, 5)
    .map(
      (entry) => `
      <div class="entry-card">
        <strong>${entry.date}</strong>
        <div class="entry-row">
          <span>Mood: ${entry.mood}</span>
          <span>Stress: ${entry.stress_level}</span>
          <span>Sleep: ${entry.sleep_hours}h</span>
          <span>Exercise: ${entry.exercise_minutes} min</span>
          <span>Water: ${entry.water_glasses} glasses</span>
          <span>Meditation: ${entry.meditation_minutes} min</span>
        </div>
        <code>${entry.notes || "No notes added."}</code>
      </div>
    `,
    )
    .join("");
}

function renderTrends(trends) {
  const trendBuckets = [
    { label: "Mood", data: trends.mood },
    { label: "Sleep", data: trends.sleep },
    { label: "Stress", data: trends.stress },
  ];

  trendList.innerHTML = trendBuckets
    .map(({ label, data }) => {
      if (!data.length) {
        return `<div class="trend-card"><strong>${label}</strong><p>No trend data yet.</p></div>`;
      }
      const points = data
        .slice(-5)
        .map(([date, value]) => `<li>${date}: ${value}</li>`)
        .join("");
      return `
        <div class="trend-card">
          <strong>${label}</strong>
          <ul>${points}</ul>
        </div>
      `;
    })
    .join("");
}

async function loadDashboard() {
  try {
    const [entries, summary, trends] = await Promise.all([
      fetchJson("/api/entries"),
      fetchJson("/api/summary"),
      fetchJson("/api/trends"),
    ]);

    renderSummary(summary);
    renderEntries(entries);
    renderTrends(trends);
  } catch (error) {
    statusMessage.textContent = "Unable to load dashboard. Please try again.";
    statusMessage.style.color = "#b91c1c";
    console.error(error);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  statusMessage.textContent = "Saving...";
  statusMessage.style.color = "#2563eb";

  const formData = new FormData(form);
  const payload = {
    mood: Number(formData.get("mood")),
    sleep: Number(formData.get("sleep")),
    exercise: Number(formData.get("exercise")),
    water: Number(formData.get("water")),
    meditation: Number(formData.get("meditation")),
    stress: Number(formData.get("stress")),
    notes: String(formData.get("notes") || ""),
  };

  try {
    const response = await fetch("/api/entries", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "Unable to save entry.");
    }

    await loadDashboard();
    form.reset();
    statusMessage.textContent = "Entry saved successfully!";
    statusMessage.style.color = "#16a34a";
  } catch (error) {
    statusMessage.textContent = error.message;
    statusMessage.style.color = "#b91c1c";
    console.error(error);
  }
});

window.addEventListener("load", loadDashboard);
