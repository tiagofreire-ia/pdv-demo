# Bibliotecas de terceiros servidas pelo próprio app

O balcão não pode depender da internet nem de um site externo. Estes arquivos vieram das CDNs
abaixo em 17/10/2026, conferidos contra o hash publicado pela própria CDN antes de entrar aqui.
`tests/test_051_revisao.py` confere o SHA-384 de cada um: qualquer alteração no arquivo faz o teste falhar.
Para atualizar: baixar a versão nova, conferir o hash publicado, trocar o arquivo, o nome nos templates e o hash abaixo.

| Arquivo | Origem | SHA-384 (base64) |
|---|---|---|
| htmx-2.0.3.min.js | https://cdnjs.cloudflare.com/ajax/libs/htmx/2.0.3/htmx.min.js (licença 0BSD) | 0895/pl2MU10Hqc6jd4RvrthNlDiE9U1tWmX7WRESftEDRosgxNsQG/Ze9YMRzHq |
| chart-4.5.1.umd.min.js | https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.5.1/chart.umd.min.js (licença MIT) | jb8JQMbMoBUzgWatfe6COACi2ljcDdZQ2OxczGA3bGNeWe+6DChMTBJemed7ZnvJ |
| zxing-0.23.0.min.js | https://cdn.jsdelivr.net/npm/@zxing/library@0.23.0/umd/index.min.js (licença Apache-2.0) | 0ASr5PEWAMtTnWsn0PzKmioHVDA4+QqFiJr94io/0DCrGP6E1gRAmbO6O8y5WZW9 |
