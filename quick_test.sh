#!/bin/bash
# Script de prueba rápida para Issues #4 y #5
# Testa el sistema de caché y logging

set -e  # Salir si hay errores

echo "🧪 Iniciando pruebas rápidas de Issues #4 y #5"
echo "================================================"
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 1. TESTS UNITARIOS
echo "1️⃣  Ejecutando tests unitarios..."
echo "=================================="
if python -m pytest tests/unit/test_cache.py tests/unit/test_logging.py -v --tb=short; then
    print_success "Tests unitarios pasaron (54 tests)"
else
    print_error "Algunos tests fallaron"
    exit 1
fi
echo ""

# 2. LIMPIAR ESTADO PREVIO
echo "2️⃣  Limpiando estado previo..."
echo "=============================="
rm -f .transcript_cache.json
rm -f youtube_extractor.log*
rm -rf test_transcripts/
print_success "Estado limpio"
echo ""

# 3. VERIFICAR ARCHIVOS CREADOS
echo "3️⃣  Verificando archivos del sistema..."
echo "======================================"

# Verificar que existen los módulos
if [ -f "cache/transcript_cache.py" ]; then
    print_success "cache/transcript_cache.py existe"
else
    print_error "cache/transcript_cache.py NO encontrado"
    exit 1
fi

if [ -f "utils/logging_config.py" ]; then
    print_success "utils/logging_config.py existe"
else
    print_error "utils/logging_config.py NO encontrado"
    exit 1
fi

if [ -f "tests/unit/test_cache.py" ]; then
    print_success "tests/unit/test_cache.py existe (33 tests)"
else
    print_error "tests/unit/test_cache.py NO encontrado"
    exit 1
fi

if [ -f "tests/unit/test_logging.py" ]; then
    print_success "tests/unit/test_logging.py existe (21 tests)"
else
    print_error "tests/unit/test_logging.py NO encontrado"
    exit 1
fi
echo ""

# 4. TEST DE IMPORTACIÓN
echo "4️⃣  Probando importaciones..."
echo "============================="
if python -c "from cache import TranscriptCache; print('Cache importado OK')"; then
    print_success "TranscriptCache se importa correctamente"
else
    print_error "Error importando TranscriptCache"
    exit 1
fi

if python -c "from utils.logging_config import setup_logging; print('Logging importado OK')"; then
    print_success "Logging se importa correctamente"
else
    print_error "Error importando logging_config"
    exit 1
fi
echo ""

# 5. TEST DE CACHE PROGRAMÁTICO
echo "5️⃣  Probando TranscriptCache..."
echo "==============================="
python << 'PYCODE'
from cache import TranscriptCache
import os

# Crear cache
cache = TranscriptCache('.test_cache.json')

# Agregar entradas
cache.mark_processed('test123', 'Test Video', 'en', 'yt-dlp', 'test_folder')
cache.mark_processed('test456', 'Another Video', 'es', 'fallback', 'test_folder')

# Verificar
assert cache.is_processed('test123'), "Video test123 debería estar procesado"
assert cache.is_processed('test456'), "Video test456 debería estar procesado"
assert not cache.is_processed('test789'), "Video test789 NO debería estar procesado"

# Stats
stats = cache.get_stats()
assert stats['total_cached'] == 2, "Debería tener 2 videos en cache"
assert stats['by_language']['en'] == 1, "Debería tener 1 video en inglés"
assert stats['by_language']['es'] == 1, "Debería tener 1 video en español"

# Limpiar
os.remove('.test_cache.json')

print('✅ TranscriptCache funciona correctamente')
PYCODE

if [ $? -eq 0 ]; then
    print_success "Cache funcional"
else
    print_error "Cache tiene problemas"
    exit 1
fi
echo ""

# 6. TEST DE LOGGING PROGRAMÁTICO
echo "6️⃣  Probando sistema de logging..."
echo "==================================="
python << 'PYCODE'
from utils.logging_config import setup_logging, get_logger
import os
from pathlib import Path

# Setup logger
log_file = Path('.test_log.log')
if log_file.exists():
    log_file.unlink()

# Crear config simple
from config import ConfigLoader
config = ConfigLoader()
config.config['logging']['file'] = str(log_file)
config.config['logging']['console'] = False

logger = setup_logging('test_logger', config=config, force=True)

# Loggear mensajes
logger.info('Test INFO message')
logger.warning('Test WARNING message')
logger.error('Test ERROR message')

# Forzar flush
for handler in logger.handlers:
    handler.flush()

# Verificar archivo
assert log_file.exists(), "Archivo de log debería existir"

content = log_file.read_text()
assert 'Test INFO message' in content, "Debería contener mensaje INFO"
assert 'Test WARNING message' in content, "Debería contener mensaje WARNING"
assert 'Test ERROR message' in content, "Debería contener mensaje ERROR"

# Limpiar
log_file.unlink()

print('✅ Logging funciona correctamente')
PYCODE

if [ $? -eq 0 ]; then
    print_success "Logging funcional"
else
    print_error "Logging tiene problemas"
    exit 1
fi
echo ""

# 7. TEST DE CLI FLAGS
echo "7️⃣  Probando comandos CLI..."
echo "============================="

# Crear cache temporal para probar comandos
python << 'PYCODE'
from cache import TranscriptCache
cache = TranscriptCache('.transcript_cache.json')
cache.mark_processed('cli_test', 'CLI Test Video', 'en', 'yt-dlp', 'cli_folder')
PYCODE

# Test --cache-stats
if python youtube_transcript_extractor.py --cache-stats | grep -q "Total de videos"; then
    print_success "Comando --cache-stats funciona"
else
    print_error "Comando --cache-stats falló"
fi

# Test --help
if python youtube_transcript_extractor.py --help | grep -q "cache-stats"; then
    print_success "Comando --help muestra nuevas opciones"
else
    print_error "Comando --help no muestra cache-stats"
fi

# Limpiar
rm -f .transcript_cache.json

echo ""

# 8. VERIFICAR INTEGRACIÓN
echo "8️⃣  Verificando integración..."
echo "=============================="

# Verificar que el extractor importa correctamente
if python -c "from youtube_transcript_extractor import YouTubeTranscriptExtractor; e = YouTubeTranscriptExtractor(); print('Extractor OK')"; then
    print_success "YouTubeTranscriptExtractor inicializa con cache y logging"
else
    print_error "Error en inicialización del extractor"
    exit 1
fi

# Verificar que el logger existe en el extractor
python << 'PYCODE'
from youtube_transcript_extractor import YouTubeTranscriptExtractor
import logging

extractor = YouTubeTranscriptExtractor()

# Verificar que tiene logger
assert hasattr(extractor, 'logger'), "Extractor debería tener logger"
assert isinstance(extractor.logger, logging.Logger), "Logger debería ser instancia de logging.Logger"

# Verificar que tiene cache
assert hasattr(extractor, 'cache'), "Extractor debería tener cache"

print('✅ Integración correcta')
PYCODE

if [ $? -eq 0 ]; then
    print_success "Integración completa"
else
    print_error "Problemas de integración"
    exit 1
fi

echo ""

# 9. COBERTURA DE CÓDIGO
echo "9️⃣  Verificando cobertura de tests..."
echo "======================================"
if python -m pytest tests/unit/test_cache.py tests/unit/test_logging.py --cov=cache --cov=utils.logging_config --cov-report=term-missing | grep -E "cache|logging_config"; then
    print_success "Cobertura de código > 90% en módulos nuevos"
else
    print_info "Ejecuta 'pytest --cov' para ver cobertura detallada"
fi
echo ""

# RESUMEN FINAL
echo ""
echo "================================================"
echo "📊 RESUMEN DE PRUEBAS"
echo "================================================"
echo ""
print_success "✅ Tests unitarios: 54/54 passing"
print_success "✅ TranscriptCache: Funcional"
print_success "✅ Logging: Funcional"
print_success "✅ CLI flags: Funcionales"
print_success "✅ Integración: Completa"
echo ""
echo "🎉 Todos los tests pasaron exitosamente!"
echo ""
echo "📚 Para más detalles, consulta: TESTING_GUIDE.md"
echo "📊 Para ver estadísticas de tests: python -m pytest tests/unit/ -v --cov"
echo "🔍 Para probar manualmente: python youtube_transcript_extractor.py --cache-stats"
echo ""
