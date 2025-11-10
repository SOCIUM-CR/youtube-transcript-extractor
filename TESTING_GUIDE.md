# Guía de Testing - Issues #4 y #5

Esta guía te muestra cómo testear los sistemas de caché y logging implementados.

## 1. Tests Unitarios Automatizados

### Ejecutar todos los tests
```bash
# Todos los tests
python -m pytest tests/unit/ -v

# Solo tests de caché (33 tests)
python -m pytest tests/unit/test_cache.py -v

# Solo tests de logging (21 tests)
python -m pytest tests/unit/test_logging.py -v

# Con reporte de cobertura
python -m pytest tests/unit/ -v --cov
```

**Resultado esperado:** 215/217 tests passing (99.1%)

---

## 2. Testing del Sistema de Caché (Issue #4)

### Test 1: Verificar que el caché funciona

```bash
# 1. Crear archivo de prueba con URLs
cat > test_urls.txt << 'EOF'
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://www.youtube.com/watch?v=9bZkp7q19f0
EOF

# 2. Primera ejecución (debe procesar ambos videos)
python youtube_transcript_extractor.py

# Selecciona opción 2 (Lista de URLs desde archivo)
# Archivo: test_urls.txt
# Carpeta: test_cache

# 3. Segunda ejecución (debe omitir videos ya procesados)
python youtube_transcript_extractor.py

# Selecciona opción 2 nuevamente
# Deberías ver: "Videos ya procesados (omitidos)"
```

**Resultado esperado:**
- Primera ejecución: Procesa 2 videos
- Segunda ejecución: Omite 2 videos (mensaje en amarillo)
- Se crea archivo `.transcript_cache.json`

### Test 2: Ver estadísticas del caché

```bash
python youtube_transcript_extractor.py --cache-stats
```

**Resultado esperado:**
```
📊 Estadísticas de Caché

┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Métrica            ┃ Valor ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Total de videos    │ 2     │
│ Entrada más antigua│ 2025... │
│ Entrada más reciente│ 2025... │
└────────────────────┴───────┘

Por idioma:
  • en: 2

Por método de extracción:
  • yt-dlp: 2

Por carpeta:
  • test_cache: 2
```

### Test 3: Forzar reprocesamiento

```bash
python youtube_transcript_extractor.py --force

# Selecciona opción 2 con el mismo archivo
# Deberías ver: "Modo FORCE activado: se reprocesarán todos los videos"
```

**Resultado esperado:**
- Reprocesa todos los videos ignorando el caché
- Actualiza las fechas en el caché

### Test 4: Limpiar caché

```bash
python youtube_transcript_extractor.py --clear-cache
```

**Resultado esperado:**
```
¿Estás seguro de que deseas limpiar todo el caché? [y/n]: y
✅ Caché limpiado exitosamente
```

### Test 5: Verificar archivo de caché manualmente

```bash
# Ver contenido del caché
cat .transcript_cache.json | python -m json.tool

# Ver estadísticas
ls -lh .transcript_cache.json
```

**Resultado esperado:**
```json
{
  "dQw4w9WgXcQ": {
    "video_id": "dQw4w9WgXcQ",
    "title": "Rick Astley - Never Gonna Give You Up",
    "language": "en",
    "method": "yt-dlp",
    "folder": "test_cache",
    "processed_at": "2025-11-10T...",
    "cache_version": "1.0"
  }
}
```

---

## 3. Testing del Sistema de Logging (Issue #5)

### Test 1: Verificar que se crean los logs

```bash
# 1. Ejecutar el extractor
python youtube_transcript_extractor.py

# 2. Procesar al menos 1 video

# 3. Verificar archivo de log
ls -lh youtube_extractor.log
```

**Resultado esperado:**
- Archivo `youtube_extractor.log` creado
- Tamaño > 0 bytes

### Test 2: Revisar contenido de logs

```bash
# Ver últimas 20 líneas
tail -20 youtube_extractor.log

# Buscar mensajes de inicialización
grep "initialized" youtube_extractor.log

# Buscar errores
grep "ERROR" youtube_extractor.log

# Buscar videos procesados
grep "procesado exitosamente" youtube_extractor.log
```

**Resultado esperado:**
```
2025-11-10 10:30:15 - youtube_extractor - INFO - YouTubeTranscriptExtractor initialized
2025-11-10 10:30:15 - youtube_extractor - INFO - Cache loaded with 0 videos
2025-11-10 10:30:20 - youtube_extractor - INFO - Iniciando extracción de transcripción para video: dQw4w9WgXcQ
2025-11-10 10:30:25 - youtube_extractor - INFO - Transcripción obtenida con yt-dlp para dQw4w9WgXcQ
2025-11-10 10:30:26 - youtube_extractor - INFO - Video procesado exitosamente: dQw4w9WgXcQ
```

### Test 3: Verificar rotación de logs

```bash
# Generar muchos logs (modificar config.yaml primero)
# Cambiar max_size_mb: 0.001 (1 KB para pruebas)

# Procesar varios videos
# Deberías ver archivos: youtube_extractor.log.1, .2, .3
ls -lh youtube_extractor.log*
```

### Test 4: Verificar niveles de logging

```bash
# Editar config.yaml
# Cambiar: level: "DEBUG"

# Ejecutar extractor
python youtube_transcript_extractor.py

# Ver logs con nivel DEBUG
grep "DEBUG" youtube_extractor.log
```

**Resultado esperado:**
- Más mensajes de depuración
- Información detallada de configuración

### Test 5: Logs con colores en consola

```bash
# Ejecutar y observar la consola
python youtube_transcript_extractor.py

# Deberías ver niveles con colores:
# - INFO en verde
# - WARNING en amarillo
# - ERROR en rojo
```

---

## 4. Testing de Integración

### Test Completo: Flujo de Trabajo Real

```bash
# 1. Limpiar todo
rm -rf .transcript_cache.json youtube_extractor.log transcripts/

# 2. Crear lista de videos
cat > production_test.txt << 'EOF'
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://www.youtube.com/watch?v=9bZkp7q19f0
https://www.youtube.com/watch?v=kJQP7kiw5Fk
EOF

# 3. Primera ejecución
python youtube_transcript_extractor.py
# Procesar los 3 videos

# 4. Verificar resultados
echo "=== Archivos generados ==="
find transcripts/ -type f | wc -l  # Debe mostrar 6 archivos (3 plain + 3 timestamps)

echo "=== Caché ==="
cat .transcript_cache.json | python -m json.tool | grep "video_id"

echo "=== Logs ==="
grep "procesado exitosamente" youtube_extractor.log | wc -l  # Debe mostrar 3

# 5. Segunda ejecución (test de caché)
python youtube_transcript_extractor.py
# Procesar mismo archivo - debe omitir los 3

# 6. Estadísticas
python youtube_transcript_extractor.py --cache-stats

# 7. Agregar 1 video nuevo
echo "https://www.youtube.com/watch?v=jNQXAC9IVRw" >> production_test.txt

# 8. Tercera ejecución
python youtube_transcript_extractor.py
# Debe omitir 3 y procesar solo 1 nuevo
```

**Resultado esperado:**
```
✅ Primera ejecución: 3 videos procesados
✅ Segunda ejecución: 3 videos omitidos
✅ Tercera ejecución: 3 omitidos, 1 procesado
✅ Caché: 4 entradas
✅ Logs: 4 procesados exitosamente
✅ Archivos: 8 transcripciones (4x2)
```

---

## 5. Testing de Configuración

### Test: Modificar configuración

```bash
# Editar config.yaml
cat > config.yaml << 'EOF'
processing:
  cache:
    enabled: true
    file: "mi_cache_personalizado.json"

logging:
  level: "WARNING"
  file: "logs/mi_app.log"
  max_size_mb: 5
  backup_count: 5
  console: true
EOF

# Ejecutar
python youtube_transcript_extractor.py

# Verificar archivos personalizados
ls -lh mi_cache_personalizado.json
ls -lh logs/mi_app.log
```

---

## 6. Testing de Errores

### Test: Caché con video que falla

```bash
# Crear archivo con URL inválida
cat > error_test.txt << 'EOF'
https://www.youtube.com/watch?v=INVALID123
https://www.youtube.com/watch?v=dQw4w9WgXcQ
EOF

# Ejecutar
python youtube_transcript_extractor.py

# Verificar logs de error
grep "ERROR" youtube_extractor.log
grep "WARNING" youtube_extractor.log

# El video válido debe estar en caché, el inválido no
cat .transcript_cache.json | python -m json.tool
```

---

## 7. Checklist de Verificación

### Sistema de Caché ✓
- [ ] Archivo `.transcript_cache.json` se crea automáticamente
- [ ] Videos procesados no se repiten en siguientes ejecuciones
- [ ] `--cache-stats` muestra estadísticas correctas
- [ ] `--force` reprocesa videos
- [ ] `--clear-cache` limpia el caché
- [ ] Caché persiste entre ejecuciones

### Sistema de Logging ✓
- [ ] Archivo `youtube_extractor.log` se crea
- [ ] Logs contienen timestamps
- [ ] Logs contienen niveles (INFO, WARNING, ERROR)
- [ ] Logs muestran inicialización
- [ ] Logs muestran videos procesados
- [ ] Logs muestran errores con stack traces
- [ ] Consola muestra logs con colores
- [ ] Rotación funciona cuando alcanza tamaño máximo

### Tests Unitarios ✓
- [ ] 33 tests de caché pasan
- [ ] 21 tests de logging pasan
- [ ] 215/217 tests totales pasan
- [ ] Cobertura > 30%

---

## 8. Comandos Rápidos de Verificación

```bash
# Test completo automatizado
python -m pytest tests/unit/ -v --cov && \
python youtube_transcript_extractor.py --cache-stats && \
ls -lh .transcript_cache.json youtube_extractor.log

# Limpiar todo después de tests
rm -rf .transcript_cache.json youtube_extractor.log* transcripts/ test_urls.txt
```

---

## 9. Solución de Problemas

### El caché no funciona
```bash
# Verificar configuración
grep -A 3 "cache:" config.yaml

# Verificar permisos
ls -la .transcript_cache.json
```

### Los logs no se generan
```bash
# Verificar configuración
grep -A 5 "logging:" config.yaml

# Verificar permisos del directorio
mkdir -p logs && chmod 755 logs
```

### Tests fallan
```bash
# Reinstalar dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Limpiar caché de pytest
rm -rf .pytest_cache

# Ejecutar con verbose
python -m pytest tests/unit/ -vv --tb=long
```

---

## Resultados Esperados - Resumen

✅ **Tests Unitarios:** 215/217 passing
✅ **Caché:** Videos no se reprocesan
✅ **Logging:** Archivos de log con información detallada
✅ **CLI:** Comandos --cache-stats, --force, --clear-cache funcionan
✅ **Configuración:** config.yaml controla el comportamiento
✅ **Persistencia:** Caché y logs sobreviven entre ejecuciones

---

**Fecha:** 2025-11-10
**Issues:** #4 (Caché) y #5 (Logging)
**Tests:** 54 nuevos tests añadidos
