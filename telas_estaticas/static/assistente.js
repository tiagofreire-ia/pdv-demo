// Assistente de IA (chat):
//   1. Pergunta via texto ou áudio (mic grava, Groq Whisper transcreve e manda sozinho).
//   2. Envio assíncrono (fetch), sem recarregar a página: mostra um balão "Pensando..."
//      enquanto espera e troca pelo balão real quando a resposta chega.
//   3. Cada resposta tem um rodapé de ações (ouvir, copiar, avaliar, compartilhar,
//      gerar de novo, excluir) — funciona tanto nos balões já na página quanto nos
//      que o JS cria na hora, via delegação de evento (nenhum listener é preso a um
//      elemento específico).
(function () {
  // Frase fixa do campo (spec 012, A2) — a saudação é que muda a cada abertura.
  var FRASE_CAMPO = "Peça à Óptima…";

  function csrfToken() {
    var meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.content : "";
  }

  // ============ Balões: montagem e indicador "pensando" ============
  // Mesmos ícones (feather-style) usados no resto do site — ver {% set ic %} em
  // base.html/assistente.html.
  var ICO = 'width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"';
  var RODAPE_HTML =
    '<div class="chat-balao-rodape">' +
    '<button type="button" class="chat-balao-acao" data-acao="ouvir" title="Ouvir"><svg ' + ICO + '><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/></svg></button>' +
    '<button type="button" class="chat-balao-acao" data-acao="copiar" title="Copiar resposta"><svg ' + ICO + '><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg></button>' +
    '<button type="button" class="chat-balao-acao" data-acao="bom" title="Resposta boa"><svg ' + ICO + '><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3H14z"/><path d="M7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/></svg></button>' +
    '<button type="button" class="chat-balao-acao" data-acao="ruim" title="Resposta ruim"><svg ' + ICO + '><path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3H10z"/><path d="M17 2h3a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-3"/></svg></button>' +
    '<button type="button" class="chat-balao-acao" data-acao="compartilhar" title="Compartilhar"><svg ' + ICO + '><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg></button>' +
    '<button type="button" class="chat-balao-acao" data-acao="atualizar" title="Gerar resposta de novo"><svg ' + ICO + '><path d="M23 4v6h-6"/><path d="M1 20v-6h6"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10"/><path d="M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg></button>' +
    '<span class="chat-balao-mais-wrap">' +
    '<button type="button" class="chat-balao-acao" data-acao="mais" title="Mais opções"><svg ' + ICO + '><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/></svg></button>' +
    '<span class="chat-balao-mais-menu" hidden><button type="button" class="chat-balao-acao" data-acao="excluir">Excluir da conversa</button></span>' +
    "</span>" +
    "</div>";

  // Frases do indicador de espera: cada uma entra numa linha nova (não substitui
  // a anterior), imitando o rastro de status de uma tarefa em andamento.
  var FRASES_PENSANDO = ["Pensando...", "Pesquisando nos dados...", "Analisando...", "Revisando a resposta...", "Tudo pronto..."];
  var FRASES_DOCUMENTO = ["Lendo documento...", "Conferindo os itens...", "Casando com os produtos cadastrados...", "Montando a proposta...", "Quase lá..."];

  function iniciarPensando(balao, frases) {
    var FRASES_PENSANDO_ATUAIS = frases || FRASES_PENSANDO;
    var textoEl = balao.querySelector(".chat-balao-texto");
    textoEl.innerHTML = "";
    balao.classList.add("chat-balao-pensando");
    var rodape = balao.querySelector(".chat-balao-rodape");
    if (rodape) rodape.hidden = true;
    var i = 0;
    function adicionarLinha() {
      if (i >= FRASES_PENSANDO_ATUAIS.length) return;
      var linha = document.createElement("div");
      linha.className = "chat-balao-pensando-linha";
      linha.textContent = FRASES_PENSANDO_ATUAIS[i];
      textoEl.appendChild(linha);
      i++;
    }
    adicionarLinha();
    var timer = setInterval(adicionarLinha, frases ? 2500 : 900);
    return function pararPensando() {
      clearInterval(timer);
      balao.classList.remove("chat-balao-pensando");
    };
  }

  function preencherBalaoAssistente(balao, pergunta, resposta) {
    balao.dataset.pergunta = pergunta;
    balao.querySelector(".chat-balao-texto").textContent = resposta;
    var rodape = balao.querySelector(".chat-balao-rodape");
    if (!rodape) balao.insertAdjacentHTML("beforeend", RODAPE_HTML);
    else rodape.hidden = false;
  }

  // Cartão de proposta (spec 003): o assistente preparou uma ação (cadastro,
  // entrada, reajuste, conta, retirada...) e NADA foi gravado ainda. Mostra o que
  // vai mudar (de → para), os itens (os opcionais com checkbox para desmarcar) e
  // os avisos. Dupla checagem: "Confirmar" ainda passa pela caixa de confirmação
  // padrão do sistema (window.confirmarAcao) antes de mandar pro servidor, que
  // revalida tudo e executa uma única vez (proposta de uso único, 15 min).
  function elemento(tag, classe, texto) {
    var el = document.createElement(tag);
    if (classe) el.className = classe;
    if (texto !== undefined && texto !== null) el.textContent = texto;
    return el;
  }

  function preencherBalaoComProposta(balao, proposta) {
    var resumo = proposta.resumo || {};
    balao.classList.add("chat-balao-proposta");
    var textoEl = balao.querySelector(".chat-balao-texto");
    textoEl.innerHTML = "";
    textoEl.appendChild(elemento("div", "chat-proposta-titulo", proposta.titulo));
    if (proposta.descricao) textoEl.appendChild(elemento("div", "chat-proposta-descricao", proposta.descricao));

    if (resumo.linhas && resumo.linhas.length) {
      var tabela = elemento("table", "chat-proposta-linhas");
      resumo.linhas.forEach(function (l) {
        var tr = document.createElement("tr");
        tr.appendChild(elemento("td", "", l.rotulo));
        var td = document.createElement("td");
        if (l.de !== null && l.de !== undefined) td.appendChild(elemento("span", "chat-proposta-de", l.de));
        td.appendChild(elemento("span", "", (l.de !== null && l.de !== undefined ? "→ " : "") + l.para));
        if (l.aviso) td.appendChild(elemento("div", "chat-proposta-aviso", l.aviso));
        tr.appendChild(td);
        tabela.appendChild(tr);
      });
      textoEl.appendChild(tabela);
    }

    var checkboxes = [];
    if (resumo.itens && resumo.itens.length) {
      var lista = elemento("ul", "chat-proposta-itens");
      resumo.itens.forEach(function (item) {
        var li = document.createElement("li");
        if (item.opcional && item.acao !== null && item.acao !== undefined) {
          var cb = document.createElement("input");
          cb.type = "checkbox";
          cb.checked = true;
          cb.dataset.acao = String(item.acao);
          checkboxes.push(cb);
          li.appendChild(cb);
        }
        var corpo = document.createElement("div");
        corpo.appendChild(elemento("div", "", item.texto));
        if (item.aviso) corpo.appendChild(elemento("div", "chat-proposta-aviso", item.aviso));
        li.appendChild(corpo);
        lista.appendChild(li);
      });
      textoEl.appendChild(lista);
    }

    if (resumo.avisos && resumo.avisos.length) {
      var avisos = elemento("div", "chat-proposta-avisos");
      resumo.avisos.forEach(function (a) { avisos.appendChild(elemento("div", "chat-proposta-aviso", "⚠ " + a)); });
      textoEl.appendChild(avisos);
    }

    var acoes = elemento("div", "chat-proposta-acoes");
    var btnConfirmar = elemento("button", "btn primary mini", "Confirmar");
    btnConfirmar.type = "button";
    var btnCancelar = elemento("button", "btn ghost mini", "Cancelar");
    btnCancelar.type = "button";
    acoes.appendChild(btnConfirmar);
    acoes.appendChild(btnCancelar);
    textoEl.appendChild(acoes);

    function mostrarStatus(texto) {
      acoes.remove();
      checkboxes.forEach(function (cb) { cb.disabled = true; });
      textoEl.appendChild(elemento("div", "chat-proposta-status", texto));
    }

    function enviar(url, corpo) {
      btnConfirmar.disabled = true;
      btnCancelar.disabled = true;
      fetch(url, { method: "POST", headers: { "X-CSRF-Token": csrfToken() }, body: corpo })
        .then(function (r) { return r.json(); })
        .then(function (resultado) { mostrarStatus(resultado.mensagem || resultado.erro || "Feito."); })
        .catch(function () { mostrarStatus("Não consegui falar com o servidor agora. Nada foi alterado; tente de novo."); });
    }

    btnConfirmar.addEventListener("click", function () {
      var desmarcados = checkboxes.filter(function (cb) { return !cb.checked; });
      if (checkboxes.length && desmarcados.length === checkboxes.length) {
        mostrarStatus("Nenhum item marcado — nada foi alterado.");
        return;
      }
      var marcados = checkboxes.length ? " (" + (checkboxes.length - desmarcados.length) + " de " + checkboxes.length + " itens)" : "";
      window.confirmarAcao(proposta.titulo + marcados + ". Confirma?", function () {
        var corpo = new URLSearchParams();
        desmarcados.forEach(function (cb) { corpo.append("desmarcados", cb.dataset.acao); });
        enviar("/admin/assistente/propostas/" + encodeURIComponent(proposta.id) + "/confirmar", corpo);
      }, { titulo: "Confirmar ação do assistente", textoSim: "Confirmar", textoNao: "Voltar" });
    });
    btnCancelar.addEventListener("click", function () {
      enviar("/admin/assistente/propostas/" + encodeURIComponent(proposta.id) + "/cancelar", new URLSearchParams());
    });
  }

  function criarBalaoUsuario(pergunta) {
    var div = document.createElement("div");
    div.className = "chat-balao chat-usuario";
    var texto = document.createElement("div");
    texto.className = "chat-balao-texto";
    texto.textContent = pergunta;
    div.appendChild(texto);
    return div;
  }

  function criarBalaoAssistenteVazio() {
    var div = document.createElement("div");
    div.className = "chat-balao chat-assistente";
    div.innerHTML = '<div class="chat-balao-texto"></div>';
    return div;
  }

  function formTopo(acao, texto, classe) {
    var f = document.createElement("form");
    f.method = "post";
    f.action = acao;
    var csrf = document.createElement("input");
    csrf.type = "hidden";
    csrf.name = "csrf_token";
    csrf.value = csrfToken();
    var btn = document.createElement("button");
    btn.type = "submit";
    btn.className = classe;
    btn.textContent = texto;
    f.appendChild(csrf);
    f.appendChild(btn);
    return f;
  }

  // Conversa nova recebe um lugar na lista "Conversas" logo depois da primeira resposta.
  function registrarConversa(conversa) {
    if (!conversa) return;
    var lista = document.getElementById("conversas-ia-itens");
    if (!lista || lista.querySelector('[data-conversa-id="' + conversa.id + '"]')) return;
    var vazio = lista.querySelector(".conversas-vazio");
    if (vazio) vazio.remove();
    lista.querySelectorAll("li.ativa").forEach(function (li) { li.classList.remove("ativa"); });
    var li = document.createElement("li");
    li.dataset.conversaId = conversa.id;
    li.className = "ativa";
    var a = document.createElement("a");
    a.href = "/admin/assistente?conversa=" + conversa.id;
    a.title = conversa.titulo;
    var titulo = document.createElement("span");
    titulo.className = "conversa-titulo";
    titulo.textContent = conversa.titulo;
    var data = document.createElement("span");
    data.className = "conversa-data muted small";
    data.textContent = "agora";
    a.appendChild(titulo);
    a.appendChild(data);
    li.appendChild(a);
    lista.insertBefore(li, lista.firstChild);
    var resumo = document.querySelector("#conversas-ia > summary");
    if (resumo) resumo.textContent = "Conversas (" + lista.querySelectorAll("li[data-conversa-id]").length + ")";
  }

  // Rolagem automática da conversa (achado de 01/10): enquanto a pessoa está no fim da
  // conversa, todo conteúdo novo (pergunta, "pensando", resposta, cartão, áudio) desce a tela
  // sozinho. Se ela subiu para ler algo antigo, não é puxada de volta; enviar uma pergunta
  // nova volta a acompanhar o fim.
  function rolarParaFim(janela) {
    janela.scrollTop = janela.scrollHeight;
    var doc = document.scrollingElement || document.documentElement;
    if (doc.scrollHeight > window.innerHeight + 2) doc.scrollTop = doc.scrollHeight;
  }

  function acompanharRolagem(janela) {
    if (!janela || janela._acompanhando) return;
    janela._acompanhando = true;
    janela._grudado = true;
    janela.addEventListener("scroll", function () {
      janela._grudado = janela.scrollHeight - janela.scrollTop - janela.clientHeight < 80;
    });
    var mensagens = janela.querySelector(".chat-mensagens") || janela;
    var aoMudar = function () { if (janela._grudado) rolarParaFim(janela); };
    if (window.MutationObserver) {
      new MutationObserver(aoMudar).observe(mensagens, { childList: true, subtree: true, characterData: true });
    }
    if (window.ResizeObserver) new ResizeObserver(aoMudar).observe(mensagens);
    rolarParaFim(janela);
  }

  function novoEnvioId() {
    var bytes = new Uint8Array(8);
    (window.crypto || window.msCrypto).getRandomValues(bytes);
    return Array.prototype.map.call(bytes, function (b) { return ("0" + b.toString(16)).slice(-2); }).join("");
  }

  // Primeira pergunta da sessão: sai da tela inicial (hero, campo centralizado)
  // para a janela de conversa, sem recarregar a página.
  function transicionarParaChat(form) {
    var hero = document.querySelector(".chat-hero");
    var janela = document.createElement("div");
    janela.className = "chat-janela";
    janela.id = "chat-janela";
    var mensagens = document.createElement("div");
    mensagens.className = "chat-mensagens";
    mensagens.id = "chat-mensagens";
    janela.appendChild(mensagens);
    if (hero) hero.replaceWith(janela);
    else document.querySelector(".chat-page").insertBefore(janela, form);

    janela.parentNode.insertBefore(form, janela.nextSibling);
    var input = form.querySelector('input[name="pergunta"]');
    if (input) input.placeholder = FRASE_CAMPO;

    acompanharRolagem(janela);
    var topo = document.querySelector(".chat-topo");
    if (topo && !topo.querySelector('form[action="/admin/assistente/nova-conversa"]')) {
      topo.appendChild(formTopo("/admin/assistente/nova-conversa", "+ Nova conversa", "btn mini"));
      var excluir = formTopo("/admin/assistente/limpar", "Excluir conversa", "btn danger ghost mini");
      excluir.addEventListener("submit", function (e) {
        if (excluir.dataset.confirmado === "1") return;
        e.preventDefault();
        window.confirmarAcao("Excluir esta conversa? As mensagens dela serão apagadas; as outras conversas continuam.",
          function () { excluir.dataset.confirmado = "1"; excluir.submit(); },
          { titulo: "Excluir conversa", textoSim: "Excluir", textoNao: "Cancelar" });
      });
      topo.appendChild(excluir);
    }
    return janela;
  }

  // Manda a pergunta pro back-end e preenche o balão (novo ou já existente, no
  // caso do "atualizar") quando a resposta chegar.
  function perguntarEExibir(pergunta, balaoAssistente, arquivo, envio) {
    var textoEl = balaoAssistente.querySelector(".chat-balao-texto");
    var pararPensando = iniciarPensando(balaoAssistente, arquivo ? FRASES_DOCUMENTO : null);
    var envioId = novoEnvioId();
    var corpo;
    if (arquivo) {
      corpo = new FormData();
      corpo.append("pergunta", pergunta);
      corpo.append("envio_id", envioId);
      corpo.append("arquivo", arquivo, arquivo.name || "documento");
    } else {
      corpo = new URLSearchParams({ pergunta: pergunta, envio_id: envioId });
    }
    // Documento pode levar mais (visão + montagem da proposta): 90 s de limite.
    var controle = window.AbortController ? new AbortController() : null;
    var limite = controle ? setTimeout(function () { controle.abort(); }, arquivo ? 90000 : 60000) : null;
    // "Parar" (spec 012, A1): quem enviou recebe como cancelar este envio.
    var parado = false;
    if (envio) {
      envio.cancelar = function () {
        if (parado) return;
        parado = true;
        if (limite) clearTimeout(limite);
        pararPensando();
        if (controle) controle.abort();
        fetch("/admin/assistente/cancelar", {
          method: "POST", headers: { "X-CSRF-Token": csrfToken() },
          body: new URLSearchParams({ envio_id: envioId }),
        }).catch(function () {});
      };
    }
    return fetch("/admin/assistente/perguntar-async", {
      method: "POST",
      headers: { "X-CSRF-Token": csrfToken() },
      body: corpo,
      signal: controle ? controle.signal : undefined,
    })
      .then(function (r) { if (limite) clearTimeout(limite); return r.json(); })
      .then(function (dados) {
        if (parado) return;
        pararPensando();
        if (dados.cancelado) return;
        // Aviso de limite diário (spec 011): só aparece perto do fim das perguntas do dia.
        var avisoEl = document.getElementById("aviso-limite");
        if (avisoEl) { avisoEl.textContent = dados.aviso_limite || ""; avisoEl.hidden = !dados.aviso_limite; }
        var contador = document.getElementById("contador-perguntas");
        if (contador && dados.limite_dia) {
          contador.querySelector("strong").textContent = Math.min(dados.perguntas_hoje, dados.limite_dia) + " de " + dados.limite_dia;
          contador.classList.toggle("perto", dados.perguntas_hoje >= 0.8 * dados.limite_dia);
        }
        if (dados.erro) { textoEl.textContent = dados.erro; return; }
        if (dados.ids) {
          balaoAssistente.dataset.ids = dados.ids.pergunta + "," + dados.ids.resposta;
          var anterior = balaoAssistente.previousElementSibling;
          if (anterior && anterior.classList.contains("chat-usuario")) anterior.dataset.id = dados.ids.pergunta;
        }
        registrarConversa(dados.conversa);
        if (dados.proposta) { preencherBalaoComProposta(balaoAssistente, dados.proposta); return; }
        preencherBalaoAssistente(balaoAssistente, dados.pergunta || pergunta, dados.resposta);
      })
      .catch(function () {
        if (parado) return;
        pararPensando();
        textoEl.textContent = "Não consegui falar com a IA agora. Tente novamente.";
      });
  }

  document.addEventListener("submit", function (e) {
    var form = e.target.closest("[data-form-pergunta]");
    if (!form) return;
    e.preventDefault();
    var input = form.querySelector('input[name="pergunta"]');
    var pergunta = (input.value || "").trim();
    var arquivo = form._arquivo || null;
    if (!pergunta && !arquivo) return;
    input.value = "";
    limparAnexo(form);

    var janela = document.getElementById("chat-janela") || transicionarParaChat(form);
    acompanharRolagem(janela);
    janela._grudado = true;
    var mensagens = document.getElementById("chat-mensagens");
    mensagens.appendChild(criarBalaoUsuario((arquivo ? "📎 " + arquivo.name + (pergunta ? "\n" : "") : "") + pergunta));
    var balaoAssistente = criarBalaoAssistenteVazio();
    mensagens.appendChild(balaoAssistente);
    janela.scrollTop = janela.scrollHeight;

    var btnEnviar = form.querySelector(".chat-pill-enviar");
    var balaoUsuario = balaoAssistente.previousElementSibling;
    var envio = {};
    function voltarAoEnvio() {
      if (btnEnviar) {
        btnEnviar.classList.remove("parar");
        btnEnviar.textContent = "↑";
        btnEnviar.setAttribute("aria-label", "Enviar");
        btnEnviar.title = "";
        btnEnviar.type = "submit";
        btnEnviar.onclick = null;
      }
      document.removeEventListener("keydown", aoTeclar, true);
    }
    function parar() {
      if (envio.cancelar) envio.cancelar();
      voltarAoEnvio();
      balaoAssistente.remove();
      if (balaoUsuario && balaoUsuario.classList.contains("chat-usuario")) balaoUsuario.remove();
      input.value = pergunta;
      if (arquivo) escolherAnexo(form, arquivo);
      input.focus();
    }
    function aoTeclar(ev) {
      if (ev.key === "Escape") { ev.preventDefault(); ev.stopPropagation(); parar(); }
    }
    // Enquanto a IA pensa, o botão de enviar vira ■ Parar (spec 012, A1).
    if (btnEnviar) {
      btnEnviar.classList.add("parar");
      btnEnviar.textContent = "■";
      btnEnviar.setAttribute("aria-label", "Parar");
      btnEnviar.title = "Parar e corrigir a pergunta (Esc)";
      btnEnviar.type = "button";
      btnEnviar.onclick = function (ev) { ev.preventDefault(); parar(); };
    }
    document.addEventListener("keydown", aoTeclar, true);

    perguntarEExibir(pergunta, balaoAssistente, arquivo, envio).then(function () {
      if (!document.body.contains(balaoAssistente)) return;  // foi parado
      voltarAoEnvio();
      janela.scrollTop = janela.scrollHeight;
      input.focus();
    });
  });

  acompanharRolagem(document.getElementById("chat-janela"));

  // ============ Pedido vindo da Ajuda (spec 005) ============
  // /admin/assistente?pergunta=... preenche o campo e põe o foco, mas NÃO envia:
  // o usuário revisa e decide (constituição, Princípio VI).
  (function () {
    var pedido = new URLSearchParams(location.search).get("pergunta");
    if (!pedido) return;
    var input = document.querySelector('[data-form-pergunta] input[name="pergunta"]');
    if (input && !input.disabled) {
      input.value = pedido.slice(0, 500);
      input.focus();
      input.setSelectionRange(input.value.length, input.value.length);
    }
    try { history.replaceState(null, "", location.pathname); } catch (e) {}
  })();

  // ============ Anexo de documento (spec 004) ============
  // 📎 escolhe arquivo (XML da NF-e, PDF, foto); 📷 abre a câmera no celular. O
  // arquivo vai junto da próxima pergunta (pode ir sem texto) e não fica salvo.
  var LIMITE_ANEXO = 10 * 1024 * 1024;

  function limparAnexo(form) {
    form._arquivo = null;
    var chip = form.querySelector("[data-anexo-chip]");
    if (chip) chip.hidden = true;
    var input = form.querySelector('input[name="pergunta"]');
    if (input) { input.required = true; delete input.dataset.placeholderFixo; input.placeholder = FRASE_CAMPO; }
    form.querySelectorAll("[data-anexo-input], [data-anexo-camera]").forEach(function (i) { i.value = ""; });
  }

  function escolherAnexo(form, arquivo) {
    if (!arquivo) return;
    if (arquivo.size > LIMITE_ANEXO) {
      alert("Arquivo acima de 10 MB. Envie um arquivo menor.");
      limparAnexo(form);
      return;
    }
    form._arquivo = arquivo;
    var chip = form.querySelector("[data-anexo-chip]");
    if (chip) {
      chip.querySelector("[data-anexo-nome]").textContent = arquivo.name || "foto";
      chip.hidden = false;
    }
    var input = form.querySelector('input[name="pergunta"]');
    if (input) {
      input.required = false; // documento pode ir sem pergunta
      if (!input.value) { input.placeholder = "Ex.: lança essa nota (opcional)"; input.dataset.placeholderFixo = "1"; }
      input.focus();
    }
  }

  document.querySelectorAll("[data-form-pergunta]").forEach(function (form) {
    var inputArquivo = form.querySelector("[data-anexo-input]");
    var inputCamera = form.querySelector("[data-anexo-camera]");
    var btnAnexo = form.querySelector("[data-btn-anexo]");
    var btnCamera = form.querySelector("[data-btn-camera]");
    var btnRemover = form.querySelector("[data-anexo-remover]");
    if (btnAnexo && inputArquivo) btnAnexo.addEventListener("click", function () { inputArquivo.click(); });
    if (btnCamera && inputCamera) btnCamera.addEventListener("click", function () { inputCamera.click(); });
    [inputArquivo, inputCamera].forEach(function (inp) {
      if (inp) inp.addEventListener("change", function () { escolherAnexo(form, inp.files && inp.files[0]); });
    });
    if (btnRemover) btnRemover.addEventListener("click", function () { limparAnexo(form); });
  });

  // ============ Ouvir resposta: tocar / pausar / continuar ============
  // Um clique toca; clicar de novo na mesma resposta pausa; de novo, continua. Tocar
  // outra resposta interrompe a anterior. O ícone mostra o estado.
  var ICONE_OUVIR = '<svg ' + ICO + '><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>';
  var ICONE_PAUSAR = '<svg ' + ICO + '><rect x="6" y="4" width="4" height="16" rx="1"/><rect x="14" y="4" width="4" height="16" rx="1"/></svg>';
  var ICONE_CONTINUAR = '<svg ' + ICO + '><polygon points="6 4 20 12 6 20 6 4"/></svg>';
  var fala = { utterance: null, botao: null, balao: null };

  function iconeFala(btn, estado) {
    if (!btn) return;
    btn.innerHTML = estado === "tocando" ? ICONE_PAUSAR : (estado === "pausado" ? ICONE_CONTINUAR : ICONE_OUVIR);
    btn.title = estado === "tocando" ? "Pausar" : (estado === "pausado" ? "Continuar" : "Ouvir");
    btn.classList.toggle("selecionada", estado !== "parado");
  }

  function textoParaFala(texto) {
    // Símbolos que o leitor de voz leria em voz alta (ou tropeçaria).
    return (texto || "").replace(/[*#|`_]+/g, " ").replace(/[•·]/g, ", ").replace(/\s+/g, " ").trim();
  }

  function pararFala() {
    var botao = fala.botao;
    fala = { utterance: null, botao: null, balao: null };
    window.speechSynthesis.cancel();
    iconeFala(botao, "parado");
  }

  function alternarFala(btn, balao, texto) {
    if (!("speechSynthesis" in window) || !texto) return;
    var synth = window.speechSynthesis;
    if (fala.balao === balao && (synth.speaking || synth.pending)) {
      if (synth.paused) { synth.resume(); iconeFala(btn, "tocando"); }
      else { synth.pause(); iconeFala(btn, "pausado"); }
      return;
    }
    pararFala();
    var u = new SpeechSynthesisUtterance(textoParaFala(texto));
    u.lang = "pt-BR";
    // Ao terminar (ou dar erro), volta o ícone — só se ainda for a fala atual (o
    // cancel() de uma fala anterior dispara o "end" dela depois).
    u.onend = u.onerror = function () {
      if (fala.utterance === u) { iconeFala(fala.botao, "parado"); fala = { utterance: null, botao: null, balao: null }; }
    };
    fala = { utterance: u, botao: btn, balao: balao };
    iconeFala(btn, "tocando");
    synth.speak(u);
  }

  // Não deixa o áudio continuar tocando ao sair da página ou excluir a resposta.
  window.addEventListener("pagehide", function () { if ("speechSynthesis" in window) window.speechSynthesis.cancel(); });

  // ============ Rodapé de ações de cada resposta ============
  function avisarAcao(btn, msg) {
    var textoOriginal = btn.textContent;
    var tituloOriginal = btn.title;
    btn.textContent = "✓";
    btn.title = msg;
    setTimeout(function () {
      btn.textContent = textoOriginal;
      btn.title = tituloOriginal;
    }, 1200);
  }

  document.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-acao]");
    if (!btn) return;
    var balao = btn.closest(".chat-balao");
    if (!balao) return;
    var acao = btn.dataset.acao;
    var textoEl = balao.querySelector(".chat-balao-texto");

    if (acao === "ouvir") {
      alternarFala(btn, balao, textoEl.textContent);
    } else if (acao === "copiar") {
      if (navigator.clipboard) {
        navigator.clipboard.writeText(textoEl.textContent).then(function () { avisarAcao(btn, "Copiado!"); });
      }
    } else if (acao === "bom" || acao === "ruim") {
      var contrario = acao === "bom" ? "ruim" : "bom";
      var btnContrario = balao.querySelector('[data-acao="' + contrario + '"]');
      var jaSelecionado = btn.classList.contains("selecionada");
      if (btnContrario) btnContrario.classList.remove("selecionada");
      btn.classList.toggle("selecionada", !jaSelecionado);
      // Só manda quando está SELECIONANDO (não ao tirar a seleção) — fica no log
      // de auditoria, mesma trilha de login/vendas/cancelamentos (nunca trava a UI).
      // 👎 (spec 017): pergunta antes "O que estava errado?" (opcional) — vira sinal para
      // o dono revisar na Memória da IA.
      if (!jaSelecionado) {
        var enviarFeedback = function (explicacao) {
          fetch("/admin/assistente/feedback", {
            method: "POST",
            headers: { "X-CSRF-Token": csrfToken() },
            body: new URLSearchParams({
              avaliacao: acao,
              pergunta: balao.dataset.pergunta || "",
              resposta: textoEl.textContent,
              explicacao: explicacao || "",
              mensagem_id: (balao.dataset.ids || "").split(",")[1] || "",
            }),
          }).catch(function () {});
        };
        if (acao === "bom") {
          enviarFeedback("");
        } else if (!balao.querySelector(".chat-feedback-explicacao")) {
          var caixa = document.createElement("form");
          caixa.className = "chat-feedback-explicacao";
          var campo = document.createElement("input");
          campo.type = "text";
          campo.maxLength = 1000;
          campo.placeholder = "O que estava errado? (Enter envia)";
          campo.setAttribute("aria-label", "O que estava errado na resposta");
          caixa.appendChild(campo);
          var enviado = false;
          var concluir = function () {
            if (enviado) return;
            enviado = true;
            enviarFeedback(campo.value.trim());
            caixa.remove();
          };
          caixa.addEventListener("submit", function (ev) { ev.preventDefault(); concluir(); });
          campo.addEventListener("blur", function () { setTimeout(concluir, 150); });
          btn.closest(".chat-balao").appendChild(caixa);
          campo.focus();
        }
      }
    } else if (acao === "compartilhar") {
      var textoCompartilhar = textoEl.textContent;
      if (navigator.share) {
        navigator.share({ text: textoCompartilhar }).catch(function () {});
      } else if (navigator.clipboard) {
        navigator.clipboard.writeText(textoCompartilhar).then(function () { avisarAcao(btn, "Copiado!"); });
      }
    } else if (acao === "atualizar") {
      var pergunta = balao.dataset.pergunta;
      if (pergunta) perguntarEExibir(pergunta, balao);
    } else if (acao === "mais") {
      var menu = balao.querySelector(".chat-balao-mais-menu");
      if (menu) menu.hidden = !menu.hidden;
    } else if (acao === "excluir") {
      // Ação destrutiva: sempre pela caixa de confirmação do próprio sistema,
      // nunca um confirm() nativo (Princípio III da constituição do projeto).
      window.confirmarAcao(
        "Excluir esta pergunta e resposta da conversa?",
        function () {
          // Apaga no servidor (spec 012, A1): antes só sumia da tela e voltava ao recarregar.
          var corpo = new URLSearchParams();
          (balao.dataset.ids || "").split(",").filter(Boolean).forEach(function (id) { corpo.append("ids", id); });
          var remover = function () {
            var anterior = balao.previousElementSibling;
            if (anterior && anterior.classList.contains("chat-usuario")) anterior.remove();
            balao.remove();
          };
          if (!corpo.toString()) { remover(); return; }
          fetch("/admin/assistente/mensagens/excluir", {
            method: "POST", headers: { "X-CSRF-Token": csrfToken() }, body: corpo,
          }).then(function (r) { return r.json(); })
            .then(function (res) { if (res && res.ok) remover(); })
            .catch(function () {});
        },
        { titulo: "Excluir da conversa", textoSim: "Excluir", textoNao: "Cancelar" }
      );
    }
  });

  // Fecha o menu "..." aberto ao clicar fora dele.
  document.addEventListener("click", function (e) {
    if (e.target.closest(".chat-balao-mais-wrap")) return;
    document.querySelectorAll(".chat-balao-mais-menu:not([hidden])").forEach(function (m) { m.hidden = true; });
  });

  // ============ Perguntar por voz (Speech-to-Text via Groq Whisper) ============
  if (!("MediaRecorder" in window) || !navigator.mediaDevices) return;

  document.querySelectorAll("[data-btn-mic]").forEach(function (btnMic) {
    var form = btnMic.closest("[data-form-pergunta]");
    var input = form ? form.querySelector('input[name="pergunta"]') : null;
    if (!form || !input) return;

    var btnPausar = form.querySelector("[data-btn-mic-pausar]");
    var btnExcluir = form.querySelector("[data-btn-mic-excluir]");

    // Ícones em SVG (o do microfone vem do HTML e é restaurado ao parar — trocar por
    // emoji aqui fazia voltar o ícone antigo depois da primeira gravação).
    var SVG = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">';
    var iconeMic = btnMic.innerHTML;
    var iconeParar = SVG + '<rect x="6" y="6" width="12" height="12" rx="2" fill="currentColor"/></svg>';
    var iconePausar = SVG + '<path d="M9 5v14M15 5v14"/></svg>';
    var iconeRetomar = SVG + '<path d="M7 5l12 7-12 7z" fill="currentColor"/></svg>';

    // Ondas da gravação: barrinhas que seguem o volume do microfone (Web Audio), no lugar
    // do campo de texto enquanto grava. Leve: um AnalyserNode e requestAnimationFrame.
    var ondas = document.createElement("span");
    ondas.className = "chat-ondas";
    ondas.hidden = true;
    ondas.setAttribute("aria-hidden", "true");
    for (var b = 0; b < 28; b++) ondas.appendChild(document.createElement("i"));
    input.parentNode.insertBefore(ondas, input);
    var barras = ondas.children;
    var audioCtx = null, analisador = null, quadro = null;
    // Gravação em silêncio ou curta demais não vai para a transcrição: o Whisper inventa frases
    // ("Legenda …") em áudio vazio, e a chamada seria gasta à toa. -1 = volume não medido.
    var VOLUME_MINIMO = 30, DURACAO_MINIMA_MS = 700;
    var picoVolume = -1, inicioGravacao = 0;

    function iniciarOndas(stream) {
      var Ctx = window.AudioContext || window.webkitAudioContext;
      if (!Ctx) return;
      try {
        audioCtx = new Ctx();
        analisador = audioCtx.createAnalyser();
        analisador.fftSize = 64;
        audioCtx.createMediaStreamSource(stream).connect(analisador);
      } catch (e) { audioCtx = null; return; }
      var dados = new Uint8Array(analisador.frequencyBinCount);
      input.hidden = true;
      ondas.hidden = false;
      picoVolume = 0;
      (function desenhar() {
        analisador.getByteFrequencyData(dados);
        if (!pausado) for (var j = 0; j < dados.length; j++) if (dados[j] > picoVolume) picoVolume = dados[j];
        for (var i = 0; i < barras.length; i++) {
          var v = pausado ? 0 : dados[(i % (dados.length - 4)) + 2] / 255;
          barras[i].style.height = Math.max(3, Math.round(v * 26)) + "px";
        }
        quadro = requestAnimationFrame(desenhar);
      })();
    }

    function pararOndas() {
      if (quadro) cancelAnimationFrame(quadro);
      quadro = null;
      if (audioCtx) audioCtx.close();
      audioCtx = analisador = null;
      ondas.hidden = true;
      input.hidden = false;
    }

    var gravador = null;
    var pedacos = [];
    var gravando = false;
    var pausado = false;
    var descartar = false; // true quando o usuário clica em excluir, em vez de enviar

    function mostrarControles(mostrar) {
      if (btnPausar) { btnPausar.hidden = !mostrar; btnPausar.innerHTML = iconePausar; }
      if (btnExcluir) btnExcluir.hidden = !mostrar;
    }

    function pararEEnviar() {
      if (!gravador) return;
      descartar = false;
      gravador.stop();
    }

    function excluirGravacao() {
      if (!gravador) return;
      descartar = true;
      if (gravador.state === "paused") gravador.resume(); // precisa estar ativo pra "stop" disparar certo
      gravador.stop();
    }

    function alternarPausa() {
      if (!gravador || gravador.state === "inactive") return;
      if (pausado) {
        gravador.resume();
        pausado = false;
        if (btnPausar) btnPausar.innerHTML = iconePausar;
      } else {
        gravador.pause();
        pausado = true;
        if (btnPausar) btnPausar.innerHTML = iconeRetomar;
      }
    }

    function iniciarGravacao(stream) {
      pedacos = [];
      pausado = false;
      descartar = false;
      picoVolume = -1;
      inicioGravacao = Date.now();
      gravador = new MediaRecorder(stream);
      gravador.addEventListener("dataavailable", function (e) {
        if (e.data.size > 0) pedacos.push(e.data);
      });
      gravador.addEventListener("stop", function () {
        stream.getTracks().forEach(function (t) { t.stop(); }); // libera o microfone
        gravando = false;
        btnMic.classList.remove("gravando");
        btnMic.innerHTML = iconeMic;
        pararOndas();
        mostrarControles(false);

        if (descartar) { pedacos = []; return; } // excluída: não manda nada pro servidor
        if (Date.now() - inicioGravacao < DURACAO_MINIMA_MS || (picoVolume >= 0 && picoVolume < VOLUME_MINIMO)) {
          pedacos = [];
          alert("Não ouvi nada. Fale perto do microfone e tente de novo, ou digite a pergunta.");
          return;
        }

        btnMic.disabled = true;
        var blob = new Blob(pedacos, { type: gravador.mimeType || "audio/webm" });
        var dados = new FormData();
        dados.append("arquivo", blob, "pergunta.webm");

        fetch("/admin/assistente/audio", {
          method: "POST",
          headers: { "X-CSRF-Token": csrfToken() },
          body: dados,
        })
          .then(function (r) { return r.json(); })
          .then(function (resposta) {
            btnMic.disabled = false;
            if (resposta.erro || !resposta.texto) {
              alert(resposta.erro || "Não consegui entender o áudio.");
              return;
            }
            input.value = resposta.texto;
            if (form.requestSubmit) form.requestSubmit(); else form.submit();
          })
          .catch(function () {
            btnMic.disabled = false;
            alert("Não consegui enviar o áudio. Confira sua conexão.");
          });
      });
      gravador.start();
      // Spec 017: no máximo 60 s por pergunta (o servidor recusa acima de 2 MB).
      var gravadorAtual = gravador;
      setTimeout(function () {
        if (gravador === gravadorAtual && gravador.state !== "inactive") pararEEnviar();
      }, 60000);
      gravando = true;
      btnMic.classList.add("gravando");
      btnMic.innerHTML = iconeParar;
      iniciarOndas(stream);
      mostrarControles(true);
    }

    btnMic.addEventListener("click", function () {
      // Clicar de novo no próprio mic (o botão que fica piscando) cancela a
      // gravação inteira, sem enviar nada — pra enviar de propósito é o botão
      // de enviar (➤) ou parar de gravar e clicar em enviar.
      if (gravando) { excluirGravacao(); return; }
      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(iniciarGravacao)
        .catch(function () {
          alert("Não consegui acessar o microfone. Verifique a permissão do navegador.");
        });
    });

    if (btnPausar) btnPausar.addEventListener("click", alternarPausa);
    if (btnExcluir) btnExcluir.addEventListener("click", excluirGravacao);

    // Clicar em enviar durante a gravação deve parar e mandar o áudio, já que o
    // campo de texto ainda está vazio (o texto só chega depois da transcrição).
    var btnEnviar = form.querySelector(".chat-pill-enviar");
    if (btnEnviar) {
      btnEnviar.addEventListener("click", function (e) {
        if (gravando) { e.preventDefault(); pararEEnviar(); }
      });
    }
  });

})();
