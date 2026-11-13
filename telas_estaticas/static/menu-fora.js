// Fecha menus/popups feitos com <details> (Conversas do assistente, Baixar ▾, ⋯ de ações) ao clicar fora
// ou apertar Esc. Vale para qualquer <details> marcado com .menu-acoes, .conversas-ia, .menu-fecha-fora.
(function () {
  var SEL = "details.menu-acoes[open], details.conversas-ia[open], details.menu-fecha-fora[open]";
  // pointerdown em vez de click: um clique em botão desabilitado não dispara "click" e o menu ficaria aberto.
  document.addEventListener("pointerdown", function (e) {
    Array.prototype.forEach.call(document.querySelectorAll(SEL), function (d) {
      if (!d.contains(e.target)) d.open = false;
    });
  }, true);
  // Botão "Cancelar" de formulários dentro de <details>: fecha o bloco (data-fecha-details).
  document.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest("[data-fecha-details]");
    var d = b && b.closest("details");
    if (d) { d.open = false; var f = b.closest("form"); if (f) f.reset(); }
  });
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    Array.prototype.forEach.call(document.querySelectorAll(SEL), function (d) { d.open = false; });
  });

  // Menu "Baixar ▾" / "⋯" dentro de tabela com rolagem: o absolute ficava cortado pela borda da área de
  // rolagem. Ao abrir, a lista passa a fixed no mesmo lugar onde abriria (mesmo alinhamento) e sobe
  // quando não cabe embaixo; rolar a página reposiciona.
  function dentroDeRolagem(el) {
    for (var p = el.parentElement; p && p !== document.body; p = p.parentElement) {
      var cs = getComputedStyle(p);
      if (cs.overflowX !== "visible" || cs.overflowY !== "visible") return true;
    }
    return false;
  }
  function soltar(d) {
    var lista = d.querySelector(":scope > .menu-acoes-lista");
    var summary = d.querySelector(":scope > summary");
    if (!lista || !summary) return;
    lista.classList.remove("menu-solto");
    lista.style.left = lista.style.top = "";
    if (!dentroDeRolagem(d)) return;
    var r = lista.getBoundingClientRect();  // onde o absolute abriria
    var s = summary.getBoundingClientRect();
    lista.classList.add("menu-solto");
    var esquerda = Math.max(8, Math.min(r.left, window.innerWidth - r.width - 8));
    var topo = s.bottom + 4;
    if (topo + r.height > window.innerHeight - 8 && s.top - 4 - r.height >= 8) topo = s.top - 4 - r.height;
    lista.style.left = esquerda + "px";
    lista.style.top = topo + "px";
  }
  document.addEventListener("toggle", function (e) {
    var d = e.target;
    if (d.matches && d.matches("details.menu-acoes") && d.open) soltar(d);
  }, true);
  window.addEventListener("scroll", function () {
    Array.prototype.forEach.call(document.querySelectorAll("details.menu-acoes[open]"), soltar);
  }, true);
  window.addEventListener("resize", function () {
    Array.prototype.forEach.call(document.querySelectorAll("details.menu-acoes[open]"), soltar);
  });
})();
