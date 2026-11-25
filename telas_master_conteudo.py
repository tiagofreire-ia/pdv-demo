"""Área Master (equipe Óptima), separada do sistema das lojas.

Mostra a SITUAÇÃO REAL da plataforma em pré-lançamento: 1 cliente piloto em produção (sistema
dedicado de uma distribuidora de bebidas) e as 4 lojas de demonstração. Onde ainda não há dado
real (pré-cadastros, chamados), a tela mostra o estado vazio e um botão "Simular" claramente
identificado.
"""
from __future__ import annotations

from telas_novas_conteudo import btn, card, kpis, pagina, switch, tabela, tag, topo

LOGO = "./static/img/lojas/"

LOJAS = [
    # (arquivo da logo ou None, nome, endereço, ramo, situação (cls, texto), módulos, cobrança (cls, texto))
    (None, "Distribuidora de bebidas", "sistema dedicado", "Bebidas", ("ok", "Em produção · 3 meses"), "Caixa, estoque, fiado, IA", ("info", "Cliente piloto")),
    ("pao-dourado", "Padaria Pão Dourado", "loja-demo.optimapdv.com.br", "Padaria", ("info", "Demonstração"), "10 de 11", ("", "Isenta (demo)")),
    ("atelie-lume", "Ateliê Lume", "demo-moda.optimapdv.com.br", "Roupas e calçados", ("info", "Demonstração"), "8 de 11", ("", "Isenta (demo)")),
    ("casa-forte", "Casa Forte Materiais", "demo-obra.optimapdv.com.br", "Material de construção", ("info", "Demonstração"), "8 de 11", ("", "Isenta (demo)")),
    ("bom-gole", "Adega Bom Gole", "adegabomgole.optimapdv.com.br", "Adega e bebidas", ("info", "Demonstração"), "11 de 11", ("", "Isenta (demo)")),
]


def celula_loja(logo, nome, sub, link="./master_loja.html"):
    img = (f'<img class="nv-logo-loja" src="{LOGO}{logo}.png" alt="">' if logo
           else '<span class="nv-loja-ini" aria-hidden="true">DB</span>')
    return f'<div class="nv-celula-loja">{img}<div><a class="pr-nome" href="{link}"><b>{nome}</b></a><span class="small muted nv-mono">{sub}</span></div></div>'


def linhas_lojas(com_modulos=True):
    out = []
    for logo, nome, end, ramo, sit, mods, cob in LOJAS:
        link = "./master_loja.html" if logo == "pao-dourado" else "#"
        linha = [celula_loja(logo, nome, end, link), ramo, tag(*sit)]
        if com_modulos:
            linha.append(mods)
        linha.append(tag(*cob))
        out.append(linha)
    return out


# ----------------------------------------------------------------------------------------------
def tela_visao_geral() -> str:
    marcos = (
        '<ul class="nv-linhas">'
        '<li><span class="nv-ico">✅</span><div class="cresce"><b>Fases 1 a 13 concluídas</b><span>caixa, estoque, cobrança, cardápio, fiscal, IA, WhatsApp, inteligência e design</span></div></li>'
        '<li><span class="nv-ico">🔎</span><div class="cresce"><b>Fase 14: verificação do sistema inteiro</b><span>Tiago e Lucas passando por 9 famílias de telas em 6 aparelhos</span></div>' + tag("info", "em andamento") + '</li>'
        '<li><span class="nv-ico">🚀</span><div class="cresce"><b>Lançamento</b><span>servidor de produção, domínio e HTTPS</span></div>' + tag("aviso", "próximo") + '</li>'
        '<li><span class="nv-ico">🧾</span><div class="cresce"><b>Nota fiscal na SEFAZ</b><span>emissão real com provedor homologado</span></div>' + tag("aviso", "próximo") + '</li>'
        '<li><span class="nv-ico">💬</span><div class="cresce"><b>WhatsApp oficial</b><span>Óptima como parceira de tecnologia da Meta</span></div>' + tag("aviso", "próximo") + '</li>'
        "</ul>"
    )
    rotinas = (
        '<ul class="nv-linhas">'
        '<li><div class="cresce"><b>Cobrança diária</b><span>gera faturas 5 dias antes, avisa 3 dias antes, carência e só leitura</span></div>' + tag("ok", "ativa") + "</li>"
        '<li><div class="cresce"><b>Backup do banco</b><span>todo dia</span></div>' + tag("ok", "ativa") + "</li>"
        '<li><div class="cresce"><b>Limpeza do WhatsApp (LGPD)</b><span>retenção de 30/90 dias</span></div>' + tag("ok", "ativa") + "</li>"
        '<li><div class="cresce"><b>Ofertas programadas</b><span>ligam e desligam sozinhas em cada loja</span></div>' + tag("ok", "ativa") + "</li>"
        "</ul>"
    )
    corpo = (
        topo("Visão geral", "A plataforma Óptima PDV em pré-lançamento: o cliente piloto em produção e as lojas de demonstração de cada ramo.",
             '<a class="btn-principal btn-alto" href="./master_nova_loja.html">+ Nova loja</a>')
        + '<div class="nv-faixa">Situação real da plataforma. A cobrança das lojas começa no lançamento.</div>'
        + kpis([
            ("Lojas na plataforma", "5", "1 cliente piloto + 4 demonstrações"),
            ("Cliente em produção", "3 meses", "distribuidora de bebidas, todos os dias"),
            ("Módulos prontos", "11", "ligados e desligados por loja"),
            ("Fase do projeto", "14 de 15", "verificação antes do lançamento"),
        ])
        + '<div class="nv-grade-lado"><div class="nv-pilha">'
        + card("Lojas", tabela(["Loja", "Situação", "Cobrança"], [[l[0], l[2], l[3]] for l in linhas_lojas(com_modulos=False)]),
               '<a class="link-ouro" href="./master_lojas.html">ver todas</a>')
        + card("Caminho até o lançamento", marcos)
        + '</div><div class="nv-pilha">'
        + card("Atalhos", '<div class="nv-pilha" style="gap:10px">'
               '<a class="btn-principal" href="./master_nova_loja.html">+ Criar uma loja</a>'
               '<a class="btn-secundario" href="./master_pre_cadastros.html">Pré-cadastros do site</a>'
               '<a class="btn-secundario" href="./master_cobranca.html">Cobrança</a></div>')
        + card("Rotinas automáticas", rotinas)
        + card("Pendências agora", '<div class="nv-vazio"><div class="ic">✨</div><b>Nada pendente</b>0 chamados abertos · 0 operações com falha · 0 pré-cadastros</div>')
        + "</div></div>"
    )
    return pagina("nv-master", corpo)


# ----------------------------------------------------------------------------------------------
def tela_lojas() -> str:
    corpo = (
        topo("Lojas", "Todas as lojas da plataforma, cada uma no próprio endereço, com a própria marca e os dados isolados.",
             '<a class="btn-principal btn-alto" href="./master_nova_loja.html">+ Nova loja</a>')
        + '<div class="pr-filtros"><form class="pr-busca"><input type="search" placeholder="Buscar por nome, endereço ou CNPJ" aria-label="Buscar loja"></form>'
        '<a class="filtro-chip ativo" href="#">Todas · 5</a><a class="filtro-chip" href="#">Em produção · 1</a><a class="filtro-chip" href="#">Demonstração · 4</a>'
        '<a class="filtro-chip" href="#">Em teste · 0</a><a class="filtro-chip" href="#">Só leitura · 0</a></div>'
        + card("Lojas", tabela(["Loja", "Ramo", "Situação", "Módulos", "Cobrança"], linhas_lojas()),
               '<span class="muted small">clique na Padaria Pão Dourado para abrir a ficha</span>')
        + '<div class="nv-grade-3 nv-secao">'
        + card("Isolamento dos dados", '<p style="margin:0">Cada tabela do banco tem regra de acesso por loja, com <b>teste automático de vazamento</b> em todas elas: uma loja nunca enxerga os dados de outra.</p>')
        + card("Endereço próprio", '<p style="margin:0">Cada loja entra em <span class="nv-mono">nome.optimapdv.com.br</span>. O endereço pode ser trocado pelo Master sem perder dados.</p>')
        + card("Marca própria", '<p style="margin:0">Logo e 5 cores por loja, com checagem de contraste. O cupom, o cardápio e a página da loja seguem a marca.</p>')
        + "</div>"
    )
    return pagina("nv-master", corpo)


# ----------------------------------------------------------------------------------------------
MODULOS_LOJA = [
    ("Frente de caixa", True), ("Estoque, lotes e validade", True), ("Clientes e Confiança", True), ("Nota fiscal NFC-e", True),
    ("Balança e etiquetas", True), ("Produção e encomendas", True), ("Cardápio digital e Minha página", True),
    ("WhatsApp com agente de IA", True), ("Fidelidade e campanhas", True), ("Inteligência e assistente de IA", True),
    ("Grade e trocas", False),
]


def tela_ficha_loja() -> str:
    mods = "".join(
        f'<div class="nv-linha-config"><div class="meio"><b>{n}</b></div>{switch(n, on)}</div>' for n, on in MODULOS_LOJA
    )
    cabeca = (
        '<div style="display:flex;gap:18px;align-items:center;flex-wrap:wrap">'
        f'<img class="nv-logo-loja grande" src="{LOGO}pao-dourado.png" alt="Logo Padaria Pão Dourado">'
        '<div><div class="small muted">Padaria · desde 1998</div><h2 style="margin:2px 0 6px">Padaria Pão Dourado</h2>'
        '<span class="nv-mono small">loja-demo.optimapdv.com.br</span> ' + tag("info", "Demonstração") + "</div></div>"
    )
    identidade = (
        '<div style="display:flex;gap:10px;align-items:center;margin-bottom:10px">'
        '<span style="width:44px;height:44px;border-radius:10px;background:#8A4B14;display:inline-block"></span>'
        '<span style="width:44px;height:44px;border-radius:10px;background:#E3A33B;display:inline-block"></span>'
        '<span class="nv-mono small">#8A4B14 · #E3A33B</span></div>'
        '<p class="muted small" style="margin:0">Cores principal e de destaque definidas pela loja, com contraste conferido.</p>'
    )
    usuarios = tabela(["Pessoa", "Situação"], [
        ["<b>Marta Dourado</b><div class='small muted'>Administradora</div>", tag("ok", "ativa")],
        ["Usuário técnico do agente<div class='small muted'>WhatsApp (sistema)</div>", tag("", "interno")],
    ])
    corpo = (
        '<p style="margin:0 0 12px"><a class="link-ouro" href="./master_lojas.html">‹ Lojas</a></p>'
        + topo("Ficha da loja", "Tudo o que a equipe Óptima controla em uma loja, num lugar só.",
               btn("Trocar endereço", "btn-secundario", "No sistema, o endereço muda sem perder dados e o antigo redireciona.")
               + btn("Abrir como suporte", "btn-principal", "Acesso de suporte registrado na auditoria da loja e na auditoria geral."))
        + f'<div class="card" style="margin-bottom:18px">{cabeca}</div>'
        + '<div class="nv-grade-lado"><div class="nv-pilha">'
        + card("Módulos da loja", mods, '<span class="muted small">liga e desliga na hora; a mensalidade acompanha</span>')
        + "</div><div class=\"nv-pilha\">"
        + card("Cobrança", '<ul class="nv-linhas">'
               '<li><div class="cresce"><b>Situação</b><span>loja de demonstração</span></div>' + tag("", "isenta") + "</li>"
               '<li><div class="cresce"><b>Provedor</b><span>Mercado Pago (cartão, Pix e boleto)</span></div></li>'
               '<li><div class="cresce"><b>Caixas extras</b><span>além do incluído no plano</span></div><span class="valor">0</span></li></ul>')
        + card("Identidade", identidade)
        + card("Usuários", usuarios)
        + "</div></div>"
    )
    return pagina("nv-master", corpo)


# ----------------------------------------------------------------------------------------------
def tela_nova_loja() -> str:
    ramos = [
        ("Adega e bebidas", "whatsapp,delivery,comandas,fiscal"), ("Padaria", "balanca,producao,fiscal"),
        ("Mercearia", "balanca,fiscal,whatsapp"), ("Roupas e calçados", "grade,fidelidade"),
        ("Material de construção", "fiscal,whatsapp"), ("Açaí e lanchonete", "cardapio,comandas,delivery"),
        ("Hortifruti", "balanca"), ("Açougue", "balanca,fiscal"), ("Perfumaria", "fidelidade,grade"), ("Papelaria", "fiscal"),
    ]
    opcoes = "".join(f'<option data-modulos="{m}">{n}</option>' for n, m in ramos)
    mods = [
        ("caixa", "Frente de caixa", "incluído no plano", True), ("estoque", "Estoque, lotes e validade", "incluído no plano", True),
        ("clientes", "Clientes e Confiança", "incluído no plano", True), ("fiscal", "Nota fiscal NFC-e", "", False),
        ("balanca", "Balança e etiquetas", "", False), ("producao", "Produção e encomendas", "", False),
        ("cardapio", "Cardápio digital e Minha página", "", False), ("comandas", "Comandas e cozinha", "", False),
        ("delivery", "Delivery", "", False), ("whatsapp", "WhatsApp com agente de IA", "", False),
        ("fidelidade", "Fidelidade e campanhas", "", False), ("grade", "Grade e trocas", "", False),
        ("inteligencia", "Inteligência e assistente de IA", "", False),
    ]
    checks = "".join(
        f'<label><input type="checkbox" data-modulo="{k}" data-base="{"sim" if base else "nao"}"{" checked" if base else ""}{" disabled" if base else ""}>'
        f'<div><b>{n}</b>{f"<span>{d}</span>" if d else ""}</div></label>'
        for k, n, d, base in mods
    )
    passos = (
        '<div class="nv-passos-barra"><span>1. Dados da loja</span><span>2. Módulos</span><span>3. Marca</span><span>4. Administrador</span><span>Pronto</span></div>'
        '<div data-passo="1"><div class="nv-form">'
        '<label>Nome da loja<input type="text" name="loja_nome" placeholder="Ex.: Mercearia São José"></label>'
        f'<label>Ramo<select name="loja_ramo"><option data-modulos="">Escolha o ramo…</option>{opcoes}</select></label>'
        '<label>CNPJ<input type="text" placeholder="00.000.000/0000-00"></label>'
        '<div class="muted small">Endereço da loja: <b class="nv-mono" data-slug>nome-da-loja.optimapdv.com.br</b></div></div>'
        '<div class="nv-acoes-topo" style="margin-top:18px"><button class="btn-principal" data-avancar-passo>Continuar</button></div></div>'
        '<div data-passo="2" hidden><p class="muted" style="margin-top:0">O ramo já liga os módulos mais usados. Ajuste se precisar.</p>'
        f'<div class="nv-checks">{checks}</div>'
        '<div class="nv-acoes-topo" style="margin-top:18px"><button class="btn-secundario" data-voltar-passo>Voltar</button><button class="btn-principal" data-avancar-passo>Continuar</button></div></div>'
        '<div data-passo="3" hidden><div class="nv-form">'
        '<label>Logo<input type="file" accept="image/*"></label>'
        '<div style="display:flex;gap:16px;flex-wrap:wrap"><label>Cor principal<input type="color" value="#0D6EFD"></label><label>Cor de destaque<input type="color" value="#F97316"></label></div>'
        '<p class="muted small" style="margin:0">A loja pode trocar depois em Identidade da marca. O contraste é conferido antes de salvar.</p></div>'
        '<div class="nv-acoes-topo" style="margin-top:18px"><button class="btn-secundario" data-voltar-passo>Voltar</button><button class="btn-principal" data-avancar-passo>Continuar</button></div></div>'
        '<div data-passo="4" hidden><div class="nv-form">'
        '<label>Nome do administrador<input type="text" placeholder="Quem vai administrar a loja"></label>'
        '<label>E-mail<input type="email" placeholder="email@loja.com.br"></label>'
        '<label>WhatsApp<input type="text" placeholder="(00) 00000-0000"></label>'
        '<label>Início<select><option>Teste grátis de 5 dias</option><option>Cobrar desde já</option><option>Isenta (demonstração ou parceria)</option></select></label></div>'
        '<div class="nv-acoes-topo" style="margin-top:18px"><button class="btn-secundario" data-voltar-passo>Voltar</button><button class="btn-principal" data-criar-loja>Criar loja</button></div></div>'
        '<div data-passo="5" hidden><div class="nv-vazio" style="border-style:solid"><div class="ic">🎉</div>'
        '<b><span data-resumo-nome>Nova loja</span> está no ar</b>'
        '<span class="nv-mono" data-slug>nome-da-loja.optimapdv.com.br</span><br>'
        'Banco isolado criado, módulos ligados, marca aplicada e convite enviado ao administrador. O teste grátis de 5 dias começou.</div>'
        '<div class="nv-acoes-topo" style="margin-top:18px;justify-content:center"><a class="btn-principal" href="./master_lojas.html">Ver na lista de lojas</a></div></div>'
    )
    corpo = (
        topo("Nova loja", "Do cadastro à loja no ar em poucos minutos: endereço, módulos do ramo, marca e administrador.")
        + '<div class="nv-grade-lado"><div class="card" data-assistente>' + passos + "</div>"
        + '<div class="nv-pilha">'
        + card("O que acontece ao criar", '<ul class="nv-linhas">'
               '<li><span class="nv-ico">🔐</span><div class="cresce"><b>Dados isolados</b><span>a loja nasce separada das outras</span></div></li>'
               '<li><span class="nv-ico">🌐</span><div class="cresce"><b>Endereço próprio</b><span>nome.optimapdv.com.br</span></div></li>'
               '<li><span class="nv-ico">👤</span><div class="cresce"><b>Perfis prontos</b><span>administrador, caixa e estoque, com permissões por ação</span></div></li>'
               '<li><span class="nv-ico">📧</span><div class="cresce"><b>Convite ao administrador</b><span>para criar a senha</span></div></li>'
               '<li><span class="nv-ico">🧪</span><div class="cresce"><b>Teste grátis</b><span>5 dias com tudo liberado, depois só leitura até pagar</span></div></li></ul>')
        + "</div></div>"
    )
    return pagina("nv-master", corpo)


# ----------------------------------------------------------------------------------------------
def tela_pre_cadastros() -> str:
    corpo = (
        topo("Pré-cadastros", "Quem pediu para testar pelo site de vendas (“Quero testar”). Com um clique vira uma loja em teste grátis.")
        + kpis([("Pré-cadastros", "0", "o site de vendas abre no lançamento"), ("Viraram loja", "—", "conversão do teste"),
                ("Tempo até criar a loja", "—", "meta: no mesmo dia"), ("Ramos com página pronta", "9+", "no site de vendas")])
        + card("Pedidos de teste",
               '<div class="nv-vazio" data-vazio="pre-exemplo"><div class="ic">📭</div><b>Nenhum pré-cadastro ainda</b>'
               'Os pedidos do “Quero testar” aparecem aqui assim que o site de vendas for publicado.</div>'
               '<div id="pre-exemplo" hidden><ul class="nv-linhas">'
               '<li><span class="nv-loja-ini" style="background:#15803D">MS</span><div class="cresce"><b>Mercearia São José</b><span>Mercearia · veio da página do ramo · agora</span></div>'
               + tag("aviso", "exemplo simulado")
               + btn("Criar loja", "nv-btn-mini cheio", "No sistema, abre o assistente de Nova loja já preenchido com os dados do pré-cadastro.")
               + "</li></ul></div>",
               '<button type="button" class="nv-btn-mini" data-simular="pre-exemplo" data-msg="Pré-cadastro de exemplo criado só nesta tela.">Simular um pré-cadastro</button>')
    )
    return pagina("nv-master", corpo)


# ----------------------------------------------------------------------------------------------
def tela_site() -> str:
    ramos = ["Mercearia", "Açougue", "Hortifruti", "Adega / distribuidora de bebidas", "Produtos naturais",
             "Roupas e calçados", "Perfumaria", "Papelaria", "Material de construção"]
    linhas = [[f"<b>{r}</b>", "módulos e preço do ramo, exemplos e perguntas do agente", tag("ok", "pronta")] for r in ramos]
    corpo = (
        topo("Site de vendas", "O site optimapdv.com.br é editado aqui: capa, páginas por ramo, módulos, preços, termos e o “Quero testar”.",
             btn("Ver o site", "btn-secundario", "O site de vendas é publicado junto com o lançamento da plataforma."))
        + '<div class="nv-faixa">Pronto para publicar no lançamento. As visitas e conversões aparecem aqui depois.</div>'
        + '<div class="nv-grade-lado">'
        + card("Páginas por ramo", tabela(["Ramo", "Conteúdo", "Situação"], linhas))
        + '<div class="nv-pilha">'
        + card("Seções do site", "".join(
            f'<div class="nv-linha-config"><div class="meio"><b>{t}</b></div>{switch(t, True)}</div>'
            for t in ["Capa", "Ramos", "Módulos e preços", "Quero testar (5 dias grátis)", "Termos e privacidade"]))
        + card("Medição", '<p style="margin:0">Visitas e links de campanha (UTM) <b>só depois do aceite dos cookies</b>, como manda a LGPD.</p>')
        + "</div></div>"
    )
    return pagina("nv-master", corpo)


# ----------------------------------------------------------------------------------------------
def tela_novidades() -> str:
    versoes = [
        ("0.13.0", "Design do sistema todo e White Label de 5 cores", "Temas prontos, simulador ao vivo, tema escuro e menu agrupado."),
        ("0.12.0", "Ramos do varejo, grade, orçamento e inteligência", "9 ramos novos, grade tamanho × cor, vale-troca, orçamento pelo WhatsApp, clima e sugestões."),
        ("0.11.0", "WhatsApp e relacionamento com IA", "WhatsApp oficial da loja, agente de IA que monta pedidos e mensagens automáticas com consentimento."),
        ("0.10.0", "Página da loja e site de vendas", "Minha página com QR e UTM, site de vendas e o sininho de novidades."),
        ("0.9.0", "Gestão e lotes", "Contas, fluxo de caixa, lotes e validade."),
    ]
    itens = "".join(
        f'<li><span class="nv-ico">📣</span><div class="cresce"><b>v{v} · {t}</b><span>{d}</span></div>{tag("ok", "publicada")}</li>'
        for v, t, d in versoes
    )
    corpo = (
        topo("Novidades", "O que a equipe publica aparece no sininho de todas as lojas, com o que mudou e como usar.",
             btn("+ Nova publicação", "btn-principal btn-alto", "Escreva a novidade, escolha as lojas ou os ramos e publique."))
        + card("Versões publicadas", f'<ul class="nv-linhas">{itens}</ul>', '<span class="muted small">do registro de mudanças do Óptima PDV</span>')
    )
    return pagina("nv-master", corpo)


# ----------------------------------------------------------------------------------------------
def tela_cobranca() -> str:
    regras = (
        '<ul class="nv-linhas">'
        '<li><span class="nv-ico">🧾</span><div class="cresce"><b>Fatura gerada 5 dias antes</b><span>rotina diária no banco</span></div></li>'
        '<li><span class="nv-ico">🔔</span><div class="cresce"><b>Aviso 3 dias antes</b><span>e faixa de aviso dentro do sistema da loja</span></div></li>'
        '<li><span class="nv-ico">⏳</span><div class="cresce"><b>5 dias de carência</b><span>a loja continua usando normalmente</span></div></li>'
        '<li><span class="nv-ico">🔒</span><div class="cresce"><b>Só leitura no 6º dia</b><span>sem bloqueio: os dados nunca somem</span></div></li></ul>'
    )
    provedores = (
        '<ul class="nv-linhas">'
        '<li><div class="cresce"><b>Mercado Pago</b><span>cartão recorrente, Pix e boleto</span></div>' + tag("ok", "pronto") + "</li>"
        '<li><div class="cresce"><b>Asaas</b></div>' + tag("", "em breve") + "</li>"
        '<li><div class="cresce"><b>Stripe</b></div>' + tag("", "em breve") + "</li>"
        '<li><div class="cresce"><b>Hotmart</b></div>' + tag("", "em breve") + "</li></ul>"
    )
    linhas = [[celula_loja(l[0], l[1], l[2]), tag(*l[6]), "—"] for l in LOJAS]
    corpo = (
        topo("Cobrança", "As lojas pagam sozinhas: assinatura no cartão, Pix ou boleto, com avisos automáticos e sem bloqueio surpresa.",
             '<a class="btn-secundario" href="./master_precos.html">Tabela de preços</a>')
        + '<div class="nv-faixa">A cobrança das lojas começa no lançamento. Hoje o cliente piloto está em condição de piloto e as lojas de demonstração são isentas.</div>'
        + kpis([("Lojas pagantes", "0", "cobrança começa no lançamento"), ("Isentas", "4", "lojas de demonstração"),
                ("Cliente piloto", "1", "em produção há 3 meses"), ("Faturas com falha", "0", "nenhuma pendente")])
        + '<div class="nv-grade-lado">'
        + card("Lojas e cobrança", tabela(["Loja", "Condição", "Próxima fatura"], linhas))
        + '<div class="nv-pilha">' + card("Regras automáticas", regras) + card("Provedores de pagamento", provedores) + "</div></div>"
    )
    return pagina("nv-master", corpo)


def tela_precos() -> str:
    mods = [
        ("Plano Inicial", "caixa, estoque, clientes e 1 caixa", "R$ 59,00/mês", True),
        ("Nota fiscal NFC-e", "", "a definir", False), ("WhatsApp com agente de IA", "", "a definir", False),
        ("Comandas, cozinha e delivery", "", "a definir", False), ("Cardápio digital e Minha página", "", "a definir", False),
        ("Fidelidade e campanhas", "", "a definir", False), ("Inteligência e assistente de IA", "", "a definir", False),
        ("Balança e etiquetas", "", "a definir", False), ("Grade e trocas", "", "a definir", False), ("Caixa extra", "", "a definir", False),
    ]
    linhas = [[f"<b>{n}</b>" + (f'<div class="small muted">{d}</div>' if d else ""), tag("ok" if fixo else "", "definido" if fixo else "rascunho"), f"<b>{p}</b>"] for n, d, p, fixo in mods]
    corpo = (
        '<p style="margin:0 0 12px"><a class="link-ouro" href="./master_cobranca.html">‹ Cobrança</a></p>'
        + topo("Tabela de preços", "Plano e módulos com histórico: a mudança vale para as próximas faturas e fica registrada.",
               btn("Salvar nova tabela", "btn-principal btn-alto", "Nova tabela salva com data de início. Faturas já emitidas não mudam."))
        + '<div class="nv-faixa aviso">Só o Plano Inicial (R$ 59) está definido. Os preços dos módulos serão fechados antes do lançamento.</div>'
        + card("Plano e módulos", tabela(["Item", "Situação", "Preço"], linhas, (2,)))
    )
    return pagina("nv-master", corpo)


# ----------------------------------------------------------------------------------------------
def tela_whatsapp() -> str:
    linhas = [
        [celula_loja("bom-gole", "Adega Bom Gole", "agente de IA ligado"), tag("info", "número de teste"), "simulado", tag("ok", "ok")],
        [celula_loja("pao-dourado", "Padaria Pão Dourado", "agente de IA ligado"), tag("info", "número de teste"), "simulado", tag("ok", "ok")],
        [celula_loja("atelie-lume", "Ateliê Lume", "agente de IA ligado"), tag("info", "número de teste"), "simulado", tag("ok", "ok")],
        [celula_loja("casa-forte", "Casa Forte Materiais", "agente de IA ligado"), tag("info", "número de teste"), "simulado", tag("ok", "ok")],
    ]
    corpo = (
        topo("WhatsApp das lojas", "Cada loja usa o WhatsApp oficial com o próprio número. Aqui a equipe acompanha conexões, custos da Meta e falhas.")
        + '<div class="nv-faixa aviso">Próximo passo: aprovação da Óptima como parceira de tecnologia da Meta (Tech Provider). Até lá, as lojas de demonstração usam o número de teste.</div>'
        + kpis([("Lojas com WhatsApp", "4", "demonstração, número de teste"), ("Em produção", "0", "após a aprovação da Meta"),
                ("Falhas de envio", "0", "nenhuma pendente"), ("Retenção de conversas", "30/90 dias", "e apagar dados a pedido (LGPD)")])
        + '<div class="nv-grade-lado">'
        + card("Conexões", tabela(["Loja", "Número", "Custo da Meta", "Situação"], linhas))
        + card("Controles por loja", '<ul class="nv-linhas">'
               '<li><div class="cresce"><b>Teto de marketing</b><span>limite de gasto com mensagens de marketing por mês</span></div></li>'
               '<li><div class="cresce"><b>Modelos aprovados pela Meta</b><span>confirmação, aniversário, cashback, cliente sumido</span></div></li>'
               '<li><div class="cresce"><b>Consentimento</b><span>só envia para quem aceitou; SAIR respeitado na hora</span></div></li></ul>')
        + "</div>"
    )
    return pagina("nv-master", corpo)


def tela_ia() -> str:
    corpo = (
        topo("IA das lojas", "O assistente e o agente de IA de todas as lojas passam por um gateway próprio: troca de provedor, teto de gasto e privacidade.")
        + kpis([("Provedores", "3", "Anthropic, OpenAI e Groq"), ("Lojas com IA", "4", "demonstração em modo simulado"),
                ("Gasto de IA no mês", "R$ 0,00", "demonstrações não consomem"), ("Dados pessoais enviados", "0", "filtro de privacidade antes da IA")])
        + '<div class="nv-grade-3">'
        + card("Rotas por tarefa", '<p style="margin:0">Cada tarefa (responder cliente, ler nota fiscal, analisar vendas) usa o modelo mais adequado e pode trocar de provedor sem mexer nas lojas.</p>')
        + card("Teto por loja", '<p style="margin:0">Orçamento mensal de IA por loja. Ao chegar no teto, a loja é avisada antes de qualquer cobrança extra.</p>')
        + card("Privacidade", '<p style="margin:0">CPF, telefone e outros dados pessoais são mascarados antes de qualquer envio para a IA.</p>')
        + "</div>"
    )
    return pagina("nv-master", corpo)


# ----------------------------------------------------------------------------------------------
def tela_chamados() -> str:
    corpo = (
        topo("Chamados", "Os pedidos de ajuda que as lojas abrem pela tela de Ajuda chegam aqui, com a loja, a tela e o aparelho.")
        + kpis([("Abertos", "0", "nenhum agora"), ("Tempo de resposta", "—", "meta: mesmo dia"),
                ("Resolvidos no mês", "—", "começa no lançamento"), ("Artigos de ajuda", "pronto", "a loja procura antes de abrir chamado")])
        + card("Fila de chamados",
               '<div class="nv-vazio" data-vazio="chamado-exemplo"><div class="ic">🎧</div><b>Nenhum chamado aberto</b>Quando uma loja pedir ajuda, o chamado aparece aqui.</div>'
               '<div id="chamado-exemplo" hidden><ul class="nv-linhas"><li>'
               f'<img class="nv-logo-loja" src="{LOGO}casa-forte.png" alt="">'
               '<div class="cresce"><b>“Como vendo fio por metro?”</b><span>Casa Forte Materiais · tela Vender · celular</span></div>'
               + tag("aviso", "exemplo simulado")
               + btn("Responder", "nv-btn-mini cheio", "A resposta chega no sininho da loja e o chamado fica no histórico.")
               + "</li></ul></div>",
               '<button type="button" class="nv-btn-mini" data-simular="chamado-exemplo" data-msg="Chamado de exemplo criado só nesta tela.">Simular um chamado</button>')
    )
    return pagina("nv-master", corpo)


def tela_operacoes() -> str:
    linhas = [
        ["<b>Cobrança diária</b><div class='small muted'>faturas, avisos e só leitura</div>", "todo dia", tag("ok", "sem falhas")],
        ["<b>Envio de avisos</b><div class='small muted'>vencimento e novidades</div>", "contínuo", tag("ok", "sem falhas")],
        ["<b>Envio de WhatsApp</b><div class='small muted'>fila com novas tentativas</div>", "contínuo", tag("ok", "sem falhas")],
        ["<b>Backup do banco</b>", "todo dia", tag("ok", "sem falhas")],
        ["<b>Limpeza LGPD</b><div class='small muted'>conversas antigas do WhatsApp</div>", "todo dia", tag("ok", "sem falhas")],
    ]
    corpo = (
        topo("Operações", "Tudo o que roda sozinho na plataforma. Se algo falhar, aparece aqui com o motivo e o botão de reprocessar.")
        + '<div class="nv-grade-lado">'
        + card("Rotinas automáticas", tabela(["Rotina", "Quando", "Situação"], linhas))
        + card("Operações com falha", '<div class="nv-vazio"><div class="ic">✅</div><b>Nenhuma falha</b>Reprocessamento com um clique quando houver.</div>')
        + "</div>"
    )
    return pagina("nv-master", corpo)


def tela_auditoria() -> str:
    linhas = [
        ["Hoje", "Tiago", "Ligou todos os módulos na <b>Adega Bom Gole</b>", tag("info", "módulos")],
        ["Hoje", "Tiago", "Aplicou a identidade da <b>Adega Bom Gole</b>", tag("info", "marca")],
        ["Ontem", "Lucas", "Conferiu as famílias 1 e 2 da verificação do sistema", tag("", "verificação")],
        ["Ontem", "Tiago", "Ligou a classificação do IBS/CBS na configuração fiscal", tag("info", "fiscal")],
        ["Esta semana", "Lucas", "Abriu as correções #734, #735 e #736 da verificação", tag("", "verificação")],
    ]
    corpo = (
        topo("Auditoria", "Tudo o que a equipe Óptima faz fica registrado: quem, quando e em qual loja.")
        + '<div class="nv-faixa">Registro do ambiente de demonstração.</div>'
        + card("Registro geral", tabela(["Quando", "Quem", "O que", "Tipo"], linhas))
    )
    return pagina("nv-master", corpo)


def tela_equipe() -> str:
    linhas = [
        ['<div class="nv-celula-loja"><span class="nv-loja-ini" style="background:#0D6EFD">T</span><div><b>Tiago</b><span class="small muted">fundador · desenvolvedor</span></div></div>', "Administrador do Master", tag("ok", "verificação em 2 etapas")],
        ['<div class="nv-celula-loja"><span class="nv-loja-ini" style="background:#F97316">L</span><div><b>Lucas</b><span class="small muted">fundador · desenvolvedor</span></div></div>', "Administrador do Master", tag("ok", "verificação em 2 etapas")],
    ]
    corpo = (
        topo("Equipe Óptima", "Quem acessa o Master. A verificação em duas etapas é obrigatória para todo mundo.",
             btn("+ Convidar pessoa", "btn-principal btn-alto", "Convite enviado. A pessoa só entra depois de configurar a verificação em duas etapas."))
        + card("Pessoas", tabela(["Pessoa", "Papel", "Segurança"], linhas))
    )
    return pagina("nv-master", corpo)


PAGINAS_MASTER = {
    "master.html": ("Master · Visão geral", tela_visao_geral()),
    "master_lojas.html": ("Master · Lojas", tela_lojas()),
    "master_loja.html": ("Master · Padaria Pão Dourado", tela_ficha_loja()),
    "master_nova_loja.html": ("Master · Nova loja", tela_nova_loja()),
    "master_pre_cadastros.html": ("Master · Pré-cadastros", tela_pre_cadastros()),
    "master_site.html": ("Master · Site de vendas", tela_site()),
    "master_novidades.html": ("Master · Novidades", tela_novidades()),
    "master_cobranca.html": ("Master · Cobrança", tela_cobranca()),
    "master_precos.html": ("Master · Tabela de preços", tela_precos()),
    "master_whatsapp.html": ("Master · WhatsApp das lojas", tela_whatsapp()),
    "master_ia.html": ("Master · IA das lojas", tela_ia()),
    "master_chamados.html": ("Master · Chamados", tela_chamados()),
    "master_operacoes.html": ("Master · Operações", tela_operacoes()),
    "master_auditoria.html": ("Master · Auditoria", tela_auditoria()),
    "master_equipe.html": ("Master · Equipe", tela_equipe()),
}
