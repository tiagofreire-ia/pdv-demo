"""Exporta todas as telas do sistema (já populadas com os 2 meses de dados do comércio
de bebidas e marca 'SUA MARCA') para HTMLs estáticos navegáveis em:
  `apresentacao_evento/telas_estaticas/`

Funciona 100% offline em QUALQUER computador (basta copiar a pasta `telas_estaticas`
num pendrive/WhatsApp e abrir no navegador, sem precisar instalar Python ou servidor),
incluindo:
  - Landing Page comercial (`landing.html`)
  - Tela de Login funcional na hora (`login.html` -> entra em `painel.html`)
  - Simulador interativo do Assistente de IA (`assistente.html` com perguntas prontas e cartões de confirmação)
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

DEMO_DIR = Path(__file__).resolve().parent
RAIZ = DEMO_DIR.parent
SAIDA_DIR = DEMO_DIR / "telas_estaticas"

sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(DEMO_DIR))

from fastapi.testclient import TestClient  # noqa: E402

import rodar_demo  # noqa: E402
from app.database import SessionLocal  # noqa: E402
from app.models import Usuario  # noqa: E402
from ia_demo_respostas import responder_demo  # noqa: E402


# Mapa de rotas do sistema -> arquivo HTML estático
MAPA_ROTAS = {
    "/admin": "painel.html",
    "/admin?periodo=7d": "painel_7d.html",
    "/admin?periodo=mes": "painel_mes.html",
    "/venda": "venda.html",
    "/venda/balcao": "venda_balcao.html",
    "/caixa": "caixa.html",
    "/caixa/historico": "caixa_historico.html",
    "/caixa/historico?periodo=7d": "caixa_historico_7d.html",
    "/caixa/historico?periodo=30d": "caixa_historico.html",
    "/caixa/historico?periodo=mes": "caixa_historico_mes.html",
    "/caixa/historico?periodo=30d&situacao=diferenca": "caixa_historico_diferenca.html",
    "/caixa/historico?periodo=30d&situacao=nao_contado": "caixa_historico_nao_contado.html",
    "/produtos": "produtos.html",
    "/produtos?filtro=baixo": "produtos_baixo.html",
    "/produtos?filtro=validade": "produtos_validade.html",
    "/entradas": "entradas.html",
    "/entradas?todas=1": "entradas_todas.html",
    "/inventarios": "inventarios.html",
    "/inventarios/1": "inventario_1.html",
    "/inventarios/2": "inventario_2.html",
    "/inventarios/3": "inventario_3.html",
    "/inventarios/4": "inventario_4.html",
    "/inventarios/5": "inventario_5.html",
    "/inventarios/5?nao_contados=1": "inventario_5_faltam.html",
    "/admin/reposicao": "reposicao.html",
    "/clientes": "clientes.html",
    "/clientes?filtro=devendo": "clientes_devendo.html",
    "/clientes?filtro=inativos": "clientes_inativos.html",
    "/fornecedores": "fornecedores.html",
    "/contas-pagar": "contas_pagar.html",
    "/contas-pagar?ver=pagas": "contas_pagas.html",
    "/contas-pagar?ver=todas": "contas_todas.html",
    "/relatorio": "relatorio.html",
    "/relatorio?periodo=hoje": "relatorio_hoje.html",
    "/relatorio?periodo=7d": "relatorio_7d.html",
    "/relatorio?periodo=mes": "relatorio.html",
    "/relatorio?periodo=mes_passado": "relatorio_mes_passado.html",
    "/patrimonio": "patrimonio.html",
    "/admin/assistente": "assistente.html",
    "/admin/assistente?conversa=1": "assistente_conversa_1.html",
    "/admin/assistente?conversa=2": "assistente_conversa_2.html",
    "/admin/assistente?conversa=3": "assistente_conversa_3.html",
    "/admin/assistente?conversa=4": "assistente_conversa_4.html",
    "/admin/assistente?conversa=5": "assistente_conversa_5.html",
    "/ajuda": "ajuda.html",
    "/ajuda/assistente": "ajuda_assistente.html",
    "/ajuda/venda": "ajuda_venda.html",
    "/ajuda/caixa": "ajuda_caixa.html",
    "/ajuda/reposicao": "ajuda_reposicao.html",
    "/ajuda/fiado": "ajuda_fiado.html",
    "/ajuda/perguntas": "ajuda_perguntas.html",
    "/ajuda/atalhos": "ajuda_atalhos.html",
    "/usuarios": "usuarios.html",
    "/admin/configuracoes": "configuracoes.html",
    "/saude": "saude.html",
    "/admin/saude": "saude.html",
    "/logs": "logs.html",
    "/admin/uso-ia": "uso_ia.html",
    "/admin/conversas-ia": "conversas_ia.html",
    "/admin/conversas-ia/1": "conversas_ia_1.html",
    "/admin/conversas-ia/2": "conversas_ia_2.html",
    "/admin/conversas-ia/3": "conversas_ia_3.html",
    "/admin/conversas-ia/4": "conversas_ia_4.html",
    "/admin/conversas-ia/5": "conversas_ia_5.html",
    "/admin/memoria-ia": "memoria_ia.html",
    "/suporte": "suporte.html",
    "/minha-conta": "minha_conta.html",
    "/login": "login.html",
    "/esqueci-senha": "esqueci_senha.html",
}


def _gerar_dicionario_respostas_js() -> dict:
    """Pré-calcula as respostas e propostas reais do banco de 2 meses para embutir no JS estático."""
    with SessionLocal() as db:
        dono = db.query(Usuario).filter(Usuario.super_admin == True).first()  # noqa: E712
        perguntas_chave = [
            ("semana", "Qual foi o meu faturamento essa semana?"),
            ("mes", "Qual o faturamento e o lucro deste mês?"),
            ("estoque_baixo", "Qual produto está em estoque baixo?"),
            ("mais_vendidos", "Quais foram os produtos mais vendidos nos últimos 60 dias?"),
            ("parados", "Quais produtos estão parados prendendo dinheiro?"),
            ("confianca", "Quem está devendo na Confiança?"),
            ("contas", "Quais contas a pagar vencem nos próximos dias?"),
            ("caixa_hoje", "Como está o caixa hoje?"),
            ("acao_entrada", "Repor estoque: entrada de 15 fardos de Brahma Duplo Malte a R$ 37,90 e 30 pacotes de Gelo 5kg a R$ 6,50 da Ambev"),
            ("acao_heineken", "Reajustar em +5% o preço das cervejas Heineken com arredondamento para R$ 0,50"),
            ("acao_promocao", "Criar promoção: baixar em 10% o preço do Licor 43 e da Tequila José Cuervo que estão parados"),
            ("acao_conta", "Lançar conta de energia elétrica de R$ 1.480,00 com vencimento para daqui a 5 dias"),
            ("acao_fiado", "Registrar pagamento de R$ 350,00 no Pix da Confiança do Espetinho do Alemão"),
        ]
        banco_respostas = {}
        for chave, texto_p in perguntas_chave:
            resp, _, prop = responder_demo(texto_p, {}, db, dono, sem_pausa=True)
            prop_limpa = None
            if prop:
                prop_limpa = {
                    "id": prop.get("proposta_id", "demo-prop"),
                    "titulo": prop.get("titulo", ""),
                    "descricao": prop.get("descricao", ""),
                    "resumo": prop.get("resumo", {}),
                }
            banco_respostas[chave] = {
                "pergunta": texto_p,
                "resposta": resp,
                "proposta": prop_limpa,
            }
        db.rollback()
    return banco_respostas


def _reescrever_links_html(html: str) -> str:
    """Converte caminhos absolutos (/static/..., /admin, etc.) para caminhos relativos locais."""
    # 1. Static files
    html = re.sub(r'(["\'])/static/([^"\'?]+)(\?[^"\']*)?\1', r'\1./static/\2\1', html)
    html = html.replace("./static/img/logo-96.png", "./static/img/logo-marca.svg")
    html = html.replace("./static/img/logo.png", "./static/img/logo-marca.svg")
    html = html.replace("./static/img/apple-touch-icon.png", "./static/img/logo-marca.svg")
    html = html.replace('href="/manifest.webmanifest"', 'href="#"')

    # 2. Conversas IA links com query string vazia (ex.: /admin/conversas-ia/1?usuario=&q=)
    html = re.sub(
        r'href="/admin/conversas-ia/(\d+)(\?[^"]*)?"',
        r'href="./conversas_ia_\1.html"',
        html,
    )
    html = html.replace('href="/admin/conversas-ia?usuario=&amp;q="', 'href="./conversas_ia.html"')

    # 3. Logout leva para a tela de Login (e forms de /logout também)
    html = html.replace('href="/logout"', 'href="./login.html"')
    html = html.replace('action="/logout"', 'action="./login.html" method="get"')

    # 4. Substitui rotas exatas nos hrefs (incluindo versões com &amp;)
    rotas_ordenadas = sorted(MAPA_ROTAS.items(), key=lambda kv: len(kv[0]), reverse=True)
    for rota, arquivo in rotas_ordenadas:
        rota_amp = rota.replace("&", "&amp;")
        html = html.replace(f'href="{rota}"', f'href="./{arquivo}"')
        html = html.replace(f'href="{rota_amp}"', f'href="./{arquivo}"')
        html = html.replace(f"href='{rota}'", f"href='./{arquivo}'")

    # 5. Links secundários de edição/detalhe em modo estático apontam para a tela correspondente
    html = re.sub(r'href="/produtos/\d+/editar"', 'href="./produtos.html"', html)
    html = re.sub(r'href="/clientes/\d+/(editar|extrato|dados)[^"]*"', 'href="./clientes.html"', html)
    html = re.sub(r'href="/fornecedores/\d+/editar"', 'href="./fornecedores.html"', html)
    html = re.sub(r'href="/contas-pagar/\d+/editar"', 'href="./contas_pagar.html"', html)
    html = re.sub(r'href="/patrimonio/\d+/editar"', 'href="./patrimonio.html"', html)
    html = re.sub(r'href="/usuarios/\d+/editar[^"]*"', 'href="./usuarios.html"', html)
    html = re.sub(r'href="/ajuda/[^"]+"', 'href="./ajuda_assistente.html"', html)

    # 6. Botão "+ Nova conversa" na tela de assistente estática leva para assistente.html
    html = html.replace('action="/admin/assistente/nova-conversa"', 'action="./assistente.html" method="get"')

    # 7. Desativa o tour automático ao abrir via file:// e intercepta forms de logout
    script_topo = """<script>
      try{localStorage.setItem('tourVisto_v1','1');}catch(e){}
      document.addEventListener('submit', function(e){
        var f = e.target;
        if (f && f.action && String(f.action).indexOf('login.html') !== -1 && !f.classList.contains('login-card')) {
          e.preventDefault();
          window.location.href = './login.html';
        }
      }, true);
    </script>"""
    html = html.replace("<head>", "<head>\n    " + script_topo, 1)
    return html


def _ligar_simulador_pdv(html: str) -> str:
    """Frente de caixa e Vitrine do Balcão sem servidor: carrega o simulador local
    (`demo_static/demo-pdv.js`) antes do pdv.js/balcao.js e faz o botão "Tela do cliente"
    abrir a vitrine estática."""
    for alvo in ('<script src="./static/pdv.js"></script>', '<script src="./static/balcao.js"></script>'):
        html = html.replace(alvo, '<script src="./static/demo-pdv.js"></script>\n' + alvo)
    return html.replace('window.open("/venda/balcao"', 'window.open("./venda_balcao.html"')


def _customizar_tela_login(html: str) -> str:
    """Deixa a tela de login pronta para funcionar ao vivo em qualquer PC sem servidor."""
    # Pré-preenche o e-mail e senha de demonstração (mas permite digitar por cima!)
    html = html.replace(
        '<input type="email" name="email" required autofocus>',
        '<input type="email" name="email" value="dono@suamarca.com.br" required autofocus>',
    )
    html = html.replace(
        '<input type="password" name="senha" required>',
        '<input type="password" name="senha" value="demo123" required>',
    )
    bloco_dica = """
    <div style="margin-top: 16px; padding: 12px 14px; border-radius: 12px; background: rgba(13, 110, 253, 0.12); border: 1px solid rgba(13, 110, 253, 0.35); font-size: 13px; line-height: 1.5; text-align: left;">
      <strong style="color: #60A5FA;">✦ Modo Demonstração Comercial:</strong><br>
      E-mail: <code style="color: #93C5FD; background: rgba(0,0,0,0.3); padding: 2px 6px; border-radius: 4px;">dono@suamarca.com.br</code> · Senha: <code style="color: #93C5FD; background: rgba(0,0,0,0.3); padding: 2px 6px; border-radius: 4px;">demo123</code><br>
      <span style="color: #94A3B8; font-size: 12px; margin-top: 4px; display: inline-block;">Basta clicar em <strong>Entrar</strong> (já está preenchido para você).</span>
    </div>
    <p class="muted small" style="margin-top: 12px;"><a href="./landing.html" class="link-login">← Voltar para a Apresentação Comercial</a></p>
  </form>"""
    html = html.replace("</form>", bloco_dica)

    script_login = """
<script>
  document.addEventListener("DOMContentLoaded", function () {
    var form = document.querySelector(".login-card");
    if (!form) return;
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var btn = form.querySelector('button[type="submit"]');
      if (btn) {
        btn.disabled = true;
        btn.textContent = "Entrando…";
      }
      setTimeout(function () {
        window.location.href = "./painel.html";
      }, 300);
    });
  });
</script>
</body>"""
    html = html.replace("</body>", script_login)
    return html


def _gerar_landing_page() -> str:
    """Cria uma Landing Page comercial elegante no padrão visual da marca (Ouro + Carvão)."""
    return """<!doctype html>
<html lang="pt-br">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SUA MARCA · Sistema PDV e Gestão com Inteligência Artificial</title>
  <link rel="icon" href="./static/img/logo-marca.svg">
  <link rel="stylesheet" href="./static/style.css">
  <style>
    :root {
      --lp-bg: #12100C;
      --lp-card: #1C1812;
      --lp-border: rgba(227, 207, 148, 0.18);
      --lp-gold: #C9A13B;
      --lp-gold-light: #E3CF94;
      --lp-text: #F7F4EC;
      --lp-muted: #B6AEA0;
    }
    body.lp-body {
      margin: 0;
      background: radial-gradient(circle at 80% 0%, rgba(201, 161, 59, 0.16), transparent 45%), var(--lp-bg);
      color: var(--lp-text);
      font-family: Manrope, system-ui, -apple-system, sans-serif;
      min-height: 100vh;
    }
    .lp-nav {
      max-width: 1200px;
      margin: 0 auto;
      padding: 24px 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }
    .lp-brand {
      display: flex;
      align-items: center;
      gap: 14px;
      text-decoration: none;
      color: var(--lp-text);
    }
    .lp-brand img {
      width: 46px;
      height: 46px;
      border-radius: 12px;
    }
    .lp-brand-title {
      font-weight: 800;
      font-size: 18px;
      letter-spacing: 0.5px;
      display: block;
    }
    .lp-brand-sub {
      font-size: 12px;
      color: var(--lp-gold-light);
      opacity: 0.85;
    }
    .lp-nav-actions {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }
    .lp-btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 12px 22px;
      border-radius: 12px;
      font-weight: 700;
      font-size: 14px;
      text-decoration: none;
      transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .lp-btn:hover {
      transform: translateY(-1px);
    }
    .lp-btn-gold {
      background: linear-gradient(135deg, #E3CF94 0%, #C9A13B 100%);
      color: #16130E;
      box-shadow: 0 8px 24px rgba(201, 161, 59, 0.28);
    }
    .lp-btn-outline {
      border: 1px solid var(--lp-border);
      background: rgba(255, 255, 255, 0.04);
      color: var(--lp-text);
    }
    .lp-hero {
      max-width: 1200px;
      margin: 20px auto 0;
      padding: 40px 28px 56px;
      display: grid;
      grid-template-columns: 1.15fr 0.85fr;
      gap: 40px;
      align-items: center;
    }
    .lp-badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 14px;
      border-radius: 999px;
      background: rgba(201, 161, 59, 0.14);
      border: 1px solid rgba(201, 161, 59, 0.35);
      color: var(--lp-gold-light);
      font-size: 12.5px;
      font-weight: 700;
      margin-bottom: 18px;
    }
    .lp-hero h1 {
      font-size: clamp(32px, 4.2vw, 50px);
      line-height: 1.12;
      margin: 0 0 18px;
      font-weight: 800;
      letter-spacing: -0.02em;
    }
    .lp-hero h1 span {
      color: var(--lp-gold-light);
    }
    .lp-hero p {
      font-size: 17px;
      line-height: 1.6;
      color: var(--lp-muted);
      margin: 0 0 28px;
      max-width: 580px;
    }
    .lp-cta-row {
      display: flex;
      gap: 14px;
      flex-wrap: wrap;
      margin-bottom: 28px;
    }
    .lp-stats {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 14px;
      padding-top: 20px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
    }
    .lp-stat strong {
      display: block;
      font-size: 22px;
      color: var(--lp-gold-light);
    }
    .lp-stat span {
      font-size: 12.5px;
      color: var(--lp-muted);
    }
    .lp-showcase {
      background: var(--lp-card);
      border: 1px solid var(--lp-border);
      border-radius: 20px;
      padding: 24px;
      box-shadow: 0 24px 60px rgba(0, 0, 0, 0.45);
    }
    .lp-showcase-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;
      padding-bottom: 12px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.07);
    }
    .lp-chat-demo {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .lp-msg-user {
      align-self: flex-end;
      background: #2B251B;
      color: #F7F4EC;
      padding: 11px 15px;
      border-radius: 14px 14px 4px 14px;
      font-size: 13.5px;
      max-width: 85%;
    }
    .lp-msg-ai {
      align-self: flex-start;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--lp-border);
      padding: 14px 16px;
      border-radius: 14px 14px 14px 4px;
      font-size: 13px;
      line-height: 1.5;
      width: 100%;
      box-sizing: border-box;
    }
    .lp-card-approve {
      margin-top: 10px;
      padding: 12px;
      border-radius: 10px;
      background: rgba(201, 161, 59, 0.1);
      border: 1px solid rgba(201, 161, 59, 0.35);
    }
    .lp-card-approve-badge {
      display: inline-block;
      margin-top: 8px;
      padding: 4px 10px;
      border-radius: 6px;
      background: rgba(46, 160, 67, 0.2);
      color: #7EE787;
      font-weight: 700;
      font-size: 12px;
    }
    .lp-grid {
      max-width: 1200px;
      margin: 0 auto;
      padding: 12px 28px 64px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 20px;
    }
    .lp-feature {
      background: var(--lp-card);
      border: 1px solid rgba(255, 255, 255, 0.07);
      border-radius: 16px;
      padding: 22px;
      text-decoration: none;
      color: inherit;
      transition: border-color 0.15s ease, transform 0.15s ease;
    }
    .lp-feature:hover {
      border-color: var(--lp-gold);
      transform: translateY(-2px);
    }
    .lp-feature h3 {
      margin: 0 0 8px;
      font-size: 17px;
      color: var(--lp-gold-light);
    }
    .lp-feature p {
      margin: 0;
      font-size: 13.5px;
      line-height: 1.55;
      color: var(--lp-muted);
    }
    @media (max-width: 860px) {
      .lp-hero { grid-template-columns: 1fr; padding-top: 16px; }
    }
  </style>
</head>
<body class="lp-body">
  <header class="lp-nav">
    <a href="./landing.html" class="lp-brand">
      <img src="./static/img/logo-marca.svg" alt="SUA MARCA">
      <div>
        <span class="lp-brand-title">SUA MARCA AQUI</span>
        <span class="lp-brand-sub">Sistema Personalizado · PDV & Gestão com IA</span>
      </div>
    </a>
    <div class="lp-nav-actions">
      <a href="./login.html" class="lp-btn lp-btn-outline">Tela de Login</a>
      <a href="./painel.html" class="lp-btn lp-btn-gold">Entrar no Sistema →</a>
    </div>
  </header>

  <section class="lp-hero">
    <div>
      <span class="lp-badge">✦ Demonstração Ao Vivo · 2 Meses de Comércio de Bebidas</span>
      <h1>O sistema com a <span>sua marca</span> e uma IA que trabalha pelo dono.</h1>
      <p>
        Frente de caixa ultrarrápida, controle de estoque por lote, reposição inteligente,
        caderneta de clientes e a <strong>Óptima IA</strong> — que lê notas fiscais, responde sobre seu lucro
        e prepara lançamentos que só entram no sistema após o seu <strong>"Confirmar"</strong>.
      </p>
      <div class="lp-cta-row">
        <a href="./login.html" class="lp-btn lp-btn-gold">Fazer Login na Demonstração</a>
        <a href="./assistente.html" class="lp-btn lp-btn-outline">Testar Assistente de IA Agora</a>
        <a href="./painel.html" class="lp-btn lp-btn-outline">Ir Direto ao Painel</a>
      </div>
      <div class="lp-stats">
        <div class="lp-stat">
          <strong>60 dias</strong>
          <span>de vendas reais simuladas</span>
        </div>
        <div class="lp-stat">
          <strong>100% Seguro</strong>
          <span>IA nunca altera dados sem seu aceite</span>
        </div>
        <div class="lp-stat">
          <strong>White-Label</strong>
          <span>Personalizado com a sua marca</span>
        </div>
      </div>
    </div>

    <div class="lp-showcase">
      <div class="lp-showcase-top">
        <strong style="font-size: 14px; color: var(--lp-gold-light);">Assistente Óptima IA · Exemplo Real</strong>
        <span style="font-size: 12px; color: var(--lp-muted);">Dupla confirmação do proprietário</span>
      </div>
      <div class="lp-chat-demo">
        <div class="lp-msg-user">
          "Chegaram 15 fardos de Brahma Duplo Malte a R$ 37,90 e 30 pacotes de Gelo 5kg a R$ 6,50 da Ambev"
        </div>
        <div class="lp-msg-ai">
          <strong>Proposta preparada: Entrada de mercadoria — NF #51904</strong><br>
          Fornecedor: Ambev S.A. — CD Direto · Total: <strong>R$ 763,50</strong>
          <div class="lp-card-approve">
            • Fardo Brahma Duplo Malte c/12: 15 un × R$ 37,90 = R$ 568,50<br>
            • Gelo Cubo Cristal 5kg: 30 un × R$ 6,50 = R$ 195,00<br>
            <span class="lp-card-approve-badge">✓ Confirmado pelo proprietário · Estoque atualizado</span>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="lp-grid">
    <a href="./painel.html" class="lp-feature">
      <h3>1. Painel & Lucro Real →</h3>
      <p>Faturamento do dia, 7 dias e mês, já descontando o custo de cada bebida vendida e as taxas de cada maquininha.</p>
    </a>
    <a href="./assistente.html" class="lp-feature">
      <h3>2. Assistente de IA ao Vivo →</h3>
      <p>Pergunte o faturamento da semana, do mês ou produtos em estoque baixo, e aprove ações com 1 clique.</p>
    </a>
    <a href="./conversas_ia.html" class="lp-feature">
      <h3>3. Auditoria de Conversas da IA →</h3>
      <p>Veja o histórico de diálogos da equipe e todas as ações executadas pela IA mediante aceite do proprietário.</p>
    </a>
    <a href="./reposicao.html" class="lp-feature">
      <h3>4. Reposição & Produtos Parados →</h3>
      <p>Descubra o que vai acabar antes do fim de semana e quais bebidas estão empatando dinheiro na prateleira.</p>
    </a>
  </section>
</body>
</html>
"""


def _script_simulador_ia_estatico(respostas_json: str) -> str:
    return f"""
<script>
// Simulador Offline do Assistente de IA para as Telas Estáticas (funciona sem servidor!)
(function () {{
  var BANCO_IA = {respostas_json};

  function normalizarTexto(s) {{
    return (s || "").toLowerCase().normalize("NFD").replace(/[\\u0300-\\u036f]/g, "");
  }}

  function escolherResposta(pergunta) {{
    var q = normalizarTexto(pergunta);
    if (q.indexOf("entrada") !== -1 || q.indexOf("repor estoque") !== -1 || q.indexOf("brahma") !== -1) return BANCO_IA.acao_entrada;
    if ((q.indexOf("licor") !== -1 || q.indexOf("tequila") !== -1) && (q.indexOf("baixar") !== -1 || q.indexOf("promocao") !== -1 || q.indexOf("10%") !== -1)) return BANCO_IA.acao_promocao;
    if (q.indexOf("reajustar") !== -1 && q.indexOf("heineken") !== -1) return BANCO_IA.acao_heineken;
    if (q.indexOf("lancar conta") !== -1 || q.indexOf("energia") !== -1) return BANCO_IA.acao_conta;
    if (q.indexOf("registrar pagamento") !== -1 || q.indexOf("alemao") !== -1) return BANCO_IA.acao_fiado;

    if (q.indexOf("semana") !== -1 || q.indexOf("7 dias") !== -1) return BANCO_IA.semana;
    if (q.indexOf("mes") !== -1 || q.indexOf("lucro") !== -1 || q === "faturamento" || q.indexOf("faturamento do mes") !== -1) return BANCO_IA.mes;
    if (q.indexOf("estoque baixo") !== -1 || q.indexOf("baixo") !== -1 || q.indexOf("acabando") !== -1 || q.indexOf("repor") !== -1 || q.indexOf("comprar") !== -1) return BANCO_IA.estoque_baixo;
    if (q.indexOf("mais vendido") !== -1 || q.indexOf("60 dias") !== -1 || q.indexOf("campeao") !== -1) return BANCO_IA.mais_vendidos;
    if (q.indexOf("parado") !== -1 || q.indexOf("dinheiro") !== -1 || q.indexOf("encalhado") !== -1) return BANCO_IA.parados;
    if (q.indexOf("devendo") !== -1 || q.indexOf("confianca") !== -1 || q.indexOf("fiado") !== -1 || q.indexOf("caderneta") !== -1) return BANCO_IA.confianca;
    if (q.indexOf("conta") !== -1 || q.indexOf("boleto") !== -1 || q.indexOf("vencem") !== -1) return BANCO_IA.contas;
    if (q.indexOf("caixa") !== -1 || q.indexOf("hoje") !== -1 || q.indexOf("gaveta") !== -1) return BANCO_IA.caixa_hoje;
    return BANCO_IA.semana;
  }}

  // Intercepta fetch para /admin/assistente/perguntar-async e confirmação de propostas no modo estático
  var fetchOriginal = window.fetch;
  window.fetch = function (url, opts) {{
    var u = String(url || "");
    if (u.indexOf("/admin/assistente/perguntar-async") !== -1) {{
      var pergunta = "";
      if (opts && opts.body && typeof opts.body.get === "function") {{
        pergunta = opts.body.get("pergunta") || "";
      }}
      var item = escolherResposta(pergunta);
      return new Promise(function (resolve) {{
        setTimeout(function () {{
          var payload = {{
            pergunta: pergunta || item.pergunta,
            resposta: item.resposta,
            proposta: item.proposta,
            ids: {{ pergunta: Date.now(), resposta: Date.now() + 1 }},
            conversa: {{ id: 99, titulo: (pergunta || item.pergunta).slice(0, 50) }},
            perguntas_hoje: 3,
            limite_dia: 50
          }};
          resolve({{
            ok: true,
            status: 200,
            json: function () {{ return Promise.resolve(payload); }}
          }});
        }}, 1100);
      }});
    }}
    if (u.indexOf("/admin/assistente/propostas/") !== -1 && u.indexOf("/confirmar") !== -1) {{
      return new Promise(function (resolve) {{
        setTimeout(function () {{
          resolve({{
            ok: true,
            status: 200,
            json: function () {{
              return Promise.resolve({{
                ok: true,
                mensagem: "✓ Ação confirmada pelo proprietário e gravada com sucesso no sistema!"
              }});
            }}
          }});
        }}, 450);
      }});
    }}
    if (u.indexOf("/admin/assistente/propostas/") !== -1 && u.indexOf("/cancelar") !== -1) {{
      return Promise.resolve({{
        ok: true,
        status: 200,
        json: function () {{ return Promise.resolve({{ ok: true, mensagem: "Proposta cancelada pelo proprietário." }}); }}
      }});
    }}
    if (u.indexOf("/admin/assistente/feedback") !== -1 || u.indexOf("/admin/assistente/mensagens/excluir") !== -1) {{
      return Promise.resolve({{
        ok: true,
        status: 200,
        json: function () {{ return Promise.resolve({{ ok: true, apagadas: 2 }}); }}
      }});
    }}
    return fetchOriginal ? fetchOriginal.apply(this, arguments) : Promise.reject();
  }};

  // No modo estático, "+ Nova conversa" e "Excluir conversa" recarregam assistente.html
  document.addEventListener("submit", function (e) {{
    var f = e.target;
    if (!f || !f.action) return;
    var act = String(f.action);
    if (act.indexOf("nova-conversa") !== -1 || act.indexOf("/limpar") !== -1 || act.indexOf("assistente.html") !== -1) {{
      e.preventDefault();
      window.location.href = "./assistente.html";
    }}
  }}, true);
}})();
</script>
"""


def main() -> None:
    if SAIDA_DIR.exists():
        shutil.rmtree(SAIDA_DIR)
    SAIDA_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Copia os arquivos estáticos (CSS, JS, fontes, ícones)
    static_destino = SAIDA_DIR / "static"
    shutil.copytree(RAIZ / "app" / "static", static_destino)
    (static_destino / "img" / "logo-marca.svg").write_text(rodar_demo.LOGO_SVG_MARCA, encoding="utf-8")
    shutil.copy2(DEMO_DIR / "demo_static" / "demo-pdv.js", static_destino / "demo-pdv.js")

    # 2. Pré-calcula as respostas e propostas da IA do banco de 2 meses
    banco_ia = _gerar_dicionario_respostas_js()
    script_ia = _script_simulador_ia_estatico(json.dumps(banco_ia, ensure_ascii=False))

    # 3. Renderiza primeiro /login e /esqueci-senha deslogado, depois loga como Proprietário
    client = TestClient(rodar_demo.app)

    gerados = set()
    for rota_pub in ("/login", "/esqueci-senha"):
        arq_pub = MAPA_ROTAS[rota_pub]
        resp_pub = client.get(rota_pub)
        html_pub = _reescrever_links_html(resp_pub.text)
        if arq_pub == "login.html":
            html_pub = _customizar_tela_login(html_pub)
        (SAIDA_DIR / arq_pub).write_text(html_pub, encoding="utf-8")
        gerados.add(arq_pub)

    # Agora autentica como Proprietário para exportar todas as telas internas
    client.get("/demo-entrar", follow_redirects=True)

    rotas_ordenadas = [
        r for r in MAPA_ROTAS.keys()
        if r not in ("/login", "/esqueci-senha") and not r.startswith("/admin/assistente?conversa=")
    ] + [
        r for r in MAPA_ROTAS.keys() if r.startswith("/admin/assistente?conversa=")
    ]

    for rota in rotas_ordenadas:
        arquivo = MAPA_ROTAS[rota]
        if rota == "/admin/assistente":
            client.post("/admin/assistente/nova-conversa", follow_redirects=False)
        resp = client.get(rota, follow_redirects=True)
        if resp.status_code != 200:
            print(f"[AVISO] Rota {rota} retornou {resp.status_code}")
            continue
        html = _reescrever_links_html(resp.text)
        if arquivo.startswith("assistente"):
            html = html.replace("</body>", script_ia + "\n</body>")
        if arquivo in ("venda.html", "venda_balcao.html"):
            html = _ligar_simulador_pdv(html)
        caminho_arq = SAIDA_DIR / arquivo
        caminho_arq.write_text(html, encoding="utf-8")
        if arquivo == "conversas_ia_1.html":
            (SAIDA_DIR / "conversas_ia.html").write_text(html, encoding="utf-8")
        gerados.add(arquivo)

    # 4. Cria a Landing Page comercial (`landing.html` e `index.html` apontando para a jornada completa!)
    landing_html = _gerar_landing_page()
    (SAIDA_DIR / "landing.html").write_text(landing_html, encoding="utf-8")
    (SAIDA_DIR / "index.html").write_text(landing_html, encoding="utf-8")
    gerados.add("landing.html")
    gerados.add("index.html")

    print(f"[OK] {len(gerados)} telas HTML estaticas exportadas em: {SAIDA_DIR}")


if __name__ == "__main__":
    main()
