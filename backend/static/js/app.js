"use strict";

const $ = (selector) => document.querySelector(selector);
const form = $("#parameters");
const defaults = Object.fromEntries(new FormData(form).entries());
const colors = {exacta: "#087f78", euler: "#b75d18", heun: "#346be0"};
const fmt = (value) => Number(value).toLocaleString("en-US", {useGrouping: false, maximumSignificantDigits: 13});
let data = null;
let selectedNode = null;
const pages = {euler: 0, heun: 0};
const PAGE_SIZE = 20;

function parameters() {
  return Object.fromEntries([...new FormData(form)].map(([key, value]) => [key, Number(value)]));
}

function markChanges() {
  const values = parameters();
  const official = Object.keys(defaults).every((key) => values[key] === Number(defaults[key]));
  $("#case-badge").textContent = official ? "Ejercicio oficial" : "PVI personalizado";
  $("#stale").hidden = !data || Object.keys(values).every((key) => values[key] === data.parametros[key]);
}

async function calculate(scroll = true) {
  const payload = parameters();
  $("#error").hidden = true;
  $("#loading").hidden = false;
  form.querySelectorAll("button, input").forEach((el) => { el.disabled = true; });
  $("#calculate").textContent = "Calculando…";
  try {
    const response = await fetch("/api/resolver", {
      method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(payload)
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.mensaje || "No se pudo resolver el PVI.");
    data = result;
    pages.euler = pages.heun = 0;
    selectedNode = null;
    $("#output").hidden = false;
    renderResults();
    if (scroll) $("#resultados").scrollIntoView({behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "smooth"});
  } catch (error) {
    $("#error").textContent = error instanceof TypeError ? "No se pudo conectar con el servidor. Comprueba que la aplicación siga en ejecución." : error.message;
    $("#error").hidden = false;
    $("#output").hidden = true;
  } finally {
    $("#loading").hidden = true;
    form.querySelectorAll("button, input").forEach((el) => { el.disabled = false; });
    $("#calculate").textContent = "Calcular métodos ↗";
    markChanges();
  }
}

function setNumber(selector, value, suffix = "") {
  $(selector).textContent = fmt(value) + suffix;
  $(selector).title = String(value) + suffix;
}

function renderResults() {
  const p = data.parametros;
  $("#run-summary").textContent = `y(${fmt(p.x0)}) = ${fmt(p.y0)} · objetivo: x = ${fmt(p.x_final)} · h = ${fmt(p.h)} · ${p.pasos} iteraciones`;
  setNumber("#exact-value", data.valor_exacto);
  $("#constant-value").textContent = `Constante C = ${fmt(data.constante)}`;
  for (const name of ["euler", "heun"]) {
    setNumber(`#${name}-value`, data[name].valor);
    setNumber(`#${name}-error`, data[name].errores.relativo_porcentual, " %");
    renderTable(name);
  }
  $("#conclusion").textContent = data.mas_preciso === "empate"
    ? "Ambos métodos presentan el mismo error absoluto para estos parámetros, a la precisión calculada."
    : `${data.mas_preciso} obtiene el menor error absoluto en x = ${fmt(p.x_final)} para este PVI y este paso. Compara las pendientes y observa cómo cambia la aproximación.`;
  const tbody = $("#error-table");
  tbody.replaceChildren();
  for (const name of ["euler", "heun"]) {
    appendRow(tbody, [name === "euler" ? "Euler" : "Heun", data[name].errores.absoluto, data[name].errores.relativo_porcentual]);
  }
  const select = $("#step-select");
  select.replaceChildren();
  const fragment = document.createDocumentFragment();
  for (let i = 0; i < p.pasos; i++) {
    const option = document.createElement("option");
    option.value = i;
    option.textContent = `${i + 1} de ${p.pasos}`;
    fragment.append(option);
  }
  select.append(fragment);
  renderStep();
  $("#copy-status").textContent = "";
  $("#chart-readout").textContent = "Mueve el cursor sobre la gráfica para consultar los nodos.";
  drawChart();
}

function appendRow(tbody, values) {
  const tr = document.createElement("tr");
  values.forEach((value) => {
    const td = document.createElement("td");
    td.textContent = typeof value === "number" ? fmt(value) : value;
    td.title = String(value);
    tr.append(td);
  });
  tbody.append(tr);
}

function renderTable(name) {
  const tbody = $(`#${name}-table tbody`);
  tbody.replaceChildren();
  const rows = data[name].traza;
  const page = pages[name];
  rows.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE).forEach((r) => {
    const values = [r.iteracion, r.x, r.y, r.h, r.k1];
    if (name === "heun") values.push(r.predictor, r.k2);
    values.push(r.incremento, r.x_siguiente, r.y_siguiente);
    appendRow(tbody, values);
  });
  const nav = $(`#${name}-pagination`);
  nav.replaceChildren();
  const label = document.createElement("span");
  label.textContent = `Filas ${page * PAGE_SIZE + 1}–${Math.min((page + 1) * PAGE_SIZE, rows.length)} de ${rows.length}`;
  nav.append(label);
  if (rows.length <= PAGE_SIZE) return;
  for (const [text, delta, disabled] of [["Anterior", -1, page === 0], ["Siguiente", 1, (page + 1) * PAGE_SIZE >= rows.length]]) {
    const button = document.createElement("button");
    button.textContent = text;
    button.className = "secondary";
    button.disabled = disabled;
    button.setAttribute("aria-label", `${text}: tabla ${name}`);
    button.addEventListener("click", () => { pages[name] += delta; renderTable(name); });
    nav.append(button);
  }
}

function detailBlock(container, title, expressions, answer = false) {
  const div = document.createElement("div");
  const small = document.createElement("small");
  small.textContent = title;
  div.append(small);
  for (const expression of expressions) {
    const p = document.createElement("p");
    p.textContent = expression;
    if (answer) p.className = "answer";
    div.append(p);
  }
  container.append(div);
}

function renderStep() {
  const i = Number($("#step-select").value);
  for (const name of ["euler", "heun"]) {
    const r = data[name].traza[i];
    const el = $(`#${name}-detail`);
    el.replaceChildren();
    detailBlock(el, "01 / PENDIENTE INICIAL", [`k₁ = ${fmt(r.x)}/${fmt(r.y)} − ${fmt(r.y)}/${fmt(r.x)} = ${fmt(r.k1)}`]);
    if (name === "heun") {
      detailBlock(el, "02 / PREDICTOR DE EULER", [`z = ${fmt(r.y)} + (${fmt(r.h)})(${fmt(r.k1)}) = ${fmt(r.predictor)}`]);
      detailBlock(el, "03 / PENDIENTE EN EL PREDICTOR", [`k₂ = ${fmt(r.x_siguiente)}/${fmt(r.predictor)} − ${fmt(r.predictor)}/${fmt(r.x_siguiente)} = ${fmt(r.k2)}`]);
      detailBlock(el, "04 / CORRECTOR", [`y${i + 1} = ${fmt(r.y)} + (${fmt(r.h)}/2)(${fmt(r.k1)} + ${fmt(r.k2)})`, `y(${fmt(r.x_siguiente)}) ≈ ${fmt(r.y_siguiente)}`], true);
    } else {
      detailBlock(el, "02 / INCREMENTO", [`Δy = (${fmt(r.h)})(${fmt(r.k1)}) = ${fmt(r.incremento)}`]);
      detailBlock(el, "03 / NUEVO PUNTO", [`x${i + 1} = ${fmt(r.x)} + ${fmt(r.h)} = ${fmt(r.x_siguiente)}`, `y${i + 1} = ${fmt(r.y)} + (${fmt(r.incremento)})`, `y(${fmt(r.x_siguiente)}) ≈ ${fmt(r.y_siguiente)}`], true);
    }
  }
}

function drawChart() {
  if (!data || $("#output").hidden) return;
  const canvas = $("#chart");
  const width = canvas.clientWidth, height = canvas.clientHeight;
  const ratio = window.devicePixelRatio || 1;
  canvas.width = Math.round(width * ratio);
  canvas.height = Math.round(height * ratio);
  const ctx = canvas.getContext("2d");
  ctx.scale(ratio, ratio);
  const left = width < 450 ? 60 : 74, right = 20, top = 20, bottom = 42;
  const pw = width - left - right, ph = height - top - bottom;
  const ys = Object.values(data.grafica).flatMap((points) => points.map((p) => p.y));
  let ymin = Math.min(...ys), ymax = Math.max(...ys);
  const margin = Math.max((ymax - ymin) * 0.12, Math.abs(ymax) * 0.001, 1e-12);
  ymin -= margin; ymax += margin;
  const {x0, x_final: xf} = data.parametros;
  const px = (x) => left + (x - x0) / (xf - x0) * pw;
  const py = (y) => top + (ymax - y) / (ymax - ymin) * ph;
  ctx.font = '11px "Segoe UI", sans-serif';
  for (let i = 0; i <= 4; i++) {
    const y = top + i * ph / 4;
    ctx.strokeStyle = "#e4ebef"; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(left, y); ctx.lineTo(width - right, y); ctx.stroke();
    ctx.fillStyle = "#576a74"; ctx.textAlign = "right";
    ctx.fillText(Number((ymax - i * (ymax - ymin) / 4).toPrecision(5)).toString(), left - 9, y + 4);
    const x = left + i * pw / 4;
    ctx.textAlign = "center";
    ctx.fillText(Number((x0 + i * (xf - x0) / 4).toPrecision(6)).toString(), x, height - 20);
  }
  ctx.fillStyle = "#152b39"; ctx.textAlign = "left"; ctx.fillText("y", left - 14, 12);
  ctx.textAlign = "right"; ctx.fillText("x", width - 4, height - 20);
  for (const key of ["exacta", "euler", "heun"]) {
    if (!$(`[data-series="${key}"]`).checked) continue;
    const points = data.grafica[key];
    ctx.strokeStyle = colors[key]; ctx.lineWidth = key === "exacta" ? 2.5 : 1.8;
    ctx.setLineDash(key === "euler" ? [6, 4] : []);
    ctx.beginPath();
    points.forEach((p, index) => { if (index === 0) ctx.moveTo(px(p.x), py(p.y)); else ctx.lineTo(px(p.x), py(p.y)); });
    ctx.stroke(); ctx.setLineDash([]);
    if (key !== "exacta") {
      for (const p of points) {
        ctx.beginPath(); ctx.arc(px(p.x), py(p.y), points.length > 100 ? 1.5 : 4, 0, 2 * Math.PI);
        ctx.fillStyle = "white"; ctx.fill(); ctx.stroke();
      }
    }
  }
  if (selectedNode !== null) {
    const point = data.euler.puntos[selectedNode];
    ctx.strokeStyle = "#8497a3"; ctx.setLineDash([3, 4]);
    ctx.beginPath(); ctx.moveTo(px(point.x), top); ctx.lineTo(px(point.x), height - bottom); ctx.stroke();
    ctx.setLineDash([]);
  }
  canvas.onpointermove = (event) => {
    const localX = event.clientX - canvas.getBoundingClientRect().left;
    const index = Math.max(0, Math.min(data.parametros.pasos, Math.round((localX - left) / pw * data.parametros.pasos)));
    if (index !== selectedNode) { selectedNode = index; nodeReadout(index); drawChart(); }
  };
}

function nodeReadout(index) {
  const e = data.euler.puntos[index], h = data.heun.puntos[index];
  $("#chart-readout").textContent = `Nodo ${index} · x = ${fmt(e.x)} · Euler = ${fmt(e.y)} · Heun = ${fmt(h.y)}`;
}

function fullReport() {
  const p = data.parametros;
  const lines = ["SESIÓN 14 — ECUACIONES DIFERENCIALES ORDINARIAS", "(y² − x²) dx + xy dy = 0", "f(x,y) = x/y − y/x", `y(${p.x0}) = ${p.y0}; x_final = ${p.x_final}; h = ${p.h}; pasos = ${p.pasos}`, `C = ${data.constante}`, "y(x) = signo(y0) sqrt(x²/2 + C/x²)", `Valor exacto: ${data.valor_exacto}`, ""];
  for (const name of ["euler", "heun"]) {
    lines.push(name.toUpperCase());
    for (const r of data[name].traza) {
      lines.push(`Paso ${r.iteracion}: x=${r.x}, y=${r.y}, h=${r.h}`, `k1 = (${r.x})/(${r.y}) - (${r.y})/(${r.x}) = ${r.k1}`);
      if (name === "heun") lines.push(`z = ${r.y} + (${r.h})*(${r.k1}) = ${r.predictor}`, `k2 = (${r.x_siguiente})/(${r.predictor}) - (${r.predictor})/(${r.x_siguiente}) = ${r.k2}`, `Corrector: ${r.y} + (${r.h}/2)*(${r.k1} + ${r.k2}) = ${r.y_siguiente}`);
      else lines.push(`y siguiente = ${r.y} + (${r.h})*(${r.k1}) = ${r.y_siguiente}`);
      lines.push(`Incremento = ${r.incremento}; x siguiente = ${r.x_siguiente}`, "");
    }
    lines.push(`Resultado: ${data[name].valor}`, `Error absoluto: ${data[name].errores.absoluto}`, `Error relativo (%): ${data[name].errores.relativo_porcentual}`, "");
  }
  lines.push(`Menor error: ${data.mas_preciso}. Comparación para los parámetros indicados.`);
  return lines.join("\n");
}

$("#copy").addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(fullReport());
    $("#copy-status").textContent = "Cálculos completos copiados, sin redondear los valores.";
  } catch {
    $("#copy-status").textContent = "El navegador no permitió copiar. Se descargará el informe como texto.";
    const url = URL.createObjectURL(new Blob([fullReport()], {type: "text/plain;charset=utf-8"}));
    const link = document.createElement("a"); link.href = url; link.download = "calculos-euler-heun.txt"; link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
});
form.addEventListener("submit", (event) => { event.preventDefault(); calculate(); });
form.addEventListener("input", markChanges);
$("#restore").addEventListener("click", () => { form.reset(); markChanges(); calculate(); });
$("#step-select").addEventListener("change", () => { renderStep(); selectedNode = Number($("#step-select").value) + 1; nodeReadout(selectedNode); drawChart(); });
document.querySelectorAll("[data-series]").forEach((el) => el.addEventListener("change", drawChart));
new ResizeObserver(drawChart).observe($(".chart-wrap"));
calculate(false);