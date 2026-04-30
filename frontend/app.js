/* ============================================================
   AI-Based CLV Prediction System — app.js
   Handles: Stats fetch, Customer table, Chart, Predict form
   ============================================================ */

const API_BASE = "http://localhost:8001";

// ── Utility: Format currency ──────────────────────────────
function fmt(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

// ── Utility: Show toast notification ─────────────────────
function showToast(msg, type = "info") {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = `toast ${type === "error" ? "error" : ""}`;
  toast.textContent = msg;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}

// ── Utility: CLV → segment config ─────────────────────────
function getSegmentConfig(clv) {
  if (clv < 1500)      return { label: "Low Value",    color: "#ef4444", emoji: "📉", strategy: "Re-engage with offers" };
  if (clv < 6000)      return { label: "Medium Value", color: "#f59e0b", emoji: "📊", strategy: "Nurture & upsell"       };
                       return { label: "High Value",   color: "#10b981", emoji: "🏆", strategy: "Retain & reward"        };
}

// ── Animated number counter ────────────────────────────────
function animateCounter(el, target, prefix = "", suffix = "", duration = 900) {
  const start     = 0;
  const startTime = performance.now();
  function step(now) {
    const pct   = Math.min((now - startTime) / duration, 1);
    const eased = 1 - Math.pow(1 - pct, 3);          // ease-out cubic
    const value = Math.round(start + eased * target);
    el.textContent = prefix + value.toLocaleString() + suffix;
    if (pct < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

// ── Chart instance (kept globally for updates) ────────────
let segChart = null;

function renderChart(dist) {
  const ctx    = document.getElementById("seg-chart").getContext("2d");
  const labels = ["Low Value", "Medium Value", "High Value"];
  const data   = labels.map(l => dist[l] ?? 0);
  const colors = ["#ef4444", "#f59e0b", "#10b981"];

  if (segChart) segChart.destroy();

  segChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label     : "Customers",
        data,
        backgroundColor: colors.map(c => c + "cc"),
        borderColor    : colors,
        borderWidth    : 2,
        borderRadius   : 8,
      }],
    },
    options: {
      responsive         : true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.parsed.y} customers`,
          },
        },
      },
      scales: {
        x: {
          grid : { color: "rgba(255,255,255,0.05)" },
          ticks: { color: "#94a3b8", font: { family: "Inter", size: 12 } },
        },
        y: {
          grid       : { color: "rgba(255,255,255,0.05)" },
          ticks      : { color: "#94a3b8", font: { family: "Inter", size: 12 } },
          beginAtZero: true,
        },
      },
    },
  });
}

// ── Fetch & render stats cards ─────────────────────────────
async function loadStats() {
  try {
    const res  = await fetch(`${API_BASE}/stats`);
    if (!res.ok) throw new Error("Stats endpoint failed.");
    const data = await res.json();

    // Animate counters
    animateCounter(document.getElementById("s-total"), data.total_customers);
    animateCounter(document.getElementById("s-avg"),   data.avg_clv, "$");
    animateCounter(document.getElementById("s-high"),  data.high_value_pct, "", "%");
    animateCounter(document.getElementById("s-max"),   data.max_clv, "$");

    // Render chart
    renderChart(data.segment_distribution);
  } catch (err) {
    console.error("loadStats error:", err);
    showToast("⚠️ Could not reach backend. Is the server running?", "error");
    // Show fallback text in stat cards
    ["s-total","s-avg","s-high","s-max"].forEach(id => {
      document.getElementById(id).textContent = "N/A";
    });
  }
}

// ── Fetch & render customer table ─────────────────────────
async function loadCustomers() {
  const tbody = document.getElementById("table-body");
  try {
    const res  = await fetch(`${API_BASE}/customers?limit=40`);
    if (!res.ok) throw new Error("Customers endpoint failed.");
    const data = await res.json();

    if (!data.customers || data.customers.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;color:var(--text-muted);padding:24px">No data found.</td></tr>`;
      return;
    }

    tbody.innerHTML = data.customers.map(c => {
      const seg = getSegmentConfig(c.CLV);
      return `
        <tr>
          <td>${c.CustomerID}</td>
          <td>${c.Age}</td>
          <td>${c.PurchaseFrequency}</td>
          <td>$${parseFloat(c.AvgOrderValue).toFixed(2)}</td>
          <td>${c.Recency}d</td>
          <td>${c.Tenure}mo</td>
          <td class="clv-cell">${fmt(c.CLV)}</td>
          <td>
            <span class="seg-pill" style="background:${seg.color}22;color:${seg.color}">
              ${seg.emoji} ${seg.label}
            </span>
          </td>
        </tr>`;
    }).join("");
  } catch (err) {
    console.error("loadCustomers error:", err);
    tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;color:var(--text-muted);padding:24px">
      Backend not reachable — start the server first.</td></tr>`;
  }
}

// ── Handle Predict Form Submit ─────────────────────────────
document.getElementById("predict-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  // Gather inputs
  const payload = {
    age               : parseInt(document.getElementById("age").value),
    purchase_frequency: parseInt(document.getElementById("purchase_frequency").value),
    avg_order_value   : parseFloat(document.getElementById("avg_order_value").value),
    recency           : parseInt(document.getElementById("recency").value),
    tenure            : parseInt(document.getElementById("tenure").value),
  };

  // Basic client-side validation
  if (Object.values(payload).some(v => isNaN(v) || v <= 0)) {
    showToast("⚠️ Please fill in all fields with valid values.", "error");
    return;
  }

  // Show loading state
  const btn     = document.getElementById("predict-btn");
  const spinner = document.getElementById("btn-spinner");
  const label   = document.getElementById("btn-label");
  btn.disabled      = true;
  spinner.style.display = "block";
  label.textContent     = "Predicting…";

  try {
    const res  = await fetch(`${API_BASE}/predict`, {
      method : "POST",
      headers: { "Content-Type": "application/json" },
      body   : JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Prediction failed.");
    }

    const data = await res.json();
    showResult(data);
  } catch (err) {
    console.error("Predict error:", err);
    showToast(`❌ ${err.message}`, "error");
  } finally {
    btn.disabled          = false;
    spinner.style.display = "none";
    label.textContent     = "⚡ Predict CLV";
  }
});

// ── Render prediction result ───────────────────────────────
function showResult(data) {
  const seg = getSegmentConfig(data.predicted_clv);

  // Switch visibility
  document.getElementById("result-placeholder").style.display = "none";
  const content = document.getElementById("result-content");
  content.style.display = "flex";
  content.style.flexDirection = "column";
  content.style.alignItems = "center";

  // CLV amount
  document.getElementById("res-clv").textContent = fmt(data.predicted_clv);

  // Segment badge
  const badge = document.getElementById("res-badge");
  badge.textContent   = `${seg.emoji}  ${seg.label}`;
  badge.style.color   = seg.color;

  // Meta boxes
  document.getElementById("res-monthly").textContent  = fmt(data.monthly_value);
  document.getElementById("res-annual").textContent   = fmt(data.annual_value);
  document.getElementById("res-segment").textContent  = seg.label;
  document.getElementById("res-strategy").textContent = seg.strategy;

  // Re-trigger animation by cloning the node
  const clvEl = document.getElementById("res-clv");
  const clone = clvEl.cloneNode(true);
  clvEl.parentNode.replaceChild(clone, clvEl);

  showToast(`✅ CLV predicted: ${fmt(data.predicted_clv)} — ${seg.label}`);
}

// ── Bootstrap ─────────────────────────────────────────────
(async function init() {
  await Promise.all([loadStats(), loadCustomers()]);
})();
