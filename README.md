# SUA MARCA — Sistema de Gestão & PDV com Inteligência Artificial

> Ambiente de demonstração comercial interativo, 100% white-label, pronto para apresentações a clientes e eventos.

🌐 **Demonstração Online no Ar:** [https://demo.optimati.com.br](https://demo.optimati.com.br)

---

## 🎯 Sobre o Projeto

Este repositório contém a versão de demonstração de um sistema completo de gestão comercial e frente de caixa (PDV) com inteligência artificial integrada, populado com **60 dias de dados reais simulados** (baseado em comércio de bebidas / varejo).

O projeto é **100% agnóstico e white-label**, configurado com a marca genérica **"SUA MARCA"** e paleta visual moderna padrão SaaS (Dark Navy, Branco Puro, Azul Tecnológico e Laranja Coral).

---

## 🚀 Módulos em Destaque

1. **Landing Page Comercial (`landing.html` / `index.html`)**
   * Apresentação visual da solução para prospecção de clientes.
   * Simulador interativo do Assistente de IA no próprio banner.
   * Acesso rápido com 1 clique a qualquer módulo do sistema.

2. **Painel de Lucro Real (`painel.html`)**
   * Faturamento diário, vendas, ticket médio e margem líquida calculada (descontando custo de mercadoria e taxas de maquininha).
   * Gráficos dinâmicos de faturamento dos últimos 7 dias e do mês.
   * Filtros rápidos entre **Hoje**, **Ontem**, **7 dias** e **Mês**.

3. **Assistente IA com Copiloto (`assistente.html`)**
   * Simulador interativo com botões rápidos de perguntas e respostas imediatas.
   * Preparação de cartões de ação (reposição de estoque, reajuste de preços, baixa de fiado) com **dupla confirmação humana do proprietário**.

4. **Frente de Caixa / PDV (`venda.html`)**
   * Operação rápida por teclado (atalhos de F1 a F9).
   * Leitor de código de barras e seleção de formas de pagamento (Pix, Dinheiro, Cartão, Confiança).

5. **Controle de Caixa & Gaveta (`caixa.html`)**
   * Abertura de turno com fundo inicial.
   * Simulação funcional de **Fechamento de Caixa com conferência cega** e comprovante emitido na tela.
   * Registro de sangrias e retiradas do proprietário.

6. **Relatórios e Inteligência Comercial (`relatorio.html`)**
   * Gráfico de barras diário com identificação automática do melhor dia de vendas.
   * Mapa de calor (heatmap) dos dias da semana e horários de maior fluxo.
   * Divisão percentual das formas de pagamento.

---

## 💻 Como Rodar

### Opção 1: Versão Estática (Sem Servidor)
Basta abrir o arquivo [`ABRIR_TELAS_ESTATICAS.html`](./ABRIR_TELAS_ESTATICAS.html) ou entrar na pasta [`telas_estaticas/index.html`](./telas_estaticas/index.html) diretamente em qualquer navegador (Chrome, Edge, Safari, Firefox) ou tablet/celular. Não necessita de Python, Node.js ou instalação.

### Opção 2: Servidor Local Interativo (Python)
Para rodar a aplicação via servidor local:

```bash
# Executa a aplicação de demonstração na porta 8050
python rodar_demo.py
```

O navegador abrirá automaticamente em `http://127.0.0.1:8050`.

---

## 📁 Estrutura de Arquivos

```text
├── telas_estaticas/           # Páginas HTML estáticas prontas para deploy web
│   ├── static/                # Folhas de estilo (style.css), fontes e logos
│   │   ├── css/               # Estilos com suporte a Tema Claro e Escuro
│   │   ├── img/               # Logotipos e ícones padrão "SUA MARCA"
│   │   └── vendor/            # Bibliotecas (Chart.js, HTMX)
│   ├── index.html             # Landing Page comercial oficial
│   ├── painel.html            # Dashboard executivo do proprietário
│   ├── assistente.html        # Chat com simulação do Assistente IA
│   ├── venda.html             # Frente de caixa (PDV)
│   ├── caixa.html             # Controle de gaveta e fechamento de turno
│   └── relatorio.html         # Relatório de vendas e mapa de calor
├── ABRIR_TELAS_ESTATICAS.html # Atalho rápido para abertura da demonstração
├── rodar_demo.py              # Inicializador da demo local via Python
├── gerar_dados_demo.py        # Gerador do banco de 60 dias de dados simulados
├── demo_bebidas.db            # Banco SQLite populado para a demonstração
├── .gitignore                 # Arquivos ignorados pelo Git
└── README.md                  # Este documento
```

---

## 🎨 Paleta de Cores Padrão SaaS

* **Fundo Claro:** `#F4F6F9` (Cinza gelo)
* **Cards & Superfícies:** `#FFFFFF` (Branco puro com elevação sutil)
* **Menu Lateral & Dark Mode:** `#0B1120` / `#1E293B` (Dark Navy)
* **Cor Primária & Gráficos:** `#0D6EFD` (Azul Tecnológico)
* **Destaques & Ações:** `#F97316` (Laranja Coral)

