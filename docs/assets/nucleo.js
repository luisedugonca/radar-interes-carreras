// Núcleo compartido de la web: lectura de datos y el modo "en vivo".
// Las reglas (semillas e intenciones) NO viven acá: se leen de data/reglas.json,
// el mismo archivo que usa el colector en Python.

export async function leerJSON(ruta) {
  const r = await fetch(ruta, { cache: "no-store" });
  if (!r.ok) throw new Error(`No se pudo leer ${ruta} (HTTP ${r.status})`);
  return r.json();
}

// Igual que normalizar() en colector/comun.py
export function normalizar(texto) {
  return String(texto).toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/\s+/g, " ").trim();
}

const VACIAS = new Set(["de", "del", "la", "el", "los", "las", "en", "y", "para", "con", "por", "un", "una", "que", "a", "o"]);
export const tokensTema = (tema) => normalizar(tema).split(" ").filter((t) => !VACIAS.has(t) && t.length >= 3);

export function limpiarTema(crudo) {
  const tema = String(crudo).replace(/^\s*consulta\s*:\s*/i, "").replace(/[^0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ \-]/g, " ").replace(/\s+/g, " ").trim().toLowerCase();
  if (tema.length < 3 || tema.length > 60) throw new Error("Escribí un tema de entre 3 y 60 letras.");
  return tema;
}

export function clasificar(textoNorm, reglas) {
  for (const i of reglas.intenciones) if (i.patron && new RegExp(i.patron).test(textoNorm)) return i.id;
  return "otros";
}

// Igual que resumir_puestos() y orden_frase() en colector/transformar.py
export function resumirPuestos(p) {
  if (!p.length) return { pos_promedio: null, pos_mejor: null, veces_top3: 0, veces_top10: 0 };
  return { pos_promedio: Math.round((10 * p.reduce((a, b) => a + b, 0)) / p.length) / 10, pos_mejor: Math.min(...p),
    veces_top3: p.filter((x) => x <= 3).length, veces_top10: p.filter((x) => x <= 10).length };
}
export const ordenFrase = (a, b) => b.apariciones - a.apariciones || (b.veces_top3 ?? 0) - (a.veces_top3 ?? 0)
  || (a.pos_promedio ?? 99) - (b.pos_promedio ?? 99) || (a.texto < b.texto ? -1 : a.texto > b.texto ? 1 : 0);

const PAUSA_MS = 150;

// Autocompletar de Google por JSONP (el servicio no permite fetch desde otra web).
function jsonp(consulta, pais) {
  return new Promise((resolver) => {
    const nombre = "__radar_" + Math.random().toString(36).slice(2);
    const s = document.createElement("script");
    const fin = (valor) => { delete window[nombre]; s.remove(); clearTimeout(reloj); resolver(valor); };
    const reloj = setTimeout(() => fin(null), 8000);
    window[nombre] = (datos) => fin(datos);
    s.onerror = () => fin(null);
    s.src = "https://suggestqueries.google.com/complete/search?client=chrome" +
      `&hl=${pais.hl}&gl=${pais.gl}&ie=utf-8&oe=utf-8&q=${encodeURIComponent(consulta)}&callback=${nombre}`;
    document.head.appendChild(s);
  });
}

// Corre en el navegador de quien mira: mismas reglas, menos semillas, nada se guarda.
export async function consultaEnVivo(temaCrudo, reglas, alAvanzar) {
  const tema = limpiarTema(temaCrudo);
  const temaNorm = normalizar(tema), tokens = tokensTema(tema);
  const semillas = [];
  for (const grupo of reglas.en_vivo) for (const p of reglas.semillas[grupo]) semillas.push({ grupo, consulta: p.replace("{tema}", tema) });

  const grupos = new Map();
  let conRespuesta = 0, rechazadas = 0;
  for (const [n, semilla] of semillas.entries()) {
    alAvanzar?.(n + 1, semillas.length);
    if (n) await new Promise((r) => setTimeout(r, PAUSA_MS));   // pausa entre pedidos: no saturar a Google
    const datos = await jsonp(semilla.consulta, reglas.pais);
    if (!datos) continue;
    conRespuesta++;
    const tipos = datos[4]?.["google:suggesttype"] ?? [];
    for (const [i, crudo] of (datos[1] ?? []).entries()) {
      const texto = String(crudo).trim();
      const norm = normalizar(texto);
      const valida = norm && (tipos[i] ?? "QUERY") === "QUERY" && texto.length <= reglas.validacion.largo_maximo && tokens.some((t) => norm.includes(t));
      if (!valida) { rechazadas++; continue; }
      if (norm === temaNorm) continue;
      const g = grupos.get(norm) ?? { texto, semillas: [], fuentes: ["google"] };
      if (!g.semillas.includes(semilla.consulta)) { g.semillas.push(semilla.consulta); (g._puestos ??= []).push(i + 1); }
      grupos.set(norm, g);
    }
  }

  const porIntencion = Object.fromEntries(reglas.intenciones.map((i) => [i.id, []]));
  const inst = {};
  for (const [norm, g] of grupos) {
    const resto = norm.replaceAll(temaNorm, " ");
    g.apariciones = g.semillas.length;
    Object.assign(g, resumirPuestos(g._puestos ?? []));
    delete g._puestos;
    g.instituciones = reglas.instituciones_uy.filter((i) => new RegExp(i.patron).test(resto)).map((i) => i.id);
    g.instituciones.forEach((id) => { inst[id] = (inst[id] ?? 0) + 1; });
    porIntencion[clasificar(resto, reglas)].push(g);
  }
  const total = grupos.size;
  const quien = { familia: 0, estudiante: 0, ambos: 0, ninguno: 0 };
  const intenciones = reglas.intenciones.map((r) => {
    const sugerencias = porIntencion[r.id].sort(ordenFrase);
    quien[r.quien] += sugerencias.length;
    return { id: r.id, nombre: r.nombre, color: r.color, quien: r.quien, que_es: r.que_es, total: sugerencias.length,
      pct: total ? Math.round((1000 * sugerencias.length) / total) / 10 : 0,
      apariciones_total: sugerencias.reduce((t, s) => t + s.apariciones, 0),
      veces_top3_total: sugerencias.reduce((t, s) => t + s.veces_top3, 0), sugerencias };
  });
  const de = (id) => intenciones.find((i) => i.id === id).total;
  const q = encodeURIComponent(tema);
  return {
    en_vivo: true, tema, slug: slugDe(tema), run_id: `en-vivo_${slugDe(tema)}`, pais: reglas.pais.nombre, reglas_version: reglas.version, generado_utc: new Date().toISOString().slice(0, 19) + "Z",
    fuentes: [{ id: "google", nombre: "Autocompletar de Google", pedidos: semillas.length, con_respuesta: conRespuesta }],
    resumen: {
      sugerencias_unicas: total, fuera_de_uruguay: de("fuera_uy"), fuera_de_uruguay_pct: total ? Math.round((1000 * de("fuera_uy")) / total) / 10 : 0,
      sin_clasificar: de("otros"), quien_supuesto: quien,
      intenciones_con_datos: intenciones.filter((i) => i.total && !["otros", "fuera_uy", "emprender"].includes(i.id)).length,
      instituciones_uy: Object.entries(inst).map(([id, sugerencias]) => ({ id, sugerencias })).sort((a, b) => b.sugerencias - a.sugerencias || a.id.localeCompare(b.id)),
    },
    intenciones, top10: [], rechazadas: { total: rechazadas, por_motivo: {} },
    enlaces: {
      trends: `https://trends.google.com/trends/explore?geo=UY&date=today%205-y&q=${q}`,
      google: `https://www.google.com/search?gl=uy&hl=es&q=${q}`,
      bing: `https://www.bing.com/search?cc=UY&setlang=es&q=${q}`,
      duckduckgo: `https://duckduckgo.com/?kl=uy-es&q=${q}`,
      youtube: `https://www.youtube.com/results?search_query=${q}`,
    },
  };
}

// Convierte una consulta en los datos que dibuja mapa.js.
// La cabeza de cada rama es el tipo de duda (con sus apariciones); los hijos, sus frases con más datos.
// Las ramas van de la que tiene más datos (apariciones sumadas) a la que tiene menos.
// Los puntos crecen con las apariciones de la frase; las 3 frases con más datos de todo el mapa llevan un aro.
export function consultaAMapa(consulta) {
  const temaNorm = normalizar(consulta.tema);
  const visibles = consulta.intenciones.filter((i) => i.total > 0 && !["otros", "fuera_uy", "emprender"].includes(i.id));
  const enMapa = visibles.flatMap((i) => i.sugerencias.slice(0, 4));
  const maxAp = Math.max(1, ...enMapa.map((s) => s.apariciones));
  const destacadas = new Set([...enMapa].sort(ordenFrase).slice(0, 3));
  const ramas = visibles
    .sort((a, b) => (b.apariciones_total ?? 0) - (a.apariciones_total ?? 0) || b.total - a.total)
    .map((i) => ({
      id: i.id, titulo: i.nombre, color: i.color, intencion: i,
      nodos: [
        { id: `${i.id}-cab`, titulo: i.nombre, icono: String(i.apariciones_total ?? i.total) },
        ...i.sugerencias.slice(0, 4).map((s, k) => ({
          id: `${i.id}-s${k}`, sugerencia: s, icono: String(s.apariciones),
          peso: s.apariciones / maxAp, destacado: destacadas.has(s),
          titulo: normalizar(s.texto).replaceAll(temaNorm, " ").replace(/\s+/g, " ").trim() || s.texto,
        })),
      ],
    }));
  return { centro: { titulo: consulta.tema, sub: consulta.pais }, ramas };
}

export const esc = (t) => String(t ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
export const num = (n) => Number(n).toLocaleString("es-UY");
export function fecha(iso) {
  const d = new Date(iso);
  return isNaN(d) ? iso : d.toLocaleString("es-UY", { dateStyle: "medium", timeStyle: "short", timeZone: "America/Montevideo" });
}

export const slugDe = (t) => normalizar(t).replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");

// ---------- CSV: las mismas columnas que colector/base_csv.py ----------
export const COLUMNAS_CSV = ["tema", "slug", "run_id", "medido_utc", "pais", "consultas_respondidas", "tipo_duda_id", "tipo_duda",
  "frase", "apariciones", "pos_promedio", "pos_mejor", "veces_top3", "veces_top10", "instituciones", "fuentes"];

export function consultaAFilas(c) {
  const n = c.fuentes.reduce((t, f) => t + f.con_respuesta, 0);
  return c.intenciones.flatMap((i) => i.sugerencias.map((s) => ({
    tema: c.tema, slug: c.slug, run_id: c.run_id ?? "", medido_utc: c.generado_utc, pais: c.pais, consultas_respondidas: n,
    tipo_duda_id: i.id, tipo_duda: i.nombre, frase: s.texto, apariciones: s.apariciones,
    pos_promedio: s.pos_promedio ?? "", pos_mejor: s.pos_mejor ?? "", veces_top3: s.veces_top3 ?? 0, veces_top10: s.veces_top10 ?? 0,
    instituciones: (s.instituciones ?? []).join("|"), fuentes: (s.fuentes ?? []).join("|"),
  })));
}

export function filasACSV(filas) {
  const celda = (v) => { const t = String(v ?? ""); return /[",\n\r]/.test(t) ? `"${t.replace(/"/g, '""')}"` : t; };
  return "\ufeff" + [COLUMNAS_CSV.join(","), ...filas.map((f) => COLUMNAS_CSV.map((k) => celda(f[k])).join(","))].join("\r\n") + "\r\n";
}

function leerCSV(texto) {
  texto = texto.replace(/^\ufeff/, "");
  const primera = texto.split(/\r?\n/, 1)[0];
  const sep = [",", ";", "\t"].sort((a, b) => primera.split(b).length - primera.split(a).length)[0];
  const filas = []; let fila = [], campo = "", comillas = false;
  for (let i = 0; i < texto.length; i++) {
    const ch = texto[i];
    if (comillas) {
      if (ch === '"' && texto[i + 1] === '"') { campo += '"'; i++; }
      else if (ch === '"') comillas = false;
      else campo += ch;
    } else if (ch === '"') comillas = true;
    else if (ch === sep) { fila.push(campo); campo = ""; }
    else if (ch === "\n" || ch === "\r") { if (ch === "\r" && texto[i + 1] === "\n") i++; fila.push(campo); filas.push(fila); fila = []; campo = ""; }
    else campo += ch;
  }
  if (campo || fila.length) { fila.push(campo); filas.push(fila); }
  const cab = filas.shift()?.map((h) => h.trim()) ?? [];
  return filas.filter((f) => f.some((x) => x.trim())).map((f) => Object.fromEntries(cab.map((h, k) => [h, f[k] ?? ""])));
}

// Vuelve a armar las consultas desde un CSV propio (una o varias, agrupadas por slug).
export function csvAConsultas(texto, reglas) {
  const filas = leerCSV(texto);
  const faltan = ["tema", "tipo_duda_id", "frase", "apariciones"].filter((c) => !(c in (filas[0] ?? {})));
  if (!filas.length || faltan.length) throw new Error(`El archivo no tiene el formato del radar${faltan.length ? ` (faltan columnas: ${faltan.join(", ")})` : ""}.`);
  const porTema = new Map();
  for (const f of filas) { const k = f.slug || slugDe(f.tema); if (!porTema.has(k)) porTema.set(k, []); porTema.get(k).push(f); }
  const n = (v) => (v === "" || v == null ? null : Number(String(v).replace(",", ".")));
  return [...porTema.entries()].map(([slug, fs]) => {
    const f0 = fs[0], consultas = n(f0.consultas_respondidas) ?? 0;
    const intenciones = reglas.intenciones.map((r) => {
      const sug = fs.filter((f) => f.tipo_duda_id === r.id).map((f) => ({
        texto: f.frase, apariciones: n(f.apariciones) ?? 0, pos_promedio: n(f.pos_promedio), pos_mejor: n(f.pos_mejor),
        veces_top3: n(f.veces_top3) ?? 0, veces_top10: n(f.veces_top10) ?? 0,
        instituciones: f.instituciones ? f.instituciones.split("|") : [], fuentes: f.fuentes ? f.fuentes.split("|") : ["google"],
      })).sort(ordenFrase);
      return { id: r.id, nombre: r.nombre, color: r.color, quien: r.quien, que_es: r.que_es, total: sug.length, sugerencias: sug,
        apariciones_total: sug.reduce((t, s) => t + s.apariciones, 0), veces_top3_total: sug.reduce((t, s) => t + s.veces_top3, 0) };
    });
    const total = intenciones.reduce((t, i) => t + i.total, 0);
    intenciones.forEach((i) => { i.pct = total ? Math.round((1000 * i.total) / total) / 10 : 0; });
    return { origen: "archivo", tema: f0.tema, slug: `archivo-${slug}`, run_id: f0.run_id, generado_utc: f0.medido_utc, pais: f0.pais || "Uruguay",
      reglas_version: "del archivo", fuentes: [{ id: "archivo", nombre: "Autocompletar (desde archivo)", pedidos: consultas, con_respuesta: consultas }],
      intenciones, top10: [], rechazadas: { total: 0, por_motivo: {} } };
  });
}

// Sellos «Foto» / «Historial»: cada bloque marcado con data-sello dice solo si muestra un día o el tiempo.
export function sellar(textos) {
  document.querySelectorAll("[data-sello]").forEach((h) => {
    const tipo = h.dataset.sello, texto = h.dataset.selloTexto || textos[tipo];
    if (!texto) return;
    let s = h.querySelector(":scope > .sello-auto");
    if (!s) { s = document.createElement("span"); h.append(" ", s); }
    s.className = `sello sello-auto ${tipo}`;
    s.textContent = texto;
    s.title = tipo === "foto" ? "Muestra un solo momento: no dice si sube o baja" : "Muestra varias mediciones en el tiempo";
  });
}

/* Lista de temas guardados bajo un campo de texto (reemplaza al <datalist> del navegador,
   que solo muestra lo que coincide con lo ya escrito y parecía no funcionar).
   opciones(): [{ tema, nota }] · alElegir(tema): qué hacer al elegir uno. */
let nSug = 0;
export function sugeridor(input, opciones, alElegir) {
  const id = `sug-${++nSug}`, caja = input.parentElement;
  caja.classList.add("con-sug");
  const lista = document.createElement("ul");
  lista.id = id; lista.className = "sug"; lista.setAttribute("role", "listbox"); lista.hidden = true;
  const abrirBtn = document.createElement("button");
  abrirBtn.type = "button"; abrirBtn.className = "sug-abrir"; abrirBtn.textContent = "▾";
  abrirBtn.setAttribute("aria-label", "Ver temas guardados"); abrirBtn.title = "Ver temas guardados";
  input.after(abrirBtn, lista);
  Object.entries({ role: "combobox", "aria-autocomplete": "list", "aria-expanded": "false", "aria-controls": id }).forEach(([k, v]) => input.setAttribute(k, v));
  let items = [], activo = -1;
  const cerrar = () => { lista.hidden = true; input.setAttribute("aria-expanded", "false"); input.removeAttribute("aria-activedescendant"); activo = -1; };
  const marcar = (k) => {
    activo = k;
    lista.querySelectorAll("[role=option]").forEach((li, j) => li.setAttribute("aria-selected", String(j === k)));
    if (k >= 0) { input.setAttribute("aria-activedescendant", `${id}-${k}`); lista.querySelector(`#${id}-${k}`)?.scrollIntoView({ block: "nearest" }); }
  };
  const pintar = (todos) => {
    const q = normalizar(input.value), todas = opciones();
    const coinciden = todos || !q ? todas : todas.filter((o) => normalizar(o.tema).includes(q));
    items = coinciden.length ? coinciden : todas;
    lista.innerHTML = (coinciden.length ? "" : `<li class="sug-nota">Ningún tema guardado con «${esc(input.value)}»: tocá Buscar o Comparar para medirlo en vivo. Guardados:</li>`)
      + items.map((o, k) => `<li role="option" id="${id}-${k}" aria-selected="false" data-k="${k}">${esc(o.tema)}${o.nota ? ` <small>${esc(o.nota)}</small>` : ""}</li>`).join("");
    lista.hidden = !items.length; input.setAttribute("aria-expanded", String(!lista.hidden)); marcar(-1);
  };
  const elegir = (k) => { const o = items[k]; if (!o) return; input.value = o.tema; cerrar(); alElegir(o.tema); };
  input.addEventListener("focus", () => pintar(true));
  input.addEventListener("input", () => pintar(false));
  input.addEventListener("blur", () => setTimeout(cerrar, 120));
  input.addEventListener("keydown", (e) => {
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault(); if (lista.hidden) pintar(false);
      const n = items.length; if (n) marcar(e.key === "ArrowDown" ? (activo + 1) % n : (activo - 1 + n) % n);
    } else if (e.key === "Enter" && !lista.hidden && activo >= 0) { e.preventDefault(); e.stopImmediatePropagation(); elegir(activo); }
    else if (e.key === "Escape" && !lista.hidden) { e.stopPropagation(); cerrar(); }
  });
  lista.addEventListener("mousedown", (e) => e.preventDefault());
  lista.addEventListener("click", (e) => { const li = e.target.closest("[role=option]"); if (li) elegir(Number(li.dataset.k)); });
  abrirBtn.addEventListener("mousedown", (e) => e.preventDefault());
  abrirBtn.addEventListener("click", () => { if (lista.hidden) { input.focus(); pintar(true); } else cerrar(); });
}
