const API = "http://localhost:8000";

// --- Tabs ---
document.querySelectorAll(".tab").forEach(tab => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
    tab.classList.add("active");
    document.getElementById(tab.dataset.tab + "-tab").classList.add("active");
  });
});

// --- Chat ---
document.getElementById("askBtn").addEventListener("click", async () => {
  const question = document.getElementById("question").value;
  const answerEl = document.getElementById("answer");

  if (!question.trim()) {
    answerEl.innerText = "Please enter a question.";
    return;
  }

  answerEl.innerText = "Loading...";

  try {
    const apiKey = await storageGet("apiKey");
    const headers = { "Content-Type": "application/json" };
    if (apiKey) headers["X-Api-Key"] = apiKey;

    const response = await fetch(`${API}/ask`, {
      method: "POST",
      headers,
      body: JSON.stringify({ question })
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || `Server returned ${response.status}`);
    }

    const data = await response.json();
    answerEl.innerHTML = renderMarkdown(data.answer);
  } catch (error) {
    answerEl.innerText = `Error: ${error.message}`;
  }
});

// --- Settings: API Key ---
const apiKeyInput = document.getElementById("apiKey");
const keyStatus = document.getElementById("keyStatus");

chrome.storage.local.get("apiKey", (data) => {
  if (data.apiKey) {
    apiKeyInput.value = data.apiKey;
    keyStatus.textContent = "Key saved";
    keyStatus.className = "status success";
  }
});

document.getElementById("toggleKey").addEventListener("click", () => {
  apiKeyInput.type = apiKeyInput.type === "password" ? "text" : "password";
});

document.getElementById("saveKey").addEventListener("click", () => {
  const key = apiKeyInput.value.trim();
  chrome.storage.local.set({ apiKey: key }, () => {
    if (chrome.runtime.lastError) {
      keyStatus.textContent = `Error saving key: ${chrome.runtime.lastError.message}`;
      keyStatus.className = "status error";
    } else {
      keyStatus.textContent = key ? "Key saved" : "Key cleared";
      keyStatus.className = "status success";
    }
  });
});

// --- Settings: PDF Upload ---
const dropZone = document.getElementById("dropZone");
const pdfInput = document.getElementById("pdfInput");
const uploadStatus = document.getElementById("uploadStatus");

// Prevent browser from opening dropped files
document.addEventListener("dragover", (e) => e.preventDefault());
document.addEventListener("drop", (e) => e.preventDefault());

dropZone.addEventListener("click", () => pdfInput.click());

dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  e.stopPropagation();
  e.dataTransfer.dropEffect = "copy";
  dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("dragover");
});

dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  e.stopPropagation();
  dropZone.classList.remove("dragover");
  const file = e.dataTransfer.files[0];
  if (file) uploadPdf(file);
});

pdfInput.addEventListener("change", () => {
  if (pdfInput.files[0]) uploadPdf(pdfInput.files[0]);
});

async function uploadPdf(file) {
  if (!file.name.endsWith(".pdf")) {
    uploadStatus.textContent = "Only PDF files are supported";
    uploadStatus.className = "status error";
    return;
  }

  uploadStatus.textContent = `Uploading ${file.name}...`;
  uploadStatus.className = "status loading";

  try {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API}/ingest-pdf`, {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Upload failed");
    }

    uploadStatus.textContent = `Ingested ${data.filename} (${data.chunks_ingested} chunks)`;
    uploadStatus.className = "status success";
    loadDocCount();
  } catch (error) {
    uploadStatus.textContent = `Error: ${error.message}`;
    uploadStatus.className = "status error";
  }
}

// --- Settings: Doc Count & Clear ---
const docCountEl = document.getElementById("docCount");
const clearStatus = document.getElementById("clearStatus");

async function loadDocCount() {
  try {
    const res = await fetch(`${API}/count`);
    const data = await res.json();
    docCountEl.textContent = `${data.documents} chunks in database`;
  } catch {
    docCountEl.textContent = "Could not load count";
  }
}

loadDocCount();

document.getElementById("clearBtn").addEventListener("click", async () => {
  clearStatus.textContent = "Clearing...";
  clearStatus.className = "status loading";

  try {
    await fetch(`${API}/clear`, { method: "DELETE" });
    clearStatus.textContent = "All data cleared";
    clearStatus.className = "status success";
    loadDocCount();
  } catch {
    clearStatus.textContent = "Error clearing data";
    clearStatus.className = "status error";
  }
});

// --- Helpers ---
function storageGet(key) {
  return new Promise((resolve) => {
    chrome.storage.local.get(key, (data) => resolve(data[key]));
  });
}

function renderMarkdown(text) {
  const escaped = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  return escaped
    .replace(/```([\s\S]*?)```/g, "<pre><code>$1</code></pre>")
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*]+)\*/g, "<em>$1</em>")
    .replace(/\n/g, "<br>");
}
