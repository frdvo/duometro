import requests
from bs4 import BeautifulSoup
import csv
import time
import os
import re
from math import radians, sin, cos, sqrt, atan2
from urllib.parse import urlparse

# Configurações globais
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
BASE_URL = "https://www.duogourmet.com.br"
LIST_URL = f"{BASE_URL}/restaurantes/sao-paulo"
HEADERS = {"User-Agent": "Mozilla/5.0"}
CSV_FILE = "restaurantes_com_metro_google.csv"
DAYS = ["dom", "seg", "ter", "qua", "qui", "sex", "sab"]
GOOGLE_API_DELAY = 0.1  # Delay para a API do Google
NOMINATIM_DELAY = 0.5  # Delay para a API Nominatim (respeitar política de uso)
MAX_RETRIES = 3
MAX_RESTAURANTS = int(os.getenv("MAX_RESTAURANTS", 5))
REQUESTS_DELAY = 0.05
STATIONS_CSV = "estacoes.csv"  # Arquivo com as estações de metrô
MAX_DISTANCE = int(os.getenv("MAX_DISTANCE", 2000)) # Distância máxima em metros para considerar cálculo de rota a pé

# Variável global para cache das estações
stations_cache = None

def load_stations():
    """Carrega as estações de metrô do arquivo CSV"""
    global stations_cache
    if stations_cache is not None:
        return stations_cache
    
    stations = []
    try:
        with open(STATIONS_CSV, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    stations.append({
                        "linha": row['Linha'],
                        "nome": row['Nome da Estacao'],
                        "lat": float(row['Latitude']),
                        "lon": float(row['Longitude'])
                    })
                except (ValueError, KeyError) as e:
                    print(f"⚠️ Erro ao processar estação {row.get('Nome da Estacao', 'N/A')}: {e}")
    except FileNotFoundError:
        print(f"❌ Arquivo {STATIONS_CSV} não encontrado.")
    
    stations_cache = stations
    return stations

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calcula distância em metros entre coordenadas usando fórmula de Haversine"""
    R = 6371.0  # Raio da Terra em km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a)) * 1000  # metros

def clean_address(address):
    """Limpa e simplifica o endereço para geocodificação"""
    if not address or address == "N/A":
        return None
    
    # Substitui abreviações problemáticas
    replacements = {
        r'\bMin\.?\b': 'Ministro',
        r'\bDes\.?\b': 'Desembargador',
        r'\bSra\.?\b': 'Senhora',
        r'\bDr\.?\b': 'Doutor'
    }
    
    for pattern, repl in replacements.items():
        address = re.sub(pattern, repl, address, flags=re.IGNORECASE)
    
    # Remove informações após números (como complementos)
    simplified = re.sub(r'(\d+).*', r'\1', address)
    # Remove códigos postais e outras informações irrelevantes
    simplified = re.sub(r',?\s*\d{5}-?\d{3}.*', '', simplified)
    # Remove termos como "próximo", "altura", etc.
    simplified = re.sub(r'(pr[óo]ximo|altura|alt|perto|ao lado).*', '', simplified, flags=re.IGNORECASE)
    # Remove pontos de referência após a vírgula
    simplified = re.sub(r',.*?(?=\s*\d|$)', '', simplified)
    # Remove espaços extras e vírgulas desnecessárias
    simplified = re.sub(r'\s{2,}', ' ', simplified).strip().strip(',')
    
    return simplified if simplified else None

def get_coordinates_nominatim(address):
    """Converte endereço em coordenadas usando Nominatim"""
    cleaned_address = clean_address(address)
    if not cleaned_address:
        print("⚠️ Endereço inválido ou vazio após limpeza")
        return None
    
    try:
        time.sleep(NOMINATIM_DELAY)  # Respeitar política de uso da API
        url = f"https://nominatim.openstreetmap.org/search?q={cleaned_address}, São Paulo, Brasil&format=json&limit=1"
        headers = {"User-Agent": "DuoGourmetMetroFinder/1.0"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data:
            return (float(data[0]["lat"]), float(data[0]["lon"]))
        else:
            print(f"⚠️ Endereço não encontrado no Nominatim: '{cleaned_address}'")
            return None
    except Exception as e:
        print(f"⚠️ Erro ao geocodificar com Nominatim: {e}")
        return None

def find_nearest_station(lat, lon):
    """Encontra a estação mais próxima usando cálculo de distância"""
    stations = load_stations()
    if not stations or lat is None or lon is None:
        return None
    
    nearest = min(
        stations,
        key=lambda s: haversine_distance(lat, lon, s["lat"], s["lon"])
    )
    distance = haversine_distance(lat, lon, nearest["lat"], nearest["lon"])
    
    return {
        "linha": nearest["linha"],
        "nome": nearest["nome"],
        "lat": nearest["lat"],
        "lon": nearest["lon"],
        "distance_haversine": distance
    }

def make_google_api_request(url):
    """Faz requisições à API do Google com tratamento de erros e retentativas"""
    for attempt in range(MAX_RETRIES):
        try:
            time.sleep(GOOGLE_API_DELAY)
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'OK':
                return data
            else:
                error_msg = data.get('error_message', data['status'])
                print(f"⚠️ Tentativa {attempt + 1}: Erro na API Google ({data['status']}): {error_msg}")
                if attempt == MAX_RETRIES - 1:
                    return None
        except Exception as e:
            print(f"⚠️ Tentativa {attempt + 1}: Erro na requisição à API: {e}")
            if attempt == MAX_RETRIES - 1:
                return None

def get_walking_distance_google(origin_lat, origin_lon, dest_lat, dest_lon):
    """Calcula distância e tempo a pé usando Google Routes API"""
    url = "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix"
    
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': GOOGLE_API_KEY,
        'X-Goog-FieldMask': 'distanceMeters,duration,status'
    }
    
    payload = {
        "origins": [{
            "waypoint": {
                "location": {
                    "latLng": {
                        "latitude": origin_lat,
                        "longitude": origin_lon
                    }
                }
            }
        }],
        "destinations": [{
            "waypoint": {
                "location": {
                    "latLng": {
                        "latitude": dest_lat,
                        "longitude": dest_lon
                    }
                }
            }
        }],
        "travelMode": "WALK"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Verifica erros HTTP
        data = response.json()
        
        if not data or not isinstance(data, list):
            print("⚠️ Resposta inválida da API")
            return None
            
        first_result = data[0]
        
        # Verifica se tem os campos necessários
        if 'distanceMeters' not in first_result or 'duration' not in first_result:
            print(f"⚠️ Dados incompletos. Resposta completa: {data}")
            return None
            
        # Converte duração (ex: "900s" → 15 minutos)
        duration_seconds = float(first_result['duration'].rstrip('s'))
        
        return {
            'distance': first_result['distanceMeters'],
            'duration': duration_seconds / 60  # Convertendo para minutos
        }
        
    except requests.exceptions.RequestException as e:
        print(f"🚨 Erro na requisição: {str(e)}")
        return None
    except (ValueError, KeyError, IndexError) as e:
        print(f"🔍 Erro ao processar resposta: {str(e)}")
        return None

def get_existing_restaurants():
    """Retorna conjunto de URLs já processadas a partir do CSV existente"""
    existing = set()
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            if reader.fieldnames and 'link' in reader.fieldnames:
                existing.update(row['link'] for row in reader)
    return existing

def get_restaurant_links():
    """Obtém links dos restaurantes ordenados por nome, evitando duplicatas"""
    try:
        existing_urls = get_existing_restaurants()
        response = requests.get(LIST_URL, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        restaurants = []
        cards = soup.select("div.restaurant-card")
        for card in cards:
            a_tag = card.select_one("a[href^='/restaurantes/sao-paulo/']")
            if a_tag:
                name = card.select_one("h3").text.strip() if card.select_one("h3") else "Sem Nome"
                full_url = BASE_URL + a_tag['href']
                
                if full_url not in existing_urls:
                    restaurants.append({
                        "name": name,
                        "link": full_url
                    })
        
        # Ordena e limita o número de restaurantes
        restaurants.sort(key=lambda x: x['name'].lower())
        return restaurants[:MAX_RESTAURANTS]
    
    except Exception as e:
        print(f"⚠️ Erro ao buscar links de restaurantes: {e}")
        return []

def parse_calendar(soup):
    """Analisa a tabela de horários de funcionamento"""
    almoco = [""] * 7
    jantar = [""] * 7

    table = soup.select_one("table")
    if not table:
        return almoco, jantar

    rows = table.select("tbody tr")
    if len(rows) >= 2:
        almoco_cells = rows[0].find_all("td")[1:]
        jantar_cells = rows[1].find_all("td")[1:]

        almoco = ["X" if "check.png" in str(cell) else "" for cell in almoco_cells]
        jantar = ["X" if "check.png" in str(cell) else "" for cell in jantar_cells]

    return almoco, jantar

def scrape_restaurant_info(url):
    """Coleta informações do restaurante com dados do metro"""
    try:
        res = requests.get(url, headers=HEADERS)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        # Informações básicas do restaurante
        name = soup.select_one("h1").text.strip() if soup.select_one("h1") else "N/A"
        address_tag = soup.select_one("h4:has(img[src*='flat-pin']) + address p")
        address = address_tag.text.strip().replace("\n", ", ") if address_tag else "N/A"
        address = re.sub(r"(,?)\s*São Paulo$", r"\1 São Paulo", address)
        contato_tag = soup.select_one("h4:has(img[src*='phone']) + p")
        contato = contato_tag.text.strip() if contato_tag else "N/A"
        cozinha_tag = soup.select_one("h4:has(img[src*='chef']) + p")
        cozinha = cozinha_tag.text.strip() if cozinha_tag else "N/A"
        almoco, jantar = parse_calendar(soup)

        # Dados do metrô (inicialmente vazios)
        metro_data = {
            "Linha": "N/A",
            "Estacao": "N/A",
            "Distancia": "N/A",
            "Tempo": "N/A",
            "Distancia_reta": "N/A"
        }

        if address != "N/A":
            # Usa Nominatim para geocodificação
            coords = get_coordinates_nominatim(address)
            if coords:
                lat, lng = coords
                
                # Encontra a estação mais próxima pelo cálculo de distância
                nearest_station = find_nearest_station(lat, lng)
                if nearest_station:
                    metro_data["Distancia_reta"] = f"{nearest_station['distance_haversine']:.0f}"
                    
                    # Verifica se a distância está dentro do limite aceitável
                    if nearest_station['distance_haversine'] <= MAX_DISTANCE:
                        # Usa Google para cálculo preciso de distância/tempo
                        walking_data = get_walking_distance_google(
                            lat, lng,
                            nearest_station["lat"], nearest_station["lon"]
                        )
                        
                        if walking_data:
                            metro_data.update({
                                "Linha": nearest_station["linha"],
                                "Estacao": nearest_station["nome"],
                                "Distancia": f"{walking_data['distance']:.0f}",
                                "Tempo": f"{walking_data['duration']:.1f}"
                            })
                    else:
                        print(f"   Estação mais próxima está a {nearest_station['distance_haversine']:.0f}m (acima do limite de {MAX_DISTANCE}m)")

        return {
            "nome": name,
            "endereco": address,
            "contato": contato,
            "cozinha": cozinha,
            "link": url,
            **metro_data,
            **{f"almoco_{day}": almoco[i] for i, day in enumerate(DAYS)},
            **{f"jantar_{day}": jantar[i] for i, day in enumerate(DAYS)},
        }

    except Exception as e:
        print(f"⚠️ Erro ao processar {url}: {e}")
        return None

def main():
    if GOOGLE_API_KEY == "SUA_CHAVE_DE_API_AQUI":
        print("❌ Erro: Você precisa configurar sua API Key do Google Maps")
        print("Obtenha uma chave em: https://developers.google.com/maps/documentation/javascript/get-api-key")
        print("Depois, habilite a Distance Matrix API")
        return

    print("\nColetando links de restaurantes...")
    restaurants = get_restaurant_links()
    print(f"{len(restaurants)} novos restaurantes serão processados (ordenados alfabeticamente, limite: {MAX_RESTAURANTS}).\n")

    fieldnames = ["nome", "endereco", "contato", "cozinha", "link",
                 "Linha", "Estacao", "Distancia", "Tempo", "Distancia_reta"] + \
                [f"almoco_{d}" for d in DAYS] + [f"jantar_{d}" for d in DAYS]

    # Verifica se o arquivo existe para determinar se precisa escrever o cabeçalho
    file_exists = os.path.isfile(CSV_FILE)
    
    with open(CSV_FILE, "a", newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Escreve o cabeçalho apenas se o arquivo não existia
        if not file_exists:
            writer.writeheader()

        for i, restaurant in enumerate(restaurants, 1):
            url = restaurant['link']
            
            print(f"\nProcessando {i}/{len(restaurants)}: {url}")
            data = scrape_restaurant_info(url)
            
            if data:
                writer.writerow(data)  # Grava imediatamente no CSV
                csvfile.flush()  # Força a escrita no disco
                
                print(f"✅ {data['nome']}")
                print(f"   Endereço: {data['endereco']}")
                if data['Estacao'] != "N/A":
                    print(f"   Estação mais próxima: {data['Estacao']} ({data['Linha']})")
                    print(f"   Distância em linha reta: {data['Distancia_reta']}m")
                    if data['Distancia'] != "N/A":
                        print(f"   Distância a pé: {data['Distancia']}m (~{data['Tempo']} min)")
                elif data['Distancia_reta'] != "N/A":
                    print(f"   Estação mais próxima está a {data['Distancia_reta']}m (acima do limite de {MAX_DISTANCE}m)")
            else:
                print(f"⚠️ Falha ao processar restaurante {i}")

            time.sleep(REQUESTS_DELAY)
    print(f"\n✅ Concluído! Dados salvos em {CSV_FILE}")

if __name__ == "__main__":
    main()