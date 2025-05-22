import requests
from bs4 import BeautifulSoup
import csv
import time
import os
import re
from urllib.parse import urlparse

# Configurações globais
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
BASE_URL = "https://www.duogourmet.com.br"
LIST_URL = f"{BASE_URL}/restaurantes/sao-paulo"
HEADERS = {"User-Agent": "Mozilla/5.0"}
CSV_FILE = "restaurantes_com_metro_google.csv"
DAYS = ["dom", "seg", "ter", "qua", "qui", "sex", "sab"]
GOOGLE_API_DELAY = 0.1
MAX_RETRIES = 3
MAX_RESTAURANTES = int(os.getenv("MAX_RESTAURANTES", 5))

def clean_address(address):
    """Remove caracteres problemáticos e formata o endereço"""
    if not address or address == "N/A":
        return None
    address = re.sub(r"\s+", " ", address).strip()
    address = re.sub(r"[^\w\s,.-]", "", address)
    return address

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
        return restaurants[:MAX_RESTAURANTES]
    
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

def get_coordinates_google(address):
    """Converte endereço em coordenadas usando Google Geocoding API"""
    cleaned_address = clean_address(address)
    if not cleaned_address:
        print("⚠️ Endereço inválido ou vazio")
        return None
    
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={cleaned_address}, São Paulo, Brasil&key={GOOGLE_API_KEY}"
    data = make_google_api_request(url)
    
    if data and data['results']:
        location = data['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    return None

def get_nearest_station_google(lat, lng):
    """Encontra a estação mais próxima usando Google Places API"""
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=3000&type=subway_station&key={GOOGLE_API_KEY}"
    data = make_google_api_request(url)
    
    if not data or not data.get('results'):
        print("⚠️ Nenhuma estação de metrô encontrada em 3 km")
        return None
    
    station = data['results'][0]
    station_lat = station['geometry']['location']['lat']
    station_lng = station['geometry']['location']['lng']
    
    # Calcula distância e tempo a pé
    distance_url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={lat},{lng}&destinations={station_lat},{station_lng}&mode=walking&key={GOOGLE_API_KEY}"
    distance_data = make_google_api_request(distance_url)
    
    if not distance_data or not distance_data.get('rows'):
        return None
    
    element = distance_data['rows'][0]['elements'][0]
    if 'distance' not in element or 'duration' not in element:
        print("⚠️ Dados de distância/tempo não disponíveis")
        return None
    
    return {
        'name': station['name'],
        'distance': element['distance']['value'],
        'duration': element['duration']['value'] / 60  # em minutos
    }

def scrape_restaurant_info(url):
    """Coleta informações do restaurante com dados do Google Maps"""
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
            "Estacao": "N/A",
            "Distancia": "N/A",
            "Tempo": "N/A"
        }

        if address != "N/A":
            coords = get_coordinates_google(address)
            if coords:
                lat, lng = coords
                station_info = get_nearest_station_google(lat, lng)
                if station_info:
                    metro_data = {
                        "Estacao": station_info['name'],
                        "Distancia": f"{station_info['distance']:.0f}",
                        "Tempo": f"{station_info['duration']:.1f}"
                    }

        return {
            "nome": name,
            "endereco": address,
            "contato": contato,
            "cozinha": cozinha,
            "link": url,  # Adiciona URL para controle de duplicatas
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
        print("Depois, habilite estas APIs:")
        print("- Geocoding API")
        print("- Places API")
        print("- Distance Matrix API")
        return

    print("\nColetando links de restaurantes...")
    restaurants = get_restaurant_links()
    print(f"{len(restaurants)} novos restaurantes serão processados (ordenados alfabeticamente, limite: {MAX_RESTAURANTES}).\n")

    fieldnames = ["nome", "endereco", "contato", "cozinha", "link",
                 "Estacao", "Distancia", "Tempo"] + \
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
                    print(f"   Estação mais próxima: {data['Estacao']}")
                    print(f"   Distância: {data['Distancia']}m (~{data['Tempo']} min a pé)")
            else:
                print(f"⚠️ Falha ao processar restaurante {i}")

            time.sleep(0.5)  # Delay entre requisições

    print(f"\n✅ Concluído! Dados salvos em {CSV_FILE}")

if __name__ == "__main__":
    main()