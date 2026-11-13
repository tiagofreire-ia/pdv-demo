// Leitor de código de barras pela câmera, comum ao cadastro de produto e à frente de caixa (spec 020).
// Spec 011 (E1): câmera traseira em 1280x720 com foco contínuo quando existir, só formatos de produto
// (EAN/UPC/Code-128), leitor nativo do navegador (BarcodeDetector) quando houver e a ZXing como reserva
// (a página carrega a ZXing de static/vendor). Só funciona em endereço seguro (https ou localhost).
//
//   var leitor = LeitorCamera(videoEl, { aoLer: function (codigo) {...}, aoAvisar: function (texto) {...} });
//   leitor.iniciar();   // abre a câmera e começa a ler
//   leitor.pausar();    // para de ler, a câmera continua aberta (imagem congelada)
//   leitor.retomar();   // volta a ler
//   leitor.parar();     // fecha a câmera
(function () {
  var FORMATOS_NATIVOS = ["ean_13", "ean_8", "upc_a", "upc_e", "code_128"];
  var INTERVALO_LEITURA_MS = 120;
  var RESTRICOES = {
    audio: false,
    video: {
      facingMode: { ideal: "environment" },
      width: { ideal: 1280 }, height: { ideal: 720 },
      advanced: [{ focusMode: "continuous" }],
    },
  };

  function mensagemErro(err) {
    var nome = err && err.name;
    return {
      NotAllowedError: "Permissão da câmera negada. Libere no cadeado ao lado do endereço e tente de novo.",
      SecurityError: "Permissão da câmera negada. Libere no cadeado ao lado do endereço e tente de novo.",
      NotFoundError: "Nenhuma câmera encontrada neste aparelho.",
      OverconstrainedError: "Nenhuma câmera compatível encontrada neste aparelho.",
      NotReadableError: "A câmera está em uso por outro programa ou aba. Feche-o e tente de novo.",
    }[nome] || "Não consegui acessar a câmera (" + (nome || err) + ").";
  }

  window.LeitorCamera = function (video, opcoes) {
    opcoes = opcoes || {};
    var aoLer = opcoes.aoLer || function () {};
    var aoAvisar = opcoes.aoAvisar || function () {};
    var fluxo = null, leitorZxing = null, detector = null, timer = null;
    var aberto = false, lendo = false;

    function lido(texto) {
      if (!lendo || !texto) return;
      lendo = false;  // quem chamou decide se retoma
      if (navigator.vibrate) { try { navigator.vibrate(80); } catch (e) {} }
      aoLer(String(texto).trim());
    }

    // Leitor nativo (Chrome/Edge no Android e alguns desktops): rápido e preciso.
    function quadroNativo() {
      if (!aberto) return;
      if (!lendo || video.readyState < 2) { timer = setTimeout(quadroNativo, INTERVALO_LEITURA_MS); return; }
      detector.detect(video).then(function (codigos) {
        if (codigos && codigos.length) lido(codigos[0].rawValue);
        timer = setTimeout(quadroNativo, INTERVALO_LEITURA_MS);
      }).catch(function () { timer = setTimeout(quadroNativo, INTERVALO_LEITURA_MS); });
    }

    // Reserva: ZXing só com os formatos de produto e "tentar mais" ligado.
    function lerComZxing() {
      if (typeof ZXing === "undefined") {
        aoAvisar("Leitor de código não carregou. Verifique a conexão com a internet e recarregue a página.");
        return;
      }
      var dicas = new Map();
      var F = ZXing.BarcodeFormat;
      dicas.set(ZXing.DecodeHintType.POSSIBLE_FORMATS, [F.EAN_13, F.EAN_8, F.UPC_A, F.UPC_E, F.CODE_128]);
      dicas.set(ZXing.DecodeHintType.TRY_HARDER, true);
      leitorZxing = new ZXing.BrowserMultiFormatReader(dicas, INTERVALO_LEITURA_MS);
      leitorZxing.timeBetweenDecodingAttempts = INTERVALO_LEITURA_MS;
      leitorZxing.decodeFromStream(fluxo, video, function (resultado) {
        if (resultado) lido(resultado.getText());
      }).catch(function (err) { if (aberto) aoAvisar(mensagemErro(err)); });
    }

    function comecarLeitura() {
      if ("BarcodeDetector" in window && window.BarcodeDetector.getSupportedFormats) {
        window.BarcodeDetector.getSupportedFormats().then(function (suportados) {
          var formatos = FORMATOS_NATIVOS.filter(function (f) { return suportados.indexOf(f) !== -1; });
          if (formatos.indexOf("ean_13") !== -1) {
            detector = new window.BarcodeDetector({ formats: formatos });
            quadroNativo();
          } else {
            lerComZxing();
          }
        }).catch(lerComZxing);
      } else {
        lerComZxing();
      }
    }

    function iniciar() {
      if (!window.isSecureContext) {
        aoAvisar("A câmera só funciona no endereço seguro do sistema (https). Abra o sistema pelo endereço com https e tente de novo.");
        return false;
      }
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        aoAvisar("Este navegador não permite usar a câmera. Use o Chrome ou o Edge atualizados.");
        return false;
      }
      aberto = true;
      lendo = true;
      navigator.mediaDevices.getUserMedia(RESTRICOES).catch(function () {
        // Alguns aparelhos recusam as restrições avançadas: tenta só a câmera traseira.
        return navigator.mediaDevices.getUserMedia({ audio: false, video: { facingMode: { ideal: "environment" } } });
      }).then(function (stream) {
        if (!aberto) { stream.getTracks().forEach(function (t) { t.stop(); }); return; }
        fluxo = stream;
        video.setAttribute("playsinline", "");
        video.muted = true;
        video.srcObject = stream;
        var tocar = video.play();
        if (tocar && tocar.catch) tocar.catch(function () {});
        comecarLeitura();
      }).catch(function (err) {
        if (window.console) console.error("Câmera:", err);
        aoAvisar(mensagemErro(err));
      });
      return true;
    }

    function parar() {
      aberto = false;
      lendo = false;
      clearTimeout(timer);
      if (leitorZxing) { try { leitorZxing.reset(); } catch (e) {} leitorZxing = null; }
      detector = null;
      if (fluxo) { fluxo.getTracks().forEach(function (t) { t.stop(); }); fluxo = null; }
      video.srcObject = null;
    }

    return {
      iniciar: iniciar,
      parar: parar,
      pausar: function () { lendo = false; if (video.pause) video.pause(); },
      retomar: function () {
        if (!aberto) return;
        var tocar = video.play && video.play();
        if (tocar && tocar.catch) tocar.catch(function () {});
        lendo = true;
      },
      aberto: function () { return aberto; },
    };
  };
})();
