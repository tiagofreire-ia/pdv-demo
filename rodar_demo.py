"""Servidor do Sistema em Modo Demonstração Comercial ("SUA MARCA").

Roda o sistema completo na porta 8050 usando o banco isolado `demo_bebidas.db`
(2 meses de comércio de bebidas), sem tocar nos arquivos ou no banco do cliente real.
Inclui:
  - Marca "SUA MARCA" em todas as telas e logo genérica dourada
  - Login automático no painel do proprietário (basta abrir http://127.0.0.1:8050)
  - Assistente de IA com perguntas e respostas prontas + cartões de ação com aceite do dono (100% offline)
"""
from __future__ import annotations

import argparse
import os
import sys
import webbrowser
from pathlib import Path
from threading import Timer

DEMO_DIR = Path(__file__).resolve().parent
RAIZ = DEMO_DIR.parent
DB_PATH = DEMO_DIR / "demo_bebidas.db"

# 1. Variáveis de ambiente isoladas ANTES de carregar a aplicação
os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH.as_posix()}"
os.environ["NOME_LOJA"] = "SUA MARCA"
os.environ["GROQ_API_KEY"] = "demo-evento-offline"

sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(DEMO_DIR))

if not DB_PATH.exists():
    from gerar_dados_demo import gerar_banco
    gerar_banco(forcar=True)

import uvicorn  # noqa: E402
from fastapi import Request  # noqa: E402
from fastapi.responses import RedirectResponse, Response  # noqa: E402
from sqlalchemy import select  # noqa: E402

import app.ajuda as ajuda_pkg  # noqa: E402
import app.routers.admin as admin_router  # noqa: E402
import app.services.agente as agente_pkg  # noqa: E402
import app.services.ia as ia_svc  # noqa: E402
import app.services.llm as llm_pkg  # noqa: E402
from app.config import settings  # noqa: E402
from app.database import SessionLocal  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Usuario  # noqa: E402
from app.security import iniciar_sessao, usuario_logado  # noqa: E402
from app.services import conversas_ia as conversas_svc  # noqa: E402
from app.templating import templates  # noqa: E402
from ia_demo_respostas import SUGESTOES_DEMO, responder_demo  # noqa: E402

# 2. Garante o nome "SUA MARCA" nos templates e settings
settings.nome_loja = "SUA MARCA"
templates.env.globals["NOME_LOJA"] = "SUA MARCA"

# 3. Conecta o Assistente de IA às respostas e propostas instantâneas da demonstração
ia_svc.configurado = lambda: True
agente_pkg.configurado = lambda com_documento=False: True
agente_pkg.responder = responder_demo
admin_router.agente.responder = responder_demo
llm_pkg.uso.limite_excedido = lambda db, user: None
ajuda_pkg.sugestoes_assistente = lambda admin=True: SUGESTOES_DEMO

# 4. Logo SVG elegante "SUA MARCA" (substitui a logo do cliente sem alterar arquivos de app/static)
LOGO_SVG_MARCA = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96" width="96" height="96">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#E3CF94"/>
      <stop offset="100%" stop-color="#C9A13B"/>
    </linearGradient>
  </defs>
  <rect width="96" height="96" rx="22" fill="#16130E"/>
  <rect x="4" y="4" width="88" height="88" rx="18" fill="none" stroke="url(#g)" stroke-width="2.5" opacity="0.85"/>
  <text x="48" y="42" text-anchor="middle" fill="#E3CF94" font-family="Manrope, system-ui, sans-serif" font-weight="800" font-size="18" letter-spacing="1.5">SUA</text>
  <text x="48" y="64" text-anchor="middle" fill="#C9A13B" font-family="Manrope, system-ui, sans-serif" font-weight="800" font-size="17" letter-spacing="1">MARCA</text>
</svg>"""


_template_response_original = templates.TemplateResponse

SCRIPT_CLIQUE_SUGESTAO = """
<script>
  // Modo Apresentação: clicar numa sugestão preenche o campo e já envia na hora!
  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-sugestao]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var form = document.querySelector("[data-form-pergunta]");
        var campo = form ? form.querySelector('input[name="pergunta"]') : null;
        if (!form || !campo) return;
        campo.value = btn.getAttribute("data-sugestao") || "";
        if (typeof form.requestSubmit === "function") form.requestSubmit();
        else form.querySelector('button[type="submit"]').click();
      });
    });
  });
</script>
</body>"""


def _template_response_demo(*args, **kwargs):
    resp = _template_response_original(*args, **kwargs)
    if hasattr(resp, "body") and resp.body:
        texto = resp.body.decode("utf-8", errors="ignore")
        texto = texto.replace('content="GH Bebidas"', 'content="SUA MARCA"')
        texto = texto.replace("Disk Bebidas GH", "SUA MARCA")
        if "data-sugestao" in texto:
            texto = texto.replace("</body>", SCRIPT_CLIQUE_SUGESTAO)
        novos_bytes = texto.encode("utf-8")
        resp.body = novos_bytes
        resp.headers["content-length"] = str(len(novos_bytes))
    return resp


templates.TemplateResponse = _template_response_demo


@app.middleware("http")
async def middleware_demo_evento(request: Request, call_next):
    caminho = request.url.path
    # Serve a logo "SUA MARCA" no lugar da logo do cliente
    if caminho in ("/static/img/logo-96.png", "/static/img/logo.png", "/static/img/apple-touch-icon.png"):
        return Response(content=LOGO_SVG_MARCA, media_type="image/svg+xml")
    return await call_next(request)


@app.get("/landing")
def demo_landing():
    """Exibe a Landing Page comercial também no servidor ao vivo."""
    arq = DEMO_DIR / "telas_estaticas" / "landing.html"
    if arq.exists():
        html = arq.read_text(encoding="utf-8")
        html = html.replace('href="./static/', 'href="/static/')
        html = html.replace('src="./static/img/logo-marca.svg"', 'src="/static/img/logo-96.png"')
        html = html.replace('href="./login.html"', 'href="/login"')
        html = html.replace('href="./painel.html"', 'href="/demo-entrar?destino=/admin"')
        html = html.replace('href="./assistente.html"', 'href="/demo-entrar?destino=/admin/assistente"')
        html = html.replace('href="./conversas_ia.html"', 'href="/demo-entrar?destino=/admin/conversas-ia/1"')
        html = html.replace('href="./reposicao.html"', 'href="/demo-entrar?destino=/admin/reposicao"')
        html = html.replace('href="./landing.html"', 'href="/landing"')
        return Response(content=html, media_type="text/html; charset=utf-8")
    return RedirectResponse("/demo-entrar", status_code=303)


@app.get("/demo-entrar")
def demo_entrar(request: Request, destino: str = "/admin"):
    """Faz login automático como Proprietário (Super Admin) e abre a conversa do Assistente limpa
    com as sugestões prontas na tela."""
    with SessionLocal() as db:
        dono = db.scalar(select(Usuario).where(Usuario.super_admin == True))  # noqa: E712
        if dono:
            iniciar_sessao(request, dono)
            # Começa na tela inicial do Assistente (com os botões de perguntas prontas visíveis),
            # mantendo as 5 conversas anteriores salvas no topo!
            conversas_svc.nova(request)
            request.session["tour_dispensado"] = True
    return RedirectResponse(destino, status_code=303)


def main() -> None:
    parser = argparse.ArgumentParser(description="Roda o sistema em Modo Demonstração para o evento.")
    parser.add_argument("--porta", type=int, default=8050, help="Porta local (padrão: 8050)")
    parser.add_argument("--reset", action="store_true", help="Recria o banco de 2 meses do zero antes de subir")
    parser.add_argument("--sem-navegador", action="store_true", help="Não abre o navegador automaticamente")
    args = parser.parse_args()

    if args.reset or not DB_PATH.exists():
        from gerar_dados_demo import gerar_banco
        gerar_banco(forcar=True)

    url = f"http://127.0.0.1:{args.porta}/demo-entrar"
    print("=" * 68)
    print("  SISTEMA EM MODO DEMONSTRACAO COMERCIAL - 'SUA MARCA'")
    print("=" * 68)
    print(f"  Acesse no navegador: {url}")
    print("  Login manual (se precisar): dono@suamarca.com.br / demo123")
    print("=" * 68)

    if not args.sem_navegador:
        Timer(1.5, lambda: webbrowser.open(url)).start()

    uvicorn.run(app, host="127.0.0.1", port=args.porta, log_level="warning")


if __name__ == "__main__":
    main()
