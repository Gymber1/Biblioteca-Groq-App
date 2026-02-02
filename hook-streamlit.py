from PyInstaller.utils.hooks import collect_all

# Esto le dice al instalador: "Llévate TODO lo que tenga que ver con streamlit"
datas, binaries, hiddenimports = collect_all('streamlit')