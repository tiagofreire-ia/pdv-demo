// Campo de arquivo em português: troca o texto em inglês/português de Portugal do navegador por
// "Selecionar arquivo" / "Nenhum arquivo selecionado". Vale para todo <input type="file"> visível; os escondidos
// (que outra tela abre por botão próprio) ficam como estão.
(function () {
  function montar(input) {
    if (input.hidden || input.dataset.arquivoPronto || input.closest(".campo-arquivo")) return;
    input.dataset.arquivoPronto = "1";
    var caixa = document.createElement("div");
    caixa.className = "campo-arquivo";
    input.parentNode.insertBefore(caixa, input);
    caixa.appendChild(input);
    var rotulo = document.createElement("label");
    rotulo.className = "campo-arquivo-botao";
    rotulo.textContent = input.multiple ? "Selecionar arquivos" : "Selecionar arquivo";
    if (!input.id) input.id = "arq-" + Math.random().toString(36).slice(2, 8);
    rotulo.setAttribute("for", input.id);
    var nome = document.createElement("span");
    nome.className = "campo-arquivo-nome";
    nome.textContent = "Nenhum arquivo selecionado";
    caixa.appendChild(rotulo);
    caixa.appendChild(nome);
    input.addEventListener("change", function () {
      var n = input.files ? input.files.length : 0;
      nome.textContent = n === 0 ? "Nenhum arquivo selecionado" : n === 1 ? input.files[0].name : n + " arquivos selecionados";
    });
  }
  function varrer(raiz) {
    Array.prototype.forEach.call((raiz || document).querySelectorAll('input[type="file"]'), montar);
  }
  varrer();
  document.addEventListener("htmx:afterSwap", function (e) { varrer(e.target); });
})();
