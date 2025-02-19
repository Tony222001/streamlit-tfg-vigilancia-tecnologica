import streamlit as st
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials
import requests

# 🔹 Configurar API de Google Gemini
genai.configure(api_key="TU_NUEVA_CLAVE_API")  # Reemplaza con tu clave de Gemini API

# 🔹 Conectar con Google Sheets
CREDENTIALS_FILE = "gen-lang-client-0677919845-cf9abf99fc8a.json"  # Asegúrate de subir este archivo también
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
gc = gspread.authorize(creds)
spreadsheet = gc.open("TFG_Vigilancia_Tecnológica")
sheet = spreadsheet.sheet1

# 🔹 Función para buscar artículos en PubMed
def obtener_articulos_pubmed(query, max_results=3):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&retmax={max_results}&retmode=json"
    response = requests.get(url)
    data = response.json()
    article_ids = data.get("esearchresult", {}).get("idlist", [])

    articles = []
    for article_id in article_ids:
        summary_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={article_id}&retmode=json"
        summary_response = requests.get(summary_url)
        summary_data = summary_response.json()
        article_info = summary_data.get("result", {}).get(article_id, {})

        title = article_info.get("title", "Título no disponible")
        pub_date = article_info.get("pubdate", "Fecha no disponible")
        source = article_info.get("source", "Fuente no disponible")

        articles.append({"Fecha": pub_date, "Título": title, "Fuente": source, "Tipo": "PubMed"})
    
    return articles

# 🔹 Función para resumir texto con Google Gemini
def resumir_texto(texto):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(f"Resume este texto en 3 líneas: {texto}")
    return response.text if response else "Resumen no disponible"

# 🔹 Interfaz de la Aplicación Web con Streamlit
st.title("📚 Búsqueda de Estudios Científicos con IA")
st.markdown("🔍 Escribe un tema para buscar estudios científicos y obtener resúmenes con inteligencia artificial.")

query = st.text_input("Tema de búsqueda:", "Artificial Intelligence in Medicine")

if st.button("Buscar y Guardar en Google Sheets"):
    with st.spinner("Buscando estudios..."):
        articulos_pubmed = obtener_articulos_pubmed(query, max_results=3)

        for art in articulos_pubmed:
            resumen = resumir_texto(art["Título"])
            sheet.append_row([art["Fecha"], art["Título"], resumen, art["Fuente"], "PubMed"])

        st.success("✅ Datos guardados en Google Sheets correctamente!")

# 🔹 Mostrar los últimos datos guardados en Google Sheets
st.subheader("📊 Últimos estudios guardados en Google Sheets")
datos = sheet.get_all_values()
st.table(datos[-5:])  # Muestra los últimos 5 registros
