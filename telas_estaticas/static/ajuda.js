// Busca da seção de Ajuda (spec 005): filtra no navegador o índice embutido na
// página (guias, perguntas, atalhos), sem diferenciar acento e maiúsculas. Todas
// as palavras digitadas precisam aparecer (título ou texto).
(function () {
  var campo = document.getElementById("ajuda-busca");
  var dadosEl = document.getElementById("ajuda-indice");
  if (!campo || !dadosEl) return;
  var resultados = document.getElementById("ajuda-resultados");
  var conteudo = document.getElementById("ajuda-conteudo");
  var itens = [];
  try { itens = JSON.parse(dadosEl.textContent || "[]"); } catch (e) { itens = []; }

  function normalizar(texto) {
    return (texto || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  }
  itens.forEach(function (i) { i._alvo = normalizar(i.titulo + " " + i.texto); i._titulo = normalizar(i.titulo); });

  function render(termo) {
    var palavras = normalizar(termo).split(/\s+/).filter(Boolean);
    if (!palavras.length) {
      resultados.hidden = true;
      conteudo.hidden = false;
      return;
    }
    var achados = itens.filter(function (i) {
      return palavras.every(function (p) { return i._alvo.indexOf(p) !== -1; });
    });
    // Quem tem a palavra no título vem primeiro.
    achados.sort(function (a, b) {
      var ta = palavras.some(function (p) { return a._titulo.indexOf(p) !== -1; }) ? 0 : 1;
      var tb = palavras.some(function (p) { return b._titulo.indexOf(p) !== -1; }) ? 0 : 1;
      return ta - tb;
    });
    resultados.innerHTML = "";
    if (!achados.length) {
      var vazio = document.createElement("p");
      vazio.className = "muted";
      vazio.textContent = "Nada encontrado. Tente outra palavra, pergunte ao assistente ou abra o Suporte.";
      resultados.appendChild(vazio);
    }
    achados.forEach(function (i) {
      var a = document.createElement("a");
      a.className = "card ajuda-card";
      a.href = i.url;
      var tipo = document.createElement("span");
      tipo.className = "muted small";
      tipo.textContent = i.tipo;
      var titulo = document.createElement("b");
      titulo.textContent = i.titulo;
      a.appendChild(tipo);
      a.appendChild(titulo);
      resultados.appendChild(a);
    });
    resultados.hidden = false;
    conteudo.hidden = true;
  }

  campo.addEventListener("input", function () { render(campo.value); });
  var inicial = new URLSearchParams(location.search).get("q");
  if (inicial) { campo.value = inicial; render(inicial); }
})();
