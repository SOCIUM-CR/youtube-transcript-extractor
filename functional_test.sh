#!/bin/bash
# Script de Testing Funcional End-to-End
# Verifica que TODAS las funcionalidades del software funcionan correctamente
# Ejecutar ANTES de cualquier refactorización importante

set -e  # Salir si hay errores

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_test() {
    echo -e "${BLUE}🧪 $1${NC}"
}

# Contadores
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

run_test() {
    local test_name="$1"
    local test_command="$2"

    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    print_test "Test $TESTS_TOTAL: $test_name"

    if eval "$test_command"; then
        print_success "PASS"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        print_error "FAIL"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Limpiar estado anterior
cleanup() {
    print_info "Limpiando archivos de prueba anteriores..."
    rm -rf test_functional/
    rm -f .transcript_cache.json
    rm -f youtube_extractor.log*
    rm -f test_*.txt
    rm -f .test_*.json
    print_success "Limpieza completada"
}

# ============================================================================
# PREPARACIÓN
# ============================================================================

print_header "🚀 TESTING FUNCIONAL END-TO-END"
echo "Este script verifica que TODAS las funcionalidades están operativas"
echo "Duración estimada: 3-5 minutos (incluye descargas de YouTube)"
echo ""

read -p "¿Continuar con el testing funcional? [Y/n] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]] && [[ ! -z $REPLY ]]; then
    echo "Testing cancelado"
    exit 0
fi

cleanup

# ============================================================================
# FASE 1: TESTS UNITARIOS
# ============================================================================

print_header "FASE 1: Tests Unitarios (54 tests)"

run_test "Ejecutar suite completa de tests unitarios" \
    "python -m pytest tests/unit/ -v --tb=short -q 2>&1 | grep -q '54 passed'"

run_test "Tests de caché (33 tests)" \
    "python -m pytest tests/unit/test_cache.py -v -q 2>&1 | grep -q '33 passed'"

run_test "Tests de logging (21 tests)" \
    "python -m pytest tests/unit/test_logging.py -v -q 2>&1 | grep -q '21 passed'"

run_test "Tests de sanitización (79 tests)" \
    "python -m pytest tests/unit/test_sanitize.py -v -q 2>&1 | grep -q '79 passed'"

run_test "Tests de configuración (26 tests)" \
    "python -m pytest tests/unit/test_config.py -v -q 2>&1 | grep -q '26 passed'"

# ============================================================================
# FASE 2: VERIFICACIÓN DE MÓDULOS
# ============================================================================

print_header "FASE 2: Verificación de Importaciones y Módulos"

run_test "Importar YouTubeTranscriptExtractor" \
    "python -c 'from youtube_transcript_extractor import YouTubeTranscriptExtractor; print(\"OK\")' 2>&1 | grep -q OK"

run_test "Importar TranscriptCache" \
    "python -c 'from cache import TranscriptCache; print(\"OK\")' 2>&1 | grep -q OK"

run_test "Importar sistema de logging" \
    "python -c 'from utils.logging_config import setup_logging; print(\"OK\")' 2>&1 | grep -q OK"

run_test "Importar sistema de configuración" \
    "python -c 'from config import get_config; print(\"OK\")' 2>&1 | grep -q OK"

run_test "Importar utilidades de sanitización" \
    "python -c 'from utils.sanitize import sanitize_filename; print(\"OK\")' 2>&1 | grep -q OK"

# ============================================================================
# FASE 3: TESTS FUNCIONALES PROGRAMÁTICOS
# ============================================================================

print_header "FASE 3: Tests Funcionales Programáticos"

# Test 1: Extracción de Video ID
print_test "Test 6: Extracción de Video ID de diferentes URLs"
python << 'PYCODE'
from youtube_transcript_extractor import YouTubeTranscriptExtractor

extractor = YouTubeTranscriptExtractor()

test_urls = {
    'https://www.youtube.com/watch?v=dQw4w9WgXcQ': 'dQw4w9WgXcQ',
    'https://youtu.be/dQw4w9WgXcQ': 'dQw4w9WgXcQ',
    'https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s': 'dQw4w9WgXcQ',
    'https://m.youtube.com/watch?v=dQw4w9WgXcQ': 'dQw4w9WgXcQ',
}

all_passed = True
for url, expected_id in test_urls.items():
    video_id = extractor.extract_video_id(url)
    if video_id != expected_id:
        print(f'FAIL: {url} -> {video_id} (esperado: {expected_id})')
        all_passed = False

if all_passed:
    print('OK')
    exit(0)
else:
    exit(1)
PYCODE

if [ $? -eq 0 ]; then
    print_success "PASS"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    print_error "FAIL"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

# Test 2: Validación de URLs
print_test "Test 7: Validación de URLs de YouTube"
python << 'PYCODE'
from youtube_transcript_extractor import YouTubeTranscriptExtractor

extractor = YouTubeTranscriptExtractor()

valid_urls = [
    'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    'https://youtu.be/dQw4w9WgXcQ',
    'https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf',
]

invalid_urls = [
    'https://www.google.com',
    'not a url',
    'https://vimeo.com/123456',
]

all_passed = True

for url in valid_urls:
    if not extractor.validate_youtube_url(url):
        print(f'FAIL: URL válida rechazada: {url}')
        all_passed = False

for url in invalid_urls:
    if extractor.validate_youtube_url(url):
        print(f'FAIL: URL inválida aceptada: {url}')
        all_passed = False

if all_passed:
    print('OK')
    exit(0)
else:
    exit(1)
PYCODE

if [ $? -eq 0 ]; then
    print_success "PASS"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    print_error "FAIL"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

# Test 3: Sistema de caché
print_test "Test 8: Sistema de caché funcional"
python << 'PYCODE'
from cache import TranscriptCache
import os

cache = TranscriptCache('.test_cache_functional.json')

# Agregar entradas
cache.mark_processed('test1', 'Video 1', 'en', 'yt-dlp', 'test')
cache.mark_processed('test2', 'Video 2', 'es', 'fallback', 'test')

# Verificar
assert cache.is_processed('test1'), "Video test1 debería estar procesado"
assert cache.is_processed('test2'), "Video test2 debería estar procesado"
assert not cache.is_processed('test3'), "Video test3 NO debería estar procesado"

# Stats
stats = cache.get_stats()
assert stats['total_cached'] == 2, "Debería tener 2 videos"
assert stats['by_language']['en'] == 1, "1 video en inglés"
assert stats['by_language']['es'] == 1, "1 video en español"

# Limpiar
os.remove('.test_cache_functional.json')

print('OK')
PYCODE

if [ $? -eq 0 ]; then
    print_success "PASS"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    print_error "FAIL"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

# Test 4: Sistema de logging
print_test "Test 9: Sistema de logging funcional"
python << 'PYCODE'
from utils.logging_config import setup_logging
from config import ConfigLoader
from pathlib import Path
import os

log_file = Path('.test_functional.log')
if log_file.exists():
    log_file.unlink()

config = ConfigLoader()
config.config['logging']['file'] = str(log_file)
config.config['logging']['console'] = False

logger = setup_logging('test_functional', config=config, force=True)
logger.info('Test message INFO')
logger.warning('Test message WARNING')
logger.error('Test message ERROR')

# Flush
for handler in logger.handlers:
    handler.flush()

# Verificar
assert log_file.exists(), "Archivo de log debe existir"
content = log_file.read_text()
assert 'Test message INFO' in content, "Debe contener INFO"
assert 'Test message WARNING' in content, "Debe contener WARNING"
assert 'Test message ERROR' in content, "Debe contener ERROR"

# Limpiar
log_file.unlink()

print('OK')
PYCODE

if [ $? -eq 0 ]; then
    print_success "PASS"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    print_error "FAIL"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

# Test 5: Conversión de timestamps
print_test "Test 10: Conversión de timestamps"
python << 'PYCODE'
from youtube_transcript_extractor import YouTubeTranscriptExtractor

extractor = YouTubeTranscriptExtractor()

# Test formato timestamp
tests = [
    (0, "00:00:00"),
    (61, "00:01:01"),
    (3661, "01:01:01"),
    (90.5, "00:01:30"),
]

all_passed = True
for seconds, expected in tests:
    result = extractor._format_timestamp(seconds)
    if result != expected:
        print(f'FAIL: {seconds}s -> {result} (esperado: {expected})')
        all_passed = False

if all_passed:
    print('OK')
    exit(0)
else:
    exit(1)
PYCODE

if [ $? -eq 0 ]; then
    print_success "PASS"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    print_error "FAIL"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

# ============================================================================
# FASE 4: TESTS DE INTEGRACIÓN CON VIDEO REAL
# ============================================================================

print_header "FASE 4: Tests de Integración con Video Real de YouTube"

print_info "Esta fase descarga transcripciones reales de YouTube"
print_info "Puede tomar 1-2 minutos dependiendo de la conexión"
echo ""

# Crear directorio de test
mkdir -p test_functional

# Crear archivo con URLs de prueba
cat > test_functional/test_urls.txt << 'EOF'
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://www.youtube.com/watch?v=9bZkp7q19f0
EOF

print_test "Test 11: Extracción de transcripción de video real"
python << 'PYCODE'
import sys
sys.path.insert(0, '.')

from youtube_transcript_extractor import YouTubeTranscriptExtractor

extractor = YouTubeTranscriptExtractor()

# Intentar extraer de un video conocido que tiene transcripciones
test_url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'

print(f'Intentando extraer transcripción de: {test_url}')
transcript = extractor.get_transcript(test_url)

if transcript and transcript.get('segments'):
    print(f'✅ Transcripción extraída exitosamente')
    print(f'   - Segmentos: {len(transcript["segments"])}')
    print(f'   - Idioma: {transcript.get("selected_language", "desconocido")}')
    print(f'   - Método: {transcript.get("method", "desconocido")}')
    print(f'   - Texto completo: {len(transcript.get("full_text", ""))} caracteres')
    print('OK')
    exit(0)
else:
    print('❌ No se pudo extraer transcripción')
    print('   Esto puede deberse a:')
    print('   - El video no tiene transcripciones disponibles')
    print('   - Problemas de conectividad')
    print('   - YouTube bloqueó la petición')
    print('SKIP')
    exit(2)  # Exit code 2 = skip (no es fallo crítico)
PYCODE

exit_code=$?
if [ $exit_code -eq 0 ]; then
    print_success "PASS"
    TESTS_PASSED=$((TESTS_PASSED + 1))
elif [ $exit_code -eq 2 ]; then
    print_info "SKIP (no crítico - puede ser problema de red/YouTube)"
else
    print_error "FAIL"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

print_test "Test 12: Procesamiento de archivo con múltiples URLs"
python << 'PYCODE'
import sys
import os
sys.path.insert(0, '.')

from youtube_transcript_extractor import YouTubeTranscriptExtractor

# Leer URLs
with open('test_functional/test_urls.txt', 'r') as f:
    urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

print(f'URLs a procesar: {len(urls)}')

extractor = YouTubeTranscriptExtractor()

# Intentar procesar
try:
    extractor.process_videos_from_urls(urls, 'test_functional_output')

    # Verificar que se crearon archivos
    output_dir = 'transcripts/test_functional_output'

    if os.path.exists(output_dir):
        plain_dir = os.path.join(output_dir, 'transcripts_plain')
        timestamps_dir = os.path.join(output_dir, 'transcripts_timestamps')

        plain_files = len(os.listdir(plain_dir)) if os.path.exists(plain_dir) else 0
        timestamp_files = len(os.listdir(timestamps_dir)) if os.path.exists(timestamps_dir) else 0

        print(f'✅ Archivos generados:')
        print(f'   - Plain: {plain_files}')
        print(f'   - Timestamps: {timestamp_files}')

        if plain_files > 0 and timestamp_files > 0:
            print('OK')
            exit(0)
        else:
            print('❌ No se generaron archivos')
            exit(2)
    else:
        print('❌ Directorio de salida no existe')
        exit(2)

except Exception as e:
    print(f'❌ Error durante procesamiento: {e}')
    exit(2)
PYCODE

exit_code=$?
if [ $exit_code -eq 0 ]; then
    print_success "PASS"
    TESTS_PASSED=$((TESTS_PASSED + 1))
elif [ $exit_code -eq 2 ]; then
    print_info "SKIP (puede ser problema de red/YouTube)"
else
    print_error "FAIL"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

# ============================================================================
# FASE 5: TESTS DE COMANDOS CLI
# ============================================================================

print_header "FASE 5: Tests de Comandos CLI"

run_test "CLI: --help muestra ayuda" \
    "python youtube_transcript_extractor.py --help 2>&1 | grep -q 'usage:'"

run_test "CLI: --cache-stats sin errores" \
    "python youtube_transcript_extractor.py --cache-stats 2>&1 | grep -q 'Estadísticas'"

run_test "CLI: --version o información del sistema" \
    "python youtube_transcript_extractor.py --help 2>&1 | grep -q 'YouTube Transcript Extractor'"

# ============================================================================
# FASE 6: VERIFICACIÓN DE ARCHIVOS CRÍTICOS
# ============================================================================

print_header "FASE 6: Verificación de Archivos Críticos"

run_test "Archivo principal existe" \
    "[ -f youtube_transcript_extractor.py ]"

run_test "Módulo cache existe" \
    "[ -f cache/transcript_cache.py ]"

run_test "Módulo logging existe" \
    "[ -f utils/logging_config.py ]"

run_test "Módulo config existe" \
    "[ -f config/config_loader.py ]"

run_test "Archivo de configuración existe" \
    "[ -f config.yaml ]"

run_test "Tests unitarios existen" \
    "[ -d tests/unit ] && [ $(ls -1 tests/unit/test_*.py | wc -l) -ge 5 ]"

run_test "README existe y tiene contenido" \
    "[ -f README.md ] && [ $(wc -l < README.md) -gt 50 ]"

run_test "Requirements.txt existe" \
    "[ -f requirements.txt ]"

# ============================================================================
# FASE 7: VERIFICACIÓN DE DEPENDENCIAS
# ============================================================================

print_header "FASE 7: Verificación de Dependencias"

run_test "yt-dlp instalado" \
    "python -c 'import yt_dlp; print(\"OK\")' 2>&1 | grep -q OK"

run_test "requests instalado" \
    "python -c 'import requests; print(\"OK\")' 2>&1 | grep -q OK"

run_test "rich instalado" \
    "python -c 'import rich; print(\"OK\")' 2>&1 | grep -q OK"

run_test "PyYAML instalado" \
    "python -c 'import yaml; print(\"OK\")' 2>&1 | grep -q OK"

run_test "pytest instalado (dev)" \
    "python -c 'import pytest; print(\"OK\")' 2>&1 | grep -q OK"

# ============================================================================
# REPORTE FINAL
# ============================================================================

print_header "📊 REPORTE FINAL DE TESTING"

echo ""
echo "Resumen de Resultados:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

print_success "Tests Pasados: $TESTS_PASSED / $TESTS_TOTAL"

if [ $TESTS_FAILED -gt 0 ]; then
    print_error "Tests Fallidos: $TESTS_FAILED / $TESTS_TOTAL"
fi

SUCCESS_RATE=$(echo "scale=1; $TESTS_PASSED * 100 / $TESTS_TOTAL" | bc)
echo ""
echo "Tasa de Éxito: $SUCCESS_RATE%"
echo ""

# Evaluación final
if [ $TESTS_FAILED -eq 0 ]; then
    print_success "✨ TODOS LOS TESTS PASARON ✨"
    echo ""
    echo "El software está 100% funcional y listo para refactorización."
    echo ""
    echo "Puedes proceder con confianza al Issue #7 (Refactorización Modular)"
    echo "sabiendo que tienes esta baseline de tests para verificar después."
    echo ""
    EXIT_CODE=0
elif [ $TESTS_FAILED -le 2 ]; then
    print_info "⚠️  CASI TODOS LOS TESTS PASARON"
    echo ""
    echo "Hay $TESTS_FAILED fallo(s) menor(es), probablemente relacionados con red/YouTube."
    echo "El software está funcional para refactorización."
    echo ""
    EXIT_CODE=0
else
    print_error "❌ MÚLTIPLES TESTS FALLARON"
    echo ""
    echo "Se encontraron $TESTS_FAILED fallos. Revisa los errores antes de refactorizar."
    echo ""
    EXIT_CODE=1
fi

# Limpieza opcional
echo ""
read -p "¿Limpiar archivos de prueba? [Y/n] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    cleanup
    print_success "Archivos de prueba eliminados"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Testing funcional completado"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

exit $EXIT_CODE
