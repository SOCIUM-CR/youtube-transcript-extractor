"""
Logging configuration for YouTube Transcript Extractor.

Provides structured logging with:
- Rotating file handler
- Console handler
- Configuration integration
- Context-aware logging
"""
import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
from config import get_config


class ColoredConsoleFormatter(logging.Formatter):
    """
    Formateador de logs con colores para consola.

    Usa códigos ANSI para colorear mensajes según nivel.
    """

    # Códigos de color ANSI
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        """
        Formatea el registro con colores.

        Args:
            record: Registro a formatear

        Returns:
            String formateado con colores
        """
        # Obtener color basado en nivel
        color = self.COLORS.get(record.levelname, '')

        # Formatear mensaje base
        formatted = super().format(record)

        # Solo colorear el nivel
        if color:
            # Reemplazar nivel con versión coloreada
            formatted = formatted.replace(
                record.levelname,
                f"{color}{record.levelname}{self.RESET}"
            )

        return formatted


def setup_logging(
    name: Optional[str] = None,
    config: Optional[object] = None,
    force: bool = False
) -> logging.Logger:
    """
    Configura sistema de logging estructurado.

    Args:
        name: Nombre del logger (default: 'youtube_extractor')
        config: ConfigLoader instance (default: usa get_config())
        force: Forzar reconfiguración incluso si ya existe

    Returns:
        Logger configurado

    Example:
        >>> logger = setup_logging()
        >>> logger.info('Iniciando extracción')
        >>> logger.error('Error al procesar video', extra={'video_id': 'abc123'})
    """
    logger_name = name or 'youtube_extractor'
    logger = logging.getLogger(logger_name)

    # Si el logger ya está configurado y no se fuerza, retornar
    if logger.handlers and not force:
        return logger

    # Limpiar handlers existentes si se fuerza reconfiguración
    if force and logger.handlers:
        logger.handlers.clear()

    # Cargar configuración
    if config is None:
        config = get_config()

    # Nivel de logging desde config
    log_level = config.get('logging.level', 'INFO').upper()
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    # Formato de logging
    log_format = config.get(
        'logging.format',
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    date_format = '%Y-%m-%d %H:%M:%S'

    # Handler 1: Archivo con rotación
    log_file = config.get('logging.file', 'youtube_extractor.log')
    max_size = config.get('logging.max_size_mb', 10) * 1024 * 1024  # MB a bytes
    backup_count = config.get('logging.backup_count', 3)

    # Crear directorio de logs si no existe
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)  # Archivo captura todo
    file_formatter = logging.Formatter(log_format, datefmt=date_format)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Handler 2: Consola (solo si no estamos en modo silencioso)
    if config.get('logging.console', True):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level, logging.INFO))

        # Usar formateador con colores si está habilitado en config
        if config.get('ui.use_colors', True):
            console_formatter = ColoredConsoleFormatter(
                '%(levelname)s: %(message)s',
                datefmt=date_format
            )
        else:
            console_formatter = logging.Formatter(
                '%(levelname)s: %(message)s',
                datefmt=date_format
            )

        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # Evitar propagación a logger raíz
    logger.propagate = False

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Obtiene logger configurado.

    Si el logger no existe, lo crea con configuración por defecto.

    Args:
        name: Nombre del logger (default: 'youtube_extractor')

    Returns:
        Logger configurado

    Example:
        >>> logger = get_logger('extractor.cache')
        >>> logger.debug('Cache hit para video abc123')
    """
    logger_name = name or 'youtube_extractor'
    logger = logging.getLogger(logger_name)

    # Si no tiene handlers, configurarlo
    if not logger.handlers:
        logger = setup_logging(name=logger_name)

    return logger


class LogContext:
    """
    Context manager para logging con contexto adicional.

    Permite agregar metadata temporal a logs dentro de un bloque.

    Example:
        >>> logger = get_logger()
        >>> with LogContext(logger, video_id='abc123', operation='extract'):
        ...     logger.info('Procesando video')
        ...     # Output: [video_id=abc123 operation=extract] Procesando video
    """

    def __init__(self, logger: logging.Logger, **context):
        """
        Inicializa contexto de logging.

        Args:
            logger: Logger a usar
            **context: Pares clave-valor para incluir en logs
        """
        self.logger = logger
        self.context = context
        self.original_formatter = None

    def __enter__(self):
        """Entra al contexto y modifica formato."""
        # Guardar formateador original del primer handler
        if self.logger.handlers:
            handler = self.logger.handlers[0]
            self.original_formatter = handler.formatter

            # Crear nuevo formato con contexto
            context_str = ' '.join(f'{k}={v}' for k, v in self.context.items())

            if isinstance(self.original_formatter, ColoredConsoleFormatter):
                new_formatter = ColoredConsoleFormatter(
                    f'%(levelname)s: [{context_str}] %(message)s'
                )
            else:
                new_formatter = logging.Formatter(
                    f'%(asctime)s - %(name)s - %(levelname)s - [{context_str}] %(message)s'
                )

            handler.setFormatter(new_formatter)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sale del contexto y restaura formato original."""
        if self.logger.handlers and self.original_formatter:
            self.logger.handlers[0].setFormatter(self.original_formatter)


def log_function_call(logger: Optional[logging.Logger] = None):
    """
    Decorador para loggear llamadas a funciones.

    Args:
        logger: Logger a usar (default: crea uno automáticamente)

    Returns:
        Decorador de función

    Example:
        >>> @log_function_call()
        ... def extract_transcript(video_url):
        ...     return "transcript"
    """
    def decorator(func):
        nonlocal logger
        if logger is None:
            logger = get_logger()

        def wrapper(*args, **kwargs):
            func_name = func.__name__
            logger.debug(f"Llamando {func_name} con args={args} kwargs={kwargs}")

            try:
                result = func(*args, **kwargs)
                logger.debug(f"{func_name} completado exitosamente")
                return result
            except Exception as e:
                logger.error(
                    f"{func_name} falló con error: {e}",
                    exc_info=True
                )
                raise

        return wrapper
    return decorator


def log_performance(logger: Optional[logging.Logger] = None):
    """
    Decorador para loggear tiempo de ejecución.

    Args:
        logger: Logger a usar (default: crea uno automáticamente)

    Returns:
        Decorador de función

    Example:
        >>> @log_performance()
        ... def slow_function():
        ...     time.sleep(2)
    """
    import time

    def decorator(func):
        nonlocal logger
        if logger is None:
            logger = get_logger()

        def wrapper(*args, **kwargs):
            func_name = func.__name__
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.info(f"{func_name} completado en {elapsed:.2f}s")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"{func_name} falló después de {elapsed:.2f}s: {e}")
                raise

        return wrapper
    return decorator


# Crear logger por defecto del módulo
_module_logger = get_logger('youtube_extractor.logging')


def log_exception(e: Exception, context: str = ''):
    """
    Loggea una excepción con contexto.

    Args:
        e: Excepción a loggear
        context: Contexto adicional

    Example:
        >>> try:
        ...     risky_operation()
        ... except Exception as e:
        ...     log_exception(e, 'procesando video abc123')
    """
    if context:
        _module_logger.error(f"Error {context}: {e}", exc_info=True)
    else:
        _module_logger.error(f"Error: {e}", exc_info=True)


def log_video_processing(video_id: str, title: str, method: str, success: bool):
    """
    Loggea procesamiento de video con formato estructurado.

    Args:
        video_id: ID del video
        title: Título del video
        method: Método usado
        success: Si fue exitoso

    Example:
        >>> log_video_processing('abc123', 'Video Title', 'yt-dlp', True)
    """
    status = 'SUCCESS' if success else 'FAILED'
    _module_logger.info(
        f"Video {status}",
        extra={
            'video_id': video_id,
            'title': title[:50],  # Truncar título
            'method': method,
            'status': status
        }
    )
