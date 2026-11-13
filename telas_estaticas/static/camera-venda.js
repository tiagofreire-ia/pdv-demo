// Câmera do celular na frente de caixa (spec 020, pedido do dono em 08/10): lê o código, mostra o produto
// numa gaveta de baixo com a quantidade (− 1 +) e lança na sacola pelo mesmo /venda/item do leitor USB —
// todas as regras (estoque, quantidade inteira, caixa fechado) continuam no servidor.
(function () {
  var btnAbrir = document.getElementById("btn-camera-venda");
  var tela = document.getElementById("camera-venda");
  if (!btnAbrir || !tela || !window.LeitorCamera) return;

  var $ = function (id) { return document.getElementById(id); };
  var video = $("camera-venda-video"), dica = $("cv-dica"), aviso = $("cv-aviso"), gaveta = $("cv-gaveta");
  var elNome = $("cv-nome"), elPreco = $("cv-preco"), elEstoque = $("cv-estoque"), elErro = $("cv-erro");
  var qtd = $("cv-quantidade"), btnAdicionar = $("cv-adicionar"), elTotal = $("cv-total");
  var REPETIDA_MS = 2000;  // a câmera ainda vê a mesma embalagem logo depois de adicionar
  var produto = null;
  var ultimo = { codigo: null, quando: 0 };

  var leitor = window.LeitorCamera(video, {
    aoLer: lido,
    aoAvisar: function (texto) { dica.hidden = false; dica.textContent = texto; },
  });

  function brl(v) { return Number(v || 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" }); }
  function numero(v) { return Number(v || 0).toLocaleString("pt-BR", { maximumFractionDigits: 3 }); }
  function atualizarTotal() {
    var total = document.getElementById("total-valor");
    if (total) elTotal.textContent = total.textContent.trim();
  }

  function bipe() {
    try {
      var Ctx = window.AudioContext || window.webkitAudioContext;
      var ctx = new Ctx(), osc = ctx.createOscillator(), vol = ctx.createGain();
      osc.frequency.value = 1800;
      vol.gain.value = 0.08;
      osc.connect(vol); vol.connect(ctx.destination);
      osc.start(); osc.stop(ctx.currentTime + 0.09);
      setTimeout(function () { ctx.close(); }, 300);
    } catch (e) {}
  }

  function avisoCurto(texto, tipo) {
    aviso.textContent = texto;
    aviso.className = "cv-aviso" + (tipo ? " " + tipo : "");
    aviso.hidden = false;
    clearTimeout(aviso._t);
    aviso._t = setTimeout(function () { aviso.hidden = true; }, 2400);
  }

  function abrir() {
    if (btnAbrir.disabled) return;
    tela.hidden = false;
    document.body.classList.add("camera-venda-aberta");
    fecharGaveta();
    atualizarTotal();
    dica.textContent = "Aponte para o código de barras";
    leitor.iniciar();
  }

  function fechar() {
    leitor.parar();
    fecharGaveta();
    tela.hidden = true;
    document.body.classList.remove("camera-venda-aberta");
    var codigo = document.getElementById("codigo");
    if (codigo && !codigo.disabled && window.matchMedia("(pointer: fine)").matches) codigo.focus();
  }

  function lido(codigo) {
    if (codigo === ultimo.codigo && Date.now() - ultimo.quando < REPETIDA_MS) { leitor.retomar(); return; }
    bipe();
    leitor.pausar();
    fetch("/venda/produto-por-codigo?codigo=" + encodeURIComponent(codigo), { credentials: "same-origin" })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (d.erro || !d.encontrado) {
          avisoCurto(d.erro || ("Produto não encontrado (" + codigo + ")."), "erro");
          ultimo = { codigo: codigo, quando: Date.now() };
          leitor.retomar();
          return;
        }
        produto = d;
        produto.codigo = codigo;
        mostrarGaveta();
      })
      .catch(function () { avisoCurto("Sem conexão com o sistema. Tente de novo.", "erro"); leitor.retomar(); });
  }

  function mostrarGaveta() {
    elNome.textContent = produto.nome;
    elPreco.textContent = brl(produto.preco);
    elEstoque.textContent = "Estoque: " + numero(produto.estoque);
    elErro.hidden = true;
    qtd.value = "1";
    qtd.inputMode = produto.inteiro ? "numeric" : "decimal";
    btnAdicionar.disabled = false;
    dica.hidden = true;
    gaveta.hidden = false;
  }

  function fecharGaveta() {
    gaveta.hidden = true;
    dica.hidden = false;
    produto = null;
  }

  function lerQtd() {
    var n = parseFloat(String(qtd.value || "").replace(",", "."));
    return isNaN(n) ? 0 : n;
  }

  function mudarQtd(delta) {
    var n = Math.max(1, lerQtd() + delta);
    qtd.value = produto && !produto.inteiro ? String(n).replace(".", ",") : String(Math.round(n));
    elErro.hidden = true;
  }

  function erro(texto) { elErro.textContent = texto; elErro.hidden = false; }

  function lerOutro() {
    if (produto) ultimo = { codigo: produto.codigo, quando: Date.now() };
    fecharGaveta();
    leitor.retomar();
  }

  function adicionar() {
    if (!produto) return;
    var q = lerQtd();
    if (q <= 0) { erro("Informe a quantidade."); return; }
    if (produto.inteiro && q !== Math.round(q)) { erro("Este produto só aceita quantidade inteira."); return; }
    if (q > produto.estoque) { erro("Estoque insuficiente. Disponível: " + numero(produto.estoque) + "."); return; }
    btnAdicionar.disabled = true;

    // O servidor responde os mesmos avisos do leitor USB (HX-Trigger); aqui eles aparecem na gaveta.
    var falha = null;
    var avisos = {
      estoqueInsuficiente: function (e) {
        return "Estoque insuficiente. Disponível: " + numero(e.detail && e.detail.disponivel) + ".";
      },
      quantidadeInvalida: function () { return "Quantidade inválida para este produto."; },
      produtoNaoEncontrado: function () { return "Produto não encontrado."; },
      caixaFechadoItem: function () { return "Caixa fechado: abra o caixa antes de lançar produtos."; },
    };
    var ouvintes = {};
    Object.keys(avisos).forEach(function (nome) {
      ouvintes[nome] = function (e) { falha = avisos[nome](e); };
      document.body.addEventListener(nome, ouvintes[nome]);
    });
    function soltar() {
      Object.keys(ouvintes).forEach(function (nome) { document.body.removeEventListener(nome, ouvintes[nome]); });
    }

    var item = produto;
    window.htmx.ajax("POST", "/venda/item", {
      target: "#carrinho", swap: "innerHTML",
      values: { produto_id: String(item.id), quantidade: String(q) },
    }).then(function () {
      soltar();
      atualizarTotal();
      if (falha) { erro(falha); btnAdicionar.disabled = false; return; }
      avisoCurto(numero(q) + "× " + item.nome + " adicionado", "ok");
      ultimo = { codigo: item.codigo, quando: Date.now() };
      fecharGaveta();
      leitor.retomar();
    }).catch(function () {
      soltar();
      erro("Não consegui lançar. Confira a conexão e tente de novo.");
      btnAdicionar.disabled = false;
    });
  }

  btnAbrir.addEventListener("click", abrir);
  $("cv-fechar").addEventListener("click", fechar);
  $("cv-concluir").addEventListener("click", fechar);
  $("cv-ler-outro").addEventListener("click", lerOutro);
  btnAdicionar.addEventListener("click", adicionar);
  tela.querySelectorAll("[data-cv-qtd]").forEach(function (b) {
    b.addEventListener("click", function () { mudarQtd(parseFloat(b.dataset.cvQtd)); });
  });
  qtd.addEventListener("keydown", function (e) {
    if (e.key === "Enter") { e.preventDefault(); adicionar(); }
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !tela.hidden) { e.preventDefault(); e.stopPropagation(); fechar(); }
  }, true);
})();
