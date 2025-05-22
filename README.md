# Scraper de Restaurantes DuoGourmet com Busca de Estações de Metrô de SP

## Introdução

Imagine saborear uma refeição incrível com o benefício do [**DuoGourmet**](https://www.duogourmet.com.br/restaurantes/sao-paulo), que te dá um segundo prato grátis em restaurantes selecionados de São Paulo, sem o estresse do trânsito! Em uma cidade onde engarrafamentos são rotina, o aumento das emissões de carbono e o nervosismo ao volante podem acabar com o prazer de sair para comer. Este projeto foi criado para transformar sua experiência gastronômica, promovendo **sustentabilidade** e **tranquilidade**. Ele mapeia os restaurantes do DuoGourmet e encontra as estações de metrô mais próximas, com distância e tempo a pé, permitindo que você chegue ao seu destino de forma prática, ecológica e sem os aborrecimentos do trânsito.

A **lista completa de restaurantes**, com todas as informações coletadas, pode ser **baixada** na seção de [**Releases**](https://github.com/frdvo/duometro/releases) deste repositório, no arquivo `restaurantes_com_metro_google.csv`.

## Visão Geral do Projeto

O script `duo_google.py` é uma ferramenta poderosa que combina web scraping com as APIs do Google Maps para facilitar sua escolha de restaurantes no DuoGourmet. Ele coleta informações detalhadas dos restaurantes, como nome, endereço, tipo de cozinha e horários, e descobre a estação de metrô mais próxima, com a distância e o tempo a pé até ela. Tudo isso é salvo em um arquivo CSV (`restaurantes_com_metro_google.csv`), ajudando você a planejar sua saída de forma sustentável e sem o caos do trânsito paulistano.

## Funcionalidades

- **Extração de Dados**: Coleta nome, endereço, contato, tipo de cozinha e horários de almoço e jantar dos restaurantes do DuoGourmet.
- **Localização de Metrô**: Usa as APIs do Google Maps (Geocoding, Places e Distance Matrix) para identificar a estação de metrô mais próxima, com distância (em metros) e tempo a pé (em minutos).
- **Evita Duplicatas**: Verifica URLs já processadas para não repetir restaurantes no CSV.
- **Limite Configurável**: Permite definir o número máximo de restaurantes a processar via variável de ambiente (`MAX_RESTAURANTES`).
- **Saída Estruturada**: Gera um arquivo CSV organizado para facilitar a consulta e análise.

## Requisitos

Para rodar o script, você vai precisar de:

- **Python**: Versão 3.6 ou superior.
- **Ambiente Virtual**: Recomendado para isolar as dependências.
- **Dependências**: Listadas no arquivo `requirements.txt`:
  - `requests`
  - `beautifulsoup4`
- **Chave de API do Google Maps**: Com as APIs Geocoding, Places e Distance Matrix ativadas.
- **Variáveis de Ambiente**:
  - `GOOGLE_API_KEY`: Sua chave de API do Google Maps.
  - `MAX_RESTAURANTES` (opcional): Número máximo de restaurantes a processar (padrão: 5).

## Configuração

### 1. Criar um Ambiente Virtual (venv)

Para manter seu projeto organizado e evitar conflitos, crie um ambiente virtual. Siga os passos para o seu sistema operacional:

#### **Windows**
1. Abra o Prompt de Comando ou PowerShell.
2. Navegue até o diretório do projeto:
   ```bash
   cd caminho/para/o/projeto
   ```
3. Crie o ambiente virtual:
   ```bash
   python -m venv venv
   ```
4. Ative o ambiente:
   ```bash
   venv\Scripts\activate
   ```
   Você verá `(venv)` no início da linha de comando.

#### **Linux/macOS**
1. Abra o terminal.
2. Navegue até o diretório do projeto:
   ```bash
   cd caminho/para/o/projeto
   ```
3. Crie o ambiente virtual:
   ```bash
   python3 -m venv venv
   ```
4. Ative o ambiente:
   ```bash
   source venv/bin/activate
   ```
   Você verá `(venv)` no início da linha do terminal.

### 2. Instalar Dependências

Com o ambiente virtual ativado, instale as dependências:
```bash
pip install -r requirements.txt
```

### 3. Configurar a Chave de API do Google Maps

- Obtenha uma chave de API em [Google Cloud Console](https://developers.google.com/maps/documentation/javascript/get-api-key).
- Ative as APIs **Geocoding**, **Places** e **Distance Matrix**.
- Defina a chave como variável de ambiente:

  #### **Windows**
  ```bash
  set GOOGLE_API_KEY=sua_chave_de_api_aqui
  ```

  #### **Linux/macOS**
  ```bash
  export GOOGLE_API_KEY=sua_chave_de_api_aqui
  ```

### 4. Configurar o Limite de Restaurantes (Opcional)

Para limitar o número de restaurantes processados:

#### **Windows**
```bash
set MAX_RESTAURANTES=10
```

#### **Linux/macOS**
```bash
export MAX_RESTAURANTES=10
```

### 5. Executar o Script

Com tudo configurado, rode o script:
```bash
python duo_google.py
```

## Como Funciona

1. **Coletar Links**:
   - Acessa a página de restaurantes de São Paulo do DuoGourmet (`https://www.duogourmet.com.br/restaurantes/sao-paulo`).
   - Filtra URLs já processadas no CSV existente.
   - Ordena os restaurantes por nome e limita ao número definido em `MAX_RESTAURANTES`.

2. **Extrair Informações**:
   - Para cada restaurante, coleta:
     - Nome
     - Endereço
     - Contato
     - Tipo de cozinha
     - Disponibilidade de almoço e jantar por dia ("X" para dias disponíveis)
   - Usa a biblioteca **BeautifulSoup** para parsear o HTML.

3. **Localizar Estações de Metrô**:
   - Limpa o endereço do restaurante e usa a **Geocoding API** para obter coordenadas.
   - A **Places API** encontra a estação de metrô mais próxima (raio de 3 km).
   - A **Distance Matrix API** calcula a distância a pé e o tempo até a estação.

4. **Salvar Resultados**:
   - Gera o arquivo `restaurantes_com_metro_google.csv` com colunas para restaurante, metrô e horários.
   - Adiciona novos dados sem sobrescrever os existentes, escrevendo o cabeçalho apenas se o arquivo for novo.

5. **Tratamento de Erros**:
   - Faz até `MAX_RETRIES` tentativas em caso de falhas na API.
   - Inclui delays para respeitar limites de taxa.
   - Lida com endereços inválidos, retornando "N/A" quando necessário.

## Saída

O script cria o arquivo `restaurantes_com_metro_google.csv` com as seguintes colunas:

- `nome`: Nome do restaurante
- `endereco`: Endereço completo
- `contato`: Informações de contato
- `cozinha`: Tipo de cozinha
- `link`: URL do restaurante
- `Estacao`: Nome da estação de metrô mais próxima
- `Distancia`: Distância até a estação (em metros)
- `Tempo`: Tempo a pé até a estação (em minutos)
- `almoco_dom`, `almoco_seg`, ..., `almoco_sab`: Disponibilidade de almoço ("X" se disponível)
- `jantar_dom`, `jantar_seg`, ..., `jantar_sab`: Disponibilidade de jantar ("X" se disponível)

Você pode baixar a lista gerada na seção de [**Releases**](https://github.com/frdvo/duometro/releases) do repositório.

## Exemplo de Uso

```bash
# Ativar ambiente virtual
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Configurar variáveis
export GOOGLE_API_KEY="sua_chave_de_api_aqui"  # Linux/macOS
set GOOGLE_API_KEY=sua_chave_de_api_aqui       # Windows
export MAX_RESTAURANTES=5                      # Linux/macOS
set MAX_RESTAURANTES=5                         # Windows

# Instalar dependências
pip install -r requirements.txt

# Executar o script
python duo_google.py
```

**Exemplo de Saída no Terminal**:
```
Coletando links de restaurantes...
5 novos restaurantes serão processados (ordenados alfabeticamente, limite: 5).

Processando 1/5: https://www.duogourmet.com.br/restaurantes/sao-paulo/restaurante-abc
✅ Restaurante ABC
   Endereço: Rua Exemplo, 123, São Paulo
   Estação mais próxima: Estação Trianon-MASP
   Distância: 850m (~12.5 min a pé)

...

✅ Concluído! Dados salvos em restaurantes_com_metro_google.csv
```

## Por que Usar?

Este projeto não é só sobre comer bem com o DuoGourmet, mas sobre fazer isso de forma **consciente** e **tranquila**. Ao escolher o metrô, você:
- **Reduz emissões**: Diminui o uso de carros, ajudando a combater a poluição e as mudanças climáticas.
- **Evita estresse**: Esqueça os engarrafamentos e os aborrecimentos do trânsito paulistano.
- **Planeja com facilidade**: Encontra restaurantes acessíveis via metrô com informações claras sobre estação, distância e tempo a pé.

## Observações

- **Custos da API**: As APIs do Google Maps têm custos. Monitore seu uso no Google Cloud Console.
- **Limites de Taxa**: O script inclui delays para evitar problemas com limites de requisições.
- **Precisão**: Os dados de estações dependem da qualidade dos endereços e das APIs do Google.
- **Sustentabilidade**: Este projeto incentiva o transporte público, contribuindo para um futuro mais verde e uma São Paulo mais tranquila.

## Licença

Licenciado sob a [Licença MIT](https://opensource.org/licenses/MIT). Sinta-se à vontade para usar, modificar e compartilhar!
](https://github.com/frdvo/duometro)
