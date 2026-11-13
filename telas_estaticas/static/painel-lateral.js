// Painel lateral de cadastro/edição (docs/10, 3.5): o mesmo de Produtos, reaproveitado em Clientes e Fornecedores.
//
//   <div class="painel-fundo" id="painel-fundo" hidden></div>
//   <aside class="painel-dialogo" data-painel data-abrir="1|" data-editando="1|" data-voltar="/lista" hidden> …
//     #btn-fechar-painel, #btn-cancelar-painel, <form id="form-painel">
//   <button data-abre-painel>…  (abre o painel)
//
// Esc fecha (menos com a confirmação ou outro modal aberto); o foco vai para o campo Nome ao abrir; na edição, fechar
// volta para a lista (que já está atrás do painel). Em "data-validar-cnpj", valida ao sair do campo.
(function () {
  var painel = document.querySelector("[data-painel]");
  var fundo = document.getElementById("painel-fundo");
  if (!painel || !fundo) return;
  var editando = painel.getAttribute("data-editando") === "1";
  var voltar = painel.getAttribute("data-voltar") || window.location.pathname;
  var form = document.getElementById("form-painel");

  function abrir() {
    painel.hidden = false;
    fundo.hidden = false;
    document.body.classList.add("painel-aberto");
    var primeiro = painel.querySelector("[data-foco]") || painel.querySelector('input[name="nome"]');
    if (primeiro) setTimeout(function () { primeiro.focus(); }, 30);
  }
  function fechar() {
    if (editando) { window.location.href = voltar; return; }
    painel.hidden = true;
    fundo.hidden = true;
    document.body.classList.remove("painel-aberto");
    if (form) form.reset();
  }

  window.painelLateral = { abrir: abrir, fechar: fechar };
  Array.prototype.forEach.call(document.querySelectorAll("[data-abre-painel]"), function (b) { b.addEventListener("click", abrir); });
  var btnFechar = document.getElementById("btn-fechar-painel");
  var btnCancelar = document.getElementById("btn-cancelar-painel");
  if (btnFechar) btnFechar.addEventListener("click", fechar);
  if (btnCancelar) btnCancelar.addEventListener("click", fechar);
  fundo.addEventListener("click", fechar);
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape" || e.defaultPrevented || painel.hidden) return;
    var confirmar = document.getElementById("modal-confirmar");
    if (confirmar && !confirmar.hidden) return;
    fechar();
  });
  if (painel.getAttribute("data-abrir") === "1") abrir();

  // Blocos "sob demanda" (ex.: Juntar cadastros).
  Array.prototype.forEach.call(document.querySelectorAll("[data-abre]"), function (b) {
    b.addEventListener("click", function () {
      var alvo = document.getElementById(b.getAttribute("data-abre"));
      if (!alvo) return;
      alvo.open = true;
      alvo.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  });

  // CNPJ: valida ao sair do campo (mesma conta do servidor, services/documento.py).
  function cnpjValido(d) {
    if (d.length !== 14 || /^(\d)\1{13}$/.test(d)) return false;
    function digito(base, pesos) {
      var soma = 0;
      for (var i = 0; i < pesos.length; i++) soma += parseInt(base.charAt(i), 10) * pesos[i];
      var r = soma % 11;
      return r < 2 ? 0 : 11 - r;
    }
    var p1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2], p2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
    return digito(d.slice(0, 12), p1) === parseInt(d.charAt(12), 10) && digito(d.slice(0, 13), p2) === parseInt(d.charAt(13), 10);
  }
  Array.prototype.forEach.call(document.querySelectorAll("[data-validar-cnpj]"), function (campo) {
    var aviso = document.getElementById(campo.getAttribute("aria-describedby") || "");
    function checar() {
      var digitos = campo.value.replace(/\D/g, ""), msg = "";
      if (digitos && digitos.length < 14) msg = "CNPJ incompleto: faltam números.";
      else if (digitos && !cnpjValido(digitos)) msg = "CNPJ inválido.";
      campo.classList.toggle("pf-invalido", !!msg);
      campo.setAttribute("aria-invalid", msg ? "true" : "false");
      campo.setCustomValidity(msg);
      if (aviso) { aviso.textContent = msg; aviso.hidden = !msg; }
    }
    campo.addEventListener("blur", checar);
    campo.addEventListener("input", function () { if (campo.classList.contains("pf-invalido")) checar(); });
    if (campo.value) checar();
  });
})();
