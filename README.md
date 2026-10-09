# Laboratorio Interactivo de Señales — versión web

Esta versión adapta el laboratorio de Tkinter a una aplicación web para compartir mediante un enlace.

## Ejecutar localmente
1. Instala Python 3.10 o superior.
2. En la carpeta del proyecto, ejecuta:
   `pip install -r requirements.txt`
3. Inicia la aplicación:
   `streamlit run streamlit_app.py`

## Publicar gratis con Streamlit Community Cloud
1. Sube `streamlit_app.py` y `requirements.txt` a un repositorio de GitHub.
2. Entra en https://share.streamlit.io e inicia sesión con GitHub.
3. Pulsa **Create app**, elige el repositorio, la rama y `streamlit_app.py`.
4. Si quieres, define un subdominio y pulsa **Deploy**.
5. Cuando termine, copia el enlace `https://...streamlit.app` y compártelo para tu exposición.

Consulta la guía oficial: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy
