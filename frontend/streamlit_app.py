import streamlit as st
import requests
import os
from io import BytesIO
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Heart Disease Prediction",
    page_icon="❤",
    layout="centered"
)

st.title("Heart Disease Prediction App")
st.caption("Enter patient details and predict heart disease risk.")

API_URL = "https://heart-disease-backend-76ni.onrender.com"


# -----------------------------
# PDF Generator
# -----------------------------
def generate_pdf_report(patient_name, report_dt, payload, pred, prob, risk_level):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 60, "Heart Disease Prediction Report")

    # Patient + datetime
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 90, f"Patient Name: {patient_name}")
    c.drawString(50, height - 110, f"Report Date & Time: {report_dt}")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 130, "----------------------------------------------")

    y = height - 160

    # Inputs
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "Patient Inputs:")
    y -= 25

    c.setFont("Helvetica", 12)
    for k, v in payload.items():
        c.drawString(60, y, f"{k}: {v}")
        y -= 18

        # if page ends
        if y < 80:
            c.showPage()
            y = height - 60

    y -= 10

    # Results
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "Prediction Result:")
    y -= 25

    c.setFont("Helvetica", 12)
    c.drawString(60, y, f"Model Output (0/1): {pred}")
    y -= 18
    c.drawString(60, y, f"Risk Probability: {prob:.2f}")
    y -= 18
    c.drawString(60, y, f"Risk Percentage: {prob*100:.0f}%")
    y -= 18
    c.drawString(60, y, f"Risk Level: {risk_level}")
    y -= 25

    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, y, "Note: This prediction is AI-based and not a medical diagnosis.")

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer


# -----------------------------
# Reset function
# -----------------------------
def reset_form():
    keys = [
        "patient_name",
        "age", "sex", "cp", "resting_bp", "cholesterol", "fbs", "restecg",
        "max_hr", "exang", "st_depression", "slope", "ca", "thal"
    ]
    for k in keys:
        if k in st.session_state:
            del st.session_state[k]


# -----------------------------
# Input Form
# -----------------------------
with st.form("heart_form"):

    st.subheader("Patient Details")

    patient_name = st.text_input(
        "Patient Name",
        placeholder="Enter patient full name...",
        key="patient_name"
    )

    st.subheader("Medical Inputs")

    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input("Age", 1, 120, 50, key="age")

        sex_val = st.selectbox(
            "Sex",
            [0, 1],
            format_func=lambda x: "Female (0)" if x == 0 else "Male (1)",
            key="sex"
        )

        cp_val = st.selectbox("Chest Pain Type", [0, 1, 2, 3], key="cp")

        resting_bp = st.number_input("Resting Blood Pressure", 50, 250, 120, key="resting_bp")

        cholesterol = st.number_input("Cholesterol", 50, 600, 200, key="cholesterol")

        fasting_blood_sugar = st.selectbox(
            "Fasting Blood Sugar (>120 mg/dl)",
            [0, 1],
            format_func=lambda x: "No (0)" if x == 0 else "Yes (1)",
            key="fbs"
        )

    with col2:
        resting_ecg = st.selectbox("Resting ECG", [0, 1, 2], key="restecg")

        max_heart_rate = st.number_input("Max Heart Rate Achieved", 50, 250, 150, key="max_hr")

        exercise_induced_angina = st.selectbox(
            "Exercise Induced Angina",
            [0, 1],
            format_func=lambda x: "No (0)" if x == 0 else "Yes (1)",
            key="exang"
        )

        st_depression = st.number_input(
            "ST Depression",
            min_value=0.0,
            max_value=10.0,
            value=1.0,
            step=0.1,
            key="st_depression"
        )

        st_slope = st.selectbox("ST Slope", [0, 1, 2], key="slope")

        num_major_vessels = st.selectbox("Num Major Vessels", [0, 1, 2, 3], key="ca")

        thalassemia = st.selectbox("Thalassemia", [0, 1, 2, 3], key="thal")

    colA, colB = st.columns(2)

    with colA:
        submitted = st.form_submit_button("Predict")

    with colB:
        reset = st.form_submit_button("Reset")


# -----------------------------
# Reset Action
# -----------------------------
if reset:
    reset_form()
    st.rerun()


# -----------------------------
# Prediction Action
# -----------------------------
if submitted:

    # Basic validation
    if not patient_name.strip():
        st.error("❌ Please enter Patient Name.")
        st.stop()

    payload = {
        "age": age,
        "sex": sex_val,
        "chest_pain_type": cp_val,
        "resting_bp": resting_bp,
        "cholesterol": cholesterol,
        "fasting_blood_sugar": fasting_blood_sugar,
        "resting_ecg": resting_ecg,
        "max_heart_rate": max_heart_rate,
        "exercise_induced_angina": exercise_induced_angina,
        "st_depression": st_depression,
        "st_slope": st_slope,
        "num_major_vessels": num_major_vessels,
        "thalassemia": thalassemia
    }

    try:
        response = requests.post(API_URL, json=payload, timeout=10)

        if response.status_code != 200:
            st.error(f"❌ Backend error: {response.status_code}")
            st.write(response.text)
            st.stop()

        result = response.json()

        if "prediction" not in result or "probability" not in result:
            st.error("❌ Backend response missing prediction/probability.")
            st.json(result)
            st.stop()

        pred = int(result["prediction"])
        prob = float(result["probability"])
        prob = max(0.0, min(1.0, prob))

        # Risk logic
        if prob < 0.35:
            risk_level = "LOW"
            icon = "🟢"
        elif prob < 0.70:
            risk_level = "MEDIUM"
            icon = "🟡"
        else:
            risk_level = "HIGH"
            icon = "🔴"

        report_dt = datetime.now().strftime("%d-%b-%Y  %I:%M %p")

        st.markdown("---")
        st.subheader("Result")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Model Output (0/1)", pred)
        with c2:
            st.metric("Risk Probability", f"{prob:.2f}")
        with c3:
            st.metric("Risk %", f"{prob*100:.0f}%")

        st.markdown(f"### {icon} Risk Level: **{risk_level}**")
        st.progress(prob)

        if risk_level == "HIGH":
            st.error("⚠️ High risk of heart disease detected. Please consult a doctor.")
        elif risk_level == "MEDIUM":
            st.warning("⚠️ Moderate risk. Consider medical checkup and lifestyle changes.")
        else:
            st.success("✅ Low risk. Maintain a healthy lifestyle.")

        # PDF report
        pdf_file = generate_pdf_report(
            patient_name=patient_name,
            report_dt=report_dt,
            payload=payload,
            pred=pred,
            prob=prob,
            risk_level=risk_level
        )

        st.download_button(
            label="📄 Download Report (PDF)",
            data=pdf_file,
            file_name=f"{patient_name.replace(' ', '_')}_heart_report.pdf",
            mime="application/pdf"
        )

    except Exception as e:
        st.error("❌ Backend API not reachable. Check backend is running.")
        st.code(str(e))
