import streamlit as st
from app.recommender import WorkoutRecommender
from collections import Counter
from fpdf import FPDF

st.title("AI Workout Recommender")

recommender = WorkoutRecommender()
session_key = "saved_workouts"
progress_key = "workout_progress"

if session_key not in st.session_state:
    st.session_state[session_key] = []

if progress_key not in st.session_state:
    st.session_state[progress_key] = {}

body_part = st.sidebar.selectbox("Select Body Part", [None] + sorted(recommender.df["BodyPart"].dropna().unique().tolist()))
difficulty = st.sidebar.selectbox("Select Difficulty", [None] + sorted(recommender.df["Level"].dropna().unique().tolist()))
equipment = st.sidebar.selectbox("Select Equipment", [None] + sorted(recommender.df["Equipment"].dropna().unique().tolist()))
workout_type = st.sidebar.selectbox("Select Workout Type", [None] + sorted(recommender.df["Type"].dropna().unique().tolist()))

if body_part or difficulty or equipment or workout_type:
    workouts = recommender.get_recommendations(body_part, difficulty, equipment, workout_type)
    st.subheader("Recommended Workouts")
    for index, workout in enumerate(workouts):
        with st.expander(f"{workout['Title']}"):
            st.write(f"- Type: {workout['Type']}")
            st.write(f"- Body Part: {workout['BodyPart']}")
            st.write(f"- Equipment: {workout['Equipment']}")
            st.write(f"- Difficulty: {workout['Level']}")
            st.write(f"- Description: {workout['Desc'] if workout['Desc'] else 'No description available'}")
            
            if st.button(f"Save {workout['Title']}", key=f"save_{workout['Title']}_{index}"):
                if workout not in st.session_state[session_key]:
                    st.session_state[session_key].append(workout)
                    st.rerun()
            
            if st.button(f"Mark Completed {workout['Title']}", key=f"complete_{workout['Title']}_{index}"):
                st.session_state[progress_key][workout['Title']] = st.session_state[progress_key].get(workout['Title'], 0) + 1
                st.rerun()

st.sidebar.subheader("Saved Workouts")
with st.sidebar.expander("Saved Workouts", expanded=True):
    search_query = st.text_input("Search Saved Workouts")
    filtered_saved_workouts = [w for w in st.session_state[session_key] if search_query.lower() in w["Title"].lower()]
    
    if not filtered_saved_workouts:
        st.write("No saved workouts found.")
    else:
        for saved_workout in filtered_saved_workouts:
            st.markdown(f"**{saved_workout['Title']}**")
            st.write(f"- Type: {saved_workout['Type']}")
            st.write(f"- Body Part: {saved_workout['BodyPart']}")
            st.write(f"- Equipment: {saved_workout['Equipment']}")
            st.write(f"- Difficulty: {saved_workout['Level']}")
            st.write(f"- Description: {saved_workout['Desc'] if saved_workout['Desc'] else 'No description available'}")

    if st.sidebar.button("Clear All Saved Workouts"):
        st.session_state[session_key] = []
        st.rerun()

st.subheader("Workout Progress Tracker")
if st.session_state[progress_key]:
    for workout, count in st.session_state[progress_key].items():
        st.write(f"{workout}: Completed {count} times")
else:
    st.write("No workouts completed yet.")

def generate_pdf(workouts):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, "Recommended Workouts", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    
    for workout in workouts:
        pdf.cell(0, 10, workout['Title'], ln=True, align='L')
        pdf.set_font("Arial", style='I', size=10)
        pdf.cell(0, 6, f"Type: {workout['Type']} | Body Part: {workout['BodyPart']} | Equipment: {workout['Equipment']} | Difficulty: {workout['Level']}", ln=True, align='L')
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 6, f"Description: {workout['Desc'] if workout['Desc'] else 'No description available'}")
        pdf.ln(5)
    
    return pdf.output(dest='S').encode('latin1')

st.subheader("Recommended for You")
if st.session_state[session_key]:
    saved_body_parts = [w["BodyPart"] for w in st.session_state[session_key]]
    saved_difficulties = [w["Level"] for w in st.session_state[session_key]]
    saved_equipment = [w["Equipment"] for w in st.session_state[session_key]]
    
    most_common_body_part = Counter(saved_body_parts).most_common(1)[0][0] if saved_body_parts else None
    most_common_difficulty = Counter(saved_difficulties).most_common(1)[0][0] if saved_difficulties else None
    most_common_equipment = Counter(saved_equipment).most_common(1)[0][0] if saved_equipment else None
    
    recommended_workouts = recommender.get_recommendations(most_common_body_part, most_common_difficulty, most_common_equipment, None)
    
    for workout in recommended_workouts[:5]:
        st.markdown(f"**{workout['Title']}**")
        st.write(f"- Type: {workout['Type']}")
        st.write(f"- Body Part: {workout['BodyPart']}")
        st.write(f"- Equipment: {workout['Equipment']}")
        st.write(f"- Difficulty: {workout['Level']}")
        st.write(f"- Description: {workout['Desc'] if workout['Desc'] else 'No description available'}")
    
    if st.button("Download Recommended Workouts as PDF"):
        pdf_content = generate_pdf(recommended_workouts[:5])
        st.download_button(label="Download PDF", data=pdf_content, file_name="recommended_for_you.pdf", mime="application/pdf")
else:
    st.write("Save workouts to get personalized recommendations!")
