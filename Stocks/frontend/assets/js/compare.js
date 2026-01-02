/* Compare panel (2-3 stocks) */

function _cmpNormalize(s){
  return String(s || "").trim().toUpperCase();
}

function _cmpRaw(id){
  return String(document.getElementById(id)?.value || "").trim();
}

function _cmpLooksLikeTicker(s){
  const t = String(s || "").trim().toUpperCase();
  return /^[A-Z]{1,5}(?:[.-][A-Z]{1,2})?$/.test(t);
}

async function _cmpResolveInput(raw){
  const txt = String(raw || "").trim();
  if (!txt) return null;
  if (_cmpLooksLikeTicker(txt)) return { input: txt, symbol: txt.toUpperCase(), resolved: false };

  // Resolve company name -> ticker using backend /search
  const res = await fetch(`${API}/search?q=${encodeURIComponent(txt)}`);
  const data = await res.json();
  const first = (data && data.results && data.results[0]) ? data.results[0] : null;
  if (!first || !first.symbol) throw new Error(`No match for "${txt}"`);
  return { input: txt, symbol: String(first.symbol).toUpperCase(), resolved: true, name: first.name || first.symbol };
}

function _cmpGetSymbols(){
  const s1 = _cmpRaw("cmp1");
  const s2 = _cmpRaw("cmp2");
  const s3 = _cmpRaw("cmp3");

  const symbols = [s1, s2, s3].filter(Boolean);

  // de-dupe while preserving order
  const seen = new Set();
  const uniq = [];
  for (const s of symbols){
    if (seen.has(s)) continue;
    seen.add(s);
    uniq.push(s);
  }
  return uniq;
}

function _cmpFillNext(symbol){
  const ids = ["cmp1","cmp2","cmp3"];
  for (const id of ids){
    const el = document.getElementById(id);
    if (el && !_cmpNormalize(el.value)){
      el.value = symbol;
      return;
    }
  }
  // if all full, replace the 3rd
  const el3 = document.getElementById("cmp3");
  if (el3) el3.value = symbol;
}

function clearCompare(){
  ["cmp1","cmp2","cmp3"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = "";
  });
  const out = document.getElementById("compareResult");
  if (out){
    out.classList.add("is-hidden");
    out.innerHTML = "";
  }
}

function swapCompare(){
  const a = document.getElementById("cmp1");
  const b = document.getElementById("cmp2");
  if (!a || !b) return;
  const tmp = a.value;
  a.value = b.value;
  b.value = tmp;
}

function _cmpMoney(x){
  if (x == null || x === "" || Number.isNaN(Number(x))) return "-";
  return `$${Number(x).toFixed(2)}`;
}
function _cmpPct(x){
  if (x == null || x === "" || Number.isNaN(Number(x))) return "-";
  const n = Number(x);
  const sign = n > 0 ? "+" : "";
  return `${sign}${n.toFixed(2)}%`;
}
function _cmpCompactInt(x){
  if (x == null || x === "" || Number.isNaN(Number(x))) return "-";
  try { return Number(x).toLocaleString(); } catch { return String(x); }
}

function _cmpRenderResult(payload){
  const out = document.getElementById("compareResult");
  if (!out) return;

  if (!payload || !payload.success){
    out.classList.remove("is-hidden");
    out.innerHTML = `<div class="compare-note">${payload?.error || "Could not compare right now."}</div>`;
    return;
  }

  const rows = (payload.stocks || []).map(s => {
    const sym = s.symbol || "-";
    const name = s.name || sym;
    const price = _cmpMoney(s.price);
    const change = _cmpPct(s.change);
    const pe = (s.pe_ratio == null) ? "-" : String(s.pe_ratio);
    const mc = _cmpCompactInt(s.market_cap);

    return `
      <tr>
        <td><b>${sym}</b><div style="color:rgba(233,236,243,0.65);font-size:12px;margin-top:4px;">${name}</div></td>
        <td>${price}</td>
        <td>${change}</td>
        <td>${pe}</td>
        <td>${mc}</td>
      </tr>
    `;
  }).join("");

  out.classList.remove("is-hidden");
  out.innerHTML = `
    <table class="compare-table">
      <thead>
        <tr>
          <th>Stock</th>
          <th>Price</th>
          <th>Change</th>
          <th>P/E</th>
          <th>Market cap</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
    <div class="compare-note">${payload.comparison || ""}</div>
  `;

  if (window.lucide) lucide.createIcons();
}

async function runCompare(){
  const inputs = _cmpGetSymbols();
  const out = document.getElementById("compareResult");

  if (inputs.length < 2){
    if (out){
      out.classList.remove("is-hidden");
      out.innerHTML = `<div class="compare-note">Add at least 2 stocks to compare.</div>`;
    }
    toastInfo("Add at least two stocks (tickers or company names).", "Compare");
    return;
  }

  if (out){
    out.classList.remove("is-hidden");
    out.innerHTML = `<div class="compare-note">Resolving symbols...</div>`;
  }

  try{
    const resolved = await Promise.all(inputs.slice(0,3).map(_cmpResolveInput));

    // de-dupe while preserving order
    const seen = new Set();
    const uniq = [];
    const mappings = [];
    for (const r of resolved){
      if (!r || !r.symbol) continue;
      const sym = r.symbol.toUpperCase();
      if (seen.has(sym)) continue;
      seen.add(sym);
      uniq.push(sym);
      if (r.resolved) mappings.push(`${r.input} -> ${sym}`);
    }

    if (uniq.length < 2){
      if (out){
        out.innerHTML = `<div class="compare-note">Couldn't resolve enough symbols to compare.</div>`;
      }
      toastError("Couldn't resolve enough symbols to compare.", "Compare");
      return;
    }

    if (out){
      const mapHtml = mappings.length
        ? `<div class="compare-map">Resolved: ${mappings.map(m => `<span>${escapeHtml(m)}</span>`).join("")}</div>`
        : "";
      out.innerHTML = `<div class="compare-note">Comparing ${uniq.join(" vs ")}...</div>${mapHtml}`;
    }

    const res = await fetch(`${API}/chat/compare`, {
      method: "POST",
      headers: { "Content-Type":"application/json" },
      body: JSON.stringify({ symbols: uniq })
    });
    const data = await res.json();
    _cmpRenderResult(data);
  }catch(err){
    console.error(err);
    _cmpRenderResult({ success:false, error: err?.message || "Could not reach the backend for compare." });
    toastError(err?.message || "Compare failed.", "Compare");
  }
}

async function initCompare(){
  // Populate datalist + clickable chips from watchlist
  const listEl = document.getElementById("tickerList");
  const chipsEl = document.getElementById("compareChips");

  try{
    const res = await fetch(`${API}/watchlist/all`);
    const data = await res.json();
    const items = data.watchlist || [];
    const symbols = items.map(x => (x.symbol || "").toUpperCase()).filter(Boolean);

    if (listEl){
      listEl.innerHTML = items.map(x => {
        const s = (x.symbol || "").toUpperCase();
        const name = x.company_name || x.company || x.name || "";
        if (!s) return "";
        return `<option value="${s}">${escapeHtml(name)}</option>`;
      }).join("");
    }
    if (chipsEl){
      chipsEl.innerHTML = symbols.map(s => `
        <button class="compare-chip" type="button" onclick="_cmpFillNext('${s}');">
          <i data-lucide="plus"></i> ${s}
        </button>
      `).join("");
    }
  }catch(err){
    // It's okay if this fails; panel still works with manual input
    console.warn("compare init failed", err);
  }

  // Enter to compare
  ["cmp1","cmp2","cmp3"].forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener("keydown", (e)=>{
      if (e.key === "Enter") runCompare();
    });
  });

  if (window.lucide) lucide.createIcons();
}

window.addEventListener("load", () => {
  initCompare();
});
