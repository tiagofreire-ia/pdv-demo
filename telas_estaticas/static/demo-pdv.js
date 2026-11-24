// Simulador da Frente de Caixa + Vitrine do Balcão para as telas estáticas (sem servidor).
//
// O PDV de verdade conversa com o servidor (htmx em /venda/item, fetch em /api/produtos,
// /venda/balcao/evento...). Nas telas estáticas não existe servidor, então este arquivo:
//   - responde essas chamadas no próprio navegador (carrinho guardado na sessionStorage);
//   - repassa as mensagens do PDV para a Vitrine (tela do cliente) aberta em outra janela,
//     via localStorage — funciona mesmo onde o BroadcastChannel não chega (ex.: file://).
// Carregado ANTES do pdv.js / balcao.js.
(function () {
  "use strict";

  var CATALOGO = [
    {
    "id": 9,
    "nome": "Amstel Lata 473ml (Latão)",
    "codigo_barras": "7896045506049",
    "preco": 5.5,
    "estoque": 96,
    "unidade": "UN"
    },
    {
    "id": 33,
    "nome": "Aperitivo Campari Bitter 900ml",
    "codigo_barras": "8000040000109",
    "preco": 64.9,
    "estoque": 10,
    "unidade": "UN"
    },
    {
    "id": 3,
    "nome": "Brahma Duplo Malte Lata 350ml",
    "codigo_barras": "7891149101993",
    "preco": 4.5,
    "estoque": 84,
    "unidade": "UN"
    },
    {
    "id": 29,
    "nome": "Cachaça Artesanal Salinas 670ml",
    "codigo_barras": "7898115420013",
    "preco": 54.9,
    "estoque": 8,
    "unidade": "UN"
    },
    {
    "id": 8,
    "nome": "Cerveja Original 600ml",
    "codigo_barras": "7891149105502",
    "preco": 11.9,
    "estoque": 48,
    "unidade": "UN"
    },
    {
    "id": 19,
    "nome": "Coca-Cola Lata 350ml",
    "codigo_barras": "7894900010015",
    "preco": 4.5,
    "estoque": 72,
    "unidade": "UN"
    },
    {
    "id": 17,
    "nome": "Coca-Cola Original PET 2L",
    "codigo_barras": "7894900011517",
    "preco": 11.9,
    "estoque": 45,
    "unidade": "UN"
    },
    {
    "id": 18,
    "nome": "Coca-Cola Sem Açúcar PET 2L",
    "codigo_barras": "7894900700046",
    "preco": 11.9,
    "estoque": 28,
    "unidade": "UN"
    },
    {
    "id": 7,
    "nome": "Corona Extra Long Neck 330ml",
    "codigo_barras": "7501064191350",
    "preco": 8.5,
    "estoque": 42,
    "unidade": "UN"
    },
    {
    "id": 16,
    "nome": "Energético Bally Tropical 2L",
    "codigo_barras": "7898357410015",
    "preco": 14.9,
    "estoque": 22,
    "unidade": "UN"
    },
    {
    "id": 2,
    "nome": "Fardo Heineken Lata 350ml c/ 12 un",
    "codigo_barras": "78936690",
    "preco": 69.9,
    "estoque": 18,
    "unidade": "UN"
    },
    {
    "id": 10,
    "nome": "Fardo Skol Pilsen Lata 350ml c/ 12 un",
    "codigo_barras": "7891991010023",
    "preco": 44.9,
    "estoque": 20,
    "unidade": "UN"
    },
    {
    "id": 6,
    "nome": "Fardo Spaten Lata 350ml c/ 12 un",
    "codigo_barras": "7891149210992",
    "preco": 56.9,
    "estoque": 11,
    "unidade": "UN"
    },
    {
    "id": 12,
    "nome": "Gelo de Água de Coco p/ Drink 200ml",
    "codigo_barras": "7898901234028",
    "preco": 4.5,
    "estoque": 55,
    "unidade": "UN"
    },
    {
    "id": 26,
    "nome": "Gin Tanqueray London Dry 750ml",
    "codigo_barras": "5000289111027",
    "preco": 119.9,
    "estoque": 9,
    "unidade": "UN"
    },
    {
    "id": 20,
    "nome": "Guaraná Antarctica PET 2L",
    "codigo_barras": "7891991000833",
    "preco": 9.9,
    "estoque": 32,
    "unidade": "UN"
    },
    {
    "id": 31,
    "nome": "Licor 43 Diego Zamora Espanhol 700ml",
    "codigo_barras": "8410013991009",
    "preco": 159.9,
    "estoque": 8,
    "unidade": "UN"
    },
    {
    "id": 15,
    "nome": "Monster Energy Green Lata 473ml",
    "codigo_barras": "070847811169",
    "preco": 11.5,
    "estoque": 34,
    "unidade": "UN"
    },
    {
    "id": 5,
    "nome": "Spaten Puro Malte Lata 350ml",
    "codigo_barras": "7891149210114",
    "preco": 5.2,
    "estoque": 62,
    "unidade": "UN"
    },
    {
    "id": 32,
    "nome": "Tequila José Cuervo Especial Gold 750ml",
    "codigo_barras": "7501035010109",
    "preco": 134.9,
    "estoque": 7,
    "unidade": "UN"
    },
    {
    "id": 30,
    "nome": "Vinho Chileno Reservado Cabernet 750ml",
    "codigo_barras": "7804320985619",
    "preco": 39.9,
    "estoque": 16,
    "unidade": "UN"
    },
    {
    "id": 27,
    "nome": "Vodka Absolut Original 1L",
    "codigo_barras": "7312040017072",
    "preco": 89.9,
    "estoque": 12,
    "unidade": "UN"
    },
    {
    "id": 28,
    "nome": "Vodka Smirnoff Red 998ml",
    "codigo_barras": "7896002100129",
    "preco": 46.9,
    "estoque": 19,
    "unidade": "UN"
    },
    {
    "id": 25,
    "nome": "Whisky Ballantine's Finest 1L",
    "codigo_barras": "5010106113127",
    "preco": 94.9,
    "estoque": 10,
    "unidade": "UN"
    },
    {
    "id": 24,
    "nome": "Whisky Johnnie Walker Red Label 1L",
    "codigo_barras": "5000267014005",
    "preco": 109.9,
    "estoque": 14,
    "unidade": "UN"
    },
    {
    "id": 23,
    "nome": "Água Mineral Cristal com Gás 500ml",
    "codigo_barras": "7891910000198",
    "preco": 3.5,
    "estoque": 64,
    "unidade": "UN"
    },
    {
    "id": 22,
    "nome": "Água Mineral Cristal sem Gás 500ml",
    "codigo_barras": "7891910000197",
    "preco": 3.0,
    "estoque": 110,
    "unidade": "UN"
    },
    {
    "id": 21,
    "nome": "Água Tônica Antarctica Lata 350ml",
    "codigo_barras": "7891991002110",
    "preco": 4.8,
    "estoque": 40,
    "unidade": "UN"
    }
    ];

  var CHAVE_CARRINHO = "demoPdvCarrinho_v1";
  var CHAVE_EVENTO = "demoPdvBalcaoEvento_v1";
  var CHAVE_ESTADO = "demoPdvBalcaoEstado_v1";
  var CHAVE_VENDAS = "demoPdvVendas_v1";

  var ehVitrine = !!document.getElementById("overlayFim");

  // ---------------------------------------------------------------- utilidades
  function brl(v) {
    return "R$ " + Number(v || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
  function esc(t) {
    return String(t == null ? "" : t).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function num(txt) {
    var t = String(txt == null ? "" : txt).replace(/[^0-9,.\-]/g, "");
    if (!t) return null;
    if (t.indexOf(",") !== -1) t = t.replace(/\./g, "").replace(",", ".");
    var n = parseFloat(t);
    return isNaN(n) ? null : n;
  }
  function norm(s) {
    return String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  }
  function lerJSON(armazem, chave, padrao) {
    try { var v = armazem.getItem(chave); return v ? JSON.parse(v) : padrao; } catch (e) { return padrao; }
  }
  function gravar(armazem, chave, valor) {
    try { armazem.setItem(chave, typeof valor === "string" ? valor : JSON.stringify(valor)); } catch (e) { /* modo privado */ }
  }
  function caminho(url) {
    var u = String(url || "");
    try { u = new URL(u, location.href).pathname + (new URL(u, location.href).search || ""); } catch (e) { /* mantém */ }
    return u;
  }
  function parametros(url, corpo) {
    var p = new URLSearchParams();
    var q = String(url).split("?")[1];
    if (q) new URLSearchParams(q).forEach(function (v, k) { p.append(k, v); });
    if (corpo) {
      if (typeof corpo === "string") new URLSearchParams(corpo).forEach(function (v, k) { p.append(k, v); });
      else if (typeof FormData !== "undefined" && corpo instanceof FormData) corpo.forEach(function (v, k) { p.append(k, v); });
      else if (corpo instanceof URLSearchParams) corpo.forEach(function (v, k) { p.append(k, v); });
    }
    return p;
  }
  function respostaJSON(dados, status) {
    return Promise.resolve(new Response(JSON.stringify(dados), {
      status: status || 200, headers: { "Content-Type": "application/json" },
    }));
  }
  function respostaHTML(html) {
    return Promise.resolve(new Response(html, { status: 200, headers: { "Content-Type": "text/html; charset=utf-8" } }));
  }

  // QR "de mentira" (padrão visual de QR, gerado do valor) — só para a demonstração.
  function htmlPixQr(valor) {
    var n = 29, cel = 8, semente = 0, s = String(valor || "0") + "SUAMARCA";
    for (var i = 0; i < s.length; i++) semente = (semente * 31 + s.charCodeAt(i)) >>> 0;
    function rnd() { semente = (semente * 1103515245 + 12345) >>> 0; return (semente >>> 16) & 1; }
    function finder(x, y) {
      return '<rect x="' + x * cel + '" y="' + y * cel + '" width="' + 7 * cel + '" height="' + 7 * cel + '" fill="#000"/>' +
        '<rect x="' + (x + 1) * cel + '" y="' + (y + 1) * cel + '" width="' + 5 * cel + '" height="' + 5 * cel + '" fill="#fff"/>' +
        '<rect x="' + (x + 2) * cel + '" y="' + (y + 2) * cel + '" width="' + 3 * cel + '" height="' + 3 * cel + '" fill="#000"/>';
    }
    function emFinder(x, y) { return (x < 8 && y < 8) || (x > n - 9 && y < 8) || (x < 8 && y > n - 9); }
    var modulos = "";
    for (var y = 0; y < n; y++) for (var x = 0; x < n; x++) {
      if (!emFinder(x, y) && rnd()) modulos += '<rect x="' + x * cel + '" y="' + y * cel + '" width="' + cel + '" height="' + cel + '"/>';
    }
    var lado = n * cel;
    var svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + lado + " " + lado + '" shape-rendering="crispEdges">' +
      '<rect width="' + lado + '" height="' + lado + '" fill="#fff"/><g fill="#000">' + modulos + "</g>" +
      finder(0, 0) + finder(n - 7, 0) + finder(0, n - 7) + "</svg>";
    var v = num(valor);
    var copia = "00020126580014BR.GOV.BCB.PIX0136demo-suamarca-pix5204000053039865406" +
      (v || 0).toFixed(2) + "5802BR5909SUA MARCA6009SAO PAULO6304DEMO";
    return '<div class="pix-qr-svg">' + svg + "</div>" +
      '<div class="pix-qr-valor">' + (v ? brl(v) : "Pix") + "</div>" +
      '<div class="pix-qr-contador">Expira em <span id="pix-qr-contador">2:00</span></div>' +
      '<div class="pix-qr-copia"><code>' + esc(copia) + "</code></div>";
  }

  // ======================================================================== VITRINE
  if (ehVitrine) {
    // Fila de mensagens que chegam do PDV (outra janela) pelo localStorage. O balcao.js
    // busca /venda/balcao/eventos em long-polling: respondemos daqui com essa fila.
    var fila = [], seq = 0, espera = null;
    function entregar() {
      if (!espera || !fila.length) return;
      var r = espera; espera = null;
      clearTimeout(r.t);
      var evs = fila; fila = [];
      r.resolve({ g: "demo", seq: seq, eventos: evs });
    }
    window.addEventListener("storage", function (e) {
      if (e.key !== CHAVE_EVENTO || !e.newValue) return;
      try { fila.push(JSON.parse(e.newValue)); seq += 1; entregar(); } catch (err) { /* ignora */ }
    });

    var fetchOriginalV = window.fetch ? window.fetch.bind(window) : null;
    window.fetch = function (url, opts) {
      var p = caminho(url);
      if (p.indexOf("/venda/balcao/eventos") !== -1) {
        if (p.indexOf("desde=") === -1) {
          // Primeira chamada: a tela já nasce com a venda em andamento no PDV.
          var inicial = lerJSON(localStorage, CHAVE_ESTADO, null);
          return respostaJSON({ g: "demo", seq: seq, eventos: inicial ? [inicial] : [] });
        }
        return new Promise(function (resolve) {
          espera = { resolve: function (d) { resolve(new Response(JSON.stringify(d), { status: 200, headers: { "Content-Type": "application/json" } })); } };
          espera.t = setTimeout(function () {
            if (espera) { var r = espera; espera = null; r.resolve({ g: "demo", seq: seq, eventos: [] }); }
          }, 25000);
          entregar();
        });
      }
      if (p.indexOf("/venda/balcao/status") !== -1) {
        var caixa = lerJSON(localStorage, "demoCaixaAberto_v1", true);
        return respostaJSON({ caixa_aberto: caixa !== false });
      }
      if (p.indexOf("/venda/pix-qrcode") !== -1) {
        return respostaHTML(htmlPixQr(parametros(p).get("valor")));
      }
      return fetchOriginalV ? fetchOriginalV(url, opts) : Promise.reject(new Error("sem fetch"));
    };
    return;
  }

  // ======================================================================== PDV
  var carrinho = lerJSON(sessionStorage, CHAVE_CARRINHO, null) || { itens: [], desconto: 0, cliente: "" };
  var tocadoId = null;

  function salvarCarrinho() { gravar(sessionStorage, CHAVE_CARRINHO, carrinho); }
  function subtotal() {
    return carrinho.itens.reduce(function (s, it) { return s + it.preco * it.qtd; }, 0);
  }
  function total() { return Math.max(0, Math.round((subtotal() - (carrinho.desconto || 0)) * 100) / 100); }
  function produtoPorId(id) {
    id = parseInt(id, 10);
    return CATALOGO.filter(function (p) { return p.id === id; })[0] || null;
  }
  function acharProduto(termo) {
    var t = String(termo || "").trim();
    if (!t) return null;
    var porCodigo = CATALOGO.filter(function (p) { return p.codigo_barras === t; })[0];
    if (porCodigo) return porCodigo;
    var n = norm(t);
    return CATALOGO.filter(function (p) { return norm(p.nome).indexOf(n) !== -1; })[0] || null;
  }
  function qtdTexto(q) {
    return Number(q).toLocaleString("pt-BR", { maximumFractionDigits: 3 });
  }

  function htmlCarrinho() {
    var linhas = carrinho.itens.map(function (it) {
      return '<tr id="item-' + it.id + '" data-item-id="' + it.id + '"' + (it.id === tocadoId ? " data-recem-bipado" : "") + ">" +
        "<td>" + esc(it.nome) + "</td>" +
        '<td class="num">' + qtdTexto(it.qtd) + "</td>" +
        '<td class="num">' + brl(it.preco) + "</td>" +
        '<td class="num">' + brl(it.preco * it.qtd) + "</td>" +
        '<td class="num"><button type="button" class="btn-remover" title="Remover" aria-label="Remover ' + esc(it.nome) + '"' +
        ' hx-post="/venda/item/' + it.id + '/remover" hx-target="#carrinho" hx-swap="innerHTML">✕</button></td></tr>';
    }).join("");
    if (!linhas) linhas = '<tr class="vazio"><td colspan="5">Nenhum item. Passe o leitor de código de barras.</td></tr>';

    var sub = subtotal(), desc = carrinho.desconto || 0, tot = total();
    var qtdItens = carrinho.itens.reduce(function (s, it) { return s + it.qtd; }, 0);
    var nProd = carrinho.itens.length;

    return '<table class="itens"><thead><tr><th>Produto</th><th class="num">Qtd</th><th class="num">Unit.</th>' +
      '<th class="num">Total</th><th></th></tr></thead><tbody>' + linhas + "</tbody></table>" +
      // Fora do #carrinho (out-of-band), como o servidor faz:
      '<div class="total-valor" id="total-valor" hx-swap-oob="true">' + brl(tot) + "</div>" +
      '<div id="totais-detalhe" class="totais-detalhe" hx-swap-oob="true" data-base="' + sub.toFixed(2) + '"' +
      ' data-desconto="' + desc.toFixed(2) + '" data-subtotal="' + sub.toFixed(2) + '" data-desconto-total="' + desc.toFixed(2) + '">' +
      '<div class="totais-linha"><span>Subtotal <b>' + brl(sub) + '</b></span><span class="totais-sep">·</span>' +
      '<span class="totais-desconto">Desconto <b>' + brl(desc) + "</b></span></div>" +
      (desc > 0 ? '<button type="button" class="btn ghost mini" hx-post="/venda/desconto/remover" hx-target="#carrinho" hx-swap="innerHTML">Tirar desconto</button>' : "") +
      "</div>" +
      '<span id="carrinho-contagem" class="carrinho-contagem" hx-swap-oob="true">' + nProd + " produto" + (nProd === 1 ? "" : "s") +
      " · " + qtdTexto(qtdItens) + " ite" + (qtdItens === 1 ? "m" : "ns") + "</span>";
  }

  // Cada rota devolve { html, gatilho } — gatilho vira o cabeçalho HX-Trigger.
  function rotear(metodo, url, corpo) {
    var p = caminho(url).split("?")[0];
    var prm = parametros(url, corpo);
    var m;
    tocadoId = null;

    if (p.slice(-11) === "/venda/item") {
      var prod = prm.get("produto_id") ? produtoPorId(prm.get("produto_id")) : acharProduto(prm.get("codigo"));
      if (!prod) return { html: htmlCarrinho(), gatilho: { produtoNaoEncontrado: true } };
      var q = num(prm.get("quantidade"));
      if (q === null || q <= 0 || q > 9999) return { html: htmlCarrinho(), gatilho: { quantidadeInvalida: { motivo: "faixa" } } };
      var ex = carrinho.itens.filter(function (it) { return it.id === prod.id; })[0];
      if (ex) ex.qtd += q;
      else carrinho.itens.push({ id: prod.id, nome: prod.nome, preco: prod.preco, qtd: q });
      tocadoId = prod.id;
      carrinho.desconto = 0;
    } else if ((m = p.match(/\/venda\/item\/(\d+)\/quantidade$/))) {
      var id = parseInt(m[1], 10), delta = num(prm.get("delta")) || 0;
      carrinho.itens = carrinho.itens.filter(function (it) {
        if (it.id !== id) return true;
        it.qtd += delta;
        return it.qtd > 0;
      });
      tocadoId = id;
      carrinho.desconto = 0;
    } else if ((m = p.match(/\/venda\/item\/(\d+)\/remover$/))) {
      var idr = parseInt(m[1], 10);
      carrinho.itens = carrinho.itens.filter(function (it) { return it.id !== idr; });
      carrinho.desconto = 0;
    } else if (/\/venda\/desconto\/remover$/.test(p)) {
      carrinho.desconto = 0;
    } else if (/\/venda\/desconto$/.test(p)) {
      var base = subtotal(), v = num(prm.get("valor"));
      var d = prm.get("modo") === "valor" ? v : base - (v === null ? base : v);
      d = Math.round((d || 0) * 100) / 100;
      if (!(d > 0 && d < base)) return { html: htmlCarrinho(), gatilho: { descontoRecusado: { mensagem: "Valor de desconto inválido." } } };
      if (d > 1 && !prm.get("senha")) return { html: htmlCarrinho(), gatilho: { descontoRecusado: { mensagem: "Digite a senha para liberar este desconto (na demonstração, qualquer senha serve)." } } };
      carrinho.desconto = d;
      salvarCarrinho();
      return { html: htmlCarrinho(), gatilho: { descontoAplicado: true } };
    } else if (/\/venda\/cliente$/.test(p)) {
      carrinho.cliente = prm.get("cliente_id") || "";
    } else if (/\/venda\/repetir$/.test(p)) {
      var ultima = lerJSON(localStorage, CHAVE_VENDAS, [])[0];
      var itens = ultima ? ultima.itens : [{ id: 3, qtd: 12 }, { id: 19, qtd: 2 }];
      carrinho.itens = [];
      itens.forEach(function (it) {
        var pr = produtoPorId(it.id);
        if (pr) carrinho.itens.push({ id: pr.id, nome: pr.nome, preco: pr.preco, qtd: it.qtd });
      });
      carrinho.desconto = 0;
    } else if (/\/venda\/demo-limpar$/.test(p)) {
      carrinho = { itens: [], desconto: 0, cliente: "" };
    } else {
      return null;
    }
    salvarCarrinho();
    return { html: htmlCarrinho(), gatilho: null };
  }

  // ---------------------------------------------------------------- XHR falso (htmx)
  var xOpen = XMLHttpRequest.prototype.open;
  var xSend = XMLHttpRequest.prototype.send;
  var xHeader = XMLHttpRequest.prototype.setRequestHeader;
  function ehRotaDemo(url) {
    var p = caminho(url).split("?")[0];
    return /\/venda\/(item|desconto|cliente|repetir|demo-limpar)(\/|$)/.test(p);
  }
  XMLHttpRequest.prototype.open = function (metodo, url) {
    if (ehRotaDemo(url)) { this._demo = { metodo: metodo, url: String(url) }; return; }
    this._demo = null;
    return xOpen.apply(this, arguments);
  };
  XMLHttpRequest.prototype.setRequestHeader = function () {
    if (this._demo) return;
    return xHeader.apply(this, arguments);
  };
  XMLHttpRequest.prototype.send = function (corpo) {
    if (!this._demo) return xSend.apply(this, arguments);
    var xhr = this, req = this._demo;
    setTimeout(function () {
      var r = rotear(req.metodo, req.url, corpo) || { html: "", gatilho: null };
      var cabecalhos = { "content-type": "text/html; charset=utf-8" };
      if (r.gatilho) cabecalhos["hx-trigger"] = JSON.stringify(r.gatilho);
      var def = function (k, v) { Object.defineProperty(xhr, k, { value: v, configurable: true }); };
      def("readyState", 4);
      def("status", 200);
      def("statusText", "OK");
      def("responseText", r.html);
      def("response", r.html);
      def("responseURL", new URL(req.url, location.href).href);
      def("getResponseHeader", function (n) { var v = cabecalhos[String(n).toLowerCase()]; return v === undefined ? null : v; });
      def("getAllResponseHeaders", function () {
        return Object.keys(cabecalhos).map(function (k) { return k + ": " + cabecalhos[k]; }).join("\r\n") + "\r\n";
      });
      if (typeof xhr.onload === "function") xhr.onload(new ProgressEvent("load"));
      try { xhr.dispatchEvent(new ProgressEvent("loadend")); } catch (e) { /* ok */ }
    }, 40);
  };

  // ---------------------------------------------------------------- fetch falso
  var fetchOriginal = window.fetch ? window.fetch.bind(window) : null;
  window.fetch = function (url, opts) {
    var p = caminho(url);
    if (p.indexOf("/api/produtos/catalogo") !== -1) return respostaJSON(CATALOGO);
    if (p.indexOf("/api/produtos") !== -1) {
      var q = norm(parametros(p).get("q"));
      var lista = CATALOGO.filter(function (pr) {
        return norm(pr.nome).indexOf(q) !== -1 || (pr.codigo_barras || "").indexOf(q) === 0;
      }).slice(0, 8);
      return respostaJSON(lista);
    }
    if (p.indexOf("/venda/pix-qrcode") !== -1) return respostaHTML(htmlPixQr(parametros(p).get("valor")));
    if (p.indexOf("/venda/balcao/evento") !== -1) {
      // Repassa a mensagem para a Vitrine aberta em outra janela.
      var corpo = opts && typeof opts.body === "string" ? opts.body : "";
      if (corpo) {
        gravar(localStorage, CHAVE_EVENTO, corpo);
        try { if (JSON.parse(corpo).tipo === "estado") gravar(localStorage, CHAVE_ESTADO, corpo); } catch (e) { /* ok */ }
      }
      return respostaJSON({ ok: true });
    }
    if (p.indexOf("/venda/sincronizar-offline") !== -1) return respostaJSON({ resultados: [] });
    return fetchOriginal ? fetchOriginal(url, opts) : Promise.reject(new Error("sem fetch"));
  };

  // ---------------------------------------------------------------- formulários
  function limparCarrinho() {
    carrinho = { itens: [], desconto: 0, cliente: "" };
    salvarCarrinho();
    if (typeof htmx !== "undefined") {
      return htmx.ajax("POST", "/venda/demo-limpar", { target: "#carrinho", swap: "innerHTML" }).then(function () {
        var btnC = document.getElementById("btn-cancelar-venda");
        if (btnC) btnC.disabled = true;
        var cod = document.getElementById("codigo");
        if (cod) { delete cod.dataset.ultimo; cod.value = ""; }
        if (typeof avisarBalcaoEstadoCarrinho === "function") avisarBalcaoEstadoCarrinho();
      });
    }
    return Promise.resolve();
  }

  var LABEL_FORMA = {
    DINHEIRO: "Dinheiro", PIX: "Pix", FIADO: "Confiança",
    CIELO_DEBITO: "Cielo · Débito", CIELO_CREDITO: "Cielo · Crédito",
    STONE_DEBITO: "Stone · Débito", STONE_CREDITO: "Stone · Crédito",
    CIELO_CREDITO_PARCELADO: "Cielo · Crédito parcelado", STONE_CREDITO_PARCELADO: "Stone · Crédito parcelado",
    COMBINADO: "Combinado",
  };

  function alerta(msg, tipo) {
    if (typeof mostrarAlerta === "function") mostrarAlerta(msg, tipo);
  }

  function somarNaGaveta(valor) {
    var el = null;
    document.querySelectorAll("#caixa-status .caixa-valores > span").forEach(function (s) {
      if (/gaveta/i.test(s.textContent)) el = s.querySelector("strong");
    });
    if (!el || !valor) return;
    var atual = num(el.textContent) || 0;
    el.textContent = brl(atual + valor);
  }

  function finalizarVenda(form) {
    if (!carrinho.itens.length) { alerta("Adicione itens antes de finalizar.", "erro"); return; }
    var forma = (form.querySelector("#forma") || {}).value || "";
    var pagamentos = (form.querySelector("#pagamentos_json") || {}).value || "";
    if (!forma && !pagamentos) { alerta("Escolha a forma de pagamento.", "erro"); return; }
    if (forma === "FIADO" && !carrinho.cliente) {
      var sel = document.getElementById("cliente_id");
      if (!sel || !sel.value) { alerta("Venda na Confiança exige selecionar um cliente cadastrado.", "erro"); return; }
    }
    var tot = total();
    var recebido = num((form.querySelector("#valor_recebido") || {}).value);
    var troco = forma === "DINHEIRO" && recebido !== null ? Math.max(0, recebido - tot) : 0;

    var vendas = lerJSON(localStorage, CHAVE_VENDAS, []);
    var numero = 1873 + vendas.length;
    vendas.unshift({ numero: numero, total: tot, forma: forma, itens: carrinho.itens.map(function (it) { return { id: it.id, qtd: it.qtd }; }) });
    gravar(localStorage, CHAVE_VENDAS, vendas.slice(0, 20));

    var totalTexto = brl(tot);
    if (typeof avisarBalcao === "function") avisarBalcao({ tipo: "finalizada", totalTexto: totalTexto });
    if (forma === "DINHEIRO") somarNaGaveta(tot);

    limparCarrinho().then(function () {
      if (window._voltarScanningPdv) window._voltarScanningPdv();
      var btnF = document.getElementById("btn-finalizar");
      if (btnF) btnF.disabled = false;
      var sel = document.getElementById("cliente_id");
      if (sel) sel.value = "";
      mostrarModalImprimir("Venda nº " + numero + " · " + totalTexto + " · " +
        (pagamentos ? "Pagamento combinado" : (LABEL_FORMA[forma] || forma)) +
        (troco > 0.004 ? " · Troco: " + brl(troco) : ""));
    });
  }

  function mostrarModalImprimir(msg) {
    var modal = document.getElementById("modal-imprimir");
    if (!modal) { alerta(msg, "ok"); return; }
    document.getElementById("modal-imprimir-msg").textContent = msg;
    modal.hidden = false;
    function fechar(imprimir) {
      modal.hidden = true;
      document.removeEventListener("keydown", teclas, true);
      btnSim.removeEventListener("click", sim);
      btnNao.removeEventListener("click", nao);
      alerta(imprimir ? "Comprovante enviado para a impressora (demonstração)." : "Venda registrada. Pronto para a próxima!", "ok");
      var cod = document.getElementById("codigo");
      if (cod) cod.focus();
    }
    function sim() { fechar(true); }
    function nao() { fechar(false); }
    function teclas(e) {
      if (e.key === "Enter") { e.preventDefault(); e.stopPropagation(); sim(); }
      else if (e.key === "Escape") { e.preventDefault(); e.stopPropagation(); nao(); }
    }
    var btnSim = document.getElementById("btn-sim-imprimir");
    var btnNao = document.getElementById("btn-nao-imprimir");
    btnSim.addEventListener("click", sim);
    btnNao.addEventListener("click", nao);
    document.addEventListener("keydown", teclas, true);
    btnSim.focus();
  }

  // Bolha (não captura): o confirmar.js e o pdv.js tratam o envio primeiro.
  document.addEventListener("submit", function (e) {
    var f = e.target;
    if (!f || !f.getAttribute) return;
    var acao = f.getAttribute("action") || "";
    if (acao.indexOf("/venda/cancelar") !== -1) {
      if (e.defaultPrevented) return;  // aguardando a confirmação
      e.preventDefault();
      limparCarrinho().then(function () {
        if (window._voltarScanningPdv) window._voltarScanningPdv();
        alerta("Venda cancelada.", "ok");
      });
    } else if (acao.indexOf("/venda/finalizar") !== -1) {
      e.preventDefault();
      finalizarVenda(f);
    }
  });

  // Recarregou a página com itens na sacola: mostra o carrinho salvo.
  document.addEventListener("DOMContentLoaded", function () {
    if (!carrinho.itens.length || typeof htmx === "undefined") return;
    htmx.ajax("POST", "/venda/cliente", { target: "#carrinho", swap: "innerHTML", values: { cliente_id: carrinho.cliente || "" } })
      .then(function () {
        var btnC = document.getElementById("btn-cancelar-venda");
        if (btnC) btnC.disabled = false;
        if (typeof avisarBalcaoEstadoCarrinho === "function") avisarBalcaoEstadoCarrinho();
      });
  });
})();
