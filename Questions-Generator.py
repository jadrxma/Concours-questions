import streamlit as st
import openai
import json
import random

# Inject CSS for enhanced styling and Streamlit branding removal
st.markdown(
    """
    <style>
        /* Hide the Streamlit footer and badges */
        footer {visibility: hidden; }
        .viewerBadge_container__1QSob { display: none !important; } /* Streamlit watermark */
        .st-emotion-cache-1v0mbdj { display: none !important; } /* Remove 'Created by' badges */
        header { visibility: hidden; } /* Hide Streamlit header */
    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <style>
    /* General Page Styling - Light Mode Only */
    body {
        color: #333333;
        background-color: #F7F9FC !important;
    }

    /* Title Styling */
    .stApp h1 {
        color: #4A6FA5;
        text-align: center;
        font-size: 3em;
        text-shadow: 1px 1px 2px #b8cbe3;
    }

    /* Buttons Styling */
    .stButton > button {
        background-color: #4A6FA5 !important;
        color: white !important;
        border-radius: 8px;
        box-shadow: 2px 2px 5px #a0b5d8 !important;
        font-size: 1.1em;
        font-weight: bold;
        padding: 0.6em 1.5em;
    }
    .stButton > button:hover {
        background-color: #3D5A80 !important;
    }

    /* Radio Button Styling */
    .stRadio label {
        font-size: 1.1em;
        color: #3D5A80;
        margin-left: 10px;
    }

    /* Remove Streamlit Branding */
    footer {visibility: hidden;}
    .viewerBadge_container__1QSob {display: none;}
    header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# Configure your OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Streamlit Application
st.title("🩺 Générateur de Questions Diagnostiques Médicales")

# Move "Paramètres" to Main Page
st.header("⚙️ Paramètres")
niveau_difficulte = st.selectbox(
    "Sélectionnez le niveau de difficulté :",
    ["Facile", "Modéré", "Difficile", "Extrême"]
)
st.markdown(
    """
    <style>
        /* Hide Streamlit branding elements */
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .viewerBadge_container__1QSob {display: none;} /* Streamlit watermark */
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state to persist data
if "question_data" not in st.session_state:
    st.session_state["question_data"] = None
if "selected_option" not in st.session_state:
    st.session_state["selected_option"] = None

# Generate a diagnostic question
if st.button("🔍 Générer une question"):
    with st.spinner("Génération de la question en cours..."):
        prompt = (
            f"Générez une question diagnostique médicale de niveau {niveau_difficulte.lower()} sous format JSON. "
            "Le format de sortie doit uniquement être en JSON (Don't include '''json ''' avec les clés suivantes: 'question', 'options' (liste), et 'correct_answer'. "
            "Assurez-vous que la bonne réponse est aléatoirement choisie parmi les options."
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

            question_json_str = response["choices"][0]["message"]["content"].strip()
            question_data = json.loads(question_json_str)

            # Randomize correct answer
            if "options" in question_data and question_data["options"]:
                question_data["correct_answer"] = random.choice(question_data["options"])

            st.session_state["question_data"] = question_data

        except json.JSONDecodeError:
            st.error("Le format de la réponse n'est pas un JSON valide. Veuillez réessayer.")
        except Exception as e:
            st.error(f"Une erreur s'est produite : {e}")

# Display the question and difficulty
if st.session_state["question_data"]:
    st.markdown(f"### **Niveau de Difficulté : {niveau_difficulte}**")
    question_data = st.session_state["question_data"]
    st.markdown(f"### **{question_data['question']}**")

    options = question_data.get("options", [])
    correct_answer = question_data.get("correct_answer", None)

    if options:
        st.session_state["selected_option"] = st.radio(
            "Choisissez votre réponse :",
            options,
            index=options.index(st.session_state["selected_option"]) if st.session_state["selected_option"] in options else 0,
        )

        if st.button("✅ Valider votre réponse"):
            if correct_answer and st.session_state["selected_option"] == correct_answer:
                st.success("🎉 Bonne réponse !")
            else:
                st.error(f"❌ Mauvaise réponse. La bonne réponse est : {correct_answer}")
    else:
        st.warning("Aucune option trouvée dans la question générée. Veuillez réessayer.")

# Footer
st.markdown("---")
st.markdown("💡 *Améliorez vos compétences diagnostiques avec des questions adaptées à votre niveau.*")
