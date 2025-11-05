"""
Tests unitarios para youtube_extractor_list.py
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from youtube_extractor_list import extract_playlist_urls


class TestExtractPlaylistUrls:
    """Tests para extract_playlist_urls()"""

    @pytest.mark.integration
    @pytest.mark.network
    def test_extract_from_valid_playlist(self, tmp_path):
        """Test extracción desde playlist válida (requiere red)

        NOTA: Este test es slow y requiere conexión. Usar con precaución.
        """
        pytest.skip("Test de integración que requiere playlist real - skip por defecto")

        output_file = tmp_path / 'playlist_urls.txt'
        playlist_url = 'https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf'

        extract_playlist_urls(playlist_url, str(output_file))

        assert output_file.exists()
        content = output_file.read_text()
        assert 'youtube.com/watch?v=' in content

    def test_extract_with_mock_pytube(self, tmp_path):
        """Test extracción con mock de pytube"""
        output_file = tmp_path / 'playlist_urls.txt'
        playlist_url = 'https://www.youtube.com/playlist?list=PLtest123'

        # Mock de Playlist
        mock_playlist = Mock()
        mock_playlist.video_urls = [
            'https://www.youtube.com/watch?v=video1',
            'https://www.youtube.com/watch?v=video2',
            'https://www.youtube.com/watch?v=video3'
        ]

        with patch('youtube_extractor_list.Playlist', return_value=mock_playlist):
            extract_playlist_urls(playlist_url, str(output_file))

            assert output_file.exists()
            content = output_file.read_text()
            lines = content.strip().split('\n')
            assert len(lines) == 3
            assert 'video1' in content

    def test_extract_invalid_url_raises_error(self, tmp_path):
        """Test URL inválida lanza error"""
        output_file = tmp_path / 'output.txt'
        invalid_url = 'https://www.youtube.com/watch?v=not_a_playlist'

        with pytest.raises(SystemExit):
            with patch('youtube_extractor_list.Playlist') as mock_playlist:
                mock_playlist.side_effect = ValueError("No playlist ID found")
                extract_playlist_urls(invalid_url, str(output_file))

    def test_extract_empty_playlist(self, tmp_path):
        """Test playlist vacía lanza error"""
        output_file = tmp_path / 'output.txt'
        playlist_url = 'https://www.youtube.com/playlist?list=PLempty'

        with pytest.raises(SystemExit):
            with patch('youtube_extractor_list.Playlist') as mock_playlist_class:
                mock_playlist = Mock()
                mock_playlist.video_urls = []
                mock_playlist_class.return_value = mock_playlist
                extract_playlist_urls(playlist_url, str(output_file))

    def test_output_file_format(self, tmp_path):
        """Test formato del archivo de salida"""
        output_file = tmp_path / 'test_output.txt'
        playlist_url = 'https://www.youtube.com/playlist?list=PLtest'

        mock_playlist = Mock()
        mock_playlist.video_urls = [
            'https://www.youtube.com/watch?v=abc123',
            'https://www.youtube.com/watch?v=def456'
        ]

        with patch('youtube_extractor_list.Playlist', return_value=mock_playlist):
            extract_playlist_urls(playlist_url, str(output_file))

            lines = output_file.read_text().strip().split('\n')
            # Cada línea debe ser una URL válida
            for line in lines:
                assert line.startswith('https://www.youtube.com/watch?v=')

    def test_url_decoding(self, tmp_path):
        """Test decodificación de URLs con caracteres especiales"""
        output_file = tmp_path / 'output.txt'
        # URL con caracteres encoded
        playlist_url = 'https://www.youtube.com/playlist?list=PLtest%20spaces'

        mock_playlist = Mock()
        mock_playlist.video_urls = ['https://www.youtube.com/watch?v=test']

        with patch('youtube_extractor_list.Playlist', return_value=mock_playlist) as mock:
            with patch('youtube_extractor_list.urllib.parse.unquote') as mock_unquote:
                mock_unquote.return_value = 'https://www.youtube.com/playlist?list=PLtest spaces'

                extract_playlist_urls(playlist_url, str(output_file))

                # Verificar que unquote fue llamado
                mock_unquote.assert_called_once_with(playlist_url)
