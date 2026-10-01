/* Copiloto Rural — backend de demostración que corre en el navegador.
   Reemplaza al servidor Python (app.py + copiloto/servicios.py) para poder mostrar la app
   en una página estática. Intercepta los fetch a /api/... y responde con la misma lógica:
   checklists, calibraciones, asistente en modo mock, progreso, alertas, tablero, constancia y sync.
   Los datos de ejemplo salen del mismo db.py (los genera construir_demo.py) y viven en este navegador.
   Si se cambia servicios.py, hay que reflejar el cambio acá. */
"use strict";

(function () {
  const D = window.COPILOTO_DATOS;
  const KB = D.conocimiento;
  const CLAVE = "copiloto.demo.base.v1";
  const demo = { sinSenal: false, base: null };
  window.CopilotoDemo = demo;

  // ------------------------------------------------------------- fechas (hora local, sin zona)
  const pad = (n) => String(n).padStart(2, "0");
  const iso = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
  const ahora = () => iso(new Date());
  const hoy = () => ahora().slice(0, 10);
  const haceDias = (n) => { const d = new Date(); d.setDate(d.getDate() - n); return iso(d); };

  class ErrorDeDatos extends Error {}

  // ------------------------------------------------------------- base en memoria (+ copia en el navegador)
  function sembrar() {
    const t = JSON.parse(JSON.stringify(D.tablas));
    // Corre los datos de ejemplo días enteros para que "hoy" sea hoy, sin pasar de la hora actual.
    const generado = new Date(D.generado.slice(0, 10) + "T00:00:00");
    const base = new Date(hoy() + "T00:00:00");
    const dias = Math.round((base - generado) / 86400000);
    const limite = new Date(Date.now() - 5 * 60000);
    for (const tabla of ["checklists", "calibraciones", "consultas", "progreso"]) {
      for (const r of t[tabla]) {
        const d = new Date(r.fecha);
        d.setDate(d.getDate() + dias);
        r.fecha = iso(d > limite ? limite : d);
      }
    }
    return { dia: hoy(), tablas: t };
  }

  function cargar() {
    try {
      const guardada = JSON.parse(localStorage.getItem(CLAVE) || "null");
      if (guardada && guardada.dia === hoy()) return guardada;
    } catch { /* sin almacenamiento: queda en memoria */ }
    return sembrar();
  }

  function guardar() {
    try { localStorage.setItem(CLAVE, JSON.stringify(demo.base)); } catch { /* sin almacenamiento */ }
  }

  demo.reiniciar = function () {
    demo.base = sembrar();
    guardar();
    try {
      for (const k of Object.keys(localStorage)) if (k.startsWith("copiloto.") && k !== CLAVE) localStorage.removeItem(k);
    } catch { /* nada */ }
  };

  demo.base = cargar();
  const T = () => demo.base.tablas;
  const proximoId = (filas) => filas.reduce((m, f) => Math.max(m, f.id || 0), 0) + 1;
  const uid = (datos) => String(datos.uid || (crypto.randomUUID ? crypto.randomUUID() : Date.now() + "-" + Math.random()));

  function obtener(tabla, id, nombre) {
    if (id === null || id === undefined || id === "") return null;
    const f = T()[tabla].find((r) => r.id === Number(id));
    if (!f) throw new ErrorDeDatos(`No existe ${nombre} ${id}`);
    return f;
  }

  function fecha(valor) {
    if (!valor) return ahora();
    const d = new Date(String(valor).replace("Z", ""));
    if (isNaN(d)) throw new ErrorDeDatos("Fecha inválida");
    return iso(d);
  }

  // ------------------------------------------------------------- cálculos (copiloto/calculos.py)
  function positivo(nombre, valor) {
    const v = parseFloat(valor);
    if (valor === null || valor === undefined || valor === "" || isNaN(v)) throw new ErrorDeDatos(`Falta el dato: ${nombre}`);
    if (v <= 0) throw new ErrorDeDatos(`El dato '${nombre}' tiene que ser mayor que cero`);
    return v;
  }
  const r1 = (x) => Math.round(x * 10) / 10;
  const r2 = (x) => Math.round(x * 100) / 100;
  const r3 = (x) => Math.round(x * 1000) / 1000;

  const calc = {
    caudal(v, vel, d) {
      const q = positivo("volumen (L/ha)", v) * positivo("velocidad (km/h)", vel) * positivo("distancia entre picos (cm)", d) / 60000;
      return { caudal_l_min: r3(q), texto: `Cada pastilla tiene que tirar ${q.toFixed(2)} litros por minuto.` };
    },
    pastillas(obj, medidos, tol = 10) {
      obj = positivo("caudal objetivo (L/min)", obj);
      if (!medidos || !medidos.length) throw new ErrorDeDatos("Cargá al menos una pastilla medida");
      const detalle = medidos.map((m, i) => {
        const med = positivo(`pastilla ${i + 1}`, m);
        const desvio = (med - obj) / obj * 100;
        return { pastilla: i + 1, medido_l_min: r3(med), desvio_pct: r1(desvio), ok: Math.abs(desvio) <= tol };
      });
      const malas = detalle.filter((d) => !d.ok).map((d) => d.pastilla);
      const prom = detalle.reduce((s, d) => s + d.medido_l_min, 0) / detalle.length;
      return {
        detalle, a_revisar: malas, promedio_l_min: r3(prom), desvio_promedio_pct: r1((prom - obj) / obj * 100), aprobada: !malas.length,
        texto: malas.length ? `Revisá o cambiá ${malas.length} pastilla(s): ${malas.join(", ")}. Se aceptan hasta ±${tol}%.` : `Todas las pastillas dentro de ±${tol}%. Bien.`,
      };
    },
    semillas(pl, dist, pg = 90, ef = 90) {
      pl = positivo("plantas por hectárea", pl);
      const d = positivo("distancia entre surcos (cm)", dist) / 100;
      pg = positivo("poder germinativo (%)", pg) / 100;
      ef = positivo("eficiencia de implantación (%)", ef) / 100;
      if (pg > 1 || ef > 1) throw new ErrorDeDatos("Los porcentajes no pueden pasar de 100");
      const pm = pl * d / 10000;
      const sm = pm / (pg * ef);
      return { plantas_por_metro: r2(pm), semillas_por_metro: r2(sm), semillas_en_10_metros: r1(sm * 10),
        texto: `Tirá ${sm.toFixed(1)} semillas por metro (contá ${Math.round(sm * 10)} en 10 metros).` };
    },
    siembra(contadas, objMetro, tol = 5) {
      const obj = positivo("semillas objetivo por metro", objMetro) * 10;
      if (!contadas || !contadas.length) throw new ErrorDeDatos("Cargá al menos un cuerpo contado");
      const detalle = contadas.map((c, i) => {
        const v = parseFloat(c);
        if (isNaN(v)) throw new ErrorDeDatos(`Falta el dato del cuerpo ${i + 1}`);
        if (v < 0) throw new ErrorDeDatos(`El cuerpo ${i + 1} no puede ser negativo`);
        const desvio = (v - obj) / obj * 100;
        return { cuerpo: i + 1, contadas: v, desvio_pct: r1(desvio), ok: Math.abs(desvio) <= tol };
      });
      const malos = detalle.filter((d) => !d.ok).map((d) => d.cuerpo);
      return { detalle, a_revisar: malos, aprobada: !malos.length, objetivo_en_10m: r1(obj),
        texto: malos.length ? `Revisá los cuerpos: ${malos.join(", ")} (se aceptan hasta ±${tol}%).` : "Todos los cuerpos dentro de lo esperado." };
    },
    perdidas(granos, p1000, cultivo = "soja") {
      const g = parseFloat(granos);
      if (isNaN(g)) throw new ErrorDeDatos("Falta el dato: granos por m²");
      if (g < 0) throw new ErrorDeDatos("Los granos no pueden ser negativos");
      const kg = g * positivo("peso de mil granos (g)", p1000) / 100;
      const tol = KB.tolerancia_perdida_kg_ha[cultivo];
      let veredicto, texto;
      if (tol === undefined) {
        veredicto = "sin_tolerancia";
        texto = `Estás perdiendo ${Math.round(kg)} kg/ha. No tengo cargada una tolerancia verificada para ${cultivo}: consultala con el técnico.`;
      } else if (kg <= tol) {
        veredicto = "ok"; texto = `Pérdida de ${Math.round(kg)} kg/ha: dentro de la tolerancia (${tol} kg/ha). Bien.`;
      } else {
        veredicto = "alta"; texto = `Pérdida de ${Math.round(kg)} kg/ha: arriba de la tolerancia (${tol} kg/ha). Revisá la regulación (te sobran ${Math.round(kg - tol)} kg/ha).`;
      }
      return { kg_ha: r1(kg), tolerancia_kg_ha: tol ?? null, veredicto, texto };
    },
  };

  // ------------------------------------------------------------- asistente mock (copiloto/asistente.py)
  const norm = (t) => (t || "").toLowerCase().normalize("NFKD").replace(/[̀-ͯ]/g, "");
  const contiene = (t, palabras) => palabras.some((p) => t.includes(norm(p)));

  function buscarGuia(pregunta, tipo) {
    const t = norm(pregunta);
    let mejor = null, puntajeMejor = 0;
    for (const g of KB.guias) {
      let p = 0;
      for (const palabra of g.palabras) if (t.includes(norm(palabra))) p += palabra.includes(" ") ? 2 : 1;
      if (!p) continue;
      if (tipo && g.maquina === tipo) p += 1.5;
      if (p > puntajeMejor) { mejor = g; puntajeMejor = p; }
    }
    return mejor;
  }
  const formatearGuia = (g) => `${g.titulo}\n\n${g.pasos.map((p, i) => `${i + 1}. ${p}`).join("\n")}\n\nCuándo parar: ${g.parar}`;

  function responder(pregunta, tipo) {
    const t = norm(pregunta);
    const urgente = contiene(t, D.asistente.urgentes);
    const escalar = contiene(t, D.asistente.escalar);
    const producto = contiene(t, D.asistente.producto);
    const guia = buscarGuia(pregunta, tipo);
    if (urgente) {
      let texto = "PRIMERO LA SEGURIDAD.\n1. Pará la máquina y apagá el motor.\n2. Alejate si hay fuego, humo o riesgo de vuelco.\n" +
        "3. Si hay alguien herido, llamá al 107 (emergencias médicas) o al 911.\n4. Avisá al encargado ahora. Ya le dejé tu consulta marcada como URGENTE.";
      if (guia) texto += "\n\n" + formatearGuia(guia);
      return { respuesta: texto, guia_id: guia ? guia.id : null, escalar: true };
    }
    if (producto) {
      return { respuesta: "De productos y dosis no te puedo recomendar nada: eso lo define la receta del ingeniero agrónomo y el marbete del producto. " +
        "Sí te puedo ayudar a calibrar la máquina para que tire exactamente el volumen que pide la receta. Probá con el botón 'Calibrar'.", guia_id: null, escalar: false };
    }
    if (guia) return { respuesta: formatearGuia(guia), guia_id: guia.id, escalar };
    const maquina = (KB.tipos_maquina[tipo] || "la máquina").toLowerCase();
    return { respuesta: `No tengo una guía para eso todavía. Contame un poco más: ¿qué hace ${maquina}, desde cuándo y qué estabas haciendo? Mientras tanto:\n` +
      "1. Si hay ruido raro, olor a quemado o pérdida, pará y revisá con el motor apagado.\n2. Fijate en el manual de tu máquina.\n3. Le pasé tu consulta al encargado para que te llame.",
      guia_id: null, escalar: true };
  }

  // ------------------------------------------------------------- servicios (copiloto/servicios.py)
  function evaluarChecklist(tipo, items) {
    if (!KB.checklists[tipo]) throw new ErrorDeDatos(`Tipo de máquina desconocido: ${tipo}`);
    let critico = false, otro = false;
    for (const i of KB.checklists[tipo]) {
      if (!items[i.id]) { if (i.critico) critico = true; else otro = true; }
    }
    return critico ? "no_apta" : otro ? "con_observaciones" : "apta";
  }

  function vistaChecklist(c) {
    const tipo = obtener("maquinas", c.maquina_id, "máquina").tipo;
    return {
      ...c,
      fallados: KB.checklists[tipo].filter((i) => !c.items[i.id]).map((i) => ({ id: i.id, texto: i.texto, critico: i.critico })),
      mensaje: {
        apta: "Máquina lista para salir. ¡Buen trabajo!",
        con_observaciones: "Puede salir, pero hay cosas para revisar. Quedan anotadas para el encargado.",
        no_apta: "NO SALE. Hay un punto crítico que resolver antes. Ya le avisamos al encargado.",
      }[c.resultado],
    };
  }

  function registrarChecklist(datos, origen = "online") {
    const u = uid(datos);
    const previo = T().checklists.find((c) => c.uid === u);
    if (previo) return { ...vistaChecklist(previo), duplicado: true };
    const op = obtener("operarios", datos.operario_id, "operario");
    const maq = obtener("maquinas", datos.maquina_id, "máquina");
    if (!op || !maq) throw new ErrorDeDatos("Faltan operario o máquina");
    obtener("lotes", datos.lote_id, "lote");
    let items = datos.items || {};
    if (typeof items !== "object" || Array.isArray(items)) throw new ErrorDeDatos("Los ítems tienen que ser un objeto {id: true/false}");
    const validos = new Set(KB.checklists[maq.tipo].map((i) => i.id));
    items = Object.fromEntries(Object.entries(items).filter(([k]) => validos.has(k)).map(([k, v]) => [k, Boolean(v)]));
    const c = {
      id: proximoId(T().checklists), uid: u, operario_id: op.id, maquina_id: maq.id, lote_id: datos.lote_id ? Number(datos.lote_id) : null,
      fecha: fecha(datos.fecha), items, resultado: evaluarChecklist(maq.tipo, items),
      observaciones: (datos.observaciones || "").trim() || null, origen,
    };
    T().checklists.push(c);
    guardar();
    return { ...vistaChecklist(c), duplicado: false };
  }

  function registrarCalibracion(datos) {
    const u = uid(datos);
    const previo = T().calibraciones.find((c) => c.uid === u);
    if (previo) return { ...previo, duplicado: true };
    const op = obtener("operarios", datos.operario_id, "operario");
    if (!op) throw new ErrorDeDatos("Falta el operario");
    obtener("maquinas", datos.maquina_id, "máquina");
    const e = datos.entradas || {};
    let resultado, aprobada;
    if (datos.tipo === "pulverizadora") {
      const obj = calc.caudal(e.volumen_l_ha, e.velocidad_km_h, e.distancia_picos_cm);
      resultado = { ...obj };
      aprobada = true;
      if (e.medidos_l_min && e.medidos_l_min.length) {
        const v = calc.pastillas(obj.caudal_l_min, e.medidos_l_min);
        resultado = { ...resultado, ...v, texto: obj.texto + " " + v.texto };
        aprobada = v.aprobada;
      }
    } else if (datos.tipo === "siembra") {
      const obj = calc.semillas(e.plantas_ha, e.distancia_surcos_cm, e.pg ?? 90, e.eficiencia ?? 90);
      resultado = { ...obj };
      aprobada = true;
      if (e.contadas_10m && e.contadas_10m.length) {
        const v = calc.siembra(e.contadas_10m, obj.semillas_por_metro);
        resultado = { ...resultado, ...v, texto: obj.texto + " " + v.texto };
        aprobada = v.aprobada;
      }
    } else if (datos.tipo === "perdidas") {
      resultado = calc.perdidas(e.granos_m2, e.p1000_g, e.cultivo || "soja");
      aprobada = resultado.veredicto !== "alta";
    } else {
      throw new ErrorDeDatos("Tipo de calibración desconocido (pulverizadora, siembra o perdidas)");
    }
    const c = { id: proximoId(T().calibraciones), uid: u, operario_id: op.id, maquina_id: datos.maquina_id ? Number(datos.maquina_id) : null,
      tipo: datos.tipo, entradas: e, resultado, aprobada, fecha: fecha(datos.fecha) };
    T().calibraciones.push(c);
    guardar();
    return { ...c, duplicado: false };
  }

  function registrarConsulta(datos) {
    const u = uid(datos);
    const previo = T().consultas.find((c) => c.uid === u);
    if (previo) return { ...previo, duplicado: true };
    const op = obtener("operarios", datos.operario_id, "operario");
    if (!op) throw new ErrorDeDatos("Falta el operario");
    const maq = obtener("maquinas", datos.maquina_id, "máquina");
    const pregunta = (datos.pregunta || "").trim();
    if (!pregunta) throw new ErrorDeDatos("La pregunta está vacía");
    if (pregunta.length > 1000) throw new ErrorDeDatos("La pregunta es muy larga (máximo 1000 caracteres)");
    let r;
    if (datos.pedido_ayuda) r = { respuesta: "Pedido de ayuda enviado al encargado.", modo: "pedido_ayuda", guia_id: datos.guia_id || null, escalar: true };
    else if (datos.respuesta_offline) r = { respuesta: datos.respuesta_offline, modo: "offline", guia_id: datos.guia_id || null, escalar: Boolean(datos.escalar) };
    else r = { ...responder(pregunta, maq ? maq.tipo : null), modo: "mock" };
    const c = { id: proximoId(T().consultas), uid: u, operario_id: op.id, maquina_id: maq ? maq.id : null, pregunta, respuesta: r.respuesta,
      modo: r.modo, guia_id: r.guia_id, escalada: r.escalar ? 1 : 0, resuelta: 0, fecha: fecha(datos.fecha) };
    T().consultas.push(c);
    guardar();
    return { ...c, duplicado: false };
  }

  function resolverConsulta(id) {
    const c = T().consultas.find((q) => q.id === Number(id));
    if (!c) throw new ErrorDeDatos("No existe esa consulta");
    c.resuelta = 1;
    guardar();
    return { id: c.id, resuelta: true };
  }

  function registrarProgreso(datos) {
    const op = obtener("operarios", datos.operario_id, "operario");
    if (!op) throw new ErrorDeDatos("Falta el operario");
    const mod = KB.modulos.find((m) => m.id === datos.modulo_id);
    if (!mod) throw new ErrorDeDatos("Módulo desconocido");
    const resp = datos.respuestas || [];
    if (resp.length !== mod.preguntas.length) throw new ErrorDeDatos("Faltan respuestas");
    const correctas = mod.preguntas.filter((p, i) => resp[i] === p.correcta).length;
    const puntaje = Math.round(correctas * 100 / mod.preguntas.length);
    const aprobado = puntaje >= 70;
    const previo = T().progreso.find((p) => p.operario_id === op.id && p.modulo_id === mod.id);
    if (!previo || puntaje >= previo.puntaje) {
      if (previo) T().progreso.splice(T().progreso.indexOf(previo), 1);
      T().progreso.push({ operario_id: op.id, modulo_id: mod.id, puntaje, aprobado: aprobado ? 1 : 0, fecha: ahora() });
      guardar();
    }
    return { modulo_id: mod.id, puntaje, aprobado, correctas, total: mod.preguntas.length };
  }

  function progresoOperario(id) {
    obtener("operarios", id, "operario");
    id = Number(id);
    const modulos = KB.modulos.map((m) => {
      const f = T().progreso.find((p) => p.operario_id === id && p.modulo_id === m.id);
      return { id: m.id, titulo: m.titulo, puntaje: f ? f.puntaje : null, aprobado: Boolean(f && f.aprobado) };
    });
    const aprobados = modulos.filter((m) => m.aprobado).length;
    const desde = haceDias(30);
    return {
      operario_id: id, modulos, aprobados, total: modulos.length, porcentaje: Math.round(aprobados * 100 / modulos.length),
      jornadas_30d: T().checklists.filter((c) => c.operario_id === id && c.fecha >= desde).length,
      calibraciones_30d: T().calibraciones.filter((c) => c.operario_id === id && c.fecha >= desde).length,
    };
  }

  const ordenFecha = (a, b) => (a.fecha < b.fecha ? 1 : a.fecha > b.fecha ? -1 : b.id - a.id);
  const nombreOperario = (id) => (T().operarios.find((o) => o.id === id) || {}).nombre;

  function estadoMaquina(m) {
    const ult = T().checklists.filter((c) => c.maquina_id === m.id).sort(ordenFecha)[0] || null;
    const motivos = [];
    let estado = "ok";
    if (ult && ult.fecha.slice(0, 10) === hoy()) {
      if (ult.resultado === "no_apta") { estado = "parada"; motivos.push("Checklist de hoy NO APTA"); }
      else if (ult.resultado === "con_observaciones") { estado = "atencion"; motivos.push("Checklist de hoy con observaciones"); }
    }
    const desdeService = (m.horas || 0) - (m.ultimo_service_horas || 0);
    if (desdeService >= (m.service_cada_horas || 250)) {
      if (estado === "ok") estado = "atencion";
      motivos.push(`Service vencido (${Math.round(desdeService)} h desde el último)`);
    }
    return { estado, motivos, ultimo: ult };
  }

  function alertas(empresaId) {
    const lista = [];
    const maquinas = T().maquinas.filter((m) => m.empresa_id === empresaId);
    for (const m of maquinas) {
      const est = estadoMaquina(m);
      for (const motivo of est.motivos) {
        lista.push({ nivel: est.estado === "parada" ? "alta" : "media", tipo: "maquina", maquina_id: m.id, texto: `${m.apodo}: ${motivo}`,
          detalle: motivo.startsWith("Checklist") ? (est.ultimo || {}).observaciones || null : null });
      }
    }
    const ops = new Set(T().operarios.filter((o) => o.empresa_id === empresaId).map((o) => o.id));
    const desde = haceDias(7);
    for (const c of T().calibraciones.filter((c) => ops.has(c.operario_id) && !c.aprobada && c.fecha >= desde).sort(ordenFecha)) {
      const apodo = (T().maquinas.find((m) => m.id === c.maquina_id) || {}).apodo;
      lista.push({ nivel: "media", tipo: "calibracion", maquina_id: c.maquina_id, texto: `${apodo || "Calibración"}: ${c.resultado.texto || "calibración fuera de rango"}`,
        detalle: `Registró ${nombreOperario(c.operario_id)} el ${c.fecha.slice(0, 10)}` });
    }
    for (const q of T().consultas.filter((q) => ops.has(q.operario_id) && q.escalada && !q.resuelta).sort(ordenFecha)) {
      lista.push({ nivel: "alta", tipo: "consulta", consulta_id: q.id, texto: `${nombreOperario(q.operario_id)} pide ayuda: "${q.pregunta.slice(0, 90)}"`,
        detalle: q.fecha.slice(0, 16).replace("T", " ") });
    }
    for (const o of T().operarios.filter((o) => o.empresa_id === empresaId && !o.rol.startsWith("Encargado"))) {
      if (!T().checklists.some((c) => c.operario_id === o.id && c.fecha.slice(0, 10) === hoy())) {
        lista.push({ nivel: "baja", tipo: "operario", operario_id: o.id, texto: `${o.nombre} no hizo checklist hoy`, detalle: null });
      }
    }
    const orden = { alta: 0, media: 1, baja: 2 };
    return lista.sort((a, b) => orden[a.nivel] - orden[b.nivel]);
  }

  function datosEmpresa(id) {
    const emp = T().empresas.find((e) => e.id === id);
    if (!emp) throw new ErrorDeDatos("No existe la empresa");
    const deLaEmpresa = (tabla) => T()[tabla].filter((r) => r.empresa_id === id).sort((a, b) => a.id - b.id);
    return { empresa: emp, operarios: deLaEmpresa("operarios"), maquinas: deLaEmpresa("maquinas"), lotes: deLaEmpresa("lotes") };
  }

  function impactoSemana(empresaId, dias = 7) {
    const desde = haceDias(dias);
    const maqs = new Set(T().maquinas.filter((m) => m.empresa_id === empresaId).map((m) => m.id));
    const ops = new Set(T().operarios.filter((o) => o.empresa_id === empresaId).map((o) => o.id));
    const cks = T().checklists.filter((c) => maqs.has(c.maquina_id) && c.fecha >= desde);
    const cals = T().calibraciones.filter((c) => ops.has(c.operario_id) && c.fecha >= desde);
    const perdidas = cals.filter((c) => c.tipo === "perdidas").map((c) => c.resultado.kg_ha);
    const qs = T().consultas.filter((q) => ops.has(q.operario_id) && q.fecha >= desde);
    const esc = qs.filter((q) => q.escalada);
    return {
      dias, checklists: cks.length, salidas_frenadas: cks.filter((c) => c.resultado === "no_apta").length,
      calibraciones: cals.length, calibraciones_fuera_de_rango: cals.filter((c) => !c.aprobada).length,
      mediciones_perdidas: perdidas.length, perdida_promedio_kg_ha: perdidas.length ? r1(perdidas.reduce((a, b) => a + b, 0) / perdidas.length) : null,
      consultas: qs.length, pedidos_ayuda: esc.length, pedidos_resueltos: esc.filter((q) => q.resuelta).length,
    };
  }

  function tablero(empresaId) {
    const base = datosEmpresa(empresaId);
    const maquinas = base.maquinas.map((m) => {
      const est = estadoMaquina(m);
      const u = est.ultimo;
      return { ...m, estado: est.estado, motivos: est.motivos,
        ultimo_checklist: u ? { fecha: u.fecha, resultado: u.resultado, operario: nombreOperario(u.operario_id) } : null };
    });
    const operarios = base.operarios.map((o) => {
      const p = progresoOperario(o.id);
      return { ...o, formacion_pct: p.porcentaje, modulos_aprobados: p.aprobados, jornadas_30d: p.jornadas_30d, calibraciones_30d: p.calibraciones_30d };
    });
    const maqs = new Set(base.maquinas.map((m) => m.id));
    const ops = new Set(base.operarios.map((o) => o.id));
    const checklistsHoy = T().checklists.filter((c) => maqs.has(c.maquina_id) && c.fecha.slice(0, 10) === hoy()).sort(ordenFecha)
      .map((c) => ({ id: c.id, fecha: c.fecha, resultado: c.resultado, observaciones: c.observaciones, operario: nombreOperario(c.operario_id),
        maquina: (T().maquinas.find((m) => m.id === c.maquina_id) || {}).apodo }));
    const consultas = T().consultas.filter((q) => ops.has(q.operario_id)).sort(ordenFecha).slice(0, 10)
      .map((q) => ({ id: q.id, fecha: q.fecha, pregunta: q.pregunta, modo: q.modo, escalada: q.escalada, resuelta: q.resuelta, operario: nombreOperario(q.operario_id) }));
    const al = alertas(empresaId);
    return {
      empresa: base.empresa,
      resumen: {
        maquinas_ok: maquinas.filter((m) => m.estado === "ok").length,
        maquinas_atencion: maquinas.filter((m) => m.estado === "atencion").length,
        maquinas_paradas: maquinas.filter((m) => m.estado === "parada").length,
        checklists_hoy: checklistsHoy.length,
        alertas_altas: al.filter((a) => a.nivel === "alta").length,
      },
      impacto: impactoSemana(empresaId), maquinas, operarios, alertas: al, checklists_hoy: checklistsHoy, consultas, lotes: base.lotes,
    };
  }

  function constanciaLote(id) {
    const lote = obtener("lotes", id, "lote");
    if (!lote) throw new ErrorDeDatos("Falta el lote");
    const labores = T().checklists.filter((c) => c.lote_id === lote.id).sort(ordenFecha).map((c) => {
      const m = T().maquinas.find((x) => x.id === c.maquina_id);
      const dia = c.fecha.slice(0, 10);
      const d0 = new Date(dia + "T00:00:00"); d0.setDate(d0.getDate() - 3);
      const desde = iso(d0).slice(0, 10);
      const cals = T().calibraciones.filter((k) => k.maquina_id === c.maquina_id && k.fecha.slice(0, 10) >= desde && k.fecha.slice(0, 10) <= dia);
      return { fecha: c.fecha, operario: nombreOperario(c.operario_id), maquina: m.apodo, tipo: m.tipo, marca: m.marca, checklist: c.resultado,
        observaciones: c.observaciones, calibraciones: cals.map((k) => ({ tipo: k.tipo, fecha: k.fecha, aprobada: Boolean(k.aprobada), texto: k.resultado.texto })) };
    });
    const empresa = T().empresas.find((e) => e.id === lote.empresa_id).nombre;
    return { lote, contratista: empresa, labores, emitida: ahora() };
  }

  function sincronizar(ops) {
    if (!Array.isArray(ops)) throw new ErrorDeDatos("Se esperaba una lista de operaciones");
    const fns = { checklist: (d) => registrarChecklist(d, "offline"), calibracion: registrarCalibracion, consulta: registrarConsulta, progreso: registrarProgreso };
    const resultados = ops.map((op) => {
      const datos = (op && op.datos) || {};
      const fn = fns[op && op.tipo];
      if (!fn) return { uid: datos.uid, ok: false, error: `Tipo desconocido: ${op && op.tipo}` };
      try { const r = fn(datos); return { uid: datos.uid, ok: true, duplicado: Boolean(r.duplicado) }; }
      catch (e) { if (e instanceof ErrorDeDatos) return { uid: datos.uid, ok: false, error: e.message }; throw e; }
    });
    return { procesadas: resultados.length, ok: resultados.filter((r) => r.ok).length, resultados };
  }

  // ------------------------------------------------------------- rutas (app.py)
  function rutear(metodo, ruta, cuerpo) {
    const [path, query] = ruta.split("?");
    const empresaId = Number(new URLSearchParams(query || "").get("empresa_id") || 1);
    const partes = path.split("/");
    if (metodo === "GET") {
      if (path === "/api/salud") return [200, { ok: true, modo_asistente: "mock" }];
      if (path === "/api/conocimiento") return [200, KB];
      if (path === "/api/empresa") return [200, datosEmpresa(empresaId)];
      if (path === "/api/tablero") return [200, tablero(empresaId)];
      if (path.startsWith("/api/lotes/") && path.endsWith("/constancia")) return [200, constanciaLote(numero(partes[3]))];
      if (path.startsWith("/api/operarios/") && path.endsWith("/progreso")) return [200, progresoOperario(numero(partes[3]))];
    } else {
      if (path === "/api/checklists") return [201, registrarChecklist(cuerpo)];
      if (path === "/api/calibraciones") return [201, registrarCalibracion(cuerpo)];
      if (path === "/api/consultas") return [201, registrarConsulta(cuerpo)];
      if (path === "/api/progreso") return [201, registrarProgreso(cuerpo)];
      if (path === "/api/sync") return [200, sincronizar(cuerpo.operaciones)];
      if (path.startsWith("/api/consultas/") && path.endsWith("/resolver")) return [200, resolverConsulta(numero(partes[3]))];
    }
    return [404, { error: "No encontrado" }];
  }

  function numero(texto) {
    if (!/^\d+$/.test(texto || "")) throw new ErrorDeDatos("Parámetro inválido");
    return Number(texto);
  }

  const fetchOriginal = window.fetch ? window.fetch.bind(window) : null;
  window.fetch = async function (entrada, opciones = {}) {
    if (typeof entrada !== "string" || !entrada.startsWith("/api/")) return fetchOriginal(entrada, opciones);
    if (demo.sinSenal) throw new TypeError("Sin conexión (simulada)");
    await new Promise((r) => setTimeout(r, 150));
    let estado, datos;
    try {
      const cuerpo = opciones.body ? JSON.parse(opciones.body) : {};
      [estado, datos] = rutear((opciones.method || "GET").toUpperCase(), entrada, cuerpo);
    } catch (e) {
      if (!(e instanceof ErrorDeDatos) && !(e instanceof SyntaxError)) console.error(e);
      [estado, datos] = [e instanceof ErrorDeDatos || e instanceof SyntaxError ? 400 : 500, { error: e.message }];
    }
    return new Response(JSON.stringify(datos), { status: estado, headers: { "Content-Type": "application/json" } });
  };

  // "Sin señal" simulado: la app consulta navigator.onLine y escucha los eventos online/offline.
  try { Object.defineProperty(navigator, "onLine", { configurable: true, get: () => !demo.sinSenal }); } catch { /* el fetch igual falla */ }
  demo.simularSinSenal = function (activar) {
    demo.sinSenal = activar;
    window.dispatchEvent(new Event(activar ? "offline" : "online"));
  };
})();
