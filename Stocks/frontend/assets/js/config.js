

const IS_LOCAL =
  location.hostname === "localhost" ||
  location.hostname === "127.0.0.1";

const API = IS_LOCAL
  ? "http://127.0.0.1:8000"
  : "https://stocksmart-fje8.onrender.com"; 

window.API = API;
