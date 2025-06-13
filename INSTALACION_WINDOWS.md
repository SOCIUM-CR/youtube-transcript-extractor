# 🚀 Instalación Rápida - Windows

## ⚡ Instalación en 3 Pasos (Recomendado)

```cmd
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno virtual  
venv\Scripts\activate

# 3. Instalar automáticamente
python install.py
```

## 🎯 Uso Inmediato

```cmd
# ¡IMPORTANTE! Activar entorno virtual primero
venv\Scripts\activate

# Ejecutar la aplicación
python start.py

# Probar con URLs de ejemplo
# → Opción 2: Lista de URLs
# → Archivo: test_urls.txt
```

## 🔧 Si Hay Problemas

### Error: "python is not recognized"
```cmd
# Opción 1: Reinstalar Python desde python.org y marcar "Add to PATH"
# Opción 2: Usar py launcher
py -m venv venv
py install.py
py start.py
```

### Error: "cannot find venv\Scripts\activate"
```cmd
# Primero crea el entorno virtual
python -m venv venv
venv\Scripts\activate
```

### Error: "execution policy"
```powershell
# En PowerShell como administrador:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Luego activa el entorno:
venv\Scripts\Activate.ps1
```

### Error: "pip is not recognized"
```cmd
# Actualizar pip
python -m ensurepip --upgrade
python -m pip install --upgrade pip
```

## 📁 ¿Qué se Crea?

Después de la instalación tendrás:
```
├── transcripts\                  # Directorio para transcripciones
├── video_urls_ejemplo.txt        # Plantilla para URLs
├── codigo_fuente_ejemplo.txt     # Plantilla para HTML
├── test_urls.txt                # URLs de prueba
└── venv\                        # Entorno virtual
```

## 🎯 Comandos Específicos de Windows

### Comando Prompt (CMD)
```cmd
python -m venv venv
venv\Scripts\activate
python install.py
python start.py
```

### PowerShell
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
python install.py
python start.py
```

### Git Bash
```bash
python -m venv venv
source venv/Scripts/activate
python install.py
python start.py
```

## 🔑 Características Específicas de Windows

- ✅ **Detección automática de Windows**: El instalador detecta que estás en Windows
- ✅ **Comandos correctos**: Usa `python` en lugar de `python3`
- ✅ **Rutas de Windows**: Usa `\` en lugar de `/` para activar entorno virtual
- ✅ **Compatible con CMD, PowerShell y Git Bash**

## 🎉 ¡Listo!

Tu instalación está completa. Usa `python start.py` para comenzar.

## 🆘 Ayuda Adicional

Si tienes problemas, el instalador te dará instrucciones específicas para tu sistema Windows.