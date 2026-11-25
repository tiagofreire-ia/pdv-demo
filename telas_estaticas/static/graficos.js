/* Gráficos da demonstração (SVG puro, sem biblioteca).
 * Uso: <div class="nv-grafico" data-grafico="linhas|colunas|barras-h|rosca|spark" data-cfg='{...}'></div>
 * Cores vêm dos tokens do tema (--accent segue a marca do cliente; --g-s1..5 é a paleta categórica
 * validada para daltonismo). Passe o mouse para ver os valores. */
(function () {
  'use strict';
  var NS = 'http://www.w3.org/2000/svg';
  var reduz = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var seq = 0;

  function el(tag, at, pai) {
    var e = document.createElementNS(NS, tag);
    for (var k in at) if (at[k] !== undefined && at[k] !== null) e.setAttribute(k, at[k]);
    if (pai) pai.appendChild(e);
    return e;
  }
  function txt(pai, x, y, s, at) {
    var t = el('text', Object.assign({ x: x, y: y }, at || {}), pai);
    t.textContent = s;
    return t;
  }
  function brl(v) { return 'R$ ' + Number(v).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
  function brlCurto(v) {
    if (Math.abs(v) >= 1000) return 'R$ ' + (v / 1000).toLocaleString('pt-BR', { maximumFractionDigits: 1 }) + ' mil';
    return 'R$ ' + Math.round(v).toLocaleString('pt-BR');
  }
  function fmt(t, v) {
    if (t === 'pct') return v.toLocaleString('pt-BR') + '%';
    if (t === 'num') return Number(v).toLocaleString('pt-BR');
    return brl(v);
  }
  function fmtEixo(t, v) {
    if (t === 'pct') return v + '%';
    if (t === 'num') return String(v);
    return brlCurto(v);
  }
  function cor(c) {
    if (!c || c === 'accent') return 'var(--accent)';
    if (c === 'muted') return 'var(--muted)';
    if (/^s\d$/.test(c)) return 'var(--g-' + c + ')';
    return c;
  }
  function escala(min, max, n) {
    var span = (max - min) || 1, passo = Math.pow(10, Math.floor(Math.log10(span / n))), e = span / n / passo;
    passo *= e >= 7.5 ? 10 : e >= 3.5 ? 5 : e >= 1.5 ? 2 : 1;
    var lo = Math.floor(min / passo) * passo, hi = Math.ceil(max / passo) * passo, t = [];
    for (var v = lo; v <= hi + passo / 1e6; v += passo) t.push(Math.round(v * 1e6) / 1e6);
    return { min: lo, max: hi, t: t };
  }
  /* curva monotônica: suave, sem inventar picos ou vales entre os pontos */
  function curva(p) {
    var n = p.length, i;
    if (n < 2) return '';
    if (n === 2) return 'M' + p[0] + 'L' + p[1];
    var dx = [], m = [], t = [];
    for (i = 0; i < n - 1; i++) { dx[i] = p[i + 1][0] - p[i][0]; m[i] = (p[i + 1][1] - p[i][1]) / dx[i]; }
    t[0] = m[0]; t[n - 1] = m[n - 2];
    for (i = 1; i < n - 1; i++) t[i] = m[i - 1] * m[i] <= 0 ? 0 : (m[i - 1] + m[i]) / 2;
    for (i = 0; i < n - 1; i++) {
      if (m[i] === 0) { t[i] = t[i + 1] = 0; continue; }
      var a = t[i] / m[i], b = t[i + 1] / m[i], s = a * a + b * b;
      if (s > 9) { var k = 3 / Math.sqrt(s); t[i] = k * a * m[i]; t[i + 1] = k * b * m[i]; }
    }
    var d = 'M' + p[0][0] + ',' + p[0][1];
    for (i = 0; i < n - 1; i++) {
      var h = dx[i] / 3;
      d += 'C' + (p[i][0] + h) + ',' + (p[i][1] + t[i] * h) + ' ' + (p[i + 1][0] - h) + ',' + (p[i + 1][1] - t[i + 1] * h) + ' ' + p[i + 1][0] + ',' + p[i + 1][1];
    }
    return d;
  }

  /* ---------- dica (tooltip) compartilhada ---------- */
  var dicaEl;
  function dica(html, x, y) {
    if (!dicaEl) { dicaEl = document.createElement('div'); dicaEl.className = 'nv-dica'; dicaEl.setAttribute('role', 'status'); document.body.appendChild(dicaEl); }
    dicaEl.innerHTML = html;
    dicaEl.hidden = false;
    var r = dicaEl.getBoundingClientRect(), l = x + 16, t = y - r.height - 12;
    if (l + r.width > innerWidth - 8) l = x - r.width - 16;
    if (t < 8) t = y + 16;
    dicaEl.style.left = Math.max(8, l) + 'px';
    dicaEl.style.top = t + 'px';
  }
  function someDica() { if (dicaEl) dicaEl.hidden = true; }
  function linhaDica(c, nome, valor, tracejado) {
    return '<div class="ln"><i style="background:' + c + (tracejado ? ';background:none;border-top:2px dashed ' + c + ';height:0' : '') + '"></i>' +
      '<span>' + nome + '</span><b>' + valor + '</b></div>';
  }

  function animarTraco(p, atraso) {
    if (reduz || !p.getTotalLength) return;
    var L = p.getTotalLength();
    p.style.strokeDasharray = L;
    p.style.strokeDashoffset = L;
    p.getBoundingClientRect();
    p.style.transition = 'stroke-dashoffset 1.1s cubic-bezier(.3,.7,.2,1) ' + (atraso || 0) + 's';
    p.style.strokeDashoffset = 0;
    setTimeout(function () { p.style.strokeDasharray = ''; }, 1300 + (atraso || 0) * 1000);
  }

  /* ---------- linhas / área ---------- */
  function linhas(host, c, W, anim) {
    var H = c.altura || 260, pad = { l: 64, r: c.folgaDireita || 18, t: 22, b: 30 };
    var n = c.rotulos.length, todos = [];
    c.series.forEach(function (s) { s.valores.forEach(function (v) { if (v !== null) todos.push(v); }); });
    if (c.faixa) todos = todos.concat(c.faixa.min, c.faixa.max);
    if (c.limite) todos.push(c.limite.valor);
    var lo = Math.min.apply(null, todos), hi = Math.max.apply(null, todos);
    if (c.zero) lo = Math.min(0, lo);
    var esc = escala(lo, hi, 4);
    var x = function (i) { return pad.l + i * (W - pad.l - pad.r) / (n - 1); };
    var y = function (v) { return pad.t + (esc.max - v) / (esc.max - esc.min) * (H - pad.t - pad.b); };
    var svg = el('svg', { width: W, height: H, viewBox: '0 0 ' + W + ' ' + H, role: 'img', 'aria-label': c.titulo || '' }, host);
    var id = 'g' + (++seq), defs = el('defs', {}, svg);
    // grade
    esc.t.forEach(function (v) {
      el('line', { x1: pad.l, x2: W - pad.r, y1: y(v), y2: y(v), class: 'g-grade' }, svg);
      txt(svg, pad.l - 10, y(v) + 4, fmtEixo(c.fmt, v), { class: 'g-eixo', 'text-anchor': 'end' });
    });
    var cada = Math.max(c.cada || 1, Math.ceil(n / Math.max(2, Math.floor((W - pad.l - pad.r) / 62))));
    c.rotulos.forEach(function (r, i) {
      if (i % cada === 0 || i === n - 1) txt(svg, x(i), H - 8, r, { class: 'g-eixo', 'text-anchor': i === 0 ? 'start' : i === n - 1 ? 'end' : 'middle' });
    });
    // faixa de previsão
    if (c.faixa) {
      var cima = c.faixa.max.map(function (v, i) { return [x(i), y(v)]; });
      var baixo = c.faixa.min.map(function (v, i) { return [x(i), y(v)]; }).reverse();
      el('path', { d: 'M' + cima.join('L') + 'L' + baixo.join('L') + 'Z', class: 'g-faixa' }, svg);
    }
    // limite (linha de referência)
    if (c.limite) {
      var yl = y(c.limite.valor);
      el('line', { x1: pad.l, x2: W - pad.r, y1: yl, y2: yl, class: 'g-limite', stroke: cor(c.limite.cor || '#F97316') }, svg);
      var esq = c.limite.lado === 'esq';
      txt(svg, esq ? pad.l + 6 : W - pad.r, yl - 7, c.limite.texto, { class: 'g-nota', 'text-anchor': esq ? 'start' : 'end' });
    }
    // séries
    var pontos = c.series.map(function (s) {
      var p = [];
      s.valores.forEach(function (v, i) { if (v !== null) p.push([x(i), y(v), i]); });
      return p;
    });
    c.series.forEach(function (s, k) {
      var p = pontos[k], xy = p.map(function (q) { return [q[0], q[1]]; }), d = curva(xy);
      if (!d) return;
      if (s.estilo === 'area') {
        var gid = id + 'a' + k, gr = el('linearGradient', { id: gid, x1: 0, y1: 0, x2: 0, y2: 1 }, defs);
        el('stop', { offset: '0%', 'stop-color': cor(s.cor), 'stop-opacity': 0.30 }, gr);
        el('stop', { offset: '100%', 'stop-color': cor(s.cor), 'stop-opacity': 0 }, gr);
        var base = y(Math.max(esc.min, 0) > esc.min ? Math.max(esc.min, 0) : esc.min);
        var area = el('path', { d: d + 'L' + xy[xy.length - 1][0] + ',' + base + 'L' + xy[0][0] + ',' + base + 'Z', fill: 'url(#' + gid + ')', class: anim && !reduz ? 'g-surge' : '' }, svg);
        area.style.pointerEvents = 'none';
      }
      var linha = el('path', { d: d, fill: 'none', stroke: cor(s.cor), 'stroke-width': s.estilo === 'tracejada' ? 2 : 2.5,
        'stroke-dasharray': s.estilo === 'tracejada' ? '6 5' : null, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, svg);
      if (anim && s.estilo !== 'tracejada') animarTraco(linha, k * 0.15);
      if (s.rotuloFim && xy.length) {
        var ult = xy[xy.length - 1];
        el('circle', { cx: ult[0], cy: ult[1], r: 5, fill: cor(s.cor), class: 'g-anel' }, svg);
        if (s.pulso && !reduz) el('circle', { cx: ult[0], cy: ult[1], r: 5, fill: cor(s.cor), class: 'g-pulso' }, svg);
        txt(svg, ult[0] + (s.rotuloFimLado === 'esq' ? -10 : 10), ult[1] - 10, s.rotuloFim, { class: 'g-nota forte', 'text-anchor': s.rotuloFimLado === 'esq' ? 'end' : 'start' });
      }
    });
    // destaque (ponto crítico)
    if (c.destaque) {
      var dz = c.destaque, sv = c.series[dz.serie || 0].valores[dz.i], cx = x(dz.i), cy = y(sv);
      el('circle', { cx: cx, cy: cy, r: 6, fill: cor(dz.cor || 'var(--erro)'), class: 'g-anel' }, svg);
      if (!reduz) el('circle', { cx: cx, cy: cy, r: 6, fill: cor(dz.cor || 'var(--erro)'), class: 'g-pulso' }, svg);
      var sobe = dz.sobe || 26, ty = cy - sobe;
      var tx = Math.min(Math.max(cx, pad.l + 80), W - pad.r - 80);
      var estreito = W < 600;
      if (sobe > 30 && !estreito) el('line', { x1: cx, x2: cx, y1: cy - 8, y2: ty + 6, class: 'g-mira' }, svg);
      if (!estreito) {
        txt(svg, tx, ty - 14, dz.titulo, { class: 'g-nota forte', 'text-anchor': 'middle' });
        txt(svg, tx, ty, dz.texto, { class: 'g-nota', 'text-anchor': 'middle' });
      }
    }
    // camada de hover: mira + pontos + dica
    var mira = el('line', { y1: pad.t, y2: H - pad.b, class: 'g-mira', visibility: 'hidden' }, svg);
    var marcas = c.series.map(function (s) { return el('circle', { r: 5, fill: cor(s.cor), class: 'g-anel', visibility: 'hidden' }, svg); });
    var alvo = el('rect', { x: pad.l - 10, y: 0, width: W - pad.l - pad.r + 20, height: H, fill: 'transparent' }, svg);
    alvo.style.cursor = 'crosshair';
    function mover(ev) {
      var r = svg.getBoundingClientRect(), px = ev.clientX - r.left;
      var i = Math.round((px - pad.l) / ((W - pad.l - pad.r) / (n - 1)));
      i = Math.max(0, Math.min(n - 1, i));
      mira.setAttribute('x1', x(i)); mira.setAttribute('x2', x(i)); mira.setAttribute('visibility', 'visible');
      var html = '<div class="tt">' + (c.rotulosDica ? c.rotulosDica[i] : c.rotulos[i]) + '</div>';
      c.series.forEach(function (s, k) {
        var v = s.valores[i];
        if (v === null || v === undefined) { marcas[k].setAttribute('visibility', 'hidden'); return; }
        marcas[k].setAttribute('cx', x(i)); marcas[k].setAttribute('cy', y(v)); marcas[k].setAttribute('visibility', 'visible');
        html += linhaDica(cor(s.cor), s.nome, fmt(c.fmt, v), s.estilo === 'tracejada');
      });
      if (c.notas && c.notas[i]) html += '<div class="nt">' + c.notas[i] + '</div>';
      dica(html, ev.clientX, ev.clientY);
    }
    alvo.addEventListener('pointermove', mover);
    alvo.addEventListener('pointerleave', function () {
      mira.setAttribute('visibility', 'hidden');
      marcas.forEach(function (m) { m.setAttribute('visibility', 'hidden'); });
      someDica();
    });
  }

  /* ---------- colunas agrupadas ---------- */
  function colunas(host, c, W, anim) {
    var H = c.altura || 240, pad = { l: 64, r: 10, t: 30, b: 30 };
    var n = c.rotulos.length, todos = [];
    c.series.forEach(function (s) { todos = todos.concat(s.valores); });
    var esc = escala(0, Math.max.apply(null, todos), 4);
    var y = function (v) { return pad.t + (esc.max - v) / (esc.max - esc.min) * (H - pad.t - pad.b); };
    var svg = el('svg', { width: W, height: H, viewBox: '0 0 ' + W + ' ' + H, role: 'img', 'aria-label': c.titulo || '' }, host);
    esc.t.forEach(function (v) {
      el('line', { x1: pad.l, x2: W - pad.r, y1: y(v), y2: y(v), class: v === 0 ? 'g-base' : 'g-grade' }, svg);
      txt(svg, pad.l - 10, y(v) + 4, fmtEixo(c.fmt, v), { class: 'g-eixo', 'text-anchor': 'end' });
    });
    var gw = (W - pad.l - pad.r) / n, ns = c.series.length;
    var bw = Math.min(30, (gw * 0.62 - (ns - 1) * 3) / ns);
    c.rotulos.forEach(function (rot, i) {
      var cx = pad.l + gw * i + gw / 2, x0 = cx - (bw * ns + 3 * (ns - 1)) / 2;
      var g = el('g', {}, svg);
      c.series.forEach(function (s, k) {
        var v = s.valores[i], bx = x0 + k * (bw + 3), by = y(v), bh = y(0) - by, rr = Math.min(4, bh, bw / 2);
        var d = 'M' + bx + ',' + y(0) + 'V' + (by + rr) + 'Q' + bx + ',' + by + ' ' + (bx + rr) + ',' + by + 'H' + (bx + bw - rr) +
          'Q' + (bx + bw) + ',' + by + ' ' + (bx + bw) + ',' + (by + rr) + 'V' + y(0) + 'Z';
        var p = el('path', { d: d, fill: cor(s.cor), class: 'g-barra' + (anim && !reduz ? ' g-cresce' : '') }, g);
        if (anim && !reduz) p.style.animationDelay = (i * 0.08 + k * 0.04) + 's';
      });
      if (c.topo && gw >= 84) txt(svg, cx, Math.min.apply(null, c.series.map(function (s) { return y(s.valores[i]); })) - 9, c.topo[i], { class: 'g-nota forte', 'text-anchor': 'middle' });
      if (gw < 90 && rot.indexOf('–') > 0) {
        var partes = rot.split('–');
        txt(svg, cx, H - 16, partes[0] + '–', { class: 'g-eixo', 'text-anchor': 'middle' });
        txt(svg, cx, H - 3, partes[1], { class: 'g-eixo', 'text-anchor': 'middle' });
      } else txt(svg, cx, H - 8, rot, { class: 'g-eixo', 'text-anchor': 'middle' });
      var alvo = el('rect', { x: pad.l + gw * i, y: pad.t - 20, width: gw, height: H - pad.t - pad.b + 20, fill: 'transparent' }, svg);
      alvo.addEventListener('pointermove', function (ev) {
        g.classList.add('foco'); svg.classList.add('com-foco');
        var html = '<div class="tt">' + (c.rotulosDica ? c.rotulosDica[i] : rot) + '</div>';
        c.series.forEach(function (s) { html += linhaDica(cor(s.cor), s.nome, fmt(c.fmt, s.valores[i])); });
        if (c.notas && c.notas[i]) html += '<div class="nt">' + c.notas[i] + '</div>';
        dica(html, ev.clientX, ev.clientY);
      });
      alvo.addEventListener('pointerleave', function () { g.classList.remove('foco'); svg.classList.remove('com-foco'); someDica(); });
    });
  }

  /* ---------- barras horizontais ---------- */
  function barrasH(host, c, W, anim) {
    var lin = c.linha || 36, pad = { l: c.colRotulo || 120, r: 92, t: c.meta ? 26 : 6, b: 6 };
    var n = c.itens.length, H = pad.t + n * lin + pad.b;
    var mx = c.max || Math.max.apply(null, c.itens.map(function (it) { return it.valor; }));
    var x = function (v) { return pad.l + v / mx * (W - pad.l - pad.r); };
    var svg = el('svg', { width: W, height: H, viewBox: '0 0 ' + W + ' ' + H, role: 'img', 'aria-label': c.titulo || '' }, host);
    c.itens.forEach(function (it, i) {
      var yy = pad.t + i * lin, bh = Math.min(18, lin - 14), by = yy + (lin - bh) / 2;
      var abaixo = c.meta && it.valor < c.meta.valor;
      var g = el('g', {}, svg);
      txt(g, 0, by + bh / 2 + 4, it.rotulo, { class: 'g-rotulo' });
      el('rect', { x: pad.l, y: by, width: W - pad.l - pad.r, height: bh, rx: bh / 2, class: 'g-trilho' }, g);
      var w = Math.max(bh, x(it.valor) - pad.l);
      var b = el('rect', { x: pad.l, y: by, width: w, height: bh, rx: bh / 2, fill: cor(it.cor || c.cor), 'fill-opacity': abaixo ? 0.42 : 1,
        class: 'g-barra' + (anim && !reduz ? ' g-estica' : '') }, g);
      if (anim && !reduz) b.style.animationDelay = (i * 0.07) + 's';
      txt(g, pad.l + w + 10, by + bh / 2 + 4, it.texto || fmt(c.fmt, it.valor), { class: 'g-valor' });
      var alvo = el('rect', { x: 0, y: yy, width: W, height: lin, fill: 'transparent' }, g);
      alvo.addEventListener('pointermove', function (ev) {
        g.classList.add('foco'); svg.classList.add('com-foco');
        dica('<div class="tt">' + it.rotulo + '</div>' + linhaDica(cor(it.cor || c.cor), c.nome || 'Valor', it.texto || fmt(c.fmt, it.valor)) +
          (it.nota ? '<div class="nt">' + it.nota + '</div>' : abaixo ? '<div class="nt">abaixo da ' + c.meta.texto + '</div>' : ''), ev.clientX, ev.clientY);
      });
      alvo.addEventListener('pointerleave', function () { g.classList.remove('foco'); svg.classList.remove('com-foco'); someDica(); });
    });
    if (c.meta) {
      var xm = x(c.meta.valor);
      el('line', { x1: xm, x2: xm, y1: pad.t - 6, y2: H - pad.b, class: 'g-limite', stroke: 'var(--ink)' }, svg).style.opacity = 0.55;
      txt(svg, xm, pad.t - 12, c.meta.texto, { class: 'g-nota', 'text-anchor': 'middle' });
    }
  }

  /* ---------- rosca ---------- */
  function rosca(host, c, W, anim) {
    var S = Math.min(c.tamanho || 190, W), R = S / 2 - 14, esp = c.espessura || 22, C = 2 * Math.PI * R;
    var total = c.itens.reduce(function (a, it) { return a + it.valor; }, 0);
    var svg = el('svg', { width: S, height: S, viewBox: '0 0 ' + S + ' ' + S, role: 'img', 'aria-label': c.titulo || '', class: 'g-rosca' }, host);
    var g = el('g', { transform: 'rotate(-90 ' + S / 2 + ' ' + S / 2 + ')' }, svg);
    el('circle', { cx: S / 2, cy: S / 2, r: R, fill: 'none', 'stroke-width': esp, class: 'g-trilho-r' }, g);
    var acum = 0, folga = c.itens.length > 1 ? 2.5 : 0;
    c.itens.forEach(function (it, i) {
      var L = it.valor / total * C, seg = Math.max(0.5, L - folga);
      var arco = el('circle', { cx: S / 2, cy: S / 2, r: R, fill: 'none', stroke: cor(it.cor || 's' + (i + 1)), 'stroke-width': esp,
        'stroke-dasharray': seg + ' ' + (C - seg), 'stroke-dashoffset': -acum, class: 'g-fatia' }, g);
      if (anim && !reduz) {
        arco.style.strokeDasharray = '0 ' + C;
        setTimeout(function () { arco.style.transition = 'stroke-dasharray .9s cubic-bezier(.3,.7,.2,1)'; arco.style.strokeDasharray = seg + ' ' + (C - seg); }, 60 + i * 90);
      }
      acum += L;
      arco.addEventListener('pointermove', function (ev) {
        svg.classList.add('com-foco'); arco.classList.add('foco');
        dica('<div class="tt">' + it.rotulo + '</div>' + linhaDica(cor(it.cor || 's' + (i + 1)), fmt(c.fmt, it.valor), Math.round(it.valor / total * 100) + '%'), ev.clientX, ev.clientY);
        host.dispatchEvent(new CustomEvent('fatia', { detail: i }));
      });
      arco.addEventListener('pointerleave', function () { svg.classList.remove('com-foco'); arco.classList.remove('foco'); someDica(); host.dispatchEvent(new CustomEvent('fatia', { detail: -1 })); });
    });
    if (c.centro) {
      txt(svg, S / 2, S / 2 - 2, c.centro.valor || fmt(c.fmt, total), { class: 'g-centro', 'text-anchor': 'middle' });
      txt(svg, S / 2, S / 2 + 17, c.centro.texto || 'total', { class: 'g-eixo', 'text-anchor': 'middle' });
    }
  }

  /* ---------- minigráfico (KPI) ---------- */
  function spark(host, c, W, anim) {
    var H = c.altura || 38, n = c.valores.length, lo = Math.min.apply(null, c.valores), hi = Math.max.apply(null, c.valores);
    var x = function (i) { return 3 + i * (W - 6) / (n - 1); };
    var y = function (v) { return 4 + (hi - v) / ((hi - lo) || 1) * (H - 8); };
    var svg = el('svg', { width: W, height: H, viewBox: '0 0 ' + W + ' ' + H, 'aria-hidden': 'true' }, host);
    var p = c.valores.map(function (v, i) { return [x(i), y(v)]; }), d = curva(p), id = 'g' + (++seq);
    var gr = el('linearGradient', { id: id, x1: 0, y1: 0, x2: 0, y2: 1 }, el('defs', {}, svg));
    el('stop', { offset: '0%', 'stop-color': cor(c.cor), 'stop-opacity': 0.28 }, gr);
    el('stop', { offset: '100%', 'stop-color': cor(c.cor), 'stop-opacity': 0 }, gr);
    el('path', { d: d + 'L' + (W - 3) + ',' + H + 'L3,' + H + 'Z', fill: 'url(#' + id + ')' }, svg);
    var l = el('path', { d: d, fill: 'none', stroke: cor(c.cor), 'stroke-width': 2, 'stroke-linecap': 'round' }, svg);
    if (anim) animarTraco(l, 0.2);
    el('circle', { cx: p[n - 1][0], cy: p[n - 1][1], r: 3.5, fill: cor(c.cor), class: 'g-anel' }, svg);
  }

  var TIPOS = { linhas: linhas, colunas: colunas, 'barras-h': barrasH, rosca: rosca, spark: spark };

  function desenhar(host, anim) {
    var c;
    try { c = JSON.parse(host.getAttribute('data-cfg')); } catch (e) { return; }
    var W = Math.floor(host.clientWidth);
    if (!W || W === host._larg) return;
    host._larg = W;
    host.querySelectorAll('svg').forEach(function (s) { s.remove(); });
    TIPOS[host.getAttribute('data-grafico')](host, c, W, anim);
  }

  /* Painel: a lista "Por forma de pagamento" ganha uma rosca com as mesmas fatias */
  function roscaPagamentos() {
    document.querySelectorAll('.formas-lista').forEach(function (lista) {
      if (lista.previousElementSibling && lista.previousElementSibling.classList.contains('nv-grafico')) return;
      var itens = [];
      lista.querySelectorAll('li').forEach(function (li, i) {
        var sp = li.querySelector('.forma-linha span'), b = li.querySelector('.forma-linha b');
        if (!sp || !b) return;
        var v = parseFloat(b.textContent.replace(/[^\d,]/g, '').replace(',', '.')) || 0;
        itens.push({ rotulo: sp.textContent.trim(), valor: v });
        var cs = 'var(--g-s' + (i % 5 + 1) + ')';
        var barra = li.querySelector('.forma-barra span');
        if (barra) barra.style.background = cs;
        var bolinha = document.createElement('i');
        bolinha.className = 'g-bolinha'; bolinha.style.background = cs;
        sp.prepend(bolinha);
      });
      if (!itens.length) return;
      var total = itens.reduce(function (a, it) { return a + it.valor; }, 0);
      var h = document.createElement('div');
      h.className = 'nv-grafico nv-grafico-rosca';
      h.setAttribute('data-grafico', 'rosca');
      h.setAttribute('data-cfg', JSON.stringify({ titulo: 'Vendas por forma de pagamento', itens: itens, centro: { valor: brl(total), texto: 'no período' } }));
      lista.parentNode.insertBefore(h, lista);
      var lis = lista.querySelectorAll('li');
      h.addEventListener('fatia', function (e) {
        lis.forEach(function (li, k) { li.classList.toggle('g-apagado', e.detail >= 0 && k !== e.detail); });
      });
    });
  }

  function iniciar() {
    roscaPagamentos();
    var hosts = document.querySelectorAll('[data-grafico]');
    var vis = 'IntersectionObserver' in window ? new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { vis.unobserve(e.target); desenhar(e.target, true); } });
    }, { threshold: 0.15 }) : null;
    hosts.forEach(function (h) { if (vis) vis.observe(h); else desenhar(h, false); });
    if ('ResizeObserver' in window) {
      var ro = new ResizeObserver(function (es) { es.forEach(function (e) { if (e.target._larg) desenhar(e.target, false); }); });
      hosts.forEach(function (h) { ro.observe(h); });
    }
    window.addEventListener('scroll', someDica, { passive: true });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})();
