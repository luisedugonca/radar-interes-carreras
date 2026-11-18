// Claro / oscuro. Se carga en el <head> para que la página no parpadee al abrir.
(function () {
  var CLAVE = "radar-tema";
  try { var guardado = localStorage.getItem(CLAVE); if (guardado) document.documentElement.dataset.theme = guardado; } catch (e) {}
  function actual() {
    return document.documentElement.dataset.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  }
  function rotular(b) {
    var o = actual() === "dark", t = o ? "Cambiar a modo claro" : "Cambiar a modo oscuro";
    b.textContent = o ? "☀" : "☾"; b.setAttribute("aria-label", t); b.title = t;
  }
  document.addEventListener("DOMContentLoaded", function () {
    var b = document.getElementById("btn-tema");
    if (!b) return;
    rotular(b);
    b.addEventListener("click", function () {
      var nuevo = actual() === "dark" ? "light" : "dark";
      document.documentElement.dataset.theme = nuevo;
      try { localStorage.setItem(CLAVE, nuevo); } catch (e) {}
      rotular(b);
    });
  });
})();
