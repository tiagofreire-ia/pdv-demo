// Campo de busca com sugestões (spec 011): escolhe produto ou fornecedor digitando parte do
// nome ou bipando o código, em vez de uma lista suspensa com milhares de opções.
//
// HTML:
//   <span class="busca-sugestao" data-busca-sugestao="produtos|fornecedores">
//     <input type="text" class="bs-texto" value="Nome atual">
//     <input type="hidden" name="produto_id" value="12">
//   </span>
//
// Delegado no document: funciona em linhas clonadas (ex.: "+ Adicionar item" da entrada).
(function () {
  var ESPERA_MS = 200;
  var timers = new WeakMap();
  var pedidos = new WeakMap();

  function partes(wrap) {
    return {
      texto: wrap.querySelector(".bs-texto"),
      id: wrap.querySelector('input[type="hidden"]'),
      lista: wrap.querySelector(".sugestoes"),
    };
  }

  function fechar(wrap) {
    var l = wrap.querySelector(".sugestoes");
    if (l) l.remove();
  }

  function rotulo(tipo, item) {
    if (tipo === "produtos") return item.codigo_barras ? item.codigo_barras : "";
    return item.cnpj || "";
  }

  function mostrar(wrap, itens) {
    fechar(wrap);
    var tipo = wrap.dataset.buscaSugestao;
    var ul = document.createElement("ul");
    ul.className = "sugestoes";
    ul.setAttribute("role", "listbox");
    if (!itens.length) {
      var vazio = document.createElement("li");
      vazio.className = "sug-vazio";
      vazio.textContent = "Nada encontrado.";
      ul.appendChild(vazio);
    }
    itens.forEach(function (item, i) {
      var li = document.createElement("li");
      li.setAttribute("role", "option");
      li.dataset.indice = i;
      var nome = document.createElement("span");
      nome.className = "sug-nome";
      nome.textContent = item.nome;
      var info = document.createElement("span");
      info.className = "sug-info";
      info.textContent = rotulo(tipo, item);
      li.appendChild(nome);
      li.appendChild(info);
      li.addEventListener("mousedown", function (e) { e.preventDefault(); escolher(wrap, item); });
      ul.appendChild(li);
    });
    ul._itens = itens;
    wrap.appendChild(ul);
    // A lista fica "fixa" na tela, ancorada no campo: dentro de tabelas com rolagem ou cartões com overflow
    // (ex.: Produtos da nota) uma lista absoluta era cortada pelo cartão.
    var campo = wrap.querySelector(".bs-texto") || wrap;
    var r = campo.getBoundingClientRect();
    var largura = Math.max(r.width, 300);
    ul.style.position = "fixed";
    ul.style.right = "auto";
    ul.style.width = Math.min(largura, window.innerWidth - 16) + "px";
    ul.style.left = Math.max(8, Math.min(r.left, window.innerWidth - largura - 8)) + "px";
    ul.style.zIndex = "400";
    var abaixo = window.innerHeight - r.bottom - 12;
    if (abaixo < 180 && r.top > abaixo) {  // pouco espaço embaixo: abre para cima
      ul.style.top = "auto"; ul.style.bottom = (window.innerHeight - r.top + 4) + "px"; ul.style.maxHeight = Math.min(320, r.top - 12) + "px";
    } else {
      ul.style.top = (r.bottom + 4) + "px"; ul.style.maxHeight = Math.min(320, abaixo) + "px";
    }
  }

  function escolher(wrap, item) {
    var p = partes(wrap);
    p.texto.value = item.nome;
    p.id.value = item.id;
    p.texto.classList.remove("bs-invalido");
    p.id.dispatchEvent(new Event("change", { bubbles: true }));
    wrap.dispatchEvent(new CustomEvent("sugestao:escolhida", { bubbles: true, detail: item }));
    fechar(wrap);
    // Leva o cursor ao próximo campo da linha/formulário (ex.: quantidade).
    var campos = Array.prototype.slice.call(
      (wrap.closest("tr") || wrap.closest("form") || document).querySelectorAll("input:not([type=hidden]), select")
    );
    var prox = campos[campos.indexOf(p.texto) + 1];
    if (prox) { prox.focus(); if (prox.select) prox.select(); }
  }

  function buscar(wrap, termo, aoChegar) {
    var tipo = wrap.dataset.buscaSugestao;
    var anterior = pedidos.get(wrap);
    if (anterior) anterior.abort();
    var ctrl = new AbortController();
    pedidos.set(wrap, ctrl);
    fetch("/api/" + tipo + "?q=" + encodeURIComponent(termo), { signal: ctrl.signal })
      .then(function (r) { return r.ok ? r.json() : []; })
      .then(function (itens) { aoChegar(Array.isArray(itens) ? itens : []); })
      .catch(function () {});
  }

  function ativo(ul) { return ul ? ul.querySelector("li.ativo") : null; }

  document.addEventListener("input", function (e) {
    var wrap = e.target.closest && e.target.closest(".busca-sugestao");
    if (!wrap || !e.target.classList.contains("bs-texto")) return;
    var p = partes(wrap);
    p.id.value = "";
    clearTimeout(timers.get(wrap));
    var termo = p.texto.value.trim();
    if (termo.length < 2) { fechar(wrap); return; }
    timers.set(wrap, setTimeout(function () {
      buscar(wrap, termo, function (itens) {
        if (p.texto.value.trim() === termo && document.activeElement === p.texto) mostrar(wrap, itens);
      });
    }, ESPERA_MS));
  });

  document.addEventListener("keydown", function (e) {
    var wrap = e.target.closest && e.target.closest(".busca-sugestao");
    if (!wrap || !e.target.classList.contains("bs-texto")) return;
    var p = partes(wrap);
    var ul = p.lista;
    var itensLi = ul ? Array.prototype.slice.call(ul.querySelectorAll("li[data-indice]")) : [];
    var atual = ativo(ul);
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      if (!itensLi.length) return;
      e.preventDefault();
      var i = atual ? itensLi.indexOf(atual) : -1;
      i = e.key === "ArrowDown" ? Math.min(itensLi.length - 1, i + 1) : Math.max(0, i - 1);
      itensLi.forEach(function (li) { li.classList.remove("ativo"); });
      itensLi[i].classList.add("ativo");
      itensLi[i].scrollIntoView({ block: "nearest" });
    } else if (e.key === "Enter") {
      e.preventDefault();  // nunca envia o formulário pela metade
      if (atual) { escolher(wrap, ul._itens[+atual.dataset.indice]); return; }
      if (ul && ul._itens && ul._itens.length === 1) { escolher(wrap, ul._itens[0]); return; }
      // Leitor de código de barras: o Enter chega antes da busca com espera.
      var termo = p.texto.value.trim();
      if (termo.length < 2) return;
      clearTimeout(timers.get(wrap));
      buscar(wrap, termo, function (itens) {
        var exato = itens.filter(function (it) { return it.codigo_barras && it.codigo_barras === termo; });
        if (exato.length === 1) escolher(wrap, exato[0]);
        else if (itens.length === 1) escolher(wrap, itens[0]);
        else mostrar(wrap, itens);
      });
    } else if (e.key === "Escape") {
      if (ul) { e.preventDefault(); e.stopPropagation(); fechar(wrap); }
    }
  });

  document.addEventListener("focusout", function (e) {
    var wrap = e.target.closest && e.target.closest(".busca-sugestao");
    if (!wrap || !e.target.classList.contains("bs-texto")) return;
    setTimeout(function () {
      if (wrap.contains(document.activeElement)) return;
      fechar(wrap);
      var p = partes(wrap);
      p.texto.classList.toggle("bs-invalido", Boolean(p.texto.value.trim() && !p.id.value));
    }, 120);
  });

  // Não deixa enviar com texto digitado mas nada escolhido da lista.
  document.addEventListener("submit", function (e) {
    var pendente = Array.prototype.slice.call(e.target.querySelectorAll(".busca-sugestao")).filter(function (w) {
      var p = partes(w);
      return p.texto.value.trim() && !p.id.value;
    });
    if (!pendente.length) return;
    e.preventDefault();
    e.stopImmediatePropagation();
    var campo = partes(pendente[0]).texto;
    campo.classList.add("bs-invalido");
    campo.focus();
    if (window.confirmarAcao) {
      window.confirmarAcao("Escolha na lista de sugestões: \"" + campo.value.trim() +
        "\" ainda não foi selecionado.", function () { campo.focus(); },
        { titulo: "Item não selecionado", textoSim: "Ok", textoNao: "Fechar", estilo: "primary" });
    }
  }, true);
  function fecharTodas() {
    Array.prototype.forEach.call(document.querySelectorAll(".busca-sugestao > .sugestoes"), function (ul) { ul.remove(); });
  }
  window.addEventListener("scroll", function (e) {
    if (e.target && e.target.closest && e.target.closest(".sugestoes")) return;  // rolar a própria lista não fecha
    fecharTodas();
  }, true);
  window.addEventListener("resize", fecharTodas);
})();
