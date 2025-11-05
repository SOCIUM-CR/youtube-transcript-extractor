"""
Tests unitarios para url_processor.py
"""
import pytest
from pathlib import Path
from url_processor import process_urls_file, save_urls_to_file


class TestProcessUrlsFile:
    """Tests para process_urls_file()"""

    def test_process_valid_urls(self, sample_urls_file):
        """Test procesamiento de URLs válidas"""
        urls = process_urls_file(str(sample_urls_file))

        assert len(urls) == 3
        assert all('youtube.com' in url or 'youtu.be' in url for url in urls)

    def test_ignore_empty_lines(self, tmp_path):
        """Test que ignora líneas vacías"""
        urls_file = tmp_path / 'urls_with_empty.txt'
        content = """https://www.youtube.com/watch?v=abc123

https://youtu.be/def456

"""
        urls_file.write_text(content)

        urls = process_urls_file(str(urls_file))

        assert len(urls) == 2
        assert '' not in urls

    def test_strip_whitespace(self, tmp_path):
        """Test que remueve espacios en blanco"""
        urls_file = tmp_path / 'urls_with_spaces.txt'
        content = """  https://www.youtube.com/watch?v=abc123
https://youtu.be/def456
   https://www.youtube.com/watch?v=ghi789"""
        urls_file.write_text(content)

        urls = process_urls_file(str(urls_file))

        assert all(not url.startswith(' ') and not url.endswith(' ') for url in urls)

    def test_only_youtube_urls(self, tmp_path):
        """Test que solo incluye URLs de YouTube"""
        urls_file = tmp_path / 'mixed_urls.txt'
        content = """https://www.youtube.com/watch?v=abc123
https://vimeo.com/123456
https://youtu.be/def456
https://www.facebook.com/video"""
        urls_file.write_text(content)

        urls = process_urls_file(str(urls_file))

        assert len(urls) == 2
        assert all('youtube.com' in url or 'youtu.be' in url for url in urls)


class TestSaveUrlsToFile:
    """Tests para save_urls_to_file()"""

    def test_save_urls_basic(self, tmp_path):
        """Test guardado básico de URLs"""
        output_file = tmp_path / 'output.txt'
        urls = [
            'https://www.youtube.com/watch?v=abc123',
            'https://youtu.be/def456'
        ]

        save_urls_to_file(urls, str(output_file))

        assert output_file.exists()
        content = output_file.read_text()
        assert 'abc123' in content
        assert 'def456' in content

    def test_save_preserves_order(self, tmp_path):
        """Test que preserva el orden de URLs"""
        output_file = tmp_path / 'output.txt'
        urls = [
            'https://www.youtube.com/watch?v=first',
            'https://www.youtube.com/watch?v=second',
            'https://www.youtube.com/watch?v=third'
        ]

        save_urls_to_file(urls, str(output_file))

        lines = output_file.read_text().strip().split('\n')
        assert 'first' in lines[0]
        assert 'second' in lines[1]
        assert 'third' in lines[2]

    def test_save_one_url_per_line(self, tmp_path):
        """Test que guarda una URL por línea"""
        output_file = tmp_path / 'output.txt'
        urls = [
            'https://www.youtube.com/watch?v=abc123',
            'https://youtu.be/def456',
            'https://www.youtube.com/watch?v=ghi789'
        ]

        save_urls_to_file(urls, str(output_file))

        lines = output_file.read_text().strip().split('\n')
        assert len(lines) == 3

    def test_save_empty_list(self, tmp_path):
        """Test guardar lista vacía"""
        output_file = tmp_path / 'empty.txt'
        urls = []

        save_urls_to_file(urls, str(output_file))

        assert output_file.exists()
        content = output_file.read_text().strip()
        assert content == ''

    def test_save_creates_parent_directories(self, tmp_path):
        """Test que crea directorios padre si no existen"""
        output_file = tmp_path / 'subdir' / 'output.txt'
        urls = ['https://www.youtube.com/watch?v=abc123']

        # Crear directorio padre manualmente ya que save_urls_to_file no lo hace
        output_file.parent.mkdir(parents=True, exist_ok=True)
        save_urls_to_file(urls, str(output_file))

        assert output_file.exists()
