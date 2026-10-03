python
import streamlit as st
import requests
from bs4 import BeautifulSoup
from google import genai
import pandas as pd

st.set_page_config(page_title="IA Analyseur PMU - Geny Courses", layout="wide")
st.title("🏇 Analyseur Hippique Universel & Pronostic 5/5")
st.write("Collez le lien de n'importe quelle course Geny Courses pour obtenir l'analyse gratuite de l'IA.")

api_key = st.sidebar.text_input("Entrez votre clé API Google Gemini (Gratuite)", type="password")
st.sidebar.markdown("[Obtenir une clé API Gemini gratuite ici](https://google.com)")

url_course = st.text_input("Lien de la course Geny Courses :", placeholder="https://geny.com...")

def extraire_donnees_geny(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None, "Erreur de connexion au site Geny."
        soup = BeautifulSoup(response.text, 'html.parser')
        infos_course = ""
        comm_section = soup.find('div', class_='comm_course')
        if comm_section:
            infos_course = comm_section.get_text(separator=" ", strip=True)
        else:
            header_course = soup.find('h1')
            if header_course: infos_course = header_course.text
        tableau = soup.find('table', class_='table-partants') or soup.find('table')
        if not tableau:
            return None, "Aucun tableau trouvé."
        lignes = tableau.find_all('tr')
        liste_partants = []
        for ligne in lignes[1:]:
            colonnes = [td.get_text(strip=True) for td in ligne.find_all(['td', 'th'])]
            if len(colonnes) >= 5:
                liste_partants.append(colonnes)
        return {"conditions": infos_course, "partants": liste_partants}, None
    except Exception as e:
        return None, str(e)

if st.button("🚀 Analyser la course") and url_course:
    if not api_key:
        st.error("Veuillez entrer votre clé API.")
    else:
        with st.spinner("Analyse en cours..."):
            donnees, erreur = extraire_donnees_geny(url_course)
        if erreur:
            st.error(erreur)
        else:
            st.success("Données récupérées !")
            df = pd.DataFrame(donnees['partants'])
            st.dataframe(df)
            prompt_analyse = f"Tu es un expert PMU. Donne un pronostic 5/5 basé sur ces infos. Conditions: {donnees['conditions']}. Partants: {df.to_string()}"
            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_analyse)
                st.subheader("🔮 Sélection 5/5 de l'IA")
                st.write(response.text)
            except Exception as e:
                st.error(str(e))
