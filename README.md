⚡ Biblio-Groq: AI-Powered Reference Extractor
A modern desktop application designed to automatically extract, fix, and format bibliographic references from academic syllabi (PDFs). Powered by the speed of Groq and the intelligence of Llama 3.

🚀 Key Features
Advanced AI Engine: Utilizes Llama 3.3 70B (via Groq) for deep semantic analysis and precise extraction.

OCR Correction: Intelligent detection and repair of OCR scanning errors (e.g., fixing broken characters or misspellings).

Native Desktop Experience: Wrapped with PyWebView to run as a standalone Windows application (no browser toolbar).

Interactive Dashboard: Modern UI built with Streamlit, featuring dark mode, result cards, and one-click copy functionality.

Integrated PDF Viewer: Built-in modal viewer to inspect the original document without leaving the app.

Security First: Secure API Key management. Credentials are never hardcoded; they are requested at runtime via a secure session login.

Smart Filtering: Logical algorithms to ignore table contents or irrelevant mentions (like "APA Style" headers) and focus strictly on the bibliography section.

🛠️ Tech Stack
Python 3.10+

Streamlit: Reactive Frontend framework.

Groq API: Ultra-low latency AI inference.

PyMuPDF (Fitz): PDF processing and rendering.

PyInstaller & PyWebView: Executable compilation (.exe) and native window encapsulation.


⚡ Biblio-Groq: Extractor Inteligente de Referencias
Una aplicación de escritorio moderna diseñada para extraer, corregir y formatear automáticamente referencias bibliográficas desde sílabos académicos en formato PDF. Potenciada por la velocidad de Groq y la inteligencia de Llama 3.

🚀 Características Principales
Motor de IA Avanzado: Utiliza Llama 3.3 70B (via Groq) para un análisis semántico profundo y extracción precisa.

Corrección de OCR: Capacidad para detectar y reparar errores de escritura comunes en PDFs escaneados (ej: corregir "?ujo" por "Flujo").

Interfaz Nativa (Desktop): Empaquetado con PyWebView para ofrecer una experiencia de programa de escritorio independiente (sin barra de navegador).

Dashboard Interactivo: Interfaz gráfica construida con Streamlit, con modo oscuro, tarjetas de resultados y botones de copiado rápido.

Visor PDF Integrado: Permite visualizar el documento original dentro de la aplicación mediante ventanas modales sin salir del flujo de trabajo.

Seguridad Primero: Gestión segura de API Keys. La clave no se almacena en el código fuente; se solicita al usuario en tiempo de ejecución mediante una sesión encriptada.

Filtros Inteligentes: Algoritmos lógicos para ignorar tablas de contenido o menciones irrelevantes (como "Normas APA") y centrarse solo en la bibliografía real.

🛠️ Tecnologías Usadas
Python 3.10+

Streamlit: Frontend reactivo.

Groq API: Inferencia de IA de ultra-baja latencia.

PyMuPDF (Fitz): Procesamiento y lectura de archivos PDF.

PyInstaller & PyWebView: Compilación a ejecutable (.exe) y encapsulamiento en ventana nativa de Windows.
