Scraper de Restaurantes DuoGourmet com Busca de Estações de Metrô
Introdução
O DuoGourmet é um serviço que permite aos clientes em aproveitar um segundo prato principal grátis em restaurantes parceiros. Com o aumento do trânsito em São Paulo, que contribui para maiores emissões de carbono e estresse ao dirigir, este projeto busca facilitar a vida dos usuários e preservar o meio ambiente. Ele identifica as estações de metrô mais próximas dos restaurantes do DuoGourmet, fornecendo a distância e o tempo a pé até cada local. Assim, os usuários podem escolher restaurantes acessíveis por metrô, com zero emissões, promovendo uma forma mais sustentável e tranquila de chegar ao destino.
A lista de restaurantes gerada pelo script pode ser baixada na seção de Releases deste repositório, no arquivo restaurantes_com_metro_google.csv.
Visão Geral do Projeto
O script duo_google.py extrai informações de restaurantes do site do DuoGourmet e utiliza as APIs do Google Maps para encontrar a estação de metrô mais próxima de cada restaurante. Os dados coletados, como nome, endereço, contato, tipo de cozinha, horários de funcionamento e informações do metrô, são salvos em um arquivo CSV (restaurantes_com_metro_google.csv) para fácil consulta. Este projeto ajuda os usuários a planejar suas refeições de forma sustentável, priorizando o transporte público.
Funcionalidades

Extrai dados dos restaurantes do site do DuoGourmet, incluindo nome, endereço, contato, tipo de cozinha e horários de almoço e jantar.
Usa as APIs do Google Maps (Geocoding, Places e Distance Matrix) para encontrar a estação de metrô mais próxima, com distância e tempo a pé.
Evita processar restaurantes duplicados, verificando URLs já processadas no arquivo CSV.
Limita o número de restaurantes processados com base na variável de ambiente MAX_RESTAURANTES.
Gera um arquivo CSV estruturado para análise fácil.

Requisitos
Para executar o script, você precisa de:

Python 3.6 ou superior
Um ambiente virtual (venv) configurado (veja instruções abaixo)
Um arquivo requirements.txt com as dependências:
requests
beautifulsoup4


Uma chave de API do Google Maps com as seguintes APIs ativadas:
Geocoding API
Places API
Distance Matrix API


Variáveis de ambiente:
GOOGLE_API_KEY: Sua chave de API do Google Maps.
MAX_RESTAURANTES (opcional): Número máximo de restaurantes a processar (padrão: 5).



Configuração
1. Criar um Ambiente Virtual (venv)
É altamente recomendável usar um ambiente virtual para isolar as dependências do projeto. Siga as instruções abaixo para o seu sistema operacional:
Windows

Abra o Prompt de Comando ou PowerShell.
Navegue até o diretório do projeto:cd caminho/para/o/projeto


Crie o ambiente virtual:python -m venv venv


Ative o ambiente virtual:venv\Scripts\activate

Você verá (venv) no início da linha de comando, indicando que o ambiente está ativo.

Linux/macOS

Abra o terminal.
Navegue até o diretório do projeto:cd caminho/para/o/projeto


Crie o ambiente virtual:python3 -m venv venv


Ative o ambiente virtual:source venv/bin/activate

Você verá (venv) no início da linha do terminal, indicando que o ambiente está ativo.

2. Instalar Dependências
Com o ambiente virtual ativado, instale as dependências listadas no arquivo requirements.txt:
pip install -r requirements.txt

3. Configurar a Chave de API do Google Maps

Obtenha uma chave de API do Google Maps em Google Cloud Console.

Ative as APIs Geocoding, Places e Distance Matrix no seu projeto do Google Cloud.

Defina a chave de API como variável de ambiente:
Windows
set GOOGLE_API_KEY=sua_chave_de_api_aqui

Linux/macOS
export GOOGLE_API_KEY=sua_chave_de_api_aqui

Alternativamente, você pode configurar a chave diretamente no script (não recomendado por questões de segurança).


4. Configurar o Limite de Restaurantes (Opcional)
Para limitar o número de restaurantes processados, defina a variável de ambiente MAX_RESTAURANTES:
Windows
set MAX_RESTAURANTES=10

Linux/macOS
export MAX_RESTAURANTES=10

5. Executar o Script
Com o ambiente virtual ativado e as variáveis configuradas, execute o script:
python duo_google.py

Como Funciona

Coletar Links dos Restaurantes:

O script acessa a página de restaurantes de São Paulo do DuoGourmet (https://www.duogourmet.com.br/restaurantes/sao-paulo).
Filtra URLs já processadas, verificando o arquivo CSV existente.
Ordena os restaurantes alfabeticamente e limita ao número definido em MAX_RESTAURANTES.


Extrair Detalhes dos Restaurantes:

Para cada URL de restaurante, o script coleta:
Nome
Endereço
Contato
Tipo de cozinha
Disponibilidade de almoço e jantar por dia da semana (indicado por "X" nos dias disponíveis)


Usa a biblioteca BeautifulSoup para parsear o HTML.


Encontrar a Estação de Metrô Mais Próxima:

O endereço do restaurante é limpo e enviado à API de Geocoding do Google para obter coordenadas (latitude e longitude).
A API de Places do Google busca a estação de metrô mais próxima em um raio de 3 km.
A API de Distance Matrix calcula a distância a pé e o tempo até a estação.


Salvar Dados:

Os dados são salvos no arquivo restaurantes_com_metro_google.csv com colunas para:
Nome, endereço, contato, tipo de cozinha e URL do restaurante
Nome da estação de metrô mais próxima, distância (em metros) e tempo a pé (em minutos)
Disponibilidade de almoço e jantar para cada dia da semana


O arquivo CSV é atualizado incrementalmente, preservando dados existentes, e o cabeçalho é escrito apenas se o arquivo for novo.


Tratamento de Erros:

O script lida com erros de API com retentativas (até MAX_RETRIES tentativas).
Inclui delays entre requisições para evitar limites de taxa.
Endereços inválidos ou ausentes são tratados, retornando "N/A" nos campos correspondentes.



Saída
O script gera um arquivo CSV (restaurantes_com_metro_google.csv) com as seguintes colunas:

nome: Nome do restaurante
endereco: Endereço do restaurante
contato: Informações de contato
cozinha: Tipo de cozinha
link: URL do restaurante
Estacao: Nome da estação de metrô mais próxima
Distancia: Distância até a estação (em metros)
Tempo: Tempo a pé até a estação (em minutos)
almoco_dom, almoco_seg, ..., almoco_sab: Disponibilidade de almoço por dia ("X" se disponível)
jantar_dom, jantar_seg, ..., jantar_sab: Disponibilidade de jantar por dia ("X" se disponível)

Você também pode baixar a lista de restaurantes gerada na seção de Releases.
Exemplo de Uso
# Ativar ambiente virtual
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Configurar variáveis de ambiente
export GOOGLE_API_KEY="sua_chave_de_api_aqui"  # Linux/macOS
set GOOGLE_API_KEY=sua_chave_de_api_aqui       # Windows
export MAX_RESTAURANTES=5                      # Linux/macOS
set MAX_RESTAURANTES=5                         # Windows

# Instalar dependências
pip install -r requirements.txt

# Executar o script
python duo_google.py

Exemplo de Saída no Terminal:
Coletando links de restaurantes...
5 novos restaurantes serão processados (ordenados alfabeticamente, limite: 5).

Processando 1/5: https://www.duogourmet.com.br/restaurantes/sao-paulo/restaurante-abc
✅ Restaurante ABC
   Endereço: Rua Exemplo, 123, São Paulo
   Estação mais próxima: Estação Trianon-MASP
   Distância: 850m (~12.5 min a pé)

...

✅ Concluído! Dados salvos em restaurantes_com_metro_google.csv

Observações

Custos da API: As APIs do Google Maps têm custos associados ao uso. Monitore o uso no Google Cloud Console.
Limites de Taxa: O script inclui um delay (GOOGLE_API_DELAY) para evitar limites de taxa da API. Ajuste se necessário.
Precisão dos Dados: A precisão das informações sobre estações de metrô depende das APIs do Google Maps e dos endereços fornecidos.
Sustentabilidade: Ao priorizar restaurantes acessíveis por metrô, o projeto incentiva o uso de transporte público, reduzindo emissões de carbono e o estresse no trânsito.

Licença
Este projeto está licenciado sob a Licença MIT. Sinta-se à vontade para modificar e distribuir conforme necessário.
