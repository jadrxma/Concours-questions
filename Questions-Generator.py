
import streamlit as st
import openai
import json

# Configurez votre clé API OpenAI depuis les secrets de Streamlit
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Application Streamlit
st.title("Générateur de Questions Diagnostiques Médicales")

# Barre latérale pour sélectionner la difficulté
st.sidebar.header("Paramètres")
niveau_difficulte = st.sidebar.selectbox(
    "Sélectionnez le niveau de difficulté :",
    ["Facile", "Modéré", "Difficile", "Extrême"]
)

# Initialize session state to persist data
if "question_data" not in st.session_state:
    st.session_state["question_data"] = None
if "selected_option" not in st.session_state:
    st.session_state["selected_option"] = None

# Générer une question diagnostique
if st.button("Générer une question"):
    with st.spinner("Génération de la question en cours..."):
        # Prompt pour générer des questions diagnostiques en format JSON
        prompt = (
            f"Générez une question diagnostique médicale de niveau {niveau_difficulte.lower()} sous format JSON."
            " Le format de sortie doit uniquement être en JSON avec les clés suivantes without including '''json ''' : 'question', 'options' (liste), et 'correct_answer'."
        )

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Vous êtes un expert en médecine qui génère des questions diagnostiques médicales."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )

            # Parse JSON response and store in session state
            st.session_state["question_data"] = json.loads(response["choices"][0]["message"]["content"].strip())

        except json.JSONDecodeError:
            st.error("Le format de la réponse n'est pas valide JSON. Veuillez réessayer.")
        except Exception as e:
            st.error(f"Une erreur s'est produite : {e}")

# Display the question and options if available
if st.session_state["question_data"]:
    question_data = st.session_state["question_data"]
    st.write(f"**{question_data['question']}**")

    options = question_data.get("options", [])
    correct_answer = question_data.get("correct_answer", None)

    if options:
        # Persist the selected option in session state
        st.session_state["selected_option"] = st.radio(
            "Choisissez votre réponse :",
            options,
            key="options_radio",
            index=options.index(st.session_state["selected_option"]) if st.session_state["selected_option"] in options else 0,
        )

        if st.button("Valider votre réponse"):
            if correct_answer and st.session_state["selected_option"] == correct_answer:
                st.success("Bonne réponse !")
            else:
                st.error(f"Mauvaise réponse. La bonne réponse est : {correct_answer}")
    else:
        st.warning("Aucune option n'a été trouvée dans la question générée. Veuillez réessayer.")

# Pied de page
st.markdown("---")

