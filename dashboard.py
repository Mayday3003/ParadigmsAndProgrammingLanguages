"""Genera el dashboard HTML (un solo archivo) a partir de resultados.json."""

from __future__ import annotations

import json
from pathlib import Path


def generar(res: dict, destino: Path) -> Path:
    datos = json.dumps(res, ensure_ascii=False).replace("</", "<\\/")
    destino.write_text(PLANTILLA.replace("__DATOS__", datos), encoding="utf-8")
    return destino


PLANTILLA = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Scala vs Python</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<script>try { const t = localStorage.getItem('tema'); if (t) document.documentElement.dataset.theme = t; } catch (e) {}</script>
<style>
:root{
  --bg:#f6f7f9;--panel:#fff;--ink:#18202c;--muted:#5d6878;--line:#e3e7ed;--soft:#f0f2f5;
  --scala:#c8323a;--scala-soft:#fbe9ea;--python:#2f6fa8;--python-soft:#e6f0f9;
  --ok:#1f8a5b;--ok-soft:#e5f5ed;--bad:#c0392b;--bad-soft:#fbeaea;--warn:#b7791f;--warn-soft:#fdf3e1;
  --shadow:0 1px 2px rgba(16,24,40,.05),0 2px 8px rgba(16,24,40,.04);
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#0f1319;--panel:#171c24;--ink:#e6e9ee;--muted:#98a2b3;--line:#2a313c;--soft:#1e242e;
  --scala:#f0676d;--scala-soft:#3a1f22;--python:#6aa8e0;--python-soft:#1b2a3a;
  --ok:#4cc38a;--ok-soft:#173326;--bad:#f07167;--bad-soft:#3a1d1b;--warn:#e5b454;--warn-soft:#352a14;--shadow:none}}
:root[data-theme="dark"]{
  --bg:#0f1319;--panel:#171c24;--ink:#e6e9ee;--muted:#98a2b3;--line:#2a313c;--soft:#1e242e;
  --scala:#f0676d;--scala-soft:#3a1f22;--python:#6aa8e0;--python-soft:#1b2a3a;
  --ok:#4cc38a;--ok-soft:#173326;--bad:#f07167;--bad-soft:#3a1d1b;--warn:#e5b454;--warn-soft:#352a14;--shadow:none}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:28px 16px 64px}
header{display:flex;flex-wrap:wrap;gap:16px;justify-content:space-between;align-items:flex-end;margin-bottom:22px}
h1{font-size:28px;line-height:1.15;margin:0 0 6px;letter-spacing:-.02em}
h2{font-size:19px;margin:0 0 4px}
h3{font-size:15px;margin:0 0 8px}
.sub{color:var(--muted);margin:0}
.meta{color:var(--muted);font-size:13px;text-align:right}
.meta code{background:var(--soft);padding:1px 6px;border-radius:5px}
nav{display:flex;gap:6px;flex-wrap:wrap;margin:0 0 22px;position:sticky;top:0;background:var(--bg);padding:8px 0;z-index:5}
nav a{color:var(--ink);text-decoration:none;font-size:13px;padding:6px 11px;border:1px solid var(--line);border-radius:999px;background:var(--panel)}
nav a:hover{border-color:var(--muted)}
section{margin:0 0 34px}
.sec-head{margin-bottom:14px}
.sec-head p{color:var(--muted);margin:2px 0 0;font-size:14px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px;box-shadow:var(--shadow)}
.grid{display:grid;gap:14px}
.g2{grid-template-columns:repeat(2,minmax(0,1fr))}
.g3{grid-template-columns:repeat(3,minmax(0,1fr))}
.g4{grid-template-columns:repeat(4,minmax(0,1fr))}
@media(max-width:900px){.g3,.g4{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:620px){.g2,.g3,.g4{grid-template-columns:1fr}h1{font-size:23px}.meta{text-align:left}}
.tag{white-space:nowrap;display:inline-block;font-size:12px;font-weight:650;padding:2px 9px;border-radius:999px}
.t-scala{background:var(--scala-soft);color:var(--scala)}
.t-python{background:var(--python-soft);color:var(--python)}
.t-tie{background:var(--soft);color:var(--muted)}
.t-ok{background:var(--ok-soft);color:var(--ok)}
.t-bad{background:var(--bad-soft);color:var(--bad)}
.t-warn{background:var(--warn-soft);color:var(--warn)}
.hero{display:grid;grid-template-columns:1.3fr 1fr;gap:14px}
@media(max-width:900px){.hero{grid-template-columns:1fr}}
.verdict-big{font-size:22px;font-weight:700;margin:6px 0 4px;letter-spacing:-.01em}
.score-row{display:flex;align-items:center;gap:10px;margin:7px 0;font-size:13px}
.score-row .lbl{width:58px;color:var(--muted)}
.bar{flex:1;height:9px;background:var(--soft);border-radius:99px;overflow:hidden}
.bar>i{display:block;height:100%;border-radius:99px}
.score-row b{width:40px;text-align:right;font-variant-numeric:tabular-nums}
.esc h3{display:flex;gap:8px;align-items:center}
.esc .ico{font-size:18px;width:26px;text-align:center}
.esc .desc{color:var(--muted);font-size:13px;margin:0 0 10px;min-height:38px}
.why{font-size:13px;margin:10px 0 0;padding:0;list-style:none}
.why li{padding:3px 0;color:var(--muted)}
.why li b{color:var(--ink);font-weight:600}
.kpi .v{font-size:24px;font-weight:700;font-variant-numeric:tabular-nums}
.kpi .l{color:var(--muted);font-size:12.5px}
.kpi .vs{display:flex;gap:14px;align-items:baseline}
.kpi .vs span{font-size:12px;color:var(--muted)}
table{width:100%;border-collapse:collapse;font-size:13.5px}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:12px;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:.03em}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}
.tbl{overflow-x:auto}
.win{font-weight:700}
.chart{position:relative;height:320px}
.chart.sm{height:260px}
.note{font-size:13px;color:var(--muted)}
.empty{color:var(--muted);font-size:14px;padding:14px;background:var(--soft);border-radius:10px}
select,button{font:inherit;color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:6px 10px}
.toolbar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:12px}
.rule{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px dashed var(--line);font-size:14px}
.rule:last-child{border:0}
details{margin-top:10px}summary{cursor:pointer;color:var(--muted);font-size:13px}
.legend{display:flex;gap:14px;font-size:13px;color:var(--muted)}
.legend i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:6px;vertical-align:-1px}
.gar-cell{display:flex;flex-direction:column;gap:4px}
.gar-cell .note{font-size:12px}
pre.inj{margin:6px 0 0;padding:8px 10px;background:var(--soft);border-radius:8px;font-size:12px;white-space:pre-wrap;overflow-x:auto}
.big{font-size:34px;font-weight:750;letter-spacing:-.02em;font-variant-numeric:tabular-nums;line-height:1.1}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12.5px}
a{color:var(--python)}
</style>
</head>
<body>
<div class="wrap">
<header>
  <div>
    <h1>Scala vs Python · Soporte360</h1>
    <p class="sub">Análisis comparativo con SonarQube, métricas estáticas, reglas funcionales y rendimiento</p>
  </div>
  <div class="meta" id="meta"></div>
</header>
<nav>
  <a href="#veredicto">Veredicto</a><a href="#garantias">Garantías funcionales</a><a href="#escenarios">Escenarios</a><a href="#criterios">Criterios</a>
  <a href="#sonar">SonarQube</a><a href="#complejidad">Complejidad</a><a href="#reglas">Reglas funcionales</a>
  <a href="#rendimiento">Rendimiento</a><a href="#cambios">Cambios</a><a href="#metodo">Metodología</a>
  <button id="tema" style="margin-left:auto">◐ Tema</button>
</nav>

<section id="veredicto"><div class="hero">
  <div class="card" id="hero-main"></div>
  <div class="card"><h3>Puntaje por escenario</h3><div class="chart sm"><canvas id="c-esc"></canvas></div></div>
</div></section>

<section id="garantias">
  <div class="sec-head"><h2>Garantías del paradigma funcional</h2><p>Experimentos sobre copias del código: ¿el lenguaje <b>impide</b> romper las reglas funcionales, o depende solo de la disciplina del programador?</p></div>
  <div id="garantias-body"></div>
</section>

<section id="escenarios">
  <div class="sec-head"><h2>¿Cuál es mejor en cada escenario?</h2><p>Cada escenario pondera los criterios de forma distinta. Los pesos se editan en <code>escenarios.json</code>.</p></div>
  <div class="grid g3" id="esc-cards"></div>
</section>

<section id="criterios">
  <div class="sec-head"><h2>Criterios (puntaje 0–10)</h2><p>Normalización relativa entre ambos lenguajes. Los criterios cualitativos no se miden del código y están marcados.</p></div>
  <div class="grid g2" style="align-items:start">
    <div class="card" style="position:sticky;top:56px"><div class="toolbar"><label>Escenario <select id="sel-radar"></select></label></div><div class="chart"><canvas id="c-radar"></canvas></div></div>
    <div class="card tbl" id="tabla-criterios"></div>
  </div>
</section>

<section id="sonar">
  <div class="sec-head"><h2>SonarQube · SonarAnalyzer</h2><p id="sonar-sub"></p></div>
  <div id="sonar-body"></div>
</section>

<section id="complejidad">
  <div class="sec-head"><h2>Complejidad por función (lizard)</h2><p>Mismo analizador y mismo criterio para ambos lenguajes.</p></div>
  <div class="grid g4" id="kpi-comp" style="margin-bottom:14px"></div>
  <div class="grid g2">
    <div class="card"><h3>Funciones más complejas · Scala</h3><div class="chart"><canvas id="c-fn-scala"></canvas></div></div>
    <div class="card"><h3>Funciones más complejas · Python</h3><div class="chart"><canvas id="c-fn-python"></canvas></div></div>
  </div>
</section>

<section id="reglas">
  <div class="sec-head"><h2>Reglas de la práctica</h2><p>Detectadas sobre el árbol de sintaxis (Python) y con un lexer que ignora comentarios y textos (Scala).</p></div>
  <div class="grid g2" id="reglas-body"></div>
</section>

<section id="rendimiento">
  <div class="sec-head"><h2>Rendimiento y equivalencia</h2><p id="rend-sub"></p></div>
  <div id="rend-body"></div>
</section>

<section id="cambios">
  <div class="sec-head"><h2>Cambios respecto a la ejecución anterior</h2><p>Se compara automáticamente con el último análisis guardado en <code>salidas/historial</code>.</p></div>
  <div class="card" id="cambios-body"></div>
</section>

<section id="metodo">
  <div class="sec-head"><h2>Metodología</h2></div>
  <div class="card note" id="metodo-body"></div>
</section>
</div>

<script>
const D = __DATOS__;
const IDS = Object.keys(D.lenguajes);
const NOM = id => D.lenguajes[id].nombre;
const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const COL = id => css('--' + id);
const fmt = (v, d = 2) => v == null || Number.isNaN(v) ? '—' : Number(v).toLocaleString('es-CO', {maximumFractionDigits: d, minimumFractionDigits: 0});
const tag = id => id ? `<span class="tag t-${id}">${NOM(id)}</span>` : '<span class="tag t-tie">Empate</span>';
const $ = id => document.getElementById(id);
const P = D.puntaje, charts = [];
Chart.defaults.animation = false;
Chart.defaults.font.family = getComputedStyle(document.body).fontFamily;

function bars(tot) {
  return IDS.map(i => `<div class="score-row"><span class="lbl">${NOM(i)}</span><span class="bar"><i style="width:${tot[i] * 10}%;background:${COL(i)}"></i></span><b>${fmt(tot[i])}</b></div>`).join('');
}

// ---------- Encabezado y veredicto ----------
$('meta').innerHTML = `Generado ${new Date(D.fecha).toLocaleString('es-CO')}<br>` +
  IDS.map(i => `${NOM(i)}: ${D.lenguajes[i].archivos.length} archivos · huella <code>${D.lenguajes[i].huella}</code>`).join('<br>');

(function hero() {
  const v = P.victorias, ord = [...IDS].sort((a, b) => v[b] - v[a]);
  const lider = v[ord[0]] > v[ord[1]] ? ord[0] : null;
  const fun = P.escenarios.find(e => e.id === 'funcional');
  $('hero-main').innerHTML = `
    <span class="note">Veredicto global</span>
    <div class="verdict-big">${lider ? `${NOM(lider)} gana ${v[lider]} de ${P.escenarios.length} escenarios` : 'Resultado dividido entre escenarios'}</div>
    <p class="note" style="margin:0 0 12px">${IDS.map(i => `${NOM(i)}: ${v[i]} victorias`).join(' · ')}${P.empates ? ` · ${P.empates} empates` : ''}. No existe un "mejor lenguaje" absoluto: depende del contexto.</p>
    ${fun ? `<div class="card" style="background:var(--soft);border:0;box-shadow:none"><h3>Para esta práctica (paradigma funcional estricto): ${tag(fun.ganador)}</h3>${bars(fun.totales)}
      <ul class="why">${fun.a_favor.map(a => `<li><b>${a.nombre}</b> · ventaja de ${fmt(a.diferencia)} pts (peso ${a.peso})</li>`).join('')}</ul>
      ${D.garantias && D.garantias.estado === 'ok' ? `<p class="note" style="margin:10px 0 0">Errores atrapados antes de ejecutar: ${IDS.map(i => `<b>${NOM(i)} ${D.garantias.resumen[i].detectados_antes}/${D.garantias.resumen[i].aplicables}</b>`).join(' · ')}. Recursión máxima: ${IDS.map(i => `<b>${NOM(i)} ${fmt(D.garantias.resumen[i].max_recursion, 0)}</b>`).join(' · ')}. <a href="#garantias">Ver experimentos ↓</a></p>` : ''}</div>` : ''}`;
})();

charts.push(new Chart($('c-esc'), {
  type: 'bar',
  data: {labels: P.escenarios.map(e => e.nombre), datasets: IDS.map(i => ({label: NOM(i), data: P.escenarios.map(e => e.totales[i]), backgroundColor: COL(i), borderRadius: 4, maxBarThickness: 16}))},
  options: {indexAxis: 'y', maintainAspectRatio: false, scales: {x: {min: 0, max: 10, grid: {color: css('--line')}, ticks: {color: css('--muted')}}, y: {grid: {display: false}, ticks: {color: css('--ink'), font: {size: 11}}}},
    plugins: {legend: {labels: {color: css('--ink'), boxWidth: 10}}}}
}));


// ---------- Garantías funcionales ----------
(function garantias() {
  const G = D.garantias;
  if (!G || G.estado !== 'ok') { $('garantias-body').innerHTML = '<div class="empty">Experimentos omitidos en esta ejecución (--sin-garantias).</div>'; return; }
  const R = G.resumen;
  const EST = {
    compilacion: ['t-ok', '✔ Detectado al compilar'], advertencia: ['t-ok', '✔ Advertencia del compilador'],
    ejecucion: ['t-warn', '⚠ Solo falla al ejecutar'], silencioso: ['t-bad', '✖ Resultado incorrecto sin aviso'],
    no_detectado: ['t-bad', '✖ No detectado'], no_aplica: ['t-tie', '— No aplicable'],
  };
  const filas = G.mutaciones[IDS[0]].map((m, k) => ({m, celdas: IDS.map(i => G.mutaciones[i][k])}));
  const maxN = Math.max(...G.recursion.map(f => f.n));
  $('garantias-body').innerHTML = `
    <div class="grid g4" style="margin-bottom:14px">
      ${IDS.map(i => `<div class="card kpi"><div class="l">${NOM(i)} · errores atrapados antes de ejecutar</div>
        <div class="big" style="color:${R[i].pct_antes >= 50 ? 'var(--ok)' : 'var(--bad)'}">${R[i].detectados_antes}/${R[i].aplicables}</div>
        <div class="note">${fmt(R[i].pct_antes, 0)} % · ${R[i].no_detectados} nunca detectados</div></div>`).join('')}
      ${IDS.map(i => `<div class="card kpi"><div class="l">${NOM(i)} · recursión máxima soportada</div>
        <div class="big" style="color:${R[i].max_recursion >= maxN ? 'var(--ok)' : 'var(--bad)'}">${fmt(R[i].max_recursion, 0)}</div>
        <div class="note">${R[i].max_recursion >= maxN ? 'superó todas las pruebas' : 'último tamaño que terminó; con el siguiente desbordó la pila'}</div></div>`).join('')}
    </div>
    <div class="card tbl"><h3>Experimento A · Errores inyectados</h3>
      <p class="note" style="margin-top:0">Se introduce cada error en una copia del proyecto y se observa cuándo lo detecta el lenguaje. Lo ideal en programación funcional es detectarlo <b>antes de ejecutar</b>.</p>
      <table><thead><tr><th>Error introducido</th>${IDS.map(i => `<th>${NOM(i)}</th>`).join('')}</tr></thead><tbody>${
        filas.map(({m, celdas}) => `<tr><td><b>${m.nombre}</b><div class="note">${m.descripcion}</div></td>${celdas.map(c => {
          const [cls, txt] = EST[c.estado] || ['t-tie', c.estado];
          return `<td><div class="gar-cell"><span class="tag ${cls}" style="align-self:flex-start">${txt}</span><span class="note mono">${c.mensaje || ''}</span>${c.codigo ? `<details><summary>Código inyectado</summary><pre class="inj">${c.codigo.replace(/</g, '&lt;')}</pre></details>` : ''}</div></td>`;
        }).join('')}</tr>`).join('')}</tbody></table></div>
    <div class="grid g2" style="margin-top:14px">
      <div class="card"><h3>Experimento B · Recursión bajo estrés</h3><div class="chart sm"><canvas id="c-rec"></canvas></div>
        <p class="note">Sin ciclos, todo se repite con recursión. Scala usa <code>@tailrec</code> (el compilador la convierte en un ciclo y no consume pila); Python no optimiza la recursión de cola y tiene un límite de profundidad.</p></div>
      <div class="card tbl"><h3>Detalle de la prueba de estrés</h3><table><thead><tr><th class="n">Solicitudes</th>${IDS.map(i => `<th>${NOM(i)}</th>`).join('')}</tr></thead><tbody>${
        G.recursion.map(f => `<tr><td class="n">${fmt(f.n, 0)}</td>${IDS.map(i => { const d = f.lenguajes[i];
          return `<td>${d.ok ? `<span class="tag t-ok">✔ ${fmt(d.tiempo_s, 2)} s</span>` : `<span class="tag t-bad">✖ falló</span><div class="note mono">${d.error || ''}</div>`}</td>`; }).join('')}</tr>`).join('')}</tbody></table></div>
    </div>`;
  charts.push(new Chart($('c-rec'), {type: 'bar',
    data: {labels: G.recursion.map(f => fmt(f.n, 0) + ' solicitudes'), datasets: IDS.map(i => ({label: NOM(i), data: G.recursion.map(f => f.lenguajes[i].ok ? 1 : 0), backgroundColor: COL(i), borderRadius: 4}))},
    options: {maintainAspectRatio: false, scales: {y: {min: 0, max: 1, ticks: {stepSize: 1, color: css('--muted'), callback: v => v ? '✔ terminó' : '✖ falló'}, grid: {color: css('--line')}}, x: {grid: {display: false}, ticks: {color: css('--ink')}}},
      plugins: {legend: {labels: {color: css('--ink'), boxWidth: 10}}, tooltip: {callbacks: {label: c => `${c.dataset.label}: ${c.raw ? 'terminó' : 'falló'}`}}}}}));
})();

// ---------- Escenarios ----------
$('esc-cards').innerHTML = P.escenarios.map(e => `
  <div class="card esc">
    <h3><span class="ico">${e.icono}</span>${e.nombre}</h3>
    <p class="desc">${e.descripcion}</p>
    <div style="margin-bottom:6px">${tag(e.ganador)} <span class="note">margen ${fmt(e.margen)}</span></div>
    ${bars(e.totales)}
    <ul class="why">
      ${e.a_favor.map(a => `<li>✔ <b>${a.nombre}</b> (+${fmt(a.diferencia)}, peso ${a.peso})</li>`).join('')}
      ${e.en_contra.map(a => `<li>✖ <b>${a.nombre}</b> favorece al otro (${fmt(a.diferencia)})</li>`).join('')}
      ${e.omitidos.length ? `<li>Sin datos: ${e.omitidos.join(', ')}</li>` : ''}
    </ul>
  </div>`).join('');

// ---------- Criterios ----------
const CR = P.criterios, CIDS = Object.keys(CR);
$('sel-radar').innerHTML = '<option value="">Todos los criterios</option>' + P.escenarios.map(e => `<option value="${e.id}">${e.nombre}</option>`).join('');
let radar;
function dibujarRadar() {
  const esc = P.escenarios.find(e => e.id === $('sel-radar').value);
  const ids = esc ? Object.keys(esc.pesos) : CIDS;
  radar && radar.destroy();
  radar = new Chart($('c-radar'), {
    type: 'radar',
    data: {labels: ids.map(c => CR[c].nombre + (CR[c].tipo === 'cualitativo' ? ' *' : '')),
      datasets: IDS.map(i => ({label: NOM(i), data: ids.map(c => CR[c].puntajes[i]), borderColor: COL(i), backgroundColor: COL(i) + '33', pointBackgroundColor: COL(i), borderWidth: 2}))},
    options: {maintainAspectRatio: false, scales: {r: {min: 0, max: 10, ticks: {stepSize: 2, color: css('--muted'), backdropColor: 'transparent'}, grid: {color: css('--line')}, angleLines: {color: css('--line')}, pointLabels: {color: css('--ink'), font: {size: 11}}}},
      plugins: {legend: {labels: {color: css('--ink'), boxWidth: 10}}}}
  });
}
$('sel-radar').onchange = dibujarRadar; dibujarRadar();

$('tabla-criterios').innerHTML = `<table><thead><tr><th>Criterio</th>${IDS.map(i => `<th class="n">${NOM(i)}</th>`).join('')}</tr></thead><tbody>${
  CIDS.map(c => {
    const p = CR[c].puntajes, best = Math.max(...IDS.map(i => p[i]));
    const sub = CR[c].tipo === 'cualitativo' ? `<div class="note">* Cualitativo: ${CR[c].justificacion}</div>` :
      CR[c].submetricas.map(s => `<div class="note">${s.descripcion}: ${IDS.map(i => `${NOM(i)} ${fmt(s.valores[i])}`).join(' · ')}</div>`).join('');
    return `<tr><td><b>${CR[c].nombre}</b>${sub}</td>${IDS.map(i => `<td class="n ${p[i] === best ? 'win' : ''}">${fmt(p[i])}</td>`).join('')}</tr>`;
  }).join('')}</tbody></table>`;

// ---------- SonarQube ----------
(function sonar() {
  const S = D.sonar;
  if (S.estado !== 'ok') {
    $('sonar-sub').textContent = 'No disponible en esta ejecución.';
    $('sonar-body').innerHTML = `<div class="empty">SonarQube no se ejecutó: ${S.motivo}. Define <code>SONAR_TOKEN</code> y vuelve a correr <code>./analizar.sh</code>.</div>`;
    return;
  }
  $('sonar-sub').innerHTML = `Analizado en SonarQube Cloud con los perfiles “Sonar way”. <a href="${S.url}" target="_blank" rel="noopener">Abrir tablero en SonarQube ↗</a>`;
  const L = S.lenguajes;
  const filas = [
    ['Calificación mantenibilidad', 'nota_mantenibilidad', 'nota'], ['Calificación confiabilidad', 'nota_confiabilidad', 'nota'], ['Calificación seguridad', 'nota_seguridad', 'nota'],
    ['Líneas de código', 'ncloc', 'min'], ['Funciones', 'functions'], ['Complejidad ciclomática', 'complexity', 'min'], ['Complejidad cognitiva', 'cognitive_complexity', 'min'],
    ['Cognitiva por función', 'complejidad_cognitiva_por_funcion', 'min'], ['Bugs', 'bugs', 'min'], ['Vulnerabilidades', 'vulnerabilities', 'min'], ['Security hotspots', 'hotspots', 'min'],
    ['Code smells', 'code_smells', 'min'], ['Deuda técnica (min)', 'sqale_index', 'min'], ['Ratio de deuda (%)', 'deuda_ratio', 'min'], ['Duplicación (%)', 'duplicacion_pct', 'min'], ['Comentarios (%)', 'comentarios_pct']];
  const celda = (k, modo, i) => {
    const v = L[i][k];
    if (modo === 'nota') return `<span class="tag ${v === 'A' ? 't-ok' : v <= 'C' ? 't-warn' : 't-bad'}">${v}</span>`;
    const otros = IDS.map(j => L[j][k]); const win = modo === 'min' && v === Math.min(...otros) && new Set(otros).size > 1;
    return `<span class="${win ? 'win' : ''}">${fmt(v)}</span>`;
  };
  const issues = IDS.flatMap(i => L[i].issues.map(x => ({...x, lang: i})));
  $('sonar-body').innerHTML = `<div class="grid g2">
    <div class="card tbl"><table><thead><tr><th>Métrica</th>${IDS.map(i => `<th class="n">${NOM(i)}</th>`).join('')}</tr></thead>
      <tbody>${filas.map(([n, k, m]) => `<tr><td>${n}</td>${IDS.map(i => `<td class="n">${celda(k, m, i)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>
    <div class="card"><h3>Complejidad cognitiva por archivo</h3><div class="chart"><canvas id="c-sonar-arch"></canvas></div></div>
  </div>
  <div class="card tbl" style="margin-top:14px"><h3>Issues abiertos (${issues.length})</h3>${issues.length ? `<table><thead><tr><th>Lenguaje</th><th>Tipo</th><th>Severidad</th><th>Archivo</th><th>Mensaje</th></tr></thead><tbody>${
    issues.map(x => `<tr><td>${tag(x.lang)}</td><td>${x.type}</td><td>${x.severity}</td><td class="mono">${x.archivo}:${x.line ?? ''}</td><td>${x.message}</td></tr>`).join('')}</tbody></table>` : '<div class="empty">Sin issues: ningún bug, vulnerabilidad ni code smell en ambos lenguajes.</div>'}</div>`;
  const arch = IDS.flatMap(i => L[i].por_archivo.map(a => ({lang: i, nombre: a.archivo.split('/').pop(), v: a.cognitive_complexity || 0}))).sort((a, b) => b.v - a.v);
  charts.push(new Chart($('c-sonar-arch'), {type: 'bar',
    data: {labels: arch.map(a => a.nombre), datasets: [{label: 'Complejidad cognitiva', data: arch.map(a => a.v), backgroundColor: arch.map(a => COL(a.lang)), borderRadius: 4}]},
    options: {indexAxis: 'y', maintainAspectRatio: false, plugins: {legend: {display: false}}, scales: {x: {grid: {color: css('--line')}, ticks: {color: css('--muted')}}, y: {grid: {display: false}, ticks: {color: css('--ink'), font: {size: 11}}}}}}));
})();

// ---------- Complejidad ----------
(function comp() {
  const E = D.estatico;
  const k = [['Funciones', 'funciones', 0], ['CCN promedio', 'ccn_promedio', 2], ['CCN máximo', 'ccn_maximo', 0], ['Líneas por función', 'nloc_promedio_funcion', 2]];
  $('kpi-comp').innerHTML = k.map(([l, key, d]) => `<div class="card kpi"><div class="l">${l}</div><div class="vs">${IDS.map(i => `<div><div class="v" style="color:${COL(i)}">${fmt(E[i].complejidad[key], d)}</div><span>${NOM(i)}</span></div>`).join('')}</div></div>`).join('');
  IDS.forEach(i => {
    const top = E[i].complejidad.detalle.slice(0, 12);
    charts.push(new Chart($('c-fn-' + i), {type: 'bar',
      data: {labels: top.map(f => f.funcion.split('::').pop()), datasets: [{label: 'Complejidad ciclomática', data: top.map(f => f.ccn), backgroundColor: COL(i), borderRadius: 4}]},
      options: {indexAxis: 'y', maintainAspectRatio: false, plugins: {legend: {display: false}, tooltip: {callbacks: {afterLabel: c => `${top[c.dataIndex].archivo}:${top[c.dataIndex].linea} · ${top[c.dataIndex].nloc} líneas`}}},
        scales: {x: {beginAtZero: true, ticks: {stepSize: 1, color: css('--muted')}, grid: {color: css('--line')}}, y: {grid: {display: false}, ticks: {color: css('--ink'), font: {size: 11}}}}}}));
  });
})();

// ---------- Reglas ----------
$('reglas-body').innerHTML = IDS.map(i => {
  const R = D.estatico[i].reglas, total = R.total_violaciones;
  return `<div class="card"><h3>${tag(i)} ${total ? `<span class="tag t-bad">${total} violaciones</span>` : '<span class="tag t-ok">Cumple todas las reglas</span>'}</h3>
    ${Object.entries(R.por_regla).map(([r, n]) => `<div class="rule"><span>${r}</span><span class="tag ${n ? 't-bad' : 't-ok'}">${n ? n : '✔ 0'}</span></div>`).join('')}
    <h3 style="margin-top:14px">Recursos funcionales usados</h3>
    ${Object.entries(R.positivos).map(([r, n]) => `<div class="rule"><span>${r.replace('_', ' ')}</span><b>${n}</b></div>`).join('')}
    ${total ? `<details><summary>Ver ubicaciones</summary><table>${R.violaciones.map(v => `<tr><td class="mono">${v.archivo}:${v.linea}</td><td>${v.regla}</td><td>${v.detalle}</td></tr>`).join('')}</table></details>` : ''}
  </div>`;
}).join('');

// ---------- Rendimiento ----------
(function rend() {
  const R = D.rendimiento;
  if (!R) { $('rend-sub').textContent = ''; $('rend-body').innerHTML = '<div class="empty">Benchmarks omitidos en esta ejecución (--sin-rendimiento).</div>'; return; }
  $('rend-sub').textContent = `Entradas generadas con la misma semilla; ${R.corridas} corridas por medición con hyperfine (1 de calentamiento).`;
  const T = R.tamanos, tiempo = (f, i) => { const d = f.lenguajes[i]; return d && d.ok ? (d.hyperfine ? d.hyperfine.mean : d.tiempo_s) : null; };
  const prep = R.preparacion;
  $('rend-body').innerHTML = `
    <div class="grid g4" style="margin-bottom:14px">${IDS.map(i => `<div class="card kpi"><div class="l">${NOM(i)} · preparación</div><div class="v" style="color:${COL(i)}">${prep[i].ok ? fmt(prep[i].construccion_s) + ' s' : '✖'}</div><div class="note">${prep[i].ok ? (i === 'scala' ? 'sbt clean compile' : 'verificación de sintaxis') + ' · ' + prep[i].punto_entrada : prep[i].error}</div></div>`).join('')}
      ${IDS.map(i => { const ok = T.filter(f => f.lenguajes[i] && f.lenguajes[i].ok).length; return `<div class="card kpi"><div class="l">${NOM(i)} · ejecuciones exitosas</div><div class="v" style="color:${ok === T.length ? 'var(--ok)' : 'var(--bad)'}">${ok}/${T.length}</div><div class="note">tamaños: ${T.map(f => f.n).join(', ')}</div></div>`; }).join('')}</div>
    <div class="grid g2">
      <div class="card"><h3>Tiempo total vs. cantidad de solicitudes</h3><div class="chart"><canvas id="c-tiempo"></canvas></div><p class="note">Incluye el arranque del proceso (JVM en Scala, intérprete en Python). Escala logarítmica.</p></div>
      <div class="card"><h3>Memoria máxima (MB)</h3><div class="chart"><canvas id="c-mem"></canvas></div></div>
    </div>
    <div class="card tbl" style="margin-top:14px"><h3>Detalle por tamaño y equivalencia de resultados</h3><table><thead><tr><th class="n">Solicitudes</th>${IDS.map(i => `<th class="n">${NOM(i)} tiempo (s)</th><th class="n">${NOM(i)} memoria</th>`).join('')}<th>¿Misma salida?</th></tr></thead><tbody>${
      T.map(f => `<tr><td class="n">${fmt(f.n, 0)}</td>${IDS.map(i => { const d = f.lenguajes[i] || {};
        return d.ok ? `<td class="n">${fmt(tiempo(f, i), 3)}${d.hyperfine ? ` <span class="note">±${fmt(d.hyperfine.stddev, 3)}</span>` : ''}</td><td class="n">${fmt(d.memoria_mb, 1)} MB</td>` : `<td colspan="2"><span class="tag t-bad">falló</span> <span class="note">${d.error || ''}</span></td>`; }).join('')}
        <td>${f.equivalencia ? (f.equivalencia.identicas ? '<span class="tag t-ok">Idéntica</span>' : `<span class="tag t-warn">${f.equivalencia.lineas_diferentes} líneas distintas</span><div class="note mono">línea ${f.equivalencia.primera_diferencia.linea}: «${f.equivalencia.primera_diferencia.a}» vs «${f.equivalencia.primera_diferencia.b}»</div>`) : '—'}</td></tr>`).join('')}</tbody></table></div>`;
  const ds = (fn) => IDS.map(i => ({label: NOM(i), data: T.map(f => fn(f, i)), borderColor: COL(i), backgroundColor: COL(i), tension: .25, spanGaps: false, pointRadius: 4}));
  const ejes = (log) => ({x: {title: {display: true, text: 'solicitudes', color: css('--muted')}, grid: {color: css('--line')}, ticks: {color: css('--muted')}}, y: {type: log ? 'logarithmic' : 'linear', beginAtZero: !log, grid: {color: css('--line')}, ticks: {color: css('--muted')}}});
  charts.push(new Chart($('c-tiempo'), {type: 'line', data: {labels: T.map(f => fmt(f.n, 0)), datasets: ds(tiempo)}, options: {maintainAspectRatio: false, scales: ejes(true), plugins: {legend: {labels: {color: css('--ink'), boxWidth: 10}}}}}));
  charts.push(new Chart($('c-mem'), {type: 'bar', data: {labels: T.map(f => fmt(f.n, 0)), datasets: IDS.map(i => ({label: NOM(i), data: T.map(f => (f.lenguajes[i] || {}).ok ? f.lenguajes[i].memoria_mb : null), backgroundColor: COL(i), borderRadius: 4}))}, options: {maintainAspectRatio: false, scales: ejes(false), plugins: {legend: {labels: {color: css('--ink'), boxWidth: 10}}}}}));
})();

// ---------- Cambios ----------
(function cambios() {
  const C = D.comparacion_anterior;
  if (!C) { $('cambios-body').innerHTML = '<div class="empty">Primera ejecución: aún no hay un análisis anterior con el cual comparar.</div>'; return; }
  const codigo = IDS.map(i => `${NOM(i)}: ${C.huellas_anteriores[i] === D.lenguajes[i].huella ? 'sin cambios en el código' : '<b>código modificado</b>'}`).join(' · ');
  $('cambios-body').innerHTML = `<p class="note" style="margin-top:0">Anterior: ${new Date(C.fecha_anterior).toLocaleString('es-CO')} · ${codigo}</p>` + (C.cambios.length ?
    `<div class="tbl"><table><thead><tr><th>Lenguaje</th><th>Indicador</th><th class="n">Antes</th><th class="n">Ahora</th><th class="n">Δ</th></tr></thead><tbody>${
      C.cambios.map(c => `<tr><td>${tag(c.lenguaje)}</td><td>${c.indicador}</td><td class="n">${fmt(c.antes, 3)}</td><td class="n">${fmt(c.ahora, 3)}</td><td class="n">${c.ahora > c.antes ? '▲' : '▼'} ${fmt(Math.abs(c.ahora - c.antes), 3)}</td></tr>`).join('')}</tbody></table></div>`
    : '<div class="empty">Ningún indicador cambió.</div>');
})();

// ---------- Metodología ----------
$('metodo-body').innerHTML = `
  <p><b>Entrada:</b> el código fuente actual de <code>${IDS.map(i => D.lenguajes[i].carpeta).join('</code> y <code>')}</code>. Archivos, funciones, punto de entrada y reglas se detectan automáticamente; la <i>huella</i> del encabezado cambia con cualquier modificación del código.</p>
  <p><b>1. SonarQube Cloud:</b> pysonar envía el código; los SonarAnalyzer de Scala y Python aplican el perfil “Sonar way”. Las métricas por archivo se agregan por lenguaje vía API. Calificación de mantenibilidad: ratio de deuda = deuda / (líneas × 30 min); A ≤ 5 %, B ≤ 10 %, C ≤ 20 %, D ≤ 50 %.</p>
  <p><b>2. lizard:</b> complejidad ciclomática, líneas y parámetros por función con el mismo criterio para ambos lenguajes.</p>
  <p><b>3. Reglas de la práctica:</b> Python con su árbol de sintaxis (<code>ast</code>): for, while, comprensiones, reasignaciones, mutaciones, global. Scala con un lexer que ignora comentarios y textos: var, for, while, do-while, colecciones mutables, return, null.</p>
  <p><b>4. Rendimiento:</b> Scala se compila desde cero (<code>sbt clean compile</code>); luego cada programa procesa entradas de ${D.rendimiento ? D.rendimiento.tamanos.map(f => f.n).join(', ') : '—'} solicitudes. Memoria con <code>/usr/bin/time</code>, tiempos con <code>hyperfine</code>; se comparan las salidas línea por línea.</p>
  <p><b>5. Garantías funcionales:</b> en una copia de cada proyecto se inyectan 5 errores que rompen el paradigma (reasignar, mutar un registro, tipo incorrecto, campo inexistente, match incompleto); los puntos de inyección se detectan automáticamente. Además se procesan ${D.garantias && D.garantias.recursion ? D.garantias.recursion.map(f => f.n).join(', ') : '—'} solicitudes para medir hasta dónde aguanta la recursión.</p>
  <p><b>Puntaje:</b> cada criterio se normaliza entre 0 y 10 de forma relativa (el mejor obtiene 10). El puntaje del escenario es el promedio ponderado; diferencias menores a 0,3 se consideran empate.</p>`;

$('tema').onclick = () => {
  const r = document.documentElement, oscuro = r.dataset.theme ? r.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
  try { localStorage.setItem('tema', oscuro ? 'light' : 'dark'); } catch (e) {}
  r.dataset.theme = oscuro ? 'light' : 'dark'; location.reload();
};
</script>
</body>
</html>
"""
