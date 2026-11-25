"""Conteúdo das telas novas da demonstração (recursos do Óptima PDV) no padrão visual atual.

Cada tela é (título da aba, HTML do conteúdo). Os dados seguem a loja de bebidas da demo
(mesmos produtos e clientes do banco `demo_bebidas.db`), com "hoje" = sexta, 06/11/2026.
"""
from __future__ import annotations

import random


# ----------------------------------------------------------------------------------------------
# Peças reutilizáveis
# ----------------------------------------------------------------------------------------------
def tag(cls: str, txt: str) -> str:
    return f'<span class="nv-tag {cls}">{txt}</span>'


def topo(titulo: str, sub: str = "", acoes: str = "") -> str:
    sub_html = f'<span class="muted">{sub}</span>' if sub else ""
    acoes_html = f'<div class="pr-acoes nv-acoes-topo">{acoes}</div>' if acoes else ""
    return (
        '<div class="pr-topo">\n'
        f'    <div class="en-titulo">\n      <h1>{titulo}</h1>\n      {sub_html}\n    </div>\n'
        f"    {acoes_html}\n  </div>"
    )


def kpis(itens) -> str:
    blocos = []
    for i, it in enumerate(itens):
        rotulo, valor, apoio = it[0], it[1], it[2]
        destaque = " destaque" if (len(it) > 3 and it[3]) or i == 0 else ""
        blocos.append(
            f'<div class="nv-kpi{destaque}"><span class="rotulo">{rotulo}</span>'
            f"<strong>{valor}</strong><span class=\"apoio\">{apoio}</span></div>"
        )
    return '<div class="nv-kpis">' + "".join(blocos) + "</div>"


def card(titulo: str, corpo: str, direita: str = "", extra: str = "") -> str:
    return (
        f'<div class="card"{extra}>\n  <div class="card-cabeca"><h2>{titulo}</h2>{direita}</div>\n'
        f"  {corpo}\n</div>"
    )


def btn(txt: str, cls: str = "btn-principal", toast: str = "") -> str:
    t = f' data-toast="{toast}"' if toast else ""
    return f'<button type="button" class="{cls}"{t}>{txt}</button>'


def switch(nome: str, ligado: bool = True) -> str:
    chk = " checked" if ligado else ""
    return f'<label class="nv-switch"><input type="checkbox" data-nome="{nome}"{chk} aria-label="{nome}"><span></span></label>'


# ----------------------------------------------------------------------------------------------
# Seletor de módulos (padrão único: Nova loja, Plano e módulos, ficha da loja no Master)
# ----------------------------------------------------------------------------------------------
_ICO_MOD = {
    "caixa": '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/>',
    "estoque": '<rect x="3" y="4" width="18" height="5" rx="1"/><path d="M5 9v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V9"/><path d="M10 13h4"/>',
    "clientes": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16 4.6a3.5 3.5 0 0 1 0 6.8"/><path d="M18.5 20a6.5 6.5 0 0 0-2.5-5.2"/>',
    "fiscal": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M9 13h6M9 17h4"/>',
    "balanca": '<path d="M12 3v18M7 21h10M5 7h14"/><path d="M5 7l-3 6a3 3 0 0 0 6 0z"/><path d="M19 7l-3 6a3 3 0 0 0 6 0z"/>',
    "producao": '<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4V3h6v1"/><path d="M9 11l2 2 4-4M9 17h6"/>',
    "cardapio": '<rect x="6" y="2" width="12" height="20" rx="2"/><path d="M11 18h2"/>',
    "comandas": '<path d="M2 4h7a3 3 0 0 1 3 3v13a2 2 0 0 0-2-2H2z"/><path d="M22 4h-7a3 3 0 0 0-3 3v13a2 2 0 0 1 2-2h8z"/>',
    "delivery": '<path d="M2 6h11v10H2z"/><path d="M13 9h4l4 4v3h-8"/><circle cx="6" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>',
    "whatsapp": '<path d="M21 12a8 8 0 0 1-8 8H7l-4 3V12a8 8 0 0 1 8-8h2a8 8 0 0 1 8 8z"/><path d="M8 11h.01M12 11h.01M16 11h.01"/>',
    "fidelidade": '<rect x="3" y="8" width="18" height="4" rx="1"/><path d="M12 8v13M5 12v8a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-8"/><path d="M7.5 8a2.5 2.5 0 0 1 0-5C10 3 12 8 12 8s2-5 4.5-5a2.5 2.5 0 0 1 0 5"/>',
    "grade": '<path d="M17 3l4 4-4 4"/><path d="M3 7h18"/><path d="M7 21l-4-4 4-4"/><path d="M21 17H3"/>',
    "inteligencia": '<path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"/><path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z"/>',
}

# (chave, nome, descrição, é IA?, incluído no plano?)
CATALOGO_MODULOS = [
    ("caixa", "Frente de caixa", "Vendas rápidas no balcão e fechamento de caixa.", False, True),
    ("estoque", "Estoque, lotes e validade", "Controle de entradas, saídas e alertas de vencimento.", False, True),
    ("clientes", "Clientes e Confiança", "Cadastro, histórico de compras e gestão de fiado.", False, True),
    ("fiscal", "Nota fiscal NFC-e", "Emissão automática de cupom fiscal eletrônico.", False, False),
    ("balanca", "Balança e etiquetas", "Integração com balanças e impressão de códigos.", False, False),
    ("producao", "Produção e encomendas", "Ficha técnica, ordens de preparo e agendamentos.", False, False),
    ("cardapio", "Cardápio digital e Minha página", "Vitrine online com link próprio e pedidos diretos.", False, False),
    ("comandas", "Comandas e cozinha", "Gestão de mesas e envio de pedidos para preparo.", False, False),
    ("delivery", "Delivery", "Taxas por bairro, motoboys e status de entrega.", False, False),
    ("whatsapp", "WhatsApp com agente de IA", "Atendimento automático e pedidos direto no WhatsApp.", True, False),
    ("fidelidade", "Fidelidade e campanhas", "Pontos, cashback e cupons para reter clientes.", False, False),
    ("grade", "Grade e trocas", "Variações de cor/tamanho e devoluções ágeis.", False, False),
    ("inteligencia", "Inteligência e assistente de IA", "Insights de vendas, alertas e copiloto gerencial.", True, False),
]


def _ico_mod(k: str) -> str:
    return ('<span class="nv-mod-ico" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{_ICO_MOD[k]}</svg></span>')


def seletor_modulos(ligados, titulo: str, sub: str, nota: str, acoes: str, precos: dict | None = None) -> str:
    """Bloco completo: cabeçalho com contador, módulos incluídos (fixos) e adicionais (marcáveis), rodapé."""
    precos = precos or {}
    base = [m for m in CATALOGO_MODULOS if m[4]]
    extras = [m for m in CATALOGO_MODULOS if not m[4]]
    total = len(base) + sum(1 for m in extras if m[0] in ligados)
    cards_base = "".join(
        f'<div class="nv-mod nv-mod-base">{_ico_mod(k)}<span class="nv-mod-incluso">✓ Incluso</span>'
        f'<b class="nv-mod-nome">{n}</b><span class="nv-mod-desc">{d}</span></div>'
        for k, n, d, ia, _ in base
    )
    cards_extra = "".join(
        f'<label class="nv-mod nv-mod-extra">{_ico_mod(k)}<span class="nv-mod-texto">'
        f'<b class="nv-mod-nome">{n}{" <em class=nv-mod-ia>IA</em>" if ia else ""}</b><span class="nv-mod-desc">{d}</span>'
        + (f'<span class="nv-mod-preco">{precos[k]}</span>' if k in precos else "")
        + f'</span><input type="checkbox" data-modulo="{k}" data-base="nao"{" checked" if k in ligados else ""} aria-label="{n}"></label>'
        for k, n, d, ia, _ in extras
    )
    return (
        '<div class="nv-mods" data-seletor-modulos>'
        f'<div class="nv-mods-cabeca"><div><h2>{titulo}</h2><p>{sub}</p></div>'
        f'<span class="nv-mods-contador"><i></i><span><span data-contador-modulos>{total}</span> módulos ativos</span></span></div>'
        '<div class="nv-mods-secao"><span class="nv-mods-rotulo">Incluídos no seu plano</span><span class="nv-mods-sempre">Sempre ativos</span></div>'
        f'<div class="nv-mods-grade base">{cards_base}</div>'
        '<div class="nv-mods-secao"><span class="nv-mods-rotulo">Módulos adicionais</span>'
        '<span class="nv-mods-links"><button type="button" data-mods-todos>Ativar todos</button><i>•</i>'
        '<button type="button" data-mods-limpar>Limpar opcionais</button></span></div>'
        f'<div class="nv-mods-grade extra">{cards_extra}</div>'
        f'<div class="nv-mods-rodape"><span>{nota}</span><div class="nv-acoes-topo">{acoes}</div></div>'
        "</div>"
    )


SETA = ' <span aria-hidden="true">→</span>'


def qr(semente: int = 7) -> str:
    """QR Code ILUSTRATIVO (padrão visual, não codifica nada)."""
    rnd = random.Random(semente)
    n = 21
    celulas = []
    for y in range(n):
        for x in range(n):
            def finder(cx, cy):
                dx, dy = x - cx, y - cy
                if 0 <= dx < 7 and 0 <= dy < 7:
                    borda = dx in (0, 6) or dy in (0, 6)
                    miolo = 2 <= dx <= 4 and 2 <= dy <= 4
                    return borda or miolo
                return None
            v = None
            for cx, cy in ((0, 0), (14, 0), (0, 14)):
                r = finder(cx, cy)
                if r is not None:
                    v = r
            if v is None:
                if (x < 8 and y < 8) or (x > 12 and y < 8) or (x < 8 and y > 12):
                    v = False
                else:
                    v = rnd.random() < 0.48
            celulas.append("<i></i>" if v else '<i class="b"></i>')
    return '<div class="nv-qr" aria-label="QR Code">' + "".join(celulas) + "</div>"


def tabela(cabecalho, linhas, classe_num=()) -> str:
    ths = "".join(f'<th class="num">{c}</th>' if i in classe_num else f"<th>{c}</th>" for i, c in enumerate(cabecalho))
    trs = []
    for linha in linhas:
        tds = "".join(f'<td class="num">{c}</td>' if i in classe_num else f"<td>{c}</td>" for i, c in enumerate(linha))
        trs.append(f"<tr>{tds}</tr>")
    return (
        '<div class="tabela-rolagem"><table class="tabela pr-tabela">'
        f"<thead><tr>{ths}</tr></thead><tbody>{''.join(trs)}</tbody></table></div>"
    )


def barras(dados, altura_max=None, fmt=lambda v: v, classe=lambda i, v: "") -> str:
    mx = altura_max or max(v for _, v in dados) or 1
    cols = []
    for i, (rot, v) in enumerate(dados):
        h = max(3, abs(v) / mx * 100)
        cols.append(
            f'<div class="col"><span class="v">{fmt(v)}</span>'
            f'<div class="b {classe(i, v)}" style="height:{h:.0f}%"></div><span class="r">{rot}</span></div>'
        )
    return '<div class="nv-barras">' + "".join(cols) + "</div>"


def pagina(classe: str, corpo: str) -> str:
    return f'<div class="page produtos-tela {classe}">\n{corpo}\n</div>'


# ----------------------------------------------------------------------------------------------
# 1. Comandas e mesas
# ----------------------------------------------------------------------------------------------
MESAS = [
    ("1", "ocupada", "Quadra Society Arena Gol", 186.40, "1h12", [("6", "Heineken Long Neck 330ml", 45.00), ("2", "Porção de calabresa", 69.80), ("1", "Gelo Cubo Cristal 5kg", 14.00), ("4", "Água Mineral com Gás", 14.00), ("1", "Copão Gin Tônica", 43.60)]),
    ("2", "livre", "", 0, "", []),
    ("3", "conta", "Marcelo Tavares", 94.30, "52 min", [("4", "Spaten Puro Malte Lata", 20.80), ("2", "Copão Caipirinha", 39.80), ("1", "Porção de batata", 33.70)]),
    ("4", "ocupada", "Mesa 4", 61.70, "25 min", [("2", "Corona Extra Long Neck", 17.00), ("1", "Porção de batata", 33.70), ("1", "Coca-Cola Lata", 4.50), ("1", "Água Tônica", 6.50)]),
    ("5", "livre", "", 0, "", []),
    ("6", "ocupada", "Rodrigo Eventos", 238.90, "1h40", [("1", "Whisky Johnnie Walker Red 1L", 109.90), ("2", "Red Bull Lata", 21.80), ("1", "Gelo Cubo Cristal 5kg", 14.00), ("3", "Porção de calabresa", 93.20)]),
    ("7", "ocupada", "Balcão 7", 42.60, "8 min", [("6", "Amstel Lata 473ml", 33.00), ("1", "Amendoim torrado", 9.60)]),
    ("8", "livre", "", 0, "", []),
    ("9", "ocupada", "Espetinho do Alemão", 156.20, "38 min", [("12", "Brahma Duplo Malte Lata", 54.00), ("2", "Gelo Cubo Cristal 5kg", 28.00), ("1", "Cachaça Salinas 670ml", 54.90), ("4", "Guaraná Antarctica Lata", 19.30)]),
    ("10", "conta", "Juliana Costa", 62.40, "47 min", [("1", "Vinho Chileno Cabernet 750ml", 39.90), ("5", "Coca-Cola Lata", 22.50)]),
    ("11", "livre", "", 0, "", []),
    ("12", "livre", "", 0, "", []),
]


def brl(v: float) -> str:
    s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"


def tela_comandas() -> str:
    abertas = [m for m in MESAS if m[1] != "livre"]
    consumo = sum(m[3] for m in abertas)
    cards = []
    for num, st, cliente, total, tempo, _itens in MESAS:
        if st == "livre":
            cards.append(f'<button type="button" class="nv-mesa livre" data-mesa="{num}"><div class="num"><span>Mesa {num}</span></div><div class="total">Livre</div><small>toque para abrir</small></button>')
        else:
            selo = tag("aviso", "conta pedida") if st == "conta" else tag("info", tempo)
            ativa = " ativa" if num == "1" else ""
            cards.append(
                f'<button type="button" class="nv-mesa {st}{ativa}" data-mesa="{num}"><div class="num"><span>Mesa {num}</span>{selo}</div>'
                f'<small>{cliente}</small><div class="total">{brl(total)}</div></button>'
            )
    paineis = []
    for num, st, cliente, total, tempo, itens in MESAS:
        oculto = "" if num == "1" else " hidden"
        if st == "livre":
            corpo = (f'<p class="muted">Mesa livre.</p>'
                     f'{btn("Abrir comanda", "btn-principal btn-alto", "Comanda aberta na mesa " + num + ". Agora é só lançar os itens.")}')
        else:
            linhas = "".join(f'<tr><td><b>{q}×</b> {n}</td><td class="num">{brl(v)}</td></tr>' for q, n, v in itens)
            taxa = total * 0.10
            corpo = (
                f'<p class="muted small">{cliente} · aberta há {tempo} · garçom: Lucas</p>'
                f'<table class="nv-itens"><tbody>{linhas}</tbody>'
                f'<tfoot><tr><td>Subtotal</td><td class="num">{brl(total)}</td></tr>'
                f'<tr><td class="muted" style="font-weight:500;font-size:14px">Serviço (10%, opcional)</td><td class="num muted" style="font-size:14px">{brl(taxa)}</td></tr></tfoot></table>'
                '<div class="nv-acoes-topo" style="margin-top:14px">'
                f'{btn("+ Lançar item", "btn-secundario", "No sistema, o garçom lança pelo celular e o pedido vai direto para a tela do bar.")}'
                f'{btn("Dividir conta", "btn-secundario", "Conta dividida em partes iguais ou por item.")}'
                f'{btn("Fechar no caixa", "btn-principal", "Comanda enviada para o caixa: é só receber no Pix, cartão ou dinheiro.")}'
                "</div>"
            )
        paineis.append(f'<div data-comanda="{num}"{oculto}><div class="card-cabeca"><h2>Mesa {num}</h2>{tag("aviso", "conta pedida") if st == "conta" else ""}</div>{corpo}</div>')

    corpo = (
        topo("Comandas e mesas", "Atendimento no salão: o garçom lança pelo celular, o pedido aparece na cozinha/bar e a conta fecha no caixa.",
             btn("+ Abrir comanda", "btn-principal btn-alto", "Comanda aberta. Escolha a mesa ou o nome do cliente."))
        + kpis([
            ("Mesas ocupadas", f"{len(abertas)} de {len(MESAS)}", "2 pediram a conta"),
            ("Consumo em aberto", brl(consumo), "ainda não recebido"),
            ("Tempo médio por mesa", "54 min", "ticket médio R$ 118,40"),
            ("Comandas hoje", "23", "<b class=\"ok\">+18%</b> sobre a sexta passada"),
        ])
        + '<div class="nv-grade-lado"><div class="card"><div class="card-cabeca"><h2>Salão</h2>'
        '<span class="muted small">toque numa mesa para ver a comanda</span></div>'
        f'<div class="nv-mesas">{"".join(cards)}</div></div>'
        f'<div class="card">{"".join(paineis)}</div></div>'
    )
    return pagina("nv-comandas", corpo)


# ----------------------------------------------------------------------------------------------
# 2. Cozinha / Bar (KDS)
# ----------------------------------------------------------------------------------------------
def pedido_kds(numero, origem, itens, minutos, limite, obs="", proximo=None, atrasado=False):
    lis = "".join(f'<li><span class="q">{q}×</span>{n}</li>' for q, n in itens)
    obs_html = f'<span class="obs">⚠ {obs}</span>' if obs else ""
    botao = ""
    if proximo == "preparando":
        botao = ('<button type="button" class="nv-btn-mini cheio" data-avancar="kds-preparando" data-proximo="kds-pronto" '
                 'data-proximo-rotulo="Pronto ✓" data-msg="Pedido em preparo.">Começar</button>')
    elif proximo == "pronto":
        botao = '<button type="button" class="nv-btn-mini cheio" data-avancar="kds-pronto" data-msg="Pedido pronto: o garçom foi avisado.">Pronto ✓</button>'
    cls = " atrasado" if atrasado else ""
    return (
        f'<div class="nv-pedido{cls}"><div class="nv-pedido-cab"><b>#{numero}</b>{tag("info", origem)}</div>'
        f"<ul>{lis}</ul>{obs_html}"
        f'<div class="rodape-pedido"><span>⏱ <span class="timer" data-inicio-min="{minutos}" data-limite="{limite}">{minutos}:00</span></span>{botao}</div></div>'
    )


def tela_cozinha() -> str:
    novos = "".join([
        pedido_kds(418, "Mesa 6", [("3", "Porção de calabresa"), ("1", "Balde de gelo")], 1, 15, proximo="preparando"),
        pedido_kds(419, "Delivery", [("2", "Copão Gin Tônica"), ("1", "Copão Caipirinha de limão")], 0, 15, "sem açúcar na caipirinha", proximo="preparando"),
        pedido_kds(420, "Cardápio online", [("1", "Porção de batata com cheddar")], 0, 15, proximo="preparando"),
    ])
    preparando = "".join([
        pedido_kds(415, "Mesa 1", [("2", "Porção de calabresa"), ("1", "Copão Gin Tônica")], 17, 15, proximo="pronto", atrasado=True),
        pedido_kds(416, "Mesa 9", [("4", "Copão Caipirinha"), ("2", "Amendoim torrado")], 9, 15, "2 com vodka, 2 com cachaça", proximo="pronto"),
        pedido_kds(417, "Balcão", [("1", "Porção de batata")], 6, 15, proximo="pronto"),
    ])
    prontos = "".join([
        pedido_kds(413, "Mesa 4", [("1", "Porção de batata")], 2, 0),
        pedido_kds(414, "Delivery", [("3", "Copão Caipirinha"), ("1", "Balde de gelo")], 1, 0),
    ])
    corpo = (
        topo("Cozinha / Bar", "Tela para a cozinha e o bar (KDS): letra grande para ler de longe, tempo de cada pedido e aviso de atraso.",
             btn("Tela cheia", "btn-secundario", "Na loja, essa tela fica numa TV ou tablet na cozinha/bar.")
             + btn("🔔 Som ligado", "btn-secundario", "Toca um som quando chega pedido novo."))
        + kpis([
            ("Na fila agora", "8 pedidos", "3 novos · 3 em preparo · 2 prontos"),
            ("Tempo médio de preparo", "11 min", "meta: 15 min"),
            ("Atrasados", "1", "acima de 15 minutos"),
            ("Pedidos hoje", "64", "mesas, balcão, delivery e cardápio"),
        ])
        + '<div class="nv-kanban nv-kds" data-atrasa>'
        f'<div class="nv-coluna" id="kds-novos"><div class="nv-coluna-cab">🆕 Novos <span class="qtd">3</span></div>{novos}</div>'
        f'<div class="nv-coluna" id="kds-preparando"><div class="nv-coluna-cab">🔥 Preparando <span class="qtd">3</span></div>{preparando}</div>'
        f'<div class="nv-coluna" id="kds-pronto"><div class="nv-coluna-cab">✅ Pronto para servir <span class="qtd">2</span></div>{prontos}</div>'
        "</div>"
    )
    return pagina("nv-cozinha", corpo)


# ----------------------------------------------------------------------------------------------
# 3. Delivery
# ----------------------------------------------------------------------------------------------
def pedido_dlv(numero, cliente, origem, bairro, itens, total, minutos, proximo=None, entregador="", entregue_em=""):
    lis = "".join(f'<li><span class="q">{q}×</span>{n}</li>' for q, n in itens)
    botao = ""
    rotulos = {
        "separacao": ("dlv-separacao", "dlv-rota", "Saiu para entrega 🛵", "Pedido aceito e em separação. O cliente recebeu aviso no WhatsApp.", "Aceitar"),
        "rota": ("dlv-rota", "dlv-entregue", "Entregue ✓", "Pedido saiu para entrega. O cliente recebeu o aviso com o nome do entregador.", "Saiu para entrega 🛵"),
        "entregue": ("dlv-entregue", None, None, "Entrega confirmada. Venda registrada no caixa.", "Entregue ✓"),
    }
    if proximo in rotulos:
        alvo, prox, prox_rot, msg, rot = rotulos[proximo]
        extra = f' data-proximo="{prox}" data-proximo-rotulo="{prox_rot}"' if prox else ""
        botao = f'<button type="button" class="nv-btn-mini cheio" data-avancar="{alvo}"{extra} data-msg="{msg}">{rot}</button>'
    ent = f' · 🛵 {entregador}' if entregador else ""
    return (
        f'<div class="nv-pedido"><div class="nv-pedido-cab"><b>#{numero}</b>{tag("ia" if "IA" in origem else "info", origem)}</div>'
        f'<div style="font-weight:700">{cliente}</div><div class="muted small">📍 {bairro}{ent}</div>'
        f"<ul>{lis}</ul>"
        + (f'<div class="rodape-pedido"><span><b style="color:var(--ink)">{brl(total)}</b> · ⏱ <span class="timer" data-inicio-min="{minutos}">{minutos}:00</span></span>{botao}</div></div>'
         if minutos is not None else f'<div class="rodape-pedido"><span><b style="color:var(--ink)">{brl(total)}</b> · entregue em {entregue_em}</span>{tag("ok", "pago")}</div></div>')
    )


def tela_delivery() -> str:
    col1 = "".join([
        pedido_dlv(2041, "Henrique Moraes", "WhatsApp · Agente IA", "Qd. 12, Jardim Europa · 1,2 km", [("2", "Fardo Heineken Lata c/ 12"), ("2", "Gelo Cubo Cristal 5kg")], 172.80, 2, "separacao"),
        pedido_dlv(2042, "Ana Paula R.", "Cardápio online", "Vila Nova · 3,4 km", [("1", "Vodka Absolut 1L"), ("4", "Red Bull Lata"), ("1", "Gelo 5kg")], 155.50, 1, "separacao"),
    ])
    col2 = "".join([
        pedido_dlv(2039, "Rodrigo Eventos & Churrascos", "WhatsApp · Agente IA", "Centro · 2,1 km", [("5", "Fardo Brahma Duplo Malte c/ 12"), ("6", "Gelo Cubo Cristal 5kg"), ("2", "Carvão 4kg")], 383.30, 9, "rota"),
    ])
    col3 = "".join([
        pedido_dlv(2036, "Quadra Society Arena Gol", "Telefone", "Setor Sul · 4,8 km", [("3", "Fardo Spaten c/ 12"), ("12", "Água Mineral 500ml")], 206.70, 22, "entregue", "Diego"),
        pedido_dlv(2037, "Juliana Costa", "Cardápio online", "Jardim Europa · 0,9 km", [("2", "Vinho Chileno Cabernet"), ("1", "Água Tônica")], 84.60, 14, "entregue", "Paulo"),
    ])
    col4 = "".join([
        pedido_dlv(2033, "Bar & Petiscaria Recanto", "WhatsApp · Agente IA", "Centro · 1,8 km", [("4", "Fardo Heineken Lata c/ 12")], 279.60, None, None, "Diego", "28 min"),
        pedido_dlv(2034, "Marcelo Tavares", "Cardápio online", "Vila Nova · 2,9 km", [("1", "Gin Tanqueray 750ml"), ("4", "Água Tônica")], 144.10, None, None, "Paulo", "31 min"),
    ])
    mapa = (
        '<div class="nv-mapa" aria-label="Mapa das entregas">'
        '<div class="raio" style="left:50%;top:52%;width:240px;height:240px"></div>'
        '<div class="raio" style="left:50%;top:52%;width:420px;height:420px;opacity:.5"></div>'
        '<div class="loja" style="left:50%;top:52%">★</div>'
        '<div class="pino" style="left:38%;top:40%">📍</div><div class="pino" style="left:66%;top:30%">📍</div>'
        '<div class="pino" style="left:61%;top:74%">🛵</div><div class="pino" style="left:27%;top:70%">🛵</div></div>'
    )
    entregadores = (
        '<ul class="nv-linhas">'
        '<li><span class="nv-avatar" style="background:#10B981">DI</span><div class="cresce"><b>Diego</b><span>levando #2036 · volta em ~8 min</span></div>' + tag("ok", "em rota") + '</li>'
        '<li><span class="nv-avatar" style="background:#6366F1">PA</span><div class="cresce"><b>Paulo</b><span>levando #2037</span></div>' + tag("ok", "em rota") + '</li>'
        '<li><span class="nv-avatar" style="background:#94A3B8">MA</span><div class="cresce"><b>Marcos</b><span>disponível na loja</span></div>' + tag("", "livre") + '</li>'
        "</ul>"
    )
    taxas = (
        '<ul class="nv-linhas">'
        '<li><div class="cresce"><b>Até 3 km</b><span>Centro, Jardim Europa, Vila Nova</span></div><span class="valor">R$ 5,00</span></li>'
        '<li><div class="cresce"><b>De 3 a 5 km</b><span>Setor Sul, Parque das Águas</span></div><span class="valor">R$ 8,00</span></li>'
        '<li><div class="cresce"><b>Pedido acima de R$ 150</b><span>entrega grátis</span></div><span class="valor nv-ok">grátis</span></li>'
        "</ul>"
    )
    corpo = (
        topo("Delivery", "Pedidos do WhatsApp (atendidos pelo agente de IA), do cardápio online e do telefone, num só lugar.",
             btn("+ Pedido por telefone", "btn-principal btn-alto", "Novo pedido de entrega: busque o cliente, os produtos e o endereço."))
        + kpis([
            ("Entregas hoje", "27", "<b class=\"ok\">+22%</b> sobre a sexta passada"),
            ("Faturamento do delivery", "R$ 4.318,60", "31% do faturamento do dia"),
            ("Tempo médio de entrega", "34 min", "do pedido até a porta"),
            ("Pedidos pelo agente de IA", "63%", "17 de 27 sem ninguém da loja"),
        ])
        + '<div class="nv-kanban" style="--colunas:4">'
        f'<div class="nv-coluna" id="dlv-novos"><div class="nv-coluna-cab">🆕 Novos <span class="qtd">2</span></div>{col1}</div>'
        f'<div class="nv-coluna" id="dlv-separacao"><div class="nv-coluna-cab">📦 Separando <span class="qtd">1</span></div>{col2}</div>'
        f'<div class="nv-coluna" id="dlv-rota"><div class="nv-coluna-cab">🛵 Em rota <span class="qtd">2</span></div>{col3}</div>'
        f'<div class="nv-coluna" id="dlv-entregue"><div class="nv-coluna-cab">✅ Entregues <span class="qtd">2</span></div>{col4}</div>'
        "</div>"
        '<div class="nv-grade-3 nv-secao">'
        + card("Mapa das entregas", mapa + '<p class="muted small" style="margin:8px 0 0">Raio de entrega: 5 km da loja.</p>')
        + card("Entregadores", entregadores)
        + card("Taxa de entrega", taxas)
        + "</div>"
    )
    return pagina("nv-delivery", corpo)


# ----------------------------------------------------------------------------------------------
# 4. Cardápio digital
# ----------------------------------------------------------------------------------------------
def tela_cardapio() -> str:
    itens_cel = [
        ("🍺", "Fardo Heineken Lata c/ 12", "350ml · bem gelada", 69.90),
        ("🍺", "Fardo Spaten Lata c/ 12", "350ml · puro malte", 56.90),
        ("🧊", "Gelo Cubo Cristal 5kg", "filtrado", 14.00),
        ("🥃", "Copão Gin Tônica", "700ml · montado na hora", 21.80),
        ("🍹", "Copão Caipirinha", "limão, vodka ou cachaça", 19.90),
        ("⚡", "Red Bull Energy Drink", "lata 250ml", 10.90),
        ("🍟", "Porção de batata", "500g · serve 2", 33.70),
    ]
    cel_itens = "".join(
        f'<div class="nv-cel-item"><div class="foto">{e}</div><div class="meio"><b>{n}</b><span>{d}</span>'
        f'<span class="preco">{brl(p)}</span></div><button type="button" class="nv-cel-mais" data-preco="{p}" aria-label="Adicionar {n}">+</button></div>'
        for e, n, d, p in itens_cel
    )
    celular = (
        '<div class="nv-celular"><div class="nv-celular-tela">'
        '<div class="nv-celular-topo"><img data-marca-logo src="./static/img/logo-marca.svg" alt="">'
        '<b>SUA MARCA</b><small>● Aberto até 23h · entrega em ~35 min</small></div>'
        '<div class="nv-cel-cats"><span class="ativo">Mais pedidos</span><span>Cervejas</span><span>Copão e drinks</span><span>Destilados</span><span>Gelo e carvão</span><span>Porções</span></div>'
        f"{cel_itens}"
        '<div class="nv-cel-carrinho" data-carrinho hidden><span>🛒 <span data-carrinho-itens>0 itens</span></span><span data-carrinho-total>R$ 0,00</span></div>'
        "</div></div>"
        '<p class="muted small nv-centro" style="margin-top:10px">Prévia do que o cliente vê no celular. Toque em <b>+</b> para testar.</p>'
    )
    categorias = tabela(
        ["Categoria", "Produtos visíveis", "Horário", ""],
        [
            ["<b>Mais pedidos</b>", "8 (automático pelo giro)", "sempre", switch("Mais pedidos")],
            ["<b>Cervejas</b>", "14", "sempre", switch("Cervejas")],
            ["<b>Copão e drinks</b>", "6", "a partir das 17h", switch("Copão e drinks")],
            ["<b>Destilados</b>", "11", "sempre", switch("Destilados")],
            ["<b>Gelo e carvão</b>", "4", "sempre", switch("Gelo e carvão")],
            ["<b>Porções</b>", "5", "das 18h às 23h", switch("Porções")],
            ["<b>Combos de fim de semana</b>", "3", "sex. a dom.", switch("Combos", False)],
        ],
    )
    config = (
        '<div class="nv-linha-config"><div class="meio"><b>Receber pedidos pelo cardápio</b><span>Os pedidos caem direto no Delivery e na cozinha/bar</span></div>' + switch("Cardápio online") + "</div>"
        '<div class="nv-linha-config"><div class="meio"><b>Retirar na loja</b><span>O cliente escolhe buscar no balcão</span></div>' + switch("Retirada na loja") + "</div>"
        '<div class="nv-linha-config"><div class="meio"><b>Pedido na mesa (QR na mesa)</b><span>Cai na comanda da mesa, sem chamar o garçom</span></div>' + switch("Pedido na mesa") + "</div>"
        '<div class="nv-linha-config"><div class="meio"><b>Pedido mínimo</b><span>Para entrega</span></div><b>R$ 30,00</b></div>'
        '<div class="nv-linha-config"><div class="meio"><b>Pagamento</b><span>Pix na hora ou na entrega (cartão e dinheiro)</span></div>' + tag("ok", "Pix automático") + "</div>"
    )
    link_card = (
        '<div style="display:flex;gap:16px;align-items:center;flex-wrap:wrap">' + qr(11) +
        '<div style="flex:1;min-width:200px"><div class="muted small">Endereço do cardápio</div>'
        '<div class="nv-mono" style="font-size:14px;margin:4px 0 10px"><b>suamarca.optimapdv.com.br/cardapio</b></div>'
        '<div class="nv-acoes-topo">'
        + btn("Copiar link", "btn-secundario", "Link copiado. Cole na bio do Instagram e no status do WhatsApp.")
        + btn("Baixar QR para as mesas", "btn-secundario", "QR em PDF pronto para imprimir e colar nas mesas.")
        + "</div></div></div>"
    )
    corpo = (
        topo("Cardápio digital", "O cliente pede pelo celular, sem aplicativo: pelo link, pelo QR na mesa ou pelo Instagram.",
             btn("Ver como cliente", "btn-secundario", "Abra a prévia ao lado: é exatamente o que o cliente vê."))
        + kpis([
            ("Pedidos pelo cardápio (mês)", "184", "<b class=\"ok\">+41%</b> sobre outubro"),
            ("Faturamento pelo cardápio", "R$ 21.460,90", "ticket médio R$ 116,64"),
            ("Visitas ao cardápio", "2.912", "6,3% viram pedido"),
            ("Produto mais pedido", "Fardo Heineken", "e Gelo 5kg junto em 72%"),
        ])
        + '<div class="nv-grade-lado"><div class="nv-pilha">'
        + card("Link e QR Code", link_card)
        + card("Categorias do cardápio", categorias, '<span class="muted small">os preços e o estoque vêm do cadastro de produtos</span>')
        + card("Como o cardápio funciona", config)
        + "</div><div>" + celular + "</div></div>"
    )
    return pagina("nv-cardapio", corpo)


# ----------------------------------------------------------------------------------------------
# 5. Orçamentos
# ----------------------------------------------------------------------------------------------
def tela_orcamentos() -> str:
    linhas = [
        ["<b>#0087</b>", "Rodrigo Eventos & Churrascos<div class=\"small muted\">Casamento · 120 pessoas</div>", "05/11", "20/11", tag("info", "Enviado · visto 3×"), "<b>R$ 4.440,40</b>"],
        ["<b>#0086</b>", "Churrascaria Boi Dourado<div class=\"small muted\">Reposição semanal</div>", "04/11", "11/11", tag("ok", "Aprovado"), "<b>R$ 2.318,90</b>"],
        ["<b>#0085</b>", "Quadra Society Arena Gol<div class=\"small muted\">Final do campeonato</div>", "03/11", "10/11", tag("ok", "Virou venda"), "<b>R$ 1.146,00</b>"],
        ["<b>#0084</b>", "Bar & Petiscaria Recanto<div class=\"small muted\">Fim de semana</div>", "01/11", "08/11", tag("ok", "Virou venda"), "<b>R$ 1.894,20</b>"],
        ["<b>#0083</b>", "Formatura Medicina 2026<div class=\"small muted\">Open bar · 300 pessoas</div>", "30/10", "14/11", tag("aviso", "Aguardando resposta"), "<b>R$ 12.740,00</b>"],
        ["<b>#0082</b>", "Espetinho do Alemão", "28/10", "04/11", tag("erro", "Vencido"), "<b>R$ 684,50</b>"],
        ["<b>#0081</b>", "Henrique Moraes<div class=\"small muted\">Aniversário</div>", "27/10", "03/11", tag("ok", "Virou venda"), "<b>R$ 742,30</b>"],
    ]
    previa_itens = [
        ("30", "Fardo Heineken Lata 350ml c/ 12", 69.90, 66.40),
        ("20", "Fardo Brahma Duplo Malte c/ 12", 49.90, 47.40),
        ("40", "Gelo Cubo Cristal Pacote 5kg", 14.00, 13.30),
        ("6", "Whisky Johnnie Walker Red Label 1L", 109.90, 104.40),
        ("12", "Água Mineral Cristal sem Gás 500ml (fardo c/ 12)", 30.00, 28.50),
    ]
    tr = "".join(f'<tr><td><b>{q}×</b> {n}</td><td class="num muted"><s>{brl(p)}</s></td><td class="num">{brl(pd)}</td><td class="num"><b>{brl(int(q) * pd)}</b></td></tr>' for q, n, p, pd in previa_itens)
    total = sum(int(q) * pd for q, _, _, pd in previa_itens)
    previa = (
        f'<p class="muted small" style="margin-top:0">Rodrigo Eventos & Churrascos · válido até 20/11 · desconto de volume de 5%</p>'
        f'<div class="tabela-rolagem"><table class="nv-itens"><tbody>{tr}</tbody><tfoot><tr><td>Total</td><td></td><td></td><td class="num">{brl(total)}</td></tr></tfoot></table></div>'
        '<div class="nv-faixa" style="margin:14px 0 0">🔒 Os preços ficam gravados no orçamento: se o produto subir, o valor combinado com o cliente não muda.</div>'
        '<div class="nv-acoes-topo" style="margin-top:14px">'
        + btn("Enviar pelo WhatsApp", "btn-principal", "Orçamento enviado no WhatsApp do cliente, com link para ver e salvar em PDF.")
        + btn("Baixar PDF", "btn-secundario", "PDF gerado com a marca da loja.")
        + btn("Converter em venda", "btn-secundario", "Orçamento convertido: os itens foram para o caixa com os preços combinados.")
        + "</div>"
    )
    corpo = (
        topo("Orçamentos", "Monte, envie pelo WhatsApp e transforme em venda com um clique: para eventos, bares e clientes de volume.",
             btn("+ Novo orçamento", "btn-principal btn-alto", "Novo orçamento: escolha o cliente, os produtos e a validade."))
        + kpis([
            ("Em aberto", "R$ 17.180,40", "2 orçamentos aguardando resposta"),
            ("Conversão (60 dias)", "64%", "16 de 25 viraram venda"),
            ("Vendido por orçamento (mês)", "R$ 5.101,40", "ticket médio R$ 1.275,35"),
            ("Tempo até a resposta", "1,4 dia", "o cliente vê pelo link"),
        ])
        + '<div class="pr-filtros"><a class="filtro-chip ativo" href="#">Todos · 25</a><a class="filtro-chip" href="#">Em aberto · 2</a>'
        '<a class="filtro-chip" href="#">Aprovados · 1</a><a class="filtro-chip" href="#">Viraram venda · 16</a><a class="filtro-chip" href="#">Vencidos · 6</a></div>'
        '<div class="nv-pilha">'
        + card("Orçamentos", tabela(["Nº", "Cliente", "Validade", "Situação", "Total"], [[l[0], l[1], l[3], l[4], l[5]] for l in linhas], (4,)))
        + card("Orçamento #0087", previa, tag("info", "Enviado"))
        + "</div>"
    )
    return pagina("nv-orcamentos", corpo)


# ----------------------------------------------------------------------------------------------
# 6. Trocas e devoluções
# ----------------------------------------------------------------------------------------------
def tela_trocas() -> str:
    linhas = [
        ["05/11 18:42", "Juliana Costa", "Vinho Chileno Cabernet 750ml<div class=\"small muted\">rolha com defeito</div>", tag("info", "Troca pelo mesmo"), "venda #8812", "—"],
        ["04/11 21:10", "Marcelo Tavares", "Fardo Spaten Lata c/ 12<div class=\"small muted\">comprou a mais</div>", tag("ok", "Vale-troca"), "venda #8790", "<b>R$ 56,90</b>"],
        ["02/11 16:05", "Henrique Moraes", "Gelo Cubo Cristal 5kg<div class=\"small muted\">derretido na entrega</div>", tag("aviso", "Devolução (Pix)"), "venda #8741", "<b>R$ 14,00</b>"],
        ["31/10 20:31", "Consumidor", "Red Bull Lata 250ml ×2<div class=\"small muted\">lata amassada</div>", tag("info", "Troca pelo mesmo"), "venda #8702", "—"],
        ["29/10 11:18", "Bar & Petiscaria Recanto", "Fardo Heineken Lata c/ 12<div class=\"small muted\">pediu Heineken long neck</div>", tag("ok", "Troca por outro"), "venda #8666", "dif. R$ 20,10"],
    ]
    vales = (
        '<ul class="nv-linhas">'
        '<li><div class="cresce"><b>Marcelo Tavares</b><span>VT-0042 · gerado em 04/11 · vale até 04/02</span></div><span class="valor">R$ 56,90</span></li>'
        '<li><div class="cresce"><b>Rodrigo Eventos & Churrascos</b><span>VT-0039 · gerado em 22/10</span></div><span class="valor">R$ 138,00</span></li>'
        '<li><div class="cresce"><b>Quadra Society Arena Gol</b><span>VT-0036 · usado parcialmente</span></div><span class="valor">R$ 24,40</span></li>'
        "</ul>"
    )
    regras = (
        '<div class="nv-linha-config"><div class="meio"><b>Prazo para troca</b><span>contado da data da venda</span></div><b>7 dias</b></div>'
        '<div class="nv-linha-config"><div class="meio"><b>Autorização do supervisor</b><span>para devolver em dinheiro ou Pix</span></div>' + switch("Autorização do supervisor") + "</div>"
        '<div class="nv-linha-config"><div class="meio"><b>Estorno do cashback</b><span>tira o cashback que o cliente ganhou na compra devolvida</span></div>' + switch("Estorno do cashback") + "</div>"
        '<div class="nv-linha-config"><div class="meio"><b>Volta para o estoque</b><span>se o produto estiver bom; com defeito vai para Perdas</span></div>' + switch("Volta para o estoque") + "</div>"
    )
    corpo = (
        topo("Trocas e devoluções", "Troca pelo mesmo produto, por outro, devolução do dinheiro ou vale-troca na ficha do cliente. Tudo ligado à venda original.",
             btn("+ Registrar troca", "btn-principal btn-alto", "Busque a venda pelo cupom, pelo cliente ou pelo código do produto."))
        + kpis([
            ("Trocas no mês", "9", "0,4% das vendas"),
            ("Devolvido em dinheiro/Pix", "R$ 92,40", "3 devoluções"),
            ("Vales-troca em aberto", "R$ 219,30", "3 clientes"),
            ("Principal motivo", "Avaria", "lata amassada / rolha"),
        ])
        + '<div class="nv-grade-lado">'
        + card("Últimas trocas", tabela(["Quando", "Cliente", "Produto e motivo", "Tipo", "Venda", "Valor"], linhas, (5,)))
        + '<div class="nv-pilha">' + card("Vales-troca em aberto", vales) + card("Regras", regras) + "</div></div>"
    )
    return pagina("nv-trocas", corpo)


# ----------------------------------------------------------------------------------------------
# 7. Nota fiscal (NFC-e)
# ----------------------------------------------------------------------------------------------
def tela_fiscal() -> str:
    notas = [
        ["14:27", "<b>001.248</b>", "<span class=\"nv-mono\">5226 1112 …0012 4815</span>", "Juliana Costa", tag("ok", "Autorizada"), "<b>R$ 66,00</b>"],
        ["14:18", "<b>001.247</b>", "<span class=\"nv-mono\">5226 1112 …0012 4710</span>", "Consumidor", tag("ok", "Autorizada"), "<b>R$ 197,70</b>"],
        ["13:32", "<b>001.246</b>", "<span class=\"nv-mono\">5226 1112 …0012 4613</span>", "CPF 123.***.***-09", tag("ok", "Autorizada"), "<b>R$ 26,80</b>"],
        ["13:28", "<b>001.245</b>", "<span class=\"nv-mono\">5226 1112 …0012 4512</span>", "Consumidor", tag("ok", "Autorizada"), "<b>R$ 47,60</b>"],
        ["12:51", "<b>001.244</b>", "<span class=\"nv-mono\">5226 1112 …0012 4411</span>", "Bar & Petiscaria Recanto", tag("ok", "Autorizada"), "<b>R$ 279,60</b>"],
        ["11:40", "<b>001.243</b>", "<span class=\"nv-mono\">5226 1112 …0012 4314</span>", "Consumidor", tag("aviso", "Cancelada"), "<b>R$ 18,00</b>"],
        ["10:02", "<b>001.242</b>", "<span class=\"nv-mono\">5226 1112 …0012 4219</span>", "Consumidor", tag("ok", "Contingência → autorizada"), "<b>R$ 34,90</b>"],
    ]
    danfe = (
        '<div class="nv-danfe"><div class="c"><b>SUA MARCA DISTRIBUIDORA LTDA</b><br>CNPJ 12.345.678/0001-90 · IE 10.987.654-3<br>'
        'Av. Central, 1500 · Centro</div><hr>'
        '<div class="c"><b>DANFE NFC-e</b><br>Documento Auxiliar da Nota Fiscal<br>de Consumidor Eletrônica</div><hr>'
        '<table><tr><td>2 FARDO HEINEKEN LT C/12</td><td class="n">139,80</td></tr>'
        '<tr><td>2 GELO CUBO CRISTAL 5KG</td><td class="n">28,00</td></tr>'
        '<tr><td>1 RED BULL LT 250ML</td><td class="n">10,90</td></tr></table><hr>'
        '<table><tr><td>Qtde. total de itens</td><td class="n">5</td></tr><tr><td><b>VALOR TOTAL R$</b></td><td class="n"><b>178,70</b></td></tr>'
        '<tr><td>Pix</td><td class="n">178,70</td></tr></table><hr>'
        '<div class="c">Tributos aprox. R$ 58,42 (Lei 12.741)<br>IBS/CBS informados (cClassTrib 000001)</div><hr>'
        '<div class="c">NFC-e nº 001.248 Série 1<br>06/11/2026 14:27:12<br><b>Protocolo 152261234567890</b><br>Consulte pela chave de acesso em<br>www.sefaz.go.gov.br/nfce</div>'
        f'<div class="qr" style="display:flex;justify-content:center;margin-top:8px">{qr(23)}</div></div>'
    )
    status = (
        '<ul class="nv-linhas">'
        '<li><span class="nv-ico">🟢</span><div class="cresce"><b>SEFAZ online</b><span>resposta em 0,8 s · última nota 14:27</span></div></li>'
        '<li><span class="nv-ico">🔐</span><div class="cresce"><b>Certificado A1 válido</b><span>vence em 14/08/2027 (281 dias)</span></div></li>'
        '<li><span class="nv-ico">📴</span><div class="cresce"><b>Contingência automática</b><span>sem internet, a nota sai em contingência e é enviada quando a conexão volta</span></div>' + tag("ok", "ligada") + "</li>"
        '<li><span class="nv-ico">📧</span><div class="cresce"><b>XML para o contador</b><span>enviado todo dia 1º para contabilidade@escritorio.com.br</span></div></li>'
        "</ul>"
    )
    reforma = (
        '<p style="margin-top:0">A NFC-e já sai com os campos novos da <b>reforma tributária</b> (IBS e CBS): a classificação tributária '
        '(<span class="nv-mono">cClassTrib</span>) fica no produto e a nota herda o padrão da loja quando o produto não tem.</p>'
        + '<ul class="nv-linhas">'
        '<li><div class="cresce"><b>Regime</b><span>Simples Nacional</span></div>' + tag("ok", "configurado") + "</li>"
        '<li><div class="cresce"><b>cClassTrib padrão</b><span><span class="nv-mono">000001</span> · tributação integral</span></div>' + tag("ok", "configurado") + "</li>"
        '<li><div class="cresce"><b>CST do IBS/CBS</b><span>3 primeiros dígitos do cClassTrib</span></div>' + tag("ok", "automático") + "</li>"
        '<li><div class="cresce"><b>Produtos sem classificação</b><span>usam o padrão da loja</span></div>' + tag("info", "62") + "</li>"
        "</ul>"
    )
    corpo = (
        topo("Nota fiscal (NFC-e)", "A nota sai sozinha ao finalizar a venda, com o QR Code impresso no cupom. Sem internet, entra em contingência.",
             btn("Configuração fiscal", "btn-secundario", "Certificado, CSC, série, regime e classificação tributária.")
             + btn("Baixar XMLs do mês", "btn-secundario", "Arquivo .zip com os XMLs de novembro gerado para o contador."))
        + kpis([
            ("Notas hoje", "16", "todas autorizadas"),
            ("Notas no mês", "119", "R$ 10.752,50 em notas"),
            ("Rejeições", "0", "nos últimos 30 dias"),
            ("Em contingência", "0", "nenhuma pendente de envio"),
        ])
        + '<div class="nv-grade-lado"><div class="nv-pilha">'
        + card("Notas de hoje", tabela(["Hora", "Número", "Chave de acesso", "Destinatário", "Situação", "Valor"], notas, (5,)))
        + '<div class="nv-grade-2">' + card("Conexão com a SEFAZ", status) + card("Reforma tributária (IBS/CBS)", reforma, tag("ok", "pronto")) + "</div>"
        + "</div>" + card("Cupom da nota (DANFE)", danfe, '<span class="muted small">80 mm</span>') + "</div>"
    )
    return pagina("nv-fiscal", corpo)


# ----------------------------------------------------------------------------------------------
# 8. Inteligência
# ----------------------------------------------------------------------------------------------
def tela_inteligencia() -> str:
    rnd = random.Random(42)
    horas = list(range(10, 24))
    dias = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    pesos_dia = [0.35, 0.3, 0.4, 0.55, 0.85, 1.0, 0.75]
    celulas = ['<span></span>'] + [f'<span class="h">{h}h</span>' for h in horas]
    for d, pd in zip(dias, pesos_dia):
        celulas.append(f'<span class="d">{d}</span>')
        for h in horas:
            curva = 0.25 + 0.75 * max(0.0, 1 - abs(h - 20) / 9)
            if d in ("Sáb", "Dom") and 11 <= h <= 15:
                curva += 0.35
            v = min(1.0, pd * curva * (0.85 + rnd.random() * 0.3))
            celulas.append(f'<span class="c" style="opacity:{0.08 + v * 0.92:.2f}" title="{d} {h}h"></span>')
    calor = (
        f'<div class="nv-calor">{"".join(celulas)}</div>'
        '<div class="nv-calor-legenda">menos <i style="opacity:.12"></i><i style="opacity:.4"></i><i style="opacity:.7"></i><i></i> mais vendas</div>'
        '<p class="muted small" style="margin:10px 0 0">Pico: <b>sábado das 19h às 22h</b>. Domingo tem um segundo pico no almoço (churrasco).</p>'
    )
    clima = (
        '<div class="nv-clima">'
        '<div class="dia quente"><div class="ic">☀️</div><b>34°</b><small>Sáb, 07/11</small><div class="efeito">+38% cerveja e gelo</div></div>'
        '<div class="dia quente"><div class="ic">🌤️</div><b>32°</b><small>Dom, 08/11</small><div class="efeito">+27% carvão e gelo</div></div>'
        '<div class="dia"><div class="ic">⛅</div><b>29°</b><small>Seg, 09/11</small><div class="efeito" style="color:var(--muted)">normal</div></div>'
        '<div class="dia"><div class="ic">🌧️</div><b>24°</b><small>Ter, 10/11</small><div class="efeito" style="color:var(--erro)">−18% no balcão</div></div>'
        '<div class="dia"><div class="ic">⛅</div><b>28°</b><small>Qua, 11/11</small><div class="efeito" style="color:var(--muted)">normal</div></div>'
        "</div>"
        '<p class="muted small" style="margin:10px 0 0">Previsão do tempo para o endereço da loja, cruzada com o histórico de vendas em dias parecidos.</p>'
    )

    def sug(tipo, titulo, texto, botao, msg):
        return (
            f'<div class="nv-sugestao"><div class="topo"><b>{titulo}</b>{tag("ia", tipo)}</div><p>{texto}</p>'
            f'<div class="acoes"><button type="button" class="nv-btn-mini cheio" data-sugestao="aceitar" data-msg="{msg}">{botao}</button>'
            '<button type="button" class="nv-btn-mini" data-sugestao="dispensar">Dispensar</button></div></div>'
        )

    sugestoes = (
        '<div class="nv-pilha" style="gap:10px">'
        + sug("Reposição", "Reforçar gelo e cerveja para o sábado de 34°",
              "Pedir <b>60 pacotes de Gelo 5kg</b> e <b>25 fardos de Heineken</b> até sexta 18h. Em sábados acima de 32° você vendeu 38% mais e faltou gelo em 2 deles.",
              "Gerar pedido de compra", "Pedido de compra gerado para o fornecedor. Está em Entradas aguardando confirmação.")
        + sug("Kit / combo", "Criar o combo “Churrasco de Domingo”",
              "Carvão 4kg + Gelo 5kg + Fardo Brahma Duplo Malte saem juntos em 41% das vendas de domingo. Sugestão: <b>R$ 84,90</b> (−5%), margem de 29%.",
              "Criar combo", "Combo criado e publicado no cardápio digital e no caixa.")
        + sug("Oferta programada", "Happy hour na terça chuvosa",
              "Terça deve chover e o balcão cai 18%. Sugestão: <b>Spaten Lata a R$ 4,49</b> das 17h às 20h, com aviso no WhatsApp para 214 clientes que aceitaram receber.",
              "Programar oferta", "Oferta programada para terça, 17h às 20h. Ela liga e desliga sozinha, até sem internet.")
        + sug("Escala", "Mais 1 pessoa no caixa sábado das 19h às 22h",
              "No último sábado a fila passou de 6 minutos nesse horário. Com 2 caixas abertos o tempo de espera cai para cerca de 2 minutos.",
              "Anotar na escala", "Anotado na escala de sábado.")
        + "</div>"
    )
    parados = (
        '<ul class="nv-linhas">'
        '<li><div class="cresce"><b>Licor 43 Diego Zamora 700ml</b><span>8 em estoque · última venda há 34 dias</span></div><span class="valor">R$ 1.279,20 parado</span></li>'
        '<li><div class="cresce"><b>Tequila José Cuervo Gold 750ml</b><span>7 em estoque · última venda há 21 dias</span></div><span class="valor">R$ 944,30 parado</span></li>'
        '<li><div class="cresce"><b>Aperitivo Campari 900ml</b><span>10 em estoque · última venda há 18 dias</span></div><span class="valor">R$ 649,00 parado</span></li>'
        "</ul>"
    )
    sumindo = (
        '<ul class="nv-linhas">'
        '<li><span class="nv-avatar" style="background:#F97316">CB</span><div class="cresce"><b>Churrascaria Boi Dourado</b><span>comprava toda semana · sem compra há 19 dias</span></div>' + btn("Chamar", "nv-btn-mini", "Mensagem pronta no WhatsApp: “Sentimos sua falta! Separei uma condição especial…”") + "</li>"
        '<li><span class="nv-avatar" style="background:#6366F1">EA</span><div class="cresce"><b>Espetinho do Alemão</b><span>comprava a cada 10 dias · há 24 dias</span></div>' + btn("Chamar", "nv-btn-mini", "Mensagem pronta no WhatsApp para o Espetinho do Alemão.") + "</li>"
        "</ul>"
    )
    meta = (
        '<div style="display:flex;justify-content:space-between;align-items:baseline"><span class="nv-grande">R$ 1.588,30</span><span class="muted">meta R$ 2.400,00</span></div>'
        '<div class="nv-progresso" style="margin:10px 0 6px"><span style="width:66%"></span></div>'
        '<p class="muted small" style="margin:0">66% da meta às 14:27. Pelo ritmo das sextas, deve fechar em <b>R$ 2.690,00</b> (112%).</p>'
    )
    margem = barras(
        [("Destilados", 38), ("Copão", 61), ("Cervejas", 22), ("Energéticos", 34), ("Gelo/carvão", 45), ("Refri/água", 29)],
        fmt=lambda v: f"{v}%", classe=lambda i, v: "" if v >= 30 else "suave",
    )
    corpo = (
        topo("Inteligência", "O sistema cruza vendas, horários, clima e clientes e sugere o que fazer. Você aprova com um clique.",
             btn("Perguntar ao assistente", "btn-secundario", "Abra o Assistente IA e pergunte: “o que eu faço para vender mais no sábado?”"))
        + kpis([
            ("Previsão de hoje", "R$ 2.690,00", "112% da meta do dia"),
            ("Sugestões novas", "4", "reposição, combo, oferta e escala"),
            ("Dinheiro parado em estoque", "R$ 2.872,50", "3 produtos sem giro há 18+ dias"),
            ("Clientes sumindo", "2", "compravam toda semana"),
        ])
        + '<div class="nv-grade-lado"><div class="nv-pilha">'
        + card("Quando sua loja vende (últimos 60 dias)", calor)
        + card("Clima dos próximos dias", clima)
        + card("Margem por categoria", margem, '<span class="muted small">abaixo de 30% em tom mais claro</span>')
        + "</div><div class=\"nv-pilha\">"
        + card("Meta do dia", meta)
        + card("Sugestões para você aprovar", sugestoes, tag("ia", "4 novas"))
        + card("Produtos parados", parados)
        + card("Clientes sumindo", sumindo)
        + "</div></div>"
    )
    return pagina("nv-inteligencia", corpo)


# ----------------------------------------------------------------------------------------------
# 9. Fluxo de caixa
# ----------------------------------------------------------------------------------------------
def tela_fluxo() -> str:
    semanas = [("06–12/11", 14820, 9640), ("13–19/11", 13950, 4210), ("20–26/11", 15480, 11380), ("27/11–03/12", 17200, 6120)]
    grafico = '<div class="nv-barras" style="height:200px">'
    mx = 18000
    for rot, ent, sai in semanas:
        grafico += (
            f'<div class="col"><span class="v nv-ok">+{brl(ent - sai)}</span>'
            f'<div style="display:flex;gap:4px;align-items:flex-end;height:100%;width:100%;justify-content:center">'
            f'<div class="b" style="height:{ent / mx * 100:.0f}%;max-width:28px"></div>'
            f'<div class="b neg" style="height:{sai / mx * 100:.0f}%;max-width:28px"></div></div><span class="r">{rot}</span></div>'
        )
    grafico += "</div>"
    legenda = ('<span class="legenda-grafico"><span><i class="lg-fat"></i>Entradas</span>'
               '<span><i style="background:var(--erro);display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:4px"></i>Saídas</span></span>')
    movs = tabela(
        ["Dia", "Descrição", "Origem", "Entrada", "Saída", "Saldo"],
        [
            ["06/11", "Vendas do dia (previsão)", tag("info", "caixa"), "R$ 2.690,00", "", "<b>R$ 21.112,40</b>"],
            ["07/11", "Cartão de crédito a receber (D+1)", tag("info", "Cielo / Stone"), "R$ 1.912,30", "", "<b>R$ 23.024,70</b>"],
            ["07/11", "Boleto Ambev · NF 88.412", tag("aviso", "contas"), "", "R$ 6.480,00", "<b>R$ 16.544,70</b>"],
            ["09/11", "Confiança a receber · Bar & Petiscaria Recanto", tag("info", "fiado"), "R$ 440,00", "", "<b>R$ 16.984,70</b>"],
            ["10/11", "Energia elétrica", tag("aviso", "contas"), "", "R$ 1.184,30", "<b>R$ 15.800,40</b>"],
            ["10/11", "Aluguel da loja", tag("aviso", "conta fixa"), "", "R$ 3.200,00", "<b>R$ 12.600,40</b>"],
            ["12/11", "Boleto Heineken · NF 21.993", tag("aviso", "contas"), "", "R$ 4.912,80", "<b>R$ 7.687,60</b>"],
            ["15/11", "Folha de pagamento", tag("aviso", "conta fixa"), "", "R$ 5.400,00", "<b>R$ 2.287,60</b>"],
        ],
        (3, 4, 5),
    )
    corpo = (
        topo("Fluxo de caixa", "O dinheiro que vai entrar e sair nos próximos 30 dias: vendas, cartões a receber, Confiança e contas a pagar.",
             btn("Exportar para Excel", "btn-secundario", "Planilha do fluxo de caixa gerada."))
        + '<div class="pr-filtros"><a class="filtro-chip" href="#">7 dias</a><a class="filtro-chip ativo" href="#">30 dias</a><a class="filtro-chip" href="#">60 dias</a><a class="filtro-chip" href="#">90 dias</a></div>'
        + kpis([
            ("Saldo hoje", "R$ 18.422,40", "caixa + banco + Pix"),
            ("Entra nos próximos 30 dias", "R$ 61.450,00", "vendas previstas, cartões e Confiança"),
            ("Sai nos próximos 30 dias", "R$ 31.350,00", "14 contas, 3 fixas"),
            ("Saldo previsto em 06/12", "R$ 48.522,40", "<b class=\"ok\">sem dia negativo</b>"),
        ])
        + '<div class="nv-faixa aviso">⚠ Dia 15/11 o saldo fica apertado (<b>R$ 2.287,60</b>) por causa da folha. Sugestão: antecipar R$ 3.000 dos recebíveis do cartão ou adiar o boleto da Heineken para 16/11.</div>'
        + '<div class="nv-grade-lado">'
        + card("Próximos 30 dias, por semana", grafico, legenda)
        + card("Cartões a receber", '<ul class="nv-linhas">'
               '<li><div class="cresce"><b>Débito</b><span>cai em D+1</span></div><span class="valor">R$ 1.204,60</span></li>'
               '<li><div class="cresce"><b>Crédito à vista</b><span>cai em D+30</span></div><span class="valor">R$ 8.947,10</span></li>'
               '<li><div class="cresce"><b>Crédito parcelado</b><span>3 parcelas em aberto</span></div><span class="valor">R$ 1.380,00</span></li>'
               '<li><div class="cresce"><b>Confiança (fiado)</b><span>5 clientes</span></div><span class="valor">R$ 2.120,00</span></li></ul>')
        + "</div>"
        + '<div class="nv-secao">' + card("Movimentos previstos", movs) + "</div>"
    )
    return pagina("nv-fluxo", corpo)


# ----------------------------------------------------------------------------------------------
# 10. WhatsApp
# ----------------------------------------------------------------------------------------------
CONVERSAS = [
    ("henrique", "HM", "#10B981", "Henrique Moraes", "Pedido #2041 confirmado ✅", "14:31", 2, "ia", [
        ("in", "Boa tarde! Vocês têm Heineken lata gelada?", "14:22"),
        ("ia", "Boa tarde, Henrique! 😊 Temos sim, bem gelada:\n• Fardo Heineken Lata c/ 12 — R$ 69,90\n• Heineken Long Neck — R$ 7,50 a unidade\nVai querer qual?", "14:22"),
        ("audio", "🎤 Áudio (0:09) — transcrição: “manda dois fardos e dois gelos de 5 quilos, é pra entregar aqui em casa”", "14:24"),
        ("ia", "Fechado! Seu pedido:\n2× Fardo Heineken Lata c/ 12 — R$ 139,80\n2× Gelo Cubo Cristal 5kg — R$ 28,00\nEntrega na Qd. 12, Jardim Europa (o mesmo endereço da última vez) — R$ 5,00\nTotal: R$ 172,80\nPix ou cartão na entrega?", "14:24"),
        ("in", "pix", "14:25"),
        ("ia", "Aqui está o Pix copia e cola 👇\n(QR dinâmico de R$ 172,80)\nAssim que cair eu já mando separar 🍺", "14:25"),
        ("sis", "Pix de R$ 172,80 confirmado · pedido #2041 enviado para o Delivery", "14:30"),
        ("ia", "Pagamento recebido! ✅ Pedido #2041 em separação. Chega em uns 30 minutos. Bom churrasco! 🔥", "14:31"),
    ]),
    ("rodrigo", "RE", "#F97316", "Rodrigo Eventos & Churrascos", "Me manda o orçamento do casamento", "13:58", 0, "humano", [
        ("in", "Fala! Tenho um casamento dia 21 pra 120 pessoas, me passa um orçamento de bebida?", "13:40"),
        ("ia", "Opa, Rodrigo! Parabéns pelo evento 🎉 Para 120 pessoas costumamos sugerir uns 30 fardos de cerveja, 40 de gelo e destilados à parte. Vou passar para o Carlos montar o orçamento com desconto de volume, tá bom?", "13:41"),
        ("sis", "Carlos Eduardo assumiu a conversa", "13:50"),
        ("loja", "Rodrigo, montei aqui com 5% de desconto. Te mandei o link do orçamento #0087, dá pra ver e salvar em PDF 👍", "13:56"),
        ("in", "Show, vou ver com os noivos e te falo", "13:58"),
    ]),
    ("ana", "AP", "#6366F1", "Ana Paula R.", "Vocês abrem domingo?", "13:12", 0, "ia", [
        ("in", "Vocês abrem domingo?", "13:11"),
        ("ia", "Abrimos sim, Ana! Domingo das 9h às 22h 😊 Quer que eu já deixe um pedido agendado?", "13:12"),
    ]),
    ("bar", "BR", "#EF4444", "Bar & Petiscaria Recanto", "Pode lançar na Confiança", "11:47", 0, "ia", [
        ("in", "Manda 4 fardos de Heineken, pode lançar na Confiança", "11:44"),
        ("ia", "Pedido anotado: 4× Fardo Heineken Lata c/ 12 = R$ 279,60 na Confiança.\nSeu saldo fica em R$ 719,60 de um limite de R$ 1.500,00. Entrega hoje até as 13h 🍺", "11:45"),
        ("in", "Pode lançar na Confiança", "11:47"),
    ]),
]


def tela_whatsapp() -> str:
    itens = []
    threads = []
    for i, (cid, ini, cor, nome, ultima, hora, nl, modo, msgs) in enumerate(CONVERSAS):
        ativo = " ativo" if i == 0 else ""
        badge = f'<span class="nv-wa-nao-lidas">{nl}</span>' if nl else ""
        selo = tag("ia", "IA") if modo == "ia" else tag("info", "humano")
        itens.append(
            f'<button type="button" class="nv-wa-item{ativo}" data-conversa="{cid}"><span class="nv-avatar" style="background:{cor}">{ini}</span>'
            f'<span class="meio"><b>{nome}</b><span>{ultima}</span></span><span class="lado">{hora}{badge}{selo}</span></button>'
        )
        bolhas = []
        for tipo, txt, h in msgs:
            if tipo == "sis":
                bolhas.append(f'<div class="nv-wa-sistema">{txt} · {h}</div>')
            elif tipo == "in":
                bolhas.append(f'<div class="nv-msg">{txt}<span class="hora">{h}</span></div>')
            elif tipo == "audio":
                bolhas.append(f'<div class="nv-msg audio">{txt}<span class="hora">{h}</span></div>')
            elif tipo == "ia":
                bolhas.append(f'<div class="nv-msg saida"><span class="quem">Agente de IA</span>{txt}<span class="hora">{h} ✓✓</span></div>')
            else:
                bolhas.append(f'<div class="nv-msg saida"><span class="quem">Carlos (loja)</span>{txt}<span class="hora">{h} ✓✓</span></div>')
        oculto = "" if i == 0 else " hidden"
        humano = modo == "humano"
        tag_at = (f'<span class="nv-tag {"info" if humano else "ia"}" data-tag-atendimento>'
                  f'{"Você está atendendo" if humano else "Agente de IA atendendo"}</span>')
        botao = (f'<button type="button" class="nv-btn-mini" data-assumir data-estado="{"humano" if humano else "ia"}">'
                 f'{"Devolver para a IA" if humano else "Assumir conversa"}</button>')
        threads.append(
            f'<div class="nv-wa-thread" data-thread="{cid}"{oculto}>'
            f'<div class="nv-wa-topo"><span class="nv-avatar" style="background:{cor}">{ini}</span><div class="meio"><b>{nome}</b><br><span>cliente desde 2025 · aceitou receber mensagens</span></div>{tag_at}{botao}</div>'
            f'<div class="nv-wa-msgs">{"".join(bolhas)}</div>'
            '<form class="nv-wa-rodape" data-wa-form="loja"><input type="text" placeholder="Escreva uma mensagem (você responde como a loja)" aria-label="Mensagem">'
            '<button type="submit" class="btn-principal">Enviar</button></form></div>'
        )
    wa = (
        '<div class="nv-wa"><div class="nv-wa-lista"><div class="nv-wa-busca"><input type="search" placeholder="Buscar conversa" aria-label="Buscar conversa"></div>'
        + "".join(itens) + "</div>" + "".join(threads) + "</div>"
    )
    corpo = (
        topo("WhatsApp", "O WhatsApp oficial da loja, no mesmo número. O agente de IA atende, monta o pedido com os preços do sistema e você assume quando quiser.",
             tag("ok", "● Conectado · (62) 99999-0000") + btn("Modelos de mensagem", "btn-secundario", "Modelos aprovados pela Meta: confirmação de pedido, aniversário, cashback, cliente sumido."))
        + kpis([
            ("Conversas hoje", "48", "41 resolvidas só pela IA (85%)"),
            ("Pedidos pelo WhatsApp hoje", "17", "R$ 2.734,10 vendidos"),
            ("Tempo da 1ª resposta", "6 s", "24 horas por dia"),
            ("Custo da Meta no mês", "R$ 38,40", "teto de marketing: R$ 150,00"),
        ])
        + wa
    )
    return pagina("nv-whatsapp", corpo)


# ----------------------------------------------------------------------------------------------
# 11. Agente de atendimento
# ----------------------------------------------------------------------------------------------
def tela_agente() -> str:
    pode = "".join(
        f'<div class="nv-linha-config"><div class="meio"><b>{t}</b><span>{d}</span></div>{switch(t, on)}</div>'
        for t, d, on in [
            ("Responder dúvidas", "horário, endereço, formas de pagamento, taxa de entrega", True),
            ("Consultar preço e estoque", "sempre com o preço do sistema, nunca inventa", True),
            ("Montar pedido de entrega", "envia para o Delivery depois do pagamento ou da confirmação", True),
            ("Gerar Pix e confirmar pagamento", "QR dinâmico, confirmação automática", True),
            ("Vender na Confiança (fiado)", "só para clientes com limite cadastrado", True),
            ("Dar desconto", "nunca: passa para alguém da loja", False),
            ("Atender fora do horário", "anota o pedido para a hora que a loja abrir", True),
        ]
    )
    conhecimento = tabela(
        ["Pergunta que apareceu", "Resposta aprovada pela loja", ""],
        [
            ["Vocês alugam freezer/caixa térmica?", "Emprestamos caixa térmica de 120L para pedidos acima de R$ 300, com caução de R$ 50.", tag("ok", "aprovada")],
            ["Tem cerveja sem álcool?", "Temos Heineken 0.0 long neck, R$ 7,90.", tag("ok", "aprovada")],
            ["Entregam em condomínio fechado?", "Sim, deixamos na portaria ou subimos até o apartamento se o condomínio liberar.", tag("ok", "aprovada")],
            ["Fazem nota no CNPJ?", "<i class=\"muted\">sugestão da IA: “Sim, emitimos nota com CNPJ. Informe os dados no pedido.”</i>", btn("Aprovar", "nv-btn-mini cheio", "Resposta aprovada: o agente passa a usar.")],
        ],
    )
    teste = (
        '<div class="nv-wa-thread" style="border:1px solid var(--line);border-radius:14px;overflow:hidden;height:420px">'
        '<div class="nv-wa-topo"><span class="nv-avatar">IA</span><div class="meio"><b>Testar o agente</b><br><span>finja que é um cliente</span></div></div>'
        '<div class="nv-wa-msgs"><div class="nv-msg saida"><span class="quem">Agente de IA</span>Oi! Aqui é o atendimento da SUA MARCA 🍻 Como posso ajudar?<span class="hora">agora</span></div></div>'
        '<form class="nv-wa-rodape" data-wa-form="teste"><input type="text" placeholder="Ex.: tem gelo? qual a taxa de entrega?" aria-label="Mensagem de teste">'
        '<button type="submit" class="btn-principal">Enviar</button></form></div>'
        '<p class="muted small" style="margin:8px 0 0">Experimente: “tem gelo?”, “qual o horário?”, “aceita cartão?”, “quanto é o fardo de cerveja?”.</p>'
    )
    corpo = (
        topo("Agente de atendimento", "Um atendente de IA no WhatsApp da loja que conhece seus produtos, preços e clientes e aprende com as suas aprovações.",
             btn("Salvar", "btn-principal btn-alto", "Configuração do agente salva."))
        + kpis([
            ("Atendimentos no mês", "1.312", "<b class=\"ok\">85%</b> resolvidos sem ninguém da loja"),
            ("Vendido pelo agente", "R$ 18.946,30", "247 pedidos no mês"),
            ("Satisfação", "4,8 / 5", "pesquisa após o atendimento"),
            ("Custo de IA no mês", "R$ 27,90", "≈ R$ 0,02 por conversa"),
        ])
        + '<div class="nv-grade-lado"><div class="nv-pilha">'
        + card("Jeito de falar", '<div class="nv-form">'
               '<label>Nome do atendente<input type="text" value="Bia, da SUA MARCA"></label>'
               '<label>Tom<select><option>Simpático e direto, com emojis</option><option>Formal</option><option>Descontraído</option></select></label>'
               '<label>Recado fixo<textarea rows="2">Pedidos acima de R$ 150 têm entrega grátis! Aos sábados temos chopp gelado.</textarea></label></div>')
        + card("O que o agente pode fazer", pode)
        + card("Conhecimento aprendido", conhecimento, '<span class="muted small">perguntas novas viram resposta depois que você aprova</span>')
        + "</div>" + card("Teste antes de ligar", teste) + "</div>"
    )
    return pagina("nv-agente", corpo)


# ----------------------------------------------------------------------------------------------
# 12. Campanhas automáticas (Relacionamento)
# ----------------------------------------------------------------------------------------------
def tela_relacionamento() -> str:
    def aut(ic, titulo, desc, enviados, retorno, ligado=True):
        return (
            f'<div class="nv-modulo{" ligado" if ligado else ""}"><span class="nv-ico">{ic}</span><div class="meio"><b>{titulo}</b><span>{desc}</span>'
            f'<div class="small" style="margin-top:6px"><b>{enviados}</b> enviadas no mês · retorno <b class="nv-ok">{retorno}</b></div></div>{switch(titulo, ligado)}</div>'
        )

    auts = (
        '<div class="nv-grade-2">'
        + aut("⏰", "Antes do horário de costume", "Quem compra toda sexta às 18h recebe às 16h: “Já separo sua Heineken e o gelo?”", 86, "R$ 6.120,40")
        + aut("🎂", "Aniversário", "Parabéns com um mimo: 10% em um fardo na semana do aniversário", 12, "R$ 842,00")
        + aut("💰", "Cashback para vencer", "Avisa 5 dias antes do cashback expirar", 34, "R$ 1.912,60")
        + aut("👋", "Cliente sumido", "Quem não compra há 2× o intervalo normal recebe um “sentimos sua falta”", 19, "R$ 1.104,90")
        + aut("⭐", "Cartão fidelidade", "Avisa quando falta 1 selo para ganhar o prêmio", 23, "R$ 980,30")
        + aut("🤝", "Confiança em dia", "Lembrete gentil 2 dias antes do vencimento do fiado", 9, "R$ 1.320,00", False)
        + "</div>"
    )
    previa = (
        '<div class="nv-wa-msgs" style="border-radius:14px;border:1px solid var(--line);min-height:auto">'
        '<div class="nv-msg saida"><span class="quem">SUA MARCA</span>Oi, Marcelo! 🍻 Sexta-feira chegou. Quer que eu já separe as suas 2 Spaten de 12 e o gelo, como sempre? É só responder SIM que a gente entrega até as 19h.\n\nPara não receber mais, responda SAIR.<span class="hora">16:00</span></div>'
        '<div class="nv-msg">SIM! manda tbm um carvão<span class="hora">16:03</span></div>'
        '<div class="nv-wa-sistema">Pedido #2029 criado pelo agente de IA · R$ 152,70</div></div>'
    )
    lgpd = (
        '<ul class="nv-linhas">'
        '<li><div class="cresce"><b>Aceitaram receber mensagens</b><span>pediram pelo WhatsApp ou no caixa</span></div><span class="valor">214 clientes</span></li>'
        '<li><div class="cresce"><b>Pediram para sair</b><span>respondendo SAIR (respeitado na hora)</span></div><span class="valor">7</span></li>'
        '<li><div class="cresce"><b>1º envio de cada tipo</b><span>precisa da sua aprovação</span></div>' + tag("ok", "ligado") + "</li>"
        '<li><div class="cresce"><b>Gasto estimado na Meta</b><span>mensagens de marketing no mês</span></div><span class="valor">R$ 38,40</span></li>'
        "</ul>"
    )
    corpo = (
        topo("Campanhas automáticas", "Mensagens pessoais no WhatsApp, na hora certa, só para quem aceitou receber. A IA escreve, você aprova a primeira de cada tipo.",
             btn("+ Campanha avulsa", "btn-principal btn-alto", "Escolha o público (ex.: quem comprou whisky nos últimos 60 dias) e a mensagem."))
        + kpis([
            ("Mensagens no mês", "183", "taxa de leitura 92%"),
            ("Vendas que vieram das mensagens", "R$ 10.960,20", "<b class=\"ok\">retorno de 285×</b> o custo"),
            ("Clientes que voltaram", "14", "estavam sumidos"),
            ("Opt-in", "214", "clientes aceitaram receber"),
        ])
        + '<div class="nv-grade-lado"><div class="nv-pilha">' + card("Automações", auts) + "</div>"
        + '<div class="nv-pilha">' + card("Como chega para o cliente", previa) + card("Consentimento e LGPD", lgpd) + "</div></div>"
    )
    return pagina("nv-relacionamento", corpo)


# ----------------------------------------------------------------------------------------------
# 13. Fidelidade e cashback
# ----------------------------------------------------------------------------------------------
def tela_fidelizacao() -> str:
    ranking = tabela(
        ["#", "Cliente", "Compras", "Cashback", "Selos", "Total gasto"],
        [
            ["1", "<b>Bar & Petiscaria Recanto</b>", "26", "R$ 84,30", "<div class=\"nv-progresso\" style=\"width:110px;height:8px\"><span style=\"width:90%\"></span></div><span class=\"small muted\">9 de 10</span>", "<b>R$ 8.420,00</b>"],
            ["2", "<b>Rodrigo Eventos & Churrascos</b>", "14", "R$ 112,60", "<div class=\"nv-progresso\" style=\"width:110px;height:8px\"><span style=\"width:40%\"></span></div><span class=\"small muted\">4 de 10</span>", "<b>R$ 7.986,40</b>"],
            ["3", "<b>Churrascaria Boi Dourado</b>", "11", "R$ 58,90", "<div class=\"nv-progresso\" style=\"width:110px;height:8px\"><span style=\"width:70%\"></span></div><span class=\"small muted\">7 de 10</span>", "<b>R$ 5.120,80</b>"],
            ["4", "<b>Quadra Society Arena Gol</b>", "18", "R$ 41,20", "<div class=\"nv-progresso\" style=\"width:110px;height:8px\"><span style=\"width:80%\"></span></div><span class=\"small muted\">8 de 10</span>", "<b>R$ 3.842,10</b>"],
            ["5", "<b>Marcelo Tavares</b>", "21", "R$ 23,70", "<div class=\"nv-progresso ok\" style=\"width:110px;height:8px\"><span style=\"width:100%\"></span></div><span class=\"small muted\">10 de 10</span>", "<b>R$ 1.912,60</b>"],
            ["6", "<b>Juliana Costa</b>", "9", "R$ 12,40", "<div class=\"nv-progresso\" style=\"width:110px;height:8px\"><span style=\"width:30%\"></span></div><span class=\"small muted\">3 de 10</span>", "<b>R$ 824,30</b>"],
        ],
        (5,),
    )
    regras = (
        '<div class="nv-linha-config"><div class="meio"><b>Cashback</b><span>% de volta em toda compra, para usar na próxima</span></div><b>3%</b></div>'
        '<div class="nv-linha-config"><div class="meio"><b>Validade do cashback</b><span>avisado no WhatsApp 5 dias antes</span></div><b>60 dias</b></div>'
        '<div class="nv-linha-config"><div class="meio"><b>Cartão fidelidade</b><span>a cada compra acima de R$ 50 ganha 1 selo</span></div><b>10 selos = 1 fardo</b></div>'
        '<div class="nv-linha-config"><div class="meio"><b>Uso mínimo</b><span>o cliente usa o saldo direto no caixa, pelo CPF</span></div><b>R$ 5,00</b></div>'
    )
    corpo = (
        topo("Fidelidade e cashback", "Cashback, cartão fidelidade digital e os clientes que mais compram. O cliente vê o saldo no WhatsApp e usa no caixa pelo CPF.",
             btn("Configurar programa", "btn-secundario", "Percentual, validade e prêmio do cartão fidelidade."))
        + kpis([
            ("Cashback distribuído (mês)", "R$ 1.284,60", "312 compras"),
            ("Cashback usado (mês)", "R$ 846,10", "66% voltou como venda"),
            ("Clientes no programa", "268", "<b class=\"ok\">+31</b> no mês"),
            ("Frequência de quem participa", "2,4×", "mais que quem não participa"),
        ])
        + '<div class="nv-grade-lado">' + card("Melhores clientes", ranking)
        + '<div class="nv-pilha">' + card("Regras do programa", regras)
        + card("Prêmios para entregar", '<ul class="nv-linhas">'
               '<li><span class="nv-ico">🎁</span><div class="cresce"><b>Marcelo Tavares</b><span>completou 10 selos · ganhou 1 Fardo Spaten</span></div>' + btn("Entregar", "nv-btn-mini cheio", "Prêmio entregue e baixado do estoque.") + "</li>"
               '<li><span class="nv-ico">🎁</span><div class="cresce"><b>Bar & Petiscaria Recanto</b><span>falta 1 selo · avisado no WhatsApp</span></div></li></ul>')
        + "</div></div>"
    )
    return pagina("nv-fidelizacao", corpo)


# ----------------------------------------------------------------------------------------------
# 14. Identidade da marca (White Label)
# ----------------------------------------------------------------------------------------------
TEMAS = [
    ("Azul tecnológico", "#0D6EFD", "#F97316", "#1E293B"),
    ("Dourado premium", "#B8860B", "#D4AF37", "#16130E"),
    ("Verde mercado", "#15803D", "#F59E0B", "#14261A"),
    ("Vinho adega", "#9F1239", "#D97706", "#2A0E16"),
    ("Roxo açaí", "#7E22CE", "#EC4899", "#1E1033"),
    ("Laranja obra", "#C2410C", "#FACC15", "#1C1917"),
    ("Rosa moda", "#BE185D", "#0EA5E9", "#241019"),
    ("Grafite", "#334155", "#0EA5E9", "#0F172A"),
]


def tela_identidade() -> str:
    temas = "".join(
        f'<button type="button" class="nv-tema" data-primaria="{p}" data-destaque="{d}" data-menu="{m}">'
        f'<div class="faixas"><i style="background:{m}"></i><i style="background:{p}"></i><i style="background:{d}"></i></div><b>{n}</b></button>'
        for n, p, d, m in TEMAS
    )
    cores = (
        '<div class="nv-cores">'
        '<label class="nv-cor"><input type="color" name="primaria"><div><b>Cor principal</b><span data-hex="primaria"></span><div class="muted small">botões, menu ativo, gráficos</div></div></label>'
        '<label class="nv-cor"><input type="color" name="destaque"><div><b>Cor de destaque</b><span data-hex="destaque"></span><div class="muted small">avisos e cartões em destaque</div></div></label>'
        '<label class="nv-cor"><input type="color" name="menu"><div><b>Fundo do menu</b><span data-hex="menu"></span><div class="muted small">barra lateral</div></div></label>'
        "</div>"
        '<div class="nv-contraste" data-contraste></div>'
    )
    previa = (
        '<div class="nv-previa"><div class="nv-previa-menu"><div class="marca"><img data-previa-logo src="./static/img/logo-marca.svg" alt=""><span data-previa-nome>SUA MARCA</span></div>'
        '<span>Vender</span><span class="ativo">Painel</span><span>Produtos</span><span>Clientes</span><span>WhatsApp</span></div>'
        '<div class="nv-previa-corpo"><div class="k"><small>Faturamento</small><b>R$ 1.588,30</b></div>'
        '<div class="k dest"><small>A receber na Confiança</small><b>R$ 2.120,00</b></div>'
        '<div><button type="button" class="btn-principal">Finalizar venda</button></div></div></div>'
    )
    onde = (
        '<ul class="nv-linhas">'
        '<li><span class="nv-ico">🖥️</span><div class="cresce"><b>Sistema inteiro</b><span>menu, botões, gráficos, tela do caixa</span></div></li>'
        '<li><span class="nv-ico">🧾</span><div class="cresce"><b>Cupom e DANFE</b><span>nome e logo no topo do cupom</span></div></li>'
        '<li><span class="nv-ico">📱</span><div class="cresce"><b>Cardápio digital e página da loja</b><span>cores e logo no celular do cliente</span></div></li>'
        '<li><span class="nv-ico">💬</span><div class="cresce"><b>WhatsApp</b><span>nome do atendente e assinatura das mensagens</span></div></li>'
        '<li><span class="nv-ico">📄</span><div class="cresce"><b>PDFs</b><span>relatórios, orçamentos e recibos</span></div></li>'
        "</ul>"
    )
    corpo = (
        '<form data-identidade>'
        + topo("Identidade da marca", "White Label completo: o sistema inteiro com o nome, a logo e as cores do cliente. Mude aqui e veja tudo mudar na hora.",
               '<button type="button" class="btn-secundario" data-restaurar-marca>Restaurar padrão</button>'
               '<button type="submit" class="btn-principal btn-alto">Aplicar em todo o sistema</button>')
        + '<div class="nv-faixa">✨ Teste ao vivo: escolha um tema pronto ou mexa nas cores. A tela muda na hora. Clique em <b>Aplicar em todo o sistema</b> e navegue pelo menu.</div>'
        + '<div class="nv-grade-lado"><div class="nv-pilha">'
        + card("Nome e logo", '<div class="nv-form"><label>Nome da marca<input type="text" name="nome" maxlength="28"></label>'
               '<div class="nv-logo-area"><img data-previa-logo src="./static/img/logo-marca.svg" alt="Logo">'
               '<label class="btn-secundario" style="cursor:pointer">Enviar logo (PNG ou SVG)<input type="file" accept="image/*" data-logo-arquivo hidden></label></div>'
               '<label>Endereço da loja<input type="text" value="suamarca.optimapdv.com.br" readonly></label></div>')
        + card("Temas prontos", f'<div class="nv-temas">{temas}</div>', '<span class="muted small">1 clique</span>')
        + card("Cores da marca", cores, '<span class="muted small">o sistema confere o contraste para manter a leitura</span>')
        + "</div><div class=\"nv-pilha\">"
        + card("Prévia ao vivo", previa)
        + card("Onde a marca aparece", onde)
        + "</div></div></form>"
    )
    return pagina("nv-identidade", corpo)


# ----------------------------------------------------------------------------------------------
# 15. Minha página
# ----------------------------------------------------------------------------------------------
def tela_minha_pagina() -> str:
    celular = (
        '<div class="nv-celular"><div class="nv-celular-tela">'
        '<div class="nv-celular-topo" style="padding:26px 18px"><img data-marca-logo src="./static/img/logo-marca.svg" alt="">'
        '<b style="font-size:22px">SUA MARCA</b><small>Distribuidora de bebidas · gelo · carvão</small>'
        '<div style="margin-top:14px;display:flex;gap:8px;flex-wrap:wrap"><span style="background:#25D366;color:#fff;padding:8px 12px;border-radius:10px;font-weight:800;font-size:13px">💬 Pedir no WhatsApp</span>'
        '<span style="background:rgba(255,255,255,.2);padding:8px 12px;border-radius:10px;font-weight:700;font-size:13px">Ver cardápio</span></div></div>'
        '<div style="padding:14px"><b>🕒 Horário</b><div class="muted small">Seg a sáb 9h–23h · Dom 9h–22h</div>'
        '<b style="display:block;margin-top:10px">📍 Endereço</b><div class="muted small">Av. Central, 1500 · Centro · entrega em até 5 km</div>'
        '<b style="display:block;margin-top:10px">⭐ Avaliações</b><div class="muted small">4,9 no Google (318 avaliações)</div></div>'
        '<div class="nv-cel-item"><div class="foto">🍺</div><div class="meio"><b>Cerveja trincando</b><span>fardos com entrega em 35 min</span></div></div>'
        '<div class="nv-cel-item"><div class="foto">🧊</div><div class="meio"><b>Gelo e carvão</b><span>para o seu churrasco</span></div></div>'
        '<div class="nv-cel-item"><div class="foto">🎉</div><div class="meio"><b>Eventos</b><span>orçamento para festas e casamentos</span></div></div>'
        "</div></div>"
    )
    utm = tabela(
        ["Link de campanha", "Visitas", "Pedidos", "Vendas"],
        [
            ["<b>Instagram · bio</b><div class=\"small muted nv-mono\">?utm_source=instagram</div>", "1.204", "68", "<b>R$ 7.840,20</b>"],
            ["<b>Panfleto do condomínio</b><div class=\"small muted nv-mono\">QR · utm_campaign=panfleto</div>", "312", "24", "<b>R$ 2.910,60</b>"],
            ["<b>Google Meu Negócio</b><div class=\"small muted nv-mono\">?utm_source=google</div>", "846", "41", "<b>R$ 4.620,00</b>"],
            ["<b>Status do WhatsApp</b><div class=\"small muted nv-mono\">?utm_source=whatsapp</div>", "550", "51", "<b>R$ 6.090,10</b>"],
        ],
        (1, 2, 3),
    )
    corpo = (
        topo("Minha página", "O site da loja, pronto em minutos, no endereço próprio. Com botão de WhatsApp, cardápio, horário e links para medir cada campanha.",
             btn("Editar página", "btn-secundario", "Edite textos, fotos e seções; publica com um clique.")
             + btn("Publicar", "btn-principal btn-alto", "Página publicada em suamarca.optimapdv.com.br"))
        + kpis([
            ("Visitas no mês", "2.912", "<b class=\"ok\">+36%</b> sobre outubro"),
            ("Cliques no WhatsApp", "684", "23% das visitas"),
            ("Pedidos vindos da página", "184", "R$ 21.460,90"),
            ("Situação", "● Publicada", "suamarca.optimapdv.com.br"),
        ])
        + '<div class="nv-grade-lado"><div class="nv-pilha">'
        + card("De onde vêm os clientes", utm, btn("+ Criar link com QR", "nv-btn-mini", "Link de campanha criado, com QR para imprimir."))
        + card("Seções da página", "".join(
            f'<div class="nv-linha-config"><div class="meio"><b>{t}</b><span>{d}</span></div>{switch(t, on)}</div>'
            for t, d, on in [("Capa com logo e botão de WhatsApp", "primeira coisa que o cliente vê", True),
                             ("Cardápio com preços", "sempre igual ao estoque do sistema", True),
                             ("Horário e mapa", "com rota no Google Maps", True),
                             ("Eventos e orçamentos", "formulário que vira orçamento no sistema", True),
                             ("Medição de visitas", "só depois que o visitante aceita os cookies", True)]))
        + "</div>" + card("Prévia no celular", celular) + "</div>"
    )
    return pagina("nv-minha-pagina", corpo)


# ----------------------------------------------------------------------------------------------
# 16. Plano e módulos
# ----------------------------------------------------------------------------------------------


PRECOS_PLANO = {
    "fiscal": "+ R$ 39/mês", "balanca": "+ R$ 19/mês", "producao": "+ R$ 19/mês", "cardapio": "+ R$ 19/mês",
    "comandas": "+ R$ 19/mês", "delivery": "+ R$ 10/mês", "whatsapp": "+ R$ 79/mês", "fidelidade": "+ R$ 29/mês",
    "grade": "+ R$ 19/mês", "inteligencia": "+ R$ 39/mês",
}
LIGADOS_PLANO = {"fiscal", "balanca", "cardapio", "comandas", "delivery", "whatsapp", "fidelidade", "grade", "inteligencia"}


def tela_plano() -> str:
    mods = seletor_modulos(
        LIGADOS_PLANO, "Personalize seus módulos",
        "O plano já inclui o essencial. Ligue só o que faz sentido para a sua operação; a mensalidade acompanha.",
        "Você pode ativar ou desativar módulos a qualquer momento. A mudança vale na próxima fatura.",
        btn("Salvar módulos" + SETA, "btn-principal", "Módulos salvos. A próxima fatura já considera a mudança."),
        PRECOS_PLANO,
    )
    faturas = tabela(
        ["Mês", "Situação", "Valor"],
        [
            ["Novembro/2026<div class=\"small muted\">vence 10/11 · cartão final 4421</div>", tag("aviso", "a vencer"), "<b>R$ 350,00</b>"],
            ["Outubro/2026<div class=\"small muted\">cartão final 4421</div>", tag("ok", "paga"), "<b>R$ 312,00</b>"],
            ["Setembro/2026<div class=\"small muted\">Pix</div>", tag("ok", "paga"), "<b>R$ 233,00</b>"],
            ["Agosto/2026<div class=\"small muted\">Pix</div>", tag("ok", "paga"), "<b>R$ 233,00</b>"],
        ],
        (2,),
    )
    corpo = (
        topo("Plano e módulos", "O cliente paga só pelo que usa: um plano base e os módulos que fazem sentido para o ramo dele. Liga e desliga na hora.",
             btn("Trocar cartão", "btn-secundario", "Troca de cartão segura pelo provedor de pagamento."))
        + '<div class="nv-faixa aviso">Preços ilustrativos da demonstração.</div>'
        + kpis([
            ("Plano", "Inicial", "R$ 59/mês · 1 caixa"),
            ("Módulos ligados", "12 de 13", "R$ 272/mês em módulos"),
            ("Mensalidade", "R$ 350,00", "próxima cobrança em 10/11"),
            ("Caixas", "2", "1 incluído + 1 extra (R$ 19)"),
        ])
        + f'<div class="card" style="margin-bottom:18px">{mods}</div>'
        + '<div class="nv-grade-lado">' + card("Faturas", faturas)
        + card("Como funciona", '<ul class="nv-linhas">'
               '<li><span class="nv-ico">🧪</span><div class="cresce"><b>Teste grátis de 5 dias</b><span>com todos os módulos</span></div></li>'
               '<li><span class="nv-ico">💳</span><div class="cresce"><b>Cartão recorrente, Pix ou boleto</b><span>aviso 3 dias antes do vencimento</span></div></li>'
               '<li><span class="nv-ico">🔒</span><div class="cresce"><b>Sem bloqueio surpresa</b><span>5 dias de carência, depois só leitura: os dados nunca somem</span></div></li></ul>')
        + "</div>"
    )
    return pagina("nv-plano", corpo)


PAGINAS = {
    "comandas.html": ("Comandas e mesas", tela_comandas()),
    "cozinha.html": ("Cozinha / Bar", tela_cozinha()),
    "delivery.html": ("Delivery", tela_delivery()),
    "cardapio.html": ("Cardápio digital", tela_cardapio()),
    "orcamentos.html": ("Orçamentos", tela_orcamentos()),
    "trocas.html": ("Trocas e devoluções", tela_trocas()),
    "fiscal.html": ("Nota fiscal (NFC-e)", tela_fiscal()),
    "inteligencia.html": ("Inteligência", tela_inteligencia()),
    "fluxo_caixa.html": ("Fluxo de caixa", tela_fluxo()),
    "whatsapp.html": ("WhatsApp", tela_whatsapp()),
    "agente.html": ("Agente de atendimento", tela_agente()),
    "relacionamento.html": ("Campanhas automáticas", tela_relacionamento()),
    "fidelizacao.html": ("Fidelidade e cashback", tela_fidelizacao()),
    "identidade.html": ("Identidade da marca", tela_identidade()),
    "minha_pagina.html": ("Minha página", tela_minha_pagina()),
    "plano.html": ("Plano e módulos", tela_plano()),
}
