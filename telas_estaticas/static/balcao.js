// Vitrine do Balcão — recebe o que o pdv.js manda a cada mudança na venda por dois
// caminhos: o BroadcastChannel("pdv-balcao") (mesmo navegador) e o servidor (venda
// passada em outro aparelho com o mesmo login, ver services/vitrine.py). A tela já nasce
// com o estado atual (renderizado pelo servidor em venda_balcao.html); daqui pra frente
// só atualiza ao vivo pelas mensagens.
(function () {
  var elLista = document.getElementById("listaItens");
  var elVazio = document.getElementById("telaOciosa");
  var elQtd = document.getElementById("qtdItens");
  var elTotal = document.getElementById("totalVenda");
  var elStatus = document.getElementById("statusProcesso");
  var elStatusTexto = document.getElementById("statusTexto");
  var elOverlay = document.getElementById("overlayFim");
  var elOverlayValor = document.getElementById("overlayValor");
  var elPixQr = document.getElementById("pixQrContainer");
  var elUltimoItem = document.getElementById("ultimoItem");
  var elVazioMsg = document.getElementById("vazioMsg");
  var elBoasVindas = document.getElementById("boasVindasMsg");
  var elTotalDetalhe = document.getElementById("totalDetalhe");
  var elSubtotal = document.getElementById("subtotalVenda");
  var elDesconto = document.getElementById("descontoVenda");
  var pixTimer = null;

  // Situação do caixa na tela ociosa: "CAIXA LIVRE" (aberto) x "CAIXA FECHADO".
  // Nasce com o que o servidor renderizou; muda na hora pelo canal (a tela /caixa
  // avisa ao abrir/fechar) e por consulta periódica (pega o fechamento automático).
  function aplicarCaixa(aberto) {
    elVazio.classList.toggle("caixa-fechado", !aberto);
    elVazio.dataset.caixaAberto = aberto ? "sim" : "nao";
    elVazioMsg.textContent = aberto ? "CAIXA LIVRE" : "CAIXA FECHADO";
    if (elBoasVindas) elBoasVindas.hidden = !aberto;
  }

  // Subtotal e desconto acima do total — só quando a venda tem desconto (só o valor,
  // nunca o motivo, que é anotação interna do operador).
  function aplicarDesconto(subtotalTexto, descontoTexto) {
    if (!elTotalDetalhe) return;
    elTotalDetalhe.hidden = !descontoTexto;
    if (descontoTexto) {
      elSubtotal.textContent = subtotalTexto || "";
      elDesconto.textContent = "− " + descontoTexto;
    }
  }

  function consultarCaixa() {
    fetch("/venda/balcao/status", { headers: { "Accept": "application/json" } })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) { if (d && typeof d.caixa_aberto === "boolean") aplicarCaixa(d.caixa_aberto); })
      .catch(function () { /* sem rede: mantém o último estado conhecido */ });
  }

  function esconderPixQr() {
    if (pixTimer) { clearInterval(pixTimer); pixTimer = null; }
    if (elPixQr) { elPixQr.hidden = true; elPixQr.innerHTML = ""; }
  }

  function mostrarPixQr(valor) {
    if (!elPixQr) return;
    var url = "/venda/pix-qrcode" + (valor ? ("?valor=" + encodeURIComponent(valor)) : "");
    fetch(url)
      .then(function (r) { return r.text(); })
      .then(function (html) {
        elPixQr.innerHTML = html;
        elPixQr.hidden = false;
        if (pixTimer) clearInterval(pixTimer);
        var restante = 120;
        var elContador = document.getElementById("pix-qr-contador");
        function atualizarContador() {
          if (!elContador) return;
          var min = Math.floor(restante / 60), seg = restante % 60;
          elContador.textContent = min + ":" + String(seg).padStart(2, "0");
        }
        atualizarContador();
        pixTimer = setInterval(function () {
          restante -= 1;
          if (restante <= 0) {
            clearInterval(pixTimer);
            pixTimer = null;
            elPixQr.innerHTML = '<p class="pix-qr-expirado">QR expirado.</p>';
            return;
          }
          atualizarContador();
        }, 1000);
      });
  }

  function adicionarStatusLinha(texto) {
    var linha = document.createElement("div");
    linha.className = "status-linha";
    linha.textContent = texto;
    elStatusTexto.appendChild(linha);
    elStatus.hidden = false;
    elStatusTexto.scrollTop = elStatusTexto.scrollHeight;
  }

  function adicionarStatusOpcoes(titulo, itens) {
    var bloco = document.createElement("div");
    bloco.className = "status-linha status-opcoes";
    var t = document.createElement("div");
    t.className = "status-opcoes-titulo";
    t.textContent = titulo;
    bloco.appendChild(t);
    var lista = document.createElement("div");
    lista.className = "status-opcoes-lista";
    (itens || []).forEach(function (op) {
      var chip = document.createElement("span");
      chip.textContent = op;
      lista.appendChild(chip);
    });
    bloco.appendChild(lista);
    elStatusTexto.appendChild(bloco);
    elStatus.hidden = false;
    elStatusTexto.scrollTop = elStatusTexto.scrollHeight;
  }

  function renderizarItens(itens) {
    elLista.innerHTML = "";
    itens.forEach(function (item) {
      var linha = document.createElement("div");
      linha.className = "item-linha";
      linha.innerHTML =
        '<span class="nome"></span><span></span><span></span><span class="sub"></span>';
      var spans = linha.querySelectorAll("span");
      spans[0].textContent = item.nome;
      spans[1].textContent = item.qtd;
      spans[2].textContent = item.unit;
      spans[3].textContent = item.subtotal;
      elLista.appendChild(linha);
    });
    elVazio.hidden = itens.length > 0;
    elLista.parentElement.scrollTop = elLista.parentElement.scrollHeight;
    atualizarUltimoItem(itens);
  }

  function atualizarUltimoItem(itens) {
    if (!elUltimoItem) return;
    if (!itens.length) { elUltimoItem.hidden = true; elUltimoItem.innerHTML = ""; return; }
    // Prefere o item marcado como "recém bipado" (pode ser qualquer linha, não
    // só a última) — cai pra última linha só se nada vier marcado (ex.: tela
    // recém aberta, antes de qualquer bipe nesta sessão do canal).
    var item = itens.filter(function (i) { return i.tocado; })[0] || itens[itens.length - 1];
    elUltimoItem.innerHTML =
      '<span class="ultimo-item-rotulo">Último item</span>' +
      '<span class="ultimo-item-nome"></span>' +
      '<span class="ultimo-item-info"></span>';
    var spans = elUltimoItem.querySelectorAll("span");
    spans[1].textContent = item.nome;
    spans[2].textContent = item.qtd + " x " + item.unit + " = " + item.subtotal;
    elUltimoItem.hidden = false;
  }

  function aoReceberMensagem(msg) {
    if (!msg) return;
    if (msg.tipo === "estado") {
      renderizarItens(msg.itens || []);
      elQtd.textContent = (msg.itens || []).length;
      if (msg.totalTexto) elTotal.textContent = msg.totalTexto;
      aplicarDesconto(msg.subtotalTexto, msg.descontoTexto);
    } else if (msg.tipo === "documento") {
      adicionarStatusLinha("Na nota: " + msg.texto);
    } else if (msg.tipo === "forma") {
      adicionarStatusLinha("Forma de pagamento: " + msg.texto);
      if (msg.formaCodigo === "PIX") { mostrarPixQr(msg.valor); } else { esconderPixQr(); }
    } else if (msg.tipo === "status") {
      adicionarStatusLinha(msg.texto);
    } else if (msg.tipo === "opcoes") {
      adicionarStatusOpcoes(msg.titulo, msg.itens);
    } else if (msg.tipo === "limpar_status") {
      elStatus.hidden = true;
      elStatusTexto.innerHTML = "";
      esconderPixQr();
    } else if (msg.tipo === "caixa") {
      aplicarCaixa(!!msg.aberto);
    } else if (msg.tipo === "finalizada") {
      elOverlayValor.textContent = msg.totalTexto || "";
      elOverlay.classList.add("mostrar");
      esconderPixQr();
      setTimeout(function () {
        elOverlay.classList.remove("mostrar");
        renderizarItens([]);
        elQtd.textContent = "0";
        elTotal.textContent = "R$ 0,00";
        elStatus.hidden = true;
        elStatusTexto.innerHTML = "";
      }, 4000);
    }
  }

  // A mesma mensagem pode chegar pelo canal e pelo servidor: aplica só a primeira.
  var vistos = [];
  function receber(msg) {
    if (!msg) return;
    if (msg.id) {
      if (vistos.indexOf(msg.id) !== -1) return;
      vistos.push(msg.id);
      if (vistos.length > 200) vistos.shift();
    }
    aoReceberMensagem(msg);
  }

  if ("BroadcastChannel" in window) {
    var canal = new BroadcastChannel("pdv-balcao");
    canal.addEventListener("message", function (e) { receber(e.data); });
  }

  // Servidor (long-polling): a venda passada em outro aparelho com o mesmo login aparece
  // aqui. Cada pedido volta na hora se já há aviso novo, ou espera até chegar um.
  var geracao = "", desde = null;
  function escutarServidor() {
    var url = "/venda/balcao/eventos?g=" + encodeURIComponent(geracao) + (desde === null ? "" : "&desde=" + desde);
    fetch(url, { headers: { "Accept": "application/json" }, cache: "no-store" })
      .then(function (r) {
        if (r.status === 401) { window.location.href = "/login"; return null; }
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(function (d) {
        if (!d) return;
        geracao = d.g;
        desde = d.seq;
        (d.eventos || []).forEach(receber);
        setTimeout(escutarServidor, 0);
      })
      .catch(function () { setTimeout(escutarServidor, 3000); });  // sem rede: tenta de novo
  }
  escutarServidor();

  function atualizarRelogio() {
    var d = new Date();
    document.getElementById("relogio").textContent =
      String(d.getHours()).padStart(2, "0") + ":" + String(d.getMinutes()).padStart(2, "0");
  }
  atualizarRelogio();
  setInterval(atualizarRelogio, 15000);

  setInterval(consultarCaixa, 20000);
  document.addEventListener("visibilitychange", function () {
    if (!document.hidden) consultarCaixa();
  });
})();
