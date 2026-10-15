Calculadora Interativa de Custo de Frete

Aplicação de portfólio para estimar custos de frete com base em uma tabela de regras editável. O usuário informa peso, distância, modal, tipo de carga e adicionais; a aplicação calcula o preço estimado, explica cada componente e permite exportar o resultado.

Importante: todas as regras e cotações são fictícias. Esta ferramenta é educacional e não representa cotação comercial.

Funcionalidades
Interface web simples com Streamlit.
Quatro modais: rodoviário, aéreo, marítimo e ferroviário.
Quatro tipos de carga: geral, frágil, refrigerada e perigosa.
Tabela de regras separada do código (data/tabela_regras_frete.csv).
Cálculo transparente com taxa fixa, peso taxável, distância, combustível, manuseio, seguro, urgência, pedágios, adicional manual, frete mínimo e desconto.
Peso cubado configurado em 200 kg/m³; o peso taxável é o maior entre peso real e cubado.
Quebra detalhada dos componentes, tabela de regras e gráfico.
Exportação da estimativa para CSV e JSON.
Opção de salvar estimativas num histórico local.
Histórico de 180 cotações fictícias para demonstração.
Validação de entradas e testes automatizados.
Fórmula de referência
Subtotal base = taxa fixa + (peso taxável × taxa/kg) + (distância × taxa/km)

Ao subtotal base são adicionados combustível, manuseio, seguro, urgência, pedágios e adicionais. Aplica-se o frete mínimo; por fim, aplica-se o desconto negociado.

Estrutura
  calculadora_custo_frete_streamlit/
    ├── data/
    │   ├── tabela_regras_frete.csv
    │   └── historico_cotacoes_ficticio.csv
    ├── docs/
    ├── outputs/
    ├── src/
    │   ├── app.py
    │   └── frete.py
    ├── tests/
    │   └── test_frete.py
    ├── requirements.txt
    └── README.md
Como executar localmente
Requer Python 3.10+.

python -m venv .venv
Windows:
.venv\Scripts\activate
macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run src/app.py
O navegador abrirá a aplicação localmente. Para executar os testes:

python -m unittest discover -s tests -v
Como personalizar
Edite data/tabela_regras_frete.csv. Cada combinação modal + tipo de carga deve aparecer uma única vez. As colunas de preço são ilustrativas; substitua-as por regras aprovadas antes de qualquer uso operacional.

Limitações e cuidados
Valores e regras fictícios, não são tarifas reais.
O cálculo não contempla todos os fatores possíveis (tributos, restrições de rota, dimensões específicas, janela de entrega, sazonalidade, capacidade, taxas portuárias, Incoterms ou negociação individual).
O fator de cubagem de 200 kg/m³ é apenas uma premissa de demonstração e deve ser parametrizado conforme modal e contrato.
O histórico salvo em CSV é local; não é adequado para múltiplos usuários concorrentes sem banco de dados.
Não usar para emitir preço vinculante sem validação comercial.
Ideias de evolução
Cadastro de transportadoras e contratos.
Regras por região, faixa de peso e faixa de distância.
Comparativo entre transportadoras.
Dashboard de margens e cenários.
Persistência em SQLite/PostgreSQL.
Deploy no Streamlit Community Cloud.
Narrativa para entrevista
“Criei uma calculadora interativa em Streamlit para padronizar uma estimativa de frete. Separei as regras comerciais da interface, detalhei a composição do preço, validei os inputs e incluí exportação e histórico local. Isso demonstra como transformar uma regra operacional em ferramenta reproduzível e auditável.”

Licença
Uso educacional/portfólio. Inclua uma licença aberta se quiser definir formalmente os termos de reutilização.
