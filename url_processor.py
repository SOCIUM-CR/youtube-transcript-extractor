def process_urls_file(file_path):
    """Procesa un archivo de URLs y devuelve una lista limpia de URLs de YouTube."""
    urls = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            # Limpiar espacios y caracteres extra
            url = line.strip()
            
            # Ignorar líneas vacías
            if not url:
                continue
                
            # Asegurarse que es una URL de YouTube
            if 'youtube.com/watch' in url or 'youtu.be/' in url:
                urls.append(url)
    
    return urls

def save_urls_to_file(urls, output_file='video_urls.txt'):
    """Guarda las URLs procesadas en un archivo."""
    with open(output_file, 'w', encoding='utf-8') as f:
        for url in urls:
            f.write(url + '\n')
    
    print(f"Se guardaron {len(urls)} URLs en {output_file}")

if __name__ == "__main__":
    print("Pega las URLs de YouTube (una por línea)")
    print("Cuando termines, presiona Ctrl+D (Unix/Mac) o Ctrl+Z (Windows) y Enter")
    
    urls = []
    try:
        while True:
            line = input()
            if 'youtube.com/watch' in line or 'youtu.be/' in line:
                urls.append(line.strip())
    except (EOFError, KeyboardInterrupt):
        pass
    
    if urls:
        save_urls_to_file(urls)
        print("\nAhora puedes usar estas URLs con el script principal")