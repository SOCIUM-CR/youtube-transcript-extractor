# ✅ Checklist Pre-Refactorización

**Propósito:** Verificar que TODO el software funciona correctamente ANTES de hacer la refactorización modular (Issue #7).

**Fecha de verificación:** ___________
**Verificado por:** ___________
**Versión del código:** ___________

---

## 🎯 Por qué este Checklist

Antes de refactorizar 752 líneas de código en módulos separados, necesitamos:
1. ✅ Verificar que todo funciona perfectamente ahora
2. ✅ Documentar el comportamiento actual esperado
3. ✅ Tener una baseline para comparar después de la refactorización

**Regla de oro:** Si algún test falla ANTES de refactorizar, arreglarlo primero.

---

## 🚀 Opción Rápida: Script Automatizado

```bash
# Ejecutar todos los tests automatizados (3-5 minutos)
./functional_test.sh
```

**Resultado esperado:**
```
✅ Tests Pasados: 25+ / 27
📊 Tasa de Éxito: >90%
✨ TODOS LOS TESTS PASARON ✨
```

Si el script automatizado pasa, puedes saltar a la sección "Checklist Final".

---

## 📋 Opción Manual: Testing Paso a Paso

### FASE 1: Tests Unitarios Automatizados

#### [ ] Test 1.1: Suite Completa de Tests
```bash
python -m pytest tests/unit/ -v
```

**Resultado esperado:**
- ✅ 215+ tests passing
- ❌ 2 fallos máximo (tests de red)
- ⏭️ 1 skipped

**Cobertura:**
```bash
python -m pytest tests/unit/ --cov
```
- ✅ Cobertura total: >30%
- ✅ cache/: >85%
- ✅ utils/logging: >65%

#### [ ] Test 1.2: Tests por Módulo
```bash
# Cache (33 tests)
python -m pytest tests/unit/test_cache.py -v

# Logging (21 tests)
python -m pytest tests/unit/test_logging.py -v

# Sanitización (79 tests)
python -m pytest tests/unit/test_sanitize.py -v

# Configuración (26 tests)
python -m pytest tests/unit/test_config.py -v
```

**Todos deben pasar 100%**

---

### FASE 2: Verificación de Importaciones

#### [ ] Test 2.1: Módulo Principal
```bash
python -c "from youtube_transcript_extractor import YouTubeTranscriptExtractor; print('✅ OK')"
```

#### [ ] Test 2.2: Sistema de Caché
```bash
python -c "from cache import TranscriptCache; print('✅ OK')"
```

#### [ ] Test 2.3: Sistema de Logging
```bash
python -c "from utils.logging_config import setup_logging; print('✅ OK')"
```

#### [ ] Test 2.4: Sistema de Configuración
```bash
python -c "from config import get_config; print('✅ OK')"
```

#### [ ] Test 2.5: Utilidades
```bash
python -c "from utils.sanitize import sanitize_filename; print('✅ OK')"
```

**Resultado esperado:** Todos imprimen "✅ OK"

---

### FASE 3: Funcionalidades Básicas (Programático)

#### [ ] Test 3.1: Extracción de Video ID

```bash
python << 'EOF'
from youtube_transcript_extractor import YouTubeTranscriptExtractor

extractor = YouTubeTranscriptExtractor()

# Test diferentes formatos de URL
urls = {
    'https://www.youtube.com/watch?v=dQw4w9WgXcQ': 'dQw4w9WgXcQ',
    'https://youtu.be/dQw4w9WgXcQ': 'dQw4w9WgXcQ',
    'https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30s': 'dQw4w9WgXcQ',
}

for url, expected in urls.items():
    video_id = extractor.extract_video_id(url)
    assert video_id == expected, f"FAIL: {url}"
    print(f"✅ {url} -> {video_id}")

print("\n✅ Todos los formatos de URL funcionan")
EOF
```

#### [ ] Test 3.2: Validación de URLs

```bash
python << 'EOF'
from youtube_transcript_extractor import YouTubeTranscriptExtractor

extractor = YouTubeTranscriptExtractor()

# URLs válidas
valid = [
    'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    'https://youtu.be/dQw4w9WgXcQ',
    'HTTPS://WWW.YOUTUBE.COM/WATCH?V=dQw4w9WgXcQ',  # Mayúsculas
]

for url in valid:
    assert extractor.validate_youtube_url(url), f"FAIL: {url} debería ser válido"
    print(f"✅ Válido: {url}")

# URLs inválidas
invalid = [
    'https://www.google.com',
    'not a url',
    'https://youtube.com/watch?v=',  # Sin ID
]

for url in invalid:
    assert not extractor.validate_youtube_url(url), f"FAIL: {url} debería ser inválido"
    print(f"✅ Inválido (correcto): {url}")

print("\n✅ Validación de URLs funciona correctamente")
EOF
```

#### [ ] Test 3.3: Conversión de Timestamps

```bash
python << 'EOF'
from youtube_transcript_extractor import YouTubeTranscriptExtractor

extractor = YouTubeTranscriptExtractor()

tests = [
    (0, "00:00:00"),
    (30, "00:00:30"),
    (61, "00:01:01"),
    (3661, "01:01:01"),
    (90.5, "00:01:30"),
]

for seconds, expected in tests:
    result = extractor._format_timestamp(seconds)
    assert result == expected, f"FAIL: {seconds}s -> {result} (esperado {expected})"
    print(f"✅ {seconds}s -> {result}")

print("\n✅ Conversión de timestamps funciona")
EOF
```

---

### FASE 4: Sistema de Caché

#### [ ] Test 4.1: Operaciones Básicas de Caché

```bash
python << 'EOF'
from cache import TranscriptCache
import os

cache = TranscriptCache('.test_manual_cache.json')

# Marcar videos como procesados
cache.mark_processed('test1', 'Video 1', 'en', 'yt-dlp', 'test_folder')
cache.mark_processed('test2', 'Video 2', 'es', 'fallback', 'test_folder')

# Verificar
assert cache.is_processed('test1'), "test1 debería estar procesado"
assert cache.is_processed('test2'), "test2 debería estar procesado"
assert not cache.is_processed('test3'), "test3 NO debería estar procesado"

print("✅ Cache marca videos correctamente")

# Estadísticas
stats = cache.get_stats()
assert stats['total_cached'] == 2, "Debería tener 2 videos"
assert stats['by_language']['en'] == 1
assert stats['by_language']['es'] == 1

print("✅ Estadísticas funcionan")

# Limpiar
cache.clear()
assert stats['total_cached'] == 2  # stats es snapshot
assert len(cache.cache) == 0, "Cache debería estar vacío"

print("✅ Clear funciona")

# Limpiar archivo
os.remove('.test_manual_cache.json')

print("\n✅ Sistema de caché funciona completamente")
EOF
```

#### [ ] Test 4.2: Persistencia de Caché

```bash
python << 'EOF'
from cache import TranscriptCache
import os

# Crear y guardar
cache1 = TranscriptCache('.test_persist.json')
cache1.mark_processed('persist_test', 'Test Video', 'en', 'yt-dlp', 'test')

# Cargar en nueva instancia
cache2 = TranscriptCache('.test_persist.json')
assert cache2.is_processed('persist_test'), "Caché debería persistir"

print("✅ Caché persiste entre sesiones")

# Limpiar
os.remove('.test_persist.json')
EOF
```

---

### FASE 5: Sistema de Logging

#### [ ] Test 5.1: Logging Básico

```bash
python << 'EOF'
from utils.logging_config import setup_logging
from config import ConfigLoader
from pathlib import Path

log_file = Path('.test_manual_logging.log')
if log_file.exists():
    log_file.unlink()

config = ConfigLoader()
config.config['logging']['file'] = str(log_file)
config.config['logging']['console'] = False
config.config['logging']['level'] = 'INFO'

logger = setup_logging('test_manual', config=config, force=True)

# Loggear diferentes niveles
logger.debug('DEBUG message')
logger.info('INFO message')
logger.warning('WARNING message')
logger.error('ERROR message')

# Flush
for handler in logger.handlers:
    handler.flush()

# Verificar archivo
assert log_file.exists(), "Log file debe existir"

content = log_file.read_text()
assert 'INFO message' in content
assert 'WARNING message' in content
assert 'ERROR message' in content

print("✅ Logging funciona correctamente")
print(f"✅ Archivo: {log_file}")

# Limpiar
log_file.unlink()
EOF
```

---

### FASE 6: Comandos CLI

#### [ ] Test 6.1: --help
```bash
python youtube_transcript_extractor.py --help
```

**Verificar que muestra:**
- ✅ Descripción del programa
- ✅ Opciones: --force, --cache-stats, --clear-cache
- ✅ Ejemplos de uso

#### [ ] Test 6.2: --cache-stats
```bash
python youtube_transcript_extractor.py --cache-stats
```

**Resultado esperado:**
```
📊 Estadísticas de Caché

┏━━━━━━━━━━━━┳━━━━━━━┓
┃ Métrica    ┃ Valor ┃
┡━━━━━━━━━━━━╇━━━━━━━┩
│ Total...   │ X     │
└────────────┴───────┘
```

#### [ ] Test 6.3: Inicialización sin errores
```bash
python -c "from youtube_transcript_extractor import YouTubeTranscriptExtractor; e = YouTubeTranscriptExtractor(); print('✅ Inicialización OK')"
```

---

### FASE 7: Testing con Video Real (IMPORTANTE)

**⚠️ Esta es la prueba MÁS IMPORTANTE - verifica que el software hace su función principal**

#### [ ] Test 7.1: Extraer transcripción de 1 video

1. Ejecutar:
```bash
python youtube_transcript_extractor.py
```

2. Seleccionar: **Opción 1** (Video individual)

3. Ingresar URL: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`

4. Carpeta: `test_manual_single`

5. **Verificar:**
   - [ ] Video se procesa sin errores
   - [ ] Mensaje de éxito aparece
   - [ ] Se crean 2 archivos:
     ```bash
     ls transcripts/test_manual_single/transcripts_plain/
     ls transcripts/test_manual_single/transcripts_timestamps/
     ```
   - [ ] Archivo `.transcript_cache.json` se crea
   - [ ] Archivo `youtube_extractor.log` se crea

6. **Verificar contenido de archivos:**
   ```bash
   # Ver transcripción plana
   cat transcripts/test_manual_single/transcripts_plain/001_*.txt

   # Debe contener:
   # - "Método: yt-dlp" o "Método: youtube-transcript-api"
   # - "Idioma: en" (o similar)
   # - Texto de la transcripción
   ```

   ```bash
   # Ver transcripción con timestamps
   cat transcripts/test_manual_single/transcripts_timestamps/001_*.txt

   # Debe contener:
   # - [00:00:00] texto
   # - [00:00:05] más texto
   # - etc.
   ```

#### [ ] Test 7.2: Procesar múltiples videos desde archivo

1. Crear archivo de URLs:
   ```bash
   cat > test_manual_urls.txt << 'EOF'
   https://www.youtube.com/watch?v=dQw4w9WgXcQ
   https://www.youtube.com/watch?v=9bZkp7q19f0
   EOF
   ```

2. Ejecutar:
   ```bash
   python youtube_transcript_extractor.py
   ```

3. Seleccionar: **Opción 2** (Lista desde archivo)

4. Archivo: `test_manual_urls.txt`

5. Carpeta: `test_manual_batch`

6. **Verificar:**
   - [ ] Ambos videos se procesan
   - [ ] Progress bar funciona
   - [ ] Se crean 4 archivos (2 plain + 2 timestamps)
   - [ ] Resumen final muestra "2/2 exitosos"
   - [ ] Cache tiene 2 entradas

#### [ ] Test 7.3: Sistema de caché funciona (skip duplicados)

1. **Ejecutar NUEVAMENTE el test 7.2** (mismo archivo)

2. **Verificar:**
   - [ ] Mensaje aparece: "Videos ya procesados (omitidos)"
   - [ ] Muestra los 2 videos que se omiten
   - [ ] NO reprocesa (termina rápido)
   - [ ] Mensaje: "Usa --force para reprocesarlos"

#### [ ] Test 7.4: Flag --force funciona

1. Ejecutar con --force:
   ```bash
   python youtube_transcript_extractor.py --force
   ```

2. Seleccionar opción 2, mismo archivo

3. **Verificar:**
   - [ ] Mensaje: "Modo FORCE activado"
   - [ ] Reprocesa todos los videos
   - [ ] NO muestra mensaje de "omitidos"

---

### FASE 8: Verificación de Archivos

#### [ ] Test 8.1: Archivos Críticos Existen

```bash
# Verificar estructura de archivos
ls -la youtube_transcript_extractor.py    # Archivo principal
ls -la cache/transcript_cache.py          # Sistema caché
ls -la utils/logging_config.py            # Sistema logging
ls -la config/config_loader.py            # Sistema config
ls -la config.yaml                        # Configuración

# Verificar tests
ls -la tests/unit/test_cache.py
ls -la tests/unit/test_logging.py
ls -la tests/unit/test_sanitize.py
ls -la tests/unit/test_config.py

# Documentación
ls -la README.md
ls -la TESTING_GUIDE.md
ls -la DEVELOPMENT_ROADMAP.md
```

**Todos deben existir ✅**

#### [ ] Test 8.2: Configuración Válida

```bash
# Verificar que config.yaml es válido
python -c "import yaml; yaml.safe_load(open('config.yaml'))"
```

**No debe mostrar errores ✅**

---

### FASE 9: Verificación de Dependencias

#### [ ] Test 9.1: Dependencias Principales

```bash
# yt-dlp
yt-dlp --version

# Python packages
python -c "import yt_dlp; print('✅ yt-dlp')"
python -c "import requests; print('✅ requests')"
python -c "import rich; print('✅ rich')"
python -c "import yaml; print('✅ PyYAML')"
python -c "import colorama; print('✅ colorama')"
```

#### [ ] Test 9.2: Dependencias de Desarrollo

```bash
python -c "import pytest; print('✅ pytest')"
python -c "import pytest_cov; print('✅ pytest-cov')"
python -c "import pytest_mock; print('✅ pytest-mock')"
```

---

## ✅ Checklist Final

Antes de proceder con la refactorización, verifica:

### Funcionalidad Core
- [ ] Extracción de video individual funciona
- [ ] Procesamiento de múltiples videos funciona
- [ ] Transcripciones se guardan correctamente (plain + timestamps)
- [ ] Formato de archivos es correcto
- [ ] Manejo de errores funciona (URLs inválidas, videos sin transcripción)

### Sistemas Implementados
- [ ] Sistema de caché funciona (skip duplicados)
- [ ] Sistema de logging funciona (archivo creado, niveles correctos)
- [ ] Sistema de configuración funciona (config.yaml se lee)
- [ ] Sanitización de nombres funciona (sin caracteres peligrosos)

### CLI y UX
- [ ] Menú interactivo funciona
- [ ] Progress bars funcionan
- [ ] Mensajes coloridos se ven bien
- [ ] Comandos --help, --cache-stats, --force funcionan

### Tests
- [ ] 215+ tests unitarios pasan
- [ ] Script funcional pasa (>90%)
- [ ] Tests manuales pasan

### Código
- [ ] No hay warnings críticos al ejecutar
- [ ] Logs muestran información útil
- [ ] Caché se persiste correctamente

---

## 📊 Resultado Final

**Fecha de completación:** ___________

**Tests automáticos pasados:** _____ / _____

**Tests manuales pasados:** _____ / _____

**Funcionalidades verificadas:** _____ / _____

### ¿Listo para refactorización?

- [ ] ✅ SÍ - Todos los tests pasan, software funciona perfectamente
- [ ] ⚠️ CASI - 1-2 fallos menores (documentar cuáles)
- [ ] ❌ NO - Múltiples fallos, arreglar primero

**Notas adicionales:**
```
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

---

## 🎯 Próximos Pasos

Si todos los tests pasan:

1. **Commit el estado actual:**
   ```bash
   git add -A
   git commit -m "Pre-refactor baseline - all tests passing"
   git tag pre-refactor-baseline
   ```

2. **Crear rama para refactorización:**
   ```bash
   git checkout -b feature/issue-7-modular-refactor
   ```

3. **Proceder con Issue #7** con confianza sabiendo que tienes:
   - ✅ Tests automatizados que puedes re-ejecutar
   - ✅ Tests manuales documentados
   - ✅ Baseline de código funcional
   - ✅ Punto de rollback si algo sale mal

---

## 📝 Plantilla de Reporte

```markdown
# Reporte de Verificación Pre-Refactorización

**Fecha:** 2025-XX-XX
**Ejecutado por:** [Tu nombre]
**Duración total:** XX minutos

## Resumen
- Tests automáticos: XX/XX pasados (XX%)
- Tests manuales: XX/XX pasados (XX%)
- Funcionalidad core: ✅ / ⚠️ / ❌

## Detalles
[Pegar output del script automatizado]

## Tests Manuales
- Video individual: ✅
- Múltiples videos: ✅
- Sistema caché: ✅
- Sistema logging: ✅

## Decisión
☑ LISTO para refactorización
☐ Necesita correcciones (especificar)

## Notas
[Cualquier observación]
```

---

**IMPORTANTE:** Guarda este checklist y los resultados. Los necesitarás para verificar que la refactorización no rompió nada.
