/* Stock details + chart + alerts */

    function quickSearch(symbol){
      document.getElementById("stockSearch").value = symbol;
      searchAndViewStock();
    }

    async function searchAndViewStock() {
      const symbol = document.getElementById("stockSearch").value.trim();
      if (!symbol) return alert("Please enter a stock symbol or company name!");
      viewStockDetails(symbol);
      document.getElementById("stockSearch").value = "";
    }

    function toggleExplanation(metricId) {
      const explanation = document.getElementById(metricId);
      if (explanation) explanation.classList.toggle("show");
    }

    function toggleAlertForm() {
      const form = document.getElementById("alertForm");
      if (form) form.classList.toggle("show");
    }

    async function setAlert() {
      const symbol = currentSymbol;
      const targetPrice = parseFloat(document.getElementById("alertPrice").value);
      const direction = document.getElementById("alertDirection").value;

      if (!targetPrice || targetPrice <= 0) return alert("Please enter a valid price");

      try {
        const response = await fetch(`${API}/alerts/add`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ symbol, target_price: targetPrice, direction }),
        });
        const data = await response.json();

        if (data.success) {
          alert(`Alert set! We'll notify you when ${data.alert.symbol} goes ${direction} $${targetPrice}`);
          toggleAlertForm();
          updateStats();
          loadWatchlist();
        } else {
          alert("Error: " + data.error);
        }
      } catch (error) {
        alert("Error setting alert");
      }
    }

    // date formatting for news (fixes "weird" timestamps)

    function renderNews(newsArr){
      if (!Array.isArray(newsArr) || newsArr.length === 0) {
        return `
          <div class="news-box">
            <h3><i data-lucide="newspaper"></i> Latest news</h3>
            <div class="news-list">
              <div class="news-item">
                <div class="news-title">No news found right now.</div>
                <div class="news-meta">Try again later.</div>
              </div>
            </div>
          </div>
        `;
      }

      const items = newsArr.slice(0, 8).map((n) => {
        const title = escapeHtml(n.title || "Untitled");
        const source = escapeHtml(n.source || n.publisher || "");
        const when = formatNewsTime(n.published_at || n.publishedAt || n.time || n.datetime);
        const url = n.url || n.link || "";

        const metaParts = [];
        if (source) metaParts.push(source);
        if (when) metaParts.push(when);
        const meta = metaParts.join(" - ");

        return `
          <div class="news-item">
            <a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">
              <div class="news-title">${title}</div>
              <div class="news-meta">${escapeHtml(meta)}</div>
            </a>
          </div>
        `;
      }).join("");

      return `
        <div class="news-box">
          <h3><i data-lucide="newspaper"></i> Latest news</h3>
          <div class="news-list">${items}</div>
        </div>
      `;
    }

    // FIXED: pass button element in

    async function loadChart(symbol, period = "1mo", btnEl = null) {
      try {
        const response = await fetch(`${API}/stock/${encodeURIComponent(symbol)}/history?period=${encodeURIComponent(period)}`);
        const data = await response.json();

        if (data.error) {
          console.error("Error loading chart:", data.error);
          return;
        }

        // Update active button
        document.querySelectorAll(".period-btn").forEach((btn) => btn.classList.remove("active"));
        if (btnEl) btnEl.classList.add("active");

        const labels = (data.data || []).map((d) => d.date);
        const prices = (data.data || []).map((d) => d.close);

        if (currentChart) currentChart.destroy();

        const canvas = document.getElementById("priceChart");
        if (!canvas) return;

        const ctx = canvas.getContext("2d");
        currentChart = new Chart(ctx, {
          type: "line",
          data: {
            labels,
            datasets: [
              {
                label: "Price",
                data: prices,
                borderColor: "#1ef7b5",
                backgroundColor: "rgba(30, 247, 181, 0.12)",
                borderWidth: 2,
                fill: true,
                tension: 0.35,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false },
              tooltip: {
                mode: "index",
                intersect: false,
                callbacks: {
                  label: (context) => "$" + context.parsed.y.toFixed(2),
                },
              },
            },
            scales: {
              x: {
                ticks: { color: "rgba(233,236,243,0.55)" },
                grid: { color: "rgba(255,255,255,0.06)" }
              },
              y: {
                ticks: {
                  color: "rgba(233,236,243,0.55)",
                  callback: (value) => "$" + Number(value).toFixed(2),
                },
                grid: { color: "rgba(255,255,255,0.06)" }
              },
            },
          },
        });
      } catch (error) {
        console.error("Error loading chart:", error);
      }
    }

    async function viewStockDetails(symbol) {
      currentSymbol = symbol;
      setContext(symbol);

      const modal = document.getElementById("detailModal");
      const content = document.getElementById("modalContent");

      modal.style.display = "block";
      content.innerHTML = '<div class="loading"><div class="spinner"></div><p>Loading details...</p></div>';

      try {
        const response = await fetch(`${API}/stock/${encodeURIComponent(symbol)}/details`);
        const data = await response.json();

        if (data.error) {
          content.innerHTML = `<div class="loading"><p style="color: rgba(255,92,108,0.95); font-weight:900;">Error: ${escapeHtml(data.error)}</p></div>`;
          return;
        }

        const change = typeof data.change_percent === "number" ? data.change_percent : 0;
        const pill = pctPill(change);

        const explanations = data.metric_explanations || {};
        const priceText = money(typeof data.price === "number" ? data.price : null);
        const prevCloseText = money(typeof data.previous_close === "number" ? data.previous_close : null);

        // news comes from backend: data.news
        const newsHtml = renderNews(data.news);

        content.innerHTML = `
          <div class="detail-header">
            <div class="detail-left">
              <h2>${escapeHtml(data.symbol)}</h2>
              <p>${escapeHtml(data.company_name || data.symbol)}</p>

              <div class="price-row">
                <div class="big-price">${priceText}</div>
                ${pill}
              </div>
            </div>

            <div class="detail-right">
              <button class="btn btn-primary" onclick="addToWatchlist('${escapeHtml(data.symbol)}')"><i data-lucide="star"></i> Add to Watchlist</button>
              <button class="btn" onclick="toggleAlertForm()"><i data-lucide="bell"></i> Set Alert</button>
            </div>
          </div>

          <div id="alertForm" class="chart-section" style="display:none; margin-top:14px;">
            <div style="display:flex; justify-content:space-between; align-items:center; gap:10px; flex-wrap:wrap;">
              <h3 style="font-size:1.08rem;">Set Price Alert</h3>
              <button class="btn" onclick="toggleAlertForm()">Close</button>
            </div>

            <div style="margin-top:12px; display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
              <div>
                <div style="color: rgba(233,236,243,0.60); font-weight:800; margin-bottom:8px;">Direction</div>
                <select id="alertDirection" style="width:100%; padding:11px 12px; border-radius:14px; border:1px solid rgba(255,255,255,0.10); background: rgba(0,0,0,0.18); color: rgba(233,236,243,0.85);">
                  <option value="below">Below</option>
                  <option value="above">Above</option>
                </select>
              </div>
              <div>
                <div style="color: rgba(233,236,243,0.60); font-weight:800; margin-bottom:8px;">Target price</div>
                <input type="number" id="alertPrice" step="0.01" placeholder="e.g., 250.00"
                  style="width:100%; padding:11px 12px; border-radius:14px; border:1px solid rgba(255,255,255,0.10); background: rgba(0,0,0,0.18); color: rgba(233,236,243,0.85); outline:none;">
              </div>
            </div>

            <button class="btn btn-primary" style="margin-top:12px;" onclick="setAlert()">Create Alert</button>
          </div>

          <div class="chart-section">
            <div class="chart-head">
              <h3><i data-lucide="line-chart"></i> Price History</h3>
              <div class="period-row">
                <button class="period-btn" onclick="loadChart('${escapeHtml(data.symbol)}', '5d', this)">5D</button>
                <button class="period-btn active" onclick="loadChart('${escapeHtml(data.symbol)}', '1mo', this)">1M</button>
                <button class="period-btn" onclick="loadChart('${escapeHtml(data.symbol)}', '3mo', this)">3M</button>
                <button class="period-btn" onclick="loadChart('${escapeHtml(data.symbol)}', '1y', this)">1Y</button>
              </div>
            </div>
            <canvas id="priceChart"></canvas>
          </div>

          <div class="metrics">
            <div class="metric-card">
              <div class="metric-top">
                <div class="metric-label">Previous Close</div>
                <div class="help-icon" onclick="toggleExplanation('exp-prev-close')">?</div>
              </div>
              <div class="metric-value">${prevCloseText}</div>
              <div id="exp-prev-close" class="metric-explanation">
                This is what the stock cost when the market closed yesterday. It's the baseline for today's changes.
              </div>
            </div>

            <div class="metric-card">
              <div class="metric-top">
                <div class="metric-label">Day High / Low</div>
                <div class="help-icon" onclick="toggleExplanation('exp-day-range')">?</div>
              </div>
              <div class="metric-value">
                ${money(typeof data.day_high === "number" ? data.day_high : null)} /
                ${money(typeof data.day_low === "number" ? data.day_low : null)}
              </div>
              <div id="exp-day-range" class="metric-explanation">
                The highest and lowest prices the stock hit today. A big range means it's bouncing around a lot.
              </div>
            </div>

            <div class="metric-card">
              <div class="metric-top">
                <div class="metric-label">52 Week High / Low</div>
                <div class="help-icon" onclick="toggleExplanation('exp-52week')">?</div>
              </div>
              <div class="metric-value">
                ${money(typeof data.week_52_high === "number" ? data.week_52_high : null)} /
                ${money(typeof data.week_52_low === "number" ? data.week_52_low : null)}
              </div>
              <div id="exp-52week" class="metric-explanation">
                ${escapeHtml(explanations.week_52_range || "The highest and lowest prices in the past year. Shows the full range of movement.")}
              </div>
            </div>

            <div class="metric-card">
              <div class="metric-top">
                <div class="metric-label">P/E Ratio</div>
                <div class="help-icon" onclick="toggleExplanation('exp-pe')">?</div>
              </div>
              <div class="metric-value">${typeof data.pe_ratio === "number" ? data.pe_ratio.toFixed(2) : "N/A"}</div>
              <div id="exp-pe" class="metric-explanation">
                ${escapeHtml(explanations.pe_ratio || "Price-to-Earnings ratio: how expensive the stock is compared to its profits.")}
              </div>
            </div>

            <div class="metric-card">
              <div class="metric-top">
                <div class="metric-label">Market Cap</div>
                <div class="help-icon" onclick="toggleExplanation('exp-market-cap')">?</div>
              </div>
              <div class="metric-value">
                ${typeof data.market_cap === "number" ? "$" + (data.market_cap / 1e9).toFixed(1) + "B" : "N/A"}
              </div>
              <div id="exp-market-cap" class="metric-explanation">
                ${escapeHtml(explanations.market_cap || "The total value of all shares. Bigger companies are often more stable.")}
              </div>
            </div>

            <div class="metric-card">
              <div class="metric-top">
                <div class="metric-label">Volume</div>
                <div class="help-icon" onclick="toggleExplanation('exp-volume')">?</div>
              </div>
              <div class="metric-value">
                ${typeof data.volume === "number" ? (data.volume / 1e6).toFixed(1) + "M" : "N/A"}
              </div>
              <div id="exp-volume" class="metric-explanation">
                How many shares were traded today. High volume means lots of buying and selling activity.
              </div>
            </div>
          </div>

          <div class="explain-box">
            <h3><i data-lucide="sparkles"></i> What does this mean?</h3>
            <p>${escapeHtml(data.main_explanation || "No explanation available right now.")}</p>
          </div>

          ${newsHtml}
        `;

        if (window.lucide) window.lucide.createIcons();

        // show/hide the alert form (keep your old function name)
        // we do it by toggling display because we re-used chart-section styling
        const oldToggle = toggleAlertForm;
        window.toggleAlertForm = function(){
          const form = document.getElementById("alertForm");
          if (!form) return;
          form.style.display = (form.style.display === "none" || form.style.display === "") ? "block" : "none";
        };

        // Load default chart once canvas exists
        setTimeout(() => {
          const activeBtn = content.querySelector(".period-btn.active");
          loadChart(data.symbol, "1mo", activeBtn);
        }, 50);

      } catch (error) {
        console.error(error);
        content.innerHTML = '<div class="loading"><p style="color: rgba(255,92,108,0.95); font-weight:900;">Error loading stock details</p></div>';
      }
    }

    function closeModal() {
      document.getElementById("detailModal").style.display = "none";
      if (currentChart) {
        currentChart.destroy();
        currentChart = null;
      }
      clearContext();
    }

    window.onclick = function (e) {
      const modal = document.getElementById("detailModal");
      if (e.target === modal) closeModal();
    };

    // ============================================
    // AI CHAT FUNCTIONALITY (unchanged logic)
    // ============================================

