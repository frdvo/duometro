# Scraper de Restaurantes DuoGourmet com Busca de Estações de Metrô de SP

## Introdução

Quer curtir uma refeição de dar água na boca com o [**DuoGourmet**](https://www.duogourmet.com.br/restaurantes/sao-paulo), onde o segundo prato sai de graça, sem cair na cilada do trânsito paulistano? 🚗💨 São Paulo é um monstro de concreto, e ninguém merece ficar preso no engarrafamento, gastando gasolina e paciência, só pra comer bem. Este projeto é o seu passe VIP pra uma experiência gastronômica **sustentável**, **prática** e sem estresse. Ele mapeia os restaurantes do DuoGourmet, acha a estação de metrô mais próxima, te diz a distância a pé e o tempo que você vai levar pra chegar lá. Tudo isso com um toque de tecnologia e um montão de bom humor! 😎

A **lista completa de restaurantes**, com todas as informações fresquinhas, está disponível para **download** na seção de [**Releases**](https://github.com/frdvo/duometro/releases), no arquivo `restaurantes_com_metro_google.csv`. Bora planejar sua próxima aventura gastronômica?

## Visão Geral do Projeto

O script, agora com o nome chique de `pega_os_duo.py` (adeus, `duo_google.py`!), é uma ferramenta ninja que junta web scraping com um uso esperto de APIs pra te ajudar a escolher o restaurante perfeito no DuoGourmet. Ele coleta nome, endereço, tipo de cozinha, horários e, claro, descobre a estação de metrô mais próxima, com distância e tempo a pé calculados com precisão. Tudo isso vai parar num arquivo CSV (`restaurantes_com_metro_google.csv`) que é praticamente um mapa do tesouro para os foodies que preferem o metrô ao caos das ruas.

E sabe o que é melhor? A nova versão é **muito mais esperta** (e econômica!) que a anterior. A primeira versão era tipo aquele amigo que pede pizza com borda recheada, caviar e entrega expressa: gastava mais do que precisava chamando várias APIs do Google Maps. Agora, otimizamos tudo pra ser mais leve no bolso e mais eficiente, sem perder o charme.

## O que mudou? (Prepare-se para o *glow-up* do projeto!)

A nova versão do `pega_os_duo.py` é como um vinho que melhora com o tempo. Aqui vão as principais novidades:

- **Geocodificação grátis com Nominatim**: Chega de torrar a grana com APIs pagas pra geocodificar endereços! Agora usamos a API gratuita do [**Nominatim**](https://nominatim.openstreetmap.org/), que transforma endereços em coordenadas com precisão e sem cobrar um centavo.
- **Lista estática de estações de metrô**: Esqueça buscar estações em tempo real. Temos um arquivo `estacoes.csv` com todas as estações de metrô de São Paulo, já com linha, endereço e coordenadas GPS. É tipo um GPS pré-carregado, pronto pra ação!
- **Fórmula de Haversine (sim, é assim que se escreve!)**: Usamos a fórmula de Haversine pra calcular a distância em linha reta até a estação mais próxima. É matemática pura, sem complicação, pra te dizer qual estação está pertinho do restaurante.
- **Google Routes API, a nova estrela**: Trocamos a antiga Distance Matrix API pela moderníssima **Google Routes API**, que calcula a distância a pé e o tempo com mais estilo e eficiência. Mantemos a precisão milimétrica do Google Maps sem agredir o bolso.
- **Novas colunas no CSV**: Agora, o `restaurantes_com_metro_google.csv` inclui **Distância em Linha Reta** (pra quem curte precisão geométrica) e **Estação**, pra você saber exatamente onde descer do metrô.
- **Diff.py mais esperto**: O script `diff.py` foi turbinado pra lidar com as mudanças e ser mais flexível, comparando as versões do CSV e mostrando o que mudou com emojis e um toque de classe. 🕵️‍♂️

## Funcionalidades

- **Extração de Dados**: Coleta nome, endereço, contato, tipo de cozinha e horários de almoço e jantar dos restaurantes do DuoGourmet. Tudo bem organizadinho!
- **Localização de Metrô**: Usa a Nominatim pra geocodificar endereços e a fórmula de Haversine pra achar a estação mais próxima em linha reta. Depois, a Google Routes API entra em cena pra calcular a distância a pé e o tempo até a estação.
- **Evita Duplicatas**: Checa URLs já processadas pra não repetir restaurantes no CSV. Nada de déjà-vu indesejado!
- **Limite Configurável**: Quer processar só alguns restaurantes? Ajuste o número máximo com a variável de ambiente `MAX_RESTAURANTES`.
- **Saída Estruturada**: Gera um CSV tão bem organizado que você vai querer emoldurá-lo.
- **Comparação de Versões**: O `diff.py` te mostra o que mudou entre versões do CSV, com direito a emojis pra deixar tudo mais divertido. 🆕

## Requisitos

Pra botar esse projeto pra rodar, você vai precisar de:

- **Python**: Versão 3.6 ou superior.
- **Ambiente Virtual**: Pra evitar bagunça de dependências.
- **Dependências**: Listadas no `requirements.txt`:
  - `requests` 
  - `beautifulsoup4`
- **Chave de API do Google Maps**: Com a **Routes API** ativada. A Geocoding e Places APIs foram pro banco de reservas!
- **Variáveis de Ambiente**:
  - `GOOGLE_API_KEY`: Sua chave de API do Google Maps.
  - `MAX_RESTAURANTES` (opcional): Número máximo de restaurantes a processar (padrão: 5, no momento o Duo tem quase 600 em São Paulo).
- **Arquivo `estacoes.csv`**: Já incluído, com todas as estações de metrô de SP, prontinho pra uso.

## Configuração

### 1. Criar um Ambiente Virtual (venv)

Nada de bagunçar seu Python global! Crie um ambiente virtual pra manter as coisas organizadas:

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
   Viu o `(venv)` no começo da linha? Tô no clima!

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
   `(venv)` apareceu? Então tá pronto!

### 2. Instalar Dependências

Com o ambiente virtual ativado, instale as dependências como quem pede um café expresso:
```bash
pip install -r requirements.txt
```

### 3. Configurar a Chave de API do Google Maps

- Pegue sua chave de API no [Google Cloud Console](https://developers.google.com/maps/documentation/javascript/get-api-key).
- Ative a **Routes API** (as outras APIs não são mais necessárias, graças ao Nominatim!).
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

Por padrão apenas 5 restaurantes para não gastar a API, mas o Duo já tem quase 600 restaurantes em SP:

#### **Windows**
```bash
set MAX_RESTAURANTES=600
```

#### **Linux/macOS**
```bash
export MAX_RESTAURANTES=600
```

### 5. Executar o Script

Tudo configurado? Então bora rodar o `pega_os_duo.py`:
```bash
python pega_os_duo.py
```

## Como Funciona

1. **Coletar Links**:
   - Acessa a página de restaurantes de São Paulo do DuoGourmet (`https://www.duogourmet.com.br/restaurantes/sao-paulo`).
   - Ignora URLs já processadas no CSV existente.
   - Ordena os restaurantes por nome e limita ao número definido em `MAX_RESTAURANTES`.

2. **Extrair Informações**:
   - Usa **BeautifulSoup** pra garimpar nome, endereço, contato, tipo de cozinha e horários (almoço e jantar, com "X" nos dias disponíveis).

3. **Localizar Estações de Metrô**:
   - Limpa o endereço do restaurante e usa a **Nominatim API** pra transformá-lo em coordenadas.
   - Aplica a **fórmula de Haversine** pra encontrar a estação mais próxima em linha reta, usando o arquivo `estacoes.csv`.
   - Se a estação estiver a menos de 2 km (ou a menos do definido em MAX_DISTANCE), a **Google Routes API** calcula a distância a pé e o tempo com precisão.

4. **Salvar Resultados**:
   - Gera o `restaurantes_com_metro_google.csv` com colunas para restaurante, metrô (incluindo Linha, Estação, Distância, Tempo e Distância em Linha Reta) e horários.
   - Adiciona novos dados sem apagar os antigos, escrevendo o cabeçalho só se o arquivo for novo.

5. **Comparar Versões**:
   - O `diff.py` analisa as diferenças entre versões do CSV, destacando restaurantes adicionados, removidos ou modificados, com emojis pra deixar tudo mais divertido.

6. **Tratamento de Erros**:
   - Faz até `MAX_RETRIES` tentativas em caso de falhas na API.
   - Inclui delays pra respeitar limites de requisições (somos educados com as APIs!).
   - Lida com endereços problemáticos, retornando "N/A" quando necessário.

## Como Usar o CSV (Hora de Brilhar!)

O arquivo `restaurantes_com_metro_google.csv` é seu melhor amigo pra planejar uma saída gastronômica. Siga o passo a passo pra virar um mestre do metrô:

1. Abra o CSV no seu app de planilha favorito (Excel, Google Spreadsheets, LibreOffice Calc... você escolhe!).
2. Selecione a primeira linha e ative o **autofiltro** (é tipo mágica, mas funciona!).
3. Filtre pelo **dia da semana** que você quer (ex.: `almoco_sab` ou `jantar_sex` com "X").
4. Escolha sua **cozinha** favorita (japonesa? italiana? vegana? tem de tudo!).
5. Filtre pela **linha de metrô** que te atende (Azul, Vermelha, Verde...).
6. Ordene por **Distância** (ou **Distancia_reta**, se você curte geometria) pra achar o restaurante mais pertinho.
7. Pegue o metrô, caminhe até o restaurante e aproveite seu prato grátis com o DuoGourmet! 🍽️

**Dica de ouro**: Baixe a lista mais recente na seção de [**Releases**](https://github.com/frdvo/duometro/releases) pra garantir que você tem os dados fresquinhos.

## Exemplo de Uso

```bash
# Ativar ambiente virtual
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Configurar variáveis
export GOOGLE_API_KEY="sua_chave_de_api_aqui"  # Linux/macOS
set GOOGLE_API_KEY=sua_chave_de_api_aqui       # Windows
export MAX_RESTAURANTES=600                    # Linux/macOS
set MAX_RESTAURANTES=600                       # Windows

# Instalar dependências
pip install -r requirements.txt

# Executar o script
python pega_os_duo.py
```

**Exemplo de Saída no Terminal**:
```
Coletando links de restaurantes...
5 novos restaurantes serão processados (ordenados alfabeticamente, limite: 5).

Processando 4/5: https://www.duogourmet.com.br/restaurantes/sao-paulo/accanto-restaurante
✅ Accanto Restaurante
   Endereço: Rua Verbo Divino, 1491. Chácara Santo Antônio São Paulo
   Estação mais próxima: Borba Gato (5-Lilas)
   Distância em linha reta: 838m
   Distância a pé: 863m (~12.6 min)

...

✅ Concluído! Dados salvos em restaurantes_com_metro_google.csv
```

## Por que Usar?

Porque comer bem não precisa ser uma aventura estressante! Com este projeto, você:
- **Reduz emissões**: Troca o carro pelo metrô e ajuda a salvar o planeta, uma refeição de cada vez. 🌍
- **Diz adeus ao estresse**: Chega de buzinas, engarrafamentos e aquela vontade de gritar no trânsito.
- **Planeja como profissional**: Escolhe restaurantes com base no dia, cozinha, linha de metrô e distância, tudo num CSV que é praticamente um guia Michelin sustentável.
- **Economiza (de verdade!)**: A nova versão usa APIs gratuitas e uma abordagem mais inteligente, pra você não gastar mais do que o necessário.

## Observações

- **Custos da API**: A Google Routes API é paga, então fique de olho no uso no Google Cloud Console, mas as primeiras 10000 requisiçoes no mês são grátis. A Nominatim é grátis, mas respeite a política de uso (1 requisição por segundo).
- **Limites de Taxa**: O script inclui delays pra não irritar as APIs (e evitar bans).
- **Precisão**: Depende da qualidade dos endereços e do arquivo `estacoes.csv`. Se algo der errado, o script é esperto o suficiente pra lidar com isso.
- **Sustentabilidade**: Ao escolher o metrô, você contribui pra uma São Paulo mais verde e menos caótica. 🚇

## Licença

Licenciado sob a [Licença MIT](https://opensource.org/licenses/MIT). Use, modifique, compartilhe e se joga na vibe gastronômica sustentável! 😄
](https://github.com/frdvo/duometro)