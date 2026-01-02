/* Watchlist + stats */

async function updateStats() {
  try {
    const response = await fetch(`${API}/watchlist/all`);
    const data = await response.json();

    document.getElementById("watchlistCount").textContent = data.total || 0;

    let alertCount = 0;
    if (data.watchlist) {
      data.watchlist.forEach((stock) => {
        if (stock.alerts) alertCount += stock.alerts.length;
      });
    }
    document.getElementById("alertCount").textContent = alertCount;
  } catch (error) {
    console.error("Error updating stats:", error);
  }
}

async function loadWatchlist() {
  const grid = document.getElementById("stockGrid");
  grid.innerHTML = '<div class="loading"><div class="spinner"></div><p>Loading...</p></div>';

  try {
    const response = await fetch(`${API}/watchlist/all`);
    const data = await response.json();

    if (data.watchlist && data.watchlist.length > 0) {
      grid.innerHTML = "";
      data.watchlist.forEach((stock) => {
        grid.innerHTML += createStockCard(stock);
      });
    } else {
      grid.innerHTML = `
        <div class="empty">
          <h3>Your watchlist is empty</h3>
          <p>Search for a stock above and add it to start tracking.</p>
        </div>
      `;
    }

    // ✅ this was missing / causing ReferenceError in your try block
    refreshLucide();

    updateStats();
  } catch (error) {
    console.error(error);
    grid.innerHTML =
      '<div class="empty"><h3>Couldn\\\'t load watchlist</h3><p>Make sure your backend server is running.</p></div>';
  }
}

function createStockCard(stock) {
  const change = typeof stock.change_percent === "number" ? stock.change_percent : 0;
  const priceText = money(typeof stock.price === "number" ? stock.price : null);

  const alertBadge = stock.has_alert
    ? `<div class="alert-badge"><i data-lucide="bell"></i> ${stock.alerts?.length || 0}</div>`
    : "";

  return `
    <div class="card" onclick="viewStockDetails('${stock.symbol}')">
      ${alertBadge}
      <div class="card-top">
        <div>
          <div class="sym">${stock.symbol}</div>
          <div class="co">${stock.company_name || stock.symbol}</div>
        </div>
        <button class="remove-btn" aria-label="Remove"
          onclick="event.stopPropagation(); removeFromWatchlist('${stock.symbol}')">
          <i data-lucide="x"></i>
        </button>
      </div>

      <div class="price">${priceText}</div>
      ${pctPill(change)}
    </div>
  `;
}

async function removeFromWatchlist(symbol) {
  if (!confirm(`Remove ${symbol} from watchlist?`)) return;

  try {
    const response = await fetch(`${API}/watchlist/remove/${symbol}`, { method: "DELETE" });
    const data = await response.json();

    if (data.success) loadWatchlist();
    else alert("Error removing stock: " + data.error);
  } catch (error) {
    alert("Error removing stock");
  }
}

async function addToWatchlist(symbol) {
  try {
    const response = await fetch(`${API}/watchlist/add`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ symbol }),
    });
    const data = await response.json();

    if (data.success) {
      alert(`Added ${data.symbol} to watchlist.`);
      loadWatchlist();
      updateStats();
    } else {
      alert("Error: " + data.error);
    }
  } catch (error) {
    alert("Error adding to watchlist");
  }
}
