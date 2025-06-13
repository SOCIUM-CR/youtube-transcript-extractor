#!/usr/bin/env python3
"""
Script de arranque rápido para YouTube Transcript Extractor
Verifica dependencias y lanza la aplicación con interfaz mejorada.
"""

import sys
import os
import subprocess
import platform

def check_dependencies():
    """Verifica si las dependencias están instaladas."""
    required_packages = [
        'yt-dlp',
        'requests', 
        'rich',
        'colorama',
        'pytube',
        'beautifulsoup4'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'beautifulsoup4':
                __import__('bs4')
            elif package == 'yt-dlp':
                # yt-dlp es un comando, verificar si está disponible
                result = subprocess.run(['yt-dlp', '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode != 0:
                    missing_packages.append(package)
            else:
                __import__(package)
        except (ImportError, subprocess.TimeoutExpired, FileNotFoundError):
            missing_packages.append(package)
    
    return missing_packages

def get_system_commands():
    """Obtiene comandos específicos del sistema."""
    system = platform.system().lower()
    if system == "windows":
        return {
            "python": "python",
            "install_cmd": "python install.py"
        }
    else:  # macOS/Linux
        return {
            "python": "python3",
            "install_cmd": "python3 install.py"
        }

def check_virtual_env():
    """Verifica si estamos en un entorno virtual."""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def main():
    system_cmds = get_system_commands()
    print("🎥 YouTube Transcript Extractor")
    print(f"Sistema: {platform.system()}")
    
    # Verificar si estamos en entorno virtual
    in_venv = check_virtual_env()
    if not in_venv:
        print("⚠️  No estás en un entorno virtual")
        print("💡 Para activar el entorno virtual:")
        if platform.system().lower() == "windows":
            print("   venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
        print(f"   Luego ejecuta: {system_cmds['python']} start.py")
        return
    
    print("✅ Entorno virtual activo")
    print("Verificando dependencias...")
    
    missing = check_dependencies()
    
    if missing:
        print(f"❌ Faltan dependencias: {', '.join(missing)}")
        print("\n💡 Para instalar las dependencias ejecuta:")
        print(f"   {system_cmds['install_cmd']}")
        print("   O manualmente: pip install -r requirements.txt")
        return
    
    print("✅ Todas las dependencias están instaladas")
    print("🚀 Iniciando YouTube Transcript Extractor...\n")
    
    # Importar y ejecutar la aplicación principal
    try:
        from youtube_transcript_extractor import main
        main()
    except Exception as e:
        print(f"❌ Error al ejecutar la aplicación: {str(e)}")
        print("\n💡 Si el problema persiste:")
        print("   1. Ejecuta: python install.py")
        print("   2. Verifica que todos los archivos estén presentes")
        print("   3. Revisa que no hay errores de sintaxis")

if __name__ == "__main__":
    main()