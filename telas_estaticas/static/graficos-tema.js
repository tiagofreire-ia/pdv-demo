// Cores dos gráficos (Chart.js) a partir dos tokens do style.css — acompanham o tema
// claro/escuro e a paleta moderna. Carregar logo depois
// do chart.umd.min.js; as telas usam window.CORES_GRAFICO em vez de cores fixas.
(function () {
  var css = getComputedStyle(document.documentElement);
  function token(nome) { return css.getPropertyValue(nome).trim(); }
  // Canvas não entende color-mix(): transparência feita à mão a partir do hex.
  function comAlfa(hex, alfa) {
    var h = hex.replace("#", "");
    if (h.length === 3) h = h.replace(/./g, "$&$&");
    var n = parseInt(h, 16);
    return "rgba(" + (n >> 16 & 255) + "," + (n >> 8 & 255) + "," + (n & 255) + "," + alfa + ")";
  }

  window.CORES_GRAFICO = {
    principal: token("--accent") || "#0D6EFD",       // série principal (faturamento - azul vibrante)
    destaque: "#F97316",                             // pico / destaque (laranja coral vibrante)
    lucro: token("--success") || "#10B981",
    neutro: token("--muted") || "#64748B",
    // Séries de categoria (formas de pagamento):
    categorias: ["#0D6EFD", "#F97316", "#10B981", "#64748B",
                 "#EF4444", "#0284C7", "#CBD5E1"],
    principalTransparente: comAlfa(token("--accent") || "#0D6EFD", 0.65),
    // Preenchimento das barras: degradê vertical, da cor cheia no topo para 45% embaixo. Uso:
    // backgroundColor: CORES_GRAFICO.degrade("#C9A13B") ou degrade(function (i) { return cor da barra i; }).
    degrade: function (cor) {
      return function (c) {
        var base = typeof cor === "function" ? cor(c.dataIndex) : cor;
        var area = c.chart.chartArea;
        if (!area || !/^#/.test(base)) return base;  // 1º desenho (sem área ainda) ou cor que não é hex
        var g = c.chart.ctx.createLinearGradient(0, area.bottom, 0, area.top);
        g.addColorStop(0, comAlfa(base, 0.45));
        g.addColorStop(1, base);
        return g;
      };
    },
    // Entrada das barras: crescem uma depois da outra (sem animação para quem pediu menos movimento).
    animacao: function () {
      if (window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches) return false;
      return {
        duration: 1000, easing: "easeOutQuart",
        delay: function (c) { return c.type === "data" && c.mode === "default" ? c.dataIndex * 70 + c.datasetIndex * 120 : 0; },
      };
    },
  };

  if (window.Chart) {
    Chart.defaults.font.family = '"Manrope", system-ui, sans-serif';
    Chart.defaults.color = token("--muted");
    Chart.defaults.borderColor = token("--line");
  }
})();
