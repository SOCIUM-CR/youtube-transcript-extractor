# 🎥 YouTube Transcript Extractor

**Una herramienta completa para extraer y organizar transcripciones de videos de YouTube con interfaz interactiva y detección automática de idiomas.**

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Stable-brightgreen.svg)](https://github.com)

---

## ✨ Características Principales

- 🎯 **Interfaz interactiva** con menús visuales y colores
- 🧠 **Detección automática de idiomas** del video original
- 📹 **Extracción de videos individuales** con preview y validación
- 📋 **Procesamiento por lotes** desde archivos de URLs
- 📂 **Soporte completo para playlists** de YouTube
- 🔍 **Búsqueda automática** de URLs en código HTML
- ⏱️ **Barras de progreso** en tiempo real
- 📁 **Organización automática** en carpetas estructuradas
- ❌ **Manejo inteligente de errores** con mensajes amigables

## 🚀 Instalación Rápida

### 📋 **Guías Específicas por Sistema**
- 🍎 **macOS/Linux**: Ver [INSTALACION_RAPIDA.md](INSTALACION_RAPIDA.md)
- 🪟 **Windows**: Ver [INSTALACION_WINDOWS.md](INSTALACION_WINDOWS.md)

### Opción 1: Instalación Automática (Recomendada)
```bash
git clone https://github.com/tu-usuario/youtube-transcript-extractor.git
cd youtube-transcript-extractor

# El instalador detecta automáticamente tu sistema operativo
python3 install.py  # macOS/Linux
python install.py   # Windows
```

**¿Qué hace el instalador automáticamente?**
- ✅ **Detecta tu sistema operativo** (Windows/macOS/Linux)
- ✅ **Verifica compatibilidad** de Python (3.6+)
- ✅ **Instala todas las dependencias** automáticamente
- ✅ **Crea estructura de directorios** (`transcripts/`)
- ✅ **Genera archivos de ejemplo** listos para usar
- ✅ **Verifica que yt-dlp funcione** correctamente
- ✅ **Muestra comandos específicos** para tu sistema

### Opción 2: Instalación Manual
```bash
git clone https://github.com/tu-usuario/youtube-transcript-extractor.git
cd youtube-transcript-extractor

# Crear entorno virtual (recomendado)
python3 -m venv venv          # macOS/Linux
# python -m venv venv         # Windows

# Activar entorno virtual
source venv/bin/activate      # macOS/Linux
# venv\Scripts\activate       # Windows

# Instalar dependencias
pip install -r requirements.txt
```

## 🎮 Uso de la Aplicación

### 🚀 Inicio Rápido
```bash
# Paso 1: Instalar dependencias (solo la primera vez)
python3 install.py  # macOS/Linux
# python install.py   # Windows

# Paso 2: Activar entorno virtual (IMPORTANTE)
source venv/bin/activate      # macOS/Linux
# venv\Scripts\activate       # Windows

# Paso 3: Iniciar la aplicación
python3 start.py    # macOS/Linux  
# python start.py     # Windows
```

### 🎯 **Prueba Inmediata (Para Principiantes)**
```bash
# ¡IMPORTANTE! Activa el entorno virtual primero:
source venv/bin/activate      # macOS/Linux
# venv\Scripts\activate       # Windows

# Luego inicia la aplicación:
python3 start.py              # macOS/Linux
# python start.py             # Windows

# → Selecciona opción 2 (Lista de URLs)
# → Archivo: test_urls.txt
# → ¡Verás el sistema funcionando!
```

### 🎯 Interfaz Principal

Al iniciar verás un menú interactivo elegante:

```
🎥 YouTube Transcript Extractor
═══════════════════════════════════

🚀 ¿Qué deseas hacer?
┏━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ # ┃ Opción                   ┃ Descripción                             ┃
┡━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 1 │ 🎥 Video individual      │ Extraer transcripción de un solo video  │
│ 2 │ 📋 Lista de URLs         │ Procesar URLs desde archivo             │
│ 3 │ 📂 Playlist de YouTube   │ Extraer todos los videos de una playlist│
│ 4 │ 🔍 Buscar en código HTML │ Encontrar URLs de YouTube en código     │
│ 5 │ ❌ Salir                 │ Cerrar la aplicación                    │
└───┴──────────────────────────┴─────────────────────────────────────────┘

👉 Selecciona una opción [1/2/3/4/5] (1): 
```

## 📝 Guía Detallada por Opción

### 1️⃣ **Video Individual**
**Ideal para:** Extraer la transcripción de un solo video

**Pasos:**
1. Selecciona opción `1`
2. Pega la URL del video de YouTube
3. El sistema detecta automáticamente el idioma original
4. Confirma si quieres proceder
5. ¡Listo! Los archivos se guardan automáticamente

### 2️⃣ **Lista de URLs**
**Ideal para:** Procesar múltiples videos desde un archivo

**Preparación:**
1. **Usa el archivo de ejemplo** (creado automáticamente): `video_urls_ejemplo.txt`
2. **Edita el archivo ejemplo**:
   ```bash
   # Abre el archivo
   nano video_urls_ejemplo.txt  # o cualquier editor
   
   # Descomenta y reemplaza las URLs de ejemplo:
   https://www.youtube.com/watch?v=tu_video_real_1
   https://www.youtube.com/watch?v=tu_video_real_2
   ```
3. **O crea tu propio archivo** (ej: `mis_videos.txt`) con una URL por línea

### 3️⃣ **Playlist Completa**
**Ideal para:** Extraer todos los videos de una playlist

**Pasos:**
1. Selecciona opción `3`
2. Pega la URL de la playlist
3. El sistema extrae automáticamente todas las URLs
4. Confirma el procesamiento

### 4️⃣ **Buscar en Código HTML**
**Ideal para:** Encontrar URLs de YouTube en código fuente

**Preparación:**
1. **Usa el archivo de ejemplo** (creado automáticamente): `codigo_fuente_ejemplo.txt`
2. **Copia y edita el archivo**:
   ```bash
   # Crea tu archivo de trabajo
   cp codigo_fuente_ejemplo.txt codigo_fuente.txt
   
   # Edita y pega tu HTML real
   nano codigo_fuente.txt
   ```
3. **Pega el código HTML** que contenga videos de YouTube
4. El sistema busca automáticamente URLs de YouTube

## 🧠 Detección Inteligente de Idiomas

El sistema detecta automáticamente el idioma original de cada video y descarga la transcripción en ese idioma:

- **Videos en inglés** → Transcripción en inglés
- **Videos en español** → Transcripción en español  
- **Otros idiomas** → Transcripción traducida al inglés

```
🌐 Idioma detectado: en
✅ Seleccionado idioma original: en
📝 Idioma seleccionado: en
```

## 📁 Archivos de Ejemplo (Creados Automáticamente)

El instalador crea archivos de ejemplo listos para usar:

### 📄 **Archivos de Plantilla**
```
video_urls_ejemplo.txt          # Plantilla para listas de URLs
codigo_fuente_ejemplo.txt       # Plantilla para código HTML
playlist_urls_ejemplo.txt       # Ejemplo de salida de playlist
test_urls.txt                   # URLs reales para probar
```

### 🎯 **Cómo Usar los Archivos de Ejemplo**

#### Para Procesar Lista de URLs:
```bash
# 1. Copia el archivo ejemplo
cp video_urls_ejemplo.txt mis_videos.txt

# 2. Edita y agrega tus URLs reales
nano mis_videos.txt

# 3. En el programa: Opción 2 → archivo: mis_videos.txt
```

#### Para Buscar en HTML:
```bash
# 1. Copia el archivo ejemplo  
cp codigo_fuente_ejemplo.txt codigo_fuente.txt

# 2. Pega tu código HTML real
nano codigo_fuente.txt

# 3. En el programa: Opción 4
```

#### Para Testing Rápido:
```bash
# Usa test_urls.txt para probar inmediatamente
python start.py → Opción 2 → test_urls.txt
```

## 📁 Estructura de Salida

Las transcripciones se organizan automáticamente:

```
transcripts/
  └── [nombre_carpeta]/
      ├── transcripts_plain/
      │   └── 001_[título_video]_[video_id].txt
      └── transcripts_with_timestamps/
          └── 001_[título_video]_[video_id].txt
```

### Ejemplo de contenido:
```
# Archivo plain:
Hola y bienvenidos a este tutorial sobre Python para SEO...

# Archivo con timestamps:
[00:00:05] Hola y bienvenidos a este tutorial sobre Python para SEO
[00:00:12] En este video vamos a aprender a automatizar...
```

## 🎬 Experiencia Durante el Procesamiento

### Barra de Progreso en Tiempo Real
```
🚀 Iniciando extracción de 25 video(s)...

Procesando... ▓▓▓▓▓▓▓░░░ 70.0% • 18/25 • 0:02:30
📹 Tutorial de Python para SEO - Extracción de Da...
```

### Resultado Final
```
╭─────────────────────────────── 🎉 Éxito Total ───────────────────────────────╮
│ ✅ ¡Procesamiento completado exitosamente!                                   │
│                                                                              │
│ 📊 Estadísticas:                                                             │
│    • Videos procesados: 25/25                                                │
│    • Éxito: 100%                                                             │
│                                                                              │
│ 📁 Archivos guardados en:                                                    │
│    • Texto plano: transcripts/mi_canal/transcripts_plain/                    │
│    • Con timestamps: transcripts/mi_canal/transcripts_with_timestamps/       │
╰──────────────────────────────────────────────────────────────────────────────╯
```

## 🔧 Requisitos Técnicos

- **Python 3.6+** (recomendado Python 3.8+)
- **yt-dlp** (para extracción robusta)
- **Dependencias automáticas** (instaladas por `install.py`):
  - requests
  - rich (interfaz mejorada)
  - colorama (colores)
  - pytube
  - beautifulsoup4

## 🛠️ Scripts Adicionales

### Extracción directa de playlists
```bash
python youtube_extractor_list.py "https://www.youtube.com/playlist?list=PLAYLIST_ID" output.txt
```

### Búsqueda en código HTML
```bash
python yt_url_finder.py
# Requiere archivo: codigo_fuente.txt
```

### Procesamiento manual de URLs
```bash
python url_processor.py
```

## 🎓 Casos de Uso

### 📚 **Para Creadores de Contenido**
```bash
# Extraer transcripciones de tu propia playlist
python start.py
# Selecciona opción 3, pega URL de tu playlist
```

### 🔬 **Para Investigadores**
```bash
# Analizar contenido de múltiples canales
# 1. Crea archivo con URLs de diferentes canales
# 2. Usa opción 2 para procesamiento por lotes
```

### 💼 **Para SEO y Marketing**
```bash
# Extraer contenido de competidores para análisis
# 1. Encuentra videos relevantes en tu nicho
# 2. Usa opción 1 para videos específicos
```

## ⚡ Consejos de Uso Eficiente

### 🚀 **Optimización de Velocidad**
- **URLs por lotes:** Agrupa videos similares en un archivo
- **Nombres descriptivos:** Usa nombres de carpeta que reflejen el contenido
- **Verificación previa:** Revisa que los videos tengan transcripciones disponibles

### 📁 **Organización de Archivos**
```
transcripts/
├── Canal_Educativo/          # ✅ Nombre descriptivo
├── Python_Tutorials_2024/   # ✅ Con fecha
├── Competidor_Analisis/     # ✅ Por propósito
└── Curso_Marketing_Digital/ # ✅ Por temática
```

## 🤔 Solución de Problemas

### ❌ **Error: "No se encontraron URLs válidas"**
**Soluciones:**
- ✅ Verifica que las URLs sean completas: `https://www.youtube.com/watch?v=VIDEO_ID`
- ✅ Prueba las URLs en tu navegador
- ✅ Revisa que los videos tengan transcripciones (CC disponible)

### ❌ **Error: "Faltan dependencias"**
```bash
# Solución rápida
python install.py

# Manual
pip install -r requirements.txt
```

### ⚠️ **Error: "No estás en un entorno virtual"**
```bash
# Activar entorno virtual primero:
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows

# Luego ejecutar:
python3 start.py              # macOS/Linux
python start.py               # Windows
```

### ❌ **Error: "Playlist vacía o no accesible"**
**Verificaciones:**
- ✅ La playlist debe ser pública
- ✅ URL debe contener `playlist?list=`
- ✅ La playlist no debe estar vacía

### 🪟 **Problemas Específicos de Windows**

#### Error: "python is not recognized"
```cmd
# Opción 1: Usar py launcher
py install.py
py start.py

# Opción 2: Reinstalar Python marcando "Add to PATH"
```

#### Error: "execution policy" (PowerShell)
```powershell
# Ejecutar como administrador:
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Error: "cannot find venv\Scripts\activate"
```cmd
# Crear entorno virtual primero:
python -m venv venv
venv\Scripts\activate
```

## 🔧 Configuración Avanzada

### 🌐 **Idiomas de Transcripción**
La aplicación prioriza automáticamente:
1. **Idioma original del video** (detectado automáticamente)
2. **Español** (si el original no está disponible)
3. **Inglés** (como fallback universal)
4. **Cualquier idioma** disponible

## 📄 Licencia

[MIT License](LICENSE)

---

## 📞 Soporte

### 🆘 **¿Necesitas ayuda?**

#### **Pasos rápidos:**
1. **Instalación**: `python install.py`
2. **Inicio**: `python start.py`  
3. **Problemas**: Revisa la sección "🤔 Solución de Problemas"

#### **Verificación rápida:**
```bash
# ¿Funciona la instalación?
python start.py

# ¿Hay problemas de dependencias?
python install.py

# ¿Qué archivos de ejemplo se crearon?
ls *ejemplo*.txt

# ¿Se creó la estructura de directorios?
ls transcripts/
```

### 🚀 **Comandos de Un Vistazo**
```bash
# Setup inicial
python install.py

# Uso diario
python start.py

# Modo avanzado
python youtube_transcript_extractor.py

# Procesar playlist específica
python youtube_extractor_list.py "URL_PLAYLIST" archivo_salida.txt
```

---

## 🎊 **La Nueva Experiencia**

### **Antes:**
- ❌ Comandos complejos en terminal
- ❌ Solo 2 opciones básicas  
- ❌ Sin validación de entrada
- ❌ Instalación manual complicada

### **Ahora:**
- ✅ **Interfaz visual elegante** con colores y emojis
- ✅ **5 opciones completas** para todas las necesidades
- ✅ **Detección automática de idiomas**
- ✅ **Validación automática** con preview de contenido
- ✅ **Instalación de un comando**: `python install.py`
- ✅ **Barras de progreso** en tiempo real
- ✅ **Para cualquier usuario** - no se necesitan conocimientos técnicos

### 💝 **El resultado:**
**¡La extracción de transcripciones de YouTube nunca fue tan fácil, rápida y profesional!** 

---

*🔗 **YouTube Transcript Extractor** - Transformando videos en conocimiento, una transcripción a la vez.*