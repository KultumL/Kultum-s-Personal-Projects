// assets/js/config.js

// Put your Render backend URL here once deployed (HTTPS)
const PROD_API_BASE = "https://YOUR-BACKEND.onrender.com";

function getApiBase() {
  const isLocal =
    location.hostname === "localhost" ||
    location.hostname === "127.0.0.1";

  // If you ever want to override manually:
  // window.API_BASE = "https://...";
  if (window.API_BASE) return window.API_BASE;

  return isLocal ? "http://127.0.0.1:8000" : PROD_API_BASE;
}

const API = getApiBase();
