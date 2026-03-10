const API_BASE = "http://localhost:5050/api";

function setStatus(id, message, isError = false) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = message;
  el.style.color = isError ? "#dc2626" : "#059669";
}

async function postJSON(endpoint, payload) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    throw new Error(detail.detail || response.statusText);
  }
  return response.json();
}

async function getJSON(endpoint) {
  const response = await fetch(`${API_BASE}${endpoint}`);
  if (!response.ok) {
    throw new Error(response.statusText);
  }
  return response.json();
}

document.getElementById("env-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = Object.fromEntries(new FormData(event.target));
  try {
    await postJSON("/save-env", formData);
    setStatus("env-status", "Saved .env successfully");
  } catch (err) {
    setStatus("env-status", err.message, true);
  }
});

document.getElementById("save-context").addEventListener("click", async () => {
  try {
    const json = JSON.parse(document.getElementById("system-context").value);
    await postJSON("/save-system-context", json);
    setStatus("context-status", "system_context.json saved");
  } catch (err) {
    setStatus("context-status", err.message, true);
  }
});

document.getElementById("knowledge-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = Object.fromEntries(new FormData(event.target));
  try {
    await postJSON("/add-knowledge", formData);
    setStatus("knowledge-status", "Markdown saved to knowledge_base/");
    event.target.reset();
  } catch (err) {
    setStatus("knowledge-status", err.message, true);
  }
});

document.getElementById("load-demo").addEventListener("click", async () => {
  try {
    const res = await postJSON("/demo/populate", {});
    if (res.context) {
      document.getElementById("system-context").value = JSON.stringify(res.context, null, 2);
    }
    setStatus("demo-status", "Demo context & knowledge loaded");
  } catch (err) {
    setStatus("demo-status", err.message, true);
  }
});

let logInterval = null;

async function fetchLogs() {
  const output = document.getElementById("command-output");
  try {
    const res = await getJSON("/logs");
    output.textContent = res.logs.join("\n") || "Waiting for output...";
    if (!res.running && logInterval) {
      clearInterval(logInterval);
      logInterval = null;
    }
  } catch (err) {
    output.textContent = `Error: ${err.message}`;
  }
}

function startLogPolling() {
  if (logInterval) clearInterval(logInterval);
  fetchLogs();
  logInterval = setInterval(fetchLogs, 2000);
}

async function runCommand(endpoint) {
  const output = document.getElementById("command-output");
  output.textContent = "Starting...";
  try {
    await postJSON(endpoint, {});
    startLogPolling();
    refreshReadiness();
  } catch (err) {
    output.textContent = `Error: ${err.message}`;
  }
}

document.getElementById("run-rag").addEventListener("click", () => runCommand("/run/rag"));
document.getElementById("run-crew").addEventListener("click", () => runCommand("/run/crew"));
document.getElementById("stop-process").addEventListener("click", async () => {
  const output = document.getElementById("command-output");
  try {
    await postJSON("/stop", {});
    output.textContent = "Process stopped";
    fetchLogs();
  } catch (err) {
    output.textContent = `Error: ${err.message}`;
  }
});

async function refreshProgress() {
  const grid = document.getElementById("progress-grid");
  grid.textContent = "Loading...";
  try {
    const states = await getJSON("/progress");
    grid.innerHTML = "";
    const labels = {
      asset_register: "Asset Inventory",
      risk_register: "Risk Assessment",
      risk_treatment_plan: "Risk Treatment",
      policies: "Policy Writer",
      statement_of_applicability: "Compliance Auditor",
      final_report: "Documentation"
    };
    Object.entries(labels).forEach(([key, label]) => {
      const card = document.createElement("div");
      card.className = `progress-card ${states[key] ? "complete" : ""}`;
      card.innerHTML = `<span>${label}</span><span>${states[key] ? "Done" : "Pending"}</span>`;
      grid.appendChild(card);
    });
  } catch (err) {
    grid.textContent = err.message;
  }
}

async function refreshOutputs() {
  const list = document.getElementById("outputs-list");
  list.textContent = "Loading...";
  try {
    const files = await getJSON("/outputs");
    if (!files.length) {
      list.textContent = "No outputs yet.";
      return;
    }
    list.innerHTML = "";
    files.forEach((file) => {
      const li = document.createElement("li");
      li.textContent = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
      list.appendChild(li);
    });
  } catch (err) {
    list.textContent = err.message;
  }
}

async function refreshReadiness() {
  const container = document.getElementById("readiness-table");
  container.textContent = "Loading...";
  try {
    const statuses = await getJSON("/readiness");
    const rows = Object.entries(statuses).map(([task, status]) => {
      const complete = status.toLowerCase() === "complete";
      return `<tr class="${complete ? "complete" : ""}"><td>${task}</td><td>${status}</td></tr>`;
    }).join("");
    container.innerHTML = `<table><thead><tr><th>Task</th><th>Status</th></tr></thead><tbody>${rows}</tbody></table>`;
  } catch (err) {
    container.textContent = err.message;
  }
}

document.getElementById("refresh-progress").addEventListener("click", refreshProgress);
document.getElementById("refresh-outputs").addEventListener("click", refreshOutputs);
document.getElementById("refresh-readiness").addEventListener("click", refreshReadiness);

refreshProgress();
refreshOutputs();
fetchLogs();
refreshReadiness();
