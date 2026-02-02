<div align="center">

# ⚡ Biblio-Groq
### Extractor Inteligente de Referencias Bibliográficas

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Groq](https://img.shields.io/badge/AI-Groq%20Llama%203-f55036?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)

<br>

**Una herramienta de escritorio moderna que utiliza Inteligencia Artificial para extraer, limpiar y estructurar bibliografía académica desde archivos PDF.**

[English](#-english-version) | [Español](#-versión-en-español)

</div>

---

## 🇺🇸 English Version

**Biblio-Groq** is a desktop application designed to solve a common academic problem: extracting messy bibliographic references from syllabi (PDFs). It combines the speed of **Groq** with the reasoning of **Llama 3.3** to detect, correct OCR errors, and format references into clean JSON data.

### 🚀 Key Features

* **🧠 Advanced AI Engine:** Powered by **Llama 3.3 70B (via Groq)** for deep semantic understanding.
* **✨ OCR Correction:** Automatically fixes scanning errors (e.g., converts `?ujo` to `Flujo`).
* **🖥️ Native Experience:** Packaged with **PyWebView** to run as a standalone Windows app (no browser UI).
* **🔒 Security First:** Your API Key is never stored in the source code. It uses a secure session login.
* **🛡️ Smart Filtering:** Ignores irrelevant content like "APA Guidelines" tables and focuses only on the actual bibliography.
* **👁️ Built-in PDF Viewer:** Inspect the original document without leaving the app.

### 🛠️ Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Language** | Python 3.10 | Core logic |
| **Frontend** | Streamlit | UI & State Management |
| **AI Inference** | Groq API | Ultra-low latency Llama 3 access |
| **PDF Engine** | PyMuPDF (Fitz) | High-performance PDF parsing |
| **Desktop Wrapper** | PyWebView | Native window container |
| **Build Tool** | PyInstaller | Compilation to `.exe` |

---

## 🇪🇸 Versión en Español

**Biblio-Groq** es una aplicación de escritorio diseñada para resolver un problema académico común: extraer referencias bibliográficas desordenadas de sílabos (PDFs). Combina la velocidad de **Groq** con el razonamiento de **Llama 3.3** para detectar, corregir errores de OCR y formatear las referencias en datos JSON limpios.

### 🚀 Características Principales

* **🧠 Motor de IA Avanzado:** Impulsado por **Llama 3.3 70B (vía Groq)** para una comprensión semántica profunda.
* **✨ Corrección de OCR:** Corrige automáticamente errores de escaneo (ej: convierte `?ujo` en `Flujo`).
* **🖥️ Experiencia Nativa:** Empaquetado con **PyWebView** para ejecutarse como una app independiente de Windows (sin barra de navegador).
* **🔒 Seguridad Ante Todo:** Tu API Key nunca se guarda en el código fuente. Utiliza un inicio de sesión de sesión segura.
* **🛡️ Filtros Inteligentes:** Ignora contenido irrelevante como tablas de "Normas APA" y se enfoca solo en la bibliografía real.
* **👁️ Visor PDF Integrado:** Inspecciona el documento original sin salir de la aplicación.

### 🛠️ Tecnologías Usadas

```python
# Resumen Técnico
Frontend  = "Streamlit"
AI_Model  = "Llama-3.3-70b-versatile (Groq)"
PDF_Tools = "PyMuPDF"
Desktop   = "PyWebView + PyInstaller"
<div align="center">

📥 Installation / Instalación
Clone the repository and install dependencies:
git clone [https://github.com/Gymber1/Gymber1-Biblioteca-Groq-App.git](https://github.com/Gymber1/Gymber1-Biblioteca-Groq-App.git)
cd Gymber1-Biblioteca-Groq-App
pip install -r requirements.txt
Run the app locally:
streamlit run app.py
</div>
