
(function () {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const NS = "http://www.w3.org/2000/svg";
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const colors = ["#3bd8e8", "#7a8cff", "#9b8cff", "#51d6a2", "#ffbf69", "#ff7692", "#4c9fe8", "#d68aff"];
  let data = null;
  let selectedLevel = "All";

  function svg(tag, attrs = {}) {
    const node = document.createElementNS(NS, tag);
    Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, value));
    return node;
  }
  function countUp(node, value) {
    if (!node) return;
    if (reduceMotion) { node.textContent = Number(value).toFixed(value % 1 ? 1 : 0); return; }
    const start = performance.now();
    const duration = 650;
    function tick(now) {
      const progress = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - progress, 3);
      node.textContent = (Number(value) * eased).toFixed(Number(value) % 1 ? 1 : 0);
      if (progress < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }
  function renderMetrics(d) {
    document.querySelectorAll("[data-metric]").forEach((card, index) => {
      const key = card.dataset.metric;
      countUp($("[data-num]", card), d.metrics[key] || 0);
      card.style.animationDelay = (index * 70) + "ms";
    });
  }
  function renderDistribution(d) {
    const total = d.metrics.total || 0;
    $("#distribution-total").textContent = total;
    $("#distribution-empty").hidden = total > 0;
    ["Low", "Medium", "High"].forEach((level) => {
      $("#lv-" + level).textContent = d.levels[level] || 0;
    });
    const low = total ? (d.levels.Low / total) * 100 : 0;
    const medium = total ? (d.levels.Medium / total) * 100 : 0;
    const high = total ? (d.levels.High / total) * 100 : 0;
    const spans = $("#distribution-bar").querySelectorAll("span");
    spans[0].style.width = low + "%";
    spans[1].style.width = medium + "%";
    spans[2].style.width = high + "%";
  }
  function renderRules(d) {
    const body = $("#rules-body");
    body.replaceChildren();
    $("#rules-empty").hidden = d.top_rules.length > 0;
    const max = Math.max(1, ...d.top_rules.map((rule) => rule.hits));
    d.top_rules.forEach((rule, index) => {
      const tr = document.createElement("tr");
      const name = document.createElement("td");
      const freq = document.createElement("td");
      const hits = document.createElement("td");
      name.textContent = window.promptGuardTranslateRuleName ? window.promptGuardTranslateRuleName(rule.name) : rule.name;
      const track = document.createElement("div");
      track.className = "frequency-track";
      const fill = document.createElement("span");
      fill.style.width = ((rule.hits / max) * 100) + "%";
      track.append(fill);
      freq.append(track);
      hits.textContent = rule.hits;
      tr.style.animationDelay = (index * 45) + "ms";
      tr.append(name, freq, hits);
      body.append(tr);
    });
  }
  function renderBubbles() {
    if (!data) return;
    const root = $("#bubbles");
    const legend = $("#bubble-legend");
    root.replaceChildren();
    legend.replaceChildren();
    const items = Object.entries(data.categories || {}).map(([name, levels]) => {
      const count = selectedLevel === "All"
        ? (levels.Low || 0) + (levels.Medium || 0) + (levels.High || 0)
        : (levels[selectedLevel] || 0);
      return { name, count };
    }).filter((item) => item.count > 0).sort((a, b) => b.count - a.count).slice(0, 12);
    $("#bubble-empty").hidden = items.length > 0;
    if (!items.length) return;
    const max = Math.max(1, items[0].count);
    const positions = [
      [300, 185], [145, 95], [455, 90], [155, 280], [455, 280], [300, 65],
      [300, 305], [80, 185], [520, 185], [220, 120], [385, 245], [380, 125]
    ];
    items.forEach((item, index) => {
      const [x, y] = positions[index % positions.length];
      const radius = 20 + Math.sqrt(item.count / max) * 45;
      const group = svg("g", { class: "bubble-node" });
      group.style.animationDelay = (index * 55) + "ms";
      const title = svg("title");
      const displayName = window.promptGuardTranslateCategory ? window.promptGuardTranslateCategory(item.name) : item.name;
      title.textContent = displayName + ": " + item.count;
      const circle = svg("circle", { cx: x, cy: y, r: radius, fill: colors[index % colors.length], opacity: ".20", stroke: colors[index % colors.length], "stroke-width": "1.5" });
      const inner = svg("circle", { cx: x, cy: y, r: Math.max(13, radius * .66), fill: colors[index % colors.length], opacity: ".10" });
      const num = svg("text", { x, y: y + 5, "text-anchor": "middle", class: "bubble-count" });
      num.textContent = item.count;
      const label = svg("text", { x, y: y + radius + 15, "text-anchor": "middle", class: "bubble-label" });
      const labelText = displayName.length > 18 ? displayName.slice(0, 16) + "…" : displayName;
      label.textContent = labelText;
      group.append(title, circle, inner, num, label);
      root.append(group);

      const legendItem = document.createElement("span");
      const dot = document.createElement("i");
      dot.style.background = colors[index % colors.length];
      const labelNode = document.createElement("span");
      labelNode.textContent = displayName + " · " + item.count;
      legendItem.append(dot, labelNode);
      legend.append(legendItem);
    });
  }
  async function loadDashboard() {
    try {
      const response = await fetch("/api/dashboard?range=" + encodeURIComponent($("#range").value), { headers: { "Accept": "application/json" } });
      if (!response.ok) throw new Error("Dashboard request failed");
      data = await response.json();
      renderMetrics(data);
      renderDistribution(data);
      renderRules(data);
      renderBubbles();
    } catch (error) {
      $("#dashboard-note").classList.add("notice-error");
      const note = $("#dashboard-note").querySelector("span:nth-child(2)");
      if (note) note.textContent = window.promptGuardGetLanguage && window.promptGuardGetLanguage() === "zh" ? "无法加载仪表盘数据，请刷新页面后重试。" : "Dashboard data could not be loaded. Please refresh and try again.";
    }
  }
  $("#range").addEventListener("change", loadDashboard);
  window.addEventListener("promptguard:languagechange", renderBubbles);
  document.querySelectorAll("[data-risk-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll("[data-risk-filter]").forEach((item) => item.classList.toggle("active", item === button));
      selectedLevel = button.dataset.riskFilter;
      renderBubbles();
    });
  });
  $("#seed").addEventListener("click", async () => {
    const button = $("#seed");
    button.disabled = true;
    try {
      await fetch("/api/seed-demo", { method: "POST" });
      await loadDashboard();
    } finally {
      button.disabled = false;
    }
  });
  loadDashboard();
})();
