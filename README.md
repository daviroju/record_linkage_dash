# Record Linkage Dash

Este projeto é uma adaptação de um sistema originalmente desenvolvido para buscar dados relacionados entre três bases do sistema prisional goiano. A versão atual foi modificada para remover dependências de servidores do Tribunal de Justiça, tornando-o mais genérico e flexível para uso com diferentes bases de dados.

## Funcionalidades
- **Geração de registros (records):** Realiza o linkage (ligação) de registros entre diferentes bases de dados prisionais, identificando possíveis correspondências entre pessoas.
- **Interface Web:** Utiliza Dash para apresentar os dados de forma interativa e visual.
- **Processamento e limpeza de dados:** Scripts para pré-processamento, limpeza e padronização dos dados.
- **Configuração flexível:** Permite adaptar as bases de entrada para diferentes contextos, sem dependências fixas de servidores externos.

## Estrutura do Projeto
- `dash_main.py`: Interface web para visualização e análise dos dados vinculados.
- `generate_records.py`: Script principal para geração dos records e linkage entre as bases.
- `scripts/`: Scripts auxiliares para limpeza, carregamento e manipulação dos dados.
- `data/`: Diretório para armazenar os arquivos de dados (pkl).
- `assets/`: Arquivos de estilo para a interface Dash.

## Instalação
1. **Clone o repositório:**
   ```bash
   git clone https://github.com/daviroju/record_linkage_dash.git
   cd prisoners_record_linkage
   ```
2. **Instale as dependências com o uv:**
   ```bash
    uv sync
   ```

## Uso
1. **Prepare os dados:**
   - Coloque os arquivos `.pkl` das bases de dados no diretório `data/`.
   - Os nomes esperados são: `base1.pkl`, `base2.pkl`, `base3.pkl` (ou adapte os scripts conforme necessário).
2. **Gere os records:**
   ```bash
   uv run scripts/generate_records.py
   ```
   Isso irá processar as bases e gerar os arquivos de saída necessários para a interface.
3. **Execute a interface Dash:**
   ```bash
   
   uv run dash_main.py
   ```
   Acesse o endereço exibido no terminal para visualizar a interface web.

## Dependências Principais
- Dash, Dash Bootstrap Components, Dash AG Grid
- Pandas
- RecordLinkage
- Faker (para gerar os dados fictícios)
- SQLAlchemy (para integração opcional com bancos de dados)

## Observações
- O projeto pode ser facilmente adaptado para outras bases, bastando ajustar os scripts de leitura e pré-processamento.