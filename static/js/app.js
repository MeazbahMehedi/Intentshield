document.addEventListener("DOMContentLoaded", function () {
  const textarea = document.getElementById("prompt");
  const counter = document.getElementById("char-count");
  const form = document.getElementById("scan-form");
  const scanButton = document.getElementById("scan-button");
  const clearButton = document.getElementById("clear-prompt");

  if (textarea && counter) {
    const updateCount = () => {
      counter.textContent = textarea.value.length.toLocaleString() + " / 10,000";
      counter.classList.toggle("counter-near-limit", textarea.value.length >= 9000);
    };
    textarea.addEventListener("input", updateCount);
    updateCount();

    document.querySelectorAll("[data-sample]").forEach((button) => {
      button.addEventListener("click", () => {
        textarea.value = button.getAttribute("data-sample") || "";
        updateCount();
        textarea.focus();
      });
    });

    if (clearButton) {
      clearButton.addEventListener("click", () => {
        textarea.value = "";
        updateCount();
        textarea.focus();
      });
    }
  }

  if (form && scanButton) {
    form.addEventListener("submit", (event) => {
      if (!textarea || !textarea.value.trim()) {
        event.preventDefault();
        if (textarea) textarea.focus();
        return;
      }
      scanButton.disabled = true;
      scanButton.setAttribute("aria-busy", "true");
      scanButton.innerHTML = '<span aria-hidden="true">◌</span> Analyzing locally…';
    });
  }
});

/* PromptGuard advanced UI: live scan, batch mode, history tools, toasts.
 * All dynamic text is inserted with textContent (never innerHTML) to prevent XSS. */
(function () {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));

  function el(tag, props = {}, children = []) {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(props)) {
      if (k === "class") n.className = v;
      else if (k === "text") n.textContent = v;
      else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
      else n.setAttribute(k, v);
    }
    [].concat(children).forEach((c) => c != null && n.append(c));
    return n;
  }

  /* ---------- toasts ---------- */
  const toastBox = $("#toasts");
  function toast(msg, isErr) {
    if (!toastBox) return;
    const t = el("div", { class: "toast" + (isErr ? " err" : ""), role: "status", text: msg });
    toastBox.append(t);
    setTimeout(() => t.remove(), 3200);
  }

  /* ---------- helpers ---------- */
  async function postJSON(url, body) {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || "Request failed (" + res.status + ")");
    return data;
  }
  function download(name, text, type) {
    const a = el("a", { href: URL.createObjectURL(new Blob([text], { type })), download: name });
    document.body.append(a);
    a.click();
    a.remove();
  }
  const csvCell = (v) => {
    let s = String(v ?? "");
    if (/^[=+\-@]/.test(s)) s = "'" + s; // neutralise spreadsheet formula injection
    return '"' + s.replace(/"/g, '""') + '"';
  };

  /* ---------- tabs ---------- */
  const tabs = $$(".tab");
  tabs.forEach((tab) =>
    tab.addEventListener("click", () => {
      tabs.forEach((t) => t.setAttribute("aria-selected", String(t === tab)));
      $$(".tab-panel").forEach((p) => (p.hidden = p.id !== tab.getAttribute("aria-controls")));
    })
  );

  /* ---------- result rendering ---------- */
  const slot = $("#result-slot");
  const CIRC = 2 * Math.PI * 52;

  function gauge(score) {
    const ns = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(ns, "svg");
    svg.setAttribute("viewBox", "0 0 124 124");
    const mk = (cls) => {
      const c = document.createElementNS(ns, "circle");
      c.setAttribute("cx", 62); c.setAttribute("cy", 62); c.setAttribute("r", 52);
      c.setAttribute("fill", "none"); c.setAttribute("stroke-width", 10);
      c.setAttribute("class", cls);
      return c;
    };
    const fg = mk("g-fg");
    fg.style.strokeDasharray = CIRC;
    fg.style.strokeDashoffset = CIRC;
    svg.append(mk("g-bg"), fg);
    requestAnimationFrame(() => requestAnimationFrame(() => {
      fg.style.strokeDashoffset = CIRC * (1 - Math.min(100, score) / 100);
    }));
    const num = el("div", { class: "g-num" }, [el("strong", { text: "0" }), el("small", { text: "/ 100" })]);
    const strong = num.firstChild;
    const start = performance.now();
    (function tick(now) {
      const p = Math.min(1, (now - start) / 900);
      strong.textContent = Math.round(score * (1 - Math.pow(1 - p, 3)));
      if (p < 1) requestAnimationFrame(tick);
    })(start);
    return el("div", { class: "gauge", role: "img", "aria-label": "Risk score " + score + " out of 100" }, [svg, num]);
  }

  function categoryBreakdown(findings) {
    const totals = {};
    findings.forEach((f) => (totals[f.category] = (totals[f.category] || 0) + f.weight));
    const entries = Object.entries(totals).sort((a, b) => b[1] - a[1]);
    if (!entries.length) return null;
    const max = Math.max(...entries.map((e) => e[1]));
    const box = el("div", {}, [el("div", { class: "sec-title", text: "SIGNALS BY CATEGORY" })]);
    entries.forEach(([cat, w]) => {
      const bar = el("div", { class: "cat-bar" }, [el("i")]);
      box.append(el("div", { class: "cat-row" }, [el("span", { text: cat }), bar, el("b", { text: "+" + w })]));
      requestAnimationFrame(() => requestAnimationFrame(() => (bar.firstChild.style.width = (w / max) * 100 + "%")));
    });
    return box;
  }

  function accordion(f, i) {
    const bid = "acc-" + i;
    const btn = el("button", { class: "acc-btn", type: "button", "aria-expanded": "false", "aria-controls": bid }, [
      el("span", { class: "chev", "aria-hidden": "true", text: "▸" }),
      el("strong", { text: f.name }),
      el("span", { class: "w", text: "+" + f.weight }),
    ]);
    const body = el("div", { class: "acc-body", id: bid }, [
      el("div", {}, [
        el("p", { text: f.explanation }),
        el("span", { class: "tag", text: f.category }),
        el("div", { class: "weight-bar", "aria-hidden": "true" }, [el("i", { style: "width:" + Math.min(100, f.weight) + "%" })]),
      ]),
    ]);
    btn.addEventListener("click", () => btn.setAttribute("aria-expanded", String(btn.getAttribute("aria-expanded") !== "true")));
    return el("div", { class: "acc" }, [btn, body]);
  }

  function renderResult(r, prompt) {
    const pin = el("span", { class: "scale-pin" });
    pin.style.left = "0%";
    requestAnimationFrame(() => requestAnimationFrame(() => (pin.style.left = "calc(" + r.score + "% - 1px)")));

    const toolbar = el("div", { class: "toolbar" }, [
      el("button", { class: "btn-ghost", type: "button", text: "Copy JSON", onclick: async () => {
        try { await navigator.clipboard.writeText(JSON.stringify(r, null, 2)); toast("Result copied as JSON"); }
        catch { toast("Clipboard unavailable in this browser", true); }
      } }),
      el("button", { class: "btn-ghost", type: "button", text: "Download JSON", onclick: () =>
        download("promptguard-result.json", JSON.stringify({ prompt, ...r }, null, 2), "application/json") }),
    ]);

    const card = el("div", { class: "adv-result level-" + r.css, "aria-live": "polite" }, [
      el("div", { class: "adv-top" }, [
        gauge(r.score),
        el("div", { class: "adv-head" }, [
          el("span", { class: "result-kicker", text: "SCAN COMPLETE" }),
          el("h3", { text: r.level + " risk" + (r.findings.length ? " detected" : " — no signals matched") }),
          el("p", { text: r.summary }),
          toolbar,
        ]),
      ]),
      el("div", { class: "scale-wrap" }, [
        el("div", { class: "scale" }), pin,
        el("div", { class: "scale-labels" }, [el("span", { text: "0 LOW" }), el("span", { text: "25 MEDIUM" }), el("span", { text: "60 HIGH" }), el("span", { text: "100" })]),
      ]),
    ]);
    const cats = categoryBreakdown(r.findings);
    if (cats) card.append(cats);
    if (r.findings.length) {
      card.append(el("div", { class: "sec-title" }, ["MATCHED RULES ", el("span", { text: String(r.findings.length) })]));
      r.findings.forEach((f, i) => card.append(accordion(f, i)));
    }
    card.append(el("p", { class: "disclaimer" }, [
      el("strong", { text: "Interpretation note: " }),
      "The score is a weighted rule-match indicator, not a probability of malicious intent. This heuristic can produce false positives and false negatives.",
    ]));
    slot.replaceChildren(card);
    card.scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "nearest" });
  }

  /* ---------- stats + history ---------- */
  function updateStats(s) {
    const set = (id, v) => { const n = $(id); if (n) n.textContent = v; };
    set("#stat-total", s.total_scans); set("#stat-threats", s.threats); set("#stat-high", s.high_risk);
  }
  const histBody = $("#history-body");
  function historyRow(h) {
    const tr = el("tr", { class: "clickable flash", tabindex: "0", title: "Click to load this preview into the scanner" }, [
      el("td", { class: "preview-cell", text: h.preview }),
      el("td", { class: "time-cell", text: h.time }),
      el("td", {}, [el("span", { class: "risk-badge badge-" + h.level.toLowerCase(), text: h.level })]),
      el("td", { class: "score-cell", text: h.score + "/100" }),
      el("td", { text: String(h.findings) }),
    ]);
    tr.dataset.level = h.level;
    return tr;
  }
  function addHistory(h) {
    if (!histBody) return;
    const empty = $("#history-empty"); if (empty) empty.hidden = true;
    const wrap = $("#history-table-wrap"); if (wrap) wrap.hidden = false;
    histBody.prepend(historyRow(h));
    while (histBody.rows.length > 8) histBody.deleteRow(-1);
    const c = $("#history-count"); if (c) c.textContent = histBody.rows.length + " records";
  }
  function filterHistory() {
    const q = ($("#hist-search")?.value || "").toLowerCase();
    const lvl = $("#hist-level")?.value || "";
    $$("#history-body tr").forEach((tr) => {
      const okText = !q || tr.textContent.toLowerCase().includes(q);
      const okLvl = !lvl || tr.dataset.level === lvl;
      tr.hidden = !(okText && okLvl);
    });
  }
  $("#hist-search")?.addEventListener("input", filterHistory);
  $("#hist-level")?.addEventListener("change", filterHistory);
  $("#hist-export")?.addEventListener("click", () => {
    const rows = $$("#history-body tr").filter((tr) => !tr.hidden);
    if (!rows.length) return toast("Nothing to export", true);
    const lines = [["Preview", "Time", "Level", "Score", "Rules matched"].map(csvCell).join(",")];
    rows.forEach((tr) => lines.push($$("td", tr).map((td) => csvCell(td.textContent)).join(",")));
    download("promptguard-history.csv", lines.join("\n"), "text/csv");
    toast("History exported");
  });
  histBody?.addEventListener("click", (e) => {
    const tr = e.target.closest("tr"); if (!tr) return;
    const ta = $("#prompt");
    if (ta) { ta.value = $(".preview-cell", tr).textContent; ta.dispatchEvent(new Event("input")); ta.focus(); }
  });
  histBody?.addEventListener("keydown", (e) => { if (e.key === "Enter") e.target.closest("tr")?.click(); });

  /* ---------- single scan (replaces full-page reload) ---------- */
  const form = $("#scan-form"), ta = $("#prompt"), btn = $("#scan-button");
  async function runScan() {
    const prompt = ta.value.trim();
    if (!prompt) { toast("Enter a prompt first", true); ta.focus(); return; }
    btn.disabled = true; btn.classList.add("loading"); btn.setAttribute("aria-busy", "true");
    try {
      const data = await postJSON("/api/scan", { prompt });
      renderResult(data.result, prompt);
      updateStats(data.stats);
      addHistory(data.history_entry);
    } catch (err) {
      toast(err.message, true);
    } finally {
      btn.disabled = false; btn.classList.remove("loading"); btn.removeAttribute("aria-busy");
    }
  }
  if (form && ta && btn && slot) {
    // Capture on document so the legacy submit handler in app.js never runs.
    document.addEventListener("submit", (e) => {
      if (e.target !== form) return;
      e.preventDefault(); e.stopPropagation();
      runScan();
    }, true);
    ta.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); runScan(); }
    });
  }

  /* ---------- batch scan ---------- */
  const batchBtn = $("#batch-run"), batchIn = $("#batch-input"), batchOut = $("#batch-output");
  let lastBatch = [];
  batchBtn?.addEventListener("click", async () => {
    const prompts = batchIn.value.split("\n").map((s) => s.trim()).filter(Boolean);
    if (!prompts.length) return toast("Enter at least one prompt (one per line)", true);
    batchBtn.disabled = true; batchBtn.classList.add("loading");
    try {
      const { rows } = await postJSON("/api/batch", { prompts });
      lastBatch = rows;
      const count = (lvl) => rows.filter((r) => r.level === lvl).length;
      const stat = (label, v) => el("div", { class: "mini-stat" }, [el("small", { text: label }), el("strong", { text: String(v) })]);
      const table = el("table", {}, [
        el("thead", {}, [el("tr", {}, ["PROMPT", "RISK", "SCORE", "SIGNALS"].map((h) => el("th", { text: h })))]),
        el("tbody", {}, rows.map((r) => el("tr", {}, [
          el("td", { class: "preview-cell", text: r.prompt, title: r.prompt }),
          el("td", {}, [el("span", { class: "risk-badge badge-" + r.css, text: r.level })]),
          el("td", { class: "score-cell", text: r.score + "/100" }),
          el("td", { text: r.findings.join(", ") || "—" }),
        ]))),
      ]);
      batchOut.replaceChildren(
        el("div", { class: "batch-summary" }, [stat("TOTAL", rows.length), stat("HIGH", count("High")), stat("MEDIUM", count("Medium")), stat("LOW", count("Low"))]),
        el("div", { class: "toolbar", style: "margin-bottom:12px" }, [
          el("button", { class: "btn-ghost", type: "button", text: "Download CSV", onclick: () => {
            const lines = [["Prompt", "Level", "Score", "Signals"].map(csvCell).join(",")];
            lastBatch.forEach((r) => lines.push([r.prompt, r.level, r.score, r.findings.join("; ")].map(csvCell).join(",")));
            download("promptguard-batch.csv", lines.join("\n"), "text/csv");
          } }),
        ]),
        el("div", { class: "table-wrap" }, [table])
      );
      toast("Scanned " + rows.length + " prompts");
    } catch (err) { toast(err.message, true); }
    finally { batchBtn.disabled = false; batchBtn.classList.remove("loading"); }
  });
})();
