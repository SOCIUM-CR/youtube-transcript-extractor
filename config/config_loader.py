"""
Configuration loader for YouTube Transcript Extractor.

Loads configuration from config.yaml and provides defaults.
"""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import os


class ConfigLoader:
    """
    Loads and manages application configuration.

    Reads from config.yaml if available, otherwise uses sensible defaults.
    """

    DEFAULT_CONFIG_PATH = 'config.yaml'

    # Default configuration if file doesn't exist
    DEFAULT_CONFIG = {
        'app': {
            'name': 'YouTube Transcript Extractor',
            'version': '1.1.0'
        },
        'output': {
            'base_dir': 'transcripts',
            'create_plain': True,
            'create_timestamps': True,
            'filename_pattern': '{index:03d}_{title}_{video_id}',
            'max_filename_length': 200
        },
        'languages': {
            'priority': ['es', 'en', 'fr', 'de', 'it', 'pt'],
            'fallback': 'en'
        },
        'extraction': {
            'ytdlp': {
                'timeout': 120,
                'retries': 3,
                'retry_delay': 2,
                'player_clients': ['web', 'web_safari', 'android', 'web_embedded'],
                'sub_languages': 'es,en,fr,de,it,pt'
            },
            'fallback': {
                'enabled': True,
                'timeout': 60
            }
        },
        'processing': {
            'parallel': {
                'enabled': False,
                'max_workers': 4
            },
            'delay_between_videos': 0.5,
            'cache': {
                'enabled': True,
                'file': '.transcript_cache.json'
            }
        },
        'logging': {
            'level': 'INFO',
            'file': 'youtube_extractor.log',
            'max_size_mb': 10,
            'backup_count': 3,
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'ui': {
            'use_colors': True,
            'show_progress_bar': True,
            'confirm_before_processing': True,
            'preview_urls_count': 5
        }
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize config loader.

        Args:
            config_path: Path to config file (default: config.yaml)
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.config = self.load()

    def load(self) -> Dict[str, Any]:
        """
        Load configuration from file or use defaults.

        Returns:
            Configuration dictionary
        """
        config_file = Path(self.config_path)

        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)

                if user_config:
                    # Merge user config with defaults
                    return self._merge_config(self.DEFAULT_CONFIG, user_config)
                else:
                    # Empty file, use defaults
                    return self.DEFAULT_CONFIG.copy()

            except yaml.YAMLError as e:
                print(f"⚠️  Error parsing config file: {e}")
                print("   Using default configuration")
                return self.DEFAULT_CONFIG.copy()
            except Exception as e:
                print(f"⚠️  Error loading config file: {e}")
                print("   Using default configuration")
                return self.DEFAULT_CONFIG.copy()
        else:
            # No config file, use defaults (don't create file automatically)
            return self.DEFAULT_CONFIG.copy()

    def _merge_config(self, default: dict, user: dict) -> dict:
        """
        Recursively merge user config with defaults.

        User values override defaults, but missing keys use defaults.

        Args:
            default: Default configuration
            user: User configuration

        Returns:
            Merged configuration
        """
        result = default.copy()

        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dicts
                result[key] = self._merge_config(result[key], value)
            else:
                # Override with user value
                result[key] = value

        return result

    def get(self, key_path: str, default=None):
        """
        Get configuration value using dot notation.

        Args:
            key_path: Dot-separated path (e.g., 'languages.priority')
            default: Default value if key not found

        Returns:
            Configuration value or default

        Examples:
            >>> config = ConfigLoader()
            >>> config.get('languages.priority')
            ['es', 'en', 'fr', 'de', 'it', 'pt']
            >>> config.get('languages.fallback')
            'en'
            >>> config.get('nonexistent.key', 'default_value')
            'default_value'
        """
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default

        return value if value is not None else default

    def save_default(self, path: Optional[str] = None):
        """
        Save default configuration to file.

        Args:
            path: Path to save config (default: self.config_path)
        """
        save_path = Path(path or self.config_path)

        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                yaml.dump(
                    self.DEFAULT_CONFIG,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False
                )
            print(f"✅ Default configuration saved to: {save_path}")
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")

    def reload(self):
        """Reload configuration from file."""
        self.config = self.load()

    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get entire configuration section.

        Args:
            section: Section name (e.g., 'languages', 'output')

        Returns:
            Section dictionary or empty dict if not found
        """
        return self.config.get(section, {})

    def __repr__(self):
        """String representation."""
        return f"ConfigLoader(config_path='{self.config_path}')"


# Singleton instance
_config_instance: Optional[ConfigLoader] = None


def get_config(config_path: Optional[str] = None) -> ConfigLoader:
    """
    Get singleton config instance.

    Args:
        config_path: Path to config file (only used on first call)

    Returns:
        ConfigLoader instance
    """
    global _config_instance

    if _config_instance is None:
        _config_instance = ConfigLoader(config_path)

    return _config_instance


def reload_config():
    """Reload configuration from file."""
    global _config_instance

    if _config_instance:
        _config_instance.reload()
    else:
        _config_instance = ConfigLoader()
