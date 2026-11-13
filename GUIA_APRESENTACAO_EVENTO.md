# Guia Rápido de Apresentação no Evento — **"SUA MARCA"**

Tudo o que foi criado para a sua demonstração comercial está isolado dentro desta pasta (`apresentacao_evento/`), sem alterar absolutamente nada do sistema ou do banco de dados do seu cliente real.

---

## Como abrir agora no evento

### Opção 1 — Sistema Real Interativo (Modo Demo Completo)
Ideal para mostrar o sistema funcionando por completo no seu notebook (filtros, vendas ao vivo, gaveta, Assistente de IA gravando ações de verdade no banco de demonstração):
1. Dê duplo clique em [`INICIAR_SISTEMA_DEMO.bat`](./INICIAR_SISTEMA_DEMO.bat) (ou rode `python apresentacao_evento/rodar_demo.py`).
2. O navegador abrirá automaticamente já logado como **Carlos Eduardo (Proprietário)** em `http://127.0.0.1:8050/demo-entrar`.
3. Se quiser resetar o banco de 2 meses do zero após várias demonstrações, rode:
   ```powershell
   python apresentacao_evento/rodar_demo.py --reset
   ```

### Opção 2 — Telas HTML Estáticas Navegáveis (Sem Servidor)
Ideal para abrir instantaneamente em qualquer computador/tablet ou deixar como backup à prova de falhas:
1. Dê duplo clique em [`ABRIR_TELAS_ESTATICAS.html`](./ABRIR_TELAS_ESTATICAS.html) (ou abra [`telas_estaticas/index.html`](./telas_estaticas/index.html)).
2. Todas as telas do menu lateral estão interligadas, com gráficos dos 2 meses, modo claro/escuro e **simulador interativo do Assistente de IA funcionando direto no navegador**.

---

## Roteiro da Tela de Assistente de IA (Perguntas e Ações Prontas)

Ao abrir **Apoio › Assistente IA** no menu lateral:
- Os botões de **Sugestões** já trazem as perguntas e pedidos prontos (basta **clicar em qualquer botão** que ele envia na hora, ou **digitar livremente** no campo!).
- Funciona **100% offline** (não depende do Wi-Fi do evento).

### 1. Perguntas para digitar ou clicar ao vivo (Responde na hora com dados de 60 dias)
Você pode digitar exatamente como combinamos (ou clicar nos chips):
- **`Qual foi o meu faturamento essa semana?`**
  → Mostra o faturamento dos últimos 7 dias, comparativo percentual com a semana anterior, lucro líquido descontando custo e taxas de maquininha, ticket médio e o dia de pico (Sábado à noite).
- **`Qual o faturamento e o lucro deste mês?`** (ou *`faturamento do mes`*)
  → Mostra o fechamento dos últimos 30 dias + comparativo do mês fechado vs. parcial do mês atual + divisão por Pix, Dinheiro, Cartão e Confiança.
- **`Qual produto está em estoque baixo?`**
  → Lista os produtos críticos calculados pelo giro real de 30 dias (*Carvão 4kg zerado, Gelo 5kg com 4 pacotes, Fardo Brahma Duplo Malte com 3 fardos, Red Bull com 9 latas, Heineken Long Neck com 14 un*) e o custo estimado de reposição.
- **`Quais foram os produtos mais vendidos nos últimos 60 dias?`**
  → Ranking dos 7 campeões de faturamento e margem no bimestre.
- **`Quais produtos estão parados prendendo dinheiro?`**
  → Mostra os destilados encalhados há mais de 45 dias (*Licor 43, Tequila José Cuervo, Campari*) e quanto dinheiro está parado na prateleira.
- **`Quem está devendo na Confiança?`**
  → Lista os clientes da caderneta (*Espetinho do Alemão, Bar Recanto, Rodrigo Eventos...*) com saldo aberto e limite.
- **`Quais contas a pagar vencem nos próximos dias?`**
  → Lista boletos de fornecedores (Ambev, Heineken), aluguel e despesas fixas a vencer.

### 2. Pedidos de Ação com Confirmação do Proprietário (Cartão Interativo ao Vivo)
Clique ou peça qualquer um destes para mostrar o **cartão de proposta com dupla checagem (`Confirmar` / `Cancelar`)**:
1. **Reposição de Estoque:**
   *`Repor estoque: entrada de 15 fardos de Brahma Duplo Malte a R$ 37,90 e 30 pacotes de Gelo 5kg a R$ 6,50 da Ambev`*
   → Abre o cartão com lote, validade, conversão de fardos e total da nota para você clicar em **Confirmar** na frente do cliente.
2. **Promoção para Girar Estoque Parado:**
   *`Criar promoção: baixar em 10% o preço do Licor 43 e da Tequila José Cuervo que estão parados`*
   → Mostra o cartão `de → para` com caixas de seleção individuais por produto.
3. **Reajuste de Preço por Marca:**
   *`Reajustar em +5% o preço das cervejas Heineken com arredondamento para R$ 0,50`*
4. **Lançamento de Despesa:**
   *`Lançar conta de energia elétrica de R$ 1.480,00 com vencimento para daqui a 5 dias`*
5. **Baixa de Fiado / Confiança via Pix:**
   *`Registrar pagamento de R$ 350,00 no Pix da Confiança do Espetinho do Alemão`*

---

## Histórico de Conversas e Auditoria da IA (Já populados)

Para mostrar ao cliente que **tudo o que a IA faz na loja fica registrado e auditado**:
1. No topo do **Assistente IA**, clique em **`Conversas anteriores · 5`**, ou vá em **`Configurações › Sistema › Conversas da IA`**:
   - **Nota Ambev #48219: entrada de estoque + boleto** *(com aceite do dono)*
   - **Promoção relâmpago para girar destilados parados** *(com aceite do dono)*
   - **Baixa de pagamento Pix na Confiança — Espetinho do Alemão** *(com aceite do dono)*
   - **Alerta de estoque baixo para sexta e sábado**
   - **Consulta de preço e estoque de fardo pelo operador de caixa**
2. Em **`Configurações › Sistema › Memória da IA`**:
   - Mostra como a IA aprendeu as conversões de embalagens dos fornecedores (*ex.: `CX BRAHMA DM 350ML C/12 = 12 un`*, *`PACK HEINEKEN LN 6X4 = 24 un`*) e um sinal novo aguardando aprovação de 1 clique do proprietário.
3. Em **`Configurações › Sistema › Logs`**:
   - Mostra no registro de auditoria as ações gravadas com a tag `(via assistente de IA)` após confirmação do proprietário.

