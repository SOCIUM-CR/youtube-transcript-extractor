# 🚀 Instalación Rápida - macOS/Linux

## ⚡ Instalación en 3 Pasos (Recomendado)

```bash
# 1. Crear entorno virtual
python3 -m venv venv

# 2. Activar entorno virtual  
source venv/bin/activate

# 3. Instalar automáticamente
python3 install.py
```

## 🎯 Uso Inmediato

```bash
# ¡IMPORTANTE! Activar entorno virtual primero
source venv/bin/activate

# Ejecutar la aplicación
python3 start.py

# Probar con URLs de ejemplo
# → Opción 2: Lista de URLs
# → Archivo: test_urls.txt
```

## 🔧 Si Hay Problemas

### Error: "command not found: python"
```bash
# Usa python3 en su lugar
python3 install.py
python3 start.py
```

### Error: "No such file or directory: venv/bin/activate"
```bash
# Primero crea el entorno virtual
python3 -m venv venv
source venv/bin/activate
```

### Error: "NameError: name 'Path' is not defined"
```bash
# Esto ya está corregido en la versión actual
# Si lo ves, descarga la versión más reciente
```

## 📁 ¿Qué se Crea?

Después de la instalación tendrás:
```
├── transcripts/                  # Directorio para transcripciones
├── video_urls_ejemplo.txt        # Plantilla para URLs
├── codigo_fuente_ejemplo.txt     # Plantilla para HTML
├── test_urls.txt                # URLs de prueba
└── venv/                        # Entorno virtual
```

## 🎉 ¡Listo!

Tu instalación está completa. Usa `python3 start.py` para comenzar.