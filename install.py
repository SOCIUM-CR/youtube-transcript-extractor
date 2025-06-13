#!/usr/bin/env python3
"""
Script de instalación para YouTube Transcript Extractor
Instala automáticamente todas las dependencias necesarias.
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def run_command(command, description):
    """Ejecuta un comando y muestra el progreso."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}:")
        print(f"   {e.stderr}")
        return False

def get_system_info():
    """Obtiene información del sistema operativo y comandos apropiados."""
    system = platform.system().lower()
    is_windows = system == "windows"
    
    # Determinar comando Python apropiado
    if is_windows:
        python_cmd = "python"
        activate_cmd = "venv\\Scripts\\activate"
    else:  # macOS/Linux
        python_cmd = "python3" if "python3" in sys.executable else "python"
        activate_cmd = "source venv/bin/activate"
    
    return {
        "system": system,
        "is_windows": is_windows,
        "python_cmd": python_cmd,
        "activate_cmd": activate_cmd
    }

def check_python_version():
    """Verifica que la versión de Python sea compatible."""
    version = sys.version_info
    system_info = get_system_info()
    
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print("❌ Python 3.6 o superior es requerido.")
        print(f"   Versión actual: {version.major}.{version.minor}.{version.micro}")
        print(f"\n💡 Sistema detectado: {system_info['system'].title()}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    print(f"✅ Sistema: {system_info['system'].title()}")
    return True

def create_project_structure():
    """Crea la estructura de directorios del proyecto."""
    print("📁 Creando estructura de directorios...")
    
    directories = [
        "transcripts",
        "transcripts/ejemplos",
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Creado: {directory}/")
    
    print()

def create_example_files():
    """Crea archivos de ejemplo para el usuario."""
    print("📄 Creando archivos de ejemplo...")
    
    # Archivo de ejemplo de URLs para videos individuales
    example_urls = """# Archivo de ejemplo para URLs de YouTube
# Una URL por línea, las líneas que empiecen con # son comentarios

# Ejemplo de video individual:
# https://www.youtube.com/watch?v=dQw4w9WgXcQ

# Puedes agregar tantas URLs como necesites:
# https://www.youtube.com/watch?v=otro_video_id
# https://www.youtube.com/watch?v=tercer_video_id

# Para usar este archivo:
# 1. Descomenta las URLs que quieras procesar (quita el #)
# 2. Reemplaza las URLs de ejemplo con las reales
# 3. Guarda el archivo
# 4. En el programa, selecciona la opción 2 y usa este archivo"""
    
    with open("video_urls_ejemplo.txt", "w", encoding="utf-8") as f:
        f.write(example_urls)
    print("✅ Creado: video_urls_ejemplo.txt")
    
    # Archivo de ejemplo para código HTML
    html_example = """<!-- Archivo de ejemplo para buscar URLs de YouTube en código HTML -->
<!-- Pega aquí el código fuente HTML que contenga videos de YouTube -->

<!-- Ejemplo de HTML que contiene URLs de YouTube: -->
<!--
<a href="https://www.youtube.com/watch?v=dQw4w9WgXcQ">Video 1</a>
<iframe src="https://www.youtube.com/embed/otro_video_id"></iframe>
<script>
    var videoUrl = "https://youtu.be/tercer_video";
</script>
-->

<!-- INSTRUCCIONES DE USO:
1. Reemplaza este contenido con el código HTML real
2. El programa buscará automáticamente URLs de YouTube en el contenido
3. Guarda el archivo como codigo_fuente.txt
4. En el programa, selecciona la opción 4
-->"""
    
    with open("codigo_fuente_ejemplo.txt", "w", encoding="utf-8") as f:
        f.write(html_example)
    print("✅ Creado: codigo_fuente_ejemplo.txt")
    
    # URLs de ejemplo para testing
    test_urls = """# URLs de prueba para verificar funcionamiento
# Estas son URLs reales que puedes usar para probar

# Video en inglés (para probar detección de idioma)
https://www.youtube.com/watch?v=dQw4w9WgXcQ

# Video educativo corto
# https://www.youtube.com/watch?v=kJQP7kiw5Fk"""
    
    with open("test_urls.txt", "w", encoding="utf-8") as f:
        f.write(test_urls)
    print("✅ Creado: test_urls.txt")
    
    print()

def main():
    print("🎥 YouTube Transcript Extractor - Instalador")
    print("=" * 50)
    
    # Verificar versión de Python
    if not check_python_version():
        return
    
    # Verificar si estamos en un entorno virtual
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if not in_venv:
        print("⚠️  No se detectó un entorno virtual activo.")
        print("   Se recomienda usar un entorno virtual para evitar conflictos.")
        response = input("   ¿Continuar con la instalación global? (y/N): ")
        if response.lower() != 'y':
            system_info = get_system_info()
            print("💡 Para crear un entorno virtual ejecuta:")
            print(f"   {system_info['python_cmd']} -m venv venv")
            print(f"   {system_info['activate_cmd']}")
            if not system_info['is_windows']:
                print("   # Luego ejecuta este script de nuevo")
            else:
                print("   # Luego ejecuta este script de nuevo")
            return
    else:
        print("✅ Entorno virtual activo")
    
    # Crear estructura del proyecto
    create_project_structure()
    create_example_files()
    
    print("🚀 Iniciando instalación de dependencias...")
    
    # Lista de comandos de instalación
    installations = [
        ("pip install --upgrade pip", "Actualizando pip"),
        ("pip install yt-dlp>=2023.7.6", "Instalando yt-dlp (extractor principal)"),
        ("pip install requests>=2.25.1", "Instalando requests"),
        ("pip install colorama>=0.4.4", "Instalando colorama (colores en terminal)"),
        ("pip install rich>=13.0.0", "Instalando rich (interfaz mejorada)"),
        ("pip install pytube", "Instalando pytube (para playlists)"),
        ("pip install beautifulsoup4", "Instalando beautifulsoup4 (parser HTML)"),
    ]
    
    success_count = 0
    total_count = len(installations)
    
    for command, description in installations:
        if run_command(command, description):
            success_count += 1
        print()  # Línea en blanco para claridad
    
    print("=" * 50)
    if success_count == total_count:
        print("🎉 ¡Instalación completada exitosamente!")
        system_info = get_system_info()
        print(f"\n🚀 Para usar la aplicación ejecuta:")
        print(f"   {system_info['python_cmd']} start.py")
        print(f"\n📋 O directamente:")
        print(f"   {system_info['python_cmd']} youtube_transcript_extractor.py")
        print("\n📁 Estructura creada:")
        print("   • transcripts/ - Directorio para transcripciones")
        print("   • video_urls_ejemplo.txt - Archivo ejemplo de URLs")
        print("   • codigo_fuente_ejemplo.txt - Ejemplo para HTML")
        print("   • test_urls.txt - URLs de prueba")
        print("\n💡 Funciones disponibles:")
        print("   • Extraer video individual")
        print("   • Procesar lista de URLs desde archivo")
        print("   • Extraer playlist completa")
        print("   • Buscar URLs en código HTML")
        print("\n🎯 Primeros pasos:")
        print(f"   1. Ejecuta: {system_info['python_cmd']} start.py")
        print("   2. Prueba con test_urls.txt (opción 2)")
        print("   3. O usa video_urls_ejemplo.txt como plantilla")
    else:
        failed = total_count - success_count
        print(f"⚠️  Instalación completada con {failed} errores.")
        print("   Revisa los mensajes de error arriba y reintenta la instalación.")
        print("   Puedes intentar instalar manualmente con:")
        print("   pip install -r requirements.txt")

if __name__ == "__main__":
    main()