// Leitor de código de barras USB no campo "Código de barras" (cadastro e edição).
// O leitor "digita" os números muito rápido (menos de ~50 ms entre teclas) e manda
// Enter no fim. Quando uma leitura chega com o campo já preenchido, o código novo
// SUBSTITUI o anterior, em vez de ser acrescentado no fim. Digitação manual (mais
// lenta) continua normal. Depois de cada leitura o código fica selecionado, então a
// próxima bipada também substitui.
function ligarLeitorCodigoBarras(campo, aoLer) {
  var INTERVALO_LEITOR_MS = 50;   // acima disso é gente digitando
  var MINIMO_DIGITOS = 6;         // leitura curta demais não é código de barras
  var rajada = "";
  var ultimaTecla = 0;
  var rapidas = 0;                // teclas que chegaram em ritmo de leitor
  var timer = null;
  var concluida = false;

  function concluir() {
    clearTimeout(timer);
    if (rajada.length >= MINIMO_DIGITOS && rapidas >= rajada.length - 1) {
      campo.value = rajada;       // descarta o que havia antes da leitura
      concluida = true;
      aoLer(rajada);
      campo.select();
    }
    rajada = "";
    rapidas = 0;
  }

  campo.addEventListener("keydown", function (e) {
    var agora = Date.now();
    if (e.key === "Enter") {
      e.preventDefault();         // não envia o formulário com "Nome" ainda vazio
      if (rajada) concluir();
      if (!concluida) aoLer(campo.value.trim());  // Enter depois de digitar à mão
      concluida = false;
      return;
    }
    if (e.key.length !== 1 || e.ctrlKey || e.metaKey || e.altKey) return;
    if (agora - ultimaTecla > INTERVALO_LEITOR_MS) {
      rajada = "";                // começo de uma nova sequência
      rapidas = 0;
    } else {
      rapidas += 1;
    }
    rajada += e.key;
    ultimaTecla = agora;
    concluida = false;
    // Leitor configurado sem Enter no fim: conclui depois de uma pausa curta.
    clearTimeout(timer);
    timer = setTimeout(concluir, 120);
  });
}

// Formulário de produto (pedido do dono, 07/10): Enter não envia (data-enter-avanca, em
// confirmar.js); só o botão grava, depois da confirmação com o resumo.
(function () {
  var form = document.getElementById("form-produto");
  if (!form) return;
  form.querySelectorAll("[data-obrigatorio-positivo]").forEach(function (campo) {
    campo.addEventListener("input", function () { campo.setCustomValidity(""); });
  });
})();

function _numeroBR(texto) {
  var t = String(texto || "").replace(/[^0-9,.-]/g, "");
  if (t.indexOf(",") !== -1) t = t.replace(/\./g, "").replace(",", ".");
  var n = parseFloat(t);
  return isNaN(n) ? 0 : n;
}

// Confirmação do cadastro NOVO (data-confirm-dinamico): confere os obrigatórios e mostra o
// resumo do que vai ser gravado. Devolver null cancela o envio.
window.mensagemCadastroProduto = function (form) {
  var nome = form.querySelector('input[name="nome"]');
  var venda = form.querySelector('input[name="preco_venda"]');
  if (!nome.value.trim()) { nome.focus(); nome.reportValidity(); return null; }
  if (_numeroBR(venda.value) <= 0) {
    venda.setCustomValidity("Informe o preço de venda (maior que zero).");
    venda.reportValidity();
    venda.focus();
    return null;
  }
  var valor = function (n) { var el = form.querySelector('[name="' + n + '"]'); return el ? el.value.trim() : ""; };
  var reais = function (n) { return "R$ " + valor(n).replace(/^R\$\s*/, ""); };  // a máscara pode já trazer "R$"
  var linhas = ["Produto: " + nome.value.trim(), "Preço de venda: " + reais("preco_venda")];
  if (_numeroBR(valor("preco_custo")) > 0) linhas.push("Preço de custo: " + reais("preco_custo"));
  linhas.push("Estoque inicial: " + (valor("estoque") || "0") + " " + (valor("unidade") || "UN"));
  if (valor("codigo_barras")) linhas.push("Código de barras: " + valor("codigo_barras"));
  return { mensagem: linhas.join("\n") + "\n\nCadastrar este produto?" };
};

// Ao bipar/digitar um código de barras no cadastro de produto NOVO:
//   1. Avisa se esse código já é de um produto seu (evita tentar duplicar).
//   2. Se não for, busca nome/marca/NCM em API externa e preenche os campos
//      que o usuário ainda não tiver digitado (ver app/services/produto_externo.py).
// Nunca roda editando um produto existente, e nunca é usado na venda.
(function () {
  var codigoInput = document.querySelector('input[name="codigo_barras"]');
  var nomeInput = document.querySelector('input[name="nome"]');
  var marcaInput = document.querySelector('input[name="marca"]');
  var ncmInput = document.querySelector('input[name="ncm"]');
  var cestInput = document.querySelector('input[name="cest"]');
  var idInput = document.querySelector('input[name="id"]');
  if (!codigoInput) return;
  var edicao = Boolean(idInput && idInput.value);
  if (edicao || !nomeInput || !marcaInput) {
    // Na edição só vale a substituição da leitura (sem busca automática).
    ligarLeitorCodigoBarras(codigoInput, function () {});
    return;
  }

  var aviso = document.createElement("small");
  aviso.className = "aviso-codigo-barras";
  aviso.hidden = true;
  codigoInput.insertAdjacentElement("afterend", aviso);

  // Campos preenchidos automaticamente por uma leitura anterior: numa nova leitura
  // eles são trocados; o que o usuário digitou à mão nunca é apagado.
  var automaticos = [nomeInput, marcaInput, ncmInput, cestInput].filter(Boolean);
  var ultimoBuscado = null;

  function preencher(campo, valor) {
    if (!campo || !valor) return;
    if (!campo.value.trim() || campo.dataset.preenchidoAuto === campo.value) {
      campo.value = valor;
      campo.dataset.preenchidoAuto = valor;
    }
  }

  function limparAutomaticos() {
    automaticos.forEach(function (campo) {
      if (campo.dataset.preenchidoAuto && campo.dataset.preenchidoAuto === campo.value) campo.value = "";
      delete campo.dataset.preenchidoAuto;
    });
  }

  function buscar() {
    var codigo = codigoInput.value.trim();
    if (codigo === ultimoBuscado) return;  // Enter + blur do mesmo código: uma busca só
    ultimoBuscado = codigo;
    aviso.hidden = true;
    limparAutomaticos();
    if (!codigo) return;

    fetch("/produtos/buscar-codigo-barras?codigo=" + encodeURIComponent(codigo))
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (dados) {
        if (!dados || codigoInput.value.trim() !== codigo) return;  // já bipou outro

        if (dados.ja_cadastrado) {
          // Nome como texto, nunca como HTML (revisão A2, V2).
          var link = document.createElement("a");
          link.href = "/produtos/" + encodeURIComponent(dados.produto_id) + "/editar";
          link.textContent = "editar em vez de cadastrar de novo";
          aviso.textContent = 'Este código já é do produto "' + dados.produto_nome + '" — ';
          aviso.appendChild(link);
          aviso.appendChild(document.createTextNode("."));
          aviso.hidden = false;
          return;
        }
        if (!dados.encontrado) return;

        preencher(nomeInput, dados.nome);
        preencher(marcaInput, dados.marca);
        preencher(ncmInput, dados.ncm);
        preencher(cestInput, dados.cest);
      })
      .catch(function () {}); // API fora do ar não deve travar o cadastro manual
  }

  codigoInput.addEventListener("blur", buscar);
  ligarLeitorCodigoBarras(codigoInput, buscar);
})();

// Escanear código de barras com a câmera — spec 011 (E1); leitura em camera-leitor.js (spec 020, comum à
// frente de caixa). Ao ler, preenche o campo e dispara o mesmo "blur" do leitor USB (no cadastro, busca
// nome/marca; na edição, só preenche).
(function () {
  var btnAbrir = document.getElementById("btn-escanear-camera");
  var codigoInput = document.querySelector('input[name="codigo_barras"]');
  if (!btnAbrir || !codigoInput || !window.LeitorCamera) return;

  var modal = document.getElementById("modal-scanner");
  var video = document.getElementById("video-scanner");
  var status = document.getElementById("scanner-status");
  var btnFechar = document.getElementById("btn-fechar-scanner");

  function avisar(texto) { if (status) status.textContent = texto; }

  var leitor = window.LeitorCamera(video, {
    aoAvisar: avisar,
    aoLer: function (texto) {
      codigoInput.value = texto;
      codigoInput.dispatchEvent(new Event("blur"));
      fechar();
      codigoInput.focus();
    },
  });

  function fechar() {
    leitor.parar();
    if (modal) modal.hidden = true;
  }

  btnAbrir.addEventListener("click", function () {
    if (modal) modal.hidden = false;
    avisar("Aponte a câmera traseira para o código de barras, a um palmo de distância.");
    leitor.iniciar();
  });
  if (btnFechar) btnFechar.addEventListener("click", fechar);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && modal && !modal.hidden) fechar();
  });
})();

// ---- Painel lateral de cadastro/edição (docs/10, 3.5) ----
(function () {
  var painel = document.getElementById("painel-produto");
  var fundo = document.getElementById("painel-fundo");
  if (!painel || !fundo) return;
  var editando = painel.getAttribute("data-editando") === "1";
  var form = document.getElementById("form-produto");

  function abrir() {
    painel.hidden = false;
    fundo.hidden = false;
    document.body.classList.add("painel-aberto");
    var nome = painel.querySelector('input[name="nome"]');
    if (nome) setTimeout(function () { nome.focus(); }, 30);
  }
  function fechar() {
    if (editando) { window.location.href = "/produtos"; return; }  // a lista já está atrás do painel
    painel.hidden = true;
    fundo.hidden = true;
    document.body.classList.remove("painel-aberto");
    if (form) form.reset();
  }

  Array.prototype.forEach.call(document.querySelectorAll("[data-abre-painel]"), function (b) {
    b.addEventListener("click", abrir);
  });
  var btnFechar = document.getElementById("btn-fechar-painel");
  var btnCancelar = document.getElementById("btn-cancelar-painel");
  if (btnFechar) btnFechar.addEventListener("click", fechar);
  if (btnCancelar) btnCancelar.addEventListener("click", fechar);
  fundo.addEventListener("click", fechar);
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape" || e.defaultPrevented || painel.hidden) return;
    var confirmar = document.getElementById("modal-confirmar");
    var scanner = document.getElementById("modal-scanner");
    if ((confirmar && !confirmar.hidden) || (scanner && !scanner.hidden)) return;
    fechar();
  });

  // "Salvar e cadastrar outro": o servidor reabre o painel vazio depois de gravar.
  var campoOutro = document.getElementById("campo-outro");
  var btnOutro = document.getElementById("btn-salvar-outro");
  var btnSalvar = document.getElementById("btn-salvar-produto");
  if (campoOutro && btnOutro) btnOutro.addEventListener("click", function () { campoOutro.value = "1"; });
  if (campoOutro && btnSalvar) btnSalvar.addEventListener("click", function () { campoOutro.value = ""; });

  // Faixa de margem ao vivo: some se faltar custo ou venda; vermelha se a margem for negativa.
  var faixa = document.getElementById("margem-vivo");
  var custo = form && form.querySelector('input[name="preco_custo"]');
  var venda = form && form.querySelector('input[name="preco_venda"]');
  function margem() {
    if (!faixa || !custo || !venda) return;
    var c = _numeroBR(custo.value), v = _numeroBR(venda.value);
    if (c <= 0 || v <= 0) { faixa.hidden = true; return; }
    var lucro = v - c, pct = lucro / v * 100;
    var reais = function (n) { return "R$ " + Math.abs(n).toFixed(2).replace(".", ",").replace(/\B(?=(\d{3})+(?!\d))/g, "."); };
    document.getElementById("margem-pct").textContent = "Margem " + Math.round(pct) + "%";
    document.getElementById("margem-lucro").textContent = (lucro >= 0 ? "lucro de " : "prejuízo de ") + reais(lucro) + " por unidade";
    faixa.classList.toggle("negativa", lucro < 0);
    faixa.hidden = false;
  }
  [custo, venda].forEach(function (c) {
    if (!c) return;
    c.addEventListener("input", margem);
    c.addEventListener("change", margem);
    c.addEventListener("blur", margem);
  });
  margem();

  if (painel.getAttribute("data-abrir") === "1") abrir();
})();

// Itens que abrem um bloco "sob demanda" (ex.: Planilha ▾ › Importar planilha).
Array.prototype.forEach.call(document.querySelectorAll("[data-abre]"), function (b) {
  b.addEventListener("click", function () {
    var alvo = document.getElementById(b.getAttribute("data-abre"));
    var menu = b.closest("details");
    if (menu) menu.open = false;
    if (!alvo) return;
    alvo.open = true;
    alvo.scrollIntoView({ behavior: "smooth", block: "center" });
  });
});
