/* Interações das telas novas da demonstração (100% no navegador, sem servidor). */
(function () {
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function brl(v) { return 'R$ ' + v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }

  /* ---------- Aviso rápido ---------- */
  var toastEl, toastTimer;
  function toast(msg) {
    if (!toastEl) { toastEl = document.createElement('div'); toastEl.className = 'nv-toast'; toastEl.setAttribute('role', 'status'); document.body.appendChild(toastEl); }
    toastEl.textContent = msg;
    toastEl.classList.add('visivel');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove('visivel'); }, 2800);
  }
  window.nvToast = toast;
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-toast]');
    if (b) { e.preventDefault(); toast(b.getAttribute('data-toast')); }
  });
  document.addEventListener('change', function (e) {
    var s = e.target.closest('.nv-switch input');
    if (!s) return;
    var nome = s.getAttribute('data-nome') || 'Opção';
    toast(nome + (s.checked ? ' ligado.' : ' desligado.'));
  });

  /* ---------- Abas ---------- */
  $$('[data-abas]').forEach(function (grupo) {
    var botoes = $$('button[data-aba]', grupo);
    botoes.forEach(function (b) {
      b.addEventListener('click', function () {
        botoes.forEach(function (x) { x.classList.toggle('ativo', x === b); });
        var alvo = b.getAttribute('data-aba');
        $$('.nv-aba[data-grupo="' + grupo.getAttribute('data-abas') + '"]').forEach(function (p) { p.hidden = p.id !== alvo; });
      });
    });
  });

  /* ---------- Kanban: avançar pedido (cozinha / delivery) ---------- */
  function contar() {
    $$('.nv-coluna').forEach(function (c) {
      var q = $('.qtd', c);
      if (q) q.textContent = $$('.nv-pedido', c).length;
    });
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-avancar]');
    if (!b) return;
    var card = b.closest('.nv-pedido');
    var destino = document.getElementById(b.getAttribute('data-avancar'));
    if (!card || !destino) return;
    var prox = b.getAttribute('data-proximo');
    var rotulo = b.getAttribute('data-proximo-rotulo');
    if (prox) { b.setAttribute('data-avancar', prox); b.textContent = rotulo || 'Avançar'; b.removeAttribute('data-proximo'); }
    else { b.remove(); }
    card.classList.remove('atrasado');
    card.classList.add('novo');
    destino.appendChild(card);
    contar();
    toast(b.getAttribute('data-msg') || 'Pedido atualizado.');
  });
  contar();

  /* ---------- Cronômetros ---------- */
  var timers = $$('[data-inicio-min]');
  if (timers.length) {
    var base = Date.now();
    setInterval(function () {
      timers.forEach(function (t) {
        var seg = Math.floor(parseFloat(t.getAttribute('data-inicio-min')) * 60 + (Date.now() - base) / 1000);
        var m = Math.floor(seg / 60), s = seg % 60;
        t.textContent = m + ':' + (s < 10 ? '0' : '') + s;
        var card = t.closest('.nv-pedido');
        var limite = parseFloat(t.getAttribute('data-limite') || '0');
        if (card && limite && m >= limite && card.closest('[data-atrasa]')) card.classList.add('atrasado');
      });
    }, 1000);
  }

  /* ---------- Mesas / comandas ---------- */
  var mesas = $$('[data-mesa]');
  mesas.forEach(function (m) {
    m.addEventListener('click', function () {
      mesas.forEach(function (x) { x.classList.toggle('ativa', x === m); });
      var alvo = m.getAttribute('data-mesa');
      $$('[data-comanda]').forEach(function (p) { p.hidden = p.getAttribute('data-comanda') !== alvo; });
    });
  });

  /* ---------- WhatsApp: trocar de conversa ---------- */
  var conversas = $$('[data-conversa]');
  conversas.forEach(function (c) {
    c.addEventListener('click', function () {
      conversas.forEach(function (x) { x.classList.toggle('ativo', x === c); });
      var alvo = c.getAttribute('data-conversa');
      $$('[data-thread]').forEach(function (t) { t.hidden = t.getAttribute('data-thread') !== alvo; });
      var nl = $('.nv-wa-nao-lidas', c);
      if (nl) nl.remove();
      var msgs = $('[data-thread="' + alvo + '"] .nv-wa-msgs');
      if (msgs) msgs.scrollTop = msgs.scrollHeight;
    });
  });
  function rolarConversas() { $$('.nv-wa-msgs').forEach(function (m) { m.scrollTop = m.scrollHeight; }); }
  rolarConversas();
  window.addEventListener('load', rolarConversas);

  /* Resposta do agente de IA (simulada) a partir do que se digita */
  function respostaAgente(texto) {
    var t = texto.toLowerCase();
    if (/gelo/.test(t)) return 'Temos sim! 🧊 Gelo Cubo Cristal 5kg sai por R$ 14,00. Quer que eu coloque no pedido? Quantos pacotes?';
    if (/cerveja|heineken|brahma|spaten|fardo/.test(t)) return 'Hoje temos:\n• Fardo Heineken Lata c/ 12 — R$ 69,90\n• Fardo Spaten Lata c/ 12 — R$ 56,90\n• Fardo Brahma Duplo Malte c/ 12 — R$ 49,90\nQual vai ser? 🍺';
    if (/hor[aá]rio|abre|fecha|aberto/.test(t)) return 'Estamos abertos hoje até as 23h. Entregamos em até 40 minutos no raio de 5 km 🛵';
    if (/entrega|taxa|frete/.test(t)) return 'A taxa de entrega é R$ 5,00 até 3 km e R$ 8,00 até 5 km. Acima de R$ 150,00 a entrega é grátis! 🎉';
    if (/pix|cart[aã]o|pagamento|pagar/.test(t)) return 'Aceitamos Pix, cartão na entrega (débito e crédito) e dinheiro. Se for dinheiro, me fala se precisa de troco 😉';
    if (/obrigad|valeu/.test(t)) return 'Nós que agradecemos! Qualquer coisa é só chamar aqui 🙌';
    return 'Entendi! Vou te ajudar com isso. Posso te mandar a lista de produtos e preços de hoje ou já montar seu pedido 😊';
  }
  $$('[data-wa-form]').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var inp = $('input', f);
      var txt = (inp.value || '').trim();
      if (!txt) return;
      var msgs = $('.nv-wa-msgs', f.closest('[data-thread]') || f.closest('.nv-wa-thread') || document);
      var modo = f.getAttribute('data-wa-form');
      var hora = new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
      var m = document.createElement('div');
      m.className = 'nv-msg ' + (modo === 'teste' ? '' : 'saida');
      m.innerHTML = (modo === 'teste' ? '' : '<span class="quem">Você (loja)</span>') + '';
      m.appendChild(document.createTextNode(txt));
      var h = document.createElement('span'); h.className = 'hora'; h.textContent = hora; m.appendChild(h);
      msgs.appendChild(m);
      inp.value = '';
      msgs.scrollTop = msgs.scrollHeight;
      if (modo === 'teste') {
        var dig = document.createElement('div'); dig.className = 'nv-wa-digitando'; dig.textContent = 'Agente de IA digitando…';
        msgs.appendChild(dig); msgs.scrollTop = msgs.scrollHeight;
        setTimeout(function () {
          dig.remove();
          var r = document.createElement('div'); r.className = 'nv-msg saida';
          r.innerHTML = '<span class="quem">Agente de IA</span>';
          r.appendChild(document.createTextNode(respostaAgente(txt)));
          var h2 = document.createElement('span'); h2.className = 'hora'; h2.textContent = hora; r.appendChild(h2);
          msgs.appendChild(r); msgs.scrollTop = msgs.scrollHeight;
        }, 1100);
      }
    });
  });
  $$('[data-assumir]').forEach(function (b) {
    b.addEventListener('click', function () {
      var assumido = b.getAttribute('data-estado') === 'humano';
      b.setAttribute('data-estado', assumido ? 'ia' : 'humano');
      b.textContent = assumido ? 'Assumir conversa' : 'Devolver para a IA';
      var tag = $('[data-tag-atendimento]', b.closest('.nv-wa-thread'));
      if (tag) { tag.className = 'nv-tag ' + (assumido ? 'ia' : 'info'); tag.textContent = assumido ? 'Agente de IA atendendo' : 'Você está atendendo'; }
      toast(assumido ? 'Conversa devolvida para o agente de IA.' : 'Você assumiu a conversa. A IA fica em silêncio.');
    });
  });

  /* ---------- Sugestões (aceitar / dispensar) ---------- */
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-sugestao]');
    if (!b) return;
    var card = b.closest('.nv-sugestao');
    var ok = b.getAttribute('data-sugestao') === 'aceitar';
    card.classList.add('aceita');
    $$('button', card).forEach(function (x) { x.disabled = true; });
    var t = $('.nv-tag', card);
    if (t) { t.className = 'nv-tag ' + (ok ? 'ok' : ''); t.textContent = ok ? 'Aceita' : 'Dispensada'; }
    toast(ok ? (b.getAttribute('data-msg') || 'Sugestão aceita.') : 'Sugestão dispensada.');
  });

  /* ---------- Cardápio no celular: carrinho ---------- */
  var carrinho = $('[data-carrinho]');
  if (carrinho) {
    var total = 0, itens = 0;
    $$('.nv-cel-mais').forEach(function (b) {
      b.addEventListener('click', function () {
        total += parseFloat(b.getAttribute('data-preco'));
        itens += 1;
        carrinho.hidden = false;
        $('[data-carrinho-itens]', carrinho).textContent = itens + (itens === 1 ? ' item' : ' itens');
        $('[data-carrinho-total]', carrinho).textContent = brl(total);
      });
    });
  }

  /* ---------- White Label (identidade.html) ---------- */
  var formMarca = $('[data-identidade]');
  if (formMarca && window.MarcaDemo) {
    var padrao = { nome: 'SUA MARCA', primaria: '#0D6EFD', destaque: '#F97316', menu: '#1E293B', logo: '' };
    var atual = Object.assign({}, padrao, window.MarcaDemo.ler() || {});
    var campos = {
      nome: $('[name=nome]', formMarca), primaria: $('[name=primaria]', formMarca),
      destaque: $('[name=destaque]', formMarca), menu: $('[name=menu]', formMarca)
    };
    var logoImg = $$('[data-previa-logo]');
    function lum(hex) {
      var h = hex.replace('#', ''); var n = parseInt(h, 16);
      return [(n >> 16) & 255, (n >> 8) & 255, n & 255].map(function (v) { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); })
        .reduce(function (a, v, i) { return a + v * [0.2126, 0.7152, 0.0722][i]; }, 0);
    }
    function contraste(a, b) { var x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); }
    function avaliar() {
      var alvo = $('[data-contraste]');
      if (!alvo) return;
      var c1 = contraste(atual.primaria, '#FFFFFF');
      var c2 = contraste(atual.menu, '#FFFFFF');
      function tag(nome, r, min) {
        var ok = r >= min;
        return '<span class="nv-tag ' + (ok ? 'ok' : 'aviso') + '">' + (ok ? '✓ ' : '! ') + nome + ' ' + r.toFixed(1) + ':1' + (ok ? '' : ' (mín. ' + min + ':1)') + '</span>';
      }
      alvo.innerHTML = tag('Botões e texto da cor principal', c1, 3) + tag('Menu lateral', c2, 4.5);
    }
    function preencher() {
      campos.nome.value = atual.nome;
      ['primaria', 'destaque', 'menu'].forEach(function (k) {
        campos[k].value = atual[k];
        var rot = $('[data-hex="' + k + '"]'); if (rot) rot.textContent = atual[k].toUpperCase();
      });
      $$('[data-previa-nome]').forEach(function (el) { el.textContent = atual.nome || 'SUA MARCA'; });
      logoImg.forEach(function (img) { img.src = atual.logo || './static/img/logo-marca.svg'; });
      window.MarcaDemo.aplicarCores(atual);
      avaliar();
    }
    ['primaria', 'destaque', 'menu'].forEach(function (k) {
      campos[k].addEventListener('input', function () {
        atual[k] = campos[k].value; preencher();
        $$('.nv-tema').forEach(function (t) { t.classList.remove('ativo'); });
      });
    });
    campos.nome.addEventListener('input', function () { atual.nome = campos.nome.value; $$('[data-previa-nome]').forEach(function (el) { el.textContent = atual.nome || 'SUA MARCA'; }); });
    $$('.nv-tema').forEach(function (t) {
      t.addEventListener('click', function () {
        atual.primaria = t.getAttribute('data-primaria');
        atual.destaque = t.getAttribute('data-destaque');
        atual.menu = t.getAttribute('data-menu');
        $$('.nv-tema').forEach(function (x) { x.classList.toggle('ativo', x === t); });
        preencher();
      });
    });
    var arq = $('[data-logo-arquivo]');
    if (arq) arq.addEventListener('change', function () {
      var f = arq.files && arq.files[0];
      if (!f) return;
      var r = new FileReader();
      r.onload = function () { atual.logo = r.result; preencher(); };
      r.readAsDataURL(f);
    });
    formMarca.addEventListener('submit', function (e) {
      e.preventDefault();
      window.MarcaDemo.salvar(atual);
      toast('Marca aplicada em todo o sistema: menu, botões, cupom, cardápio e página da loja.');
      setTimeout(function () { location.reload(); }, 900);
    });
    var restaurar = $('[data-restaurar-marca]');
    if (restaurar) restaurar.addEventListener('click', function () {
      window.MarcaDemo.limpar();
      toast('Marca padrão restaurada.');
      setTimeout(function () { location.reload(); }, 700);
    });
    preencher();
  }
})();
