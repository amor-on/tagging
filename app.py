import streamlit as st
import pandas as pd
from utils.helpers import load_labels_info

# Configuración de la página
st.set_page_config(page_title="Aplicación de Etiquetado", layout="wide")

# Cargar etiquetas desde el archivo JSON
@st.cache_data
def load_labels():
    return load_labels_info('data/labels_info.json')

labels_info = load_labels()

# Sidebar para cargar archivos y mostrar el logo
st.sidebar.title("Opciones de Carga")
uploaded_csv = st.sidebar.file_uploader("Subir CSV de Contenidos", type="csv")

@st.cache_data
def load_csv(file):
    return pd.read_csv(file)

# Verificar si se han cargado los archivos
if uploaded_csv:
    content_df = load_csv(uploaded_csv)
    
    if 'selected_options' not in st.session_state:
        st.session_state['selected_options'] = {}
    
    if 'content_df' not in st.session_state:
        st.session_state['content_df'] = content_df.copy()
    
    if 'current_row' not in st.session_state:
        st.session_state['current_row'] = 0

    content_df = st.session_state['content_df']
    row_to_label = st.session_state['current_row']
    
    # Añadir columnas para etiquetas si no existen
    for label in labels_info:
        if label["name"] not in content_df.columns:
            content_df[label["name"]] = ""
    
    # Título de la aplicación y logo en el encabezado
    st.title("Etiquetado de contenido")
    
    # Selección de fila para etiquetar
    new_row_to_label = st.number_input("Seleccione el índice de la fila para etiquetar:", min_value=0, max_value=len(content_df)-1, value=row_to_label, key='row_selector')
    
    if new_row_to_label != row_to_label:
        st.session_state['current_row'] = new_row_to_label
        st.rerun()
    
    row_data = content_df.iloc[row_to_label]

    header = st.container()

    st.markdown(f"**{row_data['subject']}** > **{row_data['card_title']}** ({row_data['card_type']}) > **{row_data['block_title']}** ({row_data['block_type']})")

    # Cargar CSS
    with open('assets/styles.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    # Dividir la página en dos columnas
    col1, col2 = st.columns([2, 2])

    # Mostrar contenido en la primera columna
    with col1:
        header = st.container()
        header.write("### Contenido para etiquetar\n\n")
        text_content = row_data['text']
        text_lines = text_content.split('\n')
        for line in text_lines:
            if line.startswith("http"):
                if any(ext in line for ext in ['.png', '.jpg', '.jpeg', '.gif']):
                    header.image(line)
                elif any(ext in line for ext in ['.mp4', '.webm']):
                    header.video(line)
                elif any(ext in line for ext in ['.mp3', '.wav', '.ogg']):
                    header.audio(line)
                else:
                    header.write(line)
            else:
                header.write(line)
        
        header.write("""<div class='fixed-header'/>""", unsafe_allow_html=True)

    # Formulario para etiquetado en la segunda columna
    with col2:
        etiquetas = {}
        for label in labels_info:
            label_name = label["name"]
            label_type = label["type"]
            label_description = label["description"]
            label_values = label["values"]
            quantifiable = label.get("quantifiable", False)

            # Obtener los valores seleccionados anteriormente si existen
            default_value = st.session_state['selected_options'].get(label_name, [])

            if label_type == "multiselect":
                # Permitir seleccionar todas las opciones primero
                selected_options = st.multiselect(f"**{label_name}**", options=label_values, default=default_value, help=label_description, key=f"multiselect_{label_name}_{row_to_label}")
                etiquetas[label_name] = {}

                # Mostrar los sliders después de seleccionar todas las opciones
                for option in selected_options:
                    if quantifiable:
                        relevance = st.slider(f"Relevancia para '{option}' en {label_name}", 0.0, 1.0, 1.0, step=0.01, format="%.2f", key=f"relevance_{label_name}_{option}_{row_to_label}")
                        etiquetas[label_name][option] = relevance
                    else:
                        etiquetas[label_name][option] = "NA"

            elif label_type == "select":
                if len(label_values) <= 6:
                    selected_option = st.radio(f"**{label_name}**", options=label_values, index=label_values.index(default_value[0]) if default_value else 0, help=label_description, key=f"radio_{label_name}_{row_to_label}")
                    st.session_state['selected_options'][label_name] = [selected_option]
                    if quantifiable:
                        relevance = st.slider(f"Relevancia para '{selected_option}'", 0.0, 1.0, 1.0, step=0.01, format="%.2f", key=f"relevance_{label_name}_{row_to_label}")
                        etiquetas[label_name] = {selected_option: relevance}
                    else:
                        etiquetas[label_name] = selected_option
                else:
                    selected_option = st.selectbox(f"**{label_name}**", options=label_values, index=label_values.index(default_value[0]) if default_value else 0, help=label_description, key=f"select_{label_name}_{row_to_label}")
                    st.session_state['selected_options'][label_name] = [selected_option]
                    if quantifiable:
                        relevance = st.slider(f"Relevancia para '{selected_option}' en {label_name}", 0.0, 1.0, 1.0, step=0.01, format="%.2f", key=f"relevance_{label_name}_{row_to_label}")
                        etiquetas[label_name] = {selected_option: relevance}
                    else:
                        etiquetas[label_name] = selected_option
            elif label_type in ["float", "bool"]:
                value = st.slider(f"**{label_name}**", min_value=0.0, max_value=1.0, value=default_value[0] if default_value else 1.0, step=0.01, help=label_description, key=f"slider_{label_name}_{row_to_label}") if label_type == "float" \
                        else st.radio(f"**{label_name}**", options=["No aplica", "True", "False"], index=["No aplica", "True", "False"].index(default_value[0]) if default_value else 0, horizontal=True, help=label_description, key=f"radio_{label_name}_{row_to_label}")
                etiquetas[label_name] = value
    
        if st.button("Guardar y ver siguiente"):
            for label_name, values in etiquetas.items():
                
                if isinstance(values, dict):
                    formatted_values = ", ".join(f"{k}:{v:.2f}" if isinstance(v, float) else f"{k}:NA" for k, v in values.items())
                    content_df.at[row_to_label, label_name] = formatted_values
                else:
                    content_df.at[row_to_label, label_name] = values

                # Guardar las selecciones actuales en session_state para la próxima fila
                st.session_state['selected_options'][label_name] = list(values.keys()) if isinstance(values, dict) else [values]
                
            st.session_state['content_df'] = content_df.copy()
            st.success("Etiqueta guardada con éxito!")
            
            # Ir a la siguiente fila automáticamente
            if row_to_label + 1 < len(content_df):
                st.session_state['current_row'] = row_to_label + 1
                st.rerun()  # Actualización aquí
    
        # Guardar cambios en un nuevo CSV
        if st.button("Guardar CSV"):
            final_columns = ["stage", "course", "content", "age", "subject", "unit_type", "unit_title", "card_title", "block_title", "card_type", "block_type", "text"] + [label["name"] for label in labels_info]
            content_df = content_df[final_columns]
            csv = content_df.to_csv(index=False).encode('utf-8')
            st.download_button(label="Descargar CSV", data=csv, file_name='etiquetado.csv', mime='text/csv')
        
        # Botón para borrar todas las selecciones
        if st.button("Borrar todas las selecciones"):
            st.session_state['selected_options'] = {}
            st.rerun()

else:
    st.warning("Por favor, suba el archivo CSV de contenido para continuar.")