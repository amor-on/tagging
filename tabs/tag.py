import pandas as pd
import streamlit as st
from utils.helpers import load_labels_info
from datetime import datetime
import os

# Cargar etiquetas desde el archivo JSON
@st.cache_data
def load_labels():
    return load_labels_info('data/labels/labels_info.json')

labels_info = load_labels()

def show_tagging_tab():
    if 'ready_to_tag' in st.session_state and st.session_state['ready_to_tag']:
        if 'content_df' in st.session_state:
            content_df = st.session_state['content_df']
            
            if 'selected_options' not in st.session_state:
                st.session_state['selected_options'] = {}
            
            if 'current_row' not in st.session_state:
                st.session_state['current_row'] = 0

            row_to_label = st.session_state['current_row']
            
            # Añadir columnas para etiquetas si no existen
            for label in labels_info:
                if label["name"] not in content_df.columns:
                    content_df[label["name"]] = ""
            
            # Título de la aplicación y logo en el encabezado
            st.title("Etiquetado de contenido")
            
            # Asegurarse de que row_to_label esté dentro del rango válido de filas
            if row_to_label >= len(content_df):
                row_to_label = len(content_df) - 1

            # Selección de fila para etiquetar
            new_row_to_label = st.number_input("Seleccione el índice de la fila para etiquetar:", min_value=0, max_value=len(content_df)-1, value=row_to_label, key='row_selector')

            if new_row_to_label != row_to_label:
                st.session_state['current_row'] = new_row_to_label
                st.rerun()

            
            row_data = content_df.iloc[new_row_to_label]

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
                    with st.container():  # Utilizar contenedor para cada etiqueta
                        st.markdown('---')  # Línea divisoria entre categorías
                        label_name = label["name"]
                        label_type = label["type"]
                        label_description = label["description"]
                        label_values = label["values"]
                        quantifiable = label.get("quantifiable", False)

                        # Obtener los valores seleccionados anteriormente si existen
                        current_value = row_data[label_name]
                        default_value = []

                        if label_type == "multiselect" and pd.notna(current_value):
                            for item in current_value.split(','):
                                option = item.split(':')[0].strip()
                                if option in label_values:
                                    default_value.append(option)

                        elif label_type == "select" and pd.notna(current_value):
                            if current_value in label_values:
                                default_value.append(current_value)

                        elif label_type in ["float", "bool"] and pd.notna(current_value) and current_value != '':
                            try:
                                default_value.append(float(current_value))
                            except ValueError:
                                pass

                        if label_type == "multiselect":
                            # Permitir seleccionar todas las opciones primero
                            selected_options = st.multiselect(f"**{label_name}**", options=label_values, default=default_value, help=label_description, key=f"multiselect_{label_name}_{row_to_label}")
                            etiquetas[label_name] = {}

                            # Mostrar los sliders después de seleccionar todas las opciones
                            for option in selected_options:
                                if quantifiable:
                                    relevance = st.slider(f"Relevancia para **{option}**", 0.0, 1.0, 1.0, step=0.01, format="%.2f", key=f"relevance_{label_name}_{option}_{row_to_label}")
                                    etiquetas[label_name][option] = relevance
                                else:
                                    etiquetas[label_name][option] = "NA"

                        elif label_type == "select":
                            if len(label_values) <= 6:
                                if default_value and default_value[0] in label_values:
                                    selected_option_index = label_values.index(default_value[0])
                                else:
                                    selected_option_index = 0
                                selected_option = st.radio(f"**{label_name}**", options=label_values, index=selected_option_index, help=label_description, key=f"radio_{label_name}_{row_to_label}")
                                st.session_state['selected_options'][label_name] = [selected_option]
                                if quantifiable:
                                    relevance = st.slider(f"Relevancia para **{selected_option}**", 0.0, 1.0, 1.0, step=0.01, format="%.2f", key=f"relevance_{label_name}_{row_to_label}")
                                    etiquetas[label_name] = {selected_option: relevance}
                                else:
                                    etiquetas[label_name] = selected_option
                            else:
                                if default_value and default_value[0] in label_values:
                                    selected_option_index = label_values.index(default_value[0])
                                else:
                                    selected_option_index = 0
                                selected_option = st.selectbox(f"**{label_name}**", options=label_values, index=selected_option_index, help=label_description, key=f"select_{label_name}_{row_to_label}")
                                st.session_state['selected_options'][label_name] = [selected_option]
                                if quantifiable:
                                    relevance = st.slider(f"Relevancia para **{selected_option}**", 0.0, 1.0, 1.0, step=0.01, format="%.2f", key=f"relevance_{label_name}_{row_to_label}")
                                    etiquetas[label_name] = {selected_option: relevance}
                                else:
                                    etiquetas[label_name] = selected_option
                        elif label_type in ["float", "bool"]:
                            if default_value:
                                value = st.slider(f"**{label_name}**", min_value=0.0, max_value=1.0, value=default_value[0], step=0.01, help=label_description, key=f"slider_{label_name}_{row_to_label}") if label_type == "float" \
                                    else st.radio(f"**{label_name}**", options=["No aplica", "True", "False"], index=["No aplica", "True", "False"].index(default_value[0]) if default_value else 0, horizontal=True, help=label_description, key=f"radio_{label_name}_{row_to_label}")
                            else:
                                value = st.slider(f"**{label_name}**", min_value=0.0, max_value=1.0, value=1.0, step=0.01, help=label_description, key=f"slider_{label_name}_{row_to_label}") if label_type == "float" \
                                    else st.radio(f"**{label_name}**", options=["No aplica", "True", "False"], index=0, horizontal=True, help=label_description, key=f"radio_{label_name}_{row_to_label}")
                            etiquetas[label_name] = value
                               

                # Botón "Guardar y continuar"
                if st.button("Guardar y continuar", help="Guarda las etiquetas actuales y pasa a la siguiente fila para seguir etiquetando."):
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
                        st.rerun()

                # Botón "Guardar progreso"
                if st.button("Guardar progreso", type="primary", help="Guarda el progreso actual como una nueva versión del CSV etiquetado."):
                    final_columns = ["stage", "course", "content", "age", "subject", "unit_type", "unit_title", "card_title", "block_title", "card_type", "block_type", "text"] + [label["name"] for label in labels_info]
                    content_df = content_df[final_columns]
                    # Guardar cambios en una nueva versión del CSV
                    user = "user1"  # Aquí debes reemplazar esto con el login del usuario actual
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    file_name = os.path.basename(st.session_state['current_file_path']).replace('.csv', f'_{user}_{timestamp}.csv')
                    versioned_file_path = os.path.join(os.path.dirname(os.path.dirname(st.session_state['current_file_path'])), 'versions', file_name)
                    os.makedirs(os.path.dirname(versioned_file_path), exist_ok=True)
                    content_df.to_csv(versioned_file_path, index=False)
                    st.success("CSV guardado con éxito!")
                    
                    # Mostrar botón para descargar el CSV guardado
                    st.download_button(
                        label="Descargar CSV guardado",
                        data=content_df.to_csv(index=False).encode('utf-8'),
                        file_name=file_name,
                        mime='text/csv'
                    )

                                
        else:
            st.warning("Por favor, cargue un archivo CSV desde la pestaña de 'Exploración de Contenidos'.")
    else:
        st.warning("Por favor, seleccione un archivo CSV desde la pestaña de 'Exploración de Contenidos'.")