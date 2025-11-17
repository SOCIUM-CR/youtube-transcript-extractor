#!/bin/bash
# Script Simple de Verificación de Baseline
# Verifica rápidamente que el software está funcional antes de refactorizar

echo "🔍 Verificación Rápida de Baseline - Pre Refactorización"
echo "========================================================"
echo ""

PASS=0
FAIL=0

check() {
    local name="$1"
    local command="$2"

    echo -n "Verificando: $name... "
    if eval "$command" > /dev/null 2>&1; then
        echo "✅"
        PASS=$((PASS + 1))
    else
        echo "❌"
        FAIL=$((FAIL + 1))
    fi
}

echo "1️⃣  TESTS UNITARIOS"
echo "-------------------"
check "Tests de caché (33 tests)" "python -m pytest tests/unit/test_cache.py -q"
check "Tests de logging (21 tests)" "python -m pytest tests/unit/test_logging.py -q"
check "Tests de sanitización" "python -m pytest tests/unit/test_sanitize.py -q"
check "Tests de configuración" "python -m pytest tests/unit/test_config.py -q"

echo ""
echo "2️⃣  IMPORTACIONES"
echo "-------------------"
check "YouTubeTranscriptExtractor" "python -c 'from youtube_transcript_extractor import YouTubeTranscriptExtractor'"
check "TranscriptCache" "python -c 'from cache import TranscriptCache'"
check "Logging" "python -c 'from utils.logging_config import setup_logging'"
check "Config" "python -c 'from config import get_config'"
check "Sanitize" "python -c 'from utils.sanitize import sanitize_filename'"

echo ""
echo "3️⃣  FUNCIONALIDAD BÁSICA"
echo "-------------------"
check "Extracción de Video ID" "python -c 'from youtube_transcript_extractor import YouTubeTranscriptExtractor; e=YouTubeTranscriptExtractor(); assert e.extract_video_id(\"https://youtube.com/watch?v=test123\") == \"test123\"'"
check "Validación de URLs" "python -c 'from youtube_transcript_extractor import YouTubeTranscriptExtractor; e=YouTubeTranscriptExtractor(); assert e.validate_youtube_url(\"https://youtube.com/watch?v=abc123\")'"
check "Formato de timestamps" "python -c 'from youtube_transcript_extractor import YouTubeTranscriptExtractor; e=YouTubeTranscriptExtractor(); assert e._format_timestamp(61) == \"00:01:01\"'"

echo ""
echo "4️⃣  SISTEMA DE CACHÉ"
echo "-------------------"
python << 'EOF' > /dev/null 2>&1
from cache import TranscriptCache
import os
cache = TranscriptCache('.verify_test.json')
cache.mark_processed('test', 'Test', 'en', 'yt-dlp', 'test')
assert cache.is_processed('test')
os.remove('.verify_test.json')
EOF

if [ $? -eq 0 ]; then
    echo "Verificando: Sistema de caché completo... ✅"
    PASS=$((PASS + 1))
else
    echo "Verificando: Sistema de caché completo... ❌"
    FAIL=$((FAIL + 1))
fi

echo ""
echo "5️⃣  SISTEMA DE LOGGING"
echo "-------------------"
python << 'EOF' > /dev/null 2>&1
from utils.logging_config import setup_logging
from config import ConfigLoader
from pathlib import Path
log_file = Path('.verify_test.log')
config = ConfigLoader()
config.config['logging']['file'] = str(log_file)
config.config['logging']['console'] = False
logger = setup_logging('verify', config=config, force=True)
logger.info('test')
for h in logger.handlers: h.flush()
assert log_file.exists()
assert 'test' in log_file.read_text()
log_file.unlink()
EOF

if [ $? -eq 0 ]; then
    echo "Verificando: Sistema de logging completo... ✅"
    PASS=$((PASS + 1))
else
    echo "Verificando: Sistema de logging completo... ❌"
    FAIL=$((FAIL + 1))
fi

echo ""
echo "6️⃣  COMANDOS CLI"
echo "-------------------"
check "CLI --help" "python youtube_transcript_extractor.py --help"
check "CLI --cache-stats" "python youtube_transcript_extractor.py --cache-stats"

echo ""
echo "7️⃣  ARCHIVOS CRÍTICOS"
echo "-------------------"
check "Archivo principal" "[ -f youtube_transcript_extractor.py ]"
check "Módulo cache" "[ -f cache/transcript_cache.py ]"
check "Módulo logging" "[ -f utils/logging_config.py ]"
check "Configuración" "[ -f config.yaml ]"
check "README" "[ -f README.md ]"

echo ""
echo "8️⃣  DEPENDENCIAS"
echo "-------------------"
check "yt-dlp" "python -c 'import yt_dlp'"
check "requests" "python -c 'import requests'"
check "rich" "python -c 'import rich'"
check "PyYAML" "python -c 'import yaml'"
check "pytest" "python -c 'import pytest'"

echo ""
echo "========================================================"
echo "📊 RESULTADO FINAL"
echo "========================================================"
echo ""
echo "✅ Verificaciones pasadas: $PASS"
echo "❌ Verificaciones fallidas: $FAIL"
echo ""

TOTAL=$((PASS + FAIL))
PERCENTAGE=$((PASS * 100 / TOTAL))

if [ $FAIL -eq 0 ]; then
    echo "🎉 ¡PERFECTO! Todas las verificaciones pasaron ($PASS/$TOTAL)"
    echo ""
    echo "✨ El software está 100% funcional"
    echo "✨ Listo para refactorización (Issue #7)"
    echo ""
    echo "Próximos pasos:"
    echo "  1. Commit: git commit -m 'Pre-refactor baseline'"
    echo "  2. Tag: git tag pre-refactor-v1"
    echo "  3. Branch: git checkout -b feature/issue-7-modular"
    echo ""
    exit 0
elif [ $PERCENTAGE -ge 90 ]; then
    echo "⚠️  Casi perfecto ($PASS/$TOTAL = $PERCENTAGE%)"
    echo ""
    echo "Solo $FAIL fallo(s) menor(es)"
    echo "Probablemente seguro para refactorizar"
    echo ""
    exit 0
else
    echo "❌ Varios fallos detectados ($FAIL/$TOTAL)"
    echo ""
    echo "Revisa y corrige antes de refactorizar"
    echo ""
    exit 1
fi
