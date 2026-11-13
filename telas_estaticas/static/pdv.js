function formatBRL(v) {
  return "R$ " + Number(v || 0).toLocaleString("pt-BR", {
    minimumFractionDigits: 2, maximumFractionDigits: 2,
  });
}

// Texto vindo do banco (nome de produto, unidade) montado em HTML: sem isso um nome com <img onerror=…> rodaria no
// navegador de quem busca (revisão A2, V2). Também usado pelo offline.js.
function escaparHtml(t) {
  return String(t == null ? "" : t).replace(/[&<>"']/g, function (c) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
  });
}

// "R$ 1.234,50" -> 1234.5
function parseBRL(txt) {
  if (!txt) return 0;
  return parseFloat(txt.replace(/[^0-9,.-]/g, "").replace(/\./g, "").replace(",", ".")) || 0;
}

function mostrarAlerta(msg, tipo) {
  var el = document.getElementById("alerta");
  if (!el) return;
  el.textContent = msg;
  el.className = "alert " + (tipo || "");
  el.hidden = false;
  clearTimeout(el._t);
  el._t = setTimeout(function () { el.hidden = true; }, 4000);
}

// Mensagens vindas do servidor via HX-Trigger.
document.body.addEventListener("produtoNaoEncontrado", function () {
  mostrarAlerta("Produto não encontrado. Cadastre-o em Produtos.", "erro");
});
document.body.addEventListener("produtoInativo", function () {
  mostrarAlerta("Esse produto foi excluído do cadastro e não está mais à venda.", "erro");
});
document.body.addEventListener("formaInvalida", function () {
  mostrarAlerta("Forma de pagamento inválida. Escolha de novo.", "erro");
});
document.body.addEventListener("clienteInvalido", function () {
  mostrarAlerta("Cliente não encontrado. Escolha o cliente de novo.", "erro");
});
document.body.addEventListener("vendaVazia", function () {
  mostrarAlerta("Adicione itens antes de finalizar.", "erro");
});
document.body.addEventListener("fiadoSemCliente", function () {
  mostrarAlerta("Venda na Confiança exige selecionar um cliente cadastrado.", "erro");
});
document.body.addEventListener("limiteFiadoExcedido", function (evt) {
  var disp = (evt.detail && typeof evt.detail.disponivel === "number") ? evt.detail.disponivel : 0;
  mostrarAlerta("Limite da Confiança excedido. Disponível: " + formatBRL(disp), "erro");
});
document.body.addEventListener("estoqueInsuficiente", function (evt) {
  var disp = (evt.detail && typeof evt.detail.disponivel === "number") ? evt.detail.disponivel : 0;
  mostrarAlerta("Estoque insuficiente. Disponível: " + disp, "erro");
});
document.body.addEventListener("pagamentoCombinadoInvalido", function () {
  mostrarAlerta("A soma das partes não bate com o total da venda. Confira os valores.", "erro");
});
document.body.addEventListener("semVendaAnterior", function () {
  mostrarAlerta("Nenhuma venda anterior deste operador pra repetir.", "erro");
});
document.body.addEventListener("quantidadeInvalida", function (evt) {
  var d = evt.detail || {};
  if (d.motivo === "inteira") {
    mostrarAlerta("Este produto (" + (d.unidade || "UN") + ") só aceita quantidade inteira.", "erro");
  } else {
    mostrarAlerta("Quantidade inválida (de 1 a 9.999).", "erro");
  }
});
document.body.addEventListener("caixaFechado", function () {
  mostrarAlerta("Abra o caixa antes de finalizar a venda.", "erro");
});
document.body.addEventListener("caixaFechadoItem", function () {
  mostrarAlerta("Caixa fechado: abra o caixa antes de lançar produtos na sacola.", "erro");
});
document.body.addEventListener("valorRecebidoInsuficiente", function (evt) {
  var falta = (evt.detail && typeof evt.detail.falta === "number") ? evt.detail.falta : 0;
  mostrarAlerta("Valor recebido menor que o total. Falta " + formatBRL(falta) + ".", "erro");
});

// "50" / "50,00" / "1.234,50" -> número; vazio ou inválido -> null.
function lerValor(txt) {
  var t = String(txt == null ? "" : txt).replace(/[^0-9,.]/g, "");
  if (!t) return null;
  if (t.indexOf(",") !== -1) t = t.replace(/\./g, "").replace(",", ".");
  var n = parseFloat(t);
  return isNaN(n) ? null : n;
}

document.body.addEventListener("documentoInvalido", function (evt) {
  var tipo = (evt.detail && evt.detail.tipo) || "Documento";
  mostrarAlerta(tipo + " inválido, confira o número digitado.", "erro");
});

// ===================== Validação de CPF/CNPJ (espelha app/services/documento.py) =====================
function validarCPF(cpf) {
  cpf = (cpf || "").replace(/\D/g, "");
  if (cpf.length !== 11 || cpf === cpf[0].repeat(11)) return false;
  for (var i = 9; i <= 10; i++) {
    var soma = 0;
    for (var n = 0; n < i; n++) soma += parseInt(cpf[n], 10) * ((i + 1) - n);
    var digito = ((soma * 10) % 11) % 10;
    if (digito !== parseInt(cpf[i], 10)) return false;
  }
  return true;
}

function validarCNPJ(cnpj) {
  cnpj = (cnpj || "").replace(/\D/g, "");
  if (cnpj.length !== 14 || cnpj === cnpj[0].repeat(14)) return false;
  var pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
  var pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
  function digitoVerificador(base, pesos) {
    var soma = 0;
    for (var n = 0; n < base.length; n++) soma += parseInt(base[n], 10) * pesos[n];
    var r = soma % 11;
    return r < 2 ? "0" : String(11 - r);
  }
  if (digitoVerificador(cnpj.slice(0, 12), pesos1) !== cnpj[12]) return false;
  if (digitoVerificador(cnpj.slice(0, 13), pesos2) !== cnpj[13]) return false;
  return true;
}

function validarDocumento(tipo, numero) {
  if (tipo === "CPF") return validarCPF(numero);
  if (tipo === "CNPJ") return validarCNPJ(numero);
  return false;
}

// ===================== Vitrine do Balcão (segundo monitor) =====================
// Manda o estado da venda pra tela do cliente por dois caminhos: BroadcastChannel (outra
// janela/aba do mesmo navegador, na hora e até sem internet) e o servidor, que repassa para
// a vitrine aberta em qualquer aparelho com o mesmo login (services/vitrine.py). O `id`
// deixa a vitrine que recebe pelos dois caminhos aplicar a mensagem uma vez só.
var _canalBalcao = ("BroadcastChannel" in window) ? new BroadcastChannel("pdv-balcao") : null;
var _origemBalcao = Math.random().toString(36).slice(2);
var _seqBalcao = 0;
var _filaBalcao = Promise.resolve();  // um envio por vez: a vitrine recebe na ordem certa

function avisarBalcao(msg) {
  msg.id = _origemBalcao + "-" + (++_seqBalcao);
  if (_canalBalcao) _canalBalcao.postMessage(msg);
  var meta = document.querySelector('meta[name="csrf-token"]');
  var corpo = JSON.stringify(msg);
  _filaBalcao = _filaBalcao.then(function () {
    // keepalive: o aviso de "finalizada" sai mesmo se a página recarregar em seguida.
    return fetch("/venda/balcao/evento", {
      method: "POST", keepalive: true, body: corpo,
      headers: { "Content-Type": "application/json", "X-CSRF-Token": meta ? meta.content : "" },
    });
  }).catch(function () { /* sem rede: o BroadcastChannel ainda atende a vitrine deste navegador */ });
}

// Lê o carrinho renderizado (mesmo DOM que o operador vê) e manda o estado completo —
// mais simples e confiável do que tentar acompanhar item por item em paralelo.
function avisarBalcaoEstadoCarrinho() {
  var linhas = document.querySelectorAll("#carrinho table.itens tbody tr[data-item-id]");
  var itens = Array.prototype.map.call(linhas, function (tr) {
    var tds = tr.querySelectorAll("td");
    return {
      nome: tds[0] ? tds[0].textContent.trim() : "",
      qtd: tds[1] ? tds[1].textContent.trim() : "",
      unit: tds[2] ? tds[2].textContent.trim() : "",
      subtotal: tds[3] ? tds[3].textContent.trim() : "",
      // Item que acabou de ser bipado/alterado (ver item_tocado_id em vendas.py)
      // — bipar um item que já está no carrinho só muda a quantidade da linha
      // dele, sem mudar a posição; sem isto a Vitrine acharia que "o último
      // item" é sempre a última linha da tabela, não o que foi bipado agora.
      tocado: tr.hasAttribute("data-recem-bipado"),
    };
  });
  var totalEl = document.getElementById("total-valor");
  // Desconto (balcão + cashback) vai para o cliente só como valor: o motivo é anotação
  // interna e fica na tela do operador. Sem desconto, a Vitrine mostra só o total.
  var detalhe = document.getElementById("totais-detalhe");
  var desconto = detalhe ? parseFloat(detalhe.dataset.descontoTotal) || 0 : 0;
  avisarBalcao({
    tipo: "estado",
    itens: itens,
    totalTexto: totalEl ? totalEl.textContent.trim() : "",
    subtotalTexto: desconto > 0 ? formatBRL(parseFloat(detalhe.dataset.subtotal) || 0) : "",
    descontoTexto: desconto > 0 ? formatBRL(desconto) : "",
  });
}

// ===================== Fluxo de pagamento por teclado =====================
// Estados: "scanning" -> "tipo" -> ("maquina" | "dinheiro") -> "ready"
var LABEL = {
  DINHEIRO: "Dinheiro", PIX: "Pix", FIADO: "Confiança",
  CIELO_DEBITO: "Cielo · Débito", CIELO_CREDITO: "Cielo · Crédito",
  STONE_DEBITO: "Stone · Débito", STONE_CREDITO: "Stone · Crédito",
  CIELO_CREDITO_PARCELADO: "Cielo · Crédito parcelado", STONE_CREDITO_PARCELADO: "Stone · Crédito parcelado",
};

// Cartão: maquininha + tipo -> forma. "CIELO_PARCELADO" + "CREDITO" -> "CIELO_CREDITO_PARCELADO" (spec 022).
function formaCartao(maq, tipo) {
  var parcelado = /_PARCELADO$/.test(maq);
  return maq.replace(/_PARCELADO$/, "") + "_" + tipo + (parcelado ? "_PARCELADO" : "");
}

document.addEventListener("DOMContentLoaded", function () {
  var codigo = document.getElementById("codigo");
  var formItem = document.getElementById("form-item");
  var formPagto = document.getElementById("form-pagto");
  var forma = document.getElementById("forma");

  var elHint = document.getElementById("pagto-hint");
  var elDocumento = document.getElementById("pay-documento");
  var elDocumentoNumero = document.getElementById("pay-documento-numero");
  var elDocumentoNumeroTitulo = document.getElementById("pay-documento-numero-titulo");
  var elDocumentoInput = document.getElementById("documento_numero_input");
  var campoDocTipo = document.getElementById("nota_documento_tipo");
  var campoDocNumero = document.getElementById("nota_documento_numero");
  var elTipo = document.getElementById("pay-tipo");
  var elMaquina = document.getElementById("pay-maquina");
  var elDinheiro = document.getElementById("pay-dinheiro");
  var elValor = document.getElementById("valor_recebido");
  var elTroco = document.getElementById("troco");
  var elFalta = document.getElementById("falta");
  var elEscolhido = document.getElementById("pay-escolhido");
  var btnFinalizar = document.getElementById("btn-finalizar");
  var elQuantidade = document.getElementById("quantidade");
  var btnVoltarDocumento = document.getElementById("btn-voltar-documento");
  var elPixQr = document.getElementById("pix-qrcode-container");
  var elComboStatus = document.getElementById("pay-combo-status");
  var elComboLista = document.getElementById("combo-lista");
  var elComboRestante = document.getElementById("combo-restante");
  var elComboValor = document.getElementById("pay-combo-valor");
  var elComboValorForma = document.getElementById("combo-valor-forma");
  var elComboValorInput = document.getElementById("combo_valor_input");
  var btnComboIniciar = document.getElementById("btn-combo-iniciar");
  var pagamentosJson = document.getElementById("pagamentos_json");

  var estado = "scanning";
  var tipoPendente = null;  // "DEBITO" ou "CREDITO" aguardando a máquina
  var docPendente = null;   // "CPF" ou "CNPJ" aguardando o número ser digitado
  var pixTimer = null;      // timeout que esconde o QR do Pix após 2 minutos
  var modoCarrinho = false;      // navegação por teclado nos itens do carrinho (F3)
  var itemSelecionadoId = null;  // id do item destacado durante modoCarrinho

  // ---------- Pagamento combinado (varias formas numa venda so) ----------
  var LABEL_TIPO = { DINHEIRO: "Dinheiro", DEBITO: "Débito", CREDITO: "Crédito", PIX: "Pix", FIADO: "Confiança" };
  var comboParcelas = [];       // {forma, valor, valorRecebido}
  var comboRestante = 0;
  var comboFormaPendente = null;  // forma (ou DEBITO/CREDITO) da parte sendo preenchida
  var comboValorPendente = 0;     // valor ja confirmado dessa parte, aguardando maquina/dinheiro

  // Exposto pro offline.js resetar a UI de pagamento após finalizar uma venda offline.
  window._voltarScanningPdv = function () { voltarScanning(); };

  function temItens() {
    return document.querySelectorAll("#carrinho table.itens tbody tr:not(.vazio)").length > 0;
  }

  function mostrar(el, visivel) { if (el) el.hidden = !visivel; }

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
            elPixQr.innerHTML = '<p class="muted small">QR expirado.</p>';
            return;
          }
          atualizarContador();
        }, 1000);
      });
  }

  function voltarScanning() {
    estado = "scanning";
    tipoPendente = null;
    docPendente = null;
    forma.value = "";
    campoDocTipo.value = "NAO";
    campoDocNumero.value = "";
    mostrar(elHint, true);
    mostrar(elDocumento, false);
    mostrar(elDocumentoNumero, false);
    mostrar(elTipo, false);
    mostrar(elMaquina, false);
    mostrar(elDinheiro, false);
    mostrar(elEscolhido, false);
    mostrar(btnFinalizar, false);
    esconderPixQr();
    if (elTroco) elTroco.textContent = "";
    mostrar(elFalta, false);
    if (btnFinalizar) btnFinalizar.disabled = false;
    if (elValor) elValor.value = "";
    if (codigo) codigo.focus();
    avisarBalcao({ tipo: "limpar_status" });
    resetarCombo();
  }

  function resetarCombo() {
    comboParcelas = [];
    comboRestante = 0;
    comboFormaPendente = null;
    comboValorPendente = 0;
    if (pagamentosJson) pagamentosJson.value = "";
    mostrar(elComboStatus, false);
    mostrar(elComboValor, false);
    mostrar(btnComboIniciar, true);
  }

  function iniciarCombo() {
    comboParcelas = [];
    comboRestante = parseBRL(document.getElementById("total-valor").textContent);
    mostrar(elComboStatus, true);
    atualizarComboStatus();
    irParaComboTipo();
  }

  function cancelarCombo() {
    resetarCombo();
    irParaFormaPagamento();
  }

  function irParaComboTipo() {
    estado = "combo-tipo";
    mostrar(elComboValor, false);
    mostrar(elMaquina, false);
    mostrar(elDinheiro, false);
    mostrar(elEscolhido, false);
    mostrar(btnFinalizar, false);
    mostrar(btnComboIniciar, false);  // dentro do combo nao pode combinar de novo
    mostrar(elTipo, true);
  }

  function atualizarComboStatus() {
    if (elComboLista) {
      elComboLista.innerHTML = comboParcelas.map(function (p) {
        return '<div>' + (LABEL_TIPO[p.forma] || LABEL[p.forma] || p.forma) + ': ' + formatBRL(p.valor) + '</div>';
      }).join("");
    }
    if (elComboRestante) {
      elComboRestante.textContent = "Falta pagar: " + formatBRL(comboRestante);
    }
  }

  function escolherTipoParaCombo(tipo) {
    if (tipo === "FIADO") {
      var cli = document.getElementById("cliente_id");
      if (!cli || !cli.value) {
        mostrarAlerta("A Confiança exige selecionar um cliente cadastrado.", "erro");
        return;
      }
    }
    comboFormaPendente = tipo;
    mostrar(elTipo, false);
    if (elComboValorForma) elComboValorForma.textContent = LABEL_TIPO[tipo] || tipo;
    estado = "combo-valor";
    if (elComboValorInput) {
      elComboValorInput.value = comboRestante.toFixed(2).replace(".", ",");
      mostrar(elComboValor, true);
      // Foca só no próximo quadro: a tecla que escolheu a forma não pode cair no
      // campo nem disputar a seleção com a primeira tecla do valor (achado B3).
      requestAnimationFrame(function () { elComboValorInput.focus(); elComboValorInput.select(); });
    }
  }

  function confirmarValorCombo() {
    var valor = lerValor(elComboValorInput.value);
    if (!valor || valor <= 0 || valor > comboRestante + 0.01) {
      mostrarAlerta("Valor inválido (máximo " + formatBRL(comboRestante) + ").", "erro");
      return;
    }
    comboValorPendente = Math.min(valor, comboRestante);
    if (comboFormaPendente === "DEBITO" || comboFormaPendente === "CREDITO") {
      mostrar(elComboValor, false);
      mostrarMaquinas(comboFormaPendente);
      estado = "combo-maquina";
    } else if (comboFormaPendente === "DINHEIRO") {
      mostrar(elComboValor, false);
      mostrar(elDinheiro, true);
      estado = "combo-dinheiro";
      if (elValor) { elValor.value = ""; elValor.focus(); }
      atualizarTroco();
    } else {
      adicionarParcelaCombo(comboFormaPendente, comboValorPendente, 0);
    }
  }

  function confirmarDinheiroCombo() {
    var recebido = lerValor(elValor.value);  // vazio = valor exato desta parte
    if (recebido !== null && recebido + 0.001 < comboValorPendente) {
      mostrarAlerta("Valor recebido menor que esta parte. Falta " +
        formatBRL(comboValorPendente - recebido) + ".", "erro");
      return;
    }
    mostrar(elDinheiro, false);
    mostrar(elFalta, false);
    adicionarParcelaCombo("DINHEIRO", comboValorPendente, recebido);
  }

  function adicionarParcelaCombo(forma, valor, valorRecebido) {
    comboParcelas.push({
      forma: forma, valor: valor,
      valorRecebido: (valorRecebido === undefined || valorRecebido === 0) ? null : valorRecebido,
    });
    comboRestante = Math.max(0, Math.round((comboRestante - valor) * 100) / 100);
    comboFormaPendente = null;
    comboValorPendente = 0;
    atualizarComboStatus();
    avisarBalcao({
      tipo: "forma", formaCodigo: forma, valor: valor,
      texto: (LABEL_TIPO[forma] || LABEL[forma] || forma) + " " + formatBRL(valor),
    });
    if (forma === "PIX") { mostrarPixQr(valor); } else { esconderPixQr(); }
    if (comboRestante <= 0.01) {
      finalizarCombo();
    } else {
      irParaComboTipo();
    }
  }

  function finalizarCombo() {
    forma.value = "COMBINADO";
    pagamentosJson.value = JSON.stringify(comboParcelas.map(function (p) {
      return { forma: p.forma, valor: p.valor, valor_recebido: p.valorRecebido };
    }));
    elEscolhido.textContent = "Pagamento combinado: " + comboParcelas.map(function (p) {
      return (LABEL_TIPO[p.forma] || LABEL[p.forma] || p.forma) + " " + formatBRL(p.valor);
    }).join(" + ");
    mostrar(elEscolhido, true);
    mostrar(btnFinalizar, true);
    estado = "ready";
    btnFinalizar.focus();
  }

  function abrirPagamento() {
    if (!temItens()) { mostrarAlerta("Adicione itens antes de pagar.", "erro"); return; }
    estado = "documento";
    if (codigo) codigo.blur();
    mostrar(elHint, false);
    mostrar(elDocumento, true);
    mostrar(elDocumentoNumero, false);
    mostrar(elTipo, false);
    mostrar(elMaquina, false);
    mostrar(elDinheiro, false);
    mostrar(elEscolhido, false);
    mostrar(btnFinalizar, false);
    avisarBalcao({ tipo: "opcoes", titulo: "CPF/CNPJ na nota?", itens: ["Não", "CPF", "CNPJ"] });
  }

  function irParaFormaPagamento() {
    mostrar(elDocumento, false);
    mostrar(elDocumentoNumero, false);
    mostrar(elTipo, true);
    estado = "tipo";
    avisarBalcao({
      tipo: "opcoes", titulo: "Forma de pagamento",
      itens: ["Dinheiro", "Débito", "Crédito", "Pix", "Confiança"],
    });
  }

  function escolherDocumento(tipo) {
    if (tipo === "NAO") {
      campoDocTipo.value = "NAO";
      campoDocNumero.value = "";
      irParaFormaPagamento();
      return;
    }
    docPendente = tipo;
    elDocumentoNumeroTitulo.textContent = tipo;
    mostrar(elDocumento, false);
    mostrar(elDocumentoNumero, true);
    estado = "documento-numero";
    if (elDocumentoInput) { elDocumentoInput.value = ""; elDocumentoInput.focus(); }
    avisarBalcao({ tipo: "status", texto: "Digitando " + tipo });
  }

  function voltarParaDocumento() {
    mostrar(elDocumentoNumero, false);
    mostrar(elDocumento, true);
    estado = "documento";
  }

  function confirmarDocumentoNumero() {
    var valor = (elDocumentoInput.value || "").replace(/\D/g, "");
    var esperado = docPendente === "CPF" ? 11 : 14;
    if (valor.length !== esperado) {
      mostrarAlerta(docPendente + " deve ter " + esperado + " dígitos.", "erro");
      return;
    }
    if (!validarDocumento(docPendente, valor)) {
      mostrarAlerta(docPendente + " inválido, confira o número digitado.", "erro");
      return;
    }
    campoDocTipo.value = docPendente;
    campoDocNumero.value = valor;
    var valorFormatado = docPendente === "CPF"
      ? valor.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4")
      : valor.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, "$1.$2.$3/$4-$5");
    avisarBalcao({ tipo: "documento", texto: docPendente + " " + valorFormatado });
    irParaFormaPagamento();
  }

  function definirForma(valor) {
    forma.value = valor;
    elEscolhido.textContent = "Pagamento: " + (LABEL[valor] || valor);
    mostrar(elEscolhido, true);
    mostrar(btnFinalizar, true);
    estado = "ready";
    btnFinalizar.focus();
    if (valor === "PIX") { mostrarPixQr(); } else { esconderPixQr(); }
    avisarBalcao({ tipo: "forma", formaCodigo: valor, texto: LABEL[valor] || valor });
  }

  function escolherTipo(tipo) {
    if (tipo === "COMBINADO") {
      iniciarCombo();
    } else if (tipo === "DINHEIRO") {
      forma.value = "DINHEIRO";
      mostrar(elTipo, false);
      mostrar(elDinheiro, true);
      mostrar(btnFinalizar, true);
      elEscolhido.textContent = "Pagamento: Dinheiro";
      mostrar(elEscolhido, true);
      estado = "dinheiro";
      if (elValor) { elValor.value = ""; elValor.focus(); }
      atualizarTroco();
      esconderPixQr();
      avisarBalcao({ tipo: "forma", formaCodigo: "DINHEIRO", texto: "Dinheiro" });
    } else if (tipo === "PIX") {
      mostrar(elTipo, false);
      definirForma("PIX");
    } else if (tipo === "FIADO") {
      var cli = document.getElementById("cliente_id");
      if (!cli || !cli.value) {
        mostrarAlerta("A Confiança exige selecionar um cliente cadastrado.", "erro");
        return;
      }
      mostrar(elTipo, false);
      definirForma("FIADO");
    } else { // DEBITO ou CREDITO -> escolher máquina
      tipoPendente = tipo;
      mostrar(elTipo, false);
      mostrarMaquinas(tipo);
      estado = "maquina";
    }
  }

  // Escolha da maquininha; no crédito aparecem também as opções parceladas (spec 022).
  function mostrarMaquinas(tipo) {
    var credito = tipo === "CREDITO";
    elMaquina.querySelectorAll("[data-so-credito]").forEach(function (b) { b.hidden = !credito; });
    mostrar(elMaquina, true);
    avisarBalcao({ tipo: "opcoes", titulo: "Qual maquininha?",
                   itens: credito ? ["Cielo", "Stone", "Cielo parcelado", "Stone parcelado"] : ["Cielo", "Stone"] });
  }

  function escolherMaquina(maq) {
    if (estado === "combo-maquina") {
      mostrar(elMaquina, false);
      if (maq === "VOLTAR") { cancelarCombo(); return; }
      adicionarParcelaCombo(formaCartao(maq, comboFormaPendente), comboValorPendente, 0);
      return;
    }
    if (maq === "VOLTAR") {
      mostrar(elMaquina, false);
      irParaFormaPagamento();
      return;
    }
    mostrar(elMaquina, false);
    definirForma(formaCartao(maq, tipoPendente));  // ex.: CIELO_DEBITO, STONE_CREDITO_PARCELADO
    tipoPendente = null;
  }

  function atualizarTroco() {
    if (!elTroco) return;
    var base = (estado === "combo-dinheiro")
      ? comboValorPendente
      : parseBRL(document.getElementById("total-valor").textContent);
    var recebido = lerValor(elValor.value);  // vazio = pagamento exato
    var falta = recebido === null ? 0 : Math.round((base - recebido) * 100) / 100;
    var troco = recebido === null ? 0 : recebido - base;
    elTroco.textContent = troco > 0.004 ? ("Troco: " + formatBRL(troco)) : "";
    if (elFalta) {
      elFalta.textContent = falta > 0 ? ("Falta " + formatBRL(falta)) : "";
      mostrar(elFalta, falta > 0);
    }
    // Com dinheiro faltando, Finalizar fica desabilitado (achado C1).
    if (btnFinalizar && estado === "dinheiro") btnFinalizar.disabled = falta > 0;
  }

  function faltaDinheiro() {
    return estado === "dinheiro" && elFalta && !elFalta.hidden;
  }

  function finalizar() {
    if (!forma.value) return;
    if (faltaDinheiro()) {
      mostrarAlerta("Valor recebido menor que o total. " + elFalta.textContent + ".", "erro");
      if (elValor) elValor.focus();
      return;
    }
    if (formPagto.requestSubmit) formPagto.requestSubmit();
    else formPagto.submit();
  }

  // ---------- Navegação por teclado no carrinho (F3) ----------
  function linhasCarrinho() {
    return Array.prototype.slice.call(
      document.querySelectorAll("#carrinho table.itens tbody tr[data-item-id]")
    );
  }

  function aplicarSelecaoCarrinho() {
    linhasCarrinho().forEach(function (tr) {
      tr.classList.toggle("selecionada", tr.dataset.itemId === itemSelecionadoId);
    });
    var atual = itemSelecionadoId && document.getElementById("item-" + itemSelecionadoId);
    if (atual) atual.scrollIntoView({ block: "nearest" });
  }

  function ativarNavegacaoCarrinho() {
    var linhas = linhasCarrinho();
    if (!linhas.length) { mostrarAlerta("Carrinho vazio.", "erro"); return; }
    if (!itemSelecionadoId || !document.getElementById("item-" + itemSelecionadoId)) {
      itemSelecionadoId = linhas[0].dataset.itemId;
    }
    modoCarrinho = true;
    if (codigo) codigo.blur();
    fecharSug();
    aplicarSelecaoCarrinho();
  }

  function sairNavegacaoCarrinho() {
    modoCarrinho = false;
    linhasCarrinho().forEach(function (tr) { tr.classList.remove("selecionada"); });
    if (codigo) codigo.focus();
  }

  function moverSelecaoCarrinho(direcao) {
    var linhas = linhasCarrinho();
    if (!linhas.length) return;
    var idx = linhas.findIndex(function (tr) { return tr.dataset.itemId === itemSelecionadoId; });
    idx = Math.max(0, Math.min(linhas.length - 1, idx + direcao));
    itemSelecionadoId = linhas[idx].dataset.itemId;
    aplicarSelecaoCarrinho();
  }

  function aposAtualizarCarrinho() {
    var linhas = linhasCarrinho();
    if (!linhas.length) { sairNavegacaoCarrinho(); return; }
    if (!document.getElementById("item-" + itemSelecionadoId)) {
      itemSelecionadoId = linhas[0].dataset.itemId;
    }
    aplicarSelecaoCarrinho();
  }

  function ajustarQuantidadeSelecionada(delta) {
    if (!itemSelecionadoId || typeof htmx === "undefined") return;
    htmx.ajax("POST", "/venda/item/" + itemSelecionadoId + "/quantidade", {
      target: "#carrinho", swap: "innerHTML", values: { delta: delta },
    }).then(aposAtualizarCarrinho);
  }

  function removerItemSelecionado() {
    if (!itemSelecionadoId || typeof htmx === "undefined") return;
    htmx.ajax("POST", "/venda/item/" + itemSelecionadoId + "/remover", {
      target: "#carrinho", swap: "innerHTML",
    }).then(aposAtualizarCarrinho);
  }

  // Cliques nos botões (também funciona por toque/mouse).
  if (elDocumento) elDocumento.addEventListener("click", function (e) {
    var b = e.target.closest("[data-doc]"); if (b) escolherDocumento(b.dataset.doc);
  });
  if (elDocumentoInput) elDocumentoInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter") { e.preventDefault(); confirmarDocumentoNumero(); }
  });
  if (elDocumentoInput) elDocumentoInput.addEventListener("input", function () {
    var max = docPendente === "CPF" ? 11 : 14;
    elDocumentoInput.value = elDocumentoInput.value.replace(/\D/g, "").slice(0, max);
  });
  if (btnVoltarDocumento) btnVoltarDocumento.addEventListener("click", voltarParaDocumento);
  var btnIrPagamento = document.getElementById("btn-ir-pagamento");
  if (btnIrPagamento) btnIrPagamento.addEventListener("click", function () {
    if (estado === "scanning") abrirPagamento();
  });

  // Barra do rodapé no celular: espelha o total (trocado pelo htmx ou pelo offline.js) e mostra a ação do momento:
  // Pagar no modo de leitura, Finalizar venda quando o botão do formulário está à vista (ele some no celular para a
  // barra não cobrir), nada nas escolhas intermediárias (CPF, forma, maquininha).
  var barraTotal = document.getElementById("pdv-barra-total");
  var btnBarra = document.getElementById("btn-barra-acao");
  var cartaoTotais = document.querySelector(".pdv-right .totais");
  function sincronizarBarra() {
    var t = document.getElementById("total-valor");
    if (barraTotal && t) barraTotal.textContent = t.textContent;
    if (!btnBarra) return;
    var lendo = elHint && !elHint.hidden;
    var finalizando = btnFinalizar && !btnFinalizar.hidden;
    btnBarra.hidden = !lendo && !finalizando;
    btnBarra.textContent = finalizando ? "Finalizar venda" : "Pagar";
    btnBarra.disabled = finalizando && btnFinalizar.disabled;
  }
  // Finalizar uma vez só: depois do primeiro envio o botão fica desativado até a página recarregar (o servidor
  // também recusa o segundo pedido — revisão A2, V1). O modo offline cancela o envio normal (offline.js, que roda
  // depois deste): aí nada fica travado.
  var enviandoPagamento = false;
  if (formPagto) formPagto.addEventListener("submit", function (e) {
    if (enviandoPagamento) { e.preventDefault(); return; }
    setTimeout(function () {
      if (e.defaultPrevented) return;
      enviandoPagamento = true;
      if (btnFinalizar) btnFinalizar.disabled = true;
    }, 0);
  });

  if (cartaoTotais) new MutationObserver(sincronizarBarra).observe(cartaoTotais, { childList: true, subtree: true, characterData: true });
  [elHint, btnFinalizar].forEach(function (el) {
    if (el) new MutationObserver(sincronizarBarra).observe(el, { attributes: true, attributeFilter: ["hidden", "disabled"] });
  });
  if (btnBarra) btnBarra.addEventListener("click", function () {
    if (btnFinalizar && !btnFinalizar.hidden) { btnFinalizar.click(); return; }
    if (estado === "scanning") abrirPagamento();
    if (estado !== "scanning") {
      var cartao = document.querySelector(".pagamento-card");
      if (cartao) cartao.scrollIntoView({ block: "start", behavior: "smooth" });
    }
  });

  if (elQuantidade) elQuantidade.addEventListener("input", function () {
    var v = elQuantidade.value.replace(/,/g, ".").replace(/[^0-9.]/g, "");
    var primeiroPonto = v.indexOf(".");
    if (primeiroPonto !== -1) {
      v = v.slice(0, primeiroPonto + 1) + v.slice(primeiroPonto + 1).replace(/\./g, "");
    }
    elQuantidade.value = v;
  });
  if (elTipo) elTipo.addEventListener("click", function (e) {
    var b = e.target.closest("[data-tipo]"); if (!b) return;
    if (estado === "combo-tipo") escolherTipoParaCombo(b.dataset.tipo);
    else escolherTipo(b.dataset.tipo);
  });
  if (elMaquina) elMaquina.addEventListener("click", function (e) {
    var b = e.target.closest("[data-maq]"); if (b) escolherMaquina(b.dataset.maq);
  });
  if (elValor) elValor.addEventListener("input", atualizarTroco);
  if (elComboValorInput) elComboValorInput.addEventListener("keydown", function (e) {
    // stopPropagation: confirmarValorCombo() pode mudar o estado pra "combo-dinheiro"
    // (que o dispatcher global tambem trata) dentro do mesmo evento — sem isso, o
    // Enter borbulha e dispara os dois handlers na mesma tecla.
    if (e.key === "Enter") { e.preventDefault(); e.stopPropagation(); confirmarValorCombo(); }
  });

  // ---------- Autocomplete de produtos ----------
  var elSug = document.getElementById("sugestoes");
  var elProdutoId = document.getElementById("produto_id");
  var sugItems = [];
  var sugIndex = -1;
  var debounce = null;

  function fecharSug() {
    sugItems = []; sugIndex = -1;
    if (elSug) { elSug.hidden = true; elSug.innerHTML = ""; }
    clearTimeout(debounce);  // cancela busca pendente (ex.: Enter logo apos digitar/bipar)
  }

  function submitItem() {
    if (formItem.requestSubmit) formItem.requestSubmit();
    else formItem.dispatchEvent(new Event("submit", { cancelable: true, bubbles: true }));
  }

  function escolherSug(idx) {
    var p = sugItems[idx];
    if (!p) return;
    elProdutoId.value = p.id;   // adiciona pelo id exato
    fecharSug();
    // O nome escolhido fica escrito na barra (pedido do dono), não só o que foi digitado.
    sairModoUltimo();
    codigo.value = p.nome;
    // Seleção deliberada via busca (ao contrário do bipe do leitor): pausa na
    // quantidade em vez de adicionar direto, já que aqui não há pressa de scanner.
    if (elQuantidade) { elQuantidade.value = "1"; elQuantidade.focus(); elQuantidade.select(); }
  }

  function cancelarSelecaoSugestao() {
    elProdutoId.value = "";
    if (elQuantidade) elQuantidade.value = "1";
    fecharSug();
    if (codigo) codigo.focus();
  }

  // Quantidade de 1 a 9.999: uma leitura de código de barras caindo neste campo
  // (8 a 14 dígitos) não pode virar quantidade (achado M2). O servidor confere de novo.
  function quantidadeValida() {
    var q = lerValor(elQuantidade.value);
    return q !== null && q > 0 && q <= 9999;
  }

  if (elQuantidade) elQuantidade.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
      e.preventDefault();
      if (!quantidadeValida()) {
        mostrarAlerta("Quantidade inválida (de 1 a 9.999).", "erro");
        elQuantidade.value = "1";
        elQuantidade.select();
        return;
      }
      submitItem();
    }
    else if (e.key === "Escape") { e.preventDefault(); cancelarSelecaoSugestao(); }
  });

  function renderSug(q) {
    if (!elSug) return;
    if (!sugItems.length) { fecharSug(); return; }
    elSug.innerHTML = sugItems.map(function (p, k) {
      var estoque = p.estoque > 0 ? (p.estoque + " " + escaparHtml(p.unidade)) : "sem estoque";
      return '<li data-idx="' + k + '" class="' + (k === sugIndex ? "ativo" : "") + '">' +
        '<span class="sug-nome">' + escaparHtml(p.nome) + "</span>" +
        '<span class="sug-info">' + formatBRL(p.preco) + " · " + estoque + "</span></li>";
    }).join("");
    elSug.hidden = false;
  }

  function buscarSugestoes() {
    var q = codigo.value.trim();
    if (q.length < 2) { fecharSug(); return; }
    fetch("/api/produtos?q=" + encodeURIComponent(q))
      .then(function (r) { return r.ok ? r.json() : []; })
      .then(function (lista) {
        sugItems = lista;
        // Auto-seleciona o 1º só quando é busca por texto (tem letra), não por código.
        sugIndex = (lista.length && /[a-zA-Z]/.test(q)) ? 0 : -1;
        renderSug(q);
      })
      .catch(function () { fecharSug(); });
  }

  if (elSug) {
    elSug.addEventListener("mousedown", function (e) {
      var li = e.target.closest("li[data-idx]");
      if (li) { e.preventDefault(); escolherSug(parseInt(li.dataset.idx, 10)); }
    });
  }

  // ---------- Barra mostrando o último produto lançado ----------
  // Depois de lançar um item, a barra mostra o nome dele (pedido do dono) em
  // "modo último produto": o texto fica todo selecionado e a primeira tecla —
  // inclusive a do leitor — apaga e começa do zero, então a leitura seguinte
  // nunca se junta à anterior (achado C3). Enter nesse modo vai para o pagamento,
  // como o campo vazio, sem lançar o produto de novo.
  function emModoUltimo() { return codigo && codigo.dataset.ultimo === "1"; }
  function sairModoUltimo() { if (codigo) delete codigo.dataset.ultimo; }
  function mostrarUltimoProduto(nome) {
    codigo.value = nome;
    codigo.dataset.ultimo = "1";
    codigo.focus();
    codigo.select();
  }

  // Resposta do /venda/item (substitui o hx-on que a CSP bloqueava): quantidade
  // volta para 1 e a barra mostra o item lançado, ou fica vazia se não entrou.
  document.body.addEventListener("htmx:afterRequest", function (evt) {
    if (!formItem || evt.detail.elt !== formItem) return;
    elProdutoId.value = "";
    if (elQuantidade) elQuantidade.value = "1";
    fecharSug();
    var tocado = document.querySelector("#carrinho tr[data-recem-bipado] td");
    if (evt.detail.successful && tocado) {
      mostrarUltimoProduto(tocado.textContent.trim());
    } else if (evt.detail.successful) {
      sairModoUltimo();
      codigo.value = "";
      codigo.focus();
    }
  });

  // A cada atualização da sacola (bipar, ✕, F3 +/−, repetir, desconto): (1) se o produto
  // mostrado na barra saiu da sacola, a barra fica vazia; (2) "Cancelar venda" só fica
  // ativo com item na sacola. O afterSwap vem antes do afterRequest acima, então um item
  // recém-bipado continua aparecendo normalmente.
  function sincronizarSacola() {
    var linhas = document.querySelectorAll("#carrinho table.itens tbody tr[data-item-id]");
    var btnCancelar = document.getElementById("btn-cancelar-venda");
    if (btnCancelar) btnCancelar.disabled = linhas.length === 0;
    if (!emModoUltimo()) return;
    var nomeNaBarra = codigo.value.trim();
    var aindaNaSacola = Array.prototype.some.call(linhas, function (tr) {
      var celula = tr.querySelector("td");
      return celula && celula.textContent.trim() === nomeNaBarra;
    });
    if (!aindaNaSacola) { sairModoUltimo(); codigo.value = ""; }
  }
  document.body.addEventListener("htmx:afterSwap", function (evt) {
    var alvo = evt.detail && evt.detail.target;
    if (alvo && alvo.id === "carrinho") sincronizarSacola();
  });

  // Leitor de código / busca: teclado.
  if (codigo) {
    codigo.focus();
    codigo.addEventListener("input", function () {
      sairModoUltimo();
      elProdutoId.value = "";
      if (modoCarrinho) sairNavegacaoCarrinho();
      clearTimeout(debounce);
      debounce = setTimeout(buscarSugestoes, 160);
    });

    function reselecionar() { if (emModoUltimo()) codigo.select(); }
    codigo.addEventListener("focus", reselecionar);
    codigo.addEventListener("mouseup", function (e) { if (emModoUltimo()) { e.preventDefault(); codigo.select(); } });

    codigo.addEventListener("keydown", function (e) {
      if (emModoUltimo()) {
        if (e.key === "Enter") { e.preventDefault(); fecharSug(); abrirPagamento(); return; }
        if (e.key === "Backspace" || e.key === "Delete") {
          e.preventDefault(); sairModoUltimo(); codigo.value = ""; return;
        }
        if (e.key.length === 1 && !e.ctrlKey && !e.metaKey && !e.altKey) {
          sairModoUltimo();
          codigo.value = "";  // a tecla em si entra normalmente logo depois
        }
      }
      var aberto = elSug && !elSug.hidden && sugItems.length;
      if (e.key === "ArrowDown" && aberto) {
        e.preventDefault(); sugIndex = Math.min(sugItems.length - 1, sugIndex + 1); renderSug(codigo.value);
        return;
      }
      if (e.key === "ArrowUp" && aberto) {
        e.preventDefault(); sugIndex = Math.max(0, sugIndex - 1); renderSug(codigo.value);
        return;
      }
      if (e.key === "Escape" && aberto) { e.preventDefault(); fecharSug(); return; }
      if (e.key === "Enter") {
        e.preventDefault();
        if (aberto && sugIndex >= 0) { escolherSug(sugIndex); return; }
        if (codigo.value.trim() === "") { fecharSug(); abrirPagamento(); return; }
        fecharSug();
        submitItem();  // leitor de código de barras / código digitado
      }
    });
  }

  // Voltar ao modo scanning sempre que um item é adicionado/removido.
  document.body.addEventListener("htmx:afterOnLoad", function (evt) {
    if (!evt.target || !evt.target.closest) return;
    if (evt.target.closest("#carrinho, #form-item")) {
      if (estado !== "scanning") voltarScanning();
      avisarBalcaoEstadoCarrinho();
    }
  });

  // Desconto (modal e "Tirar desconto") e cashback mudam o total sem mexer nos itens: a
  // Vitrine é avisada e a etapa de pagamento em que o operador está continua. Escuta o
  // afterSwap do #carrinho (que fica na página): "Tirar desconto" e os botões de cashback
  // são trocados pela própria resposta, e um evento disparado neles já não chega ao body.
  document.body.addEventListener("htmx:afterSwap", function (evt) {
    var elt = evt.detail && evt.detail.elt;
    if (elt && elt.closest && elt.closest("#form-desconto, #totais-detalhe, #cashback-info")) {
      avisarBalcaoEstadoCarrinho();
    }
  });


  // ---------- Desconto do balcão (F7) ----------
  // Regras no servidor (services/desconto.py): até R$ 1,00 livre; até R$ 2,00 com a senha de
  // quem opera; acima, senha de um administrador. Aqui só a prévia e o campo de senha certo.
  var DESCONTO_LIVRE = 1.0, DESCONTO_OPERADOR = 2.0;
  var modalDesconto = document.getElementById("modal-desconto");
  var formDesconto = document.getElementById("form-desconto");
  var elDescValor = document.getElementById("desconto-valor");
  var elDescRotulo = document.getElementById("desconto-rotulo-valor");
  var elDescPrevia = document.getElementById("desconto-previa");
  var elDescSenhaCampo = document.getElementById("desconto-senha-campo");
  var elDescSenhaRotulo = document.getElementById("desconto-senha-rotulo");
  var elDescSenha = document.getElementById("desconto-senha");
  var elDescErro = document.getElementById("desconto-erro");
  var btnDescConfirmar = document.getElementById("btn-desconto-confirmar");
  var btnDesconto = document.getElementById("btn-desconto");

  function descontoAberto() { return !!modalDesconto && !modalDesconto.hidden; }

  function baseDesconto() {
    var el = document.getElementById("totais-detalhe");
    return el ? (parseFloat(el.dataset.base) || 0) : 0;
  }

  function modoDesconto() {
    var r = formDesconto && formDesconto.querySelector('input[name="modo"]:checked');
    return r ? r.value : "pagar";
  }

  // Valor do desconto pelo que foi digitado (null = ainda inválido).
  function valorDesconto() {
    var base = baseDesconto();
    var v = lerValor(elDescValor.value);
    if (v === null) return null;
    var d = modoDesconto() === "pagar" ? base - v : v;
    d = Math.round(d * 100) / 100;
    return (d > 0 && d < base) ? d : null;
  }

  function atualizarPreviaDesconto() {
    var base = baseDesconto();
    var d = valorDesconto();
    elDescRotulo.textContent = modoDesconto() === "pagar"
      ? "Valor que o cliente vai pagar (R$)" : "Valor do desconto (R$)";
    if (d === null) {
      elDescPrevia.innerHTML = "Total atual: <b>" + formatBRL(base) + "</b>";
    } else {
      elDescPrevia.innerHTML = "Desconto de <b>" + formatBRL(d) + "</b> · o cliente paga <b>"
        + formatBRL(base - d) + "</b>";
    }
    var precisaSenha = d !== null && d > DESCONTO_LIVRE;
    elDescSenhaCampo.hidden = !precisaSenha;
    elDescSenha.required = precisaSenha;
    elDescSenhaRotulo.textContent = (d !== null && d > DESCONTO_OPERADOR)
      ? "Senha de um administrador (acima de R$ 2,00)" : "Sua senha (desconto acima de R$ 1,00)";
    btnDescConfirmar.disabled = d === null;
  }

  function abrirDesconto() {
    if (!modalDesconto) return;
    if (!temItens()) { mostrarAlerta("Adicione itens antes de dar desconto.", "erro"); return; }
    // Combinado em andamento já dividiu o total: desconto só antes de escolher o pagamento.
    if (["scanning", "documento", "tipo"].indexOf(estado) === -1) {
      mostrarAlerta("Desconto só antes de escolher a forma de pagamento (Esc para voltar).", "erro");
      return;
    }
    formDesconto.reset();
    elDescErro.hidden = true;
    modalDesconto.hidden = false;
    atualizarPreviaDesconto();
    requestAnimationFrame(function () { elDescValor.focus(); });
  }

  function fecharDesconto() {
    if (!modalDesconto) return;
    modalDesconto.hidden = true;
    if (elDescSenha) elDescSenha.value = "";
    if (estado === "scanning" && codigo) codigo.focus();
  }

  if (btnDesconto) btnDesconto.addEventListener("click", abrirDesconto);
  if (formDesconto) {
    formDesconto.addEventListener("input", atualizarPreviaDesconto);
    formDesconto.addEventListener("change", atualizarPreviaDesconto);
    document.getElementById("btn-desconto-cancelar").addEventListener("click", fecharDesconto);
  }
  document.body.addEventListener("descontoAplicado", function () {
    fecharDesconto();
    mostrarAlerta("Desconto aplicado e registrado.", "ok");
  });
  document.body.addEventListener("descontoRecusado", function (evt) {
    var msg = (evt.detail && evt.detail.mensagem) || "Desconto não aplicado.";
    if (descontoAberto()) {
      elDescErro.textContent = msg;
      elDescErro.hidden = false;
      elDescSenha.value = "";
      elDescSenha.focus();
    } else {
      mostrarAlerta(msg, "erro");
    }
  });

  function emCampoDeTexto() {
    var el = document.activeElement;
    if (!el) return false;
    var tag = el.tagName;
    return tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT";
  }

  // Teclado global do fluxo de pagamento + atalhos adicionais (US14).
  document.addEventListener("keydown", function (e) {
    // Câmera do celular aberta (camera-venda.js): as teclas são dela (quantidade, Enter, Esc).
    var telaCamera = document.getElementById("camera-venda");
    if (telaCamera && !telaCamera.hidden) return;
    // Painel de atalhos aberto: Esc fecha, tem prioridade sobre qualquer outra coisa.
    if (window._modalAtalhosAberto && window._modalAtalhosAberto()) {
      if (e.key === "Escape") { e.preventDefault(); window._alternarAtalhos(); }
      return;
    }
    // Modal de desconto aberto: só Esc (fecha); o resto é digitação no próprio formulário.
    if (descontoAberto()) {
      if (e.key === "Escape") { e.preventDefault(); fecharDesconto(); }
      return;
    }
    if (e.key === "F7") { e.preventDefault(); abrirDesconto(); return; }
    // "?" mostra/esconde os atalhos — só fora de campo de texto (não atrapalha digitação).
    if (e.key === "?" && !emCampoDeTexto()) { e.preventDefault(); window._alternarAtalhos(); return; }

    if (e.key === "F9") { e.preventDefault(); if (estado === "scanning") abrirPagamento(); return; }
    if (e.key === "F2") {  // Selecionar cliente cadastrado
      e.preventDefault();
      var cli = document.getElementById("cliente_id");
      if (cli) cli.focus();
      return;
    }
    if (e.key === "F3") { e.preventDefault(); if (estado === "scanning") ativarNavegacaoCarrinho(); return; }
    if (modoCarrinho) {
      if (e.key === "ArrowDown") { e.preventDefault(); moverSelecaoCarrinho(1); return; }
      if (e.key === "ArrowUp") { e.preventDefault(); moverSelecaoCarrinho(-1); return; }
      if (e.key === "+" || e.key === "=") { e.preventDefault(); ajustarQuantidadeSelecionada(1); return; }
      if (e.key === "-") { e.preventDefault(); ajustarQuantidadeSelecionada(-1); return; }
      if (e.key === "Delete" || e.key === "Backspace") { e.preventDefault(); removerItemSelecionado(); return; }
      if (e.key === "Escape") { e.preventDefault(); sairNavegacaoCarrinho(); return; }
    }
    if (e.key === "F4") {  // Repetir última venda
      e.preventDefault();
      var btnRepetir = document.getElementById("btn-repetir-venda");
      if (btnRepetir) btnRepetir.click();
      return;
    }
    if (e.key === "F6") {  // Abrir tela do cliente (Vitrine do Balcão)
      e.preventDefault();
      var btnTelaCliente = document.getElementById("btn-tela-cliente");
      if (btnTelaCliente) btnTelaCliente.click();
      return;
    }
    if (e.key === "F8") { e.preventDefault(); window.location.href = "/caixa"; return; }  // Abrir caixa
    if (e.ctrlKey && e.key.toLowerCase() === "l") {  // Cancelar venda / limpar carrinho (com ou sem Caps Lock)
      e.preventDefault();
      var btnCancelar = document.getElementById("btn-cancelar-venda");
      if (btnCancelar && btnCancelar.disabled) { mostrarAlerta("Não há venda para cancelar.", "erro"); return; }
      if (btnCancelar) btnCancelar.click();
      return;
    }
    if (e.key === "Escape") {
      if (estado === "maquina" || estado === "combo-maquina") { escolherMaquina("VOLTAR"); e.preventDefault(); }
      else if (estado === "combo-tipo" || estado === "combo-valor" || estado === "combo-dinheiro") {
        cancelarCombo(); e.preventDefault();
      }
      else if (estado === "documento-numero") { e.preventDefault(); voltarParaDocumento(); }
      else if (estado !== "scanning") { voltarScanning(); e.preventDefault(); }
      else if (codigo) { e.preventDefault(); codigo.focus(); }  // volta o foco pro código
      return;
    }
    if (estado === "documento") {
      var mapDoc = { "1": "NAO", "2": "CPF", "3": "CNPJ" };
      if (mapDoc[e.key]) { e.preventDefault(); escolherDocumento(mapDoc[e.key]); }
    } else if (estado === "tipo") {
      var mapTipo = { "1": "DINHEIRO", "2": "DEBITO", "3": "CREDITO", "4": "PIX", "5": "FIADO", "6": "COMBINADO" };
      if (mapTipo[e.key]) { e.preventDefault(); escolherTipo(mapTipo[e.key]); }
    } else if (estado === "combo-tipo") {
      var mapTipoCombo = { "1": "DINHEIRO", "2": "DEBITO", "3": "CREDITO", "4": "PIX", "5": "FIADO" };
      if (mapTipoCombo[e.key]) { e.preventDefault(); escolherTipoParaCombo(mapTipoCombo[e.key]); }
    } else if (estado === "maquina") {
      var mapMaq = { "1": "CIELO", "2": "STONE" };
      if (tipoPendente === "CREDITO") { mapMaq["3"] = "CIELO_PARCELADO"; mapMaq["4"] = "STONE_PARCELADO"; }
      if (mapMaq[e.key]) { e.preventDefault(); escolherMaquina(mapMaq[e.key]); }
    } else if (estado === "combo-maquina") {
      var mapMaqCombo = { "1": "CIELO", "2": "STONE" };
      if (comboFormaPendente === "CREDITO") { mapMaqCombo["3"] = "CIELO_PARCELADO"; mapMaqCombo["4"] = "STONE_PARCELADO"; }
      if (mapMaqCombo[e.key]) { e.preventDefault(); escolherMaquina(mapMaqCombo[e.key]); }
    } else if (estado === "ready") {
      if (e.key === "Enter") { e.preventDefault(); finalizar(); }
    } else if (estado === "dinheiro") {
      if (e.key === "Enter") { e.preventDefault(); finalizar(); }
    } else if (estado === "combo-dinheiro") {
      if (e.key === "Enter") { e.preventDefault(); confirmarDinheiroCombo(); }
    }
  });
});
