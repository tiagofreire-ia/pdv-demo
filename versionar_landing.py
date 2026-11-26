"""(rode na raiz do app-demo: python versionar_landing.py)
Coloca ?v=<hash do conteúdo> nas fotos da landing e no PDF do deck, para o cache do navegador
nunca mostrar uma versão velha. Pode rodar de novo sempre que as fotos ou o deck mudarem."""
import hashlib, json, pathlib, re, sys

raiz = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "telas_estaticas")
pasta = raiz / "static/img/landing"
h = lambda p: hashlib.md5(p.read_bytes()).hexdigest()[:8]
versoes = {p.stem: h(p) for p in sorted(pasta.glob("*.jpg"))}
pdf = h(raiz / "static/deck/Optima-PDV-Deck.pdf")

for nome in ("landing.html", "index.html"):
    arq = raiz / nome; t = arq.read_text(encoding="utf-8")
    # src das fotos no HTML
    t = re.sub(r'(\./static/img/landing/)([\w]+)\.jpg(\?v=[0-9a-f]+)?"', lambda m: f'{m.group(1)}{m.group(2)}.jpg?v={versoes[m.group(2)]}"', t)
    # PDF do deck
    t = re.sub(r'\./static/deck/Optima-PDV-Deck\.pdf(\?v=[0-9a-f]+)?"', f'./static/deck/Optima-PDV-Deck.pdf?v={pdf}"', t)
    # mapa de versões usado pela troca de tema
    mapa = "var VERSOES = " + json.dumps(versoes, separators=(",", ":")) + ";"
    if "var VERSOES = " in t:
        t = re.sub(r"var VERSOES = \{.*?\};", mapa, t)
    else:
        a = '    var raiz = document.documentElement, btn = document.getElementById("tema-btn");'
        assert t.count(a) == 1; t = t.replace(a, "    " + mapa + "\n" + a)
        a = '''        var novo = "./static/img/landing/" + i.getAttribute("data-tela") + (claro() ? "_claro" : "") + ".jpg";'''
        b = '''        var nome = i.getAttribute("data-tela") + (claro() ? "_claro" : "");
        var novo = "./static/img/landing/" + nome + ".jpg" + (VERSOES[nome] ? "?v=" + VERSOES[nome] : "");'''
        assert t.count(a) == 1; t = t.replace(a, b)
    arq.write_text(t, encoding="utf-8")
print(len(versoes), "fotos versionadas; pdf", pdf)
