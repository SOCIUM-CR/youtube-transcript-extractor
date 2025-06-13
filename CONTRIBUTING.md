# Contribuir a YouTube Transcript Extractor

¡Gracias por tu interés en contribuir a YouTube Transcript Extractor! Este documento proporciona pautas y información sobre cómo contribuir al proyecto.

## 📋 Formas de Contribuir

### 🐛 Reportar Bugs
- Usa GitHub Issues para reportar bugs
- Incluye pasos detallados para reproducir el problema
- Especifica tu sistema operativo y versión de Python
- Adjunta logs o capturas de pantalla si es relevante

### 💡 Sugerir Funcionalidades
- Abre un Issue con la etiqueta "enhancement"
- Describe claramente la funcionalidad propuesta
- Explica el caso de uso y beneficios

### 🔧 Enviar Pull Requests
- Fork el repositorio
- Crea una rama para tu feature: `git checkout -b feature/nueva-funcionalidad`
- Realiza tus cambios
- Añade tests si es aplicable
- Asegúrate de que el código sigue las convenciones del proyecto
- Envía el pull request

## 🛠️ Configuración del Entorno de Desarrollo

### Requisitos
- Python 3.6+
- pip
- git

### Configuración Inicial
```bash
# 1. Fork y clonar el repositorio
git clone https://github.com/tu-usuario/youtube-transcript-extractor.git
cd youtube-transcript-extractor

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Instalar dependencias
python install.py
# o manualmente: pip install -r requirements.txt

# 4. Verificar instalación
python start.py
```

## 📝 Convenciones de Código

### Estilo de Código
- Sigue PEP 8 para el estilo de Python
- Usa nombres descriptivos para variables y funciones
- Comenta código complejo
- Mantén funciones pequeñas y con una sola responsabilidad

### Estructura de Commits
```
tipo(alcance): descripción breve

Descripción más detallada si es necesario.

- Cambio específico 1
- Cambio específico 2
```

**Tipos de commit:**
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Documentación
- `style`: Cambios de formato/estilo
- `refactor`: Refactorización de código
- `test`: Añadir o modificar tests
- `chore`: Tareas de mantenimiento

### Ejemplo:
```
feat(extractor): añadir soporte para subtítulos automáticos

Implementa detección automática de idioma y selección
inteligente de subtítulos basada en el idioma original.

- Añadir método _detect_video_language()
- Mejorar _select_best_vtt_file_smart()
- Actualizar logging para mostrar idioma detectado
```

## 🧪 Testing

### Ejecutar Tests
```bash
# Tests básicos
python test_simple.py

# Tests funcionales
python test_real_functionality.py

# Verificar interfaz
python demo_interface.py
```

### Añadir Tests
- Crea tests para nuevas funcionalidades
- Asegúrate de que los tests existentes pasen
- Incluye tests de casos edge
- Usa datos de prueba que no dependan de recursos externos

## 📁 Estructura del Proyecto

```
youtube-transcript-extractor/
├── youtube_transcript_extractor.py  # Script principal
├── youtube_extractor_list.py       # Extractor de playlists
├── yt_url_finder.py                # Buscador de URLs en HTML
├── url_processor.py                # Procesador manual de URLs
├── install.py                      # Script de instalación
├── start.py                        # Launcher inteligente
├── requirements.txt                # Dependencias
├── README.md                       # Documentación principal
├── CONTRIBUTING.md                 # Esta guía
├── LICENSE                         # Licencia MIT
├── .gitignore                      # Archivos a ignorar
└── context/                        # Archivos de configuración
    └── *.md                        # Documentación técnica
```

## 🎯 Áreas de Contribución Prioritarias

### 🔥 Alta Prioridad
- Mejoras en robustez ante cambios de YouTube
- Optimización de performance para lotes grandes
- Soporte para más idiomas
- Mejoras en la interfaz de usuario

### 🚀 Media Prioridad
- Integración con servicios de traducción
- Export a diferentes formatos (JSON, CSV, etc.)
- Sistema de cache para evitar re-descargas
- Análisis automático de contenido

### 💡 Ideas Futuras
- Interfaz web con Streamlit/Flask
- Integración con APIs de IA para resúmenes
- Plugin para editores de video
- Análisis de sentimientos en transcripciones

## 📞 Comunicación

### Canales de Comunicación
- **GitHub Issues**: Para bugs y sugerencias
- **GitHub Discussions**: Para preguntas generales
- **Pull Requests**: Para contribuciones de código

### Obtener Ayuda
Si tienes preguntas sobre cómo contribuir:
1. Revisa la documentación existente
2. Busca en Issues cerrados
3. Abre un nuevo Issue con la etiqueta "question"

## 🏆 Reconocimiento

Todos los contribuyentes serán reconocidos en:
- README.md (sección de contribuyentes)
- Releases notes
- Comentarios de commit cuando sea apropiado

## 📜 Código de Conducta

### Nuestro Compromiso
Nos comprometemos a hacer de la participación en nuestro proyecto una experiencia libre de acoso para todos, independientemente de edad, tamaño corporal, discapacidad, etnia, identidad y expresión de género, nivel de experiencia, nacionalidad, apariencia personal, raza, religión o identidad y orientación sexual.

### Nuestros Estándares
**Comportamientos que contribuyen a crear un ambiente positivo:**
- Usar lenguaje acogedor e inclusivo
- Ser respetuoso con diferentes puntos de vista
- Aceptar críticas constructivas
- Enfocarse en lo que es mejor para la comunidad
- Mostrar empatía hacia otros miembros

**Comportamientos inaceptables:**
- Lenguaje o imágenes sexualizadas
- Comentarios insultantes o despectivos
- Acoso público o privado
- Publicar información privada sin permiso
- Otras conductas que podrían considerarse inapropiadas

## 🚀 Primeros Pasos

1. **Lee la documentación**: Familiarízate con README.md
2. **Configura el entorno**: Sigue las instrucciones de instalación
3. **Explora el código**: Entiende la estructura del proyecto
4. **Busca "good first issues"**: Issues marcados para principiantes
5. **Haz tu primera contribución**: Empezar con algo pequeño

## 📝 Licencia

Al contribuir a este proyecto, aceptas que tus contribuciones serán licenciadas bajo la Licencia MIT del proyecto.

---

¡Gracias por hacer que YouTube Transcript Extractor sea mejor para todos! 🎉