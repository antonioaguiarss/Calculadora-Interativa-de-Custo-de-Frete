🚚 Calculadora Interativa de Custo de Frete

Aplicação web que estima o custo de um frete a partir de uma tabela de regras editável. Você informa os dados do envio (peso, distância, modal, tipo de carga e adicionais) e a calculadora mostra o preço estimado, explica de onde vem cada parte do valor e permite exportar o resultado.

⚠️ Projeto educacional. Todas as regras, tarifas e cotações são fictícias. Esta ferramenta não substitui uma cotação comercial.

Por que este projeto existe?

Estimativas de frete muitas vezes ficam em planilhas com regras espalhadas, e quem recebe o valor final nem sempre sabe como ele foi calculado. Esta calculadora padroniza o cálculo em etapas visíveis e mantém as regras de preço num arquivo separado do código, para que possam ser revisadas e alteradas sem programar.

Funcionalidades
Interface web simples, feita com Streamlit.
4 modais de transporte: rodoviário, aéreo, marítimo e ferroviário.
4 tipos de carga: geral, frágil, refrigerada e perigosa.
Regras separadas do código: todos os preços ficam em data/tabela_regras_frete.csv.
Cálculo transparente: a tela mostra cada componente do preço, a regra aplicada e um gráfico da composição do valor.
Exportação da estimativa em CSV e JSON.
Histórico local para salvar estimativas, já com 180 cotações fictícias para demonstração.
Validação de entradas e testes automatizados.

Como o preço é calculado?

Os valores de cada taxa vêm da tabela de regras, de acordo com o modal e o tipo de carga escolhidos. O cálculo segue cinco etapas, sempre nesta ordem:

1. Peso taxável: o peso que de fato é cobrado

Uma carga leve mas volumosa ocupa espaço no veículo como se fosse pesada. Por isso, além do peso real, calcula-se o peso cubado, que converte o volume em peso:

peso cubado = volume (m³) × 200 kg/m³

O peso taxável é o maior valor entre o peso real e o peso cubado.

Exemplo: uma caixa de 50 kg que ocupa 0,5 m³ tem peso cubado de 100 kg (0,5 × 200). Como 100 kg é maior que 50 kg, o frete é calculado sobre 100 kg.

2. Subtotal base
subtotal base = taxa fixa + (peso taxável × taxa por kg) + (distância × taxa por km)
3. Adicionais

Ao subtotal base somam-se: combustível, manuseio, seguro, urgência, pedágios e um adicional manual (valor extra informado pelo usuário).

4. Frete mínimo

Se o total ficar abaixo do valor mínimo definido na tabela, cobra-se o mínimo. Isso evita que envios muito pequenos fiquem com um preço irrealista.

5. Desconto negociado

Por último, aplica-se o desconto, se houver.

Estrutura do projeto
calculadora_custo_frete_streamlit/
├── data/
│   ├── tabela_regras_frete.csv          # regras de preço por modal e tipo de carga
│   └── historico_cotacoes_ficticio.csv  # 180 cotações fictícias para demonstração
├── docs/                                # imagens e documentação de apoio
├── outputs/                             # arquivos gerados pela aplicação
├── src/
│   ├── app.py                           # interface (Streamlit)
│   └── frete.py                         # lógica do cálculo
├── tests/
│   └── test_frete.py                    # testes automatizados
├── requirements.txt
└── README.md
Como executar localmente

Pré-requisito: Python 3.10 ou superior.

1. Clone o repositório

bash
git clone https://github.com/antonioaguiarss/calculadora_custo_frete_streamlit.git
cd calculadora_custo_frete_streamlit

2. Crie e ative um ambiente virtual

bash
python -m venv .venv
Windows: .venv\Scripts\activate
macOS/Linux: source .venv/bin/activate

3. Instale as dependências

bash
pip install -r requirements.txt

4. Rode a aplicação

bash
streamlit run src/app.py

A aplicação abre automaticamente no navegador (normalmente em http://localhost:8501).

Rodando os testes
bash
python -m unittest discover -s tests -v
Como personalizar as regras

Todas as tarifas ficam em data/tabela_regras_frete.csv. Para mudar preços, basta editar esse arquivo, sem mexer no código.

Cada combinação de modal + tipo de carga deve aparecer uma única vez.
Os valores atuais são ilustrativos. Substitua-os por regras aprovadas antes de qualquer uso real.
Limitações
Valores e regras são fictícios e não representam tarifas reais.
O cálculo não considera todos os fatores de um frete real, como tributos, restrições de rota, dimensões específicas, janela de entrega, sazonalidade, capacidade disponível, taxas portuárias, Incoterms (regras internacionais que definem quem paga e quem assume o risco em cada etapa do transporte) e negociações individuais.
O fator de cubagem de 200 kg/m³ é uma premissa de demonstração. Na prática, ele varia conforme o modal e o contrato.
O histórico é salvo em um CSV local, o que não funciona bem com várias pessoas usando ao mesmo tempo. Para isso, seria necessário um banco de dados.
Não deve ser usado para emitir preço vinculante sem validação comercial.
Próximos passos
 Cadastro de transportadoras e contratos
 Regras por região, faixa de peso e faixa de distância
 Comparativo de preços entre transportadoras
 Dashboard de margens e simulação de cenários
 Banco de dados (SQLite ou PostgreSQL) no lugar do CSV
 Publicação no Streamlit Community Cloud
O que este projeto demonstra
Transformar uma regra operacional de frete em uma ferramenta reproduzível e auditável.
Separar as regras de negócio da interface, o que facilita a manutenção.
Mostrar a composição do preço de forma clara, inclusive para quem não é especialista.
Boas práticas de desenvolvimento: validação de entradas, testes automatizados e exportação de dados.
Autor

Antonio Aguiar

Projeto para fins educacionais e de portfólio.

<!-- Sugestão: adicione um arquivo LICENSE (por exemplo, MIT) para definir formalmente os termos de reutilização. -->
