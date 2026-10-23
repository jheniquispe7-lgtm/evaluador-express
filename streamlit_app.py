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

tab1, tab2 = st.tabs(["📝 Generar Examen", "📸 Calificar Foto"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        materia = st.selectbox("Materia", MATERIAS)
        titulo = st.text_input("Título", "Examen Parcial")
        modo = st.selectbox("Tipo de Examen", ["Incisos (A, B, C, D)", "Preguntas Abiertas", "Examen Mixto"])
        num_preg = st.slider("Número de preguntas", 1, 10, 5)
        num_ver = st.radio("Versiones", ["2", "3"])
        texto_ref = st.text_area("Texto de referencia")
        imgs_ref = st.file_uploader("Fotos de referencia", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
        btn_generar = st.button("⚡ Generar Examen", type="primary")

    with col2:
        if btn_generar:
            if not api_key:
                st.error("⚠️ Ingresa tu API Key en la barra lateral.")
            else:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"""
                Profesor de {materia}. Crea el examen '{titulo}'. Modo: {modo}. Preguntas: {num_preg}. Versiones: {num_ver}.
                REGLA: Redacta cada pregunta con incisos completos (A, B, C, D) explícitos y un Solucionario al final.
                Texto base: {texto_ref}
                """
                contenido = [prompt]
                if imgs_ref:
                    for img in imgs_ref:
                        contenido.append(optimizar_imagen(img))
                res = model.generate_content(contenido)
                st.text_area("Examen Generado", res.text, height=400)

with tab2:
    col_a, col_b = st.columns(2)
    with col_a:
        materia_ev = st.selectbox("Materia a calificar", MATERIAS, key="mat_ev")
        clave = st.text_area("Clave de respuestas (Ejemplo: 1: A, 2: C)")
        fotos_eval = st.file_uploader("Fotos del examen resuelto", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
        btn_calificar = st.button("🔍 Calificar Instante", type="primary")

    with col_b:
        if btn_calificar:
            if not api_key:
                st.error("⚠️ Ingresa tu API Key en la barra lateral.")
            elif not fotos_eval:
                st.warning("⚠️ Sube al menos una foto.")
            else:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                imgs_opt = [optimizar_imagen(f) for f in fotos_eval]
                prompt_ev = f"Califica este examen. Materia: {materia_ev}. Clave: {clave}. Entrega: 1. Nota final, 2. Incisos detectados, 3. Errores."
                res_ev = model.generate_content([prompt_ev] + imgs_opt)
                st.markdown(res_ev.text)
