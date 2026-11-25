/* White Label da demonstração: aplica nome, logo e cores da marca do cliente em TODAS as telas.
 * A marca é salva no navegador (localStorage) pela tela Identidade (identidade.html).
 * Também destaca no menu lateral o item da tela atual (nas telas estáticas o caminho é o arquivo). */
(function () {
  var CHAVE = 'marcaDemo';
  var NOME_PADRAO = 'SUA MARCA';
  var PROPS = ['--accent', '--ouro', '--primary', '--accent-text', '--ouro-texto', '--ouro-claro',
    '--ouro-texto-hover', '--focus-ring', '--orange', '--destaque-borda', '--destaque-muted',
    '--side-bg', '--side-pop', '--side-hover', '--side-line'];

  function ler() {
    try { return JSON.parse(localStorage.getItem(CHAVE) || 'null'); } catch (e) { return null; }
  }
  function rgba(hex, a) {
    var h = String(hex || '').replace('#', '');
    if (h.length === 3) h = h.replace(/(.)/g, '$1$1');
    var n = parseInt(h, 16);
    if (isNaN(n)) return hex;
    return 'rgba(' + ((n >> 16) & 255) + ',' + ((n >> 8) & 255) + ',' + (n & 255) + ',' + a + ')';
  }
  function misturar(hex, alvo, peso) {
    var h = String(hex || '').replace('#', ''), t = alvo.replace('#', '');
    var a = parseInt(h, 16), b = parseInt(t, 16);
    if (isNaN(a) || isNaN(b)) return hex;
    var r = Math.round(((a >> 16) & 255) * (1 - peso) + ((b >> 16) & 255) * peso);
    var g = Math.round(((a >> 8) & 255) * (1 - peso) + ((b >> 8) & 255) * peso);
    var bl = Math.round((a & 255) * (1 - peso) + (b & 255) * peso);
    return '#' + ((1 << 24) + (r << 16) + (g << 8) + bl).toString(16).slice(1);
  }
  function aplicarCores(m) {
    var s = document.documentElement.style;
    PROPS.forEach(function (p) { s.removeProperty(p); });
    if (!m) return;
    if (m.primaria) {
      ['--accent', '--ouro', '--primary', '--accent-text', '--ouro-texto', '--ouro-claro'].forEach(function (p) {
        s.setProperty(p, m.primaria);
      });
      s.setProperty('--ouro-texto-hover', misturar(m.primaria, '#000000', 0.15));
      s.setProperty('--focus-ring', rgba(m.primaria, 0.28));
    }
    if (m.destaque) {
      s.setProperty('--orange', m.destaque);
      s.setProperty('--destaque-borda', m.destaque);
      s.setProperty('--destaque-muted', m.destaque);
    }
    if (m.menu) {
      s.setProperty('--side-bg', m.menu);
      s.setProperty('--side-pop', m.menu);
      s.setProperty('--side-hover', misturar(m.menu, '#ffffff', 0.12));
      s.setProperty('--side-line', misturar(m.menu, '#ffffff', 0.12));
    }
  }
  function trocarTextos(m) {
    if (!m) return;
    var nome = (m.nome || '').trim();
    if (nome && nome !== NOME_PADRAO) {
      // Endereço da loja (suamarca.optimapdv.com.br) acompanha o nome da marca.
      var slug = nome.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '');
      if (document.title.indexOf(NOME_PADRAO) !== -1) document.title = document.title.split(NOME_PADRAO).join(nome);
      var w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null);
      var n;
      while ((n = w.nextNode())) {
        if (n.nodeValue.indexOf(NOME_PADRAO) !== -1) n.nodeValue = n.nodeValue.split(NOME_PADRAO).join(nome);
        if (slug && n.nodeValue.indexOf('suamarca.') !== -1) n.nodeValue = n.nodeValue.split('suamarca.').join(slug + '.');
      }
      if (slug) {
        document.querySelectorAll('input[value*="suamarca."]').forEach(function (el) { el.value = el.value.split('suamarca.').join(slug + '.'); });
      }
      document.querySelectorAll('[title*="' + NOME_PADRAO + '"],[placeholder*="' + NOME_PADRAO + '"]').forEach(function (el) {
        ['title', 'placeholder'].forEach(function (at) {
          var v = el.getAttribute(at);
          if (v) el.setAttribute(at, v.split(NOME_PADRAO).join(nome));
        });
      });
    }
    if (m.logo) {
      document.querySelectorAll('.side-mark, [data-marca-logo]').forEach(function (img) { img.src = m.logo; });
    }
  }
  function marcarAtivo() {
    var nav = document.querySelector('.side-nav');
    if (!nav) return;
    var atual = (location.pathname.split('/').pop() || 'index.html').replace(/\.html$/, '');
    var melhor = null, tam = 0;
    nav.querySelectorAll('a[href]').forEach(function (a) {
      var nomes = [(a.getAttribute('href') || '').split('/').pop().replace(/\.html$/, '')]
        .concat((a.getAttribute('data-ativo-arquivos') || '').split(',').filter(Boolean));
      nomes.forEach(function (base) {
        if (!base) return;
        if (atual === base || atual.indexOf(base + '_') === 0) {
          if (base.length > tam) { melhor = a; tam = base.length; }
        }
      });
    });
    if (melhor) {
      nav.querySelectorAll('a.ativo').forEach(function (a) { a.classList.remove('ativo'); });
      melhor.classList.add('ativo');
      var grupo = melhor.closest('details');
      if (grupo) grupo.open = true;
      if (!window.__menuRolagemRestaurada) { try { melhor.scrollIntoView({ block: 'nearest' }); } catch (e) {} }
    }
  }

  aplicarCores(ler());

  window.MarcaDemo = {
    padrao: NOME_PADRAO,
    ler: ler,
    aplicarCores: aplicarCores,
    salvar: function (m) {
      try { localStorage.setItem(CHAVE, JSON.stringify(m)); } catch (e) {}
      aplicarCores(m);
      trocarTextos(m);
    },
    limpar: function () {
      try { localStorage.removeItem(CHAVE); } catch (e) {}
      aplicarCores(null);
    }
  };

  document.addEventListener('DOMContentLoaded', function () {
    trocarTextos(ler());
    marcarAtivo();
  });
})();
