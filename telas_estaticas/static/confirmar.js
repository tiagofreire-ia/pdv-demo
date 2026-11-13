// Caixa de confirmação própria do sistema (substitui o confirm() do navegador).
(function () {
  var modal, msgEl, tituloEl, btnSim, btnNao, aoConfirmar = null, onKey = null;

  function elementos() {
    modal = document.getElementById("modal-confirmar");
    msgEl = document.getElementById("modal-confirmar-msg");
    tituloEl = document.getElementById("modal-confirmar-titulo");
    btnSim = document.getElementById("modal-confirmar-sim");
    btnNao = document.getElementById("modal-confirmar-nao");
  }

  function fechar() {
    if (modal) modal.hidden = true;
    if (onKey) { document.removeEventListener("keydown", onKey, true); onKey = null; }
    aoConfirmar = null;
  }

  function confirmar() {
    var cb = aoConfirmar;
    fechar();
    if (cb) cb();
  }

  // API global: window.confirmarAcao("mensagem", function(){ ...ação... }, {titulo, textoSim, textoNao})
  window.confirmarAcao = function (mensagem, callback, opts) {
    opts = opts || {};
    if (!modal) elementos();
    if (!modal) { if (window.confirm(mensagem)) callback(); return; } // fallback
    msgEl.textContent = mensagem;
    tituloEl.textContent = opts.titulo || "Confirmação";
    btnSim.textContent = opts.textoSim || "Sim, confirmar";
    btnNao.textContent = opts.textoNao || "Não";
    // "Sim" em vermelho (ação crítica) por padrão; estilo "primary" para confirmações comuns.
    btnSim.className = "btn " + (opts.estilo || "danger");
    aoConfirmar = callback;
    modal.hidden = false;
    btnSim.focus();

    onKey = function (e) {
      if (e.key === "Enter") { e.preventDefault(); confirmar(); }
      else if (e.key === "Escape") { e.preventDefault(); fechar(); }
    };
    document.addEventListener("keydown", onKey, true);
  };

  document.addEventListener("DOMContentLoaded", function () {
    elementos();
    if (btnSim) btnSim.addEventListener("click", confirmar);
    if (btnNao) btnNao.addEventListener("click", fechar);
    if (modal) modal.addEventListener("click", function (e) { if (e.target === modal) fechar(); });

    // Formulários com data-confirm: pede confirmação antes de enviar.
    document.querySelectorAll("form[data-confirm]").forEach(function (form) {
      form.addEventListener("submit", function (e) {
        if (form.dataset._confirmado === "1") { form.dataset._confirmado = ""; return; }
        e.preventDefault();
        // data-confirm-dinamico="nomeDaFuncao": a função recebe o form e devolve
        // {mensagem, titulo, textoSim} montados com o valor digitado (ex.: abertura
        // do caixa mostra o valor; retirada idem). Devolver null cancela o envio.
        var opcoes = {
          mensagem: form.getAttribute("data-confirm"),
          titulo: form.getAttribute("data-confirm-titulo") || "Confirmação",
          textoSim: form.getAttribute("data-confirm-texto-sim") || undefined,
          textoNao: form.getAttribute("data-confirm-texto-nao") || undefined,
          estilo: form.getAttribute("data-confirm-estilo") || undefined,
        };
        var dinamico = form.getAttribute("data-confirm-dinamico");
        if (dinamico && typeof window[dinamico] === "function") {
          var extra = window[dinamico](form);
          if (!extra) return;
          Object.keys(extra).forEach(function (k) { if (extra[k] !== undefined) opcoes[k] = extra[k]; });
        }
        window.confirmarAcao(opcoes.mensagem, function () {
          form.dataset._confirmado = "1";
          if (form.requestSubmit) form.requestSubmit(); else form.submit();
        }, opcoes);
      });
    });
  });

  // Regra do sistema todo (pedido do dono, 07–08/10): em formulário que GRAVA (method="post"),
  // Enter num campo NÃO envia — passa para o próximo campo; no último, fica onde está. Só o
  // botão grava (clique, ou Tab até ele e Enter — gesto intencional), e os que têm data-confirm
  // ainda pedem a confirmação. Vários Enter seguidos nunca gravam. Exceções com data-enter-envia: login, pergunta ao assistente e pagamento da
  // frente de caixa (fluxos de teclado próprios). Quem já trata o próprio Enter (leitor de
  // código de barras, busca com sugestões, contagem do inventário, esta caixa de confirmação)
  // chama preventDefault antes e fica como está.
  function gravaComBotao(form) {
    if (!form || form.hasAttribute("data-enter-envia")) return false;
    return (form.getAttribute("method") || "").toLowerCase() === "post" || form.hasAttribute("data-enter-avanca");
  }
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Enter" || e.defaultPrevented || e.isComposing) return;
    var alvo = e.target;
    if (!alvo || !gravaComBotao(alvo.form)) return;
    if (alvo.tagName === "TEXTAREA" || alvo.tagName === "BUTTON" || alvo.type === "submit" || alvo.type === "button") return;
    e.preventDefault();
    var form = alvo.form;
    var campos = Array.prototype.filter.call(form.querySelectorAll("input, select"), function (el) {
      return el.type !== "hidden" && !el.disabled && !el.readOnly && el.offsetParent !== null;
    });
    var i = campos.indexOf(alvo);
    if (i >= 0 && i < campos.length - 1) campos[i + 1].focus();
  });

  // HTMX: usa a nossa caixa no lugar do confirm() nativo quando há hx-confirm.
  document.addEventListener("htmx:confirm", function (e) {
    if (!e.detail.question) return;      // sem hx-confirm -> segue normal
    e.preventDefault();
    window.confirmarAcao(e.detail.question, function () { e.detail.issueRequest(true); });
  });
})();
