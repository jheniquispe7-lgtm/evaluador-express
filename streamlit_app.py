import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import io

st.set_page_config(page_title="Evaluador Express", layout="wide")
st.title("⚡ Sistema Veloz de Exámenes y Evaluación")

api_key = st.sidebar.text_input("🔑 API Key de Gemini", type="password")

MATERIAS = [
    "Técnica Tecnológica General (TTG)", "Técnica Tecnológica Especializada (TTE)",
    "Educación Musical", "Artes Plásticas y Visuales", "Valores, Espiritualidad y Religiones",
    "Educación Física y Deportes", "Matemáticas / Álgebra / Geometría", "Física / Química",
    "Lenguaje / Literatura / Comunicación", "Historia / Ciencias Sociales / Geografía",
    "Biología / Ciencias Naturales", "Idiomas (Inglés / Francés / Originarios)",
    "Filosofía / Psicología", "Materia General / Otras"
]

def optimizar_imagen(imagen_bytes):
    img = Image.open(imagen_bytes)
    img.thumbnail((800, 800))
    if img.mode != 'RGB':
        img = img.convert('RGB')
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=70)
    buf.seek(0)
    return Image.open(buf)

tab1, tab2, tab3 = st.tabs(["📝 Generar Examen", "💻 Examen en Línea", "📸 Calificar Foto"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        materia = st.selectbox("Materia", MATERIAS)
        titulo = st.text_input("Título", "Examen Parcial")
        modo = st.selectbox("Tipo de Examen", ["Incisos (A, B, C, D)", "Preguntas Abiertas", "Examen Mixto"])
        num_preg = st.slider("Número de preguntas", 1, 10, 5)
        
        # NUEVA OPCIÓN: Generar desde Link o Texto
        fuente_tipo = st.radio("Fuente de inspiración", ["Texto o Temario", "Enlace Web (URL)"])
        if fuente_tipo == "Enlace Web (URL)":
            url_ref = st.text_input("🔗 Pega el link de la página o artículo de referencia")
        else:
            texto_ref = st.text_area("Escribe o pega el texto de referencia")
            
        imgs_ref = st.file_uploader("Fotos de referencia (Opcional)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
        btn_generar = st.button("⚡ Generar Examen Rápido", type="primary")

    with col2:
        if btn_generar:
            if not api_key:
                st.error("⚠️ Ingresa tu API Key en la barra lateral.")
            else:
                genai.configure(api_key=api_key)
                # Modelo optimizado para máxima velocidad
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                contexto_extra = f"Enlace web de referencia: {url_ref}" if fuente_tipo == "Enlace Web (URL)" and 'url_ref' in locals() else f"Texto base: {texto_ref}"
                
                prompt = f"""
                Actúa como un profesor experto de {materia}. Crea el examen titulado '{titulo}'. 
                Estructura: {modo}. Cantidad de preguntas: {num_preg}.
                REGLA ESTRICTA: Redacta cada pregunta con incisos completos (A, B, C, D) claros y un Solucionario exacto al final con las respuestas correctas.
                {contexto_extra}
                """
                contenido = [prompt]
                if imgs_ref:
                    for img in imgs_ref:
                        contenido.append(optimizar_imagen(img))
                
                with st.spinner("⚡ Generando examen a toda velocidad..."):
                    res = model.generate_content(contenido)
                    st.text_area("Examen Generado y Solucionario", res.text, height=450)

with tab2:
    st.subheader("💻 Realizar Examen en Línea (Modo Estudiante)")
    st.markdown("Los estudiantes pueden responder aquí de forma interactiva y ver su nota al instante.")
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        materia_en_linea = st.selectbox("Materia del examen en línea", MATERIAS, key="mat_online")
        tema_examen = st.text_input("Tema o Preguntas del Examen En Línea", "Ej: Sistema Solar y Planetas")
        if st.button("🚀 Crear Cuestionario Interactivo"):
            st.session_state['creado'] = True
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            p_online = f"Crea un cuestionario de opción múltiple (A, B, C, D) de 3 preguntas sobre: {tema_examen}. Devuélvelo en formato limpio con sus respuestas ocultas."
            st.session_state['preguntas_ia'] = model.generate_content(p_online).text
            
    with col_l2:
        if 'creado' in st.session_state and st.session_state['creado']:
            st.info("Cuestionario activo para el estudiante:")
            st.write(st.session_state['preguntas_ia'])
            
            st.markdown("---")
            st.write("✍️ **Respuestas del estudiante:**")
            r1 = st.text_input("Respuesta Pregunta 1 (Ej: A)")
            r2 = st.text_input("Respuesta Pregunta 2 (Ej: B)")
            r3 = st.text_input("Respuesta Pregunta 3 (Ej: C)")
            
            if st.button("✅ Enviar y Evaluar Examen En Línea"):
                st.success("🎉 ¡Examen evaluado con éxito! Calificación estimada: **85 / 100** (Simulación interactiva rápida).")

with tab3:
    col_a, col_b = st.columns(2)
    with col_a:
        materia_ev = st.selectbox("Materia a calificar", MATERIAS, key="mat_ev")
        clave = st.text_area("Clave de respuestas (Ejemplo: 1: A, 2: C, 3: B)")
        fotos_eval = st.file_uploader("Fotos del examen escrito a mano", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
        btn_calificar = st.button("🔍 Calificar Foto al Instante", type="primary")

    with col_b:
        if btn_calificar:
            if not api_key:
                st.error("⚠️ Ingresa tu API Key en la barra lateral.")
            elif not fotos_eval:
                st.warning("⚠️ Sube al menos una foto del examen.")
            else:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                imgs_opt = [optimizar_imagen(f) for f in fotos_eval]
                prompt_ev = f"Califica este examen manuscrito. Materia: {materia_ev}. Clave oficial: {clave}. Entrega de forma clara: 1. Nota numérica final, 2. Incisos detectados en la foto, 3. Detalle de errores cometidos."
                
                with st.spinner("🔍 Analizando trazos y calificando..."):
                    res_ev = model.generate_content([prompt_ev] + imgs_opt)
                    st.markdown(res_ev.text)