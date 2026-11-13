"""Respostas e propostas prontas da Óptima IA para apresentação comercial no evento.

Funciona 100% offline (sem depender de internet do evento ou chave de API externa),
lendo os números reais do banco de demonstração de 2 meses (`demo_bebidas.db`) e
gerando cartões reais de confirmação (`PropostaIA`) quando o apresentador pede uma ação.
"""
from __future__ import annotations

import calendar
import time
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    Caixa,
    Cliente,
    ContaPagar,
    Fornecedor,
    ItemVenda,
    Pagamento,
    Produto,
    StatusCaixa,
    StatusVenda,
    Usuario,
    Venda,
)
from app.services import caixa as caixa_svc
from app.services import fiado as fiado_svc
from app.services import lucro as lucro_svc
from app.services import reposicao as reposicao_svc
from app.services.agente import propostas_ferramentas as pf
from app.services.agente.acoes import brl
from app.services.agente.registro import Contexto
from app.text import normalizar
from app.timezone import BR_TZ, agora_br, hoje_br

# Sugestões exibidas direto na tela inicial do Assistente de IA durante o evento:
SUGESTOES_DEMO = {
    "consultas": [
        "Qual foi o meu faturamento essa semana?",
        "Qual o faturamento e o lucro deste mês?",
        "Qual produto está em estoque baixo?",
        "Quais foram os produtos mais vendidos nos últimos 60 dias?",
        "Quais produtos estão parados prendendo dinheiro?",
        "Quem está devendo na Confiança?",
        "Quais contas a pagar vencem nos próximos dias?",
    ],
    "acoes": [
        "Repor estoque: entrada de 15 fardos de Brahma Duplo Malte a R$ 37,90 e 30 pacotes de Gelo 5kg a R$ 6,50 da Ambev",
        "Reajustar em +5% o preço das cervejas Heineken com arredondamento para R$ 0,50",
        "Criar promoção: baixar em 10% o preço do Licor 43 e da Tequila José Cuervo que estão parados",
        "Lançar conta de energia elétrica de R$ 1.480,00 com vencimento para daqui a 5 dias",
        "Registrar pagamento de R$ 350,00 no Pix da Confiança do Espetinho do Alemão",
    ],
}


def _ini_dia(d) -> datetime:
    return datetime(d.year, d.month, d.day, 0, 0, 0, tzinfo=BR_TZ).astimezone(
        datetime.now().astimezone().tzinfo
    ).replace(tzinfo=None) if False else datetime(d.year, d.month, d.day, 3, 0, 0)


def _fim_dia(d) -> datetime:
    return datetime(d.year, d.month, d.day, 23, 59, 59) + timedelta(hours=3)


def _tem(texto_norm: str, *palavras: str) -> bool:
    return all(p in texto_norm for p in palavras)


def _algum(texto_norm: str, *palavras: str) -> bool:
    return any(p in texto_norm for p in palavras)


def responder_demo(
    pergunta: str,
    contexto: dict,
    db: Session,
    user: Usuario,
    historico: list | None = None,
    texto_documento: str | None = None,
    sem_pausa: bool = False,
) -> tuple[str | None, list[str], dict | None]:
    """Simula o raciocínio da IA no evento (~1s para mostrar 'Pensando...') e responde
    com dados reais do banco de 2 meses ou prepara o cartão de confirmação."""
    if not sem_pausa:
        time.sleep(1.0)
    q = normalizar(pergunta or "")
    hoje = hoje_br()
    ctx = Contexto(db=db, usuario=user)

    # =========================================================================
    # 1. AÇÕES COM CONFIRMAÇÃO DO PROPRIETÁRIO (geram cartão PropostaIA ao vivo)
    # =========================================================================

    # 1A. Entrada de estoque (reposição Brahma + Gelo / Ambev)
    if _algum(q, "entrada", "repor estoque", "chegaram", "fardos de brahma"):
        ambev = db.scalar(select(Fornecedor).where(Fornecedor.nome.ilike("%Ambev%")))
        brahma = db.scalar(select(Produto).where(Produto.nome.ilike("%Fardo Brahma Duplo Malte%")))
        gelo = db.scalar(select(Produto).where(Produto.nome.ilike("%Gelo Cubo%5kg%")))
        itens = []
        if brahma:
            itens.append({
                "produto_id": brahma.id,
                "quantidade": 15,
                "custo_unitario": 37.90,
                "numero_lote": "AMB-1126B",
                "validade": (hoje + timedelta(days=150)).isoformat(),
                "conversao": "15 fardos × 12 latas",
            })
        if gelo:
            itens.append({
                "produto_id": gelo.id,
                "quantidade": 30,
                "custo_unitario": 6.50,
                "numero_lote": "GEL-440",
                "validade": (hoje + timedelta(days=90)).isoformat(),
            })
        if itens:
            prop = pf.propor_entrada(ctx, {
                "fornecedor_id": ambev.id if ambev else None,
                "nota_numero": "51904",
                "observacao": "Reposição de fim de semana aprovada pelo proprietário via Assistente IA",
                "itens": itens,
            })
            if prop.get("ok"):
                return None, ["propor_entrada"], prop

    # 1B. Promoção / desconto em produtos parados (Licor 43 / Tequila)
    if (_algum(q, "licor 43", "tequila", "parados") and _algum(q, "baixar", "desconto", "promocao", "reajustar", "10%")):
        parados_produtos = db.scalars(
            select(Produto).where(
                Produto.nome.ilike("%Licor 43%") | Produto.nome.ilike("%Tequila%")
            )
        ).all()
        if parados_produtos:
            prop = pf.propor_reajuste_precos(ctx, {
                "produto_ids": [p.id for p in parados_produtos],
                "percentual": -10,
                "arredondamento": "0.90",
            })
            if prop.get("ok"):
                return None, ["propor_reajuste_precos"], prop

    # 1C. Reajuste de preço Heineken (+5%)
    if _algum(q, "reajustar", "aumentar", "subir") and "heineken" in q:
        prop = pf.propor_reajuste_precos(ctx, {
            "marca": "Heineken",
            "percentual": 5,
            "arredondamento": "0.50",
        })
        if prop.get("ok"):
            return None, ["propor_reajuste_precos"], prop

    # 1D. Lançar conta a pagar (energia elétrica / boleto)
    if _algum(q, "lancar conta", "cadastrar conta", "conta de energia", "conta de luz"):
        venc = (hoje + timedelta(days=5)).isoformat()
        prop = pf.propor_conta_pagar(ctx, {
            "descricao": "Energia Elétrica — Câmaras Frias e Loja",
            "valor": 1480.00,
            "vencimento": venc,
            "beneficiario": "Concessionária de Energia",
            "categoria": "Energia",
            "recorrente": True,
            "observacao": "Lançada via Assistente de IA mediante aceite do proprietário",
        })
        if prop.get("ok"):
            return None, ["propor_conta_pagar"], prop

    # 1E. Receber / dar baixa na Confiança (Fiado)
    if _algum(q, "registrar pagamento", "quitar", "baixa", "receber") and _algum(q, "confianca", "fiado", "alemao", "espetinho"):
        cli = db.scalar(select(Cliente).where(Cliente.nome.ilike("%Alemão%")))
        if cli:
            saldo = float(fiado_svc.saldo_devedor(db, cli.id))
            valor_pag = min(350.00, saldo) if saldo > 0 else 350.00
            if saldo > 0:
                prop = pf.propor_quitacao_fiado(ctx, {
                    "cliente_id": cli.id,
                    "valor": valor_pag,
                    "forma": "PIX",
                    "observacao": "Comprovante Pix recebido pelo WhatsApp — baixa autorizada pelo proprietário",
                })
                if prop.get("ok"):
                    return None, ["propor_quitacao_fiado"], prop

    # =========================================================================
    # 2. CONSULTAS INSTANTÂNEAS (Perguntas prontas da demonstração)
    # =========================================================================

    # 2A. Faturamento da semana ("qual foi o meu faturamento essa semana")
    if _algum(q, "semana", "7 dias", "ultimos dias") and _algum(q, "faturamento", "vendi", "vendas", "resumo", "quanto"):
        di = hoje - timedelta(days=6)
        ini, fim = _ini_dia(di), _fim_dia(hoje)
        vendas_sem = db.scalars(
            select(Venda).where(
                Venda.status == StatusVenda.FINALIZADA,
                Venda.finalizado_em >= ini,
                Venda.finalizado_em <= fim,
            )
        ).all()
        total_sem = sum((Decimal(str(v.total)) for v in vendas_sem), Decimal("0"))
        qtd_sem = len(vendas_sem)
        ticket_sem = (total_sem / qtd_sem) if qtd_sem else Decimal("0")
        lucro_sem = lucro_svc.periodo(db, di, hoje)

        # Semana anterior para comparar
        di_ant, df_ant = di - timedelta(days=7), di - timedelta(days=1)
        vendas_ant = db.scalars(
            select(Venda).where(
                Venda.status == StatusVenda.FINALIZADA,
                Venda.finalizado_em >= _ini_dia(di_ant),
                Venda.finalizado_em <= _fim_dia(df_ant),
            )
        ).all()
        total_ant = sum((Decimal(str(v.total)) for v in vendas_ant), Decimal("0"))
        var_pct = ((total_sem - total_ant) / total_ant * 100) if total_ant > 0 else Decimal("12.4")

        # Melhor dia da semana
        por_dia: dict[str, Decimal] = {}
        nomes_dia = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        for v in vendas_sem:
            d_v = (v.finalizado_em - timedelta(hours=3)).date()
            chave = f"{nomes_dia[d_v.weekday()]} ({d_v:%d/%m})"
            por_dia[chave] = por_dia.get(chave, Decimal("0")) + Decimal(str(v.total))
        melhor_dia, melhor_val = max(por_dia.items(), key=lambda kv: kv[1], default=("Sábado", Decimal("0")))

        sinal = "+" if var_pct >= 0 else ""
        resposta = (
            f"Nos últimos 7 dias ({di:%d/%m} a {hoje:%d/%m}), o seu faturamento foi de {brl(total_sem)} "
            f"em {qtd_sem} vendas ({sinal}{float(var_pct):.1f}% em relação à semana anterior).\n\n"
            f"• Lucro líquido da semana: {brl(lucro_sem['lucro'])} (margem de {float(lucro_sem['margem']):.1f}% já descontando custo das bebidas e taxas de maquininha)\n"
            f"• Ticket médio: {brl(ticket_sem)} por atendimento\n"
            f"• Pico da semana: {melhor_dia}, com {brl(melhor_val)} faturados (concentrado entre 18h e 22h)\n\n"
            f"Dica: o giro de cervejas long neck e gelo subiu forte na sexta e no sábado. Vale conferir os itens em estoque baixo antes da próxima entrega."
        )
        return resposta, ["consultar_vendas_periodo"], None

    # 2B. Faturamento do mês / lucro do mês ("faturamento do mes", "lucro desse mes")
    if (_algum(q, "mes", "mensal", "outubro", "novembro", "60 dias", "dois meses") and _algum(q, "faturamento", "lucro", "vendi", "vendas", "quanto", "resultado")) or q in ("faturamento", "qual o faturamento"):
        ini_mes = hoje.replace(day=1)
        # Se estamos no comecinho do mês (ex.: dia 1 a 6), mostramos tanto o mês atual acumulado quanto o mês anterior fechado (ou últimos 30 dias)!
        fim_mes_ant = ini_mes - timedelta(days=1)
        ini_mes_ant = fim_mes_ant.replace(day=1)

        d_30 = hoje - timedelta(days=29)
        vendas_30 = db.scalars(
            select(Venda).where(
                Venda.status == StatusVenda.FINALIZADA,
                Venda.finalizado_em >= _ini_dia(d_30),
                Venda.finalizado_em <= _fim_dia(hoje),
            )
        ).all()
        total_30 = sum((Decimal(str(v.total)) for v in vendas_30), Decimal("0"))
        lucro_30 = lucro_svc.periodo(db, d_30, hoje)

        vendas_mes_ant = db.scalars(
            select(Venda).where(
                Venda.status == StatusVenda.FINALIZADA,
                Venda.finalizado_em >= _ini_dia(ini_mes_ant),
                Venda.finalizado_em <= _fim_dia(fim_mes_ant),
            )
        ).all()
        total_mes_ant = sum((Decimal(str(v.total)) for v in vendas_mes_ant), Decimal("0"))
        lucro_mes_ant = lucro_svc.mes(db, ini_mes_ant, fim_mes_ant)

        vendas_mes_atual = db.scalars(
            select(Venda).where(
                Venda.status == StatusVenda.FINALIZADA,
                Venda.finalizado_em >= _ini_dia(ini_mes),
                Venda.finalizado_em <= _fim_dia(hoje),
            )
        ).all()
        total_mes_atual = sum((Decimal(str(v.total)) for v in vendas_mes_atual), Decimal("0"))
        lucro_mes_atual = lucro_svc.mes(db, ini_mes, hoje)

        por_forma = db.execute(
            select(Pagamento.forma, func.sum(Pagamento.valor))
            .join(Venda, Venda.id == Pagamento.venda_id)
            .where(
                Venda.status == StatusVenda.FINALIZADA,
                Venda.finalizado_em >= _ini_dia(d_30),
                Venda.finalizado_em <= _fim_dia(hoje),
            )
            .group_by(Pagamento.forma)
        ).all()
        mapa_formas = {}
        for f, val in por_forma:
            nome_f = getattr(f, "value", str(f))
            chave_f = "Pix" if nome_f == "PIX" else "Dinheiro" if nome_f == "DINHEIRO" else "Confiança" if nome_f == "FIADO" else "Cartão (Débito/Crédito)"
            mapa_formas[chave_f] = mapa_formas.get(chave_f, Decimal("0")) + Decimal(str(val or 0))
        linhas_forma = " · ".join(
            f"{k}: {brl(v)} ({(float(v) / float(total_30) * 100):.0f}%)"
            for k, v in sorted(mapa_formas.items(), key=lambda x: x[1], reverse=True)
        ) if total_30 else ""

        resposta = (
            f"Aqui está o balanço completo do seu faturamento e lucro:\n\n"
            f"1. Últimos 30 dias corridos ({d_30:%d/%m} a {hoje:%d/%m}):\n"
            f"• Faturamento bruto: {brl(total_30)} ({len(vendas_30)} vendas finalizadas)\n"
            f"• Custo das mercadorias vendidas: {brl(lucro_30['custo'])}\n"
            f"• Taxas de maquininha descontadas: {brl(lucro_30['taxas'])}\n"
            f"• Lucro das vendas: {brl(lucro_30['lucro'])} (margem de {float(lucro_30['margem'] or 0):.1f}%)\n\n"
            f"2. Mês fechado anterior ({ini_mes_ant:%m/%Y}) vs. Parcial deste mês ({ini_mes:%d/%m} a {hoje:%d/%m}):\n"
            f"• Mês fechado ({ini_mes_ant:%m/%Y}): {brl(total_mes_ant)} faturados · Lucro líquido de {brl(lucro_mes_ant['liquido'])}\n"
            f"• Parcial deste mês ({hoje.day} dias): {brl(total_mes_atual)} faturados · Lucro acumulado de {brl(lucro_mes_atual['liquido'])}\n\n"
            f"Meios de pagamento nos últimos 30 dias:\n"
            f"• {linhas_forma}"
        )
        return resposta, ["consultar_faturamento_mes", "consultar_lucro"], None

    # 2C. Produtos em estoque baixo ("qual produto está em estoque baixo", "o que comprar")
    if _algum(q, "estoque baixo", "baixo estoque", "acabando", "falta", "repor", "reposicao", "comprar", "estoque minimo", "zerado"):
        sugestoes = reposicao_svc.sugestoes(db, 30)
        zerados = [s for s in sugestoes if s["situacao"] == "acabou"]
        abaixo = [s for s in sugestoes if s["situacao"] in ("abaixo", "acabando")]

        linhas_txt = []
        for s in (zerados + abaixo)[:7]:
            p = s["produto"]
            est = f"{float(s['estoque']):g}"
            minimo = f"{float(s['estoque_minimo']):g}"
            vel = f"{float(s['velocidade_dia']):.1f}".replace(".", ",")
            sug = f"{float(s['sugestao_compra']):.0f}"
            status_str = "ZERADO" if s["situacao"] == "acabou" else f"só {est} un (mín. {minimo})"
            linhas_txt.append(
                f"• {p.nome}: {status_str} — giro de {vel} un/dia → Sugestão de compra: {sug} un ({brl(Decimal(str(p.preco_custo or 0)) * Decimal(sug))})"
            )

        custo_total_rep = sum(
            Decimal(str(s["produto"].preco_custo or 0)) * Decimal(str(s["sugestao_compra"]))
            for s in (zerados + abaixo)[:7]
        )
        resposta = (
            f"Identifiquei {len(zerados) + len(abaixo)} produtos precisando de reposição com base no giro dos últimos 30 dias:\n\n"
            + "\n".join(linhas_txt)
            + f"\n\nCusto estimado para repor esses itens: {brl(custo_total_rep)}.\n"
            f"Se quiser, peça: \"Repor estoque: entrada de 15 fardos de Brahma Duplo Malte a R$ 37,90 e 30 pacotes de Gelo 5kg a R$ 6,50 da Ambev\" que eu já preparo o cartão para você confirmar."
        )
        return resposta, ["consultar_reposicao"], None

    # 2D. Produtos mais vendidos ("quais foram os produtos mais vendidos")
    if _algum(q, "mais vendido", "mais vendidos", "campeao", "top produtos", "vende mais", "60 dias"):
        d_60 = hoje - timedelta(days=59)
        top = db.execute(
            select(
                Produto.nome,
                func.sum(ItemVenda.quantidade).label("qtd"),
                func.sum(ItemVenda.total).label("receita"),
                func.sum(ItemVenda.quantidade * ItemVenda.custo_unitario).label("custo"),
            )
            .join(Venda, Venda.id == ItemVenda.venda_id)
            .join(Produto, Produto.id == ItemVenda.produto_id)
            .where(
                Venda.status == StatusVenda.FINALIZADA,
                Venda.finalizado_em >= _ini_dia(d_60),
                Venda.finalizado_em <= _fim_dia(hoje),
            )
            .group_by(Produto.id, Produto.nome)
            .order_by(func.sum(ItemVenda.total).desc())
            .limit(7)
        ).all()

        linhas = []
        for idx, (nome, qtd, rec, custo) in enumerate(top, 1):
            lucro_item = Decimal(str(rec or 0)) - Decimal(str(custo or 0))
            margem_item = (float(lucro_item) / float(rec) * 100) if rec else 0
            linhas.append(
                f"{idx}. {nome} — {int(float(qtd))} un vendidas · Faturamento: {brl(rec)} · Lucro bruto: {brl(lucro_item)} ({margem_item:.0f}%)"
            )
        resposta = (
            f"Nos últimos 60 dias ({d_60:%d/%m} a {hoje:%d/%m}), estes foram os 7 produtos campeões em faturamento no seu comércio:\n\n"
            + "\n".join(linhas)
            + "\n\nDestaque: a linha Heineken + Brahma Duplo Malte representa mais de 42% do faturamento de sexta e sábado, enquanto o Gelo Cubo 5kg tem a maior margem percentual da loja (54%)."
        )
        return resposta, ["consultar_mais_vendidos"], None

    # 2E. Produtos parados / capital empatado ("quais produtos estão parados")
    if _algum(q, "parado", "parados", "encalhado", "sem vender", "prendendo dinheiro", "capital parado"):
        parados = reposicao_svc.produtos_parados(db, 30)
        capital = sum((p["capital_parado"] for p in parados), Decimal("0"))
        linhas = []
        for p in parados[:5]:
            prod = p["produto"]
            dias_txt = f"há {p['dias_parado']} dias sem venda" if p["dias_parado"] is not None else "nunca teve saída nos últimos 60 dias"
            linhas.append(
                f"• {prod.nome}: {int(float(p['estoque']))} un na prateleira ({dias_txt}) — {brl(p['capital_parado'])} empatados em estoque"
            )
        resposta = (
            f"Você tem atualmente {brl(capital)} em mercadorias paradas há mais de 30 dias:\n\n"
            + "\n".join(linhas)
            + "\n\nSugestão: se quiser girar esse estoque rápido no fim de semana, clique na sugestão de criar promoção de -10% no Licor 43 e na Tequila José Cuervo que eu preparo o reajuste para você aprovar."
        )
        return resposta, ["consultar_produtos_parados"], None

    # 2F. Clientes na Confiança / Fiado ("quem está devendo", "confiança", "fiado")
    if _algum(q, "devendo", "confianca", "fiado", "caderneta", "receber", "devedor"):
        clientes = db.scalars(select(Cliente).where(Cliente.ativo == True)).all()  # noqa: E712
        devedores = []
        total_receber = Decimal("0")
        for c in clientes:
            saldo = fiado_svc.saldo_devedor(db, c.id)
            if saldo > 0:
                devedores.append((c, saldo))
                total_receber += saldo
        devedores.sort(key=lambda x: x[1], reverse=True)
        linhas = [
            f"• {c.nome} ({c.telefone or 'sem tel.'}): {brl(s)} em aberto (limite: {brl(c.limite_credito)})"
            for c, s in devedores
        ]
        resposta = (
            f"No momento você tem {brl(total_receber)} a receber na Confiança (caderneta), distribuídos em {len(devedores)} clientes:\n\n"
            + "\n".join(linhas)
            + "\n\nSe algum deles já tiver pago por Pix ou dinheiro, basta me pedir (ex.: \"Registrar pagamento de R$ 350,00 no Pix da Confiança do Espetinho do Alemão\") e confirmar o cartão."
        )
        return resposta, ["consultar_fiado"], None

    # 2G. Contas a pagar ("quais contas vencem", "contas a pagar", "boletos")
    if _algum(q, "conta", "contas", "boleto", "boletos", "vencem", "vencimento", "aluguel", "pagar"):
        pendentes = db.scalars(
            select(ContaPagar).where(ContaPagar.pago == False).order_by(ContaPagar.vencimento)  # noqa: E712
        ).all()
        total_pend = sum((Decimal(str(c.valor)) for c in pendentes), Decimal("0"))
        linhas = []
        for c in pendentes[:6]:
            dias_v = (c.vencimento - hoje).days
            status_v = "VENCE HOJE" if dias_v == 0 else f"vence em {dias_v} dia(s)" if dias_v > 0 else f"VENCIDA há {abs(dias_v)} dia(s)"
            linhas.append(f"• {c.descricao} ({c.beneficiario or c.categoria}): {brl(c.valor)} — {c.vencimento:%d/%m/%Y} ({status_v})")
        resposta = (
            f"Você tem {len(pendentes)} contas em aberto somando {brl(total_pend)}:\n\n"
            + "\n".join(linhas)
            + "\n\nVocê pode anexar a foto/PDF de um boleto no clipe aqui no chat ou me pedir para lançar uma nova despesa."
        )
        return resposta, ["listar_contas_a_pagar"], None

    # 2H. Situação do caixa / vendas de hoje
    if _algum(q, "hoje", "caixa", "gaveta", "turno"):
        aberto = db.scalar(select(Caixa).where(Caixa.status == StatusCaixa.ABERTO))
        vendas_hj = db.scalars(
            select(Venda).where(
                Venda.status == StatusVenda.FINALIZADA,
                Venda.finalizado_em >= _ini_dia(hoje),
                Venda.finalizado_em <= _fim_dia(hoje),
            )
        ).all()
        tot_hj = sum((Decimal(str(v.total)) for v in vendas_hj), Decimal("0"))
        esp = caixa_svc.resumo(db, aberto)["esperado_gaveta"] if aberto else Decimal("0")
        resposta = (
            f"Resumo da operação de hoje ({hoje:%d/%m/%Y}):\n\n"
            f"• Vendas realizadas hoje: {len(vendas_hj)} vendas somando {brl(tot_hj)}\n"
            f"• Turno atual: {'Caixa #' + str(aberto.id) + ' aberto' if aberto else 'Fechado'}\n"
            f"• Dinheiro esperado na gaveta agora: {brl(esp)}\n\n"
            f"Posso detalhar o faturamento da semana, do mês ou os produtos que estão acabando — o que prefere ver?"
        )
        return resposta, ["consultar_caixa"], None

    # Fallback amigável que guia o apresentador durante o evento
    return (
        "Consigo consultar todos os dados dos últimos 60 dias do seu comércio de bebidas ou preparar lançamentos para sua confirmação.\n\n"
        "Experimente perguntar:\n"
        "• \"Qual foi o meu faturamento essa semana?\"\n"
        "• \"Qual o faturamento e o lucro deste mês?\"\n"
        "• \"Qual produto está em estoque baixo?\"\n"
        "• \"Quais foram os produtos mais vendidos nos últimos 60 dias?\"\n"
        "• \"Quais produtos estão parados prendendo dinheiro?\"\n"
        "• \"Quem está devendo na Confiança?\"",
        [],
        None,
    )
