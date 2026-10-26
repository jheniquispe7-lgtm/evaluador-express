import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import io
import time

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

tab1, tab2, tab3 = st.tabs(["📝 Generar Examen", "💻 Examen en Línea con Tiempo", "📸 Calificar Foto"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        materia = st.selectbox("Materia", MATERIAS)
        titulo = st.text_input("Título", "Evaluación Parcial")
        modo = st.selectbox("Tipo de Preguntas", ["Incisos (A, B, C, D)", "Preguntas Abiertas", "Falso / Verdadero", "Examen Mixto"])
        num_preg = st.slider("Número de preguntas", 1, 10, 5)
        
        fuente_tipo = st.radio("Fuente de inspiración", ["Texto o Temario", "Enlace Web (URL)"])
        if fuente_tipo == "Enlace Web (URL)":
            url_ref = st.text_input("🔗 Pega el link de referencia")
        else:
            texto_ref = st.text_area("Escribe o pega el texto de referencia")
            
        imgs_ref = st.file_uploader("Fotos de referencia (Opcional)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
        btn_generar = st.button("⚡ Generar Examen Impreso", type="primary")

    with col2:
        if btn_generar:
            if not api_key:
                st.error("⚠️ Ingresa tu API Key en la barra lateral.")
            else:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                contexto_extra = f"Enlace web: {url_ref}" if fuente_tipo == "Enlace Web (URL)" and 'url_ref' in locals() else f"Texto base: {texto_ref}"
                
                prompt = f"""
                Profesor de {materia}. Crea el examen '{titulo}'. 
                Formato: {modo}. Cantidad de preguntas: {num_preg}.
                REGLA: Redacta las preguntas claramente e incluye un Solucionario completo al final.
                {contexto_extra}
                """
                contenido = [prompt]
                if imgs_ref:
                    for img in imgs_ref:
                        contenido.append(optimizar_imagen(img))
                
                with st.spinner("⚡ Generando examen..."):
                    res = model.generate_content(contenido)
                    st.text_area("Examen y Solucionario", res.text, height=450)

with tab2:
    st.subheader("💻 Examen en Línea (Interactivo con Límite de Tiempo)")
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        mat_online = st.selectbox("Materia del examen", MATERIAS, key="mat_on")
        tipo_on = st.selectbox("Formato de preguntas", ["Incisos (A, B, C, D)", "Preguntas Abiertas", "Falso / Verdadero", "Mixto"], key="tipo_on")
        tema_on = st.text_input("Tema o Contenido del Examen", "Ej: Las Leyes de Newton y Física Aplicada")
        tiempo_limite = st.slider("⏱️ Límite de tiempo (minutos)", 1, 30, 5)
        
        if st.button("🚀 Iniciar Examen en Línea"):
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt_on = f"""
            Crea un examen interactivo de {mat_online} sobre '{tema_on}'.
            Formato: {tipo_on}.
            Cantidad: 4 preguntas directas. 
            Devuélvelo numerado y claro para que el estudiante responda. Incluye al final las respuestas correctas ocultas bajo una etiqueta 'SOLUCIONARIO_OCULTO:'.
            """
            st.session_state['examen_activo'] = model.generate_content(prompt_on).text
            st.session_state['tiempo_inicio'] = time.time()
            st.session_state['duracion_limite'] = tiempo_limite * 60
            st.success("¡Examen generado! Responde abajo antes de que acabe el tiempo.")

    with col_l2:
        if 'examen_activo' in st.session_state:
            # Control de tiempo simple
            tiempo_transcurrido = time.time() - st.session_state['tiempo_inicio']
            tiempo_restante = st.session_state['duracion_limite'] - tiempo_transcurrido
            
            if tiempo_restante > 0:
                mins, secs = divmod(int(tiempo_restante), 60)
                st.warning(f"⏳ **Tiempo restante:** {mins:02d}:{secs:02d}")
                
                st.markdown("### 📋 Cuestionario:")
                st.markdown(st.session_state['examen_activo'])
                
                st.markdown("---")
                respuestas_estudiante = st.text_area("✍️ Escribe tus respuestas ordenadas (Ej: 1: A, 2: V, 3: Explicación...)")
                
                if st.button("📤 Entregar Examen y Calificar"):
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    eval_prompt = f"""
                    Actúa como profesor evaluador. Revisa las respuestas del estudiante para este examen:
                    {st.session_state['examen_activo']}
                    
                    Respuestas del alumno:
                    {respuestas_estudiante}
                    
                    Entrega: 1. Calificación numérica (sobre 100), 2. Retroalimentación de aciertos y errores detallada.
                    """
                    with st.spinner("Corrigiendo examen..."):
                        resultado_revision = model.generate_content(eval_prompt)
                        st.success("✅ ¡Examen evaluado con éxito!")
                        st.markdown(resultado_revision.text)
            else:
                st.error("⏰ ¡El tiempo del examen ha terminado! Ya no se aceptan respuestas.")

with tab3:
    col_a, col_b = st.columns(2)
    with col_a:
        materia_ev = st.selectbox("Materia a calificar", MATERIAS, key="mat_ev")
        clave = st.text_area("Clave de respuestas (Ejemplo: 1: A, 2: F, 3: Verdadero)")
        fotos_eval = st.file_uploader("Fotos del examen físico", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
        btn_calificar = st.button("🔍 Calificar Foto al Instante", type="primary")

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
                prompt_ev = f"Califica este examen manuscrito. Materia: {materia_ev}. Clave: {clave}. Entrega: 1. Nota final, 2. Incisos/respuestas detectadas, 3. Detalle de errores."
                
                with st.spinner("Calificando imagen..."):
                    res_ev = model.generate_content([prompt_ev] + imgs_opt)
                    st.markdown(res_ev.text)