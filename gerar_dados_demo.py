"""Gera o banco SQLite de demonstração (`apresentacao_evento/demo_bebidas.db`) com
60 dias (2 meses) de operação realista de um comércio/distribuidora de bebidas,
incluindo conversas da IA e ações executadas mediante confirmação do proprietário.

Não toca em nenhum arquivo do projeto principal.
"""
from __future__ import annotations

import os
import random
import secrets
import sys
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path

DEMO_DIR = Path(__file__).resolve().parent
RAIZ = DEMO_DIR.parent
DB_PATH = DEMO_DIR / "demo_bebidas.db"

# Configura o ambiente ANTES de importar app.*
os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH.as_posix()}"
os.environ["NOME_LOJA"] = "SUA MARCA"
os.environ["GROQ_API_KEY"] = "demo-evento-offline"

sys.path.insert(0, str(RAIZ))

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models import (  # noqa: E402
    AlertaSistema,
    AtivoFixo,
    Caixa,
    ChamadoSuporte,
    Cliente,
    Configuracao,
    ContaPagar,
    ConversaIA,
    EntradaEstoque,
    EstadoAtivo,
    FiscalStatus,
    FormaPagamento,
    Fornecedor,
    Inventario,
    ItemEntrada,
    ItemInventario,
    ItemRemovido,
    ItemVenda,
    LicaoIA,
    LogAuditoria,
    Lote,
    MensagemIA,
    Pagamento,
    PerdaEstoque,
    Produto,
    PropostaIA,
    QuitacaoFiado,
    RetiradaCaixa,
    RetiradaDono,
    SinalIA,
    StatusCaixa,
    StatusInventario,
    StatusVenda,
    TipoDocumento,
    TipoPessoa,
    Unidade,
    UsoIA,
    Usuario,
    Venda,
)
from app.security import hash_senha  # noqa: E402
from app.text import normalizar  # noqa: E402
from app.timezone import hoje_br  # noqa: E402


def _utc(d: date, h: int, m: int = 0) -> datetime:
    """Converte horário de Brasília (d, h:m) para UTC sem tzinfo (padrão do banco)."""
    return datetime.combine(d, time(h, m)) + timedelta(hours=3)


def gerar_banco(forcar: bool = True) -> Path:
    if forcar and DB_PATH.exists():
        try:
            engine.dispose()
            DB_PATH.unlink()
        except PermissionError:
            # Se o servidor rodar_demo.py estiver aberto usando o arquivo no Windows,
            # recriamos as tabelas por dentro da conexão sem precisar apagar o arquivo!
            Base.metadata.drop_all(bind=engine)

    Base.metadata.create_all(bind=engine)
    rnd = random.Random(202611)
    hoje = hoje_br()

    with SessionLocal() as db:
        # 1. USUÁRIOS (Proprietário, Gerente e 2 Operadores de Caixa)
        senha_padrao = hash_senha("demo123")
        dono = Usuario(
            nome="Carlos Eduardo (Proprietário)",
            email="dono@suamarca.com.br",
            senha_hash=senha_padrao,
            admin=True,
            super_admin=True,
            ativo=True,
            criado_em=_utc(hoje - timedelta(days=90), 9, 0),
        )
        gerente = Usuario(
            nome="Fernanda Lima (Gerente)",
            email="gerente@suamarca.com.br",
            senha_hash=senha_padrao,
            admin=True,
            super_admin=False,
            ativo=True,
            criado_em=_utc(hoje - timedelta(days=85), 10, 0),
        )
        caixa_dia = Usuario(
            nome="Lucas Mendes",
            email="lucas@suamarca.com.br",
            senha_hash=senha_padrao,
            admin=False,
            super_admin=False,
            ativo=True,
            criado_em=_utc(hoje - timedelta(days=80), 8, 30),
        )
        caixa_noite = Usuario(
            nome="Marcos Vinícius",
            email="marcos@suamarca.com.br",
            senha_hash=senha_padrao,
            admin=False,
            super_admin=False,
            ativo=True,
            criado_em=_utc(hoje - timedelta(days=75), 14, 0),
        )
        ex_operador = Usuario(
            nome="Rafael Souza",
            email="rafael@suamarca.com.br",
            senha_hash=senha_padrao,
            admin=False,
            super_admin=False,
            ativo=False,
            criado_em=_utc(hoje - timedelta(days=120), 9, 0),
        )
        db.add_all([dono, gerente, caixa_dia, caixa_noite, ex_operador])
        db.flush()

        # 2. CONFIGURAÇÕES DA LOJA (Taxas de maquininha + fechamento automático)
        configs = [
            ("fechamento_automatico_ativo", "1"),
            ("fechamento_automatico_horario", "23:30"),
            ("taxa_cielo_debito", "1.39"),
            ("taxa_cielo_credito", "3.19"),
            ("taxa_cielo_credito_parcelado", "5.49"),
            ("taxa_stone_debito", "1.29"),
            ("taxa_stone_credito", "2.99"),
            ("taxa_stone_credito_parcelado", "4.99"),
        ]
        for ch, val in configs:
            db.add(Configuracao(chave=ch, valor=val))

        # 3. FORNECEDORES DE BEBIDAS
        f_ambev = Fornecedor(
            nome="Ambev S.A. — CD Direto",
            cnpj="07.526.557/0001-00",
            telefone="(11) 3003-2be0",
            email="pedidos@ambev.com.br",
            endereco="Rod. Anhanguera, Km 42 — Galpão Logístico",
            observacao="Entregas terças e sextas até 11h. Boleto 14/28 dias.",
        )
        f_heineken = Fornecedor(
            nome="Heineken Brasil Bebidas Ltda",
            cnpj="50.221.019/0001-36",
            telefone="(11) 4004-8812",
            email="comercial@heineken.com.br",
            endereco="Av. das Nações, 1400 — Distrito Industrial",
            observacao="Pedido mínimo 25 caixas/fardos. Vendedor: Ricardo.",
        )
        f_coca = Fornecedor(
            nome="Coca-Cola FEMSA Brasil",
            cnpj="61.186.888/0001-93",
            telefone="(11) 0800-727-1100",
            email="faturamento@kof.com.mx",
            endereco="Via Expressa Sul, 890",
            observacao="Entrega toda quarta-feira.",
        )
        f_destilados = Fornecedor(
            nome="Império dos Destilados & Importados Ltda",
            cnpj="14.892.301/0001-54",
            telefone="(11) 99812-4410",
            email="vendas@imperiodestilados.com.br",
            endereco="Rua do Comércio Atacadista, 312",
            observacao="Whisky, Gin, Vodka e Licores com selo IPI.",
        )
        f_gelo = Fornecedor(
            nome="Gelo Cristal & Brasa Atacado Ltda",
            cnpj="28.441.902/0001-19",
            telefone="(11) 98711-0092",
            email="entrega@gelocristal.com.br",
            endereco="Av. Marginal Norte, 115",
            observacao="Reposição diária de gelo 5kg, gelo de coco e carvão.",
        )
        f_energeticos = Fornecedor(
            nome="Sul Distribuidora de Energéticos e Conveniência",
            cnpj="33.109.774/0001-82",
            telefone="(11) 97122-8830",
            email="contato@sulenergeticos.com.br",
            endereco="Rua das Indústrias, 504",
        )
        db.add_all([f_ambev, f_heineken, f_coca, f_destilados, f_gelo, f_energeticos])
        db.flush()

        # 4. PRODUTOS (~30 itens realistas do comércio de bebidas)
        # (codigo, nome, un, preco_venda, preco_custo, estoque_atual, estoque_min, vol_ml, cat, marca, forn, peso_giro)
        catalogo = [
            # Cervejas alto giro (algumas com estoque baixo de propósito para demonstração!)
            ("78936683", "Heineken Long Neck 330ml", Unidade.UN, 7.50, 4.95, 14, 48, 330, "Cervejas", "Heineken", f_heineken, 28),
            ("78936690", "Fardo Heineken Lata 350ml c/ 12 un", Unidade.FARDO, 69.90, 51.60, 18, 12, 4200, "Cervejas", "Heineken", f_heineken, 16),
            ("7891149101993", "Brahma Duplo Malte Lata 350ml", Unidade.UN, 4.50, 2.89, 84, 48, 350, "Cervejas", "Brahma", f_ambev, 32),
            ("7891149102006", "Fardo Brahma Duplo Malte 350ml c/ 12 un", Unidade.FARDO, 49.90, 37.90, 3, 15, 4200, "Cervejas", "Brahma", f_ambev, 22),
            ("7891149210114", "Spaten Puro Malte Lata 350ml", Unidade.UN, 5.20, 3.45, 62, 36, 350, "Cervejas", "Spaten", f_ambev, 20),
            ("7891149210992", "Fardo Spaten Lata 350ml c/ 12 un", Unidade.FARDO, 56.90, 41.40, 11, 10, 4200, "Cervejas", "Spaten", f_ambev, 13),
            ("7501064191350", "Corona Extra Long Neck 330ml", Unidade.UN, 8.50, 5.60, 42, 24, 330, "Cervejas", "Corona", f_ambev, 15),
            ("7891149105502", "Cerveja Original 600ml", Unidade.UN, 11.90, 7.80, 48, 24, 600, "Cervejas", "Original", f_ambev, 14),
            ("7896045506049", "Amstel Lata 473ml (Latão)", Unidade.UN, 5.50, 3.65, 96, 48, 473, "Cervejas", "Amstel", f_heineken, 24),
            ("7891991010023", "Fardo Skol Pilsen Lata 350ml c/ 12 un", Unidade.FARDO, 44.90, 33.60, 20, 12, 4200, "Cervejas", "Skol", f_ambev, 14),

            # Gelo e Churrasco (altíssimo giro e margem — com estoque crítico para brilhar na demo!)
            ("7898901234011", "Gelo Cubo Cristal Pacote 5kg", Unidade.UN, 14.00, 6.50, 4, 30, 5000, "Gelo e Carvão", "Gelo Cristal", f_gelo, 26),
            ("7898901234028", "Gelo de Água de Coco p/ Drink 200ml", Unidade.UN, 4.50, 2.10, 55, 24, 200, "Gelo e Carvão", "Gelo Cristal", f_gelo, 18),
            ("7898901234097", "Carvão Vegetal Eucalipto Saco 4kg", Unidade.UN, 24.90, 14.50, 0, 12, 4000, "Gelo e Carvão", "Brasa Forte", f_gelo, 12),

            # Energéticos
            ("9002490100070", "Red Bull Energy Drink Lata 250ml", Unidade.UN, 10.90, 7.10, 9, 36, 250, "Energéticos", "Red Bull", f_energeticos, 19),
            ("070847811169", "Monster Energy Green Lata 473ml", Unidade.UN, 11.50, 7.40, 34, 24, 473, "Energéticos", "Monster", f_energeticos, 14),
            ("7898357410015", "Energético Bally Tropical 2L", Unidade.UN, 14.90, 8.20, 22, 12, 2000, "Energéticos", "Bally", f_energeticos, 10),

            # Refrigerantes e Águas
            ("7894900011517", "Coca-Cola Original PET 2L", Unidade.UN, 11.90, 7.85, 45, 24, 2000, "Refrigerantes", "Coca-Cola", f_coca, 22),
            ("7894900700046", "Coca-Cola Sem Açúcar PET 2L", Unidade.UN, 11.90, 7.85, 28, 18, 2000, "Refrigerantes", "Coca-Cola", f_coca, 14),
            ("7894900010015", "Coca-Cola Lata 350ml", Unidade.UN, 4.50, 2.75, 72, 36, 350, "Refrigerantes", "Coca-Cola", f_coca, 18),
            ("7891991000833", "Guaraná Antarctica PET 2L", Unidade.UN, 9.90, 6.40, 32, 18, 2000, "Refrigerantes", "Antarctica", f_ambev, 15),
            ("7891991002110", "Água Tônica Antarctica Lata 350ml", Unidade.UN, 4.80, 2.90, 40, 24, 350, "Refrigerantes", "Antarctica", f_ambev, 9),
            ("7891910000197", "Água Mineral Cristal sem Gás 500ml", Unidade.UN, 3.00, 1.15, 110, 48, 500, "Águas", "Cristal", f_coca, 20),
            ("7891910000198", "Água Mineral Cristal com Gás 500ml", Unidade.UN, 3.50, 1.40, 64, 36, 500, "Águas", "Cristal", f_coca, 12),

            # Destilados e Vinhos (bons de margem)
            ("5000267014005", "Whisky Johnnie Walker Red Label 1L", Unidade.UN, 109.90, 76.00, 14, 6, 1000, "Destilados", "Johnnie Walker", f_destilados, 6),
            ("5010106113127", "Whisky Ballantine's Finest 1L", Unidade.UN, 94.90, 65.00, 10, 6, 1000, "Destilados", "Ballantine's", f_destilados, 5),
            ("5000289111027", "Gin Tanqueray London Dry 750ml", Unidade.UN, 119.90, 82.00, 9, 5, 750, "Destilados", "Tanqueray", f_destilados, 5),
            ("7312040017072", "Vodka Absolut Original 1L", Unidade.UN, 89.90, 61.50, 12, 6, 1000, "Destilados", "Absolut", f_destilados, 6),
            ("7896002100129", "Vodka Smirnoff Red 998ml", Unidade.UN, 46.90, 31.20, 19, 10, 998, "Destilados", "Smirnoff", f_destilados, 9),
            ("7898115420013", "Cachaça Artesanal Salinas 670ml", Unidade.UN, 54.90, 36.00, 8, 6, 670, "Destilados", "Salinas", f_destilados, 4),
            ("7804320985619", "Vinho Chileno Reservado Cabernet 750ml", Unidade.UN, 39.90, 23.50, 16, 8, 750, "Vinhos", "Concha y Toro", f_destilados, 7),

            # PRODUTOS PARADOS (peso_giro = 0 nos últimos 45+ dias, para demonstrar "Dinheiro parado"!)
            ("8410013991009", "Licor 43 Diego Zamora Espanhol 700ml", Unidade.UN, 159.90, 114.00, 8, 2, 700, "Destilados", "Licor 43", f_destilados, 0),
            ("7501035010109", "Tequila José Cuervo Especial Gold 750ml", Unidade.UN, 134.90, 96.00, 7, 2, 750, "Destilados", "José Cuervo", f_destilados, 0),
            ("8000040000109", "Aperitivo Campari Bitter 900ml", Unidade.UN, 64.90, 45.00, 10, 4, 900, "Destilados", "Campari", f_destilados, 0),
        ]

        produtos_db: list[Produto] = []
        pesos_giro: list[int] = []
        for cb, nome, un, pv, pc, est, est_min, vol, cat, marca, forn, peso in catalogo:
            p = Produto(
                codigo_barras=cb,
                nome=nome,
                nome_busca=normalizar(nome),
                unidade=un,
                preco_venda=pv,
                preco_custo=pc,
                estoque=est,
                estoque_minimo=est_min,
                volume_ml=vol,
                categoria=cat,
                marca=marca,
                fornecedor_principal_id=forn.id,
                ativo=True,
                criado_em=_utc(hoje - timedelta(days=90), 10, 0),
            )
            db.add(p)
            produtos_db.append(p)
            pesos_giro.append(peso)
        db.flush()

        # Lotes (incluindo 2 lotes próximos do vencimento para o Painel destacar em "Precisa de atenção")
        p_heineken_ln = produtos_db[0]
        p_spaten = produtos_db[4]
        p_original = produtos_db[7]
        p_coca_zero = produtos_db[17]
        db.add_all([
            Lote(produto_id=p_coca_zero.id, numero_lote="KOF-0826", validade=hoje + timedelta(days=4), quantidade=12),
            Lote(produto_id=p_spaten.id, numero_lote="AMB-0911", validade=hoje + timedelta(days=6), quantidade=18),
            Lote(produto_id=p_heineken_ln.id, numero_lote="HNK-1044", validade=hoje + timedelta(days=120), quantidade=14),
            Lote(produto_id=p_original.id, numero_lote="AMB-1088", validade=hoje + timedelta(days=95), quantidade=48),
        ])

        # Uma venda muito antiga (há 52 dias) para Licor 43 e há 48 dias para Tequila para aparecerem como "48 dias" e "52 dias" parados!
        # (Campari fica sem nenhuma venda = "nunca vendeu")

        # 5. CLIENTES (Bares parceiros, organizadores de festa e vizinhos com Confiança)
        clientes_dados = [
            ("Espetinho do Alemão", TipoPessoa.PJ, "18.421.099/0001-71", "(11) 99123-4501", "Rua das Palmeiras, 410", 1200.00, "Pega cerveja e carvão toda quinta/sexta; acerta no Pix segunda."),
            ("Bar & Petiscaria Recanto", TipoPessoa.PJ, "22.610.884/0001-30", "(11) 98412-3309", "Av. Brasil, 1020", 1500.00, "Cliente antigo, compra fardos e destilados."),
            ("Rodrigo Eventos & Churrascos", TipoPessoa.PF, "319.442.818-20", "(11) 97211-9088", "Condomínio Bela Vista, Q. 4", 800.00, "Organizador de festas de fim de semana."),
            ("Churrascaria Boi Dourado", TipoPessoa.PJ, "09.331.712/0001-44", "(11) 3412-8800", "Rodovia Sul, Km 12", 2000.00, "Compra gelo e long neck de emergência."),
            ("Henrique Moraes (Morador Qd. 12)", TipoPessoa.PF, "402.118.998-05", "(11) 99654-1120", "Quadra 12, Casa 08", 400.00, "Vizinho da loja, paga todo dia 5."),
            ("Juliana Costa", TipoPessoa.PF, "288.901.448-12", "(11) 98110-7741", "Rua Ipê Amarelo, 88", 300.00, ""),
            ("Quadra Society Arena Gol", TipoPessoa.PJ, "41.802.119/0001-16", "(11) 99301-5566", "Rua Esportiva, 55", 1000.00, "Bar da quadra de futebol."),
            ("Marcelo Tavares", TipoPessoa.PF, "195.672.338-90", "(11) 98877-2211", "Rua das Acácias, 19", 250.00, ""),
        ]
        clientes_db: list[Cliente] = []
        for nome, tp, doc, tel, end, lim, obs in clientes_dados:
            c = Cliente(
                nome=nome,
                tipo=tp,
                cpf_cnpj=doc,
                telefone=tel,
                endereco=end,
                limite_credito=lim,
                observacao=obs,
                ativo=True,
                criado_em=_utc(hoje - timedelta(days=80), 11, 0),
            )
            db.add(c)
            clientes_db.append(c)
        db.flush()

        # 6. 60 DIAS DE CAIXAS E VENDAS REALISTAS (2 meses completos)
        produtos_ativos_venda = [p for p, w in zip(produtos_db, pesos_giro) if w > 0]
        pesos_ativos = [w for w in pesos_giro if w > 0]

        formas_comuns = [
            FormaPagamento.PIX,
            FormaPagamento.PIX,
            FormaPagamento.PIX,
            FormaPagamento.DINHEIRO,
            FormaPagamento.DINHEIRO,
            FormaPagamento.STONE_DEBITO,
            FormaPagamento.STONE_DEBITO,
            FormaPagamento.CIELO_DEBITO,
            FormaPagamento.STONE_CREDITO,
            FormaPagamento.CIELO_CREDITO,
        ]

        for offset in range(60, -1, -1):
            dia = hoje - timedelta(days=offset)
            sem = dia.weekday()  # 0=Seg ... 4=Sex, 5=Sáb, 6=Dom
            eh_hoje = offset == 0

            # Quantidade de vendas por dia de acordo com o ritmo de distribuidora de bebidas
            if eh_hoje:
                n_vendas = 16
            elif sem in (0, 1):  # Seg, Ter
                n_vendas = rnd.randint(12, 17)
            elif sem == 2:  # Qua (jogo de futebol à noite!)
                n_vendas = rnd.randint(18, 24)
            elif sem == 3:  # Qui
                n_vendas = rnd.randint(20, 26)
            elif sem == 4:  # Sex
                n_vendas = rnd.randint(32, 42)
            elif sem == 5:  # Sáb (pico!)
                n_vendas = rnd.randint(40, 52)
            else:  # Dom
                n_vendas = rnd.randint(24, 34)

            operador_turno = caixa_noite if sem in (4, 5) else caixa_dia
            if eh_hoje:
                operador_turno = dono

            fundo_abertura = Decimal("200.00")
            aberto_dt = _utc(dia, 9, rnd.randint(0, 15))
            caixa_turno = Caixa(
                usuario_id=operador_turno.id,
                status=StatusCaixa.ABERTO if eh_hoje else StatusCaixa.FECHADO,
                valor_abertura=float(fundo_abertura),
                aberto_em=aberto_dt,
            )
            db.add(caixa_turno)
            db.flush()

            dinheiro_vendas = Decimal("0")

            for _ in range(n_vendas):
                # Horário realista (concentrado 17h-22h na sexta/sábado, 11h-17h no domingo)
                if eh_hoje:
                    hora_v = rnd.choice([9, 10, 10, 11, 11, 12, 13, 14])
                elif sem in (4, 5):
                    hora_v = rnd.choices(
                        [10, 11, 12, 14, 15, 16, 17, 18, 19, 20, 21, 22],
                        weights=[2, 3, 4, 3, 4, 6, 10, 16, 22, 24, 20, 12],
                    )[0]
                elif sem == 6:
                    hora_v = rnd.choices(
                        [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
                        weights=[6, 14, 18, 16, 14, 12, 10, 8, 6, 4, 2],
                    )[0]
                else:
                    hora_v = rnd.choices(
                        [9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20, 21],
                        weights=[2, 3, 4, 5, 4, 5, 6, 10, 15, 18, 14, 8],
                    )[0]
                min_v = rnd.randint(0, 58)
                dt_venda = _utc(dia, hora_v, min_v)

                # Escolhe de 1 a 4 itens por venda
                qtd_itens = rnd.choices([1, 2, 3, 4], weights=[30, 42, 20, 8])[0]
                escolhidos = rnd.choices(produtos_ativos_venda, weights=pesos_ativos, k=qtd_itens)
                # Remove duplicados na mesma venda mantendo ordem
                vistos = set()
                itens_unicos = []
                for p in escolhidos:
                    if p.id not in vistos:
                        vistos.add(p.id)
                        itens_unicos.append(p)

                subtotal = Decimal("0")
                itens_obj = []
                for p in itens_unicos:
                    if p.unidade == Unidade.FARDO:
                        q = rnd.choices([1, 2, 3], weights=[70, 22, 8])[0]
                    elif p.preco_venda < 12:
                        q = rnd.choices([2, 4, 6, 12], weights=[35, 30, 25, 10])[0]
                    else:
                        q = rnd.choices([1, 2], weights=[82, 18])[0]
                    tot_item = (Decimal(str(p.preco_venda)) * Decimal(q)).quantize(Decimal("0.01"))
                    subtotal += tot_item
                    itens_obj.append(
                        ItemVenda(
                            produto_id=p.id,
                            descricao=p.nome,
                            quantidade=q,
                            preco_unitario=float(p.preco_venda),
                            custo_unitario=float(p.preco_custo),
                            total=float(tot_item),
                        )
                    )

                cli = rnd.choice(clientes_db) if rnd.random() < 0.22 else None
                forma = rnd.choice(formas_comuns)
                v = Venda(
                    caixa_id=caixa_turno.id,
                    usuario_id=operador_turno.id,
                    cliente_id=cli.id if cli else None,
                    cliente_nome=cli.nome if cli else None,
                    status=StatusVenda.FINALIZADA,
                    subtotal=float(subtotal),
                    total=float(subtotal),
                    criado_em=dt_venda,
                    finalizado_em=dt_venda,
                    documento_tipo=TipoDocumento.RECIBO,
                    fiscal_status=FiscalStatus.NAO_EMITIDO,
                )
                v.itens.extend(itens_obj)
                valor_rec = float(subtotal + Decimal("10.00")) if forma == FormaPagamento.DINHEIRO else None
                v.pagamentos.append(
                    Pagamento(
                        forma=forma,
                        valor=float(subtotal),
                        valor_recebido=valor_rec,
                        criado_em=dt_venda,
                    )
                )
                db.add(v)
                if forma == FormaPagamento.DINHEIRO:
                    dinheiro_vendas += subtotal

            # Vendas históricas antigas dos produtos parados (há 52 e 48 dias) para constarem como parados > 45d
            if offset == 52:
                licor = produtos_db[-3]
                v_par = Venda(
                    caixa_id=caixa_turno.id,
                    usuario_id=operador_turno.id,
                    status=StatusVenda.FINALIZADA,
                    subtotal=float(licor.preco_venda),
                    total=float(licor.preco_venda),
                    criado_em=_utc(dia, 19, 15),
                    finalizado_em=_utc(dia, 19, 15),
                )
                v_par.itens.append(ItemVenda(
                    produto_id=licor.id, descricao=licor.nome, quantidade=1,
                    preco_unitario=float(licor.preco_venda), custo_unitario=float(licor.preco_custo),
                    total=float(licor.preco_venda),
                ))
                v_par.pagamentos.append(Pagamento(forma=FormaPagamento.PIX, valor=float(licor.preco_venda)))
                db.add(v_par)
            elif offset == 48:
                tequila = produtos_db[-2]
                v_par2 = Venda(
                    caixa_id=caixa_turno.id,
                    usuario_id=operador_turno.id,
                    status=StatusVenda.FINALIZADA,
                    subtotal=float(tequila.preco_venda),
                    total=float(tequila.preco_venda),
                    criado_em=_utc(dia, 20, 40),
                    finalizado_em=_utc(dia, 20, 40),
                )
                v_par2.itens.append(ItemVenda(
                    produto_id=tequila.id, descricao=tequila.nome, quantidade=1,
                    preco_unitario=float(tequila.preco_venda), custo_unitario=float(tequila.preco_custo),
                    total=float(tequila.preco_venda),
                ))
                v_par2.pagamentos.append(Pagamento(forma=FormaPagamento.STONE_CREDITO, valor=float(tequila.preco_venda)))
                db.add(v_par2)

            # Sangrias / retiradas em dias de bom movimento
            sangria_total = Decimal("0")
            if dinheiro_vendas > Decimal("350.00") and not eh_hoje:
                val_sangria = Decimal("250.00")
                sangria_total += val_sangria
                db.add(
                    RetiradaCaixa(
                        caixa_id=caixa_turno.id,
                        usuario_id=operador_turno.id,
                        valor=float(val_sangria),
                        motivo="Alívio de gaveta para cofre",
                        criado_em=_utc(dia, 20, 30),
                    )
                )

            if not eh_hoje:
                esperado = fundo_abertura + dinheiro_vendas - sangria_total
                # Em 2 turnos do mês damos uma pequena diferença de caixa (-R$ 10,00 / +R$ 5,00) para enriquecer o Histórico de Caixas
                dif = Decimal("-10.00") if offset == 4 else Decimal("5.00") if offset == 11 else Decimal("0.00")
                caixa_turno.valor_fechamento = float(max(Decimal("0"), esperado + dif))
                caixa_turno.fechado_em = _utc(dia, 23, rnd.randint(5, 25))

        # 7. VENDAS NA CONFIANÇA (FIADO) E QUITAÇÕES PARCIAIS (para deixar saldo realista a receber)
        vendas_fiado_especificas = [
            (clientes_db[0], 9, 890.00, 400.00, "Pedido sexta-feira (fardos Brahma + gelo)"),
            (clientes_db[1], 6, 740.00, 300.00, "Reposição de fim de semana"),
            (clientes_db[2], 4, 520.00, 0.00, "Evento aniversário sábado"),
            (clientes_db[4], 12, 210.00, 0.00, "Compras da quinzena"),
            (clientes_db[6], 3, 460.00, 0.00, "Abastecimento bar da quadra"),
        ]
        for cli_f, dias_atras, valor_f, valor_pago, obs_f in vendas_fiado_especificas:
            dt_f = _utc(hoje - timedelta(days=dias_atras), 18, 20)
            vf = Venda(
                usuario_id=dono.id,
                cliente_id=cli_f.id,
                cliente_nome=cli_f.nome,
                status=StatusVenda.FINALIZADA,
                subtotal=valor_f,
                total=valor_f,
                criado_em=dt_f,
                finalizado_em=dt_f,
            )
            vf.itens.append(
                ItemVenda(
                    produto_id=produtos_db[1].id,
                    descricao=produtos_db[1].nome,
                    quantidade=int(valor_f // 70) or 1,
                    preco_unitario=round(valor_f / (int(valor_f // 70) or 1), 2),
                    custo_unitario=51.60,
                    total=valor_f,
                )
            )
            vf.pagamentos.append(Pagamento(forma=FormaPagamento.FIADO, valor=valor_f, criado_em=dt_f))
            db.add(vf)
            if valor_pago > 0:
                db.add(
                    QuitacaoFiado(
                        cliente_id=cli_f.id,
                        usuario_id=dono.id,
                        valor=valor_pago,
                        forma=FormaPagamento.PIX,
                        observacao=f"Pagamento parcial via Pix ({obs_f})",
                        criado_em=_utc(hoje - timedelta(days=max(1, dias_atras - 3)), 14, 10),
                    )
                )

        # 8. ENTRADAS DE ESTOQUE (Notas fiscais dos últimos 2 meses)
        entradas_hist = [
            (f_ambev, "48219", 3, "Entrega programada Ambev — lançada pelo Assistente de IA com confirmação do proprietário", [
                (produtos_db[2], 240, 2.89),
                (produtos_db[4], 120, 3.45),
                (produtos_db[7], 72, 7.80),
            ]),
            (f_heineken, "91042", 8, "Pedido quinzenal Heineken e Amstel", [
                (produtos_db[0], 120, 4.95),
                (produtos_db[1], 24, 51.60),
                (produtos_db[8], 144, 3.65),
            ]),
            (f_coca, "77310", 11, "Reposição refrigerantes e águas", [
                (produtos_db[16], 60, 7.85),
                (produtos_db[18], 96, 2.75),
                (produtos_db[21], 120, 1.15),
            ]),
            (f_destilados, "12089", 19, "Compra mensal de destilados e vinhos", [
                (produtos_db[23], 12, 76.00),
                (produtos_db[25], 8, 82.00),
                (produtos_db[27], 18, 31.20),
                (produtos_db[29], 18, 23.50),
            ]),
            (f_gelo, "00841", 5, "Entrega semanal de gelo cristal e coco", [
                (produtos_db[10], 50, 6.50),
                (produtos_db[11], 60, 2.10),
            ]),
        ]
        for forn_e, nf_e, dias_e, obs_e, itens_e in entradas_hist:
            dt_e = hoje - timedelta(days=dias_e)
            tot_e = sum(Decimal(str(q)) * Decimal(str(c)) for _, q, c in itens_e)
            ent = EntradaEstoque(
                fornecedor_id=forn_e.id,
                usuario_id=dono.id,
                nota_numero=nf_e,
                observacao=obs_e,
                total=float(tot_e),
                data_compra=dt_e,
                criado_em=_utc(dt_e, 10, 45),
            )
            for prod_e, qtd_e, custo_e in itens_e:
                ent.itens.append(
                    ItemEntrada(
                        produto_id=prod_e.id,
                        quantidade=qtd_e,
                        custo_unitario=custo_e,
                        total=float(Decimal(str(qtd_e)) * Decimal(str(custo_e))),
                    )
                )
            db.add(ent)

        # 9. CONTAS A PAGAR (Pagas nos últimos 2 meses + Vencendo nos próximos dias)
        contas_dados = [
            ("Boleto NF #48219 — Ambev S.A.", "Mercadoria (fornecedor)", "Ambev S.A.", 1669.20, hoje + timedelta(days=2), False, False, "Lançado via Assistente de IA na leitura da NF #48219"),
            ("Aluguel do Ponto Comercial e Depósito", "Aluguel", "Imobiliária Central", 3200.00, hoje + timedelta(days=4), False, True, "Contrato comercial loja + galpão"),
            ("Boleto NF #91042 — Heineken Brasil", "Mercadoria (fornecedor)", "Heineken Brasil", 2358.00, hoje + timedelta(days=6), False, False, "2ª parcela pedido quinzenal"),
            ("Internet Fibra 600Mb + Telefone Fixo", "Outros", "Vivo Empresas", 169.90, hoje + timedelta(days=9), False, True, "Débito / Pix"),
            ("Honorários Contabilidade Mensal", "Outros", "Exata Contabilidade", 550.00, hoje + timedelta(days=14), False, True, "Simples Nacional"),
            # Já pagas
            ("Energia Elétrica — Câmaras Frias e Loja", "Energia", "Concessionária de Energia", 1420.50, hoje - timedelta(days=18), True, True, "Pago via Pix"),
            ("Folha Salarial — Equipe de Caixa", "Funcionário", "Equipe Interna", 4600.00, hoje - timedelta(days=15), True, True, "Pagamento mensal"),
            ("Água e Saneamento", "Água", "Companhia de Saneamento", 198.40, hoje - timedelta(days=12), True, True, ""),
            ("Boleto Coca-Cola FEMSA NF #77310", "Mercadoria (fornecedor)", "Coca-Cola FEMSA", 873.00, hoje - timedelta(days=7), True, False, ""),
            ("Manutenção Preventiva Câmara Fria", "Outros", "Refrigeração Polar", 380.00, hoje - timedelta(days=24), True, False, "Limpeza de condensadores e gás"),
        ]
        for desc, cat, ben, val, venc, pago, rec, obs in contas_dados:
            db.add(
                ContaPagar(
                    descricao=desc,
                    categoria=cat,
                    beneficiario=ben,
                    valor=val,
                    vencimento=venc,
                    pago=pago,
                    pago_em=_utc(venc, 15, 0) if pago else None,
                    recorrente=rec,
                    observacao=obs,
                )
            )

        # 10. PATRIMÔNIO DA LOJA (Ativos Fixos)
        ativos_dados = [
            ("Câmara Fria Walk-in 12m³ (Motor Elgin)", "Refrigeração", 24500.00, hoje - timedelta(days=420), 10, 4000.00, EstadoAtivo.EM_USO, "Capacidade para 280 fardos/caixas"),
            ("Cervejeira Expositora Vertical Hussmann 550L #01", "Refrigeração", 6800.00, hoje - timedelta(days=380), 8, 1200.00, EstadoAtivo.EM_USO, "Corredor principal — regulada a -4°C"),
            ("Cervejeira Expositora Vertical Hussmann 550L #02", "Refrigeração", 6800.00, hoje - timedelta(days=380), 8, 1200.00, EstadoAtivo.EM_USO, "Corredor principal — regulada a -4°C"),
            ("Freezer Horizontal Dupla Ação 530L (Gelo)", "Refrigeração", 4200.00, hoje - timedelta(days=310), 7, 600.00, EstadoAtivo.EM_USO, "Armazenamento de gelo 5kg e gelo de coco"),
            ("Conjunto PDV Completo (PC + Leitor + Impressora Térmica)", "Informática", 3900.00, hoje - timedelta(days=290), 5, 400.00, EstadoAtivo.EM_USO, "Balcão de atendimento"),
            ("Empilhadeira Hidráulica Manual Paleteira 2,5t", "Logística", 2450.00, hoje - timedelta(days=350), 8, 300.00, EstadoAtivo.EM_USO, "Descarga de paletes Ambev/Heineken"),
        ]
        for nome_a, cat_a, val_a, dt_a, vida_a, res_a, est_a, obs_a in ativos_dados:
            db.add(
                AtivoFixo(
                    nome=nome_a,
                    categoria=cat_a,
                    valor_aquisicao=val_a,
                    data_aquisicao=dt_a,
                    vida_util_anos=vida_a,
                    valor_residual=res_a,
                    estado=est_a,
                    observacao=obs_a,
                )
            )

        # 11. INVENTÁRIOS (4 concluídos nos últimos 2 meses + 1 contagem cega EM ANDAMENTO hoje!)
        inventarios_fechados_cfg = [
            # (dias_atras, usuario, min_duracao, obs, divergencias: {idx_produto: delta_qtd})
            (
                52,
                dono,
                48,
                "Balanço geral do início do bimestre — depósito e salão",
                {2: -3, 10: -2, 18: -1},  # -3 Brahma lata, -2 Gelo 5kg, -1 Coca lata
            ),
            (
                38,
                gerente,
                35,
                "Conferência quinzenal de cervejeiras e fardos",
                {0: +2, 8: +1},  # +2 Heineken LN, +1 Amstel latão
            ),
            (
                24,
                dono,
                28,
                "Auditoria de destilados, whisky e importados (selo IPI)",
                {},  # 100% batido sem diferença
            ),
            (
                10,
                gerente,
                41,
                "Conferência mensal de câmara fria e bebidas de alto giro",
                {4: -2, 13: -1},  # -2 Spaten lata, -1 Red Bull
            ),
        ]

        for dias_inv, usr_inv, dur_min, obs_inv, divs_map in inventarios_fechados_cfg:
            dt_ini_inv = _utc(hoje - timedelta(days=dias_inv), 8, 30)
            dt_fim_inv = dt_ini_inv + timedelta(minutes=dur_min)
            inv_f = Inventario(
                usuario_id=usr_inv.id,
                status=StatusInventario.FECHADO,
                observacao=obs_inv,
                criado_em=dt_ini_inv,
                fechado_em=dt_fim_inv,
            )
            for idx_p, p_inv in enumerate(produtos_db):
                est_base = float(max(Decimal("12"), Decimal(str(p_inv.estoque)) + Decimal(rnd.randint(4, 20))))
                delta = float(divs_map.get(idx_p, 0))
                contado = max(0.0, est_base + delta)
                inv_f.itens.append(
                    ItemInventario(
                        produto_id=p_inv.id,
                        quantidade_sistema=est_base,
                        quantidade_contada=contado,
                        diferenca=contado - est_base,
                    )
                )
            db.add(inv_f)

        # Inventário #5 ABERTO (Contagem cega em andamento hoje: 24 de 32 produtos já contados = 75%)
        inv_aberto = Inventario(
            usuario_id=gerente.id,
            status=StatusInventario.ABERTO,
            observacao="Conferência semanal câmara fria e corredor de cervejas",
            criado_em=_utc(hoje, 8, 40),
            fechado_em=None,
        )
        for idx_p, p_inv in enumerate(produtos_db):
            est_sist = float(p_inv.estoque)
            # Os primeiros 24 produtos já foram contados; 8 ainda faltam contar (quantidade_contada=None)
            if idx_p < 24:
                delta_ab = -1.0 if idx_p in (2, 16) else 0.0
                cont_ab = max(0.0, est_sist + delta_ab)
                inv_aberto.itens.append(
                    ItemInventario(
                        produto_id=p_inv.id,
                        quantidade_sistema=est_sist,
                        quantidade_contada=cont_ab,
                        diferenca=None,  # contagem cega: diferença oficial grava no fechamento
                    )
                )
            else:
                inv_aberto.itens.append(
                    ItemInventario(
                        produto_id=p_inv.id,
                        quantidade_sistema=est_sist,
                        quantidade_contada=None,
                        diferenca=None,
                    )
                )
        db.add(inv_aberto)

        db.add_all([
            RetiradaDono(
                usuario_id=dono.id,
                valor=2500.00,
                origem="banco",
                observacao="Adiantamento de pró-labore mensal (Pix)",
                criado_em=_utc(hoje - timedelta(days=5), 17, 0),
            ),
            RetiradaDono(
                usuario_id=dono.id,
                valor=1500.00,
                origem="gaveta",
                observacao="Retirada do proprietário aprovada via Assistente de IA",
                criado_em=_utc(hoje - timedelta(days=2), 19, 30),
            ),
        ])

        # 12. CONVERSAS DA IA COM AÇÕES CONFIRMADAS PELO PROPRIETÁRIO
        # Criamos 5 conversas completas que aparecem em "Conversas anteriores" e em "Sistema > Conversas da IA"
        conversas_roteiro = [
            {
                "usuario": dono,
                "titulo": "Nota Ambev #48219: entrada de estoque + boleto",
                "dias_atras": 3,
                "hora": 10,
                "min": 42,
                "proposta_titulo": "Entrada de mercadoria — nota 48219 + Conta a Pagar",
                "proposta_resumo": {
                    "titulo": "Entrada de mercadoria — nota 48219",
                    "descricao": "Fornecedor: Ambev S.A. — CD Direto · Total R$ 1.669,20",
                    "itens": [
                        {"acao": 0, "texto": "Brahma Duplo Malte Lata 350ml: 240 un × R$ 2,89 = R$ 693,60 (20 fardos × 12 un)"},
                        {"acao": 1, "texto": "Spaten Puro Malte Lata 350ml: 120 un × R$ 3,45 = R$ 414,00 (10 fardos × 12 un)"},
                        {"acao": 2, "texto": "Cerveja Original 600ml: 72 un × R$ 7,80 = R$ 561,60 (6 caixas × 12 un)"},
                    ],
                },
                "mensagens": [
                    ("user", "[Documento: NF_Ambev_48219.xml] Chegou a entrega da Ambev, confere os itens e já prepara a entrada e o boleto pra vencer daqui a 5 dias."),
                    ("assistant", "[Proposta] Entrada de mercadoria — nota 48219 — Fornecedor: Ambev S.A. — CD Direto · Total R$ 1.669,20 (240 un Brahma Duplo Malte 350ml, 120 un Spaten 350ml, 72 un Original 600ml) + Boleto R$ 1.669,20."),
                    ("user", "Confirmado! Já atualizou o estoque e o contas a pagar?"),
                    ("assistant", "Sim, Carlos! Após a sua confirmação no cartão, executei as duas ações:\n• Entrada #1 registrada: +240 un de Brahma Duplo Malte, +120 un de Spaten e +72 un de Original 600ml.\n• Conta a pagar lançada: Boleto NF #48219 — Ambev S.A. no valor de R$ 1.669,20."),
                ],
                "auditoria": ("assistente_ia.proposta_confirmada", "Entrada de mercadoria — nota 48219 (R$ 1.669,20) confirmada pelo proprietário"),
            },
            {
                "usuario": dono,
                "titulo": "Promoção relâmpago para girar destilados parados",
                "dias_atras": 2,
                "hora": 16,
                "min": 15,
                "proposta_titulo": "Reajustar preço de 2 produto(s) (-12%)",
                "proposta_resumo": {
                    "titulo": "Reajustar preço de 2 produto(s) (-12%)",
                    "descricao": "Ação confirmada pelo proprietário.",
                    "itens": [
                        {"acao": 0, "texto": "Licor 43 Diego Zamora 700ml: R$ 179,90 → R$ 159,90"},
                        {"acao": 1, "texto": "Tequila José Cuervo Especial Gold 750ml: R$ 149,90 → R$ 134,90"},
                    ],
                },
                "mensagens": [
                    ("user", "Quais bebidas estão paradas há mais de 40 dias prendendo dinheiro no estoque?"),
                    ("assistant", "Analisei os últimos 60 dias e encontrei 3 destilados sem giro recente:\n• Licor 43 Diego Zamora 700ml: 8 un paradas (R$ 912,00 empatados)\n• Tequila José Cuervo Gold 750ml: 7 un paradas (R$ 672,00 empatados)\n• Aperitivo Campari 900ml: 10 un paradas (R$ 450,00 empatados)\n\nQuer que eu prepare uma redução promocional de ~12% no Licor 43 e na Tequila mantendo margem positiva?"),
                    ("user", "Pode preparar esse reajuste no Licor 43 e na Tequila para eu aprovar."),
                    ("assistant", "[Proposta] Reajustar preço de 2 produto(s) (-12%) — Licor 43 (R$ 179,90 → R$ 159,90) e Tequila José Cuervo (R$ 149,90 → R$ 134,90)."),
                    ("user", "Pronto, aceitei a alteração no cartão."),
                    ("assistant", "Preços atualizados na frente de caixa após seu aceite:\n• Licor 43 700ml: R$ 159,90 (margem bruta preservada de 28,7%)\n• Tequila José Cuervo 750ml: R$ 134,90 (margem bruta preservada de 28,8%)"),
                ],
                "auditoria": ("assistente_ia.proposta_confirmada", "Reajuste promocional de 2 destilados parados confirmado pelo proprietário"),
            },
            {
                "usuario": dono,
                "titulo": "Baixa de pagamento Pix na Confiança — Espetinho do Alemão",
                "dias_atras": 1,
                "hora": 14,
                "min": 20,
                "proposta_titulo": "Receber R$ 400,00 de Espetinho do Alemão",
                "proposta_resumo": {
                    "titulo": "Receber R$ 400,00 de Espetinho do Alemão",
                    "descricao": "Forma: PIX · Saldo devedor passa de R$ 890,00 para R$ 490,00",
                },
                "mensagens": [
                    ("user", "O Espetinho do Alemão acabou de mandar um Pix de R$ 400,00 para abater da Confiança. Prepara a baixa pra mim."),
                    ("assistant", "[Proposta] Receber R$ 400,00 de Espetinho do Alemão — Forma: PIX · Saldo devedor: R$ 890,00 → R$ 490,00."),
                    ("user", "Confirmado! Quanto ele ainda resta devendo agora?"),
                    ("assistant", "Quitação de R$ 400,00 registrada após a sua confirmação! O saldo atualizado do Espetinho do Alemão na Confiança agora é de R$ 490,00 (dentro do limite de R$ 1.200,00)."),
                ],
                "auditoria": ("assistente_ia.proposta_confirmada", "Quitação de Confiança R$ 400,00 (Espetinho do Alemão) confirmada pelo proprietário"),
            },
            {
                "usuario": dono,
                "titulo": "Alerta de estoque baixo para sexta e sábado",
                "dias_atras": 0,
                "hora": 9,
                "min": 15,
                "proposta_titulo": None,
                "proposta_resumo": None,
                "mensagens": [
                    ("user", "O que corre risco de acabar neste fim de semana se eu não pedir hoje?"),
                    ("assistant", "Pelo ritmo das últimas 8 sextas e sábados, estes 5 produtos precisam de compra imediata:\n\n1. Carvão Vegetal Eucalipto 4kg — ZERADO (mínimo: 12 sacos)\n2. Gelo Cubo Cristal 5kg — só 4 pacotes (mínimo: 30 pacotes)\n3. Fardo Brahma Duplo Malte 350ml c/ 12 — só 3 fardos (mínimo: 15 fardos)\n4. Red Bull Energy Drink 250ml — 9 latas (mínimo: 36 latas)\n5. Heineken Long Neck 330ml — 14 garrafas (mínimo: 48 garrafas)\n\nQuando quiser, basta clicar na sugestão de reposição que eu preparo a entrada para você confirmar."),
                ],
                "auditoria": None,
            },
            {
                "usuario": caixa_dia,
                "titulo": "Consulta de preço e estoque de barril / fardo",
                "dias_atras": 1,
                "hora": 11,
                "min": 5,
                "proposta_titulo": None,
                "proposta_resumo": None,
                "mensagens": [
                    ("user", "Quanto tá saindo o fardo da Heineken lata e quantas unidades temos?"),
                    ("assistant", "O Fardo Heineken Lata 350ml c/ 12 un está R$ 69,90 (sai a R$ 5,82 por lata). Temos 18 fardos disponíveis em estoque no momento."),
                ],
                "auditoria": None,
            },
        ]

        for item_c in conversas_roteiro:
            dt_c = _utc(hoje - timedelta(days=item_c["dias_atras"]), item_c["hora"], item_c["min"])
            conv = ConversaIA(
                usuario_id=item_c["usuario"].id,
                titulo=item_c["titulo"],
                criado_em=dt_c,
                atualizado_em=dt_c + timedelta(minutes=4),
            )
            db.add(conv)
            db.flush()

            prop_id = None
            if item_c["proposta_titulo"]:
                prop_id = secrets.token_hex(16)
                db.add(
                    PropostaIA(
                        id=prop_id,
                        usuario_id=item_c["usuario"].id,
                        acoes=[{"tipo": "demo.confirmada", "parametros": {}}],
                        resumo=item_c["proposta_resumo"],
                        status="confirmada",
                        criado_em=dt_c + timedelta(minutes=1),
                        expira_em=dt_c + timedelta(minutes=16),
                        decidido_em=dt_c + timedelta(minutes=2),
                    )
                )

            for idx_m, (role_m, txt_m) in enumerate(item_c["mensagens"]):
                db.add(
                    MensagemIA(
                        usuario_id=item_c["usuario"].id,
                        role=role_m,
                        conteudo=txt_m,
                        conversa_id=conv.id,
                        proposta_id=prop_id if (role_m == "assistant" and txt_m.startswith("[Proposta]")) else None,
                        criado_em=dt_c + timedelta(minutes=idx_m),
                    )
                )

            if item_c["auditoria"]:
                acao_aud, det_aud = item_c["auditoria"]
                db.add(
                    LogAuditoria(
                        criado_em=dt_c + timedelta(minutes=2),
                        usuario_id=item_c["usuario"].id,
                        usuario_nome=item_c["usuario"].nome,
                        acao=acao_aud,
                        detalhe=det_aud,
                        ip="127.0.0.1",
                    )
                )

        # 13. MEMÓRIA DA IA (Lições aprovadas pelo proprietário + Sinais de conversão de fardo/caixa)
        db.add_all([
            LicaoIA(
                tipo="conversao",
                modulo="assunto",
                assunto="fornecedores",
                texto="CX BRAHMA DM 350ML C/12 = 12 un de Brahma Duplo Malte Lata 350ml",
                dados={"produto_id": produtos_db[2].id, "fator": 12, "nome_na_nota": "CX BRAHMA DM 350ML C/12", "fornecedor_id": f_ambev.id},
                situacao="ativa",
                criado_por_id=dono.id,
                aprovado_por_id=dono.id,
                aprovado_em=_utc(hoje - timedelta(days=20), 11, 0),
                criado_em=_utc(hoje - timedelta(days=20), 11, 0),
            ),
            LicaoIA(
                tipo="conversao",
                modulo="assunto",
                assunto="fornecedores",
                texto="PACK HEINEKEN LN 330ML 6X4 = 24 un de Heineken Long Neck 330ml",
                dados={"produto_id": produtos_db[0].id, "fator": 24, "nome_na_nota": "PACK HEINEKEN LN 330ML 6X4", "fornecedor_id": f_heineken.id},
                situacao="ativa",
                criado_por_id=dono.id,
                aprovado_por_id=dono.id,
                aprovado_em=_utc(hoje - timedelta(days=15), 14, 0),
                criado_em=_utc(hoje - timedelta(days=15), 14, 0),
            ),
            LicaoIA(
                tipo="texto",
                modulo="loja",
                texto="Nas sextas e sábados o giro de Gelo 5kg e Heineken triplica após as 18h; priorizar alerta preventivo na quinta-feira.",
                situacao="ativa",
                criado_por_id=dono.id,
                aprovado_por_id=dono.id,
                aprovado_em=_utc(hoje - timedelta(days=10), 16, 0),
                criado_em=_utc(hoje - timedelta(days=10), 16, 0),
            ),
            SinalIA(
                tipo="conversao_sugerida",
                usuario_id=dono.id,
                pergunta="Leitura automática NF Coca-Cola FEMSA",
                resposta="FARDO COCA LATA 350ML C/12 → 12 un de Coca-Cola Lata 350ml",
                dados={"produto_id": produtos_db[18].id, "fator": 12, "nome_na_nota": "FARDO COCA LATA 350ML C/12", "fornecedor_id": f_coca.id},
                tratado=False,
                criado_em=_utc(hoje - timedelta(days=2), 11, 30),
            ),
        ])

        # 14. USO DA IA (Telemetria de 30 dias para a aba Sistema > Uso da IA ficar rica)
        tarefas_ex = [
            ("agente_leve", "groq", "openai/gpt-oss-120b", "leve"),
            ("agente_pesado", "groq", "openai/gpt-oss-120b", "verbo_alteracao"),
            ("extracao_texto", "groq", "openai/gpt-oss-120b", "leve"),
            ("funcionario", "groq", "openai/gpt-oss-20b", "leve"),
        ]
        for d_u in range(29, -1, -1):
            dia_u = hoje - timedelta(days=d_u)
            n_chamadas = rnd.randint(4, 14) if d_u > 0 else 8
            for _ in range(n_chamadas):
                tar, prov, mod, mot = rnd.choice(tarefas_ex)
                db.add(
                    UsoIA(
                        criado_em=_utc(dia_u, rnd.randint(9, 21), rnd.randint(0, 59)),
                        usuario_id=dono.id if tar != "funcionario" else caixa_dia.id,
                        tarefa=tar,
                        provedor=prov,
                        modelo=mod,
                        reserva=False,
                        sucesso=True,
                        duracao_ms=rnd.randint(420, 1350),
                        rodadas=1,
                        tokens_entrada=rnd.randint(650, 1800),
                        tokens_saida=rnd.randint(140, 480),
                        custo_usd=0.0,
                        motivo=mot,
                    )
                )

        # 15. LOGS DE AUDITORIA E CHAMADO DE SUPORTE
        logs_ex = [
            (hoje, 9, 5, dono, "login", "Acesso ao painel administrativo"),
            (hoje, 9, 10, dono, "caixa.abrir", "abertura 200.0"),
            (hoje, 9, 15, dono, "assistente_ia.perguntar", "O que corre risco de acabar neste fim de semana? | assuntos: estoque, reposicao"),
            (hoje - timedelta(days=1), 14, 21, dono, "fiado.quitacao", "cliente #1 Espetinho do Alemão valor 400.0 (via assistente de IA)"),
            (hoje - timedelta(days=2), 16, 17, dono, "produto.editar", "#31 Licor 43 Diego Zamora 700ml: preço R$ 179,90 -> R$ 159,90 (via assistente de IA)"),
            (hoje - timedelta(days=2), 19, 30, dono, "lucro.retirada_dono", "R$ 1500.00 da gaveta - Retirada aprovada pelo proprietário"),
            (hoje - timedelta(days=3), 10, 44, dono, "entrada.criar", "#1 total 1669.20 (via assistente de IA)"),
            (hoje - timedelta(days=3), 10, 44, dono, "conta_pagar.criar", "#1 Boleto NF #48219 — Ambev S.A. (via assistente de IA)"),
        ]
        for d_l, h_l, m_l, usr_l, acao_l, det_l in logs_ex:
            db.add(
                LogAuditoria(
                    criado_em=_utc(d_l, h_l, m_l),
                    usuario_id=usr_l.id,
                    usuario_nome=usr_l.nome,
                    acao=acao_l,
                    detalhe=det_l,
                    ip="127.0.0.1",
                )
            )

        db.add(
            ChamadoSuporte(
                usuario_id=dono.id,
                usuario_nome=dono.nome,
                texto="Gostaria de configurar a impressão do QR Code do Instagram da loja no rodapé do cupom de 80mm.",
                pagina_origem="/admin/configuracoes",
                criado_em=_utc(hoje - timedelta(days=6), 15, 20),
                enviado_em=_utc(hoje - timedelta(days=6), 15, 20),
                tentativas=1,
                resolvido_em=_utc(hoje - timedelta(days=5), 10, 0),
                resolvido_por="Suporte Técnico",
            )
        )

        db.commit()

    print(f"[OK] Banco de demonstracao criado em: {DB_PATH}")
    return DB_PATH


if __name__ == "__main__":
    gerar_banco(forcar=True)

