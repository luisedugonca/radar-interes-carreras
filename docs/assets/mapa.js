// Mapa radial interactivo. Un solo componente para dos usos:
//   - el mapa agéntico (cómo trabajamos)     -> datos de data/mapa.json
//   - el mapa de interés (qué busca la gente) -> datos de una consulta
// Recibe: { centro:{titulo,sub}, ramas:[{id,titulo,color,nodos:[{id,titulo,icono}]}] }
const NS = "http://www.w3.org/2000/svg";
const R0 = 152, PASO_R = 86, MAX_NODOS = 5;

function el(nombre, attrs = {}, padre) {
  const e = document.createElementNS(NS, nombre);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  if (padre) padre.appendChild(e);
  return e;
}
const polar = (r, a) => [r * Math.cos(a), r * Math.sin(a)];
const f = (n) => n.toFixed(1);

function partir(texto, largo = 16) {
  const lineas = [""];
  for (const palabra of String(texto).split(/\s+/)) {
    const ult = lineas[lineas.length - 1];
    if (!ult) lineas[lineas.length - 1] = palabra;
    else if ((ult + " " + palabra).length <= largo) lineas[lineas.length - 1] = ult + " " + palabra;
    else lineas.push(palabra);
  }
  if (lineas.length > 2) { lineas.length = 2; lineas[1] = lineas[1].slice(0, largo - 1) + "…"; }
  return lineas.map((l) => (l.length > largo + 3 ? l.slice(0, largo + 2) + "…" : l));
}

export function renderMapa(svg, datos, alSeleccionar) {
  svg.replaceChildren();
  svg.setAttribute("viewBox", "-575 -575 1150 1150");
  svg.setAttribute("role", "group");
  const ramas = datos.ramas;
  const n = Math.max(ramas.length, 1);
  const paso = (2 * Math.PI) / n;
  const quieto = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const defs = el("defs", {}, svg);
  const grad = el("radialGradient", { id: "g-centro" }, defs);
  el("stop", { offset: "0", "stop-color": "#4f9bff" }, grad);
  el("stop", { offset: "1", "stop-color": "#1546c0" }, grad);

  const grupos = [];
  ramas.forEach((rama, i) => {
    const a = -Math.PI / 2 + i * paso;
    const g = el("g", { class: "rama", "data-rama": rama.id }, svg);
    grupos.push(g);

    // Sector de fondo
    const [x1, y1] = polar(800, a - paso / 2), [x2, y2] = polar(800, a + paso / 2);
    el("path", { class: "sector", fill: rama.color,
      d: n === 1 ? "M-800,0A800,800 0 1 1 800,0A800,800 0 1 1 -800,0Z"
        : `M0,0L${f(x1)},${f(y1)}A800,800 0 0 1 ${f(x2)},${f(y2)}Z` }, g);

    // Posiciones: la cadena serpentea hacia afuera
    const vaiven = Math.min(paso * 0.21, 0.26);
    const signo = i % 2 ? 1 : -1;
    const nodos = rama.nodos.slice(0, MAX_NODOS);
    const pos = nodos.map((_, k) => polar(R0 + k * PASO_R, k === 0 ? a : a + signo * (k % 2 ? 1 : -1) * vaiven * (0.55 + 0.1 * k)));

    // Lazos
    let camino = `M0,0L${f(pos[0]?.[0] ?? 0)},${f(pos[0]?.[1] ?? 0)}`;
    if (pos.length) el("path", { class: "lazo", stroke: rama.color, d: camino }, g);
    for (let k = 1; k < pos.length; k++) {
      const [cx, cy] = polar(R0 + (k - 0.5) * PASO_R, a - signo * (k % 2 ? 1 : -1) * vaiven * 0.5);
      const tramo = `Q${f(cx)},${f(cy)} ${f(pos[k][0])},${f(pos[k][1])}`;
      el("path", { class: "lazo hijo-l", stroke: rama.color, d: `M${f(pos[k - 1][0])},${f(pos[k - 1][1])}${tramo}` }, g);
      camino += tramo;
    }
    if (!quieto && pos.length > 1) {
      const pulso = el("circle", { class: "pulso", r: 3.4, opacity: ".85" }, g);
      el("animateMotion", { dur: `${3 + pos.length * 0.5}s`, begin: `${(i * 0.45).toFixed(2)}s`, repeatCount: "indefinite", path: camino }, pulso);
    }

    // Nodos
    nodos.forEach((nodo, k) => {
      const [x, y] = pos[k];
      const r = k === 0 ? 27 : 16 + Math.round(9 * (nodo.peso ?? 0.55));
      const gn = el("g", { class: `nodo ${k === 0 ? "cabeza" : "hijo"}`, tabindex: "0", role: "button",
        "aria-label": `${rama.titulo}: ${nodo.titulo}`, transform: `translate(${f(x)},${f(y)})` }, g);
      if (nodo.destacado) el("circle", { class: "aro", r: r + 7, stroke: rama.color }, gn);
      el("circle", { class: "disco", r, stroke: rama.color }, gn);
      el("text", { class: "ico", fill: rama.color }, gn).textContent = nodo.icono ?? "";
      if (k === 0) {
        el("circle", { cx: -r * 0.72, cy: -r * 0.72, r: 10, fill: rama.color }, gn);
        el("text", { class: "num", x: -r * 0.72, y: -r * 0.72 }, gn).textContent = i + 1;
      }
      partir(nodo.titulo).forEach((linea, j) => {
        el("text", { class: "rot", y: r + 16 + j * 14.5 }, gn).textContent = linea;
      });
      const elegir = () => seleccionar(rama.id, nodo.id, true);
      gn.addEventListener("click", elegir);
      gn.addEventListener("keydown", (ev) => { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); elegir(); } });
    });
    g.querySelector(".sector").addEventListener("click", () => seleccionar(rama.id, rama.nodos[0]?.id, true));
  });

  // Centro
  const c = el("g", { class: "centro" }, svg);
  el("circle", { class: "halo", r: 58 }, c);
  el("circle", { r: 58, fill: "url(#g-centro)", stroke: "#9cc4ff", "stroke-width": 2 }, c);
  const lt = partir(datos.centro.titulo, 13);
  lt.forEach((l, j) => { el("text", { class: "centro-t", y: (datos.centro.sub ? -8 : 2) + (j - (lt.length - 1) / 2) * 16 }, c).textContent = l; });
  if (datos.centro.sub) el("text", { class: "centro-s", y: 12 + (lt.length - 1) * 8 + 8 }, c).textContent = datos.centro.sub;

  function seleccionar(idRama, idNodo, avisar) {
    grupos.forEach((g) => {
      g.classList.toggle("sel", g.dataset.rama === idRama);
      g.querySelectorAll(".nodo").forEach((nd) => nd.classList.remove("sel"));
    });
    const rama = ramas.find((r) => r.id === idRama);
    if (!rama) return;
    const k = Math.max(0, rama.nodos.findIndex((x) => x.id === idNodo));
    grupos[ramas.indexOf(rama)].querySelectorAll(".nodo")[k]?.classList.add("sel");
    if (avisar && alSeleccionar) alSeleccionar(rama, rama.nodos[k]);
  }
  return { seleccionar };
}
