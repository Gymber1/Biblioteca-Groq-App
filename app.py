import streamlit as st
import fitz  # PyMuPDF
from groq import Groq
import json
import base64
import re
import requests
from bs4 import BeautifulSoup

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Biblio-Groq Llama 3", page_icon="⚡", layout="wide")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom right, #0f172a, #1e293b); color: white; }
    section[data-testid="stSidebar"] { background-color: #0f172a; border-right: 1px solid #334155; }
    [data-testid="stFileUploader"] {
        background: linear-gradient(90deg, #1e293b, #0f172a);
        border: 2px dashed #f43f5e;
        border-radius: 15px; padding: 20px; text-align: center;
    }
    .stCode { font-family: 'Source Code Pro', monospace !important; font-size: 14px !important; }
    .stCaption { color: #94a3b8 !important; text-transform: uppercase; font-size: 11px; font-weight: bold; margin-bottom: 0px !important; margin-top: 5px !important; }
    div.stButton > button {
        background-color: #f43f5e; color: white; font-weight: bold; border: none; transition: all 0.3s;
    }
    div.stButton > button:hover { background-color: #e11d48; transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES ---

def escanear_enlaces(texto):
    urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', texto)
    urls = list(set(urls)) 
    
    info_web = ""
    if urls:
        with st.status("🌐 Verificando enlaces...", expanded=True) as status:
            for i, url in enumerate(urls[:6]):
                if not url.startswith('http'): url = 'http://' + url
                try:
                    status.write(f"Leyendo: {url[:40]}...")
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    response = requests.get(url, headers=headers, timeout=2)
                    
                    if response.status_code == 200:
                        content_type = response.headers.get('Content-Type', '').lower()
                        if 'pdf' in content_type:
                            titulo_web = "ARCHIVO PDF ACADÉMICO"
                        else:
                            soup = BeautifulSoup(response.text, 'html.parser')
                            titulo_web = soup.title.string.strip()[:100] if soup.title else "Web General"
                        info_web += f"- Link: {url} | Título: {titulo_web}\n"
                    else:
                        info_web += f"- Link: {url} (Inaccesible)\n"
                except:
                    pass
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

# --- GESTIÓN DE SESIÓN ---
if 'api_key_valid' not in st.session_state: st.session_state.api_key_valid = False
if 'groq_key' not in st.session_state: st.session_state.groq_key = ""

with st.sidebar:
    if not st.session_state.api_key_valid:
        st.title("🔐 Configuración Groq")
        st.markdown("Ingresa tu **Groq API Key**.")
        input_key = st.text_input("API Key (gsk_...)", type="password")
        if st.button("🚀 Conectar", use_container_width=True):
            if input_key.startswith("gsk_"):
                st.session_state.groq_key = input_key
                st.session_state.api_key_valid = True
                st.rerun()
            else:
                st.error("Clave inválida. Debe empezar con 'gsk_'")
    else:
        st.title("Biblio-Groq ⚡")
        placeholder_boton = st.empty()
        st.divider()
        if st.button("🔴 Cerrar Sesión", use_container_width=True):
            st.session_state.api_key_valid = False
            st.session_state.groq_key = ""
            st.rerun()

if not st.session_state.api_key_valid:
    st.markdown("<h1 style='text-align:center'>👋 Bienvenido a Biblio-Groq</h1>", unsafe_allow_html=True)
    st.stop()

client = Groq(api_key=st.session_state.groq_key)

if 'archivo_procesado' not in st.session_state: st.session_state.archivo_procesado = None
if 'datos_libros' not in st.session_state: st.session_state.datos_libros = None
if 'img_preview' not in st.session_state: st.session_state.img_preview = None

st.markdown("## Dashboard de Referencias (Llama 3)")
uploaded_file = st.file_uploader("Sube tu sílabo (PDF)", type="pdf")

if uploaded_file is not None:
    file_id = f"{uploaded_file.name}_{uploaded_file.size}"
    
    with placeholder_boton.container():
        st.success("✅ Archivo Cargado")
        if st.button("👁️ PDF Original", use_container_width=True):
            visualizar_pdf_modal(uploaded_file.getvalue())

    if st.session_state.archivo_procesado != file_id:
        
        texto_pdf, img_preview = procesar_pdf(uploaded_file)
        contexto_web = escanear_enlaces(texto_pdf)
        
        with st.spinner("🧠 Llama 3 filtrando y corrigiendo textos..."):
            try:
                # --- PROMPT MAESTRO V5: CORRECCIÓN OCR + FILTRO DE SECCIÓN ---
                prompt_usuario = f"""
                Analiza el siguiente texto de un sílabo universitario.
                
                1. ZONA DE BÚSQUEDA (ESTRICTO):
                   - Ve DIRECTAMENTE al final del documento ("REFERENCIAS BIBLIOGRÁFICAS" o "BIBLIOGRAFÍA").
                   - IGNORA las tablas de "Programación Semanal".
                   - Solo extrae la lista final consolidada.
                   - **LINKS:** Si hay enlaces, mira la "INFO WEB" abajo. Si el link es un Libro/Manual/Paper -> ¡AGRÉGALO!

                2. CORRECCIÓN DE OCR:
                   - Repara errores: "?ujo" -> "Flujo", "Dise?o" -> "Diseño".

                3. CLASIFICACIÓN:
                   - Cuenta TODO: Libros, Revistas, Artículos, Manuales.
                   - Clasifica en: "Libro", "Revista", "Articulo", "Manual".
                   - Ignora "Basura" (Noticias, Blogs, YouTube).

                4. REGLA DE ORO - AÑOS (CRÍTICO):
                   - **EL AÑO ES OBLIGATORIO.**
                   - Si el PDF no tiene el año (o dice s.f.), **USA TU CONOCIMIENTO INTERNO** para poner el año de publicación real de la edición más conocida.
                   - **PROHIBIDO** poner "Sin especificar", "s.f." o "Indeterminado" en libros conocidos. ¡Invéntalo basándote en la realidad si hace falta!
                   - (La Ciudad sí puede quedar como "No indicada" si no la sabes).

                5. REGLAS DE EXTRACCIÓN:
                   - Excluye editoriales de periódicos (El Comercio, La República).

                TEXTO DEL PDF (OCR Sucio):
                {texto_pdf}

                INFO WEB:
                {contexto_web}

                SALIDA JSON OBLIGATORIA:
                [
                    {{
                        "Titulo": "Título Corregido",
                        "Autor": "Autor",
                        "Editorial": "Editorial",
                        "Ciudad": "Ciudad (Opcional)",
                        "Anio": "AAAA (¡Rellénalo siempre!)",
                        "Tipo": "Libro/Revista/Articulo/Manual"
                    }}
                ]
                """

                chat_completion = client.chat.completions.create(
                    messages=[
                        # Le damos permiso explícito en el sistema para "usar su conocimiento"
                        {"role": "system", "content": "Eres un Bibliotecario Experto que siempre completa los datos bibliográficos faltantes (especialmente el año) usando su enciclopedia interna."},
                        {"role": "user", "content": prompt_usuario}
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.2 # Subimos un poquito la temperatura para que se atreva a "recordar" fechas
                )
                
                datos = extraer_json_seguro(chat_completion.choices[0].message.content)
                
                if datos:
                    datos_unicos = {v['Titulo']: v for v in datos}.values()
                    datos = list(datos_unicos)

                st.session_state.archivo_procesado = file_id
                st.session_state.datos_libros = datos
                st.session_state.img_preview = img_preview
                
            except Exception as e:
                st.error(f"Error: {e}")
                st.session_state.datos_libros = []

    # --- VISUALIZACIÓN ---
    datos = st.session_state.datos_libros
    img_preview = st.session_state.img_preview
    
    # Filtro: Contamos todo, mostramos solo libros/manuales
    total_referencias = len(datos) if datos else 0
    libros_para_mostrar = [
        d for d in datos 
        if d.get('Tipo') in ['Libro', 'Libro Digital', 'Manual'] 
    ] if datos else []
    
    c1, c2 = st.columns([1.5, 3.5])
    with c1:
        st.markdown("### 📊 Resumen")
        if datos:
            st.metric("Total Referencias Detectadas", total_referencias)
            st.caption(f"Mostrando {len(libros_para_mostrar)} libros para copiar")
        if img_preview: st.image(img_preview, caption="Portada", use_container_width=True)
    
    with c2:
        st.markdown("### 📚 Libros para Copiar")
        if libros_para_mostrar:
            for libro in libros_para_mostrar:
                with st.container(border=True):
                    st.caption(f"TÍTULO ({libro.get('Tipo', 'Ref')})")
                    st.code(libro.get('Titulo', '---'), language=None)
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.caption("AUTOR"); st.code(libro.get('Autor', '---'), language=None)
                        st.caption("EDITORIAL"); st.code(libro.get('Editorial', '---'), language=None)
                    with col_b:
                        st.caption("AÑO"); st.code(libro.get('Anio', '---'), language=None)
                        st.caption("CIUDAD"); st.code(libro.get('Ciudad', '---'), language=None)
        elif st.session_state.archivo_procesado == file_id:
            st.warning("No se encontraron Libros. (Revisa si solo hay artículos o enlaces web).")

else:
    st.session_state.archivo_procesado = None
    placeholder_boton.empty()
    st.info("👆 Sube un archivo para comenzar")