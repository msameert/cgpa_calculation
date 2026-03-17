import base64
import json
import os
from datetime import datetime

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, get_app

# Initialize Firebase (only once)
try:
    get_app()  # Check if already initialized
except ValueError:
    # Not initialized, so initialize
    try:
        # Try to get from Streamlit secrets (base64 encoded JSON)
        cred_b64 = st.secrets["FIREBASE_SERVICE_ACCOUNT_B64"]
        cred_json = base64.b64decode(cred_b64).decode('utf-8')
        cred_dict = json.loads(cred_json)
        cred = credentials.Certificate(cred_dict)
    except json.JSONDecodeError as e:
        st.error(f"Invalid Firebase JSON in secrets. Error: {str(e)}. Please check the base64 encoded JSON.")
        st.stop()
    except (KeyError, FileNotFoundError):
        # Fallback for local development: use serviceAccountKey.json
        if os.path.exists("serviceAccountKey.json"):
            cred = credentials.Certificate("serviceAccountKey.json")
        else:
            st.error("Firebase credentials not found. Please add serviceAccountKey.json for local development or set FIREBASE_SERVICE_ACCOUNT_B64 in secrets.")
            st.stop()
    firebase_admin.initialize_app(cred)

db = firestore.client()


def get_grades(score: float) -> str:
    """Return the letter grade for a numeric score."""

    if score >= 85:
        return "A"
    elif score >= 80:
        return "A-"
    elif score >= 75:
        return "B+"
    elif score >= 71:
        return "B"
    elif score >= 68:
        return "B-"
    elif score >= 64:
        return "C+"
    elif score >= 61:
        return "C"
    elif score >= 58:
        return "C-"
    elif score >= 54:
        return "D+"
    elif score >= 50:
        return "D"
    else:
        return "F"


GRADE_POINTS = {
    "A": 4.0,
    "A-": 3.66,
    "B+": 3.33,
    "B": 3.00,
    "B-": 2.66,
    "C+": 2.33,
    "C": 2.00,
    "C-": 1.66,
    "D+": 1.33,
    "D": 1.00,
    "F": 0.00,
}


COURSES = [
    {"name": "OOP", "credits": 3},
    {"name": "Database", "credits": 3},
    {"name": "Linear Algebra", "credits": 3},
    {"name": "Computer Network", "credits": 2},
    {"name": "Digital Logic Design", "credits": 2},
]

LABS = [
    {"name": "OOP Lab", "credits": 1},
    {"name": "Database Lab", "credits": 1},
    {"name": "Computer Network Lab", "credits": 1},
    {"name": "Digital Logic Design Lab", "credits": 1},
]


def load_history() -> list[dict]:
    try:
        docs = db.collection("cgpa_history").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(100).stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        st.error(f"Error loading history: {e}")
        return []


def save_history(entry: dict) -> None:
    try:
        db.collection("cgpa_history").add(entry)
    except Exception as e:
        st.error(f"Error saving history: {e}")


def calculate_semester_gpa(entries: list[dict]) -> tuple[float, float]:
    total_points = 0.0
    total_credits = 0.0

    for entry in entries:
        grade = entry["grade"]
        credits = entry["credits"]
        gp = GRADE_POINTS.get(grade, 0.0)
        total_points += gp * credits
        total_credits += credits

    if total_credits == 0:
        return 0.0, 0.0
    return total_points / total_credits, total_credits


def format_semester_table(entries: list[dict]) -> list[dict]:
    return [
        {
            "Course": e["name"],
            "Score": e["score"],
            "Grade": e["grade"],
            "GP": GRADE_POINTS.get(e["grade"], 0.0),
            "Credits": e["credits"],
            "Points": round(GRADE_POINTS.get(e["grade"], 0.0) * e["credits"], 3),
        }
        for e in entries
    ]


def build_entry_row(
    student_name: str,
    first_sem_gpa: float,
    first_sem_credits: float,
    second_sem_entries: list[dict],
    second_sem_gpa: float,
    second_sem_credits: float,
    cgpa: float,
) -> dict:
    return {
        "student_name": student_name.strip(),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "first_sem_gpa": round(first_sem_gpa, 3),
        "first_sem_credits": round(first_sem_credits, 2),
        "second_sem_gpa": round(second_sem_gpa, 3),
        "second_sem_credits": round(second_sem_credits, 2),
        "cgpa": round(cgpa, 3),
        "second_sem_details": second_sem_entries,
    }


def main() -> None:
    st.set_page_config(
        page_title="2nd Semester CGPA Calculator",
        page_icon="🎓",
        layout="wide",
    )

    st.title("2nd Semester CGPA Calculator")

    st.markdown(
        """
        This tool calculates your 2nd semester GPA (based on course scores) and then computes your overall CGPA by combining it with a provided 1st-semester GPA.

        - Enter your **1st semester GPA** and the **credits** it was based on (MAKE it to 16).
        - Enter your **scores for 2nd semester courses**.
        - Click **Calculate** to see the GPA and your updated CGPA.

        Your name is compulsory.
        """
    )

    with st.form("input_form"):
        st.subheader("👤 Student Information")
        student_name = st.text_input(
            "Your Name",
            placeholder="Enter your full name",
            max_chars=100,
            help="This is required.",
        )

        st.subheader("1️⃣ First Semester")
        col1, col2 = st.columns(2)
        with col1:
            first_sem_gpa = st.number_input(
                "Your 1st Semester GPA",
                min_value=0.0,
                max_value=4.0,
                value=0.0,
                step=0.01,
                help="Your CGPA/GPA from 1st semester.",
            )
        with col2:
            first_sem_credits = st.number_input(
                "1st Semester Credits ; NOTE : IT'S 16 for first semester",
                min_value=0.0,
                value=16.0,
                step=1.0,
                help="Total credit hours for the 1st semester.",
            )

        st.subheader("2️⃣ Second Semester Scores")
        st.markdown("Enter your **percentage score** for each course and lab.")

        second_sem_entries: list[dict] = []

        for course in COURSES + LABS:
            score = st.number_input(
                f"{course['name']} (credits: {course['credits']})",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.5,
                key=course["name"],
            )
            grade = get_grades(score)

            second_sem_entries.append(
                {
                    "name": course["name"],
                    "score": score,
                    "grade": grade,
                    "credits": course["credits"],
                }
            )

        calculate = st.form_submit_button("Calculate")

    if calculate:
        if not student_name.strip():
            st.error("❌ Please enter your name to proceed.")
            st.stop()

        second_sem_gpa, second_sem_credits = calculate_semester_gpa(second_sem_entries)
        if first_sem_credits + second_sem_credits == 0:
            st.error("Total credits cannot be zero.")
            return

        cgpa = (
            first_sem_gpa * first_sem_credits + second_sem_gpa * second_sem_credits
        ) / (first_sem_credits + second_sem_credits)

        st.subheader("Your Results")
        st.metric("2nd Semester GPA : ", f"{second_sem_gpa:.3f}")
        st.metric("CGPA (1st+2nd combined) : ", f"{cgpa:.3f}")

        st.markdown("2nd Semester Grade Breakdown : ")
        st.table(format_semester_table(second_sem_entries))

        history = load_history()
        entry = build_entry_row(
            student_name,
            first_sem_gpa,
            first_sem_credits,
            second_sem_entries,
            second_sem_gpa,
            second_sem_credits,
            cgpa,
        )
        save_history(entry)


if __name__ == "__main__":
    main()
