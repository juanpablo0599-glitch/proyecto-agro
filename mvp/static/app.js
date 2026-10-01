/* Copiloto Rural — app del maquinista y tablero del dueño.
   Vanilla JS, sin dependencias. Funciona sin señal: el conocimiento queda guardado
   y lo que se carga se encola en el teléfono hasta que vuelve la conexión. */
"use strict";

const $vista = document.getElementById("vista");
const $titulo = document.getElementById("titulo");
const $senal = document.getElementById("senal");
const $volver = document.getElementById("btn-volver");

const estado = {
  conocimiento: null,
  empresa: null,
  operarioId: null,
  maquinaId: null,
  chat: [],
};

// ---------------------------------------------------------------- almacenamiento
const guardado = {
  leer(clave, porDefecto) {
    try { const v = localStorage.getItem("copiloto." + clave); return v ? JSON.parse(v) : porDefecto; }
    catch { return porDefecto; }
  },
  escribir(clave, valor) {
    try { localStorage.setItem("copiloto." + clave, JSON.stringify(valor)); } catch { /* sin espacio o modo privado */ }
  },
};

function uid() {
  if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
  return "u" + Date.now().toString(36) + Math.random().toString(36).slice(2);
}

function ahoraISO() {
  const d = new Date();
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`;
}

function esc(t) {
  return String(t ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

// ---------------------------------------------------------------- red y cola offline
async function api(ruta, opciones = {}) {
  const resp = await fetch(ruta, {
    headers: { "Content-Type": "application/json" },
    ...opciones,
    body: opciones.body ? JSON.stringify(opciones.body) : undefined,
  });
  const datos = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    const err = new Error(datos.error || "Error del servidor");
    err.status = resp.status;
    throw err;
  }
  return datos;
}

function cola() { return guardado.leer("cola", []); }

function encolar(tipo, datos) {
  const c = cola();
  c.push({ tipo, datos });
  guardado.escribir("cola", c);
  pintarSenal();
}

/** Intenta mandar al servidor; si no hay señal, lo guarda en la cola. Devuelve {online, datos}. */
async function enviar(ruta, tipo, datos) {
  if (navigator.onLine) {
    try {
      return { online: true, datos: await api(ruta, { method: "POST", body: datos }) };
    } catch (e) {
      if (e.status && e.status < 500) throw e; // error de datos: mostrarlo
    }
  }
  encolar(tipo, datos);
  return { online: false, datos: null };
}

async function sincronizar() {
  const pendientes = cola();
  if (!pendientes.length || !navigator.onLine) return;
  try {
    const r = await api("/api/sync", { method: "POST", body: { operaciones: pendientes } });
    // Se descartan las que entraron o fallaron por datos; quedan solo las que no se procesaron.
    const procesados = new Set(r.resultados.map((x) => x.uid));
    guardado.escribir("cola", pendientes.filter((p) => !procesados.has(p.datos.uid)));
  } catch { /* se reintenta después */ }
  pintarSenal();
}

function pintarSenal() {
  const n = cola().length;
  const online = navigator.onLine;
  $senal.className = "senal" + (online ? "" : " sin");
  $senal.textContent = (online ? "Con señal" : "Sin señal") + (n ? ` · ${n} por enviar` : "");
}

window.addEventListener("online", () => { pintarSenal(); sincronizar(); });
window.addEventListener("offline", pintarSenal);

async function cargarBase() {
  try {
    estado.conocimiento = await api("/api/conocimiento");
    estado.empresa = await api("/api/empresa");
    guardado.escribir("conocimiento", estado.conocimiento);
    guardado.escribir("empresa", estado.empresa);
  } catch {
    estado.conocimiento = guardado.leer("conocimiento", null);
    estado.empresa = guardado.leer("empresa", null);
  }
  estado.operarioId = guardado.leer("operarioId", null);
  estado.maquinaId = guardado.leer("maquinaId", null);
}

// ---------------------------------------------------------------- utilidades de datos
const operario = () => estado.empresa?.operarios.find((o) => o.id === estado.operarioId);
const maquina = (id = estado.maquinaId) => estado.empresa?.maquinas.find((m) => m.id === id);
const nombreTipo = (t) => estado.conocimiento?.tipos_maquina[t] || t;

function opcionesMaquinas(seleccion, tipos) {
  return estado.empresa.maquinas
    .filter((m) => !tipos || tipos.includes(m.tipo))
    .map((m) => `<option value="${m.id}" ${m.id === seleccion ? "selected" : ""}>${esc(m.apodo)} — ${esc(nombreTipo(m.tipo))} ${esc(m.marca || "")}</option>`)
    .join("");
}

function opcionesLotes() {
  return `<option value="">(sin lote)</option>` + estado.empresa.lotes
    .map((l) => `<option value="${l.id}">${esc(l.nombre)} — ${esc(l.cliente)}</option>`).join("");
}

// ---------------------------------------------------------------- cálculos (espejo de copiloto/calculos.py)
const calc = {
  caudal(vol, vel, dist) { return (vol * vel * dist) / 60000; },
  pastillas(obj, medidos, tol = 10) {
    const det = medidos.map((m, i) => ({ n: i + 1, m, desvio: ((m - obj) / obj) * 100 }));
    det.forEach((d) => (d.ok = Math.abs(d.desvio) <= tol));
    return { det, malas: det.filter((d) => !d.ok).map((d) => d.n) };
  },
  semillasMetro(plHa, distCm, pg, ef) { return (plHa * (distCm / 100)) / 10000 / ((pg / 100) * (ef / 100)); },
  perdidas(granos, p1000) { return (granos * p1000) / 100; },
};

// ---------------------------------------------------------------- buscador offline (espejo de asistente.py)
function normalizar(t) { return (t || "").toLowerCase().normalize("NFKD").replace(/[̀-ͯ]/g, ""); }

function buscarGuia(pregunta, tipo) {
  const t = normalizar(pregunta);
  let mejor = null, puntajeMejor = 0;
  for (const g of estado.conocimiento.guias) {
    let p = 0;
    for (const palabra of g.palabras) if (t.includes(normalizar(palabra))) p += palabra.includes(" ") ? 2 : 1;
    if (!p) continue;
    if (tipo && g.maquina === tipo) p += 1.5;
    if (p > puntajeMejor) { mejor = g; puntajeMejor = p; }
  }
  return mejor;
}

function textoGuia(g) {
  return `${g.titulo}\n\n${g.pasos.map((p, i) => `${i + 1}. ${p}`).join("\n")}\n\nCuándo parar: ${g.parar}`;
}

// ---------------------------------------------------------------- navegación
const rutas = {};
function ruta(nombre, titulo, fn) { rutas[nombre] = { titulo, fn }; }

function ir(hash) { location.hash = hash; }

async function render() {
  const [nombre, ...params] = (location.hash.replace(/^#\/?/, "") || "inicio").split("/");
  const r = rutas[nombre] || rutas.inicio;
  $titulo.textContent = r.titulo;
  $volver.hidden = nombre === "inicio";
  if (!estado.conocimiento || !estado.empresa) {
    $vista.innerHTML = `<div class="tarjeta peligro"><p class="resultado">No hay datos guardados todavía</p>
      <p>Abrí la app una vez con señal para que se guarde lo necesario para usarla en el campo.</p></div>`;
    return;
  }
  await r.fn(...params);
  $vista.focus({ preventScroll: true });
  window.scrollTo(0, 0);
}

$volver.addEventListener("click", () => {
  const actual = location.hash.replace(/^#\/?/, "").split("/")[0];
  if (actual === "tablero" || actual === "operario") ir("#/inicio");
  else if (estado.operarioId) ir("#/operario");
  else ir("#/inicio");
});
window.addEventListener("hashchange", render);

// ---------------------------------------------------------------- pantallas
ruta("inicio", "Copiloto Rural", () => {
  $vista.innerHTML = `
    <h2>¿Quién sos?</h2>
    <div class="grilla">
      <button class="boton" data-ir="#/elegir"><span class="ico">👷</span><span>Soy maquinista u operario<small>Checklist, calibrar, problemas, preguntar</small></span></button>
      <button class="boton" data-ir="#/tablero"><span class="ico">📋</span><span>Soy dueño o encargado<small>Estado del equipo y alertas</small></span></button>
    </div>
    <p class="suave" style="margin-top:20px">${esc(estado.empresa.empresa.nombre)} · ${esc(estado.empresa.empresa.localidad)}</p>`;
});

ruta("elegir", "¿Cuál es tu nombre?", () => {
  const ops = estado.empresa.operarios.filter((o) => !o.rol.startsWith("Encargado"));
  $vista.innerHTML = `<div class="grilla">${ops.map((o) => `
    <button class="boton" data-operario="${o.id}"><span class="ico">🙋</span><span>${esc(o.nombre)}<small>${esc(o.rol)}</small></span></button>`).join("")}</div>`;
  $vista.querySelectorAll("[data-operario]").forEach((b) => b.addEventListener("click", () => {
    estado.operarioId = Number(b.dataset.operario);
    guardado.escribir("operarioId", estado.operarioId);
    ir("#/operario");
  }));
});

ruta("operario", "Mi jornada", () => {
  const op = operario();
  if (!op) return ir("#/elegir");
  $vista.innerHTML = `
    <h2>Hola, ${esc(op.nombre.split(" ")[0])}</h2>
    <label for="sel-maquina">¿Con qué máquina trabajás hoy?</label>
    <select id="sel-maquina"><option value="">Elegí la máquina</option>${opcionesMaquinas(estado.maquinaId)}</select>
    <div class="grilla dos" style="margin-top:16px">
      <button class="boton" data-ir="#/checklist"><span class="ico">✅</span><span>Checklist antes de salir<small>2 minutos</small></span></button>
      <button class="boton" data-ir="#/calibrar"><span class="ico">📏</span><span>Calibrar<small>Pulverizadora, sembradora, pérdidas</small></span></button>
      <button class="boton" data-ir="#/problema"><span class="ico">🔧</span><span>Tengo un problema<small>Guías paso a paso</small></span></button>
      <button class="boton" data-ir="#/preguntar"><span class="ico">💬</span><span>Preguntar al Copiloto<small>Escribí tu duda</small></span></button>
      <button class="boton" data-ir="#/aprender"><span class="ico">🎓</span><span>Aprender y mi progreso<small>Lecciones cortas</small></span></button>
    </div>
    <p style="margin-top:18px"><button class="enlace" id="cambiar">No soy ${esc(op.nombre.split(" ")[0])}</button></p>`;
  document.getElementById("sel-maquina").addEventListener("change", (e) => {
    estado.maquinaId = e.target.value ? Number(e.target.value) : null;
    guardado.escribir("maquinaId", estado.maquinaId);
  });
  document.getElementById("cambiar").addEventListener("click", () => {
    estado.operarioId = null; guardado.escribir("operarioId", null); ir("#/elegir");
  });
});

function pedirMaquina(siguiente) {
  $vista.innerHTML = `<h2>Primero elegí la máquina</h2>
    <select id="sel-maquina"><option value="">Elegí la máquina</option>${opcionesMaquinas(null)}</select>`;
  document.getElementById("sel-maquina").addEventListener("change", (e) => {
    if (!e.target.value) return;
    estado.maquinaId = Number(e.target.value);
    guardado.escribir("maquinaId", estado.maquinaId);
    render(siguiente);
  });
}

// ---- Checklist
ruta("checklist", "Checklist antes de salir", () => {
  const m = maquina();
  if (!operario()) return ir("#/elegir");
  if (!m) return pedirMaquina();
  const items = estado.conocimiento.checklists[m.tipo];
  const respuestas = {};
  $vista.innerHTML = `
    <h2>${esc(m.apodo)} <span class="suave">· ${esc(nombreTipo(m.tipo))}</span></h2>
    <p class="suave">Tocá <b>Bien</b> o <b>Mal</b> en cada punto. Los marcados <b style="color:var(--peligro)">CRÍTICO</b> no dejan salir la máquina.</p>
    <div id="items">${items.map((i) => `
      <div class="item" data-item="${i.id}">
        <div class="texto">${esc(i.texto)}${i.critico ? '<span class="critico">CRÍTICO</span>' : ""}</div>
        <div class="opciones">
          <button type="button" class="si" data-valor="1">👍 Bien</button>
          <button type="button" class="no" data-valor="0">👎 Mal</button>
        </div>
      </div>`).join("")}</div>
    <label for="lote">Lote (opcional)</label>
    <select id="lote">${opcionesLotes()}</select>
    <label for="obs">¿Algo para avisar? (opcional)</label>
    <textarea id="obs" placeholder="Ej: pierde aceite el cardán"></textarea>
    <p id="faltan" class="aviso oculto"></p>
    <button class="boton primario" id="guardar" style="margin-top:14px">Terminar checklist</button>`;
  $vista.querySelectorAll(".item").forEach((div) => {
    div.querySelectorAll("button").forEach((b) => b.addEventListener("click", () => {
      const ok = b.dataset.valor === "1";
      respuestas[div.dataset.item] = ok;
      div.classList.toggle("bien", ok); div.classList.toggle("mal", !ok);
      div.querySelectorAll("button").forEach((x) => x.classList.toggle("activo", x === b));
    }));
  });
  document.getElementById("guardar").addEventListener("click", async () => {
    const faltan = items.filter((i) => !(i.id in respuestas));
    const $f = document.getElementById("faltan");
    if (faltan.length) {
      $f.textContent = `Te faltan ${faltan.length} punto(s) por revisar.`;
      $f.classList.remove("oculto");
      return;
    }
    const datos = {
      uid: uid(), operario_id: estado.operarioId, maquina_id: m.id,
      lote_id: document.getElementById("lote").value ? Number(document.getElementById("lote").value) : null,
      items: respuestas, observaciones: document.getElementById("obs").value, fecha: ahoraISO(),
    };
    try {
      const r = await enviar("/api/checklists", "checklist", datos);
      mostrarResultadoChecklist(r.datos || resultadoLocal(m.tipo, respuestas), r.online);
    } catch (e) { $f.textContent = e.message; $f.classList.remove("oculto"); }
  });
});

function resultadoLocal(tipo, respuestas) {
  const items = estado.conocimiento.checklists[tipo];
  const fallados = items.filter((i) => !respuestas[i.id]);
  const resultado = fallados.some((i) => i.critico) ? "no_apta" : fallados.length ? "con_observaciones" : "apta";
  const mensaje = {
    apta: "Máquina lista para salir. ¡Buen trabajo!",
    con_observaciones: "Puede salir, pero hay cosas para revisar. Quedan anotadas para el encargado.",
    no_apta: "NO SALE. Hay un punto crítico que resolver antes. Avisale al encargado.",
  }[resultado];
  return { resultado, fallados, mensaje };
}

function mostrarResultadoChecklist(r, online) {
  const clase = { apta: "ok", con_observaciones: "atencion", no_apta: "peligro" }[r.resultado];
  const icono = { apta: "✅", con_observaciones: "⚠️", no_apta: "⛔" }[r.resultado];
  $vista.innerHTML = `
    <div class="tarjeta ${clase}">
      <p class="resultado">${icono} ${esc(r.mensaje)}</p>
      ${r.fallados.length ? `<p><b>Para revisar:</b></p><ul>${r.fallados.map((f) => `<li>${esc(f.texto)}${f.critico ? " <b>(crítico)</b>" : ""}</li>`).join("")}</ul>` : ""}
    </div>
    ${online ? "" : '<p class="aviso">Sin señal: quedó guardado en el teléfono y se manda solo cuando vuelva la señal.</p>'}
    <div class="grilla">
      ${r.resultado !== "apta" ? '<button class="boton" data-ir="#/problema"><span class="ico">🔧</span><span>Ver cómo resolverlo</span></button>' : ""}
      <button class="boton primario" data-ir="#/operario">Volver al inicio</button>
    </div>`;
}

// ---- Calibrar
ruta("calibrar", "Calibrar", () => {
  $vista.innerHTML = `
    <div class="grilla">
      <button class="boton" data-ir="#/cal-pulverizadora"><span class="ico">💧</span><span>Pulverizadora<small>Caudal por pastilla y prueba de jarra</small></span></button>
      <button class="boton" data-ir="#/cal-siembra"><span class="ico">🌱</span><span>Sembradora<small>Semillas por metro y control a campo</small></span></button>
      <button class="boton" data-ir="#/cal-perdidas"><span class="ico">🌾</span><span>Pérdidas de cosecha<small>Método de los aros (INTA)</small></span></button>
    </div>
    <p class="suave" style="margin-top:16px">Las cuentas se hacen en el teléfono: funcionan sin señal.</p>`;
});

function bloqueResultado(clase, html) { return `<div class="tarjeta ${clase}" id="res">${html}</div>`; }

async function guardarCalibracion(tipo, entradas, maquinaId) {
  const datos = { uid: uid(), operario_id: estado.operarioId, maquina_id: maquinaId || null, tipo, entradas, fecha: ahoraISO() };
  const r = await enviar("/api/calibraciones", "calibracion", datos);
  return r.online ? "Guardado. El encargado lo ve en su tablero." : "Sin señal: guardado en el teléfono, se manda cuando vuelva la señal.";
}

ruta("cal-pulverizadora", "Calibrar pulverizadora", () => {
  if (!operario()) return ir("#/elegir");
  const m = maquina();
  $vista.innerHTML = `
    <label for="maq">Máquina</label>
    <select id="maq">${opcionesMaquinas(m && m.tipo === "pulverizadora" ? m.id : null, ["pulverizadora"])}</select>
    <div class="fila">
      <div><label for="vol">Volumen (L/ha)</label><input id="vol" inputmode="decimal" value="80"></div>
      <div><label for="vel">Velocidad (km/h)</label><input id="vel" inputmode="decimal" value="18"></div>
    </div>
    <label for="dist">Distancia entre picos (cm)</label><input id="dist" inputmode="decimal" value="52.5">
    <div class="tarjeta" id="obj" style="margin-top:12px"></div>
    <h3>Prueba de jarra (opcional)</h3>
    <p class="suave">Juntá lo que tira cada pastilla en 1 minuto y cargalo en litros (ej: 1.25). Dejá vacías las que no mediste.</p>
    <div class="mini-grilla" id="jarra">${Array.from({ length: 8 }, (_, i) => `<input inputmode="decimal" aria-label="Pastilla ${i + 1}" placeholder="P${i + 1}">`).join("")}</div>
    <div id="salida"></div>
    <button class="boton primario" id="guardar" style="margin-top:14px">Calcular y guardar</button>`;
  const num = (id) => parseFloat(String(document.getElementById(id).value).replace(",", "."));
  const pintarObj = () => {
    const q = calc.caudal(num("vol"), num("vel"), num("dist"));
    document.getElementById("obj").innerHTML = isFinite(q) && q > 0
      ? `<p class="resultado">Cada pastilla tiene que tirar ${q.toFixed(2)} L/min</p>` : `<p>Completá los tres datos.</p>`;
    return q;
  };
  ["vol", "vel", "dist"].forEach((id) => document.getElementById(id).addEventListener("input", pintarObj));
  pintarObj();
  document.getElementById("guardar").addEventListener("click", async () => {
    const q = pintarObj();
    if (!(q > 0)) return;
    const medidos = [...document.querySelectorAll("#jarra input")].map((i) => parseFloat(i.value.replace(",", "."))).filter((v) => v > 0);
    let html = `<p class="resultado">Objetivo: ${q.toFixed(2)} L/min por pastilla</p>`, clase = "ok";
    if (medidos.length) {
      const r = calc.pastillas(q, medidos);
      clase = r.malas.length ? "atencion" : "ok";
      html += `<table><tr><th>Pastilla</th><th>Medido</th><th>Desvío</th></tr>${r.det.map((d) =>
        `<tr><td>${d.n}</td><td>${d.m.toFixed(2)}</td><td>${d.ok ? "✅" : "❌"} ${d.desvio.toFixed(1)}%</td></tr>`).join("")}</table>
        <p>${r.malas.length ? `<b>Limpiá o cambiá:</b> ${r.malas.join(", ")} (se acepta ±10%).` : "Todas dentro de ±10%. Bien."}</p>`;
    }
    const msj = await guardarCalibracion("pulverizadora", {
      volumen_l_ha: num("vol"), velocidad_km_h: num("vel"), distancia_picos_cm: num("dist"), medidos_l_min: medidos,
    }, Number(document.getElementById("maq").value) || null).catch((e) => e.message);
    document.getElementById("salida").innerHTML = bloqueResultado(clase, html + `<p class="suave">${esc(msj)}</p>`);
    document.getElementById("res").scrollIntoView({ behavior: "smooth" });
  });
});

ruta("cal-siembra", "Calibrar sembradora", () => {
  if (!operario()) return ir("#/elegir");
  const m = maquina();
  $vista.innerHTML = `
    <label for="maq">Máquina</label>
    <select id="maq">${opcionesMaquinas(m && m.tipo === "sembradora" ? m.id : null, ["sembradora"])}</select>
    <div class="fila">
      <div><label for="pl">Plantas/ha objetivo</label><input id="pl" inputmode="numeric" value="80000"></div>
      <div><label for="dist">Entre surcos (cm)</label><input id="dist" inputmode="decimal" value="52.5"></div>
    </div>
    <div class="fila">
      <div><label for="pg">Poder germinativo (%)</label><input id="pg" inputmode="numeric" value="95"></div>
      <div><label for="ef">Logro a campo (%)</label><input id="ef" inputmode="numeric" value="90"></div>
    </div>
    <div class="tarjeta" id="obj" style="margin-top:12px"></div>
    <h3>Control a campo (opcional)</h3>
    <p class="suave">Sembrá 50 m, destapá y contá las semillas en 10 m de cada cuerpo.</p>
    <div class="mini-grilla" id="cuerpos">${Array.from({ length: 8 }, (_, i) => `<input inputmode="numeric" aria-label="Cuerpo ${i + 1}" placeholder="C${i + 1}">`).join("")}</div>
    <p class="suave">Velocidad recomendada por el INTA: <b>5 a 8 km/h</b> según la máquina.</p>
    <div id="salida"></div>
    <button class="boton primario" id="guardar" style="margin-top:14px">Calcular y guardar</button>`;
  const num = (id) => parseFloat(String(document.getElementById(id).value).replace(",", "."));
  const pintarObj = () => {
    const s = calc.semillasMetro(num("pl"), num("dist"), num("pg"), num("ef"));
    document.getElementById("obj").innerHTML = isFinite(s) && s > 0
      ? `<p class="resultado">Tirá ${s.toFixed(1)} semillas por metro</p><p>En 10 metros tenés que contar <b>${Math.round(s * 10)}</b>.</p>`
      : `<p>Completá los datos.</p>`;
    return s;
  };
  ["pl", "dist", "pg", "ef"].forEach((id) => document.getElementById(id).addEventListener("input", pintarObj));
  pintarObj();
  document.getElementById("guardar").addEventListener("click", async () => {
    const s = pintarObj();
    if (!(s > 0)) return;
    const contadas = [...document.querySelectorAll("#cuerpos input")].map((i) => parseFloat(i.value)).filter((v) => v >= 0);
    let html = `<p class="resultado">Objetivo: ${Math.round(s * 10)} semillas en 10 m</p>`, clase = "ok";
    if (contadas.length) {
      const obj = s * 10;
      const det = contadas.map((c, i) => ({ n: i + 1, c, d: ((c - obj) / obj) * 100 }));
      const malos = det.filter((x) => Math.abs(x.d) > 5);
      clase = malos.length ? "atencion" : "ok";
      html += `<table><tr><th>Cuerpo</th><th>Contadas</th><th>Desvío</th></tr>${det.map((x) =>
        `<tr><td>${x.n}</td><td>${x.c}</td><td>${Math.abs(x.d) <= 5 ? "✅" : "❌"} ${x.d.toFixed(1)}%</td></tr>`).join("")}</table>
        <p>${malos.length ? `<b>Revisá los cuerpos:</b> ${malos.map((x) => x.n).join(", ")} (se acepta ±5%).` : "Todos los cuerpos bien."}</p>`;
    }
    const msj = await guardarCalibracion("siembra", {
      plantas_ha: num("pl"), distancia_surcos_cm: num("dist"), pg: num("pg"), eficiencia: num("ef"), contadas_10m: contadas,
    }, Number(document.getElementById("maq").value) || null).catch((e) => e.message);
    document.getElementById("salida").innerHTML = bloqueResultado(clase, html + `<p class="suave">${esc(msj)}</p>`);
    document.getElementById("res").scrollIntoView({ behavior: "smooth" });
  });
});

ruta("cal-perdidas", "Pérdidas de cosecha", () => {
  if (!operario()) return ir("#/elegir");
  const m = maquina();
  const p1000 = estado.conocimiento.p1000_tipico_g;
  $vista.innerHTML = `
    <p class="suave">Tirá 4 aros de 56 cm de diámetro detrás de la máquina (suman ~1 m²) y contá los granos que quedaron en el suelo dentro de los aros.</p>
    <label for="maq">Máquina</label>
    <select id="maq">${opcionesMaquinas(m && m.tipo === "cosechadora" ? m.id : null, ["cosechadora"])}</select>
    <label for="cult">Cultivo</label>
    <select id="cult">${Object.keys(p1000).map((c) => `<option value="${c}">${c[0].toUpperCase() + c.slice(1)}</option>`).join("")}</select>
    <div class="fila">
      <div><label for="gr">Granos en 1 m²</label><input id="gr" inputmode="numeric" value="60"></div>
      <div><label for="p1000">Peso de 1000 granos (g)</label><input id="p1000" inputmode="decimal" value="${p1000.soja}"></div>
    </div>
    <div id="salida"></div>
    <button class="boton primario" id="guardar" style="margin-top:14px">Calcular y guardar</button>`;
  document.getElementById("cult").addEventListener("change", (e) => { document.getElementById("p1000").value = p1000[e.target.value]; });
  document.getElementById("guardar").addEventListener("click", async () => {
    const cultivo = document.getElementById("cult").value;
    const granos = parseFloat(document.getElementById("gr").value);
    const pmil = parseFloat(String(document.getElementById("p1000").value).replace(",", "."));
    if (!(granos >= 0) || !(pmil > 0)) return;
    const kg = calc.perdidas(granos, pmil);
    const tol = estado.conocimiento.tolerancia_perdida_kg_ha[cultivo];
    let clase = "ok", texto;
    if (tol === undefined) { clase = "atencion"; texto = `No hay una tolerancia verificada cargada para ${cultivo}: consultala con el técnico.`; }
    else if (kg <= tol) texto = `Dentro de la tolerancia del INTA (${tol} kg/ha). Bien.`;
    else { clase = "peligro"; texto = `Arriba de la tolerancia del INTA (${tol} kg/ha): te sobran ${Math.round(kg - tol)} kg/ha. Revisá la regulación.`; }
    const msj = await guardarCalibracion("perdidas", { granos_m2: granos, p1000_g: pmil, cultivo },
      Number(document.getElementById("maq").value) || null).catch((e) => e.message);
    document.getElementById("salida").innerHTML = bloqueResultado(clase,
      `<p class="resultado">Pérdida: ${Math.round(kg)} kg/ha</p><p>${esc(texto)}</p>
       ${clase === "peligro" ? '<button class="boton" data-ir="#/problema/cosechadora"><span class="ico">🔧</span><span>Ver cómo bajar las pérdidas</span></button>' : ""}
       <p class="suave">${esc(msj)}</p>`);
    document.getElementById("res").scrollIntoView({ behavior: "smooth" });
  });
});

// ---- Tengo un problema
ruta("problema", "Tengo un problema", (tipo) => {
  const m = maquina();
  tipo = tipo || (m && m.tipo);
  const tipos = Object.keys(estado.conocimiento.tipos_maquina);
  const guias = estado.conocimiento.guias.filter((g) => !tipo || g.maquina === tipo);
  $vista.innerHTML = `
    <div class="chips">${tipos.map((t) => `<button data-ir="#/problema/${t}" ${t === tipo ? 'style="border-color:var(--primario);font-weight:700"' : ""}>${esc(nombreTipo(t))}</button>`).join("")}</div>
    <h2>¿Qué te pasa?</h2>
    <div class="grilla">${guias.map((g) => `<button class="boton" data-ir="#/guia/${g.id}"><span class="ico">❓</span><span>${esc(g.titulo)}</span></button>`).join("")}</div>
    <p style="margin-top:16px"><button class="boton" data-ir="#/preguntar"><span class="ico">💬</span><span>No está mi problema: preguntar</span></button></p>`;
});

ruta("guia", "Paso a paso", (id) => {
  const g = estado.conocimiento.guias.find((x) => x.id === id);
  if (!g) return ir("#/problema");
  $vista.innerHTML = `
    <h2>${esc(g.titulo)}</h2>
    <ol class="pasos">${g.pasos.map((p) => `<li>${esc(p)}</li>`).join("")}</ol>
    <div class="tarjeta peligro"><b>Cuándo parar:</b> ${esc(g.parar)}</div>
    <h3>¿Se solucionó?</h3>
    <div class="grilla dos">
      <button class="boton" id="si"><span class="ico">👍</span><span>Sí, listo</span></button>
      <button class="boton" id="no"><span class="ico">🆘</span><span>No, pedir ayuda al encargado</span></button>
    </div>
    <div id="salida"></div>`;
  document.getElementById("si").addEventListener("click", () => ir("#/operario"));
  document.getElementById("no").addEventListener("click", async () => {
    if (!operario()) return ir("#/elegir");
    const datos = {
      uid: uid(), operario_id: estado.operarioId, maquina_id: estado.maquinaId,
      pregunta: `Seguí la guía "${g.titulo}" y no se solucionó. Necesito ayuda.`,
      pedido_ayuda: true, guia_id: g.id, fecha: ahoraISO(),
    };
    const r = await enviar("/api/consultas", "consulta", datos).catch(() => ({ online: false }));
    document.getElementById("salida").innerHTML = `<div class="tarjeta atencion"><p class="resultado">🆘 Pedido de ayuda ${r.online ? "enviado" : "guardado"}</p>
      <p>${r.online ? "El encargado lo ve en su tablero." : "Sin señal: se manda solo cuando vuelva. Si es urgente, llamalo por teléfono."}</p></div>`;
  });
});

// ---- Preguntar (chat)
ruta("preguntar", "Preguntar al Copiloto", () => {
  if (!operario()) return ir("#/elegir");
  const sugerencias = ["La sembradora deja dobles", "Las pastillas tiran distinto", "Se pierde grano por la cola", "El motor calienta", "Hay mucho viento para aplicar"];
  const pintarChat = () => estado.chat.map((c) => `<div class="burbuja ${c.de}">${esc(c.texto)}</div>`).join("");
  $vista.innerHTML = `
    <p class="suave">Máquina: <b>${esc(maquina()?.apodo || "sin elegir")}</b>. Respuestas cortas y paso a paso. Si es grave, le aviso al encargado.</p>
    <div id="chat">${pintarChat()}</div>
    <div class="chips">${sugerencias.map((s) => `<button data-sug="${esc(s)}">${esc(s)}</button>`).join("")}</div>
    <label for="preg">Tu pregunta</label>
    <p class="suave">¿No querés escribir? Tocá el 🎤 del teclado del celular y dictala.</p>
    <textarea id="preg" placeholder="Ej: la sembradora deja huecos en la línea" maxlength="1000"></textarea>
    <button class="boton primario" id="mandar" style="margin-top:10px">Preguntar</button>`;
  const $preg = document.getElementById("preg");
  const $chat = document.getElementById("chat");
  $vista.querySelectorAll("[data-sug]").forEach((b) => b.addEventListener("click", () => { $preg.value = b.dataset.sug; $preg.focus(); }));
  document.getElementById("mandar").addEventListener("click", async () => {
    const pregunta = $preg.value.trim();
    if (!pregunta) return;
    const boton = document.getElementById("mandar");
    boton.disabled = true; boton.textContent = "Pensando…";
    estado.chat.push({ de: "yo", texto: pregunta });
    const tipo = maquina()?.tipo;
    let texto;
    const datos = { uid: uid(), operario_id: estado.operarioId, maquina_id: estado.maquinaId, pregunta, fecha: ahoraISO() };
    try {
      if (!navigator.onLine) throw new Error("offline");
      const r = await api("/api/consultas", { method: "POST", body: datos });
      texto = r.respuesta + (r.escalada ? "\n\n(Le avisé al encargado.)" : "");
    } catch (e) {
      if (e.status && e.status < 500) { texto = e.message; }
      else {
        const g = buscarGuia(pregunta, tipo);
        texto = g ? textoGuia(g) : "No tengo una guía para eso sin señal. Quedó guardada tu pregunta y se la paso al encargado cuando vuelva la señal.";
        texto += "\n\n(Sin señal: respuesta de la guía guardada en el teléfono.)";
        encolar("consulta", { ...datos, respuesta_offline: texto, guia_id: g ? g.id : null, escalar: !g });
      }
    }
    estado.chat.push({ de: "copiloto", texto });
    $chat.innerHTML = pintarChat();
    $preg.value = "";
    boton.disabled = false; boton.textContent = "Preguntar";
    $chat.lastElementChild.scrollIntoView({ behavior: "smooth" });
  });
});

// ---- Aprender
ruta("aprender", "Aprender", async () => {
  if (!operario()) return ir("#/elegir");
  let prog = null;
  try { prog = await api(`/api/operarios/${estado.operarioId}/progreso`); guardado.escribir("progreso." + estado.operarioId, prog); }
  catch { prog = guardado.leer("progreso." + estado.operarioId, null); }
  const porId = Object.fromEntries((prog?.modulos || []).map((m) => [m.id, m]));
  $vista.innerHTML = `
    ${prog ? `<div class="tarjeta"><b>Tu avance: ${prog.aprobados} de ${prog.total} módulos</b>
      <div class="barra-prog"><span style="width:${prog.porcentaje}%"></span></div>
      <p class="suave">Últimos 30 días: ${prog.jornadas_30d} checklists y ${prog.calibraciones_30d} calibraciones registradas.</p></div>` : ""}
    <div class="grilla">${estado.conocimiento.modulos.map((m) => {
      const p = porId[m.id];
      const marca = p?.aprobado ? "✅" : p?.puntaje != null ? "🔁" : "📘";
      return `<button class="boton" data-ir="#/modulo/${m.id}"><span class="ico">${marca}</span><span>${esc(m.titulo)}<small>${esc(m.resumen)}${p?.puntaje != null ? ` · ${p.puntaje}%` : ""}</small></span></button>`;
    }).join("")}</div>`;
});

ruta("modulo", "Lección", (id) => {
  const m = estado.conocimiento.modulos.find((x) => x.id === id);
  if (!m) return ir("#/aprender");
  const resp = new Array(m.preguntas.length).fill(null);
  $vista.innerHTML = `
    <h2>${esc(m.titulo)}</h2><p>${esc(m.resumen)}</p>
    ${m.preguntas.map((p, i) => `<div class="item" data-preg="${i}"><div class="texto">${i + 1}. ${esc(p.p)}</div>
      <div class="grilla">${p.opciones.map((o, j) => `<button type="button" class="boton" data-op="${j}" style="min-height:56px">${esc(o)}</button>`).join("")}</div></div>`).join("")}
    <p id="faltan" class="aviso oculto"></p>
    <button class="boton primario" id="corregir">Ver cómo me fue</button><div id="salida"></div>`;
  $vista.querySelectorAll("[data-preg]").forEach((div) => div.querySelectorAll("[data-op]").forEach((b) => b.addEventListener("click", () => {
    resp[Number(div.dataset.preg)] = Number(b.dataset.op);
    div.querySelectorAll("[data-op]").forEach((x) => { x.style.borderColor = x === b ? "var(--primario)" : ""; x.style.borderWidth = x === b ? "3px" : ""; });
  })));
  document.getElementById("corregir").addEventListener("click", async () => {
    if (resp.includes(null)) { const f = document.getElementById("faltan"); f.textContent = "Respondé todas las preguntas."; f.classList.remove("oculto"); return; }
    const correctas = m.preguntas.filter((p, i) => p.correcta === resp[i]).length;
    const puntaje = Math.round((correctas * 100) / m.preguntas.length);
    await enviar("/api/progreso", "progreso", { uid: uid(), operario_id: estado.operarioId, modulo_id: m.id, respuestas: resp }).catch(() => {});
    $vista.querySelectorAll("[data-preg]").forEach((div) => {
      const i = Number(div.dataset.preg);
      div.classList.add(resp[i] === m.preguntas[i].correcta ? "bien" : "mal");
      if (resp[i] !== m.preguntas[i].correcta) div.insertAdjacentHTML("beforeend", `<p><b>Correcta:</b> ${esc(m.preguntas[i].opciones[m.preguntas[i].correcta])}</p>`);
    });
    document.getElementById("salida").innerHTML = `<div class="tarjeta ${puntaje >= 70 ? "ok" : "atencion"}" style="margin-top:12px">
      <p class="resultado">${puntaje >= 70 ? "✅ Aprobado" : "🔁 Repasá y probá de nuevo"}: ${correctas} de ${m.preguntas.length}</p></div>
      <button class="boton" data-ir="#/aprender">Volver a las lecciones</button>`;
  });
});

// ---- Tablero del dueño
ruta("tablero", "Tablero del equipo", async () => {
  let t;
  try { t = await api("/api/tablero"); guardado.escribir("tablero", t); }
  catch { t = guardado.leer("tablero", null); }
  if (!t) { $vista.innerHTML = `<p class="aviso">Sin señal y sin datos guardados del tablero.</p>`; return; }
  const r = t.resumen;
  const txtEstado = { ok: "Lista", atencion: "Atención", parada: "Parada" };
  $vista.innerHTML = `
    <p class="suave">${esc(t.empresa.nombre)} · actualizado ${new Date().toLocaleTimeString("es-AR", { hour: "2-digit", minute: "2-digit" })}${navigator.onLine ? "" : " (datos guardados, sin señal)"}</p>
    <div class="tiles">
      <div class="tile"><div class="num" style="color:var(--ok)">${r.maquinas_ok}</div><div class="lbl">máquinas listas</div></div>
      <div class="tile"><div class="num" style="color:var(--atencion)">${r.maquinas_atencion}</div><div class="lbl">con atención</div></div>
      <div class="tile"><div class="num" style="color:var(--peligro)">${r.maquinas_paradas}</div><div class="lbl">paradas</div></div>
      <div class="tile"><div class="num">${r.checklists_hoy}</div><div class="lbl">checklists hoy</div></div>
    </div>
    <h3>Alertas</h3>
    <div class="tarjeta"><ul class="lista">${t.alertas.length ? t.alertas.map((a) => `
      <li><span class="punto ${a.nivel}" aria-hidden="true"></span><div style="flex:1">
        <div><b>${esc(a.texto)}</b></div>${a.detalle ? `<div class="suave">${esc(a.detalle)}</div>` : ""}
        ${a.consulta_id ? `<button class="enlace" data-resolver="${a.consulta_id}">Marcar como resuelta</button>` : ""}
      </div></li>`).join("") : "<li>Sin alertas. 👌</li>"}</ul></div>
    <h3>Máquinas</h3>
    <div class="tarjeta"><ul class="lista">${t.maquinas.map((m) => `
      <li><span class="punto ${m.estado}" aria-hidden="true"></span><div style="flex:1">
        <div><b>${esc(m.apodo)}</b> · ${esc(nombreTipo(m.tipo))} ${esc(m.marca || "")} ${m.anio ? "(" + m.anio + ")" : ""} <span class="chip ${m.estado === "parada" ? "peligro" : m.estado}">${txtEstado[m.estado]}</span></div>
        <div class="suave">${m.ultimo_checklist ? `Último checklist: ${esc(m.ultimo_checklist.fecha.slice(0, 16).replace("T", " "))} por ${esc(m.ultimo_checklist.operario)}` : "Sin checklist registrado"} · ${Math.round(m.horas)} h</div>
        ${m.motivos.length ? `<div class="suave">${m.motivos.map(esc).join(" · ")}</div>` : ""}
      </div></li>`).join("")}</ul></div>
    <h3>Operarios</h3>
    <div class="tarjeta"><ul class="lista">${t.operarios.map((o) => `
      <li><div style="flex:1"><div><b>${esc(o.nombre)}</b> <span class="suave">· ${esc(o.rol)}</span></div>
        <div class="suave">Formación ${o.formacion_pct}% (${o.modulos_aprobados} módulos) · ${o.jornadas_30d} checklists y ${o.calibraciones_30d} calibraciones en 30 días</div>
        <div class="barra-prog"><span style="width:${o.formacion_pct}%"></span></div></div></li>`).join("")}</ul></div>
    <h3>Últimas consultas al Copiloto</h3>
    <div class="tarjeta"><ul class="lista">${t.consultas.map((q) => `
      <li><div style="flex:1"><div>${esc(q.pregunta)}</div>
        <div class="suave">${esc(q.operario)} · ${esc(q.fecha.slice(0, 16).replace("T", " "))} · ${q.escalada ? (q.resuelta ? "resuelta" : "<b>pidió ayuda</b>") : "respondida"} · modo ${esc(q.modo)}</div></div></li>`).join("") || "<li>Sin consultas.</li>"}</ul></div>
    <button class="boton primario" id="refrescar">Actualizar</button>`;
  document.getElementById("refrescar").addEventListener("click", render);
  $vista.querySelectorAll("[data-resolver]").forEach((b) => b.addEventListener("click", async () => {
    try { await api(`/api/consultas/${b.dataset.resolver}/resolver`, { method: "POST", body: {} }); render(); }
    catch (e) { b.textContent = "No se pudo (¿sin señal?)"; }
  }));
});

// ---------------------------------------------------------------- arranque
document.addEventListener("click", (e) => {
  const destino = e.target.closest("[data-ir]");
  if (destino) { e.preventDefault(); ir(destino.dataset.ir); }
});

(async function arrancar() {
  pintarSenal();
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => {});
  await cargarBase();
  await sincronizar();
  render();
  setInterval(sincronizar, 30000);
})();
