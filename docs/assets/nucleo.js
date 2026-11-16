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
      if (!g.semillas.includes(semilla.consulta)) g.semillas.push(semilla.consulta);
      grupos.set(norm, g);
    }
  }

  const porIntencion = Object.fromEntries(reglas.intenciones.map((i) => [i.id, []]));
  const inst = {};
  for (const [norm, g] of grupos) {
    const resto = norm.replaceAll(temaNorm, " ");
    g.apariciones = g.semillas.length;
    g.instituciones = reglas.instituciones_uy.filter((i) => new RegExp(i.patron).test(resto)).map((i) => i.id);
    g.instituciones.forEach((id) => { inst[id] = (inst[id] ?? 0) + 1; });
    porIntencion[clasificar(resto, reglas)].push(g);
  }
  const total = grupos.size;
  const quien = { familia: 0, estudiante: 0, ambos: 0, ninguno: 0 };
  const intenciones = reglas.intenciones.map((r) => {
    const sugerencias = porIntencion[r.id].sort((a, b) => b.apariciones - a.apariciones || a.texto.localeCompare(b.texto));
    quien[r.quien] += sugerencias.length;
    return { id: r.id, nombre: r.nombre, color: r.color, quien: r.quien, que_es: r.que_es, total: sugerencias.length,
      pct: total ? Math.round((1000 * sugerencias.length) / total) / 10 : 0, sugerencias };
  });
  const de = (id) => intenciones.find((i) => i.id === id).total;
  const q = encodeURIComponent(tema);
  return {
    en_vivo: true, tema, pais: reglas.pais.nombre, reglas_version: reglas.version, generado_utc: new Date().toISOString().slice(0, 19) + "Z",
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
// La cabeza de cada rama es la intención (con su total); los hijos, sus búsquedas más repetidas.
export function consultaAMapa(consulta) {
  const temaNorm = normalizar(consulta.tema);
  const ramas = consulta.intenciones
    .filter((i) => i.total > 0 && !["otros", "fuera_uy", "emprender"].includes(i.id))
    .sort((a, b) => b.total - a.total)
    .map((i) => ({
      id: i.id, titulo: i.nombre, color: i.color, intencion: i,
      nodos: [
        { id: `${i.id}-cab`, titulo: i.nombre, icono: String(i.total) },
        ...i.sugerencias.slice(0, 4).map((s, k) => ({
          id: `${i.id}-s${k}`, sugerencia: s, icono: String(s.apariciones),
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
