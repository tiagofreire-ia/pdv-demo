// Modo offline da frente de caixa (US15 — versão mínima).
//
// Se a conexão cair, a venda continua funcionando: catálogo de produtos fica
// espelhado localmente (IndexedDB) enquanto há internet, e vendas feitas sem
// conexão ficam numa fila local até sincronizar. Escopo desta primeira versão:
// só dinheiro, sem cliente/fiado/cashback, sem tela de conflito de estoque.
(function () {
  var DB_NAME = "pdv_offline";
  var DB_VERSION = 1;
  var modoOffline = false;
  var carrinhoOffline = [];
  var ultimoTermoDigitado = "";

  function abrirDB() {
    return new Promise(function (resolve, reject) {
      var req = indexedDB.open(DB_NAME, DB_VERSION);
      req.onupgradeneeded = function () {
        var d = req.result;
        if (!d.objectStoreNames.contains("catalogo")) d.createObjectStore("catalogo", { keyPath: "id" });
        if (!d.objectStoreNames.contains("fila")) d.createObjectStore("fila", { keyPath: "uuid" });
      };
      req.onsuccess = function () { resolve(req.result); };
      req.onerror = function () { reject(req.error); };
    });
  }

  function normalizarTexto(s) {
    return (s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  }

  function salvarCatalogo(produtos) {
    return abrirDB().then(function (d) {
      return new Promise(function (resolve, reject) {
        var tx = d.transaction("catalogo", "readwrite");
        var store = tx.objectStore("catalogo");
        store.clear();
        produtos.forEach(function (p) { store.put(p); });
        tx.oncomplete = resolve;
        tx.onerror = function () { reject(tx.error); };
      });
    });
  }

  function carregarCatalogo() {
    return abrirDB().then(function (d) {
      return new Promise(function (resolve, reject) {
        var req = d.transaction("catalogo", "readonly").objectStore("catalogo").getAll();
        req.onsuccess = function () { resolve(req.result || []); };
        req.onerror = function () { reject(req.error); };
      });
    });
  }

  function filaAdicionar(venda) {
    return abrirDB().then(function (d) {
      return new Promise(function (resolve, reject) {
        var tx = d.transaction("fila", "readwrite");
        tx.objectStore("fila").put(venda);
        tx.oncomplete = resolve;
        tx.onerror = function () { reject(tx.error); };
      });
    });
  }

  function filaListar() {
    return abrirDB().then(function (d) {
      return new Promise(function (resolve, reject) {
        var req = d.transaction("fila", "readonly").objectStore("fila").getAll();
        req.onsuccess = function () { resolve(req.result || []); };
        req.onerror = function () { reject(req.error); };
      });
    });
  }

  function filaRemover(uuid) {
    return abrirDB().then(function (d) {
      return new Promise(function (resolve, reject) {
        var tx = d.transaction("fila", "readwrite");
        tx.objectStore("fila").delete(uuid);
        tx.oncomplete = resolve;
        tx.onerror = function () { reject(tx.error); };
      });
    });
  }

  function gerarUUID() {
    if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
      var r = (Math.random() * 16) | 0, v = c === "x" ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }

  function sincronizarCatalogo() {
    return fetch("/api/produtos/catalogo")
      .then(function (r) { return r.ok ? r.json() : Promise.reject(); })
      .then(salvarCatalogo)
      .catch(function () { /* sem conexão: segue usando o que já está em cache */ });
  }

  function atualizarIndicador() {
    var el = document.getElementById("offline-indicador");
    if (!el) return;
    filaListar().then(function (fila) {
      if (modoOffline) {
        el.hidden = false;
        el.textContent = "⚠ Sem conexão · modo offline (só dinheiro)" +
          (fila.length ? " · " + fila.length + " venda(s) pendente(s)" : "");
      } else if (fila.length) {
        el.hidden = false;
        el.textContent = "🔄 Sincronizando " + fila.length + " venda(s) pendente(s)...";
      } else {
        el.hidden = true;
      }
    });
  }

  function renderCarrinhoOffline() {
    var tbody = document.querySelector("#carrinho table.itens tbody");
    var total = 0;
    var linhas = carrinhoOffline.map(function (it, idx) {
      total += it.total;
      return "<tr><td>" + escaparHtml(it.nome) + "</td><td class='num'>" + it.quantidade +
        "</td><td class='num'>" + formatBRL(it.preco_unitario) + "</td><td class='num'>" +
        formatBRL(it.total) + "</td><td class='num'>" +
        "<button type='button' class='btn danger ghost mini' data-rm-offline='" + idx + "'>✕</button></td></tr>";
    }).join("");
    if (!linhas) linhas = "<tr class='vazio'><td colspan='5'>Nenhum item. Passe o leitor de código de barras.</td></tr>";
    if (tbody) tbody.innerHTML = linhas;
    var elTotal = document.getElementById("total-valor");
    if (elTotal) elTotal.textContent = formatBRL(total);
    return total;
  }

  function ativarModoOffline() {
    if (modoOffline) return;
    modoOffline = true;
    carrinhoOffline = [];
    renderCarrinhoOffline();
    atualizarIndicador();
    mostrarAlerta("Sem conexão · vendas em dinheiro continuam funcionando (offline).", "erro");
  }

  function adicionarItemOffline(termo) {
    termo = (termo || "").trim();
    if (!termo) return;
    return carregarCatalogo().then(function (produtos) {
      var termoNorm = normalizarTexto(termo);
      var prod = produtos.find(function (p) { return p.codigo_barras && p.codigo_barras === termo; }) ||
        produtos.find(function (p) { return normalizarTexto(p.nome).indexOf(termoNorm) !== -1; });
      if (!prod) { mostrarAlerta("Produto não encontrado no catálogo offline.", "erro"); return; }
      var existente = carrinhoOffline.find(function (it) { return it.produto_id === prod.id; });
      if (existente) {
        existente.quantidade += 1;
        existente.total = existente.quantidade * existente.preco_unitario;
      } else {
        carrinhoOffline.push({
          produto_id: prod.id, nome: prod.nome,
          preco_unitario: prod.preco_venda, quantidade: 1, total: prod.preco_venda,
        });
      }
      renderCarrinhoOffline();
    });
  }

  function finalizarOffline(valorRecebido) {
    var total = renderCarrinhoOffline();
    if (!carrinhoOffline.length) { mostrarAlerta("Adicione itens antes de finalizar.", "erro"); return; }
    var venda = {
      uuid: gerarUUID(),
      itens: carrinhoOffline.map(function (it) { return { produto_id: it.produto_id, quantidade: it.quantidade }; }),
      total: total,
      valor_recebido: valorRecebido || 0,
      criado_em: new Date().toISOString(),
    };
    filaAdicionar(venda).then(function () {
      var troco = Math.max(0, (valorRecebido || 0) - total);
      carrinhoOffline = [];
      renderCarrinhoOffline();
      atualizarIndicador();
      mostrarAlerta(
        "Venda registrada offline (R$ " + total.toFixed(2).replace(".", ",") +
        (troco ? " · troco " + formatBRL(troco) : "") + "). Sincroniza quando a conexão voltar.",
        "ok"
      );
      tentarSincronizar();
    });
  }

  function tentarSincronizar() {
    filaListar().then(function (fila) {
      if (!fila.length) return;
      var _meta = document.querySelector('meta[name="csrf-token"]');
      fetch("/venda/sincronizar-offline", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-Token": _meta ? _meta.content : "",
        },
        body: JSON.stringify({ vendas: fila }),
      })
        .then(function (r) { return r.ok ? r.json() : Promise.reject(); })
        .then(function (resultado) {
          var pendentes = [];
          (resultado.resultados || []).forEach(function (res) {
            if (res.status === "ok") pendentes.push(filaRemover(res.uuid));
          });
          Promise.all(pendentes).then(atualizarIndicador);
        })
        .catch(function () { /* ainda sem conexão de verdade; tenta de novo depois */ });
    });
  }

  document.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-rm-offline]");
    if (btn) { carrinhoOffline.splice(parseInt(btn.dataset.rmOffline, 10), 1); renderCarrinhoOffline(); }
  });

  window.addEventListener("online", function () {
    sincronizarCatalogo();
    tentarSincronizar();
  });
  window.addEventListener("offline", ativarModoOffline);

  document.addEventListener("DOMContentLoaded", function () {
    sincronizarCatalogo();
    tentarSincronizar();
    atualizarIndicador();
    setInterval(function () { tentarSincronizar(); atualizarIndicador(); }, 30000);

    var formItem = document.getElementById("form-item");
    var codigo = document.getElementById("codigo");
    if (formItem && codigo) {
      // Guarda o termo digitado ANTES do htmx processar o submit — se a requisição
      // falhar (sendError), o pdv.js já pode ter limpado o campo (htmx:afterRequest).
      formItem.addEventListener("submit", function () { ultimoTermoDigitado = codigo.value.trim(); });
      formItem.addEventListener("htmx:sendError", function () {
        ativarModoOffline();
        adicionarItemOffline(ultimoTermoDigitado);
        codigo.value = "";
        codigo.focus();
      });
    }

    var formPagto = document.getElementById("form-pagto");
    if (formPagto) {
      formPagto.addEventListener("submit", function (e) {
        if (!modoOffline) return;  // fluxo normal (online) segue intacto, sem mudança
        e.preventDefault();
        var forma = document.getElementById("forma").value;
        if (forma !== "DINHEIRO") {
          mostrarAlerta("Offline, só é possível vender em Dinheiro.", "erro");
          return;
        }
        var valor = (typeof lerValor === "function")
          ? (lerValor(document.getElementById("valor_recebido").value) || 0)
          : parseFloat(document.getElementById("valor_recebido").value || 0);
        finalizarOffline(valor);
        if (window._voltarScanningPdv) window._voltarScanningPdv();
      });
    }
  });
})();
