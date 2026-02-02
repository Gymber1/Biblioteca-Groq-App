import streamlit as st
import fitz  # PyMuPDF
from groq import Groq
import json
import base64
import re
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Ref+ Groq", page_icon="⚡", layout="wide")

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
    
    /* TARJETAS DE RESULTADOS */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 15px !important; margin-bottom: 15px;
    }
    
    /* CÓDIGO (Botones de copia) */
    .stCode { font-family: 'Source Code Pro', monospace !important; font-size: 14px !important; }
    
    /* ETIQUETAS PEQUEÑAS */
    .stCaption { color: #94a3b8 !important; text-transform: uppercase; font-size: 11px; font-weight: bold; margin-bottom: 0px !important; margin-top: 5px !important; }
    
    /* BOTONES ROJOS */
    div.stButton > button {
        background-color: #f43f5e; color: white; font-weight: bold; border: none; transition: all 0.3s;
    }
    div.stButton > button:hover { background-color: #e11d48; transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)


def escanear_enlaces(texto):
    """Analiza enlaces para dar contexto a la IA sobre si es basura o material académico"""
    urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', texto)
    urls = list(set(urls)) 
    
    info_web = ""
    if urls:
        with st.status("🌐 Analizando enlaces externos...", expanded=True) as status:
            for url in urls:
                if not url.startswith('http'): url = 'http://' + url
                try:
                    status.write(f"Verificando: {url[:40]}...")
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    response = requests.get(url, headers=headers, timeout=2)
                    
                    if response.status_code == 200:
                        content_type = response.headers.get('Content-Type', '').lower()
                        if 'pdf' in content_type:
                            titulo_web = "ARCHIVO PDF (Alta probabilidad de ser Libro/Paper)"
                        else:
                            soup = BeautifulSoup(response.text, 'html.parser')
                            titulo_web = soup.title.string.strip() if soup.title else "Web General"
                        
                        info_web += f"- URL: {url} | TIPO DETECTADO: {titulo_web}\n"
                    else:
                        info_web += f"- URL: {url} (No accesible, ignorar si no es obvio)\n"
                except:
                    info_web += f"- URL: {url} (Error conexión)\n"
            status.update(label="✅ Enlaces procesados", state="complete", expanded=False)
    return info_web

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
    for pagina in doc:
        texto_completo += pagina.get_text() + "\n"
    
    page = doc.load_page(0)
    pix = page.get_pixmap()
    img_bytes = pix.tobytes("png")
    return texto_completo, img_bytes

if 'api_key_valid' not in st.session_state: st.session_state.api_key_valid = False
if 'groq_key' not in st.session_state: st.session_state.groq_key = ""

with st.sidebar:
    if not st.session_state.api_key_valid:
        st.title("🔐 Configuración")
        st.markdown("Ingresa tu llave de Groq para activar.")
        input_key = st.text_input("API Key (gsk_...)", type="password")
        if st.button("🚀 Entrar", use_container_width=True):
            if input_key.startswith("gsk_"):
                st.session_state.groq_key = input_key
                st.session_state.api_key_valid = True
                st.rerun()
            else:
                st.error("La clave debe empezar con 'gsk_'")
    else:
        st.title("Biblioteca ⚡")
        placeholder_boton = st.empty()
        st.divider()
        if st.button("🔴 Cerrar Sesión", use_container_width=True):
            st.session_state.api_key_valid = False
            st.session_state.groq_key = ""
            st.rerun()

if not st.session_state.api_key_valid:
    st.markdown("<h1 style='text-align:center'>👋 Bienvenido a Ref+ Groq</h1>", unsafe_allow_html=True)
    st.stop()

client = Groq(api_key=st.session_state.groq_key)

if 'archivo_procesado' not in st.session_state: st.session_state.archivo_procesado = None
if 'datos_libros' not in st.session_state: st.session_state.datos_libros = None
if 'img_preview' not in st.session_state: st.session_state.img_preview = None

# --- UI PRINCIPAL ---
st.markdown("## Dashboard de Referencias")
uploaded_file = st.file_uploader("Arrastra tu sílabo aquí", type="pdf")

if uploaded_file is not None:
    file_id = f"{uploaded_file.name}_{uploaded_file.size}"
    
    with placeholder_boton.container():
        st.success("✅ Archivo Cargado")
        if st.button("👁️ PDF Original", use_container_width=True):
            visualizar_pdf_modal(uploaded_file.getvalue())

    if st.session_state.archivo_procesado != file_id:
        
        texto_pdf, img_preview = procesar_pdf(uploaded_file)
        
        # 1. Escanear enlaces
        contexto_web = escanear_enlaces(texto_pdf)
        
        with st.spinner("🧠 Groq analizando (Recuperando años perdidos)..."):
            try:
                prompt_usuario = f"""
                Eres un Bibliotecario Académico Experto con memoria enciclopédica.
                
                TU MISIÓN: Completar la bibliografía del sílabo, rellenando datos faltantes con tu conocimiento.

                REGLAS DE ORO (AÑOS Y DATOS):
                1. **DETECTAR**: Si el año está en el PDF, úsalo.
                2. **AUTO-COMPLETAR (CRUCIAL)**: Si el PDF NO tiene el año (o dice s/f), **TÚ DEBES PONER EL AÑO REAL** usando tu conocimiento.
                   - Ejemplo: Si ves "Boudeville - La región económica", tú sabes que es de ~1961. ¡Pon "1961" (o la fecha de la edición más conocida)!
                   - **PROHIBIDO** dejar el campo "Anio" vacío o poner "Sin especificar" si es un libro conocido.
                   - Lo mismo para Ciudad y Editorial. ¡Rellénalos!

                REGLAS DE FILTRADO (LINKS):
                - Videos/Blogs/Wikis -> BASURA (Ignorar).
                - Libros/Papers/Tesis -> VÁLIDO.

                TEXTO PDF:
                {texto_pdf}
                
                INFO WEB:
                {contexto_web}
                
                SALIDA JSON OBLIGATORIA:
                [
                    {{
                        "Titulo": "Título Completo",
                        "Autor": "Autor",
                        "Editorial": "Editorial (Rellenar si falta)",
                        "Ciudad": "Ciudad (Rellenar si falta)",
                        "Anio": "AAAA (¡OBLIGATORIO RELLENAR!)",
                        "Tipo": "Libro/Paper"
                    }}
                ]
                """

                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "Eres un experto en bibliografía que SIEMPRE completa los años y editoriales faltantes usando su base de datos interna."},
                        {"role": "user", "content": prompt_usuario}
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.2
                )
                
                datos = extraer_json_seguro(chat_completion.choices[0].message.content)
                st.session_state.archivo_procesado = file_id
                st.session_state.datos_libros = datos
                st.session_state.img_preview = img_preview
                
            except Exception as e:
                st.error(f"Error: {e}")
                st.session_state.datos_libros = []

    datos = st.session_state.datos_libros
    img_preview = st.session_state.img_preview
    
    c1, c2 = st.columns([1.5, 3.5])
    with c1:
        st.markdown("### 📊 Resumen")
        if datos: st.metric("Referencias Válidas", len(datos))
        if img_preview: st.image(img_preview, caption="Portada", use_container_width=True)
    
    with c2:
        st.markdown("### 📚 Lista Procesada")
        if datos:
            for libro in datos:
                with st.container(border=True):
                    st.caption(f"TÍTULO ({libro.get('Tipo', 'Ref')})")
                    st.code(libro.get('Titulo', '---'), language=None)
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.caption("AUTOR")
                        st.code(libro.get('Autor', '---'), language=None)
                        st.caption("EDITORIAL")
                        st.code(libro.get('Editorial', '---'), language=None)
                    with col_b:
                        st.caption("AÑO")
                        st.code(libro.get('Anio', '---'), language=None)
                        st.caption("CIUDAD")
                        st.code(libro.get('Ciudad', '---'), language=None)
        elif st.session_state.archivo_procesado == file_id:
            st.warning("Se analizaron los textos y enlaces, pero no se encontraron libros o papers válidos.")
else:
    st.session_state.archivo_procesado = None
    placeholder_boton.empty()
    st.info("👆 Sube un archivo para comenzar")