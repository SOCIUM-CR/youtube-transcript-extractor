# Tests - YouTube Transcript Extractor

Suite completa de tests para YouTube Transcript Extractor.

## Estructura

```
tests/
├── unit/                    # Tests unitarios
│   ├── test_extractor.py   # Tests del extractor principal
│   ├── test_url_processor.py
│   └── test_youtube_extractor_list.py
├── integration/             # Tests de integración
├── fixtures/                # Archivos de ejemplo para tests
│   └── sample.vtt          # Archivo VTT de ejemplo
├── conftest.py             # Fixtures compartidas
└── README.md               # Este archivo
```

## Instalación de Dependencias

```bash
# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt
```

## Ejecutar Tests

### Todos los tests
```bash
pytest
```

### Con cobertura
```bash
pytest --cov
```

### Solo tests unitarios
```bash
pytest tests/unit/ -v
```

### Solo tests de integración
```bash
pytest tests/integration/ -v -m integration
```

### Excluir tests que requieren red
```bash
pytest -m "not network"
```

### Excluir tests lentos
```bash
pytest -m "not slow"
```

### Test específico
```bash
pytest tests/unit/test_extractor.py::TestExtractVideoId::test_extract_from_standard_url -v
```

## Reportes de Cobertura

### Terminal
```bash
pytest --cov --cov-report=term-missing
```

### HTML (navegador)
```bash
pytest --cov --cov-report=html
# Abrir: htmlcov/index.html
```

### XML (para CI/CD)
```bash
pytest --cov --cov-report=xml
```

## Markers Disponibles

Los tests están organizados con markers de pytest:

- `@pytest.mark.unit` - Tests unitarios
- `@pytest.mark.integration` - Tests de integración
- `@pytest.mark.network` - Tests que requieren conexión a internet
- `@pytest.mark.slow` - Tests que toman más de 1 segundo

### Ejemplos de uso de markers

```bash
# Solo tests unitarios
pytest -m unit

# Tests que NO requieren red
pytest -m "not network"

# Tests rápidos (sin slow)
pytest -m "not slow"

# Combinación
pytest -m "unit and not network"
```

## Fixtures Disponibles

Ver `conftest.py` para lista completa. Algunas fixtures útiles:

- `valid_youtube_urls` - Lista de URLs válidas
- `invalid_youtube_urls` - URLs inválidas para tests
- `sample_vtt_content` - Contenido VTT de ejemplo
- `sample_transcript_dict` - Transcripción completa mock
- `temp_output_dir` - Directorio temporal para tests
- `sample_urls_file` - Archivo con URLs de prueba

### Ejemplo de uso

```python
def test_my_function(valid_youtube_urls):
    """Test usando fixture de URLs válidas"""
    for url in valid_youtube_urls:
        result = my_function(url)
        assert result is not None
```

## Escribir Nuevos Tests

### Template de Test Unitario

```python
"""
Tests para mi_modulo.py
"""
import pytest
from mi_modulo import mi_funcion


class TestMiFuncion:
    """Tests para mi_funcion()"""

    def test_caso_basico(self):
        """Test caso básico"""
        resultado = mi_funcion('input')
        assert resultado == 'expected'

    def test_caso_edge(self):
        """Test caso edge"""
        resultado = mi_funcion('')
        assert resultado is None

    @pytest.mark.parametrize("input,expected", [
        ('a', 'A'),
        ('b', 'B'),
        ('c', 'C'),
    ])
    def test_multiples_casos(self, input, expected):
        """Test múltiples casos con parametrize"""
        assert mi_funcion(input) == expected
```

### Tests con Mocks

```python
from unittest.mock import Mock, patch

def test_con_mock():
    """Test usando mock"""
    with patch('youtube_transcript_extractor.subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = 'output'

        # Tu código de test aquí
        resultado = funcion_que_usa_subprocess()
        assert resultado == 'expected'
```

## Buenas Prácticas

1. **Un test, un concepto**: Cada test debe verificar una sola cosa
2. **Nombres descriptivos**: `test_extract_video_id_from_standard_url` es mejor que `test_1`
3. **AAA Pattern**: Arrange (preparar), Act (actuar), Assert (verificar)
4. **Usar fixtures**: Reutilizar código de setup con fixtures
5. **Tests independientes**: Un test no debe depender de otro
6. **Cleanup automático**: Usar `tmp_path` fixture para archivos temporales
7. **Documentar con docstrings**: Explicar qué hace el test

### Ejemplo de AAA Pattern

```python
def test_process_video():
    """Test procesamiento de video"""
    # Arrange (preparar)
    extractor = YouTubeTranscriptExtractor()
    video_url = 'https://youtube.com/watch?v=abc123'

    # Act (actuar)
    result = extractor.get_transcript(video_url)

    # Assert (verificar)
    assert result is not None
    assert 'segments' in result
```

## Continuous Integration

Los tests se ejecutan automáticamente en GitHub Actions:

- En cada push a branches: `main`, `develop`, `claude/**`
- En cada Pull Request
- En múltiples OS: Ubuntu, Windows, macOS
- En múltiples versiones de Python: 3.8, 3.9, 3.10, 3.11

Ver: `.github/workflows/tests.yml`

## Troubleshooting

### Tests fallan con "ModuleNotFoundError"
```bash
# Asegúrate de estar en el directorio raíz
cd /path/to/youtube-transcript-extractor

# Instala el proyecto en modo editable
pip install -e .
```

### Tests de integración fallan
```bash
# Los tests de integración requieren conexión
# Skipea tests de red si no tienes conexión
pytest -m "not network"
```

### Coverage muy bajo
```bash
# Verifica qué archivos no están cubiertos
pytest --cov --cov-report=term-missing

# Verifica archivos específicos
pytest --cov=youtube_transcript_extractor --cov-report=term-missing
```

## Métricas de Calidad

### Objetivo de Cobertura
- **Mínimo aceptable**: 60%
- **Objetivo**: 70%+
- **Ideal**: 80%+

### Verificar Cobertura Actual
```bash
pytest --cov --cov-report=term

# Output ejemplo:
# youtube_transcript_extractor.py    450    120    73%
# url_processor.py                    43      5    88%
# ...
# TOTAL                              650    150    77%
```

## Recursos

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)

## Contribuir

Al agregar nuevas features:

1. Escribe tests primero (TDD)
2. Asegúrate que todos los tests pasen
3. Verifica cobertura no disminuya
4. Actualiza este README si es necesario
