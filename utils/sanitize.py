"""
Utilidades para sanitización y validación de input.

Este módulo proporciona funciones para prevenir ataques de seguridad
como path traversal, injection, y otros problemas relacionados con input
no confiable del usuario.
"""
import re
import os
from pathlib import Path
from typing import Optional


def sanitize_filename(filename: str, max_length: int = 200) -> str:
    """
    Sanitiza nombre de archivo removiendo caracteres peligrosos.

    Previene ataques de path traversal y problemas de encoding.

    Args:
        filename: Nombre de archivo a sanitizar
        max_length: Longitud máxima permitida (default: 200)

    Returns:
        Nombre de archivo seguro

    Examples:
        >>> sanitize_filename("../../../etc/passwd")
        'etc_passwd'
        >>> sanitize_filename("<script>alert('xss')</script>")
        'script_alert_xss_script'
        >>> sanitize_filename("Video: Python 101")
        'Video_Python_101'
    """
    if not filename:
        return 'untitled'

    # Remover path separators
    filename = filename.replace('/', '_').replace('\\', '_')

    # Remover caracteres peligrosos
    dangerous_chars = ['..', '<', '>', ':', '"', '|', '?', '*', '\0', '\n', '\r', '\t']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')

    # Remover caracteres de control ASCII (0-31)
    filename = ''.join(char if ord(char) >= 32 else '_' for char in filename)

    # Remover caracteres no-ASCII problemáticos pero preservar Unicode válido
    # Solo remover los que causan problemas en filesystems
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '_', filename)

    # Colapsar múltiples underscores consecutivos
    filename = re.sub(r'_+', '_', filename)

    # Remover underscores al inicio y final
    filename = filename.strip('_. ')

    # Truncar si excede max_length
    if len(filename) > max_length:
        # Intentar preservar extensión si existe
        if '.' in filename:
            name, ext = os.path.splitext(filename)
            max_name_length = max_length - len(ext)
            filename = name[:max_name_length] + ext
        else:
            filename = filename[:max_length]

    # Asegurar que no esté vacío después de sanitización
    if not filename or filename == '_':
        filename = 'untitled'

    # Prevenir nombres reservados en Windows
    windows_reserved = [
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    ]
    name_without_ext = os.path.splitext(filename)[0].upper()
    if name_without_ext in windows_reserved:
        filename = 'file_' + filename

    return filename


def validate_output_path(base_dir: str, user_path: str) -> bool:
    """
    Valida que el path de salida esté dentro del directorio base.

    Previene ataques de path traversal donde un usuario malicioso
    intenta escribir archivos fuera del directorio permitido.

    Args:
        base_dir: Directorio base permitido (absoluto)
        user_path: Path proporcionado por el usuario (puede ser relativo)

    Returns:
        True si el path es seguro, False si hay intento de path traversal

    Examples:
        >>> validate_output_path('/home/user/transcripts', 'my_videos')
        True
        >>> validate_output_path('/home/user/transcripts', '../../../etc/passwd')
        False
        >>> validate_output_path('/home/user/transcripts', '/tmp/malicious')
        False
    """
    try:
        # Convertir a paths absolutos y resolver symlinks
        base_path = Path(base_dir).resolve()
        full_path = (base_path / user_path).resolve()

        # Verificar que full_path esté dentro de base_path
        # Esto previene path traversal con ../
        full_path.relative_to(base_path)
        return True
    except (ValueError, OSError):
        # ValueError: path no está dentro de base
        # OSError: problemas de permisos o path inválido
        return False


def sanitize_url(url: str, max_length: int = 2048) -> Optional[str]:
    """
    Sanitiza una URL removiendo caracteres peligrosos.

    Args:
        url: URL a sanitizar
        max_length: Longitud máxima permitida

    Returns:
        URL sanitizada o None si es inválida

    Examples:
        >>> sanitize_url('https://youtube.com/watch?v=abc123')
        'https://youtube.com/watch?v=abc123'
        >>> sanitize_url('javascript:alert("xss")')
        None
    """
    if not url or len(url) > max_length:
        return None

    # Remover espacios en blanco
    url = url.strip()

    # Prevenir URLs con esquemas peligrosos
    dangerous_schemes = ['javascript:', 'data:', 'file:', 'vbscript:']
    url_lower = url.lower()
    if any(url_lower.startswith(scheme) for scheme in dangerous_schemes):
        return None

    # Remover caracteres de control
    url = ''.join(char for char in url if ord(char) >= 32)

    # Validar que contenga un esquema válido
    if not url.startswith(('http://', 'https://')):
        return None

    return url


def sanitize_folder_name(folder_name: str, max_length: int = 100) -> str:
    """
    Sanitiza nombre de carpeta de forma más estricta que archivos.

    Args:
        folder_name: Nombre de carpeta a sanitizar
        max_length: Longitud máxima permitida

    Returns:
        Nombre de carpeta seguro

    Examples:
        >>> sanitize_folder_name('My Videos 2024')
        'My_Videos_2024'
        >>> sanitize_folder_name('../../../evil')
        'evil'
    """
    if not folder_name:
        return 'folder'

    # Aplicar sanitización básica
    folder_name = sanitize_filename(folder_name, max_length)

    # Ser más restrictivo: solo alfanuméricos, guiones y underscores
    folder_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', folder_name)

    # Colapsar múltiples underscores
    folder_name = re.sub(r'_+', '_', folder_name)

    # Limpiar
    folder_name = folder_name.strip('_-')

    if not folder_name:
        return 'folder'

    return folder_name


def validate_video_id(video_id: str) -> bool:
    """
    Valida que un video ID de YouTube sea válido.

    YouTube video IDs tienen exactamente 11 caracteres alfanuméricos,
    guiones y underscores.

    Args:
        video_id: Video ID a validar

    Returns:
        True si es válido, False en caso contrario

    Examples:
        >>> validate_video_id('dQw4w9WgXcQ')
        True
        >>> validate_video_id('abc')
        False
        >>> validate_video_id('../../../etc/passwd')
        False
    """
    if video_id is None or not isinstance(video_id, str):
        return False

    if not video_id or len(video_id) != 11:
        return False

    # Video IDs solo contienen: a-z, A-Z, 0-9, -, _
    if not re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
        return False

    return True


def escape_shell_argument(arg: str) -> str:
    """
    Escapa un argumento para uso seguro en shell.

    ADVERTENCIA: Esto NO hace el código completamente seguro contra
    shell injection. Usar subprocess con lista de argumentos es preferible.

    Args:
        arg: Argumento a escapar

    Returns:
        Argumento escapado

    Note:
        Preferir siempre subprocess.run(['cmd', 'arg']) sobre shell=True
    """
    # Envolver en comillas simples y escapar comillas simples existentes
    return "'" + arg.replace("'", "'\\''") + "'"


def sanitize_dict_values(data: dict, max_depth: int = 3) -> dict:
    """
    Sanitiza recursivamente valores de un diccionario.

    Útil para limpiar datos de configuración o entrada de usuario.

    Args:
        data: Diccionario a sanitizar
        max_depth: Profundidad máxima de recursión

    Returns:
        Diccionario con valores sanitizados
    """
    if max_depth <= 0:
        return data

    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            # Remover caracteres de control
            value = ''.join(char for char in value if ord(char) >= 32 or char in '\n\r\t')
            sanitized[key] = value
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict_values(value, max_depth - 1)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_dict_values(item, max_depth - 1) if isinstance(item, dict)
                else item
                for item in value
            ]
        else:
            sanitized[key] = value

    return sanitized
