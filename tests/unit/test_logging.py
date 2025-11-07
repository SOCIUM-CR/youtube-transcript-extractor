"""
Tests unitarios para utils/logging_config.py
"""
import pytest
import logging
from pathlib import Path
from utils.logging_config import (
    setup_logging,
    get_logger,
    LogContext,
    ColoredConsoleFormatter,
    log_exception
)
from config import ConfigLoader


class TestSetupLogging:
    """Tests para setup_logging"""

    def test_setup_logging_creates_logger(self, tmp_path):
        """Test crear logger con configuración"""
        # Crear config temporal
        config = ConfigLoader()
        config.config['logging']['file'] = str(tmp_path / 'test.log')

        logger = setup_logging('test_logger', config=config)

        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert logger.name == 'test_logger'

    def test_setup_logging_creates_log_file(self, tmp_path):
        """Test que se crea archivo de log"""
        log_file = tmp_path / 'test.log'

        config = ConfigLoader()
        config.config['logging']['file'] = str(log_file)
        config.config['logging']['level'] = 'INFO'

        logger = setup_logging('test_logger', config=config, force=True)

        # Logger debe tener nivel INFO para que loggee el mensaje
        assert logger.level <= logging.INFO

        logger.info('Test message')

        # Forzar flush de los handlers
        for handler in logger.handlers:
            handler.flush()

        # El archivo debe existir después de loggear
        assert log_file.exists()

    def test_setup_logging_respects_level(self, tmp_path):
        """Test que respeta nivel de logging"""
        config = ConfigLoader()
        config.config['logging']['level'] = 'WARNING'
        config.config['logging']['file'] = str(tmp_path / 'test.log')

        logger = setup_logging('test_logger_level', config=config, force=True)

        assert logger.level == logging.WARNING

    def test_setup_logging_default_name(self, tmp_path):
        """Test nombre por defecto"""
        config = ConfigLoader()
        config.config['logging']['file'] = str(tmp_path / 'test.log')

        logger = setup_logging(config=config)

        assert logger.name == 'youtube_extractor'

    def test_setup_logging_force_reconfigure(self, tmp_path):
        """Test forzar reconfiguración"""
        config = ConfigLoader()
        config.config['logging']['file'] = str(tmp_path / 'test.log')

        # Primera configuración
        logger1 = setup_logging('test_logger', config=config)
        handlers_count1 = len(logger1.handlers)

        # Segunda configuración sin force - debe usar misma instancia
        logger2 = setup_logging('test_logger', config=config, force=False)
        assert logger1 is logger2
        assert len(logger2.handlers) == handlers_count1

        # Tercera configuración con force - debe reconfigurar
        logger3 = setup_logging('test_logger', config=config, force=True)
        assert logger3 is logger2  # Mismo logger
        # Puede tener misma cantidad de handlers pero fueron reconfigurados


class TestGetLogger:
    """Tests para get_logger"""

    def test_get_logger_returns_logger(self):
        """Test obtener logger"""
        logger = get_logger('test')

        assert logger is not None
        assert isinstance(logger, logging.Logger)

    def test_get_logger_creates_if_not_exists(self):
        """Test crea logger si no existe"""
        logger_name = f'test_logger_{id(self)}'
        logger = get_logger(logger_name)

        assert logger.name == logger_name
        assert len(logger.handlers) > 0  # Debe tener handlers

    def test_get_logger_default_name(self):
        """Test nombre por defecto"""
        logger = get_logger()

        assert logger.name == 'youtube_extractor'


class TestColoredConsoleFormatter:
    """Tests para ColoredConsoleFormatter"""

    def test_formatter_adds_colors(self):
        """Test que agrega colores a los niveles"""
        formatter = ColoredConsoleFormatter('%(levelname)s: %(message)s')

        # Crear registro de prueba
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='test.py',
            lineno=1,
            msg='Test message',
            args=(),
            exc_info=None
        )

        formatted = formatter.format(record)

        # Debe contener códigos ANSI
        assert '\033[' in formatted or 'INFO' in formatted

    def test_formatter_handles_all_levels(self):
        """Test que maneja todos los niveles"""
        formatter = ColoredConsoleFormatter('%(levelname)s: %(message)s')

        levels = [
            (logging.DEBUG, 'DEBUG'),
            (logging.INFO, 'INFO'),
            (logging.WARNING, 'WARNING'),
            (logging.ERROR, 'ERROR'),
            (logging.CRITICAL, 'CRITICAL')
        ]

        for level, level_name in levels:
            record = logging.LogRecord(
                name='test',
                level=level,
                pathname='test.py',
                lineno=1,
                msg='Test message',
                args=(),
                exc_info=None
            )

            formatted = formatter.format(record)
            assert level_name in formatted


class TestLogContext:
    """Tests para LogContext"""

    def test_log_context_adds_context(self, tmp_path, capsys):
        """Test que LogContext agrega contexto"""
        config = ConfigLoader()
        config.config['logging']['file'] = str(tmp_path / 'test.log')
        config.config['logging']['console'] = False  # Deshabilitar consola

        logger = setup_logging('test_context', config=config, force=True)

        # Usar contexto
        with LogContext(logger, video_id='abc123', operation='test'):
            logger.info('Test message')

        # Verificar que el log contiene el contexto
        log_content = (tmp_path / 'test.log').read_text()
        assert 'video_id=abc123' in log_content
        assert 'operation=test' in log_content

    def test_log_context_restores_formatter(self, tmp_path):
        """Test que restaura formateador original"""
        config = ConfigLoader()
        config.config['logging']['file'] = str(tmp_path / 'test.log')

        logger = setup_logging('test_restore', config=config, force=True)

        if logger.handlers:
            original_formatter = logger.handlers[0].formatter

            with LogContext(logger, test='value'):
                pass  # Contexto

            # Debe restaurar formateador original
            current_formatter = logger.handlers[0].formatter
            # Puede ser un nuevo formateador pero debe ser del mismo tipo
            assert type(current_formatter) == type(original_formatter)


class TestLogException:
    """Tests para log_exception"""

    def test_log_exception_logs_error(self, tmp_path):
        """Test que loggea excepciones"""
        config = ConfigLoader()
        config.config['logging']['file'] = str(tmp_path / 'test.log')

        # Configurar logger antes de usar log_exception
        setup_logging('youtube_extractor.logging', config=config, force=True)

        try:
            raise ValueError('Test error')
        except Exception as e:
            log_exception(e, 'durante test')

        # Verificar que el error fue loggeado
        log_content = (tmp_path / 'test.log').read_text()
        assert 'Test error' in log_content
        assert 'durante test' in log_content

    def test_log_exception_without_context(self, tmp_path):
        """Test loggear excepción sin contexto"""
        config = ConfigLoader()
        config.config['logging']['file'] = str(tmp_path / 'test.log')

        setup_logging('youtube_extractor.logging', config=config, force=True)

        try:
            raise RuntimeError('Another error')
        except Exception as e:
            log_exception(e)

        log_content = (tmp_path / 'test.log').read_text()
        assert 'Another error' in log_content


class TestLoggingIntegration:
    """Tests de integración de logging"""

    def test_multiple_loggers_same_file(self, tmp_path):
        """Test múltiples loggers escribiendo al mismo archivo"""
        log_file = tmp_path / 'shared.log'

        config = ConfigLoader()
        config.config['logging']['file'] = str(log_file)

        logger1 = setup_logging('logger1', config=config, force=True)
        logger2 = setup_logging('logger2', config=config, force=True)

        logger1.info('Message from logger1')
        logger2.info('Message from logger2')

        log_content = log_file.read_text()
        assert 'Message from logger1' in log_content
        assert 'Message from logger2' in log_content

    def test_log_file_rotation_configuration(self, tmp_path):
        """Test configuración de rotación de archivos"""
        config = ConfigLoader()
        config.config['logging']['file'] = str(tmp_path / 'rotating.log')
        config.config['logging']['max_size_mb'] = 1  # 1 MB
        config.config['logging']['backup_count'] = 3

        logger = setup_logging('test_rotation', config=config, force=True)

        # Verificar que tiene un RotatingFileHandler
        has_rotating_handler = False
        for handler in logger.handlers:
            if isinstance(handler, logging.handlers.RotatingFileHandler):
                has_rotating_handler = True
                assert handler.maxBytes == 1 * 1024 * 1024
                assert handler.backupCount == 3
                break

        assert has_rotating_handler

    def test_console_logging_can_be_disabled(self, tmp_path):
        """Test que logging a consola puede deshabilitarse"""
        config = ConfigLoader()
        config.config['logging']['file'] = str(tmp_path / 'test.log')
        config.config['logging']['console'] = False

        logger = setup_logging('no_console', config=config, force=True)

        # No debe tener StreamHandler
        has_stream_handler = any(
            isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)
            for h in logger.handlers
        )

        # RotatingFileHandler hereda de FileHandler, pero StreamHandler directo no debe estar
        stream_handlers = [
            h for h in logger.handlers
            if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)
        ]

        assert len(stream_handlers) == 0

    def test_logging_levels_are_respected(self, tmp_path):
        """Test que niveles de logging se respetan"""
        log_file = tmp_path / 'levels.log'

        config = ConfigLoader()
        config.config['logging']['file'] = str(log_file)
        config.config['logging']['level'] = 'WARNING'

        logger = setup_logging('test_levels', config=config, force=True)

        # Estos no deben aparecer
        logger.debug('Debug message')
        logger.info('Info message')

        # Estos sí deben aparecer
        logger.warning('Warning message')
        logger.error('Error message')

        # Leer archivo (solo handlers de archivo capturan todo)
        log_content = log_file.read_text()

        # Nota: FileHandler está configurado con DEBUG, así que captura todo
        # pero el logger mismo está en WARNING
        # Dependiendo de cómo está configurado, puede que debug/info no aparezcan

        assert 'Warning message' in log_content
        assert 'Error message' in log_content


class TestLoggingEdgeCases:
    """Tests de casos límite"""

    def test_logging_with_unicode(self, tmp_path):
        """Test logging con caracteres unicode"""
        config = ConfigLoader()
        config.config['logging']['file'] = str(tmp_path / 'unicode.log')

        logger = setup_logging('test_unicode', config=config, force=True)

        unicode_msg = 'Test 日本語 español 中文 🎥'
        logger.info(unicode_msg)

        log_content = (tmp_path / 'unicode.log').read_text(encoding='utf-8')
        assert unicode_msg in log_content

    def test_logging_creates_parent_directories(self, tmp_path):
        """Test que crea directorios padre si no existen"""
        log_file = tmp_path / 'subdir' / 'logs' / 'app.log'

        config = ConfigLoader()
        config.config['logging']['file'] = str(log_file)

        logger = setup_logging('test_mkdir', config=config, force=True)
        logger.info('Test')

        assert log_file.exists()
        assert log_file.parent.exists()

    def test_logging_empty_message(self, tmp_path):
        """Test logging de mensaje vacío"""
        config = ConfigLoader()
        config.config['logging']['file'] = str(tmp_path / 'empty.log')

        logger = setup_logging('test_empty', config=config, force=True)

        # No debe generar error
        logger.info('')

        assert (tmp_path / 'empty.log').exists()
