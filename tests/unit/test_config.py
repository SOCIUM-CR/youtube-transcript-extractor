"""
Tests unitarios para config/config_loader.py
"""
import pytest
import yaml
from pathlib import Path
from config.config_loader import ConfigLoader, get_config, reload_config


class TestConfigLoader:
    """Tests para ConfigLoader"""

    def test_load_default_config(self, tmp_path):
        """Test carga configuración por defecto"""
        # Sin archivo config.yaml, debe usar defaults
        config = ConfigLoader(config_path=str(tmp_path / 'nonexistent.yaml'))

        assert config.config is not None
        assert 'app' in config.config
        assert 'languages' in config.config
        assert 'extraction' in config.config

    def test_get_simple_value(self):
        """Test obtener valor simple"""
        config = ConfigLoader()

        app_name = config.get('app.name')
        assert app_name is not None
        assert isinstance(app_name, str)

    def test_get_nested_value(self):
        """Test obtener valor anidado"""
        config = ConfigLoader()

        priority = config.get('languages.priority')
        assert priority is not None
        assert isinstance(priority, list)
        assert 'es' in priority or 'en' in priority

    def test_get_nonexistent_returns_default(self):
        """Test obtener clave inexistente retorna default"""
        config = ConfigLoader()

        value = config.get('nonexistent.key', 'default_value')
        assert value == 'default_value'

    def test_get_with_none_default(self):
        """Test obtener con default None"""
        config = ConfigLoader()

        value = config.get('nonexistent.key')
        assert value is None

    def test_load_custom_config(self, tmp_path):
        """Test cargar configuración personalizada"""
        config_file = tmp_path / 'custom_config.yaml'

        custom_config = {
            'app': {
                'name': 'Custom App',
                'version': '2.0.0'
            },
            'languages': {
                'priority': ['fr', 'de'],
                'fallback': 'fr'
            }
        }

        with open(config_file, 'w') as f:
            yaml.dump(custom_config, f)

        config = ConfigLoader(config_path=str(config_file))

        assert config.get('app.name') == 'Custom App'
        assert config.get('app.version') == '2.0.0'
        assert config.get('languages.priority') == ['fr', 'de']
        assert config.get('languages.fallback') == 'fr'

    def test_merge_partial_config(self, tmp_path):
        """Test merge de configuración parcial con defaults"""
        config_file = tmp_path / 'partial_config.yaml'

        # Solo override algunas configuraciones
        partial_config = {
            'app': {
                'name': 'Modified Name'
                # version no especificado, debe usar default
            }
        }

        with open(config_file, 'w') as f:
            yaml.dump(partial_config, f)

        config = ConfigLoader(config_path=str(config_file))

        # Valor overrideado
        assert config.get('app.name') == 'Modified Name'

        # Valor por defecto (no especificado en partial)
        assert config.get('app.version') is not None

        # Sección completa por defecto (no especificada en partial)
        assert config.get('languages.priority') is not None

    def test_invalid_yaml_uses_defaults(self, tmp_path):
        """Test YAML inválido usa configuración por defecto"""
        config_file = tmp_path / 'invalid.yaml'

        # YAML mal formado
        config_file.write_text('invalid: yaml: content: {')

        config = ConfigLoader(config_path=str(config_file))

        # Debe usar defaults a pesar del error
        assert config.get('app.name') is not None

    def test_empty_config_file_uses_defaults(self, tmp_path):
        """Test archivo vacío usa defaults"""
        config_file = tmp_path / 'empty.yaml'
        config_file.write_text('')

        config = ConfigLoader(config_path=str(config_file))

        assert config.get('app.name') is not None
        assert config.get('languages.priority') is not None

    def test_get_section(self):
        """Test obtener sección completa"""
        config = ConfigLoader()

        languages_section = config.get_section('languages')

        assert isinstance(languages_section, dict)
        assert 'priority' in languages_section
        assert 'fallback' in languages_section

    def test_get_nonexistent_section(self):
        """Test obtener sección inexistente"""
        config = ConfigLoader()

        section = config.get_section('nonexistent_section')

        assert section == {}

    def test_save_default_config(self, tmp_path):
        """Test guardar configuración por defecto"""
        config = ConfigLoader()
        save_path = tmp_path / 'saved_config.yaml'

        config.save_default(str(save_path))

        assert save_path.exists()

        # Verificar que se puede cargar
        with open(save_path, 'r') as f:
            loaded = yaml.safe_load(f)

        assert loaded is not None
        assert 'app' in loaded
        assert 'languages' in loaded

    def test_reload_config(self, tmp_path):
        """Test recargar configuración"""
        config_file = tmp_path / 'reload_test.yaml'

        # Crear config inicial
        initial_config = {
            'app': {'name': 'Initial Name'}
        }

        with open(config_file, 'w') as f:
            yaml.dump(initial_config, f)

        config = ConfigLoader(config_path=str(config_file))
        assert config.get('app.name') == 'Initial Name'

        # Modificar archivo
        modified_config = {
            'app': {'name': 'Modified Name'}
        }

        with open(config_file, 'w') as f:
            yaml.dump(modified_config, f)

        # Recargar
        config.reload()
        assert config.get('app.name') == 'Modified Name'

    def test_repr(self):
        """Test representación string"""
        config = ConfigLoader()
        repr_str = repr(config)

        assert 'ConfigLoader' in repr_str
        assert 'config_path' in repr_str


class TestGetConfigSingleton:
    """Tests para get_config singleton"""

    def test_get_config_returns_instance(self):
        """Test get_config retorna instancia"""
        config = get_config()

        assert config is not None
        assert isinstance(config, ConfigLoader)

    def test_get_config_is_singleton(self):
        """Test get_config es singleton"""
        config1 = get_config()
        config2 = get_config()

        # Deben ser la misma instancia
        assert config1 is config2

    def test_reload_config_function(self):
        """Test función reload_config"""
        # Asegurar que existe una instancia
        get_config()

        # reload_config no debe lanzar error
        reload_config()


class TestConfigValues:
    """Tests para valores específicos de configuración"""

    def test_app_section(self):
        """Test sección app tiene valores requeridos"""
        config = ConfigLoader()

        assert config.get('app.name') is not None
        assert config.get('app.version') is not None

    def test_output_section(self):
        """Test sección output tiene valores requeridos"""
        config = ConfigLoader()

        assert config.get('output.base_dir') is not None
        assert isinstance(config.get('output.create_plain'), bool)
        assert isinstance(config.get('output.create_timestamps'), bool)
        assert config.get('output.filename_pattern') is not None

    def test_languages_section(self):
        """Test sección languages tiene valores requeridos"""
        config = ConfigLoader()

        priority = config.get('languages.priority')
        assert priority is not None
        assert isinstance(priority, list)
        assert len(priority) > 0

        fallback = config.get('languages.fallback')
        assert fallback is not None
        assert isinstance(fallback, str)

    def test_extraction_section(self):
        """Test sección extraction tiene valores requeridos"""
        config = ConfigLoader()

        assert config.get('extraction.ytdlp.timeout') is not None
        assert config.get('extraction.ytdlp.retries') is not None
        assert config.get('extraction.fallback.enabled') is not None

    def test_processing_section(self):
        """Test sección processing tiene valores requeridos"""
        config = ConfigLoader()

        assert config.get('processing.delay_between_videos') is not None
        assert config.get('processing.cache.enabled') is not None
        assert config.get('processing.cache.file') is not None

    def test_logging_section(self):
        """Test sección logging tiene valores requeridos"""
        config = ConfigLoader()

        assert config.get('logging.level') is not None
        assert config.get('logging.file') is not None
        assert config.get('logging.format') is not None

    def test_ui_section(self):
        """Test sección ui tiene valores requeridos"""
        config = ConfigLoader()

        assert isinstance(config.get('ui.use_colors'), bool)
        assert isinstance(config.get('ui.show_progress_bar'), bool)


class TestConfigMerging:
    """Tests para merge de configuraciones"""

    def test_deep_merge(self, tmp_path):
        """Test merge profundo de configuraciones anidadas"""
        config_file = tmp_path / 'deep_merge.yaml'

        user_config = {
            'extraction': {
                'ytdlp': {
                    'timeout': 240  # Override solo timeout
                    # retries, retry_delay deben venir de defaults
                }
            }
        }

        with open(config_file, 'w') as f:
            yaml.dump(user_config, f)

        config = ConfigLoader(config_path=str(config_file))

        # Valor overrideado
        assert config.get('extraction.ytdlp.timeout') == 240

        # Valores por defecto en misma sección
        assert config.get('extraction.ytdlp.retries') is not None
        assert config.get('extraction.ytdlp.retry_delay') is not None

    def test_list_override_not_merge(self, tmp_path):
        """Test que listas se reemplazan, no se mezclan"""
        config_file = tmp_path / 'list_override.yaml'

        user_config = {
            'languages': {
                'priority': ['fr', 'de']  # Debe reemplazar completamente
            }
        }

        with open(config_file, 'w') as f:
            yaml.dump(user_config, f)

        config = ConfigLoader(config_path=str(config_file))

        # Lista debe ser reemplazada, no merged
        priority = config.get('languages.priority')
        assert priority == ['fr', 'de']
        assert 'es' not in priority
        assert 'en' not in priority
