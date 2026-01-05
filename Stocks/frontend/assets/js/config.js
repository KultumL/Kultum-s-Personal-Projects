

const IS_LOCAL =
  location.hostname === "localhost" ||
  location.hostname === "127.0.0.1";

const API = IS_LOCAL
  ? "http://127.0.0.1:8000"
  : "https://YOUR-RENDER-BACKEND.onrender.com"; // <-- replace

window.API = API;
