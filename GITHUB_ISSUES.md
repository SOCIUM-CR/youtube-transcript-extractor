# GitHub Issues - YouTube Transcript Extractor
## Issues Propuestos para Fases de Desarrollo

Este documento contiene las issues en formato listo para copiar a GitHub Issues.

---

## 🔴 FASE 1: FUNDAMENTOS (Prioridad Crítica)

### Issue #1: Implementar Suite de Tests Unitarios

**Labels:** `enhancement`, `testing`, `priority-critical`

**Descripción:**

Implementar una suite completa de tests con pytest para asegurar la estabilidad y calidad del código base. Actualmente el proyecto no tiene tests automatizados, lo que dificulta el desarrollo de nuevas features con confianza.

**Motivación:**
- Asegurar que cambios futuros no rompan funcionalidad existente
- Facilitar refactorización del código
- Mejorar confianza en releases
- Establecer base para CI/CD

**Tareas:**
- [ ] Setup pytest con configuración en `pytest.ini`
- [ ] Tests para `extract_video_id()` (mínimo 10 casos: URLs válidas, inválidas, edge cases)
- [ ] Tests para `_process_vtt_transcript()` con fixtures de archivos VTT
- [ ] Tests para `_detect_video_language()` con mocks de yt-dlp
- [ ] Tests para `validate_youtube_url()` (patrones válidos/inválidos)
- [ ] Tests para `_time_to_seconds()` y `_format_timestamp()`
- [ ] Setup GitHub Actions workflow para CI/CD
- [ ] Documentar cómo ejecutar tests en README

**Archivos a crear:**
```
tests/
├── __init__.py
├── conftest.py
├── unit/
│   ├── test_extractor.py
│   ├── test_processors.py
│   └── test_utils.py
└── fixtures/
    ├── sample.vtt
    └── sample_metadata.json
.github/
└── workflows/
    └── tests.yml
pytest.ini
```

**Criterios de Aceptación:**
- ✅ Cobertura mínima de código: 60%
- ✅ Todos los tests pasan en Python 3.8, 3.9, 3.10, 3.11
- ✅ CI/CD ejecuta tests automáticamente en cada push
- ✅ Documentación de cómo ejecutar tests localmente

**Estimación:** 3 días

---

### Issue #2: Implementar Validación y Sanitización de Input (Seguridad)

**Labels:** `security`, `priority-critical`, `bug`

**Descripción:**

Implementar validación robusta de nombres de archivo y paths para prevenir ataques de path traversal y otros problemas de seguridad. Actualmente los nombres de archivo se crean usando el título del video directamente sin sanitización adecuada.

**Problema de Seguridad:**
Un video con título malicioso como `../../../etc/passwd` o `<script>alert('xss')</script>` podría causar:
- Sobrescritura de archivos del sistema
- Creación de archivos en directorios no autorizados
- Problemas de encoding

**Propuesta de Solución:**

Crear módulo `utils/sanitize.py`:

```python
import re
from pathlib import Path

def sanitize_filename(filename: str, max_length: int = 200) -> str:
    """
    Sanitiza nombre de archivo removiendo caracteres peligrosos.

    Args:
        filename: Nombre de archivo a sanitizar
        max_length: Longitud máxima permitida

    Returns:
        Nombre de archivo seguro
    """
    # Remover path separators
    filename = filename.replace('/', '_').replace('\\', '_')

    # Remover caracteres peligrosos
    dangerous_chars = ['..', '<', '>', ':', '"', '|', '?', '*', '\0', '\n', '\r']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')

    # Remover caracteres no-ASCII problemáticos
    filename = re.sub(r'[^\w\s\-.]', '_', filename)

    # Colapsar múltiples underscores
    filename = re.sub(r'_+', '_', filename)

    # Truncar si excede max_length
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[:max_length-len(ext)] + ext

    # Asegurar que no esté vacío
    if not filename or filename == '_':
        filename = 'untitled'

    return filename.strip('_. ')

def validate_output_path(base_dir: str, user_path: str) -> bool:
    """
    Valida que el path de salida esté dentro del directorio base.
    Previene path traversal attacks.
    """
    base_path = Path(base_dir).resolve()
    full_path = (base_path / user_path).resolve()

    # Verificar que full_path esté dentro de base_path
    try:
        full_path.relative_to(base_path)
        return True
    except ValueError:
        return False
```

**Tareas:**
- [ ] Crear módulo `utils/sanitize.py`
- [ ] Implementar `sanitize_filename()` con casos edge
- [ ] Implementar `validate_output_path()`
- [ ] Aplicar sanitización en `youtube_transcript_extractor.py:459`
- [ ] Tests exhaustivos con inputs maliciosos
- [ ] Documentar caracteres permitidos en README

**Casos de Test Requeridos:**
```python
# Path traversal
assert sanitize_filename("../../../etc/passwd") != "../../../etc/passwd"

# Script injection
assert "<" not in sanitize_filename("<script>alert('xss')</script>")

# Long names
assert len(sanitize_filename("a" * 300)) <= 200

# Unicode
assert sanitize_filename("Título con ñ y émojis 🎥") # Should handle gracefully

# Empty/whitespace
assert sanitize_filename("   ") == "untitled"
```

**Archivos Afectados:**
- `utils/sanitize.py` (nuevo)
- `youtube_transcript_extractor.py` línea 459
- `tests/unit/test_sanitize.py` (nuevo)

**Criterios de Aceptación:**
- ✅ Todos los paths son validados antes de crear archivos
- ✅ Nombres de archivo no contienen caracteres peligrosos
- ✅ Tests cubren casos maliciosos (path traversal, XSS, etc.)
- ✅ No se rompe funcionalidad con títulos Unicode válidos

**Estimación:** 1 día

---

### Issue #3: Sistema de Configuración Externalizada

**Labels:** `enhancement`, `refactor`, `priority-high`

**Descripción:**

Mover todas las configuraciones hardcodeadas del código a un archivo de configuración externo (`config.yaml`). Esto permitirá a los usuarios personalizar el comportamiento sin modificar código.

**Configuraciones Actualmente Hardcodeadas:**
- Idiomas prioritarios: `['es', 'en', 'fr', 'de', 'it', 'pt']`
- Directorio de salida: `'transcripts'`
- Timeout de yt-dlp: No configurable
- Delay entre videos: `0.5` segundos
- Formato de nombres de archivo: `"{idx:03d}_{title}_{video_id}"`
- Nivel de logging: No configurable

**Propuesta:**

Crear archivo `config.yaml` con estructura:

```yaml
# config.yaml - YouTube Transcript Extractor Configuration

app:
  name: "YouTube Transcript Extractor"
  version: "1.1.0"

output:
  # Directorio base para transcripciones
  base_dir: "transcripts"

  # Crear ambos formatos
  create_plain: true
  create_timestamps: true

  # Patrón de nombres: {index}, {title}, {video_id}
  filename_pattern: "{index:03d}_{title}_{video_id}"
  max_filename_length: 200

languages:
  # Orden de prioridad para selección de idioma
  priority:
    - es
    - en
    - fr
    - de
    - it
    - pt

  # Idioma fallback si ninguno disponible
  fallback: en

extraction:
  # Configuración de yt-dlp
  ytdlp:
    timeout: 120  # segundos
    retries: 3
    retry_delay: 2  # segundos entre reintentos

    # Clientes de player a intentar
    player_clients:
      - web
      - web_safari
      - android
      - web_embedded

  # youtube-transcript-api como fallback
  fallback:
    enabled: true
    timeout: 60

processing:
  # Procesamiento paralelo (Feature futura - Issue #6)
  parallel:
    enabled: false
    max_workers: 4

  # Rate limiting para evitar bans de YouTube
  delay_between_videos: 0.5  # segundos

  # Caché de videos ya procesados
  cache:
    enabled: true
    file: ".transcript_cache.json"

logging:
  # Nivel: DEBUG, INFO, WARNING, ERROR, CRITICAL
  level: INFO

  # Archivo de log
  file: "youtube_extractor.log"

  # Rotación de logs
  max_size_mb: 10
  backup_count: 3

  # Formato de mensajes
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

ui:
  # Opciones de interfaz
  use_colors: true
  show_progress_bar: true
  confirm_before_processing: true
```

**Implementación:**

Crear `config/config_loader.py`:

```python
import yaml
from pathlib import Path
from typing import Dict, Any

class ConfigLoader:
    DEFAULT_CONFIG_PATH = 'config.yaml'

    DEFAULT_CONFIG = {
        'output': {'base_dir': 'transcripts'},
        'languages': {'priority': ['es', 'en'], 'fallback': 'en'},
        # ... resto de defaults
    }

    def __init__(self, config_path: str = None):
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.config = self.load()

    def load(self) -> Dict[str, Any]:
        """Carga configuración desde archivo o usa defaults."""
        if Path(self.config_path).exists():
            with open(self.config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                return self._merge_config(self.DEFAULT_CONFIG, user_config)
        else:
            # Generar config default si no existe
            self.save_default()
            return self.DEFAULT_CONFIG.copy()

    def _merge_config(self, default: dict, user: dict) -> dict:
        """Merge recursivo de configuraciones."""
        result = default.copy()
        for key, value in user.items():
            if isinstance(value, dict) and key in result:
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result

    def save_default(self):
        """Genera archivo de configuración default."""
        with open(self.config_path, 'w') as f:
            yaml.dump(self.DEFAULT_CONFIG, f, default_flow_style=False)

    def get(self, key_path: str, default=None):
        """Get configuración usando dot notation: 'languages.priority'"""
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
        return value if value is not None else default
```

**Tareas:**
- [ ] Añadir `PyYAML` a `requirements.txt`
- [ ] Crear estructura de `config.yaml` default
- [ ] Implementar `config/config_loader.py`
- [ ] Migrar constantes hardcodeadas a usar config
- [ ] Actualizar `install.py` para generar `config.yaml`
- [ ] Tests para config loader
- [ ] Documentar opciones de configuración en README

**Archivos Afectados:**
- `config/config.yaml` (nuevo)
- `config/config_loader.py` (nuevo)
- `youtube_transcript_extractor.py` (refactor para usar config)
- `install.py` (generar config en instalación)
- `requirements.txt` (añadir PyYAML)
- `README.md` (documentar configuración)

**Criterios de Aceptación:**
- ✅ Cero configuraciones hardcodeadas en código
- ✅ Config se genera automáticamente en instalación
- ✅ Valores por defecto sensatos si falta config
- ✅ Documentación completa de todas las opciones
- ✅ Backwards compatible (funciona sin config.yaml)

**Estimación:** 2 días

---

### Issue #4: Sistema de Detección de Duplicados

**Labels:** `enhancement`, `priority-high`, `performance`

**Descripción:**

Implementar sistema de detección de duplicados para evitar procesar el mismo video múltiples veces. Actualmente si un video aparece en múltiples playlists o archivos de entrada, se procesa cada vez, desperdiciando tiempo y recursos.

**Casos de Uso:**
1. Usuario procesa playlist con 50 videos
2. Más tarde procesa otra playlist que comparte 20 videos
3. Actualmente: Se re-procesan los 20 videos (pérdida de tiempo)
4. Deseado: Se detecta que ya están procesados y se saltean

**Implementación:**

Crear `cache/transcript_cache.py`:

```python
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

class TranscriptCache:
    """Gestiona caché de videos ya procesados."""

    def __init__(self, cache_file: str = '.transcript_cache.json'):
        self.cache_file = Path(cache_file)
        self.cache: Dict[str, dict] = self._load_cache()

    def _load_cache(self) -> dict:
        """Carga caché desde archivo."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def _save_cache(self):
        """Guarda caché a archivo."""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)

    def is_processed(self, video_id: str) -> bool:
        """Verifica si video ya fue procesado."""
        return video_id in self.cache

    def get_entry(self, video_id: str) -> Optional[dict]:
        """Obtiene entrada de caché para un video."""
        return self.cache.get(video_id)

    def mark_processed(
        self,
        video_id: str,
        title: str,
        language: str,
        method: str,
        folder: str
    ):
        """Marca video como procesado."""
        self.cache[video_id] = {
            'video_id': video_id,
            'title': title,
            'language': language,
            'method': method,
            'folder': folder,
            'processed_at': datetime.now().isoformat(),
            'version': '1.0'  # Para compatibilidad futura
        }
        self._save_cache()

    def remove(self, video_id: str):
        """Remueve entrada de caché."""
        if video_id in self.cache:
            del self.cache[video_id]
            self._save_cache()

    def clear(self):
        """Limpia todo el caché."""
        self.cache = {}
        self._save_cache()

    def get_stats(self) -> dict:
        """Retorna estadísticas del caché."""
        if not self.cache:
            return {
                'total_cached': 0,
                'oldest_entry': None,
                'newest_entry': None
            }

        dates = [entry['processed_at'] for entry in self.cache.values()]
        return {
            'total_cached': len(self.cache),
            'oldest_entry': min(dates),
            'newest_entry': max(dates),
            'languages': self._count_by_field('language'),
            'methods': self._count_by_field('method')
        }

    def _count_by_field(self, field: str) -> dict:
        """Cuenta entradas por campo."""
        counts = {}
        for entry in self.cache.values():
            value = entry.get(field, 'unknown')
            counts[value] = counts.get(value, 0) + 1
        return counts
```

**Integración en flujo principal:**

```python
# En YouTubeTranscriptExtractor.__init__():
self.cache = TranscriptCache()

# En process_videos_from_urls():
def process_videos_from_urls(self, urls: List[str], folder_name: str):
    # Filtrar videos ya procesados
    videos_to_process = []
    videos_skipped = []

    for url in urls:
        video_id = self.extract_video_id(url)
        if self.cache.is_processed(video_id) and not self.config.get('force_reprocess'):
            videos_skipped.append(url)
            cached_entry = self.cache.get_entry(video_id)
            self.console.print(
                f'[dim]⏭️  Skipping {video_id}: Already processed on '
                f'{cached_entry["processed_at"]}[/dim]'
            )
        else:
            videos_to_process.append(url)

    # Mostrar resumen
    if videos_skipped:
        self.console.print(
            f'\n[yellow]ℹ️  Skipped {len(videos_skipped)} already processed videos[/yellow]'
        )
        self.console.print(
            f'[dim]Use --force to reprocess them[/dim]'
        )

    # Procesar solo videos nuevos
    for url in videos_to_process:
        # ... procesamiento normal ...

        # Al terminar exitosamente:
        self.cache.mark_processed(
            video_id=video_id,
            title=title,
            language=transcript['selected_language'],
            method=transcript['method'],
            folder=folder_name
        )
```

**Nuevas opciones de CLI:**

```bash
# Ver estadísticas de caché
python youtube_transcript_extractor.py --cache-stats

# Limpiar caché
python youtube_transcript_extractor.py --clear-cache

# Forzar reprocesamiento ignorando caché
python youtube_transcript_extractor.py --force
```

**Tareas:**
- [ ] Implementar `cache/transcript_cache.py`
- [ ] Integrar en `YouTubeTranscriptExtractor`
- [ ] Agregar flags `--force`, `--cache-stats`, `--clear-cache`
- [ ] UI muestra videos skipped vs procesados
- [ ] Tests para cache (add, check, clear)
- [ ] Documentar en README

**Criterios de Aceptación:**
- ✅ Videos duplicados se detectan y saltean
- ✅ Mensaje claro indica cuando se salta un video
- ✅ Opción `--force` permite reprocesar
- ✅ Caché persiste entre ejecuciones
- ✅ Estadísticas de caché disponibles

**Estimación:** 1 día

---

### Issue #5: Sistema de Logging Estructurado

**Labels:** `enhancement`, `priority-medium`, `infrastructure`

**Descripción:**

Implementar sistema de logging robusto con rotación de archivos, diferentes niveles y formato estructurado. Actualmente el proyecto usa `print()` y mensajes de Rich console, pero no hay logs persistentes para debugging.

**Motivación:**
- Debugging de errores reportados por usuarios
- Auditoría de procesamiento
- Análisis de performance
- Troubleshooting de problemas de red/YouTube

**Implementación:**

Crear `utils/logging_config.py`:

```python
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging(config: dict) -> logging.Logger:
    """
    Configura sistema de logging.

    Args:
        config: Dict con configuración de logging

    Returns:
        Logger configurado
    """
    logger = logging.getLogger('youtube_extractor')
    logger.setLevel(getattr(logging, config['logging']['level']))

    # Evitar duplicar handlers
    if logger.handlers:
        return logger

    # File handler con rotación
    log_file = Path(config['logging']['file'])
    log_file.parent.mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=config['logging']['max_size_mb'] * 1024 * 1024,
        backupCount=config['logging']['backup_count'],
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)  # Log todo a archivo
    file_handler.setFormatter(logging.Formatter(
        config['logging']['format']
    ))
    logger.addHandler(file_handler)

    # Console handler (solo WARNING y ERROR)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(logging.Formatter(
        '%(levelname)s: %(message)s'
    ))
    logger.addHandler(console_handler)

    return logger
```

**Uso en código:**

```python
# En YouTubeTranscriptExtractor.__init__():
self.logger = setup_logging(self.config)

# Reemplazar prints con logs:
# Antes:
print(f"Error al procesar video: {e}")

# Después:
self.logger.error(f"Error al procesar video {video_id}: {e}", exc_info=True)

# Niveles de logging:
self.logger.debug(f"Fetching metadata for {video_id}")
self.logger.info(f"Successfully processed {video_id}")
self.logger.warning(f"No transcript found for {video_id}, using fallback")
self.logger.error(f"Failed to process {video_id}: {error}")
self.logger.critical(f"yt-dlp not found in PATH")
```

**Estructura de Log File:**

```
2025-11-05 10:30:15,123 - youtube_extractor - INFO - Starting YouTube Transcript Extractor v1.1.0
2025-11-05 10:30:15,456 - youtube_extractor - DEBUG - Loading config from config.yaml
2025-11-05 10:30:16,789 - youtube_extractor - INFO - Processing 25 videos from playlist
2025-11-05 10:30:17,012 - youtube_extractor - DEBUG - Extracting video ID from https://youtube.com/watch?v=abc123
2025-11-05 10:30:18,345 - youtube_extractor - INFO - Detected language: en
2025-11-05 10:30:20,678 - youtube_extractor - DEBUG - Running yt-dlp with args: ['yt-dlp', '--write-auto-sub', ...]
2025-11-05 10:30:25,901 - youtube_extractor - WARNING - yt-dlp failed, trying fallback method
2025-11-05 10:30:27,234 - youtube_extractor - INFO - Successfully extracted transcript using youtube-transcript-api
2025-11-05 10:30:27,567 - youtube_extractor - ERROR - Failed to process video xyz789: Connection timeout
Traceback (most recent call last):
  File "youtube_transcript_extractor.py", line 456, in get_transcript
    ...
```

**Tareas:**
- [ ] Implementar `utils/logging_config.py`
- [ ] Integrar en `YouTubeTranscriptExtractor`
- [ ] Reemplazar `print()` statements con `logger` calls
- [ ] Configuración de logging en `config.yaml`
- [ ] Tests para logger
- [ ] Documentar niveles de logging en README
- [ ] Añadir a `.gitignore`: `*.log`

**Archivos Afectados:**
- `utils/logging_config.py` (nuevo)
- `youtube_transcript_extractor.py` (refactor logging)
- `config.yaml` (sección logging)
- `.gitignore` (ignorar logs)

**Criterios de Aceptación:**
- ✅ Todos los `print()` reemplazados por logger
- ✅ Logs rotan automáticamente
- ✅ Nivel configurable desde config.yaml
- ✅ Stack traces capturados en errors
- ✅ Timestamps en todos los logs

**Estimación:** 1 día

---

## 🟠 FASE 2: OPTIMIZACIÓN

### Issue #6: Procesamiento Paralelo de Videos

**Labels:** `enhancement`, `performance`, `priority-high`

**Descripción:**

Implementar procesamiento paralelo/concurrente de videos para reducir significativamente el tiempo total de procesamiento. Actualmente los videos se procesan secuencialmente, lo que es ineficiente.

**Problema Actual:**
- Playlist con 100 videos a ~10 seg/video = 1000 segundos (~17 minutos)
- La mayoría del tiempo es I/O (red) esperando respuestas

**Solución Propuesta:**
- Procesamiento paralelo con ThreadPoolExecutor
- 4 workers procesando simultáneamente
- Tiempo estimado: 250 segundos (~4 minutos) = **Reducción del 75%**

**Implementación:** Ver `DEVELOPMENT_ROADMAP.md` sección Issue #6

**Tareas:**
- [ ] Refactorizar `process_videos_from_urls()` para threading
- [ ] Implementar `_process_single_video()` thread-safe
- [ ] Progress bar compatible con concurrencia
- [ ] Rate limiting entre workers
- [ ] Configuración `parallel.enabled` en config
- [ ] Benchmarks antes/después
- [ ] Tests de concurrencia

**Estimación:** 5 días

---

### Issue #7: Refactorización Modular del Código

**Labels:** `refactor`, `priority-high`, `technical-debt`

**Descripción:**

Refactorizar el archivo monolítico `youtube_transcript_extractor.py` (752 líneas) en una estructura modular bien organizada. Esto mejorará mantenibilidad, testing y reusabilidad.

**Nueva Estructura:** Ver `DEVELOPMENT_ROADMAP.md` sección Issue #7

**Tareas:**
- [ ] Crear estructura de paquetes `ytextractor/`
- [ ] Migrar código a módulos correspondientes
- [ ] Actualizar imports
- [ ] Mantener compatibilidad hacia atrás
- [ ] Documentar nueva estructura

**Estimación:** 4 días

---

## 🟡 FASE 3: NUEVAS FUNCIONALIDADES

### Issue #9: Exportación a Múltiples Formatos

**Labels:** `feature`, `priority-medium`

**Descripción:**

Soportar exportación de transcripciones a múltiples formatos: JSON, CSV, SRT (subtítulos), Markdown, DOCX.

**Formatos a Implementar:**
- JSON: Datos estructurados con metadata
- CSV: Para análisis en Excel/pandas
- SRT: Subtítulos estándar
- Markdown: Documentación legible
- DOCX (opcional): Word documents

**Ver Especificación Completa:** `DEVELOPMENT_ROADMAP.md` Issue #9

**Tareas:**
- [ ] Implementar exporters para cada formato
- [ ] Menú de selección de formatos
- [ ] Configuración de formatos default
- [ ] Tests para cada exporter

**Estimación:** 5 días

---

### Issue #10: Sistema de Estadísticas y Analytics

**Labels:** `feature`, `analytics`, `priority-medium`

**Descripción:**

Generar estadísticas automáticas sobre contenido procesado: duración total, conteo de palabras, distribución de idiomas, keywords frecuentes.

**Estadísticas a Incluir:**
- Total de videos procesados
- Duración total (suma de timestamps)
- Palabras totales y promedio por video
- Distribución de idiomas
- Top 10 keywords más frecuentes
- Métodos de extracción usados

**Exportar a:** JSON, CSV, visualización en consola

**Estimación:** 3 días

---

### Issue #11: Resume de Sesiones Interrumpidas

**Labels:** `feature`, `priority-medium`, `ux`

**Descripción:**

Guardar progreso de procesamiento y permitir retomar sesiones interrumpidas (Ctrl+C, crash, pérdida de conexión).

**Funcionalidad:**
- Guardar estado cada N videos procesados
- Al iniciar, detectar sesión interrumpida
- Preguntar al usuario si desea retomar
- Continuar desde último video procesado

**Ver Implementación:** `DEVELOPMENT_ROADMAP.md` Issue #11

**Estimación:** 3 días

---

## 🟢 FASE 4: INNOVACIÓN

### Issue #13: Integración con OpenAI para Resúmenes Automáticos

**Labels:** `feature`, `ai`, `priority-medium`

**Descripción:**

Integrar OpenAI GPT-4 API para generar resúmenes automáticos de transcripciones, extracción de keywords con IA, y Q&A sobre contenido.

**Funcionalidades:**
- Resumen en bullet points (3-5 puntos clave)
- Resumen en párrafo
- Extracción de keywords principales
- Traducción automática
- Q&A sobre el video

**Consideraciones:**
- Costos de API (~$0.03 por video)
- Límites de tokens (4K para GPT-4)
- Caché de resúmenes generados
- Configuración de API key en `.env`

**Estimación:** 5 días

---

### Issue #14: GUI con Streamlit

**Labels:** `feature`, `ui`, `priority-low`

**Descripción:**

Crear interfaz web con Streamlit para usuarios no técnicos.

**Características:**
- Upload de archivos con URLs
- Selección visual de opciones
- Progress tracking en tiempo real
- Preview de transcripciones
- Download de resultados
- Visualización de estadísticas

**Estimación:** 7 días

---

## Notas de Implementación

### Orden Recomendado:
1. Issue #1 (Tests) - **CRÍTICO**
2. Issue #2 (Seguridad) - **CRÍTICO**
3. Issue #3 (Config)
4. Issue #4 (Caché)
5. Issue #5 (Logging)
6. Issue #6 (Paralelo)
7. Issue #7 (Refactor)
8. Resto según prioridad

### Labels Propuestas para GitHub:
- `priority-critical` (🔴)
- `priority-high` (🟠)
- `priority-medium` (🟡)
- `priority-low` (🟢)
- `enhancement`
- `feature`
- `bug`
- `security`
- `refactor`
- `testing`
- `documentation`
- `performance`
- `ui`
- `ai`

---

**Para crear estas issues en GitHub:**
1. Ir a repositorio → Issues → New Issue
2. Copiar título y contenido
3. Añadir labels correspondientes
4. Asignar milestone (ej: "v1.1.0 - Foundations")
5. Crear issue

**Documentos de Referencia:**
- `TECHNICAL_ANALYSIS.md` - Análisis técnico detallado
- `DEVELOPMENT_ROADMAP.md` - Plan de desarrollo completo
