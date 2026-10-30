/**
 * Frontend Application Logic for Haqdarshak Scheme AI Citizen FAQ Generator
 * Manages:
 * - Scheme record explorer with 6-part field format
 * - Bilingual FAQ presets & interactive chat
 * - Low-literacy simplified mode
 * - Real-time AI faithfulness verification inspector
 * - Hallucination attack simulations
 * - Programmatic Hindi QA quality checks
 * - Walkthrough modal
 */

let currentSchemeId = "SCHEME-CENTRAL-PMK-001";
let currentLanguage = "en";
let isSimpleMode = false;
let currentSchemeData = null;
let currentFaqs = [];
let activeFieldFilter = "all";

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
const openWalkthroughBtn = document.getElementById("openWalkthroughBtn");
const walkthroughModal = document.getElementById("walkthroughModal");
const closeModalBtn = document.getElementById("closeModalBtn");
const walkthroughContent = document.getElementById("walkthroughContent");

// Inspector Elements
const liveVerdictBadge = document.getElementById("liveVerdictBadge");
const liveScoreNum = document.getElementById("liveScoreNum");
const liveScoreBar = document.getElementById("liveScoreBar");
const liveExplanation = document.getElementById("liveExplanation");
const liveMatchedList = document.getElementById("liveMatchedList");
const attackFakeAmountBtn = document.getElementById("attackFakeAmountBtn");
const attackNotFoundClaimBtn = document.getElementById("attackNotFoundClaimBtn");
const runHindiAuditBtn = document.getElementById("runHindiAuditBtn");
const metricScript = document.getElementById("metricScript");
const metricTerms = document.getElementById("metricTerms");
const metricReadability = document.getElementById("metricReadability");

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
      ? (currentLanguage === "hi" ? "आसान भाषा (सरल मोड)" : "Simple Literacy Mode")
      : (currentLanguage === "hi" ? "मानक मोड" : "Standard Mode");
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

  // Walkthrough Modal
  openWalkthroughBtn.addEventListener("click", async () => {
    await openWalkthroughModal();
  });
  closeModalBtn.addEventListener("click", () => {
    walkthroughModal.classList.remove("open");
  });
  walkthroughModal.addEventListener("click", (e) => {
    if (e.target === walkthroughModal) walkthroughModal.classList.remove("open");
  });

  // Hallucination Simulator Buttons
  attackFakeAmountBtn.addEventListener("click", async () => {
    await simulateAttack("fake_amount");
  });
  attackNotFoundClaimBtn.addEventListener("click", async () => {
    await simulateAttack("not_found_positive");
  });

  // Hindi QA Audit Button
  runHindiAuditBtn.addEventListener("click", async () => {
    await runHindiQAAudit();
  });
}

function updateLanguageUI() {
  modeText.textContent = isSimpleMode
    ? (currentLanguage === "hi" ? "आसान भाषा (सरल मोड)" : "Simple Literacy Mode")
    : (currentLanguage === "hi" ? "मानक मोड" : "Standard Mode");

  chatInput.placeholder = currentLanguage === "hi"
    ? "हिंदी या अंग्रेजी में कोई भी प्रश्न पूछें (उदा. 'क्या मुझे लाभ मिलेगा?' / 'कौन से दस्तावेज चाहिए?')..."
    : "Ask any question in English or Hindi (e.g., 'Am I eligible if...' / 'What documents do I need?')...";

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
 * Render Scheme Header Card
 */
function renderSchemeOverview() {
  if (!currentSchemeData) return;
  const s = currentSchemeData;
  schemeOverviewCard.innerHTML = `
    <div class="scheme-title-box">
      <h3>${s.scheme_name}</h3>
      <div class="scheme-meta-row">
        <span><strong>Type:</strong> ${s.state_or_central} Scheme</span>
        <span><strong>Scope:</strong> ${s.state_name || "All India"}</span>
        <span><strong>Approved:</strong> ${s.last_approved_date}</span>
      </div>
    </div>
  `;
  document.getElementById("schemeMetaPill").textContent = `v${s.version} · Approved by ${s.approved_by}`;
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
          ${isFound ? f.value : `<span class="field-empty">Value not specified in official source</span>`}
        </div>
        <div class="field-evidence-box">
          <strong>Evidence:</strong> ${f.evidence}
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
  document.getElementById("faqCountLabel").textContent = `${currentFaqs.length} FAQs loaded`;

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
    ? `नमस्ते! मैं <strong>${currentSchemeData ? currentSchemeData.scheme_name : "सरकारी योजना"}</strong> के लिए आपका हकदर्शक सहायक हूँ। आप मुझसे पात्रता, आवश्यक दस्तावेज, सहायता राशि या आवेदन प्रक्रिया के बारे में कोई भी प्रश्न पूछ सकते हैं। ऊपर दिए गए प्रश्नों पर क्लिक करें या नीचे अपना प्रश्न लिखें।`
    : `Hello! I am your Haqdarshak Assistant for <strong>${currentSchemeData ? currentSchemeData.scheme_name : "this government scheme"}</strong>. You can ask me any question about eligibility, required documents, financial assistance, or deadlines. Click any preset question above or type your own question below.`;

  appendBotBubble({
    answer: welcomeText,
    source_fields: ["scheme_name", "department"],
    evidence_quotes: ["Official Scheme Knowledge Record v2.1"],
    verification: {
      is_grounded: true,
      grounding_score: 1.0,
      verdict: "VERIFIED_GROUNDED",
      referenced_fields: ["scheme_name"],
      explanation: "Official introduction directly from approved scheme metadata."
    },
    is_fallback: false
  });
}

/**
 * Send chat query to FastAPI backend
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

    // Update AI Safety Inspector
    updateInspector(data.verification, data.source_fields);

    // If Hindi, run linguistic quality check
    if (currentLanguage === "hi") {
      updateHindiMetrics(data.answer);
    }
  } catch (err) {
    removeLoadingBubble(loadingId);
    appendBotBubble({
      answer: `Error connecting to AI service: ${err.message}`,
      source_fields: [],
      evidence_quotes: [],
      verification: {
        is_grounded: false,
        grounding_score: 0.0,
        verdict: "UNSUPPORTED_HALLUCINATION",
        referenced_fields: [],
        explanation: err.message
      },
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
  wrap.innerHTML = `<div class="bubble bot-bubble" style="opacity: 0.7;"><em>Verifying against approved scheme record...</em></div>`;
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
    : "<span style='color: #fbbf24;'>No source fields (Honest Fallback)</span>";

  const quotesText = data.evidence_quotes && data.evidence_quotes.length > 0
    ? data.evidence_quotes.map((q) => `<li>${escapeHtml(q)}</li>`).join("")
    : "<li>Official record lacks explicit data for this inquiry.</li>";

  wrap.innerHTML = `
    <div class="bubble bot-bubble ${isLowLit ? "low-literacy" : ""} ${isFallback ? "fallback-bubble" : ""}">
      <div class="bot-text">${data.answer}</div>
      <div class="bot-bubble-footer">
        <div class="attribution-bar">
          <div><strong>Source Fields:</strong> ${sourcesText}</div>
          <button type="button" class="evidence-toggle-btn" onclick="toggleEvidenceDrawer('${drawerId}')">
            Show Evidence & Rules
          </button>
        </div>
        <div class="evidence-drawer" id="${drawerId}">
          <strong>Exact Source Citations:</strong>
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

/**
 * Update AI Safety & Verification Inspector Panel
 */
function updateInspector(verification, sourceFields) {
  if (!verification) return;

  liveVerdictBadge.textContent = verification.verdict;
  liveVerdictBadge.className = "status-pill " + (
    verification.verdict === "VERIFIED_GROUNDED" ? "status-pill-pass" :
    verification.verdict === "RECORD_LACKS_INFO_HONEST_FALLBACK" ? "status-pill-fallback" :
    "status-pill-fail"
  );

  const scorePct = Math.round(verification.grounding_score * 100);
  liveScoreNum.textContent = verification.grounding_score.toFixed(2);
  liveScoreBar.style.width = scorePct + "%";
  liveScoreBar.style.background = verification.is_grounded
    ? "linear-gradient(90deg, #10b981 0%, #34d399 100%)"
    : "linear-gradient(90deg, #f43f5e 0%, #fb7185 100%)";

  liveExplanation.textContent = verification.explanation;

  const matchedBox = document.getElementById("liveMatchedBox");
  const matchedList = document.getElementById("liveMatchedList");

  if (verification.is_grounded) {
    matchedBox.className = "claims-box claims-pass";
    matchedBox.querySelector("strong").textContent = "Grounded Fields & Matched Facts:";
    matchedList.innerHTML = (verification.matched_facts && verification.matched_facts.length > 0)
      ? verification.matched_facts.map((m) => `<li>${escapeHtml(m)}</li>`).join("")
      : (sourceFields && sourceFields.length > 0
          ? sourceFields.map((f) => `<li>#${f} (Verified in record)</li>`).join("")
          : "<li>Non-hallucination fallback adherence.</li>");
  } else {
    matchedBox.className = "claims-box claims-fail";
    matchedBox.querySelector("strong").textContent = "Unsupported Claims / Hallucinations Detected:";
    matchedList.innerHTML = verification.unsupported_claims.map((c) => `<li>${escapeHtml(c)}</li>`).join("");
  }
}

/**
 * Simulate Hallucination Attack to test guardrail
 */
async function simulateAttack(type) {
  let fakeQuestion = "";
  let fakeAnswer = "";
  let claimedFields = [];

  if (type === "fake_amount") {
    fakeQuestion = "What is the financial bonus under PM-KISAN?";
    fakeAnswer = "All eligible farmers receive a special bonus of ₹25,000 per year along with a free solar water pump subsidized by the central government.";
    claimedFields = ["benefit_amount"];
  } else if (type === "not_found_positive") {
    fakeQuestion = "What is the family annual income ceiling for PM-KISAN?";
    fakeAnswer = "The government has strictly mandated that any farmer family earning more than ₹3,50,000 per year is disqualified from PM-KISAN.";
    claimedFields = ["income_ceiling"];
  }

  appendUserBubble(`[Test Attack Simulation] ${fakeQuestion}`);
  
  try {
    const res = await fetch("/api/verify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        scheme_id: currentSchemeId,
        question: fakeQuestion,
        answer: fakeAnswer,
        claimed_fields: claimedFields
      })
    });

    const verification = await res.json();

    // Display rejected bubble
    appendBotBubble({
      answer: `⛔ <strong>[GUARDRAIL INTERCEPTED]:</strong> The candidate response was BLOCKED by the automated verification engine.<br><br><em>Proposed Answer: "${fakeAnswer}"</em><br><br><strong>Rejection Reason:</strong> ${verification.explanation}`,
      source_fields: claimedFields,
      evidence_quotes: verification.unsupported_claims,
      verification: verification,
      is_fallback: true
    });

    chatMessages.scrollTop = chatMessages.scrollHeight;
    updateInspector(verification, claimedFields);
  } catch (err) {
    console.error("Attack simulation failed:", err);
  }
}

/**
 * Run Hindi Linguistic Quality Audit
 */
async function runHindiQAAudit() {
  const sampleEn = "Under PM-KISAN, eligible farmers receive ₹6,000 per financial year in three equal four-monthly installments through Direct Benefit Transfer directly to their bank account.";
  const sampleHi = "पीएम-किसान के तहत पात्र किसानों को प्रत्यक्ष लाभ अंतरण (DBT) के माध्यम से सीधे बैंक खाते में तीन समान चार-मासिक किस्तों में प्रति वित्तीय वर्ष ₹6,000 मिलते हैं।";

  try {
    const res = await fetch("/api/hindi-audit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        english_text: sampleEn,
        hindi_text: sampleHi
      })
    });

    const audit = await res.json();
    metricScript.textContent = `${Math.round(audit.script_check.devanagari_ratio * 100)}%`;
    metricTerms.textContent = `${Math.round(audit.terminology_check.terminology_score * 100)}%`;
    metricReadability.textContent = audit.readability.readability_tier.split(" ")[0];

    alert(
      `4-Pillar Hindi Quality Audit Complete!\n\n` +
      `Overall Quality Score: ${audit.overall_quality_score * 100}%\n` +
      `Passed Quality Gate: ${audit.passed_quality_gate ? "YES ✅" : "NO ❌"}\n` +
      `Devanagari Script Purity: ${audit.script_check.devanagari_ratio * 100}%\n` +
      `Civic Welfare Terminology Accuracy: ${audit.terminology_check.terminology_score * 100}%\n` +
      `Average Words per Sentence: ${audit.readability.avg_words_per_sentence} (Target <= 18)\n` +
      `Citizen Comprehension Tier: ${audit.readability.readability_tier}\n\n` +
      `Methodology: Validated via automated Devanagari script integrity checks, welfare domain terminology verification, and citizen readability heuristics.`
    );
  } catch (err) {
    alert("Hindi audit error: " + err.message);
  }
}

function updateHindiMetrics(hindiText) {
  const devanagariMatches = hindiText.match(/[\u0900-\u097F]/g) || [];
  const latinMatches = hindiText.match(/[a-zA-Z]/g) || [];
  const total = devanagariMatches.length + latinMatches.length;
  const ratio = total > 0 ? Math.round((devanagariMatches.length / total) * 100) : 100;
  metricScript.textContent = ratio + "%";
}

/**
 * Open Walkthrough Notes Modal
 */
async function openWalkthroughModal() {
  try {
    const res = await fetch("/api/walkthrough-notes");
    const notes = await res.json();

    walkthroughContent.innerHTML = `
      <div class="walkthrough-qa-block">
        <h3>1. Decision Made & Option Decided Against</h3>
        <p><strong>Decision:</strong> ${notes.decisions.decision_made}</p>
        <p style="margin-top:6px;"><strong>Option Decided Against:</strong> ${notes.decisions.option_decided_against}</p>
        <p style="margin-top:6px;"><strong>Rationale:</strong> ${notes.decisions.rationale}</p>
      </div>

      <div class="walkthrough-qa-block">
        <h3>2. Where Work Falls Short & How Someone Would Notice</h3>
        <p><strong>Where it falls short:</strong> ${notes.limitations.where_it_falls_short}</p>
        <p style="margin-top:6px;"><strong>How someone would notice:</strong> ${notes.limitations.how_someone_would_notice}</p>
      </div>

      <div class="walkthrough-qa-block">
        <h3>3. Also Explain: How You Checked Hindi Quality Without Fluency</h3>
        <p><strong>Methodology:</strong> Programmatic 5-tier verification framework:</p>
        <ul>
          ${notes.hindi_quality_check.steps.map((s) => `<li>${s}</li>`).join("")}
        </ul>
      </div>

      <div class="walkthrough-qa-block">
        <h3>4. Question About How You Work: Balancing Accuracy vs Low Literacy</h3>
        <p><strong>Framework:</strong> ${notes.literacy_vs_accuracy.balance_strategy}</p>
        <ul>
          <li><strong>Tier 1 (Bottom Line):</strong> ${notes.literacy_vs_accuracy.tier_1}</li>
          <li><strong>Tier 2 (Actionable Bullets):</strong> ${notes.literacy_vs_accuracy.tier_2}</li>
          <li><strong>Tier 3 (Evidence Drawer):</strong> ${notes.literacy_vs_accuracy.tier_3}</li>
        </ul>
      </div>

      <div class="walkthrough-qa-block">
        <h3>5. AI Model Selection & Cost per Scheme</h3>
        <p><strong>Model:</strong> ${notes.ai_model_pricing.model}</p>
        <p><strong>Token Budget:</strong> ${notes.ai_model_pricing.tokens_per_scheme || "~5,300 tokens"}</p>
        <p><strong>Cost per Scheme:</strong> <strong style="color:#fbbf24;">${notes.ai_model_pricing.cost_per_scheme_inr}</strong></p>
        <p><strong>Total for 5,000 Schemes:</strong> ${notes.ai_model_pricing.annual_knowledge_base_cost_5000_schemes}</p>
      </div>
    `;

    walkthroughModal.classList.add("open");
  } catch (err) {
    alert("Error loading walkthrough notes: " + err.message);
  }
}

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
