// Menu de ações (⋮) nas linhas de tabela de listagem (Produtos, Clientes,
// Fornecedores, Contas a Pagar, Patrimônio, Usuários, Inventário) — substitui os
// links de texto soltos ("editar | excluir") por um menu único, mesmo padrão do
// "..." do chat do assistente. Delegado no document: funciona em qualquer tabela
// que use esse HTML, sem precisar de JS por página.
//
// O menu é position:fixed, posicionado pelo botão na hora de abrir: a tabela tem
// overflow:hidden (cantos arredondados) e, com poucas linhas (ex.: busca com um
// resultado só), um menu absolute ficava cortado sem espaço pra aparecer. Se não
// couber embaixo do botão, abre pra cima.
(function () {
  function fecharTodos() {
    document.querySelectorAll(".tabela-menu-lista").forEach(function (l) { l.hidden = true; });
  }

  function posicionar(btn, lista) {
    var r = btn.getBoundingClientRect();
    var margem = 4;
    var largura = lista.offsetWidth;
    var altura = lista.offsetHeight;
    var esquerda = Math.max(8, Math.min(r.right - largura, window.innerWidth - largura - 8));
    var topo = r.bottom + margem;
    if (topo + altura > window.innerHeight - 8 && r.top - margem - altura >= 8) {
      topo = r.top - margem - altura;
    }
    lista.style.left = esquerda + "px";
    lista.style.top = topo + "px";
  }

  document.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-tabela-menu-btn]");
    if (btn) {
      var lista = btn.nextElementSibling;
      var jaAberto = lista && !lista.hidden;
      fecharTodos();
      if (lista && !jaAberto) {
        lista.hidden = false;
        posicionar(btn, lista);
      }
      return;
    }
    if (!e.target.closest(".tabela-menu-wrap")) fecharTodos();
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") fecharTodos();
  });
  // Caixas de ação com senha/formulário dentro de uma linha (details.cancelar-venda:
  // excluir, cancelar venda, editar entrada) — spec 011, bug U4: na última linha o
  // formulário ficava cortado pelo overflow:hidden da tabela. Ao abrir, passa a fixed,
  // posicionado pelo summary e aberto para cima quando não cabe embaixo. O mesmo vale
  // para o "Excluir" com senha dentro do menu ⋮ (details.menu-senha): o menu cresce e é
  // reposicionado para continuar inteiro na tela.
  function posicionarCaixa(details) {
    var form = details.querySelector(":scope > form");
    var summary = details.querySelector(":scope > summary");
    if (!form || !summary) return;
    form.classList.add("caixa-flutuante");
    var r = summary.getBoundingClientRect();
    var largura = form.offsetWidth;
    var altura = form.offsetHeight;
    var esquerda = Math.max(8, Math.min(r.right - largura, window.innerWidth - largura - 8));
    var topo = r.bottom + 6;
    if (topo + altura > window.innerHeight - 8) topo = Math.max(8, r.top - 6 - altura);
    form.style.left = esquerda + "px";
    form.style.top = topo + "px";
  }

  function fecharCaixas(exceto) {
    document.querySelectorAll("details.cancelar-venda[open]").forEach(function (d) {
      if (d !== exceto) d.open = false;
    });
  }

  document.addEventListener("toggle", function (e) {
    var d = e.target;
    if (!d.matches) return;
    if (d.matches("details.cancelar-venda") && d.open) {
      fecharCaixas(d);
      posicionarCaixa(d);
      var campo = d.querySelector('input[type="password"], input:not([type="hidden"]), select');
      if (campo) campo.focus({ preventScroll: true });
    } else if (d.matches("details.menu-senha")) {
      var lista = d.closest(".tabela-menu-lista");
      var btn = lista && lista.previousElementSibling;
      if (lista && btn) posicionar(btn, lista);
      if (d.open) {
        var senha = d.querySelector('input[type="password"]');
        if (senha) senha.focus({ preventScroll: true });
      }
    }
  }, true);

  document.addEventListener("click", function (e) {
    if (!e.target.closest("details.cancelar-venda")) fecharCaixas(null);
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") fecharCaixas(null);
  });

  // Fixed não acompanha a rolagem: fecha em vez de deixar o menu "solto" na tela.
  function aoRolar(e) {
    // Rolar dentro da própria caixa/menu (ex.: lista longa) não fecha.
    if (e && e.target && e.target.closest && e.target.closest(".tabela-menu-lista, .caixa-flutuante")) return;
    fecharTodos();
    fecharCaixas(null);
  }
  window.addEventListener("scroll", aoRolar, true);
  window.addEventListener("resize", aoRolar);
})();
