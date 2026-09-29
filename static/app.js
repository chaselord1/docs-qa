const docList = document.getElementById("doc-list");
const uploadForm = document.getElementById("upload-form");
const fileInput = document.getElementById("file-input");
const uploadStatus = document.getElementById("upload-status");
const askForm = document.getElementById("ask-form");
const questionInput = document.getElementById("question-input");
const askStatus = document.getElementById("ask-status");
const answerPanel = document.getElementById("answer-panel");
const answerText = document.getElementById("answer-text");
const citationsEl = document.getElementById("citations");
const demoBanner = document.getElementById("demo-banner");
const modal = document.getElementById("citation-modal");
const modalSource = document.getElementById("modal-source");
const modalText = document.getElementById("modal-text");
const modalClose = document.getElementById("modal-close");

async function loadDocuments() {
  const res = await fetch("/api/documents");
  const data = await res.json();
  docList.innerHTML = "";
  data.documents.forEach((name) => {
    const li = document.createElement("li");
    const label = document.createElement("span");
    label.textContent = name;
    const removeBtn = document.createElement("button");
    removeBtn.textContent = "remove";
    removeBtn.onclick = () => removeDocument(name);
    li.appendChild(label);
    li.appendChild(removeBtn);
    docList.appendChild(li);
  });
  demoBanner.classList.toggle("hidden", !data.demo_mode);
}

async function removeDocument(name) {
  await fetch(`/api/documents/${encodeURIComponent(name)}`, { method: "DELETE" });
  loadDocuments();
}

uploadForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const file = fileInput.files[0];
  if (!file) return;
  const formData = new FormData();
  formData.append("file", file);
  uploadStatus.textContent = "uploading...";
  try {
    const res = await fetch("/api/upload", { method: "POST", body: formData });
    if (!res.ok) throw new Error((await res.json()).detail || "upload failed");
    uploadStatus.textContent = "uploaded";
    fileInput.value = "";
    loadDocuments();
  } catch (err) {
    uploadStatus.textContent = err.message;
  }
});

askForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const question = questionInput.value.trim();
  if (!question) return;
  askStatus.textContent = "thinking...";
  answerPanel.classList.add("hidden");
  try {
    const res = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await res.json();
    askStatus.textContent = "";
    answerText.textContent = data.answer;
    citationsEl.innerHTML = "";
    (data.citations || []).forEach((c) => {
      const chip = document.createElement("span");
      chip.className = "citation-chip";
      chip.textContent = `${c.source} p.${c.page}`;
      chip.onclick = () => showCitation(c);
      citationsEl.appendChild(chip);
    });
    answerPanel.classList.remove("hidden");
  } catch (err) {
    askStatus.textContent = "request failed";
  }
});

function showCitation(c) {
  modalSource.textContent = `${c.source} p.${c.page}`;
  modalText.textContent = c.text;
  modal.classList.remove("hidden");
}

modalClose.addEventListener("click", () => modal.classList.add("hidden"));
modal.addEventListener("click", (e) => {
  if (e.target === modal) modal.classList.add("hidden");
});

loadDocuments();
