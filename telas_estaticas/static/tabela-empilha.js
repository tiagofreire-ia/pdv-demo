// Tabelas das listas (.pr-tabela e .rl-tabela) viram cartões empilhados no celular: copia o título de cada coluna
// para o atributo data-rotulo das células; o CSS (max-width: 700px) mostra "Rótulo ... valor" em cada linha.
(function () {
  function preparar(tabela) {
    var ths = tabela.querySelectorAll("thead th");
    var titulos = Array.prototype.map.call(ths, function (th) { return th.textContent.trim(); });
    if (!titulos.length) return;
    tabela.classList.add("empilha");
    Array.prototype.forEach.call(tabela.querySelectorAll("tbody tr"), function (tr) {
      Array.prototype.forEach.call(tr.children, function (td, i) {
        if (td.hasAttribute("colspan") || td.hasAttribute("data-rotulo")) return;
        var th = ths[i];
        // Coluna de ações (⋯, Cupom): sem rótulo; vai para o canto do cartão.
        if (th && (th.classList.contains("pr-acao") || /^a[cç][oõ]es$/i.test(titulos[i]))) { td.classList.add("pr-acao"); return; }
        if (titulos[i]) td.setAttribute("data-rotulo", titulos[i]);
      });
    });
  }
  function varrer(raiz) { Array.prototype.forEach.call((raiz || document).querySelectorAll("table.pr-tabela, table.rl-tabela"), preparar); }
  varrer();
  document.addEventListener("htmx:afterSwap", function (e) { varrer(e.target); });
})();
