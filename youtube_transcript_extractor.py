import subprocess
import re
import json
from typing import Optional, List
from pathlib import Path
import requests
import time
import os
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.table import Table
import colorama
from colorama import Fore, Style
import sys
import tempfile
import glob

class YouTubeTranscriptExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.console = Console()
        colorama.init(autoreset=True)

    def extract_video_id(self, url: str) -> Optional[str]:
        """Extrae el ID del video de una URL de YouTube."""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'youtu\.be\/([0-9A-Za-z_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def get_video_title(self, video_url: str) -> str:
        """Obtiene el título del video."""
        try:
            response = self.session.get(video_url)
            match = re.search(r'<title>(.+?)</title>', response.text)
            if match:
                title = match.group(1).replace(' - YouTube', '').strip()
                # Limpiar el título para usarlo como nombre de archivo
                title = re.sub(r'[<>:"/\\|?*]', '_', title)
                return title
            return self.extract_video_id(video_url)
        except:
            return self.extract_video_id(video_url)

    def _detect_video_language(self, video_url: str) -> str:
        """Detecta el idioma original del video usando metadata de yt-dlp."""
        try:
            cmd = ['yt-dlp', '--dump-json', '--no-download', video_url]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                metadata = json.loads(result.stdout)
                # Intentar obtener idioma de diferentes campos
                language = (metadata.get('language') or 
                           metadata.get('language_preference') or 
                           metadata.get('automatic_captions', {}).get('language') or
                           'en')  # Default inglés
                
                self.console.print(f'[blue]🌐 Idioma detectado: {language}[/blue]')
                return language
            else:
                self.console.print('[yellow]⚠️ No se pudo detectar idioma, usando inglés por defecto[/yellow]')
                return 'en'
                
        except Exception as e:
            self.console.print(f'[yellow]⚠️ Error detectando idioma: {str(e)}, usando inglés[/yellow]')
            return 'en'
    
    def get_transcript(self, video_url: str) -> Optional[dict]:
        """Obtiene la transcripción de un video de YouTube usando yt-dlp."""
        try:
            video_id = self.extract_video_id(video_url)
            if not video_id:
                return None
            
            # Detectar idioma original del video
            original_language = self._detect_video_language(video_url)
            
            # Crear directorio temporal para descargar subtítulos
            with tempfile.TemporaryDirectory() as temp_dir:
                # Configurar comando yt-dlp - incluir más idiomas
                cmd = [
                    'yt-dlp',
                    '--write-auto-sub',
                    '--write-sub', 
                    '--skip-download',
                    '--sub-lang', f'{original_language},es,en,fr,de,it,pt',
                    '--output', f'{temp_dir}/%(title)s.%(ext)s',
                    video_url
                ]
                
                # Ejecutar yt-dlp
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=temp_dir)
                
                if result.returncode != 0:
                    self.console.print(f'[bold yellow]⚠️ No hay transcripciones disponibles para este video[/bold yellow]')
                    return None
                
                # Buscar archivos de subtítulos descargados
                vtt_files = glob.glob(f'{temp_dir}/*.vtt')
                
                if not vtt_files:
                    self.console.print(f'[bold yellow]⚠️ No se descargaron transcripciones[/bold yellow]')
                    return None
                
                # Seleccionar el mejor archivo priorizando idioma original
                best_vtt = self._select_best_vtt_file_smart(vtt_files, original_language)
                
                if best_vtt:
                    # Procesar archivo VTT
                    with open(best_vtt, 'r', encoding='utf-8') as f:
                        vtt_content = f.read()
                    
                    transcript = self._process_vtt_transcript(vtt_content)
                    
                    if transcript:
                        # Agregar información del idioma usado
                        transcript['detected_language'] = original_language
                        transcript['selected_language'] = self._extract_language_from_filename(best_vtt)
                        self.console.print(f'[blue]📝 Idioma seleccionado: {transcript["selected_language"]}[/blue]')
                        return transcript
                
            return None
            
        except Exception as e:
            self.console.print(f'[bold red]❌ Error al obtener transcripción: {str(e)}[/bold red]')
            return None
    
    def _extract_language_from_filename(self, filename: str) -> str:
        """Extrae el código de idioma del nombre del archivo VTT."""
        # Buscar patrones como .es.vtt, .en.vtt, etc.
        import re
        match = re.search(r'\.([a-z]{2})\.vtt$', filename)
        return match.group(1) if match else 'unknown'
    
    def _select_best_vtt_file_smart(self, vtt_files: List[str], original_language: str) -> Optional[str]:
        """Selecciona el mejor archivo VTT priorizando idioma original."""
        if not vtt_files:
            return None
        
        self.console.print(f'[blue]🔍 Archivos VTT disponibles: {len(vtt_files)}[/blue]')
        for vtt_file in vtt_files:
            lang = self._extract_language_from_filename(vtt_file)
            self.console.print(f'[dim]  • {lang}: {Path(vtt_file).name}[/dim]')
        
        # 1. Priorizar idioma original detectado
        for vtt_file in vtt_files:
            if f'.{original_language}.vtt' in vtt_file:
                self.console.print(f'[green]✅ Seleccionado idioma original: {original_language}[/green]')
                return vtt_file
        
        # 2. Para videos en inglés/español, priorizar esos idiomas
        if original_language in ['en', 'es']:
            priority_langs = [original_language, 'en' if original_language == 'es' else 'es']
        else:
            # Para otros idiomas, traducir a inglés por defecto como requiere el usuario
            self.console.print(f'[yellow]⚠️ Video en {original_language}, usando inglés como solicitado[/yellow]')
            priority_langs = ['en', 'es']
        
        for lang in priority_langs:
            for vtt_file in vtt_files:
                if f'.{lang}.vtt' in vtt_file:
                    self.console.print(f'[green]✅ Seleccionado idioma fallback: {lang}[/green]')
                    return vtt_file
        
        # 3. Último recurso: primer archivo disponible
        selected_lang = self._extract_language_from_filename(vtt_files[0])
        self.console.print(f'[yellow]⚠️ Usando primer archivo disponible: {selected_lang}[/yellow]')
        return vtt_files[0]
    
    def _select_best_vtt_file(self, vtt_files: List[str]) -> Optional[str]:
        """Método legacy - mantener para compatibilidad."""
        return self._select_best_vtt_file_smart(vtt_files, 'es')
    
    def _process_vtt_transcript(self, vtt_content: str) -> dict:
        """Procesa el contenido VTT de yt-dlp."""
        transcript = {
            'segments': [],
            'full_text': []
        }

        try:
            lines = vtt_content.split('\n')
            i = 0
            
            while i < len(lines):
                line = lines[i].strip()
                
                # Buscar líneas de tiempo (formato: 00:00:00.000 --> 00:00:03.000)
                if '-->' in line:
                    time_match = re.match(r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})', line)
                    if time_match:
                        start_time = time_match.group(1)
                        end_time = time_match.group(2)
                        
                        # Convertir tiempo a segundos
                        start_seconds = self._time_to_seconds(start_time)
                        end_seconds = self._time_to_seconds(end_time)
                        duration = end_seconds - start_seconds
                        
                        # Leer las líneas de texto siguiente
                        i += 1
                        text_lines = []
                        while i < len(lines) and lines[i].strip() and '-->' not in lines[i]:
                            text_line = lines[i].strip()
                            if text_line:
                                # Limpiar texto VTT (remover tags de tiempo y formato)
                                clean_text = re.sub(r'<[^>]+>', '', text_line)  # Remover tags HTML
                                clean_text = re.sub(r'<\d{2}:\d{2}:\d{2}\.\d{3}>', '', clean_text)  # Remover timestamps inline
                                if clean_text:
                                    text_lines.append(clean_text)
                            i += 1
                        
                        # Unir el texto y crear segmento
                        if text_lines:
                            full_text = ' '.join(text_lines)
                            segment = {
                                'text': full_text.strip(),
                                'start': start_seconds,
                                'duration': duration,
                                'start_formatted': start_time
                            }
                            
                            if segment['text']:  # Solo agregar si hay texto
                                transcript['segments'].append(segment)
                                transcript['full_text'].append(segment['text'])
                        
                        continue
                
                i += 1
            
            transcript['full_text'] = ' '.join(transcript['full_text'])
            return transcript
            
        except Exception as e:
            self.console.print(f'[bold red]❌ Error al procesar VTT: {str(e)}[/bold red]')
            return None

    def _time_to_seconds(self, time_str: str) -> float:
        """Convierte tiempo VTT (HH:MM:SS.mmm) a segundos."""
        try:
            parts = time_str.split(':')
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds_parts = parts[2].split('.')
            seconds = int(seconds_parts[0])
            milliseconds = int(seconds_parts[1]) if len(seconds_parts) > 1 else 0
            
            total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000
            return total_seconds
        except:
            return 0.0

    def _format_timestamp(self, seconds: float) -> str:
        """Convierte segundos a formato timestamp (HH:MM:SS)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def create_directory_structure(self, base_dir: str, page_name: str) -> tuple:
        """Crea la estructura de directorios para las transcripciones."""
        page_dir = os.path.join(base_dir, page_name)
        timestamps_dir = os.path.join(page_dir, 'transcripts_with_timestamps')
        plain_dir = os.path.join(page_dir, 'transcripts_plain')
        
        os.makedirs(timestamps_dir, exist_ok=True)
        os.makedirs(plain_dir, exist_ok=True)
        
        return timestamps_dir, plain_dir

    def read_urls_from_file(self, file_path: str) -> List[str]:
        """Lee URLs desde un archivo de texto."""
        urls = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    # Ignorar comentarios y líneas vacías
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if 'youtube.com/watch' in line or 'youtu.be/' in line:
                            urls.append(line)
            return urls
        except Exception as e:
            self.console.print(f'[bold red]❌ Error al leer el archivo: {str(e)}[/bold red]')
            return []

    def process_videos_from_urls(self, urls: List[str], folder_name: str):
        """Procesa una lista de URLs de videos."""
        timestamps_dir, plain_dir = self.create_directory_structure('transcripts', folder_name)
        
        total_videos = len(urls)
        successful = 0
        
        with Progress(
            TextColumn('[bold blue]Procesando...', justify='right'),
            BarColumn(bar_width=None),
            '[progress.percentage]{task.percentage:>3.1f}%',
            '•',
            TextColumn('[bold green]{task.completed}/{task.total}'),
            '•',
            TimeRemainingColumn(),
            console=self.console
        ) as progress:
            
            task = progress.add_task('Extrayendo transcripciones', total=total_videos)
            
            for idx, video_url in enumerate(urls, 1):
                video_title = self.get_video_title(video_url)
                progress.update(task, description=f'[bold blue]📹 {video_title[:40]}...')
                
                transcript = self.get_transcript(video_url)
                if transcript and transcript['segments']:
                    # Crear nombre de archivo
                    video_id = self.extract_video_id(video_url)
                    filename = f"{idx:03d}_{video_title}_{video_id}"
                    
                    # Guardar texto completo
                    with open(os.path.join(plain_dir, f"{filename}.txt"), 'w', encoding='utf-8') as f:
                        f.write(transcript['full_text'])
                    
                    # Guardar con timestamps
                    with open(os.path.join(timestamps_dir, f"{filename}.txt"), 'w', encoding='utf-8') as f:
                        for segment in transcript['segments']:
                            f.write(f"[{segment['start_formatted']}] {segment['text']}\n")
                    
                    successful += 1
                    
                progress.advance(task)
                time.sleep(0.5)
        
        # Mostrar resumen final
        self.console.print()
        if successful == total_videos:
            success_text = f'''[bold green]✅ ¡Procesamiento completado exitosamente!

📊 Estadísticas:
   • Videos procesados: {successful}/{total_videos}
   • Éxito: 100%

📁 Archivos guardados en:
   • Texto plano: {plain_dir}
   • Con timestamps: {timestamps_dir}'''
            self.console.print(Panel(success_text, title='[bold green]🎉 Éxito Total', border_style='green'))
        else:
            warning_text = f'''[bold yellow]⚠️  Procesamiento completado con algunos errores

📊 Estadísticas:
   • Videos procesados: {successful}/{total_videos}
   • Éxito: {(successful/total_videos)*100:.1f}%
   • Errores: {total_videos-successful}

📁 Archivos guardados en:
   • Texto plano: {plain_dir}
   • Con timestamps: {timestamps_dir}'''
            self.console.print(Panel(warning_text, title='[bold yellow]⚠️  Procesamiento Completado', border_style='yellow'))

    def validate_youtube_url(self, url: str) -> bool:
        """Valida si una URL es de YouTube."""
        youtube_patterns = [
            r'youtube\.com/watch\?v=',
            r'youtu\.be/',
            r'youtube\.com/playlist\?list=',
            r'youtube\.com/embed/'
        ]
        return any(re.search(pattern, url) for pattern in youtube_patterns)
    
    def get_playlist_urls(self, playlist_url: str) -> List[str]:
        """Extrae URLs de videos de una playlist usando youtube_extractor_list.py"""
        try:
            from youtube_extractor_list import extract_playlist_urls
            import tempfile
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
                extract_playlist_urls(playlist_url, tmp_file.name)
                return self.read_urls_from_file(tmp_file.name)
        except Exception as e:
            self.console.print(f'[bold red]❌ Error al extraer playlist: {str(e)}[/bold red]')
            return []
    
    def show_welcome(self):
        """Muestra la pantalla de bienvenida."""
        self.console.clear()
        welcome_text = Text('🎥 YouTube Transcript Extractor', style='bold magenta')
        welcome_text.stylize('bold cyan', 0, 3)  # emoji
        
        self.console.print(Panel.fit(
            welcome_text,
            subtitle='[italic]Extrae y organiza transcripciones de videos de YouTube[/italic]',
            border_style='magenta'
        ))
        self.console.print()

def show_menu(extractor):
    """Muestra el menú principal y retorna la opción seleccionada."""
    # Mostrar opciones del menú principal
    table = Table(show_header=True, header_style='bold blue')
    table.add_column('#', style='bold', width=3)
    table.add_column('Opción', style='cyan')
    table.add_column('Descripción', style='dim')
    
    table.add_row('1', '🎥 Video individual', 'Extraer transcripción de un solo video')
    table.add_row('2', '📋 Lista de URLs', 'Procesar URLs desde archivo video_urls.txt') 
    table.add_row('3', '📂 Playlist de YouTube', 'Extraer todos los videos de una playlist')
    table.add_row('4', '🔍 Buscar en código HTML', 'Encontrar URLs de YouTube en código fuente')
    table.add_row('5', '❌ Salir', 'Cerrar la aplicación')
    
    extractor.console.print(Panel(table, title='[bold]🚀 ¿Qué deseas hacer?', border_style='blue'))
    
    choice = Prompt.ask(
        '\n[bold yellow]👉 Selecciona una opción[/bold yellow]', 
        choices=['1', '2', '3', '4', '5'], 
        default='1'
    )
    
    return choice

def main():
    extractor = YouTubeTranscriptExtractor()
    
    try:
        extractor.show_welcome()
        
        # Loop principal - regresar al menú después de cada operación
        while True:
            choice = show_menu(extractor)
            
            if choice == '5':
                extractor.console.print('[bold cyan]👋 ¡Hasta luego![/bold cyan]')
                break
            
            urls = []
            folder_name = ''
            
            if choice == '1':
                # Video individual
                extractor.console.print('\n[bold cyan]🎥 Procesamiento de video individual[/bold cyan]')
                
                while True:
                    video_url = Prompt.ask('[yellow]Introduce la URL del video de YouTube[/yellow]')
                    
                    if extractor.validate_youtube_url(video_url):
                        title = extractor.get_video_title(video_url)
                        extractor.console.print(f'[green]✅ Video válido encontrado: {title}[/green]')
                        
                        if Confirm.ask('¿Proceder con este video?'):
                            urls = [video_url]
                            folder_name = 'single_videos'
                            break
                    else:
                        extractor.console.print('[bold red]❌ URL no válida. Debe ser una URL de YouTube.[/bold red]')
                        if not Confirm.ask('¿Intentar con otra URL?'):
                            break
            
            elif choice == '2':
                # Lista de URLs desde archivo
                extractor.console.print('\n[bold cyan]📋 Procesamiento desde archivo[/bold cyan]')
                
                file_path = Prompt.ask('[yellow]Nombre del archivo[/yellow]', default='video_urls.txt')
                
                if not os.path.exists(file_path):
                    extractor.console.print(f'[bold red]❌ No se encontró el archivo: {file_path}[/bold red]')
                    extractor.console.print('[dim]💡 Asegúrate de que el archivo existe y contiene URLs de YouTube, una por línea.[/dim]')
                    continue
                    
                urls = extractor.read_urls_from_file(file_path)
                if not urls:
                    extractor.console.print('[bold red]❌ No se encontraron URLs válidas en el archivo[/bold red]')
                    continue
                
                extractor.console.print(f'[green]✅ Se encontraron {len(urls)} URLs válidas[/green]')
                
                # Mostrar preview de las primeras URLs
                if len(urls) <= 5:
                    for i, url in enumerate(urls, 1):
                        title = extractor.get_video_title(url)
                        extractor.console.print(f'   {i}. {title[:60]}...')
                else:
                    for i in range(5):
                        title = extractor.get_video_title(urls[i])
                        extractor.console.print(f'   {i+1}. {title[:60]}...')
                    extractor.console.print(f'   ... y {len(urls)-5} videos más')
                
                if not Confirm.ask(f'\n¿Procesar estos {len(urls)} videos?'):
                    continue
                    
                folder_name = Prompt.ask('[yellow]Nombre de la carpeta para las transcripciones[/yellow]', default='transcripts_batch')
                
            elif choice == '3':
                # Playlist de YouTube
                extractor.console.print('\n[bold cyan]📂 Procesamiento de playlist[/bold cyan]')
                
                while True:
                    playlist_url = Prompt.ask('[yellow]Introduce la URL de la playlist de YouTube[/yellow]')
                    
                    if 'playlist?list=' in playlist_url:
                        extractor.console.print('[blue]🔍 Extrayendo videos de la playlist...[/blue]')
                        urls = extractor.get_playlist_urls(playlist_url)
                        
                        if urls:
                            extractor.console.print(f'[green]✅ Se encontraron {len(urls)} videos en la playlist[/green]')
                            
                            # Mostrar preview de algunos videos
                            if len(urls) <= 3:
                                for i, url in enumerate(urls, 1):
                                    title = extractor.get_video_title(url)
                                    extractor.console.print(f'   {i}. {title[:60]}...')
                            else:
                                for i in range(3):
                                    title = extractor.get_video_title(urls[i])
                                    extractor.console.print(f'   {i+1}. {title[:60]}...')
                                extractor.console.print(f'   ... y {len(urls)-3} videos más')
                            
                            if Confirm.ask(f'\n¿Procesar estos {len(urls)} videos de la playlist?'):
                                break
                        else:
                            extractor.console.print('[bold red]❌ No se pudieron extraer videos de la playlist[/bold red]')
                            if not Confirm.ask('¿Intentar con otra URL de playlist?'):
                                break
                    else:
                        extractor.console.print('[bold red]❌ URL no válida. Debe ser una URL de playlist de YouTube.[/bold red]')
                        if not Confirm.ask('¿Intentar con otra URL?'):
                            break
                
                folder_name = Prompt.ask('[yellow]Nombre de la carpeta para las transcripciones[/yellow]', default='playlist_transcripts')
                
            elif choice == '4':
                # Buscar en código HTML
                extractor.console.print('\n[bold cyan]🔍 Búsqueda en código HTML[/bold cyan]')
                extractor.console.print('[dim]Esta opción busca URLs de YouTube en el archivo "codigo_fuente.txt"[/dim]')
                
                if not os.path.exists('codigo_fuente.txt'):
                    extractor.console.print('[bold red]❌ No se encontró el archivo "codigo_fuente.txt"[/bold red]')
                    extractor.console.print('[dim]💡 Crea el archivo "codigo_fuente.txt" y pega el código HTML que contiene los videos.[/dim]')
                    
                    if Confirm.ask('¿Quieres usar otro archivo?'):
                        html_file = Prompt.ask('[yellow]Nombre del archivo HTML[/yellow]')
                        if not os.path.exists(html_file):
                            extractor.console.print(f'[bold red]❌ No se encontró el archivo: {html_file}[/bold red]')
                            continue
                    else:
                        continue
                else:
                    html_file = 'codigo_fuente.txt'
                
                extractor.console.print('[blue]🔍 Buscando URLs de YouTube en el código...[/blue]')
                
                try:
                    from yt_url_finder import extract_youtube_urls
                    
                    with open(html_file, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    found_urls = extract_youtube_urls(html_content)
                    
                    if found_urls:
                        extractor.console.print(f'[green]✅ Se encontraron {len(found_urls)} URLs de YouTube[/green]')
                        
                        # Mostrar preview de URLs encontradas
                        preview_count = min(5, len(found_urls))
                        for i in range(preview_count):
                            video_id = extractor.extract_video_id(found_urls[i])
                            extractor.console.print(f'   {i+1}. Video ID: {video_id}')
                        
                        if len(found_urls) > 5:
                            extractor.console.print(f'   ... y {len(found_urls)-5} videos más')
                        
                        if Confirm.ask(f'\n¿Procesar estos {len(found_urls)} videos encontrados?'):
                            urls = found_urls
                        else:
                            continue
                    else:
                        extractor.console.print('[bold red]❌ No se encontraron URLs de YouTube en el archivo[/bold red]')
                        continue
                        
                except ImportError:
                    extractor.console.print('[bold red]❌ Error: No se pudo importar yt_url_finder.py[/bold red]')
                    continue
                except Exception as e:
                    extractor.console.print(f'[bold red]❌ Error al procesar el archivo HTML: {str(e)}[/bold red]')
                    continue
                
                folder_name = Prompt.ask('[yellow]Nombre de la carpeta para las transcripciones[/yellow]', default='html_extracted_transcripts')
            
            # Procesar los videos
            if urls and folder_name:
                extractor.console.print(f'\n[bold green]🚀 Iniciando extracción de {len(urls)} video(s)...[/bold green]')
                extractor.process_videos_from_urls(urls, folder_name)
                
                # Pausa antes de regresar al menú
                extractor.console.print('\n[dim]⏸️  Presiona Enter para regresar al menú principal...[/dim]')
                input()
            else:
                extractor.console.print('[bold red]❌ No se encontraron videos para procesar[/bold red]')
                extractor.console.print('\n[dim]⏸️  Presiona Enter para regresar al menú principal...[/dim]')
                input()
    
    except KeyboardInterrupt:
        extractor.console.print('\n[bold yellow]⏹️  Proceso interrumpido por el usuario[/bold yellow]')
    except Exception as e:
        extractor.console.print(f'\n[bold red]💥 Error inesperado: {str(e)}[/bold red]')
        extractor.console.print('[dim]Si el problema persiste, revisa que todas las dependencias estén instaladas correctamente.[/dim]')

if __name__ == '__main__':
    main()