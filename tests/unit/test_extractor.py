"""
Tests unitarios para YouTubeTranscriptExtractor
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from youtube_transcript_extractor import YouTubeTranscriptExtractor


class TestExtractVideoId:
    """Tests para extract_video_id()"""

    def test_extract_from_standard_url(self):
        """Test extracción desde URL estándar watch?v="""
        extractor = YouTubeTranscriptExtractor()
        url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        video_id = extractor.extract_video_id(url)
        assert video_id == 'dQw4w9WgXcQ'

    def test_extract_from_short_url(self):
        """Test extracción desde URL corta youtu.be"""
        extractor = YouTubeTranscriptExtractor()
        url = 'https://youtu.be/dQw4w9WgXcQ'
        video_id = extractor.extract_video_id(url)
        assert video_id == 'dQw4w9WgXcQ'

    def test_extract_with_timestamp(self):
        """Test extracción con parámetro de timestamp"""
        extractor = YouTubeTranscriptExtractor()
        url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s'
        video_id = extractor.extract_video_id(url)
        assert video_id == 'dQw4w9WgXcQ'

    def test_extract_from_embed_url(self):
        """Test extracción desde URL embed"""
        extractor = YouTubeTranscriptExtractor()
        url = 'https://www.youtube.com/embed/dQw4w9WgXcQ'
        video_id = extractor.extract_video_id(url)
        assert video_id == 'dQw4w9WgXcQ'

    def test_extract_from_mobile_url(self):
        """Test extracción desde URL móvil"""
        extractor = YouTubeTranscriptExtractor()
        url = 'https://m.youtube.com/watch?v=dQw4w9WgXcQ'
        video_id = extractor.extract_video_id(url)
        assert video_id == 'dQw4w9WgXcQ'

    def test_extract_with_playlist(self):
        """Test extracción con parámetros de playlist"""
        extractor = YouTubeTranscriptExtractor()
        url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf'
        video_id = extractor.extract_video_id(url)
        assert video_id == 'dQw4w9WgXcQ'

    def test_extract_from_http(self):
        """Test extracción desde HTTP (no HTTPS)"""
        extractor = YouTubeTranscriptExtractor()
        url = 'http://youtube.com/watch?v=dQw4w9WgXcQ'
        video_id = extractor.extract_video_id(url)
        assert video_id == 'dQw4w9WgXcQ'

    def test_invalid_url_returns_none(self):
        """Test URL inválida retorna None"""
        extractor = YouTubeTranscriptExtractor()
        url = 'https://vimeo.com/123456'
        video_id = extractor.extract_video_id(url)
        assert video_id is None

    def test_empty_url_returns_none(self):
        """Test URL vacía retorna None"""
        extractor = YouTubeTranscriptExtractor()
        video_id = extractor.extract_video_id('')
        assert video_id is None

    def test_video_id_exactly_11_chars(self):
        """Test que el video ID extraído siempre tenga 11 caracteres"""
        extractor = YouTubeTranscriptExtractor()
        urls = [
            'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'https://youtu.be/abc123DEF45',
            'https://www.youtube.com/watch?v=_-123456789'
        ]
        for url in urls:
            video_id = extractor.extract_video_id(url)
            assert len(video_id) == 11


class TestValidateYoutubeUrl:
    """Tests para validate_youtube_url()"""

    def test_valid_watch_url(self, valid_youtube_urls):
        """Test URLs válidas de YouTube"""
        extractor = YouTubeTranscriptExtractor()
        for url in valid_youtube_urls:
            assert extractor.validate_youtube_url(url) is True

    def test_invalid_urls(self, invalid_youtube_urls):
        """Test URLs inválidas"""
        extractor = YouTubeTranscriptExtractor()
        for url in invalid_youtube_urls:
            assert extractor.validate_youtube_url(url) is False

    def test_playlist_url_is_valid(self):
        """Test URL de playlist es válida"""
        extractor = YouTubeTranscriptExtractor()
        url = 'https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf'
        assert extractor.validate_youtube_url(url) is True

    def test_case_insensitive(self):
        """Test validación es case-insensitive"""
        extractor = YouTubeTranscriptExtractor()
        urls = [
            'https://WWW.YOUTUBE.COM/watch?v=dQw4w9WgXcQ',
            'https://YOUTU.BE/dQw4w9WgXcQ',
        ]
        for url in urls:
            assert extractor.validate_youtube_url(url) is True


class TestTimeConversion:
    """Tests para conversión de timestamps"""

    def test_time_to_seconds_basic(self):
        """Test conversión básica de tiempo a segundos"""
        extractor = YouTubeTranscriptExtractor()
        assert extractor._time_to_seconds('00:00:05.000') == 5.0

    def test_time_to_seconds_with_minutes(self):
        """Test conversión con minutos"""
        extractor = YouTubeTranscriptExtractor()
        assert extractor._time_to_seconds('00:01:30.000') == 90.0

    def test_time_to_seconds_with_hours(self):
        """Test conversión con horas"""
        extractor = YouTubeTranscriptExtractor()
        assert extractor._time_to_seconds('01:30:45.000') == 5445.0

    def test_time_to_seconds_with_milliseconds(self):
        """Test conversión con milisegundos"""
        extractor = YouTubeTranscriptExtractor()
        assert extractor._time_to_seconds('00:00:05.500') == 5.5

    def test_format_timestamp_seconds_only(self):
        """Test formateo de timestamp con solo segundos"""
        extractor = YouTubeTranscriptExtractor()
        assert extractor._format_timestamp(5.0) == '00:00:05'

    def test_format_timestamp_with_minutes(self):
        """Test formateo con minutos"""
        extractor = YouTubeTranscriptExtractor()
        assert extractor._format_timestamp(90.0) == '00:01:30'

    def test_format_timestamp_with_hours(self):
        """Test formateo con horas"""
        extractor = YouTubeTranscriptExtractor()
        assert extractor._format_timestamp(5445.0) == '01:30:45'

    def test_format_timestamp_zero(self):
        """Test formateo de timestamp cero"""
        extractor = YouTubeTranscriptExtractor()
        assert extractor._format_timestamp(0.0) == '00:00:00'

    def test_roundtrip_conversion(self):
        """Test conversión ida y vuelta"""
        extractor = YouTubeTranscriptExtractor()
        original = '01:23:45.000'
        seconds = extractor._time_to_seconds(original)
        formatted = extractor._format_timestamp(seconds)
        assert formatted == '01:23:45'


class TestProcessVttTranscript:
    """Tests para procesamiento de archivos VTT"""

    def test_process_basic_vtt(self, sample_vtt_content):
        """Test procesamiento básico de VTT"""
        extractor = YouTubeTranscriptExtractor()
        result = extractor._process_vtt_transcript(sample_vtt_content)

        assert result is not None
        assert 'segments' in result
        assert 'full_text' in result
        assert len(result['segments']) > 0

    def test_vtt_segments_have_required_fields(self, sample_vtt_content):
        """Test que segmentos VTT tengan campos requeridos"""
        extractor = YouTubeTranscriptExtractor()
        result = extractor._process_vtt_transcript(sample_vtt_content)

        for segment in result['segments']:
            assert 'text' in segment
            assert 'start' in segment
            assert 'duration' in segment
            assert 'start_formatted' in segment

    def test_vtt_text_is_cleaned(self, sample_vtt_content):
        """Test que texto VTT esté limpio de tags HTML"""
        extractor = YouTubeTranscriptExtractor()
        result = extractor._process_vtt_transcript(sample_vtt_content)

        # Verificar que no hay tags HTML en el texto
        full_text = result['full_text']
        assert '<c>' not in full_text
        assert '</c>' not in full_text
        assert '<' not in full_text or '>' not in full_text

    def test_vtt_full_text_not_empty(self, sample_vtt_content):
        """Test que full_text no esté vacío"""
        extractor = YouTubeTranscriptExtractor()
        result = extractor._process_vtt_transcript(sample_vtt_content)

        assert result['full_text']
        assert len(result['full_text']) > 0

    def test_vtt_segments_in_order(self, sample_vtt_content):
        """Test que segmentos estén en orden cronológico"""
        extractor = YouTubeTranscriptExtractor()
        result = extractor._process_vtt_transcript(sample_vtt_content)

        segments = result['segments']
        for i in range(len(segments) - 1):
            assert segments[i]['start'] <= segments[i + 1]['start']

    def test_empty_vtt_returns_empty_result(self):
        """Test VTT vacío retorna resultado vacío"""
        extractor = YouTubeTranscriptExtractor()
        result = extractor._process_vtt_transcript('WEBVTT\n\n')

        assert result is not None
        assert len(result['segments']) == 0
        assert result['full_text'] == ''


class TestReadUrlsFromFile:
    """Tests para lectura de URLs desde archivo"""

    def test_read_valid_urls(self, sample_urls_file):
        """Test lectura de URLs válidas"""
        extractor = YouTubeTranscriptExtractor()
        urls = extractor.read_urls_from_file(str(sample_urls_file))

        assert len(urls) == 3  # Solo las 3 URLs válidas
        assert 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' in urls

    def test_ignore_comments(self, sample_urls_file):
        """Test que ignora líneas con comentarios"""
        extractor = YouTubeTranscriptExtractor()
        urls = extractor.read_urls_from_file(str(sample_urls_file))

        # No debe incluir la línea que empieza con #
        assert not any(url.startswith('#') for url in urls)

    def test_ignore_empty_lines(self, sample_urls_file):
        """Test que ignora líneas vacías"""
        extractor = YouTubeTranscriptExtractor()
        urls = extractor.read_urls_from_file(str(sample_urls_file))

        # No debe incluir strings vacíos
        assert '' not in urls

    def test_nonexistent_file_returns_empty(self):
        """Test archivo inexistente retorna lista vacía"""
        extractor = YouTubeTranscriptExtractor()
        urls = extractor.read_urls_from_file('/nonexistent/file.txt')

        assert urls == []

    def test_file_with_only_comments(self, tmp_path):
        """Test archivo con solo comentarios retorna vacío"""
        file_path = tmp_path / 'comments_only.txt'
        file_path.write_text('# Comment 1\n# Comment 2\n# Comment 3')

        extractor = YouTubeTranscriptExtractor()
        urls = extractor.read_urls_from_file(str(file_path))

        assert urls == []


class TestCreateDirectoryStructure:
    """Tests para creación de estructura de directorios"""

    def test_create_basic_structure(self, temp_output_dir):
        """Test creación de estructura básica"""
        extractor = YouTubeTranscriptExtractor()
        timestamps_dir, plain_dir = extractor.create_directory_structure(
            str(temp_output_dir), 'test_folder'
        )

        assert timestamps_dir.endswith('transcripts_with_timestamps')
        assert plain_dir.endswith('transcripts_plain')

    def test_directories_are_created(self, temp_output_dir):
        """Test que directorios se crean físicamente"""
        import os
        extractor = YouTubeTranscriptExtractor()
        timestamps_dir, plain_dir = extractor.create_directory_structure(
            str(temp_output_dir), 'test_folder'
        )

        assert os.path.exists(timestamps_dir)
        assert os.path.exists(plain_dir)
        assert os.path.isdir(timestamps_dir)
        assert os.path.isdir(plain_dir)

    def test_nested_folder_names(self, temp_output_dir):
        """Test con nombres de carpeta con caracteres especiales"""
        extractor = YouTubeTranscriptExtractor()
        folder_name = 'my_videos_2025'
        timestamps_dir, plain_dir = extractor.create_directory_structure(
            str(temp_output_dir), folder_name
        )

        assert folder_name in timestamps_dir
        assert folder_name in plain_dir


class TestExtractLanguageFromFilename:
    """Tests para extracción de idioma desde nombre de archivo"""

    def test_extract_english(self):
        """Test extracción de código de idioma inglés"""
        extractor = YouTubeTranscriptExtractor()
        filename = '/tmp/video_title.en.vtt'
        lang = extractor._extract_language_from_filename(filename)
        assert lang == 'en'

    def test_extract_spanish(self):
        """Test extracción de código de idioma español"""
        extractor = YouTubeTranscriptExtractor()
        filename = '/tmp/video_title.es.vtt'
        lang = extractor._extract_language_from_filename(filename)
        assert lang == 'es'

    def test_extract_french(self):
        """Test extracción de código de idioma francés"""
        extractor = YouTubeTranscriptExtractor()
        filename = '/tmp/video_title.fr.vtt'
        lang = extractor._extract_language_from_filename(filename)
        assert lang == 'fr'

    def test_no_language_code_returns_unknown(self):
        """Test archivo sin código de idioma retorna 'unknown'"""
        extractor = YouTubeTranscriptExtractor()
        filename = '/tmp/video_title.vtt'
        lang = extractor._extract_language_from_filename(filename)
        assert lang == 'unknown'


@pytest.mark.integration
class TestGetVideoTitle:
    """Tests de integración para obtención de título de video"""

    @pytest.mark.network
    def test_get_title_from_real_url(self):
        """Test obtención de título desde URL real (requiere red)"""
        extractor = YouTubeTranscriptExtractor()
        url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'

        # Este test requiere conexión a internet
        title = extractor.get_video_title(url)

        assert title is not None
        assert len(title) > 0
        assert title != 'dQw4w9WgXcQ'  # No debe ser solo el ID

    def test_get_title_invalid_url_returns_video_id(self):
        """Test URL inválida retorna video ID como fallback"""
        extractor = YouTubeTranscriptExtractor()
        url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'

        with patch.object(extractor.session, 'get', side_effect=Exception('Network error')):
            title = extractor.get_video_title(url)
            # Debería retornar el video ID como fallback
            assert title == 'dQw4w9WgXcQ'
