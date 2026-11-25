"""Gera as telas NOVAS da demonstração (recursos trazidos do Óptima PDV) no MESMO padrão visual
das telas estáticas atuais, e atualiza o menu lateral de todas as telas.

Não depende do servidor nem do sistema original: usa uma tela já exportada
(`telas_estaticas/patrimonio.html`) como molde do layout (cabeçalho, menu, rodapé e scripts).

Uso:
    python gerar_telas_novas.py

É seguro rodar várias vezes: o menu é sempre reescrito e os arquivos de apoio
(`static/novos.css`, `static/novos.js`, `static/marca.js`) só são incluídos uma vez.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

DEMO_DIR = Path(__file__).resolve().parent
TELAS = DEMO_DIR / "telas_estaticas"
MOLDE = TELAS / "patrimonio.html"

sys.path.insert(0, str(DEMO_DIR))
from telas_novas_conteudo import PAGINAS  # noqa: E402
from telas_master_conteudo import PAGINAS_MASTER  # noqa: E402


# ----------------------------------------------------------------------------------------------
# Ícones (traço, 20px, mesmo estilo do menu atual)
# ----------------------------------------------------------------------------------------------
def ic(caminho: str) -> str:
    return (
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">' + caminho + "</svg>"
    )


ICONES = {
    "vender": '<circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 2h3l2.5 12.4a2 2 0 0 0 2 1.6h9.6a2 2 0 0 0 2-1.6L22 6H5.2"/>',
    "caixa": '<rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="2.5"/><path d="M6 12h.01M18 12h.01"/>',
    "pedidos": '<path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/><path d="M9 12h6M9 16h4"/>',
    "comandas": '<path d="M4 3h16v18l-3-2-3 2-2-2-2 2-3-2-3 2z"/><path d="M8 8h8M8 12h8"/>',
    "cozinha": '<path d="M6 13.9V20h12v-6.1"/><path d="M6 14a4 4 0 0 1-.9-7.9A5 5 0 0 1 12 3a5 5 0 0 1 6.9 3.1A4 4 0 0 1 18 14z"/><path d="M6 17h12"/>',
    "delivery": '<circle cx="5.5" cy="17.5" r="2.5"/><circle cx="18.5" cy="17.5" r="2.5"/><path d="M8 17.5h7.5M15 6h3l3 5v6.5h-.5M3 17.5V8h10v9.5"/>',
    "cardapio": '<rect x="6" y="2" width="12" height="20" rx="2"/><path d="M10 18h4M9 7h6M9 11h6"/>',
    "orcamentos": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M9 13h6M9 17h3"/>',
    "trocas": '<path d="M17 1l4 4-4 4"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><path d="M7 23l-4-4 4-4"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/>',
    "estoque": '<rect x="3" y="3" width="18" height="5" rx="1"/><path d="M4 8v11a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1V8"/><path d="M10 13h4"/>',
    "produtos": '<path d="M12 2 3 7v10l9 5 9-5V7z"/><path d="M3 7l9 5 9-5"/><path d="M12 12v10"/>',
    "entradas": '<path d="M12 3v10"/><path d="M8 9l4 4 4-4"/><path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2"/>',
    "inventario": '<path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>',
    "reposicao": '<path d="M21 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v3"/><path d="M3 8h18l-1.5 11a2 2 0 0 1-2 1.7H6.5a2 2 0 0 1-2-1.7L3 8z"/><path d="M9 12h6"/>',
    "clientes": '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    "fornecedores": '<path d="M1 4h13v10H1z"/><path d="M14 8h4l3 3v3h-7z"/><circle cx="5.5" cy="18" r="1.6"/><circle cx="17.5" cy="18" r="1.6"/>',
    "painel": '<rect x="3" y="3" width="7" height="9"/><rect x="14" y="3" width="7" height="5"/><rect x="14" y="12" width="7" height="9"/><rect x="3" y="16" width="7" height="5"/>',
    "inteligencia": '<path d="M9 18h6M10 22h4"/><path d="M12 2a7 7 0 0 0-4 12.7c.6.5 1 1.2 1 2V17h6v-.3c0-.8.4-1.5 1-2A7 7 0 0 0 12 2z"/>',
    "fluxo": '<path d="M3 17l6-6 4 4 8-8"/><path d="M14 7h7v7"/>',
    "contas": '<rect x="3" y="4" width="18" height="17" rx="2"/><path d="M3 9h18"/><path d="M8 2v4M16 2v4"/><path d="M8 14h4"/>',
    "relatorios": '<path d="M3 3v18h18"/><rect x="7" y="10" width="3" height="8"/><rect x="12" y="6" width="3" height="12"/><rect x="17" y="13" width="3" height="5"/>',
    "fiscal": '<path d="M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1-2 1z"/><path d="M8 8h8M8 12h8M8 16h5"/>',
    "patrimonio": '<rect x="3" y="7" width="18" height="14" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>',
    "whatsapp": '<path d="M21 11.5a8.4 8.4 0 0 1-12.3 7.5L3 21l1.9-5.6A8.4 8.4 0 1 1 21 11.5z"/><path d="M9 9.5c0 3 2.5 5.5 5.5 5.5l1-1.5-2-1-1 1c-1-.4-1.6-1-2-2l1-1-1-2z"/>',
    "agente": '<rect x="4" y="8" width="16" height="12" rx="3"/><path d="M12 4v4M9 13h.01M15 13h.01M9 17h6"/><circle cx="12" cy="3" r="1"/>',
    "relacionamento": '<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8l1 1L12 21l7.8-7.6 1-1a5.5 5.5 0 0 0 0-7.8z"/>',
    "fidelizacao": '<path d="M12 2l3 6.3 7 1-5 4.8 1.2 6.9L12 17.8 5.8 21l1.2-6.9-5-4.8 7-1z"/>',
    "assistente": '<path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"/><path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z"/>',
    "ajuda": '<circle cx="12" cy="12" r="9"/><path d="M9.6 9a2.4 2.4 0 1 1 3.4 2.2c-.8.4-1 .9-1 1.6"/><path d="M12 17h.01"/>',
    "config": '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82 2 2 0 1 1-2.83 2.83 1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51 2 2 0 0 1-4 0 1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33 2 2 0 1 1-2.83-2.83A1.65 1.65 0 0 0 4.6 15a1.65 1.65 0 0 0-1.51-1 2 2 0 0 1 0-4 1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82 2 2 0 1 1 2.83-2.83A1.65 1.65 0 0 0 9 4.6a1.65 1.65 0 0 0 1-1.51 2 2 0 0 1 4 0 1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33 2 2 0 1 1 2.83 2.83A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1 2 2 0 0 1 0 4 1.65 1.65 0 0 0-1.51 1z"/>',
    "identidade": '<circle cx="13.5" cy="6.5" r="1.5"/><circle cx="17.5" cy="10.5" r="1.5"/><circle cx="8.5" cy="7.5" r="1.5"/><circle cx="6.5" cy="12.5" r="1.5"/><path d="M12 2a10 10 0 0 0 0 20c1 0 1.7-.8 1.7-1.7 0-.4-.2-.8-.4-1.1-.3-.3-.4-.7-.4-1.1 0-.9.8-1.7 1.7-1.7h2A5.6 5.6 0 0 0 22 11 10 10 0 0 0 12 2z"/>',
    "pagina": '<circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
    "plano": '<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20"/><path d="M6 15h4"/>',
    "usuarios": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 21a6.5 6.5 0 0 1 13 0"/><path d="M16 5.6a3.5 3.5 0 0 1 0 4.8"/><path d="M18.5 21a6.5 6.5 0 0 0-3-5.4"/>',
    "loja": '<path d="M3 9l1.5-5h15L21 9"/><path d="M4 9v11h16V9"/><path d="M9 20v-6h6v6"/>',
    "sistema": '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    "suporte": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4"/><path d="m4.93 4.93 4.24 4.24M14.83 14.83l4.24 4.24M14.83 9.17l4.24-4.24M4.93 19.07l4.24-4.24"/>',
    "tour": '<circle cx="12" cy="12" r="9"/><path d="m15.5 8.5-2 5-5 2 2-5z"/>',
    "master": '<path d="M3 21h18"/><path d="M5 21V7l7-4 7 4v14"/><path d="M9 21v-6h6v6"/><path d="M9 10h.01M15 10h.01"/>',
}
CHEVRON = ('<svg class="chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
           'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>')


def link(arquivo, rotulo, icone, titulo=None, extra="", kbd="", novo=False, ativo_arquivos=""):
    titulo = titulo or rotulo
    attrs = f' data-ativo-arquivos="{ativo_arquivos}"' if ativo_arquivos else ""
    selo = '<span class="nv-novo" aria-label="novo">novo</span>' if novo else ""
    kbd_html = f'\n            <kbd class="side-kbd">{kbd}</kbd>' if kbd else ""
    return (
        f'<a href="./{arquivo}" title="{titulo}"{attrs}{extra}>\n'
        f"            {ic(ICONES[icone])}\n"
        f'            <span class="label">{rotulo}</span>{selo}{kbd_html}\n'
        f"          </a>"
    )


def grupo(id_, rotulo, icone, itens):
    corpo = "\n              ".join(itens)
    return (
        f'<details class="side-grupo" id="{id_}">\n'
        f'            <summary title="{rotulo}">\n'
        f"              {ic(ICONES[icone])}\n"
        f'              <span class="label">{rotulo}</span>\n'
        f"              {CHEVRON}\n"
        f"            </summary>\n"
        f'            <div class="side-subnav">\n              {corpo}\n            </div>\n'
        f"          </details>"
    )


def secao(nome):
    return f'<div class="side-secao">{nome}</div>'


def montar_nav() -> str:
    partes = [
        secao("Operação"),
        link("venda.html", "Vender", "vender", "Frente de caixa (F1)", kbd="F1", ativo_arquivos="venda_balcao"),
        link("caixa.html", "Abrir/fechar caixa", "caixa", "Abrir e fechar o caixa"),
        grupo("grupo-pedidos", "Pedidos", "pedidos", [
            link("comandas.html", "Comandas", "comandas", "Comandas e mesas", novo=True),
            link("cozinha.html", "Cozinha/Bar", "cozinha", "Tela da cozinha e do bar (KDS)", novo=True),
            link("delivery.html", "Delivery", "delivery", novo=True),
            link("cardapio.html", "Cardápio", "cardapio", "Cardápio digital", novo=True),
        ]),
        link("orcamentos.html", "Orçamentos", "orcamentos", novo=True),
        link("trocas.html", "Trocas", "trocas", "Trocas e devoluções", novo=True),

        secao("Cadastros"),
        grupo("grupo-estoque", "Estoque", "estoque", [
            link("produtos.html", "Produtos", "produtos"),
            link("entradas.html", "Entradas", "entradas"),
            link("inventarios.html", "Inventário", "inventario", ativo_arquivos="inventario"),
            link("reposicao.html", "Reposição", "reposicao"),
        ]),
        link("clientes.html", "Clientes", "clientes"),
        link("fornecedores.html", "Fornecedores", "fornecedores"),

        secao("Gestão"),
        link("painel.html", "Painel", "painel"),
        link("inteligencia.html", "Inteligência", "inteligencia", "Inteligência do negócio: horários, clima e sugestões", novo=True),
        link("fluxo_caixa.html", "Fluxo de caixa", "fluxo", novo=True),
        link("contas_pagar.html", "Contas", "contas", ativo_arquivos="contas"),
        link("relatorio.html", "Relatórios", "relatorios"),
        link("fiscal.html", "Nota fiscal", "fiscal", "Nota fiscal (NFC-e)", novo=True),
        link("patrimonio.html", "Patrimônio", "patrimonio"),

        secao("Relacionamento"),
        link("whatsapp.html", "WhatsApp", "whatsapp", "Conversas do WhatsApp com o agente de IA", novo=True),
        link("agente.html", "Agente de IA", "agente", "Agente de IA que atende no WhatsApp", novo=True),
        link("relacionamento.html", "Campanhas", "relacionamento", "Relacionamento com IA", novo=True),
        link("fidelizacao.html", "Fidelidade", "fidelizacao", "Fidelidade e cashback", novo=True),

        secao("Apoio"),
        link("assistente.html", "Assistente IA", "assistente", "Assistente de IA", ativo_arquivos="conversas_ia,memoria_ia,uso_ia"),
        link("ajuda.html", "Ajuda", "ajuda"),
        grupo("grupo-configuracoes", "Configurações", "config", [
            link("identidade.html", "Identidade", "identidade", "White Label: nome, logo e cores", novo=True),
            link("minha_pagina.html", "Minha página", "pagina", "Site da loja", novo=True),
            link("plano.html", "Plano e módulos", "plano", novo=True),
            link("usuarios.html", "Usuários", "usuarios"),
            link("configuracoes.html", "Loja", "loja", "Taxas das maquininhas e fechamento automático do caixa."),
            link("saude.html", "Sistema", "sistema", ativo_arquivos="logs"),
            link("suporte.html", "Suporte", "suporte"),
            '<button type="button" id="btn-tour" class="side-link" title="Tour guiado">\n'
            f"                {ic(ICONES['tour'])}\n"
            '                <span class="label">Tour guiado</span>\n'
            "              </button>",
        ]),
    ]
    return '<nav class="side-nav">\n          ' + "\n\n          ".join(partes) + "\n        </nav>"


ICONES["megafone"] = '<path d="M3 11v2a1 1 0 0 0 1 1h2l5 4V6L6 10H4a1 1 0 0 0-1 1z"/><path d="M15.5 8.5a5 5 0 0 1 0 7"/><path d="M18.5 5.5a9 9 0 0 1 0 13"/>'
ICONES["mais"] = '<circle cx="12" cy="12" r="9"/><path d="M12 8v8M8 12h8"/>'
ICONES["auditoria"] = '<path d="M12 2l8 4v6c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V6z"/><path d="M9 12l2 2 4-4"/>'


def montar_nav_master() -> str:
    partes = [
        secao("Plataforma"),
        link("master.html", "Visão geral", "painel"),
        secao("Lojas"),
        link("master_lojas.html", "Lojas", "loja", ativo_arquivos="master_loja"),
        link("master_nova_loja.html", "Nova loja", "mais"),
        link("master_pre_cadastros.html", "Pré-cadastros", "clientes", "Pedidos de teste do site"),
        secao("Comercial"),
        link("master_site.html", "Site de vendas", "pagina"),
        link("master_novidades.html", "Novidades", "megafone", "Novidades publicadas para as lojas"),
        link("master_cobranca.html", "Cobrança", "plano", ativo_arquivos="master_precos"),
        secao("Serviços das lojas"),
        link("master_whatsapp.html", "WhatsApp das lojas", "whatsapp"),
        link("master_ia.html", "IA das lojas", "assistente"),
        secao("Operação"),
        link("master_chamados.html", "Chamados", "suporte"),
        link("master_operacoes.html", "Operações", "sistema"),
        link("master_auditoria.html", "Auditoria", "auditoria"),
        link("master_equipe.html", "Equipe Óptima", "usuarios"),
        secao("Demonstração"),
        link("painel.html", "Abrir uma loja", "vender", "Sistema de uma loja (Adega Bom Gole)"),
    ]
    return '<nav class="side-nav">\n          ' + "\n\n          ".join(partes) + "\n        </nav>"


def converter_para_master(html: str, nav_master: str) -> str:
    """Troca o menu, a marca e o usuário do molde da loja pelos da equipe Óptima."""
    html = html.replace('<html lang="pt-br">', '<html lang="pt-br" data-sem-marca>', 1)
    html = NAV_RE.sub(lambda _m: nav_master, html, count=1)
    html = re.sub(r'<img class="side-mark"[^>]*>\s*<span class="side-name">[^<]*</span>',
                  '<span class="nv-simbolo-optima" aria-hidden="true">Ó</span>\n          '
                  '<span class="side-name">Óptima<span class="nv-selo-master">Master</span></span>', html, count=1)
    html = html.replace('title="Carlos Eduardo (Proprietário) · Super admin"', 'title="Tiago · Equipe Óptima"')
    html = html.replace('<span class="side-avatar" aria-hidden="true">C(</span>', '<span class="side-avatar" aria-hidden="true">T</span>')
    html = html.replace('<span class="side-usuario-nome">Carlos Eduardo (Proprietário)</span>', '<span class="side-usuario-nome">Tiago</span>')
    html = html.replace('<span class="side-usuario-papel">Super admin</span>', '<span class="side-usuario-papel">Equipe Óptima · admin</span>')
    html = html.replace('href="./minha_conta.html" class="side-usuario-item"', 'href="./master_equipe.html" class="side-usuario-item"')
    html = html.replace('<a href="./login.html" class="side-usuario-item side-sair"', '<a href="./master_entrar.html" class="side-usuario-item side-sair"')
    html = re.sub(r'\s*<a class="ajuda-contexto"[^>]*>\?</a>', "", html, count=1)
    return html


ENTRAR_MASTER = """<!doctype html>
<html lang="pt-br" data-sem-marca>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Óptima Master · Entrar</title>
<link rel="icon" href="./static/img/favicon.ico" sizes="any">
<link rel="stylesheet" href="./static/style.css">
<link rel="stylesheet" href="./static/novos.css">
<script>try{var _t=localStorage.getItem('tema');if(_t==='dark'||_t==='light')document.documentElement.setAttribute('data-theme',_t);}catch(e){}</script>
<style>
  body { margin: 0; min-height: 100vh; display: grid; place-items: center; background: var(--bg); padding: 16px; }
  .entrar { width: min(420px, 100%); background: var(--card); border: 1px solid var(--line); border-radius: 18px; padding: 32px; box-shadow: 0 20px 60px rgba(15,23,42,.12); }
  .entrar .topo-marca { display: flex; align-items: center; gap: 10px; font-weight: 800; font-size: 20px; margin-bottom: 22px; }
  .entrar h1 { font-size: 24px; margin: 0 0 6px; }
  .entrar p { color: var(--muted); margin: 0 0 20px; font-size: 15px; }
  .entrar .btn-principal { width: 100%; margin-top: 8px; }
</style>
</head>
<body>
  <main class="entrar">
    <div class="topo-marca"><span class="nv-simbolo-optima" style="width:38px;height:38px;border-radius:10px;display:grid;place-items:center;background:linear-gradient(135deg,#0D6EFD,#3B82F6);color:#fff">Ó</span>Óptima Master</div>
    <section id="passo-senha">
      <h1>Entrar no Master</h1>
      <p>Área da equipe Óptima. As lojas entram pelo endereço de cada uma.</p>
      <form class="nv-form" id="form-senha">
        <label>E-mail<input type="email" value="tiago@optimati.com.br" autocomplete="username"></label>
        <label>Senha<input type="password" value="demonstracao" autocomplete="current-password"></label>
        <button class="btn-principal btn-alto" type="submit">Continuar</button>
      </form>
    </section>
    <section id="passo-mfa" hidden>
      <h1>Verificação em duas etapas</h1>
      <p>Digite o código de 6 números do seu aplicativo autenticador. Na demonstração, qualquer código entra.</p>
      <form id="form-mfa">
        <div class="nv-mfa">
          <input inputmode="numeric" maxlength="1" aria-label="Dígito 1" value="4"><input inputmode="numeric" maxlength="1" aria-label="Dígito 2" value="8">
          <input inputmode="numeric" maxlength="1" aria-label="Dígito 3" value="1"><input inputmode="numeric" maxlength="1" aria-label="Dígito 4" value="0">
          <input inputmode="numeric" maxlength="1" aria-label="Dígito 5" value="9"><input inputmode="numeric" maxlength="1" aria-label="Dígito 6" value="2">
        </div>
        <button class="btn-principal btn-alto" type="submit" style="width:100%;margin-top:20px">Entrar</button>
      </form>
    </section>
  </main>
  <script>
    document.getElementById('form-senha').addEventListener('submit', function (e) {
      e.preventDefault();
      document.getElementById('passo-senha').hidden = true;
      document.getElementById('passo-mfa').hidden = false;
    });
    document.getElementById('form-mfa').addEventListener('submit', function (e) {
      e.preventDefault();
      location.href = './master.html';
    });
  </script>
</body>
</html>
"""


NAV_RE = re.compile(r'<nav class="side-nav">.*?</nav>', re.S)
ATIVOS = ('<link rel="stylesheet" href="./static/novos.css">\n'
          '    <script src="./static/marca.js"></script>')


def incluir_ativos(html: str) -> str:
    if "static/marca.js" in html:
        return html
    alvo = '<link rel="stylesheet" href="./static/style.css">'
    if alvo in html:
        return html.replace(alvo, alvo + "\n    " + ATIVOS, 1)
    return html.replace("</head>", "    " + ATIVOS + "\n</head>", 1)


def molde() -> tuple[str, str, str]:
    """Devolve (antes_do_titulo, depois_do_titulo_ate_o_conteudo, depois_do_conteudo)."""
    html = re.sub(r'(\.(?:css|js))\?v=[0-9a-f]+"', r'\1"', MOLDE.read_text(encoding="utf-8"))  # tira a versão; é reposta no fim
    i_tit = html.index("<title>")
    f_tit = html.index("</title>") + len("</title>")
    i_pag = html.index('<div class="page')
    i_main_fim = html.index("        </main>")
    marca_scripts = 'painel-lateral.js"></script>'
    f_scripts = html.index(marca_scripts) + len(marca_scripts)
    antes = html[:i_tit]
    meio = html[f_tit:i_pag]
    meio = re.sub(r'(<a class="ajuda-contexto" href=")[^"]*(")', r"\1./ajuda.html\2", meio)
    depois = html[i_main_fim:f_scripts] + '\n<script src="./static/novos.js"></script>\n</body>\n</html>\n'
    return antes, meio, depois


def main() -> None:
    nav = montar_nav()
    antes, meio, depois = molde()

    # 1) Telas novas
    for arquivo, (titulo, conteudo) in PAGINAS.items():
        html = antes + f"<title>{titulo}</title>" + meio + conteudo + "\n" + depois
        html = NAV_RE.sub(lambda _m: nav, html, count=1)
        html = incluir_ativos(html)
        (TELAS / arquivo).write_text(html, encoding="utf-8")
        print(f"  + {arquivo}")

    # 2) Área Master (equipe Óptima): menu, marca e usuário próprios, sem White Label
    nav_master = montar_nav_master()
    for arquivo, (titulo, conteudo) in PAGINAS_MASTER.items():
        html = antes + f"<title>{titulo}</title>" + meio + conteudo + "\n" + depois
        html = incluir_ativos(html)
        html = converter_para_master(html, nav_master)
        (TELAS / arquivo).write_text(html, encoding="utf-8")
        print(f"  + {arquivo} (Master)")
    (TELAS / "master_entrar.html").write_text(ENTRAR_MASTER, encoding="utf-8")

    # 3) Menu novo + marca em todas as telas existentes da loja
    alteradas = 0
    for pagina in sorted(TELAS.glob("*.html")):
        if pagina.name in PAGINAS or pagina.name.startswith("master"):
            continue
        html = pagina.read_text(encoding="utf-8")
        novo = NAV_RE.sub(lambda _m: nav, html, count=1)
        novo = incluir_ativos(novo)
        if novo != pagina.read_text(encoding="utf-8"):
            pagina.write_text(novo, encoding="utf-8")
            alteradas += 1
    print(f"Telas novas: {len(PAGINAS)} · telas existentes atualizadas: {alteradas}")

    # 4) Versão nos CSS/JS (?v=hash do conteúdo): o navegador nunca usa um estilo velho do cache
    versionar_ativos()


ATIVO_RE = re.compile(r'(\./static/([\w.-]+\.(?:css|js)))(?:\?v=[0-9a-f]+)?"')


def versionar_ativos() -> None:
    import hashlib
    hashes = {p.name: hashlib.md5(p.read_bytes()).hexdigest()[:8] for p in (TELAS / "static").glob("*.*") if p.suffix in (".css", ".js")}
    for pagina in TELAS.glob("*.html"):
        original = html = pagina.read_text(encoding="utf-8")
        if ("data-grafico" in html or "formas-lista" in html) and "static/graficos.js" not in html:
            html = html.replace("</body>", '<script src="./static/graficos.js"></script>\n</body>', 1)
        novo = ATIVO_RE.sub(lambda m: f'{m.group(1)}?v={hashes[m.group(2)]}"' if m.group(2) in hashes else m.group(0), html)
        if novo != original:
            pagina.write_text(novo, encoding="utf-8")


if __name__ == "__main__":
    main()
