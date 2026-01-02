/* Bootstrapping */
window.addEventListener("load", () => {
  // render lucide icons in static HTML
  if (typeof refreshLucide === "function") refreshLucide();

  // initial fetches
  if (typeof loadWatchlist === "function") loadWatchlist();
  if (typeof updateStats === "function") updateStats();
});

// Enter-to-search
const searchEl = document.getElementById("stockSearch");
if (searchEl) {
  searchEl.addEventListener("keypress", (e) => {
    if (e.key === "Enter") searchAndViewStock();
  });
}

// Enter-to-send in chat
const chatInputEl = document.getElementById("chatInput");
if (chatInputEl) {
  chatInputEl.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
  });
}
