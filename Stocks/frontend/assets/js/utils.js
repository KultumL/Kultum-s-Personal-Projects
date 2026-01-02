/* Utilities */

function money(val) {
  return typeof val === "number" && isFinite(val) ? "$" + val.toFixed(2) : "N/A";
}

// Lucide icons are injected by replacing <i data-lucide="..."></i> nodes with SVG.
// Call this after any innerHTML updates that include data-lucide.
function refreshLucide() {
  try {
    if (window.lucide && typeof window.lucide.createIcons === "function") {
      window.lucide.createIcons();
    }
  } catch (_) {
    // no-op
  }
}

function pctPill(change) {
  const cls = change > 0 ? "pos" : change < 0 ? "neg" : "neu";
  const iconName = change > 0 ? "trending-up" : change < 0 ? "trending-down" : "minus";

  return `
    <div class="pill ${cls}">
      <i data-lucide="${iconName}"></i>
      ${Math.abs(change).toFixed(2)}%
    </div>
  `;
}

function formatNewsTime(input) {
  if (!input) return "";
  let d = null;

  if (typeof input === "number") {
    d = new Date(input * 1000);
  } else if (typeof input === "string") {
    const s = input.trim();
    if (/^\d+$/.test(s)) {
      const num = Number(s);
      d = new Date(num < 1e12 ? num * 1000 : num);
    } else {
      d = new Date(s);
    }
  }

  if (!d || isNaN(d.getTime())) return "";

  return d.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function escapeHtml(str) {
  return String(str || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
