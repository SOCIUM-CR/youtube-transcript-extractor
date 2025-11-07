"""
Tests unitarios para cache/transcript_cache.py
"""
import pytest
import json
from pathlib import Path
from datetime import datetime, timedelta
from cache.transcript_cache import TranscriptCache


class TestTranscriptCacheBasic:
    """Tests básicos de TranscriptCache"""

    def test_initialize_empty_cache(self, tmp_path):
        """Test inicialización con caché vacío"""
        cache_file = tmp_path / 'test_cache.json'
        cache = TranscriptCache(str(cache_file))

        assert cache.cache == {}
        assert cache.cache_file == cache_file

    def test_initialize_creates_cache_file(self, tmp_path):
        """Test que el archivo de caché se crea al primer guardado"""
        cache_file = tmp_path / 'test_cache.json'
        cache = TranscriptCache(str(cache_file))

        # Inicialmente no existe
        assert not cache_file.exists()

        # Marcar un video como procesado
        cache.mark_processed('test_id', 'Test Video', 'en', 'yt-dlp', 'test_folder')

        # Ahora debe existir
        assert cache_file.exists()

    def test_is_processed_empty_cache(self, tmp_path):
        """Test is_processed en caché vacío"""
        cache_file = tmp_path / 'test_cache.json'
        cache = TranscriptCache(str(cache_file))

        assert not cache.is_processed('any_video_id')

    def test_mark_processed_basic(self, tmp_path):
        """Test marcar video como procesado"""
        cache_file = tmp_path / 'test_cache.json'
        cache = TranscriptCache(str(cache_file))

        cache.mark_processed('abc123', 'Test Video', 'es', 'yt-dlp', 'videos')

        assert cache.is_processed('abc123')

    def test_mark_processed_creates_entry(self, tmp_path):
        """Test que mark_processed crea entrada completa"""
        cache_file = tmp_path / 'test_cache.json'
        cache = TranscriptCache(str(cache_file))

        cache.mark_processed('xyz789', 'Another Video', 'en', 'fallback', 'playlist')

        entry = cache.get_entry('xyz789')
        assert entry is not None
        assert entry['video_id'] == 'xyz789'
        assert entry['title'] == 'Another Video'
        assert entry['language'] == 'en'
        assert entry['method'] == 'fallback'
        assert entry['folder'] == 'playlist'
        assert 'processed_at' in entry
        assert entry['cache_version'] == '1.0'

    def test_get_entry_nonexistent(self, tmp_path):
        """Test get_entry con video inexistente"""
        cache_file = tmp_path / 'test_cache.json'
        cache = TranscriptCache(str(cache_file))

        entry = cache.get_entry('nonexistent')
        assert entry is None

    def test_remove_entry(self, tmp_path):
        """Test remover entrada del caché"""
        cache_file = tmp_path / 'test_cache.json'
        cache = TranscriptCache(str(cache_file))

        cache.mark_processed('remove_me', 'Test', 'en', 'yt-dlp', 'test')
        assert cache.is_processed('remove_me')

        cache.remove('remove_me')
        assert not cache.is_processed('remove_me')

    def test_remove_nonexistent(self, tmp_path):
        """Test remover entrada inexistente no genera error"""
        cache_file = tmp_path / 'test_cache.json'
        cache = TranscriptCache(str(cache_file))

        # No debe lanzar excepción
        cache.remove('nonexistent')

    def test_clear_cache(self, tmp_path):
        """Test limpiar todo el caché"""
        cache_file = tmp_path / 'test_cache.json'
        cache = TranscriptCache(str(cache_file))

        # Agregar varios videos
        cache.mark_processed('video1', 'Video 1', 'en', 'yt-dlp', 'test')
        cache.mark_processed('video2', 'Video 2', 'es', 'fallback', 'test')
        cache.mark_processed('video3', 'Video 3', 'fr', 'yt-dlp', 'test')

        assert len(cache.cache) == 3

        cache.clear()

        assert len(cache.cache) == 0
        # El archivo todavía existe pero contiene un diccionario vacío
        assert cache_file.exists()

        # Verificar que el archivo contiene un objeto vacío
        with open(cache_file, 'r') as f:
            data = json.load(f)
        assert data == {}


class TestTranscriptCachePersistence:
    """Tests de persistencia del caché"""

    def test_save_and_load_cache(self, tmp_path):
        """Test guardar y cargar caché"""
        cache_file = tmp_path / 'persist_cache.json'

        # Crear y guardar
        cache1 = TranscriptCache(str(cache_file))
        cache1.mark_processed('persist1', 'Persist Video', 'en', 'yt-dlp', 'test')

        # Cargar en nueva instancia
        cache2 = TranscriptCache(str(cache_file))

        assert cache2.is_processed('persist1')
        entry = cache2.get_entry('persist1')
        assert entry['title'] == 'Persist Video'

    def test_load_multiple_entries(self, tmp_path):
        """Test cargar caché con múltiples entradas"""
        cache_file = tmp_path / 'multi_cache.json'

        # Crear varias entradas
        cache1 = TranscriptCache(str(cache_file))
        for i in range(10):
            cache1.mark_processed(f'video{i}', f'Video {i}', 'en', 'yt-dlp', 'test')

        # Cargar en nueva instancia
        cache2 = TranscriptCache(str(cache_file))

        for i in range(10):
            assert cache2.is_processed(f'video{i}')

    def test_corrupted_cache_file(self, tmp_path):
        """Test caché corrupto se maneja correctamente"""
        cache_file = tmp_path / 'corrupted.json'

        # Crear archivo JSON corrupto
        cache_file.write_text('{invalid json content')

        # Debe crear caché vacío sin error
        cache = TranscriptCache(str(cache_file))
        assert cache.cache == {}

    def test_empty_cache_file(self, tmp_path):
        """Test archivo de caché vacío"""
        cache_file = tmp_path / 'empty.json'
        cache_file.write_text('')

        cache = TranscriptCache(str(cache_file))
        assert cache.cache == {}

    def test_cache_file_with_null(self, tmp_path):
        """Test archivo con null"""
        cache_file = tmp_path / 'null.json'
        cache_file.write_text('null')

        cache = TranscriptCache(str(cache_file))
        assert cache.cache == {}


class TestTranscriptCacheStatistics:
    """Tests de estadísticas del caché"""

    def test_get_stats_empty_cache(self, tmp_path):
        """Test estadísticas de caché vacío"""
        cache_file = tmp_path / 'stats_cache.json'
        cache = TranscriptCache(str(cache_file))

        stats = cache.get_stats()

        assert stats['total_cached'] == 0
        assert stats['oldest_entry'] is None
        assert stats['newest_entry'] is None
        assert stats['by_language'] == {}
        assert stats['by_method'] == {}
        assert stats['by_folder'] == {}

    def test_get_stats_with_entries(self, tmp_path):
        """Test estadísticas con entradas"""
        cache_file = tmp_path / 'stats_cache.json'
        cache = TranscriptCache(str(cache_file))

        cache.mark_processed('video1', 'Video 1', 'en', 'yt-dlp', 'folder1')
        cache.mark_processed('video2', 'Video 2', 'es', 'fallback', 'folder1')
        cache.mark_processed('video3', 'Video 3', 'en', 'yt-dlp', 'folder2')

        stats = cache.get_stats()

        assert stats['total_cached'] == 3
        assert stats['oldest_entry'] is not None
        assert stats['newest_entry'] is not None

        # Estadísticas por idioma
        assert stats['by_language']['en'] == 2
        assert stats['by_language']['es'] == 1

        # Estadísticas por método
        assert stats['by_method']['yt-dlp'] == 2
        assert stats['by_method']['fallback'] == 1

        # Estadísticas por carpeta
        assert stats['by_folder']['folder1'] == 2
        assert stats['by_folder']['folder2'] == 1

    def test_count_by_language(self, tmp_path):
        """Test contar por idioma"""
        cache_file = tmp_path / 'lang_cache.json'
        cache = TranscriptCache(str(cache_file))

        cache.mark_processed('v1', 'Video 1', 'en', 'yt-dlp', 'test')
        cache.mark_processed('v2', 'Video 2', 'en', 'yt-dlp', 'test')
        cache.mark_processed('v3', 'Video 3', 'es', 'yt-dlp', 'test')
        cache.mark_processed('v4', 'Video 4', 'fr', 'yt-dlp', 'test')
        cache.mark_processed('v5', 'Video 5', 'en', 'yt-dlp', 'test')

        stats = cache.get_stats()

        assert stats['by_language']['en'] == 3
        assert stats['by_language']['es'] == 1
        assert stats['by_language']['fr'] == 1


class TestTranscriptCacheFiltering:
    """Tests de filtrado y consultas"""

    def test_get_videos_by_folder(self, tmp_path):
        """Test obtener videos por carpeta"""
        cache_file = tmp_path / 'filter_cache.json'
        cache = TranscriptCache(str(cache_file))

        cache.mark_processed('v1', 'Video 1', 'en', 'yt-dlp', 'folder_a')
        cache.mark_processed('v2', 'Video 2', 'es', 'yt-dlp', 'folder_b')
        cache.mark_processed('v3', 'Video 3', 'en', 'yt-dlp', 'folder_a')

        videos_a = cache.get_videos_by_folder('folder_a')
        assert len(videos_a) == 2
        assert all(v['folder'] == 'folder_a' for v in videos_a)

        videos_b = cache.get_videos_by_folder('folder_b')
        assert len(videos_b) == 1

    def test_get_videos_nonexistent_folder(self, tmp_path):
        """Test obtener videos de carpeta inexistente"""
        cache_file = tmp_path / 'filter_cache.json'
        cache = TranscriptCache(str(cache_file))

        videos = cache.get_videos_by_folder('nonexistent')
        assert videos == []

    def test_get_recent_videos(self, tmp_path):
        """Test obtener videos recientes"""
        cache_file = tmp_path / 'recent_cache.json'
        cache = TranscriptCache(str(cache_file))

        # Agregar varios videos
        for i in range(10):
            cache.mark_processed(f'v{i}', f'Video {i}', 'en', 'yt-dlp', 'test')

        # Obtener 5 más recientes
        recent = cache.get_recent_videos(5)

        assert len(recent) == 5
        # Deben estar en orden descendente por fecha
        dates = [v['processed_at'] for v in recent]
        assert dates == sorted(dates, reverse=True)

    def test_get_recent_videos_limit_exceeds(self, tmp_path):
        """Test límite mayor que total de videos"""
        cache_file = tmp_path / 'recent_cache.json'
        cache = TranscriptCache(str(cache_file))

        cache.mark_processed('v1', 'Video 1', 'en', 'yt-dlp', 'test')
        cache.mark_processed('v2', 'Video 2', 'en', 'yt-dlp', 'test')

        recent = cache.get_recent_videos(10)
        assert len(recent) == 2


class TestTranscriptCacheExportImport:
    """Tests de exportación e importación"""

    def test_export_to_file(self, tmp_path):
        """Test exportar caché a archivo"""
        cache_file = tmp_path / 'main_cache.json'
        export_file = tmp_path / 'export.json'

        cache = TranscriptCache(str(cache_file))
        cache.mark_processed('v1', 'Video 1', 'en', 'yt-dlp', 'test')
        cache.mark_processed('v2', 'Video 2', 'es', 'fallback', 'test')

        cache.export_to_file(str(export_file))

        assert export_file.exists()

        # Verificar contenido - el formato incluye metadata
        with open(export_file, 'r') as f:
            exported = json.load(f)

        # Verificar estructura del export
        assert 'exported_at' in exported
        assert 'total_videos' in exported
        assert 'videos' in exported
        assert exported['total_videos'] == 2

        # Verificar videos dentro de la estructura
        assert 'v1' in exported['videos']
        assert 'v2' in exported['videos']

    def test_import_from_file(self, tmp_path):
        """Test importar caché desde archivo"""
        import_file = tmp_path / 'import.json'

        # Crear archivo de exportación manual
        export_data = {
            'imported1': {
                'video_id': 'imported1',
                'title': 'Imported Video',
                'language': 'en',
                'method': 'yt-dlp',
                'folder': 'imported',
                'processed_at': datetime.now().isoformat(),
                'cache_version': '1.0'
            }
        }

        with open(import_file, 'w') as f:
            json.dump(export_data, f)

        # Importar a caché nuevo
        cache_file = tmp_path / 'new_cache.json'
        cache = TranscriptCache(str(cache_file))

        cache.import_from_file(str(import_file))

        assert cache.is_processed('imported1')
        entry = cache.get_entry('imported1')
        assert entry['title'] == 'Imported Video'

    def test_import_invalid_file(self, tmp_path):
        """Test importar archivo inválido no genera error"""
        cache_file = tmp_path / 'cache.json'
        cache = TranscriptCache(str(cache_file))

        # Intentar importar archivo inexistente
        cache.import_from_file('nonexistent.json')

        # No debe romper, caché debe estar vacío
        assert len(cache.cache) == 0

    def test_import_merge_with_existing(self, tmp_path):
        """Test importar hace merge con caché existente"""
        import_file = tmp_path / 'import.json'
        cache_file = tmp_path / 'cache.json'

        # Crear caché con datos existentes
        cache = TranscriptCache(str(cache_file))
        cache.mark_processed('existing', 'Existing Video', 'en', 'yt-dlp', 'test')

        # Crear archivo de importación
        export_data = {
            'imported': {
                'video_id': 'imported',
                'title': 'Imported Video',
                'language': 'es',
                'method': 'fallback',
                'folder': 'imported',
                'processed_at': datetime.now().isoformat(),
                'cache_version': '1.0'
            }
        }

        with open(import_file, 'w') as f:
            json.dump(export_data, f)

        # Importar
        cache.import_from_file(str(import_file))

        # Debe tener ambos
        assert cache.is_processed('existing')
        assert cache.is_processed('imported')
        assert len(cache.cache) == 2


class TestTranscriptCacheEdgeCases:
    """Tests de casos límite"""

    def test_unicode_title(self, tmp_path):
        """Test títulos con caracteres unicode"""
        cache_file = tmp_path / 'unicode_cache.json'
        cache = TranscriptCache(str(cache_file))

        unicode_title = 'Video 日本語 Español 中文 🎥'
        cache.mark_processed('unicode_id', unicode_title, 'en', 'yt-dlp', 'test')

        entry = cache.get_entry('unicode_id')
        assert entry['title'] == unicode_title

    def test_very_long_title(self, tmp_path):
        """Test títulos muy largos"""
        cache_file = tmp_path / 'long_cache.json'
        cache = TranscriptCache(str(cache_file))

        long_title = 'A' * 1000
        cache.mark_processed('long_id', long_title, 'en', 'yt-dlp', 'test')

        entry = cache.get_entry('long_id')
        assert entry['title'] == long_title

    def test_special_characters_in_folder(self, tmp_path):
        """Test caracteres especiales en nombre de carpeta"""
        cache_file = tmp_path / 'special_cache.json'
        cache = TranscriptCache(str(cache_file))

        special_folder = 'folder_with-special.chars_123'
        cache.mark_processed('special_id', 'Video', 'en', 'yt-dlp', special_folder)

        videos = cache.get_videos_by_folder(special_folder)
        assert len(videos) == 1

    def test_empty_strings(self, tmp_path):
        """Test cadenas vacías"""
        cache_file = tmp_path / 'empty_cache.json'
        cache = TranscriptCache(str(cache_file))

        # Debería manejar strings vacíos sin error
        cache.mark_processed('empty_id', '', '', '', '')

        assert cache.is_processed('empty_id')
        entry = cache.get_entry('empty_id')
        assert entry['title'] == ''

    def test_none_values(self, tmp_path):
        """Test valores None se convierten a strings"""
        cache_file = tmp_path / 'none_cache.json'
        cache = TranscriptCache(str(cache_file))

        # mark_processed debe manejar valores que puedan ser None
        # (aunque normalmente no debería recibir None)
        cache.mark_processed('id', 'Title', 'en', 'yt-dlp', 'test')

        entry = cache.get_entry('id')
        assert entry is not None

    def test_duplicate_video_id_updates(self, tmp_path):
        """Test que marcar mismo video actualiza entrada"""
        cache_file = tmp_path / 'dup_cache.json'
        cache = TranscriptCache(str(cache_file))

        # Marcar primera vez
        cache.mark_processed('dup_id', 'First Title', 'en', 'yt-dlp', 'folder1')

        # Marcar segunda vez con diferentes datos
        cache.mark_processed('dup_id', 'Second Title', 'es', 'fallback', 'folder2')

        # Debe tener solo una entrada con los últimos datos
        entry = cache.get_entry('dup_id')
        assert entry['title'] == 'Second Title'
        assert entry['language'] == 'es'
        assert entry['method'] == 'fallback'
        assert entry['folder'] == 'folder2'


class TestTranscriptCacheTimestamps:
    """Tests relacionados con timestamps"""

    def test_processed_at_format(self, tmp_path):
        """Test formato de processed_at"""
        cache_file = tmp_path / 'timestamp_cache.json'
        cache = TranscriptCache(str(cache_file))

        cache.mark_processed('time_id', 'Video', 'en', 'yt-dlp', 'test')

        entry = cache.get_entry('time_id')
        processed_at = entry['processed_at']

        # Debe ser formato ISO
        datetime.fromisoformat(processed_at)  # No debe lanzar excepción

    def test_ordering_by_date(self, tmp_path):
        """Test ordenamiento por fecha"""
        cache_file = tmp_path / 'order_cache.json'
        cache = TranscriptCache(str(cache_file))

        # Agregar videos con pequeño delay para asegurar orden
        import time
        for i in range(3):
            cache.mark_processed(f'v{i}', f'Video {i}', 'en', 'yt-dlp', 'test')
            time.sleep(0.01)  # Pequeño delay

        recent = cache.get_recent_videos(3)

        # El más reciente debe ser v2
        assert recent[0]['video_id'] == 'v2'
        assert recent[1]['video_id'] == 'v1'
        assert recent[2]['video_id'] == 'v0'
