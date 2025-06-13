import re
import os
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs

def extract_video_id_from_text(text):
    """
    Extrae IDs de videos de YouTube de cualquier texto.
    """
    # Patrones para encontrar IDs de videos
    video_ids = set()
    
    # Buscar en objetos JSON y texto normal
    patterns = [
        # Patrones de URL directa
        r'(?:youtube\.com/(?:watch\?v=|embed/|v/)|youtu\.be/)([\w-]{11})',
        r'v=([\w-]{11})',
        # Patrones de JSON y datos estructurados
        r'\"videoId\"\s*:\s*\"([\w-]{11})\"',
        r'\"videoRenderer\"\s*:\s*{[^}]*\"videoId\"\s*:\s*\"([\w-]{11})\"',
        r'\"watchEndpoint\"\s*:\s*{[^}]*\"videoId\"\s*:\s*\"([\w-]{11})\"',
        r'\"videoPrimaryInfoRenderer[^}]*\"videoId\"\s*:\s*\"([\w-]{11})\"',
        # Patrones escapados
        r'/watch\\?v=([\w-]{11})',
        r'videoId\\?":\\?"([\w-]{11})',
        # Patrones de URL con comillas
        r'\"url\":\s*\"[^\"]*(?:youtube\.com/(?:watch\?v=|embed/|v/)|youtu\.be/)([\w-]{11})\"',
        # Patrones específicos de la página
        r'richItemRenderer.*?videoId\\?":\\?"([\w-]{11})',
        r'gridVideoRenderer.*?videoId\\?":\\?"([\w-]{11})',
        r'playlistVideoRenderer.*?videoId\\?":\\?"([\w-]{11})',
        r'compactVideoRenderer.*?videoId\\?":\\?"([\w-]{11})',
        r'endScreenVideoRenderer.*?videoId\\?":\\?"([\w-]{11})',
        # Búsqueda en datos serializados
        r'serializedShareEntity\\?":\\?"video_([\w-]{11})',
        r'watchEndpoint\\?":{[^}]*\\?"videoId\\?":\\?"([\w-]{11})',
    ]
    
    for pattern in patterns:
        # Usar re.DOTALL para que el punto coincida con saltos de línea
        matches = re.finditer(pattern, text, re.DOTALL)
        for match in matches:
            video_id = match.group(1)
            if video_id and len(video_id) == 11:  # Los IDs de YouTube tienen 11 caracteres
                video_ids.add(video_id)
    
    # Buscar en estructuras JSON
    try:
        # Encontrar objetos JSON en el texto
        json_matches = re.finditer(r'var ytInitialData = ({.*?});', text, re.DOTALL)
        for json_match in json_matches:
            try:
                json_data = json.loads(json_match.group(1))
                # Convertir el JSON a texto y buscar IDs
                json_text = json.dumps(json_data)
                for pattern in patterns:
                    matches = re.finditer(pattern, json_text)
                    for match in matches:
                        video_id = match.group(1)
                        if video_id and len(video_id) == 11:
                            video_ids.add(video_id)
            except:
                continue
    except:
        pass
    
    return video_ids

def extract_youtube_urls(html_content):
    """
    Extrae todas las URLs de videos de YouTube de un contenido HTML.
    """
    video_ids = set()
    
    # Extraer IDs directamente del HTML completo
    ids_from_html = extract_video_id_from_text(html_content)
    video_ids.update(ids_from_html)
    
    # Parsear el HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Buscar en scripts
    for script in soup.find_all('script'):
        if script.string:
            ids_from_script = extract_video_id_from_text(script.string)
            video_ids.update(ids_from_script)
    
    # Buscar en atributos específicos
    for element in soup.find_all(attrs={"data-video-id": True}):
        video_id = element.get('data-video-id')
        if video_id and len(video_id) == 11:
            video_ids.add(video_id)
    
    # Buscar en atributos href que contengan IDs de video
    for a in soup.find_all('a', href=True):
        ids_from_href = extract_video_id_from_text(a['href'])
        video_ids.update(ids_from_href)
    
    # Convertir IDs a URLs completas y filtrar duplicados
    youtube_urls = set()
    for video_id in video_ids:
        url = f'https://www.youtube.com/watch?v={video_id}'
        youtube_urls.add(url)
    
    return sorted(list(youtube_urls))

def save_urls_to_file(urls, directory_path):
    """
    Guarda las URLs extraídas en un archivo de texto.
    """
    os.makedirs(directory_path, exist_ok=True)
    output_file = os.path.join(directory_path, 'video_urls.txt')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for url in urls:
            f.write(f'{url}\n')

def main():
    """
    Función principal que lee el archivo de código fuente y extrae las URLs.
    """
    directory_path = '/Users/francomicalizzi/Downloads/Claude/youtube-extract'
    input_file = os.path.join(directory_path, 'codigo_fuente.txt')
    
    try:
        # Leer el contenido del archivo
        print(f"Leyendo código fuente desde '{input_file}'...")
        with open(input_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print(f"\nLongitud total del contenido: {len(html_content)} caracteres")
        
        # Extraer las URLs
        youtube_urls = extract_youtube_urls(html_content)
        
        # Mostrar resultados
        print(f"\nSe encontraron {len(youtube_urls)} URLs de YouTube:")
        for url in youtube_urls:
            print(url)
        
        # Guardar en archivo
        save_urls_to_file(youtube_urls, directory_path)
        print(f"\nLas URLs han sido guardadas en '{os.path.join(directory_path, 'video_urls.txt')}'")
        
    except FileNotFoundError:
        print(f"\nError: No se encontró el archivo '{input_file}'")
        print("Por favor, asegúrate de crear el archivo 'codigo_fuente.txt' con el código HTML antes de ejecutar el script.")
    except Exception as e:
        print(f"\nError al procesar el archivo: {str(e)}")

if __name__ == "__main__":
    main()