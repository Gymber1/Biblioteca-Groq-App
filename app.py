import streamlit as st
import fitz  # PyMuPDF
from groq import Groq
import json
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Ref+ Groq", page_icon="⚡", layout="wide")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    /* FONDO */
    .stApp { background: linear-gradient(to bottom right, #0f172a, #1e293b); color: white; }
    
    /* SIDEBAR */
    section[data-testid="stSidebar"] { background-color: #0f172a; border-right: 1px solid #334155; }
    
    /* UPLOADER */
    [data-testid="stFileUploader"] {
        background: linear-gradient(90deg, #1e293b, #0f172a);
        border: 2px dashed #f43f5e;
        border-radius: 15px; padding: 20px; text-align: center;
    }
    [data-testid="stFileUploader"] label { display: none; }
    
    /* TARJETAS */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 15px !important; margin-bottom: 15px;
    }
    
    /* TEXTOS */
    .title-code .stCode { font-size: 18px !important; font-weight: bold !important; color: #f43f5e !important; }
    h1, h2, h3 { color: #f8fafc !important; }
    .stCaption { color: #94a3b8 !important; text-transform: uppercase; font-size: 10px; font-weight: bold; }
    .stCode { font-size: 12px !important; }
    
    /* BOTONES */
    div.stButton > button {
        background-color: #f43f5e; color: white; font-weight: bold; border: none; transition: all 0.3s;
    }
    div.stButton > button:hover { background-color: #e11d48; transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES ---
def extraer_json_seguro(texto_ia):
    try:
        inicio = texto_ia.find('[')
        fin = texto_ia.rfind(']') + 1
        if inicio != -1 and fin != 0:
            return json.loads(texto_ia[inicio:fin])
        return None
    except:
        return None

@st.dialog("Visor de Documento", width="large")
def visualizar_pdf_modal(file_bytes):
    base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="700px" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def procesar_pdf(pdf_file):
    bytes_data = pdf_file.getvalue()
    doc = fitz.open(stream=bytes_data, filetype="pdf")
    texto_completo = ""
    encontrado = False
    total_paginas = len(doc)
    
    for i, pagina in enumerate(doc):
        texto = pagina.get_text()
        # Filtro estricto anti-tabla
        if "REFERENCIAS BIBLIOGRÁFICAS" in texto.upper() or "BIBLIOGRAFÍA" in texto.upper():
            lines = texto.split('\n')
            for line in lines:
                clean_line = line.strip().upper()
                es_titulo_real = ("REFERENCIAS BIBLIOGRÁFICAS" in clean_line) or (clean_line == "BIBLIOGRAFÍA")
                es_tabla_falsa = "APA" in clean_line
                if es_titulo_real and not es_tabla_falsa:
                    encontrado = True
                    break
        if i == total_paginas - 1 and not encontrado: encontrado = True 
        if encontrado: texto_completo += texto + "\n"
    
    page = doc.load_page(0)
    pix = page.get_pixmap()
    img_bytes = pix.tobytes("png")
    return texto_completo, img_bytes

# --- GESTIÓN DE SESIÓN (LOGIN) ---
if 'api_key_valid' not in st.session_state:
    st.session_state.api_key_valid = False
if 'groq_key' not in st.session_state:
    st.session_state.groq_key = ""

# --- SIDEBAR INTELIGENTE ---
with st.sidebar:
    if not st.session_state.api_key_valid:
        # ESTADO 1: NO HAY CLAVE (Login)
        st.title("🔐 Configuración")
        st.markdown("Ingresa tu llave de Groq para activar el sistema.")
        
        input_key = st.text_input("API Key (gsk_...)", type="password")
        
        if st.button("🚀 Entrar", use_container_width=True):
            if input_key.startswith("gsk_"):
                st.session_state.groq_key = input_key
                st.session_state.api_key_valid = True
                st.rerun() # <--- ESTO RECARGA LA PÁGINA Y OCULTA EL INPUT
            else:
                st.error("La clave debe empezar con 'gsk_'")
        
        st.divider()
        st.caption("¿No tienes clave? Consíguela gratis en console.groq.com")
        
    else:
        # ESTADO 2: YA HAY CLAVE (Menú Normal)
        st.title("Biblioteca - Referencias ⚡")
        st.caption("Conectado con Llama 3")
        st.divider()
        
        # Placeholder para el botón de visualizar (se llena desde el main)
        placeholder_boton = st.empty()
        
        st.info("💡 Arrastra el PDF al recuadro grande.")
        
        st.divider()
        # Botón para salir y volver a poner clave
        if st.button("🔴 Cerrar Sesión", use_container_width=True):
            st.session_state.api_key_valid = False
            st.session_state.groq_key = ""
            st.rerun()

# --- BLOQUEO DE SEGURIDAD ---
# Si no hay clave válida, detenemos la ejecución aquí.
if not st.session_state.api_key_valid:
    st.markdown("""
    <div style='text-align: center; padding: 50px;'>
        <h1>👋 Bienvenido a Ref+ Groq</h1>
        <p>Por favor, ingresa tu API Key en la barra lateral para comenzar.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop() # DETIENE TODO EL CÓDIGO DE ABAJO

# --- A PARTIR DE AQUÍ SOLO SE EJECUTA SI HAY CLAVE ---
client = Groq(api_key=st.session_state.groq_key)

# Inicializar variables de memoria
if 'archivo_procesado' not in st.session_state: st.session_state.archivo_procesado = None
if 'datos_libros' not in st.session_state: st.session_state.datos_libros = None
if 'img_preview' not in st.session_state: st.session_state.img_preview = None

# --- UI PRINCIPAL ---
st.markdown("## User Dashboard")
st.markdown("##### 📂 Sube tu PDF Aquí")
uploaded_file = st.file_uploader("Arrastra tu sílabo aquí", type="pdf")

if uploaded_file is not None:
    file_id = f"{uploaded_file.name}_{uploaded_file.size}"
    
    # Inyectamos el botón en el hueco que dejamos en la sidebar
    with placeholder_boton.container():
        st.success("✅ Archivo Cargado")
        if st.button("👁️ Visualizar PDF", use_container_width=True):
            visualizar_pdf_modal(uploaded_file.getvalue())

    col_izq, col_der = st.columns([1.5, 3.5])

    # Lógica de procesamiento (Solo si es archivo nuevo)
    if st.session_state.archivo_procesado != file_id:
        with st.spinner("🚀 Groq analizando..."):
            try:
                texto_ref, img_preview = procesar_pdf(uploaded_file)
                
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "Eres experto en bibliografía. Corrige errores OCR."},
                        {"role": "user", "content": f"""
                            Extrae referencias finales (Ignora tablas APA).
                            Corrige errores (ej: '?ujo' -> 'Flujo').
                            Formato JSON estricto: [{{Titulo, Autor, Editorial, Ciudad, Anio, ISBN}}]
                            Texto: {texto_ref}
                        """}
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.1,
                    stream=False,
                )
                
                datos = extraer_json_seguro(chat_completion.choices[0].message.content)
                st.session_state.archivo_procesado = file_id
                st.session_state.datos_libros = datos
                st.session_state.img_preview = img_preview
                
            except Exception as e:
                st.error(f"Error: {e}")
                st.session_state.datos_libros = []

    # Mostrar Resultados
    datos = st.session_state.datos_libros
    img_preview = st.session_state.img_preview

    with col_izq:
        st.markdown("### 📊 Estado")
        if datos: st.metric("Libros", len(datos))
        else: st.metric("Estado", "0 Ref.")
        st.divider()
        if img_preview: st.image(img_preview, caption="Portada", use_container_width=True)

    with col_der:
        st.markdown("### 📋 Resultados")
        if datos:
            for libro in datos:
                with st.container(border=True):
                    st.caption("TÍTULO (Click icono para copiar)")
                    st.markdown('<div class="title-code">', unsafe_allow_html=True)
                    st.code(libro.get('Titulo', '---'), language=None)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.caption("AUTOR"); st.code(libro.get('Autor', ''), language=None)
                        st.caption("EDITORIAL"); st.code(libro.get('Editorial', ''), language=None)
                    with c2:
                        st.caption("AÑO"); st.code(libro.get('Anio', ''), language=None)
                        st.caption("CIUDAD"); st.code(libro.get('Ciudad', ''), language=None)
                    
                    if libro.get('ISBN') and libro.get('ISBN') != "No encontrado":
                        st.divider(); st.caption("ISBN"); st.code(libro.get('ISBN'), language=None)
        elif st.session_state.archivo_procesado == file_id:
            st.warning("No se encontraron referencias válidas.")

else:
    st.session_state.archivo_procesado = None
    placeholder_boton.empty()
    st.info("👆 Esperando archivo...")