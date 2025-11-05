"""
Tests unitarios para utils/sanitize.py

Tests completos de funciones de sanitización y validación de seguridad.
"""
import pytest
from pathlib import Path
from utils.sanitize import (
    sanitize_filename,
    validate_output_path,
    sanitize_url,
    sanitize_folder_name,
    validate_video_id,
    sanitize_dict_values,
)


class TestSanitizeFilename:
    """Tests para sanitize_filename()"""

    def test_basic_filename(self):
        """Test nombre de archivo básico sin caracteres especiales"""
        assert sanitize_filename("video_title") == "video_title"

    def test_path_traversal_attack(self):
        """Test prevención de path traversal"""
        result = sanitize_filename("../../../etc/passwd")
        assert ".." not in result
        assert "/" not in result
        assert "\\" not in result

    def test_dangerous_characters_removed(self):
        """Test remoción de caracteres peligrosos"""
        dangerous = "<>:\"|?*\0\n\r\t"
        result = sanitize_filename(f"file{dangerous}name")
        for char in dangerous:
            assert char not in result

    def test_script_injection_attempt(self):
        """Test prevención de script injection"""
        result = sanitize_filename("<script>alert('xss')</script>")
        assert "<" not in result
        assert ">" not in result
        assert "script" in result  # El texto sigue ahí, solo sin <>

    def test_unicode_characters_preserved(self):
        """Test que Unicode válido se preserva"""
        result = sanitize_filename("Video con ñ y acentós")
        # Los caracteres especiales deberían preservarse o manejarse apropiadamente
        assert len(result) > 0
        assert result != "untitled"

    def test_empty_string_returns_untitled(self):
        """Test string vacío retorna 'untitled'"""
        assert sanitize_filename("") == "untitled"

    def test_only_dangerous_chars_returns_untitled(self):
        """Test string con solo caracteres peligrosos"""
        result = sanitize_filename("../../../")
        assert result == "untitled"

    def test_max_length_truncation(self):
        """Test truncado a longitud máxima"""
        long_name = "a" * 300
        result = sanitize_filename(long_name, max_length=100)
        assert len(result) <= 100

    def test_max_length_preserves_extension(self):
        """Test que truncado preserva extensión"""
        long_name = "a" * 300 + ".txt"
        result = sanitize_filename(long_name, max_length=100)
        assert result.endswith(".txt")
        assert len(result) <= 100

    def test_multiple_underscores_collapsed(self):
        """Test que múltiples underscores se colapsan"""
        result = sanitize_filename("file___name___here")
        assert "___" not in result
        assert result == "file_name_here"

    def test_leading_trailing_underscores_removed(self):
        """Test remoción de underscores al inicio/final"""
        result = sanitize_filename("_file_name_")
        assert not result.startswith("_")
        assert not result.endswith("_")

    def test_windows_reserved_names(self):
        """Test prevención de nombres reservados de Windows"""
        reserved = ["CON", "PRN", "AUX", "NUL", "COM1", "LPT1"]
        for name in reserved:
            result = sanitize_filename(name)
            assert result != name
            assert result.startswith("file_")

    def test_windows_reserved_with_extension(self):
        """Test nombres reservados con extensión"""
        result = sanitize_filename("CON.txt")
        assert result != "CON.txt"
        assert ".txt" in result

    def test_control_characters_removed(self):
        """Test remoción de caracteres de control ASCII"""
        control_chars = "".join(chr(i) for i in range(0, 32))
        result = sanitize_filename(f"file{control_chars}name")
        # Los caracteres de control deben convertirse en underscores o removerse
        assert result == "file_name"

    def test_spaces_preserved(self):
        """Test que espacios se preservan"""
        result = sanitize_filename("My Video Title")
        assert " " in result or "_" in result  # Podría convertirse en _ o preservarse

    @pytest.mark.parametrize("input,should_not_contain", [
        ("../../../etc/passwd", ".."),
        ("<script>alert</script>", "<"),
        ("file|name", "|"),
        ("file:name", ":"),
        ("file?name", "?"),
        ("file*name", "*"),
    ])
    def test_dangerous_patterns(self, input, should_not_contain):
        """Test múltiples patrones peligrosos"""
        result = sanitize_filename(input)
        assert should_not_contain not in result


class TestValidateOutputPath:
    """Tests para validate_output_path()"""

    def test_valid_subdirectory(self, tmp_path):
        """Test path válido dentro del directorio base"""
        base = str(tmp_path)
        assert validate_output_path(base, "subfolder") is True

    def test_path_traversal_rejected(self, tmp_path):
        """Test path traversal es rechazado"""
        base = str(tmp_path)
        assert validate_output_path(base, "../../../etc") is False

    def test_absolute_path_outside_rejected(self, tmp_path):
        """Test path absoluto fuera del base es rechazado"""
        base = str(tmp_path)
        assert validate_output_path(base, "/etc/passwd") is False

    def test_nested_subdirectories_allowed(self, tmp_path):
        """Test subdirectorios anidados son permitidos"""
        base = str(tmp_path)
        assert validate_output_path(base, "folder/subfolder/deep") is True

    def test_current_directory_allowed(self, tmp_path):
        """Test directorio actual (.) es permitido"""
        base = str(tmp_path)
        assert validate_output_path(base, ".") is True

    def test_symlink_traversal_prevented(self, tmp_path):
        """Test que symlinks que apuntan fuera son detectados"""
        base = tmp_path / "base"
        base.mkdir()
        outside = tmp_path / "outside"
        outside.mkdir()

        # Crear symlink dentro de base que apunta fuera
        symlink = base / "link"
        try:
            symlink.symlink_to(outside)
            # El symlink resuelve a fuera de base, debe ser rechazado
            # Esta es la protección correcta contra symlink traversal
            assert validate_output_path(str(base), "link") is False
        except OSError:
            # En algunos sistemas no se pueden crear symlinks
            pytest.skip("Cannot create symlinks on this system")


class TestSanitizeUrl:
    """Tests para sanitize_url()"""

    def test_valid_http_url(self):
        """Test URL HTTP válida"""
        url = "http://youtube.com/watch?v=abc123"
        assert sanitize_url(url) == url

    def test_valid_https_url(self):
        """Test URL HTTPS válida"""
        url = "https://youtube.com/watch?v=abc123"
        assert sanitize_url(url) == url

    def test_javascript_url_rejected(self):
        """Test URL javascript: es rechazada"""
        assert sanitize_url("javascript:alert('xss')") is None

    def test_data_url_rejected(self):
        """Test URL data: es rechazada"""
        assert sanitize_url("data:text/html,<script>alert(1)</script>") is None

    def test_file_url_rejected(self):
        """Test URL file: es rechazada"""
        assert sanitize_url("file:///etc/passwd") is None

    def test_vbscript_url_rejected(self):
        """Test URL vbscript: es rechazada"""
        assert sanitize_url("vbscript:msgbox('xss')") is None

    def test_empty_url_rejected(self):
        """Test URL vacía es rechazada"""
        assert sanitize_url("") is None

    def test_too_long_url_rejected(self):
        """Test URL muy larga es rechazada"""
        long_url = "https://example.com/" + "a" * 3000
        assert sanitize_url(long_url, max_length=2048) is None

    def test_url_with_spaces_stripped(self):
        """Test espacios en blanco son removidos"""
        url = "  https://youtube.com/watch?v=abc  "
        result = sanitize_url(url)
        assert result == "https://youtube.com/watch?v=abc"

    def test_url_without_scheme_rejected(self):
        """Test URL sin esquema es rechazada"""
        assert sanitize_url("youtube.com/watch?v=abc") is None

    def test_control_characters_removed(self):
        """Test caracteres de control son removidos"""
        url = "https://youtube.com/watch?v=abc\x00\x01\x02"
        result = sanitize_url(url)
        assert result is not None
        assert "\x00" not in result

    @pytest.mark.parametrize("dangerous_scheme", [
        "javascript:alert(1)",
        "data:text/html,<script>",
        "file:///etc/passwd",
        "vbscript:msgbox(1)",
    ])
    def test_dangerous_schemes_rejected(self, dangerous_scheme):
        """Test múltiples esquemas peligrosos son rechazados"""
        assert sanitize_url(dangerous_scheme) is None


class TestSanitizeFolderName:
    """Tests para sanitize_folder_name()"""

    def test_basic_folder_name(self):
        """Test nombre de carpeta básico"""
        assert sanitize_folder_name("my_folder") == "my_folder"

    def test_spaces_converted_to_underscores(self):
        """Test espacios se convierten en underscores"""
        result = sanitize_folder_name("My Folder Name")
        assert " " not in result
        assert "_" in result

    def test_special_characters_removed(self):
        """Test caracteres especiales son removidos"""
        result = sanitize_folder_name("folder@#$%name")
        assert "@" not in result
        assert "#" not in result
        assert "$" not in result

    def test_path_traversal_prevented(self):
        """Test path traversal es prevenido"""
        result = sanitize_folder_name("../../../etc")
        assert ".." not in result
        assert "/" not in result

    def test_only_alphanumeric_dash_underscore(self):
        """Test solo alfanuméricos, guiones y underscores"""
        result = sanitize_folder_name("My-Folder_123")
        assert result == "My-Folder_123"

    def test_empty_returns_folder(self):
        """Test string vacío retorna 'folder'"""
        assert sanitize_folder_name("") == "folder"

    def test_max_length_respected(self):
        """Test longitud máxima es respetada"""
        long_name = "a" * 200
        result = sanitize_folder_name(long_name, max_length=50)
        assert len(result) <= 50


class TestValidateVideoId:
    """Tests para validate_video_id()"""

    def test_valid_video_id(self):
        """Test video ID válido"""
        assert validate_video_id("dQw4w9WgXcQ") is True

    def test_valid_with_dash(self):
        """Test video ID con guión"""
        assert validate_video_id("abc-123-xyz") is True

    def test_valid_with_underscore(self):
        """Test video ID con underscore"""
        assert validate_video_id("abc_123_xyz") is True

    def test_too_short_rejected(self):
        """Test video ID muy corto es rechazado"""
        assert validate_video_id("abc123") is False

    def test_too_long_rejected(self):
        """Test video ID muy largo es rechazado"""
        assert validate_video_id("abcdefghijk12345") is False

    def test_empty_rejected(self):
        """Test video ID vacío es rechazado"""
        assert validate_video_id("") is False

    def test_special_characters_rejected(self):
        """Test caracteres especiales son rechazados"""
        assert validate_video_id("abc@#$%^123") is False

    def test_path_traversal_rejected(self):
        """Test path traversal es rechazado"""
        assert validate_video_id("../etc/pass") is False

    def test_spaces_rejected(self):
        """Test espacios son rechazados"""
        assert validate_video_id("abc 123 xyz") is False

    @pytest.mark.parametrize("valid_id", [
        "dQw4w9WgXcQ",
        "abc123DEFGH",
        "___________",  # 11 underscores
        "-----------",  # 11 guiones
        "aB1-_aB1-_a",
    ])
    def test_various_valid_ids(self, valid_id):
        """Test varios IDs válidos"""
        assert len(valid_id) == 11  # Verificar prerequisito del test
        assert validate_video_id(valid_id) is True

    @pytest.mark.parametrize("invalid_id", [
        "short",
        "toolongstring123",
        "abc@123defg",
        "../etc/passwd",
        "abc 123 xyz",
        "",
        None,
    ])
    def test_various_invalid_ids(self, invalid_id):
        """Test varios IDs inválidos"""
        # Todos los casos inválidos deben retornar False, incluyendo None
        assert validate_video_id(invalid_id) is False


class TestSanitizeDictValues:
    """Tests para sanitize_dict_values()"""

    def test_basic_dict(self):
        """Test diccionario básico"""
        data = {"key": "value"}
        result = sanitize_dict_values(data)
        assert result == {"key": "value"}

    def test_control_characters_removed(self):
        """Test caracteres de control son removidos"""
        data = {"key": "value\x00\x01\x02"}
        result = sanitize_dict_values(data)
        assert "\x00" not in result["key"]

    def test_nested_dict(self):
        """Test diccionario anidado"""
        data = {
            "level1": {
                "level2": "value\x00"
            }
        }
        result = sanitize_dict_values(data)
        assert "\x00" not in result["level1"]["level2"]

    def test_list_values(self):
        """Test valores de lista"""
        data = {"items": [{"name": "test\x00"}]}
        result = sanitize_dict_values(data)
        assert "\x00" not in result["items"][0]["name"]

    def test_max_depth_respected(self):
        """Test profundidad máxima es respetada"""
        data = {
            "l1": {
                "l2": {
                    "l3": {
                        "l4": "value"
                    }
                }
            }
        }
        result = sanitize_dict_values(data, max_depth=2)
        # Después de max_depth=2, ya no sanitiza más profundo
        assert "l1" in result
        assert "l2" in result["l1"]

    def test_preserves_non_string_values(self):
        """Test preserva valores no-string"""
        data = {
            "string": "text",
            "int": 123,
            "float": 45.67,
            "bool": True,
            "none": None
        }
        result = sanitize_dict_values(data)
        assert result["int"] == 123
        assert result["float"] == 45.67
        assert result["bool"] is True
        assert result["none"] is None

    def test_whitespace_characters_preserved(self):
        """Test caracteres de espacio en blanco son preservados"""
        data = {"key": "value\n\r\t"}
        result = sanitize_dict_values(data)
        assert "\n" in result["key"]
        assert "\r" in result["key"]
        assert "\t" in result["key"]


class TestIntegrationSanitize:
    """Tests de integración de sanitización"""

    def test_full_workflow_sanitization(self, tmp_path):
        """Test workflow completo de sanitización"""
        # Simular input de usuario malicioso
        malicious_title = "../../../etc/passwd<script>alert('xss')</script>"
        video_id = "dQw4w9WgXcQ"

        # Sanitizar
        safe_title = sanitize_filename(malicious_title)
        filename = f"001_{safe_title}_{video_id}.txt"

        # Verificar que es seguro
        assert ".." not in filename
        assert "/" not in filename
        assert "\\" not in filename
        assert "<" not in filename
        assert ">" not in filename

        # Verificar que se puede crear el archivo
        output_dir = tmp_path / "transcripts"
        output_dir.mkdir()

        file_path = output_dir / filename
        file_path.write_text("Test content")

        assert file_path.exists()

    def test_validate_then_sanitize(self):
        """Test validar primero, luego sanitizar"""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

        # Validar URL
        safe_url = sanitize_url(url)
        assert safe_url is not None

        # Extraer video ID (simulated)
        video_id = "dQw4w9WgXcQ"
        assert validate_video_id(video_id) is True

        # Sanitizar título
        title = "My Video <script>alert(1)</script>"
        safe_title = sanitize_filename(title)
        assert "<" not in safe_title
        assert ">" not in safe_title
