// Análisis por reglas, con la estructura del rol «Analista de Datos Senior» (docs/data/rol-analista.md, punto 5).
// Sin IA: cada hallazgo aparece solo si los datos lo sostienen. Las explicaciones son hipótesis y se marcan así.
// Umbrales a la vista para poder discutirlos y cambiarlos.
import { normalizar } from "./nucleo.js?v=20261118g";

const APARTE = ["otros", "fuera_uy", "emprender"];
const COMO_CARRERA = ["formato", "plan", "donde", "costo", "becas", "modalidad", "salida", "comparar"];
const UMBRAL = { minimo_util: 20, confianza_alta: 40, confianza_media: 15, otro_uso: 35, como_carrera: 75, fuera: 25, sin_regla: 25, temas: 4 };

const POR_QUE = {
  donde: "La persona ya eligió el tema y está comparando dónde estudiarlo.",
  salida: "La decisión depende de si hay trabajo y de cuánto se gana.",
  costo: "El precio pesa en la decisión, o se busca una opción gratuita.",
  becas: "Se busca cómo financiar el estudio.",
  modalidad: "Se busca una forma de cursar compatible con el trabajo o la distancia.",
  plan: "No está claro qué se estudia ni cuánto dura.",
  formato: "Todavía se duda entre carrera, curso o posgrado.",
  temas: "El tema se entiende combinado con otras áreas.",
  aprender: "El tema se busca más para aprender por cuenta propia que como carrera.",
  comparar: "Se está eligiendo entre opciones parecidas.",
};
const RECOMIENDA = {
  donde: "Que la ficha diga en las primeras líneas dónde se cursa y por qué en UCU, usando el nombre del tema junto a «UCU».",
  salida: "Poner salida laboral y sueldos de referencia, con su fuente, arriba de la ficha.",
  costo: "Mostrar el costo o un rango y las formas de pago; si no se puede, decir cómo consultarlo.",
  becas: "Destacar becas y financiación con un enlace directo.",
  modalidad: "Decir la modalidad y los horarios en el título o en la primera línea.",
  plan: "Mostrar duración, título y materias principales arriba, sin tener que bajar un PDF.",
  formato: "Aclarar el tipo de título (licenciatura, técnico, posgrado) en el nombre.",
  temas: "Evaluar un énfasis o un nombre que incluya los temas con los que más se busca.",
  aprender: "Responder «qué es» con contenido propio (artículo o preguntas frecuentes) que lleve a la carrera.",
  comparar: "Agregar una comparación honesta con las alternativas («¿en qué se diferencia?»).",
};

const r1 = (v) => Math.round(v * 10) / 10;
const f = (v) => Number(v).toLocaleString("es-UY", { maximumFractionDigits: 1 });   // para mostrar: coma decimal
const pct = (a, b) => (b ? r1((100 * a) / b) : 0);
const confianza = (n) => (n >= UMBRAL.confianza_alta ? "alta" : n >= UMBRAL.confianza_media ? "media" : "baja");
const ap = (c, id) => c.intenciones.find((i) => i.id === id)?.apariciones_total ?? 0;
const consultas = (c) => c.fuentes.reduce((t, f) => t + f.con_respuesta, 0);

function instituciones(c) {
  const m = {};
  c.intenciones.filter((i) => !APARTE.includes(i.id)).forEach((i) => i.sugerencias.forEach((s) => (s.instituciones ?? []).forEach((id) => {
    m[id] ??= { id, frases: 0, apariciones: 0 }; m[id].frases++; m[id].apariciones += s.apariciones;
  })));
  return Object.values(m).sort((a, b) => b.apariciones - a.apariciones || b.frases - a.frases || a.id.localeCompare(b.id));
}

// Calidad de los datos (rol, punto 1): qué parte de lo medido sirve para el análisis.
export function calidad(c) {
  const todo = c.intenciones.reduce((t, i) => t + i.apariciones_total, 0);
  const utiles = c.intenciones.filter((i) => !APARTE.includes(i.id)).reduce((t, i) => t + i.apariciones_total, 0);
  return {
    consultas: consultas(c), rechazadas: c.rechazadas?.total ?? 0, total: todo,
    partes: [
      { id: "utiles", nombre: "Útiles para el análisis", ap: utiles, color: "var(--accent)" },
      { id: "fuera_uy", nombre: "De otros países", ap: ap(c, "fuera_uy"), color: "#8b93a7" },
      { id: "emprender", nombre: "Emprender o ganar dinero", ap: ap(c, "emprender"), color: "#fb923c" },
      { id: "otros", nombre: "Sin clasificar", ap: ap(c, "otros"), color: "#c3ccdb" },
    ].map((p) => ({ ...p, pct: pct(p.ap, todo) })),
  };
}

export function hallazgos(c, comparados = []) {
  const tema = c.tema, N = consultas(c), q = calidad(c);
  const util = q.partes[0].ap;
  const ramas = c.intenciones.filter((i) => !APARTE.includes(i.id) && i.total > 0).sort((a, b) => b.apariciones_total - a.apariciones_total);
  const H = [];

  // 0. Cuándo no conviene decidir
  if (util < UMBRAL.minimo_util) {
    H.push({ id: "pocos-datos", titulo: "Con estos datos no conviene decidir", cifra: `${util}`, cifra_t: "apariciones útiles",
      encontramos: `Solo ${util} apariciones útiles en ${N} consultas.`,
      porque: "El tema se busca poco con esta forma de escribirlo, o se midió en vivo con menos consultas.",
      significa: "Cualquier conclusión puede cambiar con la próxima medición.",
      oportunidad: "Probar otras formas de nombrar el tema antes de descartarlo.",
      recomendamos: "No cambiar nada todavía. Guardar el tema (más consultas) y probar sinónimos con «Comparar».",
      validamos: `Que la medición guardada supere ${UMBRAL.minimo_util} apariciones útiles.`,
      impacto: "alto", esfuerzo: "bajo", confianza: "alta" });
  }

  // 1. Duda principal
  if (ramas.length) {
    const d1 = ramas[0], d2 = ramas[1], peso = pct(d1.apariciones_total, util);
    H.push({ id: "duda", titulo: `La duda que más se repite es «${d1.nombre}»`, cifra: `${f(peso)} %`, cifra_t: "de las apariciones útiles",
      encontramos: `«${d1.nombre}» suma ${d1.apariciones_total} apariciones (${f(peso)} %)${d2 ? `; le sigue «${d2.nombre}» con ${f(pct(d2.apariciones_total, util))} %` : ""}.`,
      porque: POR_QUE[d1.id] ?? "Sin explicación cargada para este tipo de duda.",
      significa: `Una página sobre «${tema}» que no responda esto primero deja sin respuesta la duda más frecuente.`,
      oportunidad: "Responder antes que la competencia lo que más se pregunta.",
      recomendamos: RECOMIENDA[d1.id] ?? "Responder esta duda arriba de la ficha.",
      validamos: `Volver a medir: que «${d1.nombre}» siga arriba. En la página, ver si esa sección es la más leída (con Analytics, si UCU lo comparte).`,
      impacto: "alto", esfuerzo: "bajo", confianza: confianza(d1.apariciones_total) });
  }

  // 2. Instituciones: quién ocupa el tema
  const inst = instituciones(c), lider = inst[0], ucu = inst.find((x) => x.id === "UCU");
  if (!inst.length && util >= UMBRAL.minimo_util) {
    H.push({ id: "sin-duenio", titulo: "Ninguna institución aparece junto al tema", cifra: "0", cifra_t: "instituciones",
      encontramos: `Google no propone ninguna universidad de Uruguay junto a «${tema}».`,
      porque: "Ninguna institución usa ese término para una carrera, o el tema no se busca como carrera.",
      significa: "El término está libre: nadie lo ocupa todavía.",
      oportunidad: "Ser la primera institución asociada al término.",
      recomendamos: `Si la carrera encaja, usar «${tema}» textual en el nombre o en el título de la ficha.`,
      validamos: `Que «${tema} ucu» aparezca en una próxima medición.`,
      impacto: "medio", esfuerzo: "bajo", confianza: confianza(util) });
  } else if (lider && lider.id !== "UCU") {
    H.push({ id: "competencia", titulo: `Google asocia «${tema}» con ${lider.id} antes que con UCU`, cifra: `${lider.apariciones} vs ${ucu?.apariciones ?? 0}`, cifra_t: `apariciones ${lider.id} vs UCU`,
      encontramos: `${lider.id} aparece en ${lider.apariciones} consultas (${lider.frases} frases); UCU en ${ucu?.apariciones ?? 0} (${ucu?.frases ?? 0} frases).`,
      porque: `${lider.id} tiene una carrera o una página que Google relaciona con ese término.`,
      significa: `Quien busca «${tema}» ve primero a ${lider.id} como opción.`,
      oportunidad: "Que UCU aparezca asociada al término exacto.",
      recomendamos: `Usar «${tema}» textual en el título, la descripción y el primer párrafo de la ficha de UCU; mirar la página de ${lider.id} como referencia.`,
      validamos: `Que «${tema} ucu» aparezca más veces y más arriba en la próxima medición.`,
      impacto: "alto", esfuerzo: "bajo", confianza: confianza(lider.apariciones) });
  } else if (lider) {
    H.push({ id: "ucu-lidera", titulo: `UCU es la institución que más aparece con «${tema}»`, cifra: `${lider.apariciones}`, cifra_t: "apariciones de UCU",
      encontramos: `UCU aparece en ${lider.apariciones} consultas${inst[1] ? `; le sigue ${inst[1].id} con ${inst[1].apariciones}` : ""}.`,
      porque: "La ficha o la marca de UCU ya está asociada al término.",
      significa: "Cambiar el nombre puede hacer perder esa asociación.",
      oportunidad: "Cuidar lo que ya funciona.",
      recomendamos: "No cambiar el nombre. Mantener el término en el título y la descripción de la ficha.",
      validamos: "Que UCU siga primera en la próxima medición.",
      impacto: "medio", esfuerzo: "bajo", confianza: confianza(lider.apariciones) });
  }

  // 3. ¿Se busca como carrera o para otra cosa?
  const comoCarrera = COMO_CARRERA.reduce((t, id) => t + ap(c, id), 0), otroUso = ap(c, "aprender") + ap(c, "emprender");
  const base = comoCarrera + otroUso, pOtro = pct(otroUso, base);
  if (base >= UMBRAL.confianza_media && pOtro >= UMBRAL.otro_uso) {
    H.push({ id: "otro-uso", titulo: "El tema se busca mucho para aprender o ganar dinero, no solo como carrera", cifra: `${f(pOtro)} %`, cifra_t: "aprender o emprender",
      encontramos: `${otroUso} de ${base} apariciones son de aprender por cuenta propia o de emprender.`,
      porque: "El término se usa en la vida diaria o en cursos cortos, no solo para hablar de una carrera.",
      significa: "Usado solo, el término atrae a gente que no busca una carrera.",
      oportunidad: "Usarlo como palabra de apoyo, no como nombre solo.",
      recomendamos: `Acompañarlo de «licenciatura» o «carrera» y medir también «licenciatura en ${tema}».`,
      validamos: `Comparar «${tema}» con «licenciatura en ${tema}» en el radar.`,
      impacto: "alto", esfuerzo: "bajo", confianza: confianza(base) });
  } else if (base >= UMBRAL.confianza_media && 100 - pOtro >= UMBRAL.como_carrera) {
    H.push({ id: "como-carrera", titulo: "El tema se busca sobre todo como carrera", cifra: `${f(100 - pOtro)} %`, cifra_t: "dudas de carrera",
      encontramos: `${comoCarrera} de ${base} apariciones son dudas de carrera (dónde, costo, plan, salida, modalidad…).`,
      porque: "Quien lo busca está pensando en estudiarlo.",
      significa: "El término sirve como nombre o como palabra principal de una carrera.",
      oportunidad: "Usarlo en el nombre.",
      recomendamos: "Si la carrera encaja, usar este término en el nombre o en el título de la ficha.",
      validamos: "Que se sostenga en la próxima medición.",
      impacto: "medio", esfuerzo: "bajo", confianza: confianza(base) });
  }

  // 4. Con qué se combina
  const temas = c.intenciones.find((i) => i.id === "temas");
  if (temas && temas.apariciones_total >= UMBRAL.temas) {
    const tn = normalizar(tema);
    const top = temas.sugerencias.slice(0, 3).map((s) => `${normalizar(s.texto).replaceAll(tn, " ").replace(/\s+/g, " ").trim()} (${s.apariciones})`);
    H.push({ id: "combina", titulo: "Se busca combinado con otras áreas", cifra: `${temas.apariciones_total}`, cifra_t: "apariciones",
      encontramos: `Se busca junto con: ${top.join(", ")}.`,
      porque: "El mercado entiende el tema como parte de un área más amplia.",
      significa: "Hay espacio para un énfasis o un nombre compuesto.",
      oportunidad: "Diferenciarse con un foco que la competencia no nombra.",
      recomendamos: RECOMIENDA.temas,
      validamos: "Medir el nombre compuesto en el radar y compararlo con el tema solo.",
      impacto: "medio", esfuerzo: "medio", confianza: confianza(temas.apariciones_total) });
  }

  // 5. Calidad y debilidades del método (rol, puntos 1 y 6)
  const fuera = q.partes.find((p) => p.id === "fuera_uy"), sinRegla = q.partes.find((p) => p.id === "otros");
  if (fuera.pct >= UMBRAL.fuera) {
    H.push({ id: "fuera", titulo: "Buena parte de lo que propone Google es de otros países", cifra: `${f(fuera.pct)} %`, cifra_t: "de otros países",
      encontramos: `${fuera.ap} de ${q.total} apariciones nombran otro país o una universidad extranjera.`,
      porque: "El tema se busca mucho en otros países de habla hispana y Google mezcla sugerencias.",
      significa: "El interés local es menor de lo que parece a simple vista.",
      oportunidad: "Leer solo lo de Uruguay para no sobreestimar.",
      recomendamos: "No usar el total de frases como señal de demanda; mirar solo las útiles.",
      validamos: "Contrastar con Google Trends para Uruguay.",
      impacto: "medio", esfuerzo: "bajo", confianza: "alta" });
  }
  if (sinRegla.pct >= UMBRAL.sin_regla) {
    H.push({ id: "reglas", titulo: "Las reglas no reconocen una parte grande de las frases", cifra: `${f(sinRegla.pct)} %`, cifra_t: "sin clasificar",
      encontramos: `${sinRegla.ap} de ${q.total} apariciones quedaron sin tipo de duda.`,
      porque: "Faltan reglas para este tema (nombres de lugares, herramientas o temas nuevos).",
      significa: "El mapa puede no mostrar dudas importantes.",
      oportunidad: "Mejorar la clasificación para todos los temas.",
      recomendamos: "Revisar las frases sin clasificar y sumar reglas en reglas.json.",
      validamos: "Que «sin clasificar» baje en el reproceso.",
      impacto: "bajo", esfuerzo: "bajo", confianza: "alta" });
  }

  // 6. Comparación entre temas
  if (comparados.length) {
    const fila = (x) => { const n = consultas(x), cc = COMO_CARRERA.reduce((t, id) => t + ap(x, id), 0); return { tema: x.tema, n, cc, tasa: n ? cc / n : 0, vivo: !!x.en_vivo }; };
    const filas = [fila(c), ...comparados.map(fila)].sort((a, b) => b.tasa - a.tasa);
    const [g, s] = filas;
    H.push({ id: "comparar", titulo: `Entre los temas comparados, «${g.tema}» es el que más se busca como carrera`, cifra: `${f(g.tasa)}`, cifra_t: "dudas de carrera por consulta",
      encontramos: filas.map((fila) => `«${fila.tema}»: ${f(fila.tasa)} por consulta (${fila.cc} en ${fila.n})`).join("; ") + ".",
      porque: "Es la forma en que la gente nombra el estudio de este tema.",
      significa: "Es el candidato más fuerte para el nombre o el título.",
      oportunidad: "Nombrar la carrera como la busca la gente.",
      recomendamos: `Preferir «${g.tema}» en el nombre y usar ${s ? `«${s.tema}»` : "los otros"} como palabras de apoyo en la ficha.`,
      validamos: "Volver a comparar con todos los temas guardados (misma cantidad de consultas).",
      impacto: "alto", esfuerzo: "bajo", confianza: filas.some((x) => x.vivo) ? "media" : confianza(g.cc) });
  }

  const peso = { alto: 3, medio: 2, bajo: 1 };
  return H.sort((a, b) => (a.id === "pocos-datos" ? -1 : b.id === "pocos-datos" ? 1 : 0)
    || peso[b.impacto] - peso[a.impacto] || peso[b.confianza] - peso[a.confianza] || peso[a.esfuerzo] - peso[b.esfuerzo]);
}
