// Máscara de valor em R$ para campos de dinheiro (Caixa, Entradas, Patrimônio).
// Digita só números, tratados como centavos (ex.: "150" vira "R$ 1,50", "15000" vira
// "R$ 150,00") — mesmo padrão usado em maquininha de cartão e apps de banco, sem
// ambiguidade sobre onde fica a vírgula decimal.
//
// O campo mostra "R$ 1.234,56" pro usuário, mas manda "1234.56" (número puro) pro
// servidor no momento do submit — o backend continua recebendo float normalmente.
function aplicarMascaraReal(el) {
  function centavosParaTexto(centavos) {
    var valor = (centavos / 100).toLocaleString("pt-BR", {
      minimumFractionDigits: 2, maximumFractionDigits: 2,
    });
    return "R$ " + valor;
  }

  function textoParaCentavos(str) {
    var digitos = (str || "").replace(/\D/g, "");
    return digitos ? parseInt(digitos, 10) : 0;
  }

  // Valor inicial (renderizado pelo servidor, ex.: "45.5") formatado como R$.
  var inicial = parseFloat(el.value || "0") || 0;
  el.value = centavosParaTexto(Math.round(inicial * 100));
  el.setAttribute("inputmode", "numeric");
  el.setAttribute("autocomplete", "off");

  // Teto em reais (data-max, spec 011): dígito que passaria do teto é ignorado.
  var tetoCentavos = el.dataset.max ? Math.round(parseFloat(el.dataset.max) * 100) : null;
  var ultimoValido = textoParaCentavos(el.value);
  el.addEventListener("input", function () {
    var centavos = textoParaCentavos(el.value);
    if (tetoCentavos !== null && !isNaN(tetoCentavos) && centavos > tetoCentavos) centavos = ultimoValido;
    ultimoValido = centavos;
    el.value = centavosParaTexto(centavos);
    el.setSelectionRange(el.value.length, el.value.length);
  });

  var form = el.closest("form");
  if (form) {
    form.addEventListener("submit", function (e) {
      // Envio segurado pela caixa de confirmação (confirmar.js registra antes):
      // o campo continua em R$ até o envio de verdade.
      if (e.defaultPrevented) return;
      var centavos = textoParaCentavos(el.value);
      el.value = (centavos / 100).toFixed(2);
    });
    // Botão "Cancelar" (type=reset) devolve o valor bruto original (ex.: "45.5"),
    // sem o "R$" — reaplica a máscara depois que o navegador termina o reset.
    form.addEventListener("reset", function () {
      setTimeout(function () {
        var valor = parseFloat(el.value || "0") || 0;
        el.value = centavosParaTexto(Math.round(valor * 100));
      }, 0);
    });
  }
}

// Campo de quantidade (contagem de inventário, etc.): só dígitos + no máximo um ponto
// decimal, nunca vírgula — evita o comportamento confuso do <input type=number> nativo
// (mesmo problema já corrigido no campo de quantidade da frente de caixa).
function aplicarMascaraQuantidade(el) {
  el.setAttribute("inputmode", "decimal");
  el.setAttribute("autocomplete", "off");
  el.addEventListener("input", function () {
    var v = el.value.replace(/,/g, ".").replace(/[^0-9.]/g, "");
    var primeiroPonto = v.indexOf(".");
    if (primeiroPonto !== -1) {
      v = v.slice(0, primeiroPonto + 1) + v.slice(primeiroPonto + 1).replace(/\./g, "");
    }
    el.value = v;
  });
}

// Campo de número inteiro (estoque de produto): só dígitos, sem vírgula nem ponto, e
// limitado ao maxlength do campo pra ninguém digitar um valor absurdo.
function aplicarMascaraInteiro(el) {
  el.setAttribute("inputmode", "numeric");
  el.setAttribute("autocomplete", "off");
  el.addEventListener("focus", function () { el.select(); });
  el.addEventListener("input", function () {
    var v = el.value.replace(/\D/g, "").replace(/^0+(?=\d)/, "");
    var max = parseInt(el.getAttribute("maxlength"), 10);
    if (max > 0) v = v.slice(0, max);
    el.value = v;
  });
}

// Telefone brasileiro: (11) 91234-5678 (celular, 11 dígitos) ou (11) 1234-5678
// (fixo, 10 dígitos) — formata conforme a quantidade de dígitos já digitados,
// mesmo padrão em qualquer cadastro que tenha campo de telefone (Clientes,
// Fornecedores).
function aplicarMascaraTelefone(el) {
  el.setAttribute("inputmode", "tel");
  el.setAttribute("autocomplete", "off");
  el.setAttribute("maxlength", "15");

  function formatar(valor) {
    var v = (valor || "").replace(/\D/g, "").slice(0, 11);
    if (v.length <= 2) return v.replace(/^(\d*)/, "($1");
    if (v.length <= 6) return v.replace(/^(\d{2})(\d*)/, "($1) $2");
    if (v.length <= 10) return v.replace(/^(\d{2})(\d{4})(\d*)/, "($1) $2-$3");
    return v.replace(/^(\d{2})(\d{5})(\d*)/, "($1) $2-$3");
  }

  if (el.value) el.value = formatar(el.value);
  el.addEventListener("input", function () {
    var pos = el.selectionStart;
    var antes = el.value.length;
    el.value = formatar(el.value);
    var depois = el.value.length;
    el.setSelectionRange(pos + (depois - antes), pos + (depois - antes));
  });
}

// CPF/CNPJ (spec 011): até 11 dígitos formata como CPF (000.000.000-00), de 12 a 14
// como CNPJ (00.000.000/0000-00). data-mascara-documento="cnpj" força CNPJ (fornecedor).
// No cliente, ajusta o "Tipo" do mesmo formulário (PF/PJ) conforme o que foi digitado,
// para o servidor não recusar um CNPJ como "CPF inválido".
function formatarDocumento(valor, soCnpj) {
  var v = (valor || "").replace(/\D/g, "").slice(0, 14);
  if (!soCnpj && v.length <= 11) {
    return v.replace(/^(\d{3})(\d)/, "$1.$2").replace(/^(\d{3})\.(\d{3})(\d)/, "$1.$2.$3")
      .replace(/\.(\d{3})(\d{1,2})$/, ".$1-$2");
  }
  return v.replace(/^(\d{2})(\d)/, "$1.$2").replace(/^(\d{2})\.(\d{3})(\d)/, "$1.$2.$3")
    .replace(/\.(\d{3})(\d)/, ".$1/$2").replace(/(\d{4})(\d{1,2})$/, "$1-$2");
}

function aplicarMascaraDocumento(el) {
  var soCnpj = el.dataset.mascaraDocumento === "cnpj";
  el.setAttribute("inputmode", "numeric");
  el.setAttribute("autocomplete", "off");
  el.setAttribute("maxlength", "18");
  var tipo = el.form ? el.form.querySelector('select[name="tipo"]') : null;
  function ajustar(doUsuario) {
    el.value = formatarDocumento(el.value, soCnpj);
    if (tipo && doUsuario) {
      var n = el.value.replace(/\D/g, "").length;
      if (n >= 12) tipo.value = "PJ";
      else if (n > 0) tipo.value = "PF";
    }
  }
  if (el.value) ajustar(false);
  el.addEventListener("input", function () { ajustar(true); });
}

// Nº do lote (spec 011): só letras, números, hífen, ponto e barra, em maiúsculas.
function aplicarMascaraLote(el) {
  el.setAttribute("autocomplete", "off");
  if (!el.getAttribute("maxlength")) el.setAttribute("maxlength", "20");
  el.addEventListener("input", function () {
    var max = parseInt(el.getAttribute("maxlength"), 10) || 20;
    el.value = el.value.toUpperCase().replace(/[^A-Z0-9./-]/g, "").slice(0, max);
  });
}

// Contador de caracteres (observações): "restam N caracteres" embaixo do campo.
function aplicarContador(el) {
  var max = parseInt(el.getAttribute("maxlength"), 10);
  if (!max) return;
  var aviso = document.createElement("small");
  aviso.className = "contador muted";
  el.insertAdjacentElement("afterend", aviso);
  function atualizar() {
    var resta = max - el.value.length;
    aviso.textContent = "restam " + resta + " caractere" + (resta === 1 ? "" : "s");
    aviso.classList.toggle("contador-fim", resta <= 10);
  }
  el.addEventListener("input", atualizar);
  if (el.form) el.form.addEventListener("reset", function () { setTimeout(atualizar, 0); });
  atualizar();
}

// Datas (spec 011): o navegador deixa digitar ano com 5 ou 6 dígitos (ex.: 275760).
// Fora da faixa min/max o campo fica inválido com a mensagem da faixa — o envio é
// barrado pelo navegador, e o servidor recusa de novo se chegar assim mesmo.
function dataBr(iso) {
  var p = (iso || "").split("-");
  return p.length === 3 ? p[2] + "/" + p[1] + "/" + p[0] : iso;
}

function aplicarFaixaData(el) {
  function conferir() {
    var v = el.value;
    var msg = "";
    if (v) {
      var ano = v.split("-")[0];
      if (ano.length !== 4 || (el.min && v < el.min) || (el.max && v > el.max)) {
        msg = el.min && el.max
          ? "Use uma data entre " + dataBr(el.min) + " e " + dataBr(el.max) + "."
          : "Data inválida.";
      }
    }
    el.setCustomValidity(msg);
    return msg;
  }
  // Durante a digitação só marca o campo (spec 012, S2): o balão de erro aparecia no meio
  // do ano (ex.: "0002" já é uma data completa, fora da faixa), tirava o foco e embaralhava
  // os dígitos. O aviso aparece ao sair do campo.
  el.addEventListener("change", conferir);
  el.addEventListener("blur", function () { if (conferir()) el.reportValidity(); });
}

// Filtro de data que filtra sozinho (Logs, Painel) — spec 012, S2: antes o formulário era
// enviado a cada dígito do ano (onchange), recarregando a página no meio da digitação.
// Agora só envia ao sair do campo com uma data completa, válida e diferente da inicial;
// Enter e o botão do formulário continuam funcionando normalmente.
function aplicarEnviarAoSair(el) {
  var inicial = el.value;
  function enviar(forcar) {
    var v = el.value;
    if ((!forcar && v === inicial) || !el.form) return;
    if (v && (v.split("-")[0].length !== 4 || !el.checkValidity())) return;
    inicial = v;
    if (el.form.requestSubmit) el.form.requestSubmit(); else el.form.submit();
  }
  el.addEventListener("blur", function () { enviar(false); });
  // No Chrome o campo de data não envia o formulário com Enter: envia aqui.
  var ultimaTecla = 0;
  el.addEventListener("keydown", function (e) {
    ultimaTecla = Date.now();
    if (e.key === "Enter") { e.preventDefault(); enviar(true); }
  });
  // Dia escolhido no calendário (sem tecla agora há pouco): envia na hora, sem esperar o campo perder o foco.
  // Digitando, continua esperando o blur/Enter para não recarregar a cada número.
  el.addEventListener("change", function () {
    if (Date.now() - ultimaTecla > 400) enviar(false);
  });
}

// Mostrar/esconder senha (Usuários): botão de olho ao lado do campo.
function aplicarMostrarSenha(el) {
  var embrulho = document.createElement("span");
  embrulho.className = "campo-com-olho";
  el.parentNode.insertBefore(embrulho, el);
  embrulho.appendChild(el);
  var botao = document.createElement("button");
  botao.type = "button";
  botao.className = "btn-olho";
  botao.setAttribute("aria-label", "Mostrar senha");
  botao.title = "Mostrar senha";
  botao.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>';
  botao.addEventListener("click", function () {
    var mostrar = el.type === "password";
    el.type = mostrar ? "text" : "password";
    botao.setAttribute("aria-label", mostrar ? "Esconder senha" : "Mostrar senha");
    botao.title = mostrar ? "Esconder senha" : "Mostrar senha";
    botao.classList.toggle("ativo", mostrar);
  });
  embrulho.appendChild(botao);
}

document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("[data-mascara-documento]").forEach(aplicarMascaraDocumento);
  document.querySelectorAll("[data-mascara-lote]").forEach(aplicarMascaraLote);
  document.querySelectorAll("[data-contador]").forEach(aplicarContador);
  document.querySelectorAll('input[type="date"]').forEach(aplicarFaixaData);
  document.querySelectorAll("[data-mostrar-senha]").forEach(aplicarMostrarSenha);
  document.querySelectorAll("[data-enviar-ao-sair]").forEach(aplicarEnviarAoSair);
  document.querySelectorAll("[data-mascara-real]").forEach(aplicarMascaraReal);
  document.querySelectorAll("[data-mascara-quantidade]").forEach(aplicarMascaraQuantidade);
  document.querySelectorAll("[data-mascara-inteiro]").forEach(aplicarMascaraInteiro);
  document.querySelectorAll("[data-mascara-telefone]").forEach(aplicarMascaraTelefone);
});
