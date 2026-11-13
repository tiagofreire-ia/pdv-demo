// Tour guiado — sem dependências externas.
//
// Spec 011: o tour começa pelo "?" de ajuda da tela, passa pelas áreas marcadas da tela
// atual (formulários, campos, busca, listas e botões — atributos data-tour-tela +
// data-tour-text [+ data-tour-titulo]) e, no fim, pergunta se a pessoa quer ver o menu
// (itens com data-tour, como antes). Áreas dentro de <details> fechados são abertas para
// o destaque e fechadas de novo ao terminar.
(function () {
  var STORAGE_KEY = "tourVisto_v1";

  function visivel(el) {
    if (!el || el.closest("[hidden]")) return false;
    if (el.closest(".modal")) return false;
    // Alvo sem tamanho (ex.: escondido por CSS no celular) não pode ser destacado. Só vale para o que NÃO está dentro
    // de um <details> fechado: esses o tour abre sozinho antes de destacar.
    if (el.tagName !== "DETAILS" && !el.closest("details:not([open])") && el.getClientRects().length === 0) return false;
    return true;
  }

  function passoAjuda() {
    var el = document.querySelector(".ajuda-contexto");
    if (!visivel(el)) return [];
    return [{
      el: el,
      titulo: "Ajuda desta tela (?)",
      texto: "O ? no canto de cada tela abre o guia daquela tela: passo a passo, dicas e exemplos de pedidos para o assistente de IA.",
    }];
  }

  function passosTela() {
    return Array.prototype.slice.call(document.querySelectorAll("[data-tour-tela]"))
      .filter(visivel)
      .map(function (el) {
        return {
          el: el,
          titulo: el.getAttribute("data-tour-titulo") || (el.querySelector("summary, h2, h3") || el).textContent.trim().slice(0, 60),
          texto: el.getAttribute("data-tour-text") || "",
        };
      });
  }

  function passosMenu() {
    return Array.prototype.slice.call(document.querySelectorAll(".sidebar [data-tour]")).map(function (el) {
      return {
        el: el,
        titulo: el.getAttribute("data-tour-titulo") || el.textContent.trim(),
        texto: el.getAttribute("data-tour-text") || el.textContent.trim(),
      };
    });
  }

  function iniciarTour() {
    var steps = passoAjuda().concat(passosTela());
    var menu = passosMenu();
    var perguntouMenu = false;
    if (!steps.length) { steps = menu; perguntouMenu = true; }
    if (!steps.length) return;
    var i = 0;
    var abertos = [];  // <details> abertos pelo tour, fechados ao terminar

    var overlay = document.createElement("div");
    overlay.className = "tour-overlay";
    var balao = document.createElement("div");
    balao.className = "tour-balao";
    balao.setAttribute("role", "dialog");
    // Balão numa camada própria, acima do elemento destacado: dentro do overlay ele ficava
    // por baixo de áreas grandes (ex.: formulário de cadastro aberto).
    document.body.appendChild(overlay);
    document.body.appendChild(balao);

    // Celular/tablet (até 900 px o menu é uma gaveta): a gaveta abre só nos passos do menu —
    // fechada, os itens do menu não aparecem; aberta, ela cobre a tela nos passos da tela.
    function gaveta(abrir) {
      if (window.innerWidth > 900) return;
      var html = document.documentElement;
      if (html.classList.contains("sidebar-mobile-open") === abrir) return;
      html.classList.toggle("sidebar-mobile-open", abrir);
      window.dispatchEvent(new Event("resize"));  // atualiza o ☰/✕ (base.html)
    }

    var alvoAtual = null;
    function limparAlvo() {
      if (alvoAtual) { alvoAtual.classList.remove("tour-alvo"); alvoAtual = null; }
    }

    function abrirDetalhes(el) {
      var d = el.tagName === "DETAILS" ? el : null;
      var cadeia = [];
      if (d) cadeia.push(d);
      var p = el.parentElement ? el.parentElement.closest("details") : null;
      while (p) { cadeia.push(p); p = p.parentElement ? p.parentElement.closest("details") : null; }
      cadeia.forEach(function (det) {
        if (!det.open) { det.open = true; abertos.push(det); }
      });
    }

    function escapar(t) {
      var div = document.createElement("div");
      div.textContent = t;
      return div.innerHTML;
    }

    function posicionar(el) {
      requestAnimationFrame(function () {
        var r = el.getBoundingClientRect();
        var bw = balao.offsetWidth || 320;
        var bh = balao.offsetHeight || 150;
        var top = r.bottom + 10;
        if (top + bh > window.innerHeight - 10) top = r.top - bh - 10; // acima, se não couber
        if (top < 10) top = Math.min(window.innerHeight - bh - 10, Math.max(10, r.top + 10)); // alvo grande
        top = Math.max(10, Math.min(top, window.innerHeight - bh - 10));
        var left = Math.max(10, Math.min(r.left, window.innerWidth - bw - 10));
        balao.style.top = top + "px";
        balao.style.left = left + "px";
      });
    }

    function render() {
      limparAlvo();
      var passo = steps[i];
      var el = passo.el;
      gaveta(!!el.closest(".sidebar"));
      abrirDetalhes(el);
      el.classList.add("tour-alvo");
      alvoAtual = el;
      el.scrollIntoView({ block: el.offsetHeight > window.innerHeight * 0.6 ? "start" : "center", inline: "nearest" });

      var ultimo = i === steps.length - 1;
      var botaoFinal;
      if (ultimo && !perguntouMenu && menu.length) {
        botaoFinal = '<button type="button" class="btn mini" data-t="fim">Concluir</button>' +
          '<button type="button" class="btn primary mini" data-t="menu">Ver o menu também</button>';
      } else {
        botaoFinal = '<button type="button" class="btn primary mini" data-t="prox">' + (ultimo ? "Concluir" : "Próximo") + "</button>";
      }
      balao.innerHTML =
        '<div class="tour-passo">' + (i + 1) + " de " + steps.length + "</div>" +
        "<h3>" + escapar(passo.titulo) + "</h3>" +
        "<p>" + escapar(passo.texto) + "</p>" +
        '<div class="tour-botoes">' +
        '<button type="button" class="btn ghost mini" data-t="pular">Pular</button>' +
        '<span style="flex:1"></span>' +
        (i > 0 ? '<button type="button" class="btn mini" data-t="ant">Anterior</button>' : "") +
        botaoFinal +
        "</div>";
      posicionar(el);
    }

    function fechar() {
      limparAlvo();
      gaveta(false);
      abertos.forEach(function (d) { d.open = false; });
      overlay.remove();
      balao.remove();
      document.removeEventListener("keydown", onKey);
      try { localStorage.setItem(STORAGE_KEY, "1"); } catch (e) {}
    }

    function irParaMenu() {
      perguntouMenu = true;
      steps = steps.concat(menu);
      i = i + 1;
      render();
    }

    function avancar() {
      if (i === steps.length - 1) {
        if (!perguntouMenu && menu.length) return irParaMenu();
        return fechar();
      }
      i += 1;
      render();
    }

    function aoClicar(e) {
      var t = e.target.getAttribute && e.target.getAttribute("data-t");
      if (t === "pular" || t === "fim") return fechar();
      if (t === "menu") return irParaMenu();
      if (t === "ant") { i = Math.max(0, i - 1); return render(); }
      if (t === "prox") return avancar();
      if (e.target === overlay) fechar(); // clicar fora fecha
    }
    overlay.addEventListener("click", aoClicar);
    balao.addEventListener("click", aoClicar);

    function onKey(e) {
      if (!document.body.contains(overlay)) { document.removeEventListener("keydown", onKey); return; }
      if (e.key === "Escape") { e.preventDefault(); fechar(); }
      else if (e.key === "ArrowRight" || e.key === "Enter") { e.preventDefault(); avancar(); }
      else if (e.key === "ArrowLeft") { e.preventDefault(); i = Math.max(0, i - 1); render(); }
    }
    document.addEventListener("keydown", onKey);
    window.addEventListener("resize", function () { if (alvoAtual) posicionar(alvoAtual); });

    render();
  }

  document.addEventListener("DOMContentLoaded", function () {
    var btn = document.getElementById("btn-tour");
    if (btn) btn.addEventListener("click", iniciarTour);
    // O tour NÃO abre mais sozinho (não trava a tela). Use o botão "Tour guiado".
  });
})();
