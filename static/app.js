/**
 * Frontend Application Logic for Haqdarshak Scheme AI Citizen FAQ Assistant
 * Focused strictly on user needs:
 * - Scheme record viewing (6-part format)
 * - 8-10 Curated bilingual FAQs
 * - Interactive Citizen Q&A
 * - Low-literacy simple mode
 * - Clean source attribution
 */

let currentSchemeId = "SCHEME-CENTRAL-PMK-001";
let currentLanguage = "en";
let isSimpleMode = false;
let currentSchemeData = null;
let currentFaqs = [];
let activeFieldFilter = "all";
let isSidebarOpen = true;

// DOM Elements
const schemeSelect = document.getElementById("schemeSelect");
const langToggle = document.getElementById("langToggle");
const modeToggle = document.getElementById("modeToggle");
const modeText = document.getElementById("modeText");
const schemeOverviewCard = document.getElementById("schemeOverviewCard");
const fieldsList = document.getElementById("fieldsList");
const faqPresets = document.getElementById("faqPresets");
const chatMessages = document.getElementById("chatMessages");
const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const sendBtn = document.getElementById("sendBtn");
const toggleSidebarBtn = document.getElementById("toggleSidebarBtn");
const sidebarBtnText = document.getElementById("sidebarBtnText");
const mainLayout = document.getElementById("mainLayout");

// Filter count elements
const countAll = document.getElementById("countAll");
const countFound = document.getElementById("countFound");
const countNotFound = document.getElementById("countNotFound");

// Initialization
document.addEventListener("DOMContentLoaded", async () => {
  setupEventListeners();
  await loadSchemeData(currentSchemeId);
  await loadFaqs(currentSchemeId);
  renderWelcomeMessage();
});

function setupEventListeners() {
  // Scheme Switcher
  schemeSelect.addEventListener("change", async (e) => {
    currentSchemeId = e.target.value;
    await loadSchemeData(currentSchemeId);
    await loadFaqs(currentSchemeId);
    renderWelcomeMessage();
  });

  // Language Toggle
  langToggle.querySelectorAll(".segment-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      langToggle.querySelectorAll(".segment-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      currentLanguage = btn.dataset.lang;
      updateLanguageUI();
    });
  });

  // Mode Toggle (Standard vs Low-Literacy)
  modeToggle.addEventListener("click", () => {
    isSimpleMode = !isSimpleMode;
    modeToggle.classList.toggle("active", isSimpleMode);
    modeText.textContent = isSimpleMode
      ? (currentLanguage === "hi" ? "आसान भाषा चालू" : "Simple Mode: ON")
      : (currentLanguage === "hi" ? "आसान भाषा" : "Simple Mode");
  });

  // Toggle Sidebar
  toggleSidebarBtn.addEventListener("click", () => {
    isSidebarOpen = !isSidebarOpen;
    mainLayout.classList.toggle("sidebar-collapsed", !isSidebarOpen);
    sidebarBtnText.textContent = isSidebarOpen ? "Hide Scheme Details" : "Show Scheme Details";
  });

  // Chat Form Submit
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = chatInput.value.trim();
    if (!query) return;
    chatInput.value = "";
    await sendChatMessage(query);
  });

  // Field Filter Chips
  document.querySelectorAll(".chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      document.querySelectorAll(".chip").forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");
      activeFieldFilter = chip.dataset.filter;
      renderSchemeFields();
    });
  });
}

function updateLanguageUI() {
  modeText.textContent = isSimpleMode
    ? (currentLanguage === "hi" ? "आसान भाषा चालू" : "Simple Mode: ON")
    : (currentLanguage === "hi" ? "आसान भाषा" : "Simple Mode");

  chatInput.placeholder = currentLanguage === "hi"
    ? "हिंदी या अंग्रेजी में कोई भी प्रश्न पूछें (उदा. 'क्या मैं पात्र हूँ?' / 'कौन से दस्तावेज चाहिए?')..."
    : "Ask any question in English or Hindi (e.g., 'Am I eligible if...' / 'What documents do I need?')...";

  document.getElementById("faqHeaderTitle").textContent = currentLanguage === "hi"
    ? "अक्सर पूछे जाने वाले प्रश्न (FAQs)"
    : "Frequently Asked Questions";

  renderFaqChips();
}

/**
 * Load Scheme Record from backend API
 */
async function loadSchemeData(schemeId) {
  try {
    const res = await fetch(`/api/schemes/${schemeId}`);
    if (!res.ok) throw new Error("Failed to load scheme");
    currentSchemeData = await res.json();
    renderSchemeOverview();
    renderSchemeFields();
  } catch (err) {
    console.error("Error loading scheme:", err);
    schemeOverviewCard.innerHTML = `<p class="field-empty">Error loading scheme record: ${err.message}</p>`;
  }
}

/**
 * Render Scheme Overview Card
 */
function renderSchemeOverview() {
  if (!currentSchemeData) return;
  const s = currentSchemeData;
  schemeOverviewCard.innerHTML = `
    <div class="scheme-title-box">
      <h3>${s.scheme_name}</h3>
      <div class="scheme-meta-row">
        <span><strong>Type:</strong> ${s.state_or_central}</span>
        <span><strong>Scope:</strong> ${s.state_name || "All India"}</span>
        <span><strong>Approved:</strong> ${s.last_approved_date}</span>
      </div>
    </div>
  `;
  document.getElementById("schemeMetaPill").textContent = `v${s.version} · Approved`;
}

/**
 * Render 6-Part Scheme Fields
 */
function renderSchemeFields() {
  if (!currentSchemeData || !currentSchemeData.fields) return;
  const fields = currentSchemeData.fields;

  // Update counts
  const found = fields.filter((f) => f.status === "found").length;
  const notFound = fields.filter((f) => f.status === "not found").length;
  countAll.textContent = fields.length;
  countFound.textContent = found;
  countNotFound.textContent = notFound;

  // Filter
  const filtered = fields.filter((f) => {
    if (activeFieldFilter === "found") return f.status === "found";
    if (activeFieldFilter === "not_found") return f.status === "not found";
    return true;
  });

  fieldsList.innerHTML = filtered.map((f) => {
    const isFound = f.status === "found";
    return `
      <div class="field-card" data-field="${f.field}">
        <div class="field-card-header">
          <span class="field-name">${f.field}</span>
          <span class="field-status ${isFound ? "status-found" : "status-not-found"}">
            ${f.status}
          </span>
        </div>
        <div class="field-value">
          ${isFound ? f.value : `<span class="field-empty">Not specified in official source</span>`}
        </div>
        <div class="field-evidence-box">
          <strong>Source:</strong> ${f.evidence}
        </div>
        <div class="field-meta-row">
          <span>Confidence: <strong>${f.confidence}</strong></span>
          ${f.note ? `<span>Note: ${f.note}</span>` : ""}
        </div>
      </div>
    `;
  }).join("");
}

/**
 * Load and render 8-10 Curated Scheme FAQs
 */
async function loadFaqs(schemeId) {
  try {
    const res = await fetch(`/api/schemes/${schemeId}/faqs`);
    if (!res.ok) throw new Error("Failed to load FAQs");
    currentFaqs = await res.json();
    renderFaqChips();
  } catch (err) {
    console.error("Error loading FAQs:", err);
    faqPresets.innerHTML = `<p class="field-empty">Error loading FAQs</p>`;
  }
}

function renderFaqChips() {
  if (!currentFaqs || currentFaqs.length === 0) return;
  document.getElementById("faqCountLabel").textContent = `${currentFaqs.length} Questions`;

  faqPresets.innerHTML = currentFaqs.map((faq) => {
    const qText = currentLanguage === "hi" ? faq.question_hi : faq.question_en;
    return `
      <button type="button" class="faq-preset-chip" data-faq-id="${faq.faq_id}" title="${qText}">
        ${qText}
      </button>
    `;
  }).join("");

  faqPresets.querySelectorAll(".faq-preset-chip").forEach((chip) => {
    chip.addEventListener("click", async () => {
      const faqId = chip.dataset.faqId;
      const faq = currentFaqs.find((f) => f.faq_id === faqId);
      if (faq) {
        const q = currentLanguage === "hi" ? faq.question_hi : faq.question_en;
        await sendChatMessage(q);
      }
    });
  });
}

function renderWelcomeMessage() {
  chatMessages.innerHTML = "";
  const isHi = currentLanguage === "hi";
  const welcomeText = isHi
    ? `नमस्ते! मैं <strong>${currentSchemeData ? currentSchemeData.scheme_name : "सरकारी योजना"}</strong> के लिए आपका हकदर्शक सहायक हूँ। आप मुझसे पात्रता, आवश्यक दस्तावेज, सहायता राशि या आवेदन प्रक्रिया के बारे में कोई भी प्रश्न पूछ सकते हैं।`
    : `Hello! I am your Haqdarshak Assistant for <strong>${currentSchemeData ? currentSchemeData.scheme_name : "this government scheme"}</strong>. You can ask me any question about eligibility, required documents, benefits, or how to apply.`;

  appendBotBubble({
    answer: welcomeText,
    source_fields: ["scheme_name"],
    evidence_quotes: ["Official Scheme Knowledge Record v2.1"],
    is_fallback: false
  });
}

/**
 * Send chat query to backend
 */
async function sendChatMessage(query) {
  // Append User Bubble
  appendUserBubble(query);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  // Loading indicator
  const loadingId = appendLoadingBubble();
  chatMessages.scrollTop = chatMessages.scrollHeight;

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        scheme_id: currentSchemeId,
        question: query,
        language: currentLanguage,
        mode: isSimpleMode ? "simple_literacy" : "standard"
      })
    });

    removeLoadingBubble(loadingId);

    if (!res.ok) throw new Error("Server error responding to query");
    const data = await res.json();

    // Append Assistant Bubble
    appendBotBubble(data);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  } catch (err) {
    removeLoadingBubble(loadingId);
    appendBotBubble({
      answer: `Error connecting to AI service: ${err.message}`,
      source_fields: [],
      evidence_quotes: [],
      is_fallback: true
    });
  }
}

function appendUserBubble(text) {
  const wrap = document.createElement("div");
  wrap.className = "chat-bubble-wrap user-wrap";
  wrap.innerHTML = `<div class="bubble user-bubble">${escapeHtml(text)}</div>`;
  chatMessages.appendChild(wrap);
}

function appendLoadingBubble() {
  const id = "loading-" + Date.now();
  const wrap = document.createElement("div");
  wrap.id = id;
  wrap.className = "chat-bubble-wrap bot-wrap";
  wrap.innerHTML = `<div class="bubble bot-bubble" style="opacity: 0.7;"><em>Checking official scheme guidelines...</em></div>`;
  chatMessages.appendChild(wrap);
  return id;
}

function removeLoadingBubble(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function appendBotBubble(data) {
  const wrap = document.createElement("div");
  wrap.className = "chat-bubble-wrap bot-wrap";

  const isLowLit = isSimpleMode;
  const isFallback = data.is_fallback;
  const drawerId = "evidence-" + Date.now();

  const sourcesText = data.source_fields && data.source_fields.length > 0
    ? data.source_fields.map((f) => `<span class="source-badge">#${f}</span>`).join(" ")
    : "<span style='color: #fbbf24;'>Official Record (Absence verified)</span>";

  const quotesText = data.evidence_quotes && data.evidence_quotes.length > 0
    ? data.evidence_quotes.map((q) => `<li>${escapeHtml(q)}</li>`).join("")
    : "<li>The official scheme record does not contain this information.</li>";

  wrap.innerHTML = `
    <div class="bubble bot-bubble ${isLowLit ? "low-literacy" : ""} ${isFallback ? "fallback-bubble" : ""}">
      <div class="bot-text">${data.answer}</div>
      <div class="bot-bubble-footer">
        <div class="attribution-bar">
          <div><strong>Source:</strong> ${sourcesText}</div>
          <button type="button" class="evidence-toggle-btn" onclick="toggleEvidenceDrawer('${drawerId}')">
            Show Official Evidence
          </button>
        </div>
        <div class="evidence-drawer" id="${drawerId}">
          <strong>Exact Government Document Citations:</strong>
          <ul>${quotesText}</ul>
        </div>
      </div>
    </div>
  `;
  chatMessages.appendChild(wrap);
}

window.toggleEvidenceDrawer = function (id) {
  const el = document.getElementById(id);
  if (el) el.classList.toggle("open");
};

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
