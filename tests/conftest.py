"""
Fixtures compartidas para tests de YouTube Transcript Extractor
"""
import pytest
import json
from pathlib import Path
from unittest.mock import Mock, MagicMock


@pytest.fixture
def sample_vtt_path():
    """Retorna path al archivo VTT de ejemplo."""
    return Path(__file__).parent / 'fixtures' / 'sample.vtt'


@pytest.fixture
def sample_vtt_content(sample_vtt_path):
    """Retorna contenido del archivo VTT de ejemplo."""
    with open(sample_vtt_path, 'r', encoding='utf-8') as f:
        return f.read()


@pytest.fixture
def valid_youtube_urls():
    """Lista de URLs válidas de YouTube para testing."""
    return [
        'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'https://youtu.be/dQw4w9WgXcQ',
        'https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s',
        'https://www.youtube.com/embed/dQw4w9WgXcQ',
        'https://m.youtube.com/watch?v=dQw4w9WgXcQ',
        'http://youtube.com/watch?v=dQw4w9WgXcQ',  # HTTP también válido
    ]


@pytest.fixture
def invalid_youtube_urls():
    """Lista de URLs inválidas para testing."""
    return [
        'https://vimeo.com/123456',
        'https://www.facebook.com/video',
        'not a url at all',
        '',
        'https://youtube.com/invalid',
        'https://www.youtube.com/watch?v=',  # Sin video ID
        'https://www.youtube.com/watch?v=abc',  # ID muy corto
    ]


@pytest.fixture
def sample_video_metadata():
    """Metadata de ejemplo de un video de YouTube."""
    return {
        'id': 'dQw4w9WgXcQ',
        'title': 'Example Video Title',
        'language': 'en',
        'duration': 212,
        'upload_date': '20091024',
        'uploader': 'Example Channel',
        'description': 'This is an example video description',
    }


@pytest.fixture
def sample_transcript_segments():
    """Segmentos de transcripción de ejemplo."""
    return [
        {
            'text': 'Hello everyone and welcome',
            'start': 0.5,
            'duration': 1.5,
            'start_formatted': '00:00:00'
        },
        {
            'text': 'to this YouTube video tutorial',
            'start': 2.0,
            'duration': 3.0,
            'start_formatted': '00:00:02'
        },
        {
            'text': 'Today we are going to learn about Python programming',
            'start': 5.5,
            'duration': 2.5,
            'start_formatted': '00:00:05'
        },
    ]


@pytest.fixture
def sample_transcript_dict(sample_transcript_segments):
    """Diccionario de transcripción completo de ejemplo."""
    full_text = ' '.join([seg['text'] for seg in sample_transcript_segments])
    return {
        'segments': sample_transcript_segments,
        'full_text': full_text,
        'detected_language': 'en',
        'selected_language': 'en',
        'method': 'yt-dlp'
    }


@pytest.fixture
def mock_extractor():
    """Mock del YouTubeTranscriptExtractor para testing."""
    from youtube_transcript_extractor import YouTubeTranscriptExtractor

    extractor = Mock(spec=YouTubeTranscriptExtractor)
    extractor.extract_video_id = YouTubeTranscriptExtractor.extract_video_id.__get__(extractor)
    extractor.validate_youtube_url = YouTubeTranscriptExtractor.validate_youtube_url.__get__(extractor)

    return extractor


@pytest.fixture
def temp_output_dir(tmp_path):
    """Crea directorio temporal para salida de tests."""
    output_dir = tmp_path / "transcripts"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def sample_urls_file(tmp_path):
    """Crea archivo temporal con URLs de ejemplo."""
    urls_file = tmp_path / "test_urls.txt"
    urls = [
        'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        '# Este es un comentario',
        'https://www.youtube.com/watch?v=abc123def45',
        '',  # Línea vacía
        'https://youtu.be/xyz789hij12',
    ]
    urls_file.write_text('\n'.join(urls))
    return urls_file


@pytest.fixture
def sample_ytdlp_output():
    """Output de ejemplo de yt-dlp --dump-json."""
    return json.dumps({
        'id': 'dQw4w9WgXcQ',
        'title': 'Example Video',
        'language': 'en',
        'duration': 212,
        'formats': [],
        'subtitles': {
            'en': [{'ext': 'vtt', 'url': 'http://example.com/sub.vtt'}]
        },
        'automatic_captions': {
            'en': [{'ext': 'vtt', 'url': 'http://example.com/auto.vtt'}],
            'es': [{'ext': 'vtt', 'url': 'http://example.com/auto_es.vtt'}]
        }
    })


@pytest.fixture
def mock_subprocess_run():
    """Mock de subprocess.run para tests."""
    mock = MagicMock()
    mock.return_value.returncode = 0
    mock.return_value.stdout = ''
    mock.return_value.stderr = ''
    return mock


@pytest.fixture(autouse=True)
def reset_colorama():
    """Reset colorama para cada test."""
    import colorama
    colorama.deinit()
    colorama.init(autoreset=True)
    yield
    colorama.deinit()
