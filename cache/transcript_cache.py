"""
Sistema de caché para transcripciones procesadas.

Evita reprocesar videos ya extraídos, mejorando eficiencia y ahorrando recursos.
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List


class TranscriptCache:
    """
    Gestiona caché persistente de videos ya procesados.

    Almacena metadata de videos procesados en archivo JSON para evitar
    reprocesamiento innecesario. Útil cuando se procesan playlists con
    overlap o se ejecuta el programa múltiples veces.

    Attributes:
        cache_file (Path): Path al archivo de caché JSON
        cache (Dict): Diccionario en memoria con videos procesados
    """

    def __init__(self, cache_file: str = '.transcript_cache.json'):
        """
        Inicializa sistema de caché.

        Args:
            cache_file: Path al archivo JSON de caché (default: .transcript_cache.json)
        """
        self.cache_file = Path(cache_file)
        self.cache: Dict[str, dict] = self._load_cache()

    def _load_cache(self) -> Dict[str, dict]:
        """
        Carga caché desde archivo JSON.

        Returns:
            Diccionario con videos en caché, o dict vacío si no existe archivo

        Note:
            Si el archivo está corrupto, retorna dict vacío y muestra warning
        """
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Validar formato básico
                    if isinstance(data, dict):
                        return data
                    else:
                        print(f"⚠️  Cache file format invalid, starting fresh")
                        return {}
            except json.JSONDecodeError:
                print(f"⚠️  Cache file corrupted, starting fresh")
                return {}
            except Exception as e:
                print(f"⚠️  Error loading cache: {e}")
                return {}
        return {}

    def _save_cache(self):
        """
        Guarda caché a archivo JSON.

        Escribe el diccionario de caché al archivo JSON con formato legible.
        Si hay error al guardar, muestra warning pero no lanza excepción.
        """
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Error saving cache: {e}")

    def is_processed(self, video_id: str) -> bool:
        """
        Verifica si un video ya fue procesado.

        Args:
            video_id: YouTube video ID (11 caracteres)

        Returns:
            True si el video está en caché, False en caso contrario

        Examples:
            >>> cache = TranscriptCache()
            >>> cache.is_processed('dQw4w9WgXcQ')
            False
            >>> cache.mark_processed('dQw4w9WgXcQ', 'Title', 'en', 'yt-dlp', 'folder')
            >>> cache.is_processed('dQw4w9WgXcQ')
            True
        """
        return video_id in self.cache

    def get_entry(self, video_id: str) -> Optional[dict]:
        """
        Obtiene entrada completa de caché para un video.

        Args:
            video_id: YouTube video ID

        Returns:
            Diccionario con metadata del video, o None si no está en caché

        Example:
            >>> entry = cache.get_entry('dQw4w9WgXcQ')
            >>> if entry:
            ...     print(entry['title'])
            ...     print(entry['processed_at'])
        """
        return self.cache.get(video_id)

    def mark_processed(
        self,
        video_id: str,
        title: str,
        language: str,
        method: str,
        folder: str
    ):
        """
        Marca un video como procesado y guarda en caché.

        Args:
            video_id: YouTube video ID
            title: Título del video
            language: Idioma de la transcripción extraída
            method: Método usado ('yt-dlp' o 'youtube-transcript-api')
            folder: Carpeta donde se guardó la transcripción

        Example:
            >>> cache.mark_processed(
            ...     video_id='dQw4w9WgXcQ',
            ...     title='Example Video',
            ...     language='en',
            ...     method='yt-dlp',
            ...     folder='my_videos'
            ... )
        """
        self.cache[video_id] = {
            'video_id': video_id,
            'title': title,
            'language': language,
            'method': method,
            'folder': folder,
            'processed_at': datetime.now().isoformat(),
            'cache_version': '1.0'  # Para compatibilidad futura
        }
        self._save_cache()

    def remove(self, video_id: str) -> bool:
        """
        Remueve un video del caché.

        Args:
            video_id: YouTube video ID a remover

        Returns:
            True si el video fue removido, False si no estaba en caché

        Example:
            >>> cache.remove('dQw4w9WgXcQ')
            True
        """
        if video_id in self.cache:
            del self.cache[video_id]
            self._save_cache()
            return True
        return False

    def clear(self) -> int:
        """
        Limpia todo el caché.

        Returns:
            Número de entradas removidas

        Example:
            >>> count = cache.clear()
            >>> print(f"Removed {count} entries")
        """
        count = len(self.cache)
        self.cache = {}
        self._save_cache()
        return count

    def get_stats(self) -> dict:
        """
        Retorna estadísticas del caché.

        Returns:
            Diccionario con estadísticas:
            - total_cached: Número total de videos en caché
            - oldest_entry: Fecha del video más antiguo
            - newest_entry: Fecha del video más reciente
            - by_language: Conteo por idioma
            - by_method: Conteo por método de extracción
            - by_folder: Conteo por carpeta

        Example:
            >>> stats = cache.get_stats()
            >>> print(f"Total cached: {stats['total_cached']}")
            >>> print(f"Languages: {stats['by_language']}")
        """
        if not self.cache:
            return {
                'total_cached': 0,
                'oldest_entry': None,
                'newest_entry': None,
                'by_language': {},
                'by_method': {},
                'by_folder': {}
            }

        dates = [entry.get('processed_at') for entry in self.cache.values() if entry.get('processed_at')]

        return {
            'total_cached': len(self.cache),
            'oldest_entry': min(dates) if dates else None,
            'newest_entry': max(dates) if dates else None,
            'by_language': self._count_by_field('language'),
            'by_method': self._count_by_field('method'),
            'by_folder': self._count_by_field('folder')
        }

    def _count_by_field(self, field: str) -> Dict[str, int]:
        """
        Cuenta entradas agrupadas por campo.

        Args:
            field: Nombre del campo a contar ('language', 'method', 'folder')

        Returns:
            Diccionario con conteos por valor del campo
        """
        counts = {}
        for entry in self.cache.values():
            value = entry.get(field, 'unknown')
            counts[value] = counts.get(value, 0) + 1
        return counts

    def get_videos_by_folder(self, folder: str) -> List[dict]:
        """
        Obtiene todos los videos de una carpeta específica.

        Args:
            folder: Nombre de la carpeta

        Returns:
            Lista de entradas de videos en esa carpeta

        Example:
            >>> videos = cache.get_videos_by_folder('my_videos')
            >>> for video in videos:
            ...     print(video['title'])
        """
        return [
            entry for entry in self.cache.values()
            if entry.get('folder') == folder
        ]

    def get_recent_videos(self, limit: int = 10) -> List[dict]:
        """
        Obtiene los videos procesados más recientemente.

        Args:
            limit: Número máximo de videos a retornar

        Returns:
            Lista de entradas ordenadas por fecha (más reciente primero)

        Example:
            >>> recent = cache.get_recent_videos(5)
            >>> for video in recent:
            ...     print(f"{video['title']} - {video['processed_at']}")
        """
        entries = list(self.cache.values())
        # Ordenar por fecha de procesamiento (más reciente primero)
        entries.sort(
            key=lambda x: x.get('processed_at', ''),
            reverse=True
        )
        return entries[:limit]

    def export_to_file(self, output_file: str):
        """
        Exporta caché a archivo JSON legible.

        Args:
            output_file: Path al archivo de salida

        Example:
            >>> cache.export_to_file('cache_backup.json')
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(
                    {
                        'exported_at': datetime.now().isoformat(),
                        'total_videos': len(self.cache),
                        'videos': self.cache
                    },
                    f,
                    indent=2,
                    ensure_ascii=False
                )
            print(f"✅ Cache exported to {output_file}")
        except Exception as e:
            print(f"❌ Error exporting cache: {e}")

    def import_from_file(self, input_file: str) -> int:
        """
        Importa caché desde archivo JSON.

        Args:
            input_file: Path al archivo a importar

        Returns:
            Número de videos importados

        Example:
            >>> count = cache.import_from_file('cache_backup.json')
            >>> print(f"Imported {count} videos")
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Soportar tanto formato exportado como formato simple
            if 'videos' in data:
                videos = data['videos']
            else:
                videos = data

            count = 0
            for video_id, entry in videos.items():
                self.cache[video_id] = entry
                count += 1

            self._save_cache()
            print(f"✅ Imported {count} videos from {input_file}")
            return count

        except Exception as e:
            print(f"❌ Error importing cache: {e}")
            return 0

    def __len__(self) -> int:
        """Retorna número de videos en caché."""
        return len(self.cache)

    def __contains__(self, video_id: str) -> bool:
        """Permite usar 'in' operator: if video_id in cache"""
        return video_id in self.cache

    def __repr__(self) -> str:
        """Representación string del caché."""
        return f"TranscriptCache(file='{self.cache_file}', entries={len(self.cache)})"
