import os
import pandas as pd
import streamlit as st
from utils.helpers import load_labels_info

# Cargar etiquetas desde el archivo JSON
@st.cache_data
def load_labels():
    return load_labels_info('data/labels/labels_info.json')

labels_info = load_labels()

# Función para explorar el directorio de contenidos
def explore_directory(base_path):
    content_summary = []
    for isbn in os.listdir(base_path):
        original_path = os.path.join(base_path, isbn, 'original')
        versions_path = os.path.join(base_path, isbn, 'versions')
        if os.path.isdir(original_path):
            for file in os.listdir(original_path):
                if file.endswith(".csv"):
                    file_path = os.path.join(original_path, file)
                    content_summary.append({
                        "isbn": isbn,
                        "file_name": file,
                        "file_path": file_path,
                        "versions_path": versions_path
                    })
    return content_summary

def explore_versions(versions_path, unit_name):
    versions_summary = []
    if os.path.exists(versions_path):
        for file in os.listdir(versions_path):
            if file.startswith(unit_name) and file.endswith('.csv'):
                file_path = os.path.join(versions_path, file)
                df = pd.read_csv(file_path)
                total_rows = len(df)
                available_labels = [label["name"] for label in labels_info if label["name"] in df.columns]
                labeled_rows = df.dropna(how='all', subset=available_labels).shape[0]
                if labeled_rows == 0:
                    status = "Pending"
                elif labeled_rows == total_rows:
                    status = "Done"
                else:
                    status = "In Progress"
                versions_summary.append({
                    "file_name": file,
                    "file_path": file_path,
                    "status": status,
                    "total_rows": total_rows,
                    "labeled_rows": labeled_rows
                })
    return versions_summary

def show_explore_sidebar():
    base_path = 'data/contents'
    content_summary = explore_directory(base_path)

    st.sidebar.header("Exploración de Contenidos")

    # Agrupar archivos CSV por el directorio padre (ISBN)
    grouped_content = {}
    for item in content_summary:
        isbn = item['isbn']
        if isbn not in grouped_content:
            grouped_content[isbn] = []
        grouped_content[isbn].append(item)
    
    # Selección del ISBN
    isbns = sorted(grouped_content.keys())
    selected_isbn = st.sidebar.selectbox("Seleccione el ISBN", isbns)
    
    # Mostrar unidades del ISBN seleccionado
    if selected_isbn:
        units = grouped_content[selected_isbn]
        unit_options = [f"{unit['file_name']}" for unit in units]
        selected_unit = st.sidebar.selectbox("Seleccione la unidad", unit_options)
        
        if selected_unit:
            unit_index = unit_options.index(selected_unit)
            selected_file_path = units[unit_index]['file_path']
            versions_path = units[unit_index]['versions_path']
            unit_name = units[unit_index]['file_name'].split('.')[0]
            
            # Comprobar si existen versiones guardadas para la unidad seleccionada
            versions_summary = explore_versions(versions_path, unit_name)
            if versions_summary:
                version_options = ["Etiquetar desde cero"] + [
                    f"{version['file_name']} - {version['status']} ({version['labeled_rows']}/{version['total_rows']} filas etiquetadas)"
                    for version in versions_summary
                ]
                selected_version = st.sidebar.selectbox("Seleccione una versión guardada", version_options)
                
                if st.sidebar.button("Cargar Unidad"):
                    if selected_version == "Etiquetar desde cero":
                        content_df = pd.read_csv(selected_file_path)
                        st.session_state['current_row'] = 0
                    else:
                        version_index = version_options.index(selected_version) - 1
                        versioned_file_path = versions_summary[version_index]['file_path']
                        content_df = pd.read_csv(versioned_file_path)
                        st.session_state['current_row'] = versions_summary[version_index]['labeled_rows']
                    
                    st.session_state['content_df'] = content_df.copy()
                    st.session_state['current_file_path'] = selected_file_path
                    st.session_state['selected_options'] = {}
                    st.session_state['ready_to_tag'] = True
                    st.rerun()  # Recargar la aplicación para mostrar el contenido
            else:
                if st.sidebar.button("Etiquetar desde cero"):
                    content_df = pd.read_csv(selected_file_path)
                    st.session_state['content_df'] = content_df.copy()
                    st.session_state['current_file_path'] = selected_file_path
                    st.session_state['current_row'] = 0
                    st.session_state['selected_options'] = {}
                    st.session_state['ready_to_tag'] = True
                    st.rerun()  # Recargar la aplicación para mostrar el contenido
