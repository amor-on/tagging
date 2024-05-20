# Aplicación de Etiquetado de Contenido Educativo

Esta aplicación permite cargar y etiquetar contenido educativo a partir de un archivo CSV. Está desarrollada con Streamlit y ofrece una interfaz intuitiva para el etiquetado de múltiples contenidos.

## Características

- Carga de contenido educativo desde un archivo CSV.
- Visualización y etiquetado del contenido en una interfaz amigable.
- Soporte para múltiples tipos de etiquetas: selección múltiple, selección única, booleanas y flotantes.
- Guardado de etiquetas y descarga del contenido etiquetado en un nuevo archivo CSV.
- Navegación sencilla entre filas de contenido para etiquetar.

## Instalación

### Requisitos del sistema

- Python 3.10.12

### Crear un entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Linux/MacOS
venv\Scripts\activate  # En Windows
```

### Instalar dependencias

```bash
pip install -r requirements.txt
```

## Uso

1. **Ejecutar la aplicación:**

```bash
streamlit run app.py
```

1.**Cargar un archivo CSV:**

- Utiliza la barra lateral para subir tu archivo CSV que contiene el contenido educativo.

2.**Navegar y etiquetar contenido:**

- La aplicación mostrará el contenido cargado. Selecciona la fila que deseas etiquetar y utiliza las opciones de etiquetado proporcionadas.

3.**Guardar y descargar el contenido etiquetado:**

- Una vez que hayas etiquetado el contenido, puedes guardar los cambios y descargar el archivo CSV actualizado.

## Estructura del Proyecto

- `app.py`: Código principal de la aplicación.
- `data/labels_info.json`: Archivo JSON con la información de las etiquetas.
- `utils/helpers.py`: Módulo con funciones auxiliares.
- `assets/styles.css`: Archivo CSS para estilos personalizados.
