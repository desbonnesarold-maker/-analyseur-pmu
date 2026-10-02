python
import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai
import pandas as pd

# Configuration de la page
st.set_page_config(page_title="IA Analyseur PMU - Geny Courses", layout="wide")
st.title("🏇 Analyseur Hippique Universel & Pronostic 5/5")
st.write("Collez le lien de n'importe quelle course Geny Courses pour extraire les données et obtenir l'analyse de l'IA.")

# Clé API OpenAI (Sécurisée via l'interface)
api_key = st.sidebar.text_input("Entrez votre clé API OpenAI (GPT-4o)", type="password")

# Saisie de l'URL par l'utilisateur
url_course = st.text_input("Lien de la course Geny Courses :", placeholder="https://geny.com...")

def extraire_donnees_geny(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None, "Impossible d'accéder à la page (Erreur HTTP)."
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Extraction des conditions de la course
        infos_course = ""
        comm_section = soup.find('div', class_='comm_course')
        if comm_section:
            infos_course = comm_section.get_text(separator=" ", strip=True)
        else:
            header_course = soup.find('h1')
            if header_course: infos_course = header_course.text
            
        # 2. Extraction du tableau des partants
        tableau = soup.find('table', class_='table-partants') or soup.find('table')
        if not tableau:
            return None, "Aucun tableau de partants trouvé sur cette page."
            
        lignes = tableau.find_all('tr')
        liste_partants = []
        
        for ligne in lignes[1:]: # On saute l'en-tête
            colonnes = [td.get_text(strip=True) for td in ligne.find_all(['td', 'th'])]
            if len(colonnes) >= 5:
                liste_partants.append(colonnes)
                
        return {"conditions": infos_course, "partants": liste_partants}, None
    except Exception as e:
        return None, f"Erreur lors du scraping : {str(e)}"

if st.button("🚀 Analyser la course") and url_course:
    if not api_key:
        st.error("Veuillez entrer votre clé API OpenAI dans la barre latérale pour activer le cerveau de l'IA.")
    else:
        with st.spinner("Extraction de toutes les données de Geny Courses en cours..."):
            donnees, erreur = extraire_donnees_geny(url_course)
            
        if erreur:
            st.error(erreur)
        else:
            st.success("Données récupérées avec succès !")
            
            # Affichage des données brutes récoltées pour transparence
            st.subheader("📊 Données brutes de la course")
            st.write(f"**Conditions de course détectées :** {donnees['conditions']}")
            
            df = pd.DataFrame(donnees['partants'])
            st.dataframe(df)
            
            # Préparation du prompt pour ChatGPT
            prompt_analyse = f"""
            Tu es le meilleur expert mondial en pronostics hippiques (PMU). Ton objectif est de sortir un pronostic théorique 5/5 (Quinté) hautement optimisé en te basant sur les données brutes suivantes issues de Geny Courses.
            
            CONDITIONS DE LA COURSE :
            {donnees['conditions']}
            
            TABLEAU DES PARTANTS (Colonnes brutes : N°, Cheval, Jockey, Entraîneur, Musique, Cotes/Poids selon la course) :
            {df.to_string()}
            
            INSTRUCTIONS SPECIFIQUES D'ANALYSE :
            1. Analyse la musique de chaque cheval (les performances récentes, les disciplines attelé/monté/obstacle, les disqualifications 'Dai').
            2. Évalue la qualité des couples Jockey/Entraîneur si l'information est marquante.
            3. Prends en compte les conditions de la course (distance, allocation, âge) face aux profils.
            4. Détecte les favoris logiques et repère 1 ou 2 outsiders spéculatifs (les "tocs") pour maximiser les gains du 5/5.
            
            FORMAT DE RÉPONSE ATTENDU :
            - ** Synthèse de la course ** (En 2 phrases : profil de la course, pièges à éviter).
            - ** Le Pronostic 5/5 (Incontournables au moins probables) ** : Liste claire des 5 numéros sélectionnés + 2 chevaux de complément.
            - ** L'analyse rapide par cheval sélectionné ** : Pourquoi ce cheval fait partie des 5.
            - ** Indice de confiance ** : Note sur 10.
            """
            
            with st.spinner("ChatGPT analyse le tableau et prépare votre 5/5..."):
                try:
                    client = openai.OpenAI(api_key=api_key)
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": prompt_analyse}],
                        temperature=0.3
                    )
                    
                    st.subheader("🔮 Analyse de l'IA & Sélection 5/5")
                    st.markdown(response.choices.message.content)
                    
                except Exception as e:
                    st.error(f"Erreur avec l'API OpenAI : {str(e)}")
