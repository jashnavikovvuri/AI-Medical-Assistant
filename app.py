from flask import Flask, render_template, request, redirect, url_for, send_file

import sqlite3
import os

from predict import predict_image

from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from datetime import datetime

import matplotlib.pyplot as plt


app = Flask(__name__)
# Create Profile Table
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS profile(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
age INTEGER,
gender TEXT,
blood_group TEXT,
phone TEXT,
address TEXT
)
""")
conn.commit()
conn.close()

# Add patient details columns to predictions table

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE predictions ADD COLUMN patient_name TEXT")
except sqlite3.OperationalError:
    pass

try:
    cursor.execute("ALTER TABLE predictions ADD COLUMN patient_age INTEGER")
except sqlite3.OperationalError:
    pass

try:
    cursor.execute("ALTER TABLE predictions ADD COLUMN patient_gender TEXT")
except sqlite3.OperationalError:
    pass

try:
    cursor.execute("ALTER TABLE predictions ADD COLUMN patient_id TEXT")
except sqlite3.OperationalError:
    pass

try:
    cursor.execute("ALTER TABLE predictions ADD COLUMN patient_contact TEXT")
except sqlite3.OperationalError:
    pass

conn.commit()
conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:
            return redirect(url_for('dashboard'))
        else:
            return render_template(
                "login.html",
                error="Invalid Email or Password!"
            )

    return render_template("login.html")
@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users(name, email, password) VALUES (?, ?, ?)",
            (name, email, password)
        )

        conn.commit()
        conn.close()

        return redirect(url_for('login'))

    return render_template('signup.html')
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET password=? WHERE email=?",
            (password, email)
        )

        conn.commit()
        conn.close()

        return render_template(
            "forgot_password.html",
            message="Password Updated Successfully!"
        )

    return render_template("forgot_password.html")

@app.route('/dashboard')
def dashboard():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions")
    total_predictions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT disease) FROM predictions")
    total_diseases = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        total_users=total_users,
        total_predictions=total_predictions,
        total_diseases=total_diseases
    )
@app.route('/history')
def history():

    disease = request.args.get("disease")
    date = request.args.get("date")
    confidence = request.args.get("confidence")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    query = "SELECT * FROM predictions WHERE 1=1"
    values = []

    if disease:
        query += " AND disease LIKE ?"
        values.append("%" + disease + "%")

    if date:
        query += " AND date LIKE ?"
        values.append("%" + date + "%")

    if confidence:
        query += " AND confidence LIKE ?"
        values.append("%" + confidence + "%")

    cursor.execute(query, values)

    data = cursor.fetchall()

    conn.close()

    return render_template("history.html", data=data)
@app.route('/delete_prediction/<int:id>')
def delete_prediction(id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM predictions WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for('history'))
@app.route('/profile', methods=['GET', 'POST'])
def profile():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":

        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        blood_group = request.form["blood_group"]
        phone = request.form["phone"]
        address = request.form["address"]

        cursor.execute("SELECT * FROM patient_profile")
        patient = cursor.fetchone()

        if patient:
            cursor.execute("""
            UPDATE patient_profile
            SET
                name=?,
                age=?,
                gender=?,
                blood_group=?,
                phone=?,
                address=?
            WHERE id=?
            """, (
                name,
                age,
                gender,
                blood_group,
                phone,
                address,
                patient[0]
            ))
        else:
            cursor.execute("""
            INSERT INTO patient_profile
            (name, age, gender, blood_group, phone, address)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                name,
                age,
                gender,
                blood_group,
                phone,
                address
            ))

        conn.commit()

    cursor.execute("SELECT * FROM patient_profile")
    patient = cursor.fetchone()

    conn.close()

    return render_template("profile.html", patient=patient)
@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/contact')
def contact():
    return render_template('contact.html')
@app.route('/appointment', methods=['GET', 'POST'])
def appointment():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        doctor = request.form['doctor']
        date = request.form['date']
        time = request.form['time']
        problem = request.form['problem']

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO appointments
        (name, email, doctor, date, time, problem)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (name, email, doctor, date, time, problem))

        conn.commit()
        conn.close()

        return render_template(
            "appointment.html",
            message="Appointment Booked Successfully!"
        )

    return render_template("appointment.html")
@app.route('/doctor')
def doctor():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM appointments")
    appointments = cursor.fetchall()

    conn.close()

    return render_template(
        "doctor_dashboard.html",
        appointments=appointments
    )
@app.route('/admin')
def admin():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions")
    total_predictions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM appointments")
    total_appointments = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "admin.html",
        total_users=total_users,
        total_predictions=total_predictions,
        total_appointments=total_appointments
    )
@app.route('/predict', methods=['POST'])
def predict():

    image = request.files['image']

    upload_folder = "static/uploads"
    os.makedirs(upload_folder, exist_ok=True)

    image_path = os.path.join(upload_folder, image.filename)
    image.save(image_path)

    # AI Prediction
    disease, confidence = predict_image(image_path)
    confidence = f"{confidence}%"

    # Patient Details
    patient_name = request.form.get("patient_name", "")
    patient_age = request.form.get("patient_age", "")
    patient_gender = request.form.get("patient_gender", "")
    patient_id = request.form.get("patient_id", "")
    patient_contact = request.form.get("patient_contact", "")

    # Disease Information
    details = {

        "glioma": {
            "description": "Glioma is a type of brain tumor that starts in the glial cells.",
            "precautions": "Consult a neurologist immediately. Avoid self-medication.",
            "doctor": "Neurologist / Neurosurgeon"
        },

        "meningioma": {
            "description": "Meningioma is a tumor that develops from the membranes around the brain.",
            "precautions": "Regular MRI scans and consult a neurosurgeon.",
            "doctor": "Neurosurgeon"
        },

        "pituitary": {
            "description": "Pituitary tumor develops in the pituitary gland and may affect hormone levels.",
            "precautions": "Consult an endocrinologist and neurosurgeon.",
            "doctor": "Endocrinologist / Neurosurgeon"
        },

        "notumor": {
            "description": "No brain tumor detected in the uploaded MRI image.",
            "precautions": "Maintain a healthy lifestyle and attend regular checkups if needed.",
            "doctor": "General Physician"
        }
    }

    info = details[disease]

    # Save Prediction
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    current_date = datetime.now().strftime("%d-%m-%Y %H:%M")

    cursor.execute(
        """INSERT INTO predictions
        (image, disease, confidence, date,
         patient_name, patient_age, patient_gender,
         patient_id, patient_contact)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            image.filename,
            disease,
            confidence,
            current_date,
            patient_name,
            patient_age,
            patient_gender,
            patient_id,
            patient_contact
        )
    )

    conn.commit()

    # Dashboard Statistics

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions")
    total_predictions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT disease) FROM predictions")
    total_diseases = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        filename=image.filename,
        disease=disease,
        confidence=confidence,
        description=info["description"],
        precautions=info["precautions"],
        doctor=info["doctor"],
        patient_name=patient_name,
        patient_age=patient_age,
        patient_gender=patient_gender,
        patient_id=patient_id,
        patient_contact=patient_contact,
        total_users=total_users,
        total_predictions=total_predictions,
        total_diseases=total_diseases
    )
@app.route('/download_report')
def download_report():

    os.makedirs("reports", exist_ok=True)

    pdf_path = "reports/medical_report.pdf"

    # Connect Database
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT disease, confidence,
               patient_name, patient_age,
               patient_gender, patient_id,
               patient_contact, image
        FROM predictions
        ORDER BY id DESC
        LIMIT 1
    """)

    result = cursor.fetchone()
    conn.close()

    if result:
        disease = result[0]
        confidence = result[1]
        patient_name = result[2]
        patient_age = result[3]
        patient_gender = result[4]
        patient_id = result[5]
        patient_contact = result[6]
        image_name = result[7]

    else:
        disease = "No Prediction"
        confidence = "N/A"
        patient_name = "N/A"
        patient_age = "N/A"
        patient_gender = "N/A"
        patient_id = "N/A"
        patient_contact = "N/A"
        image_name = None

    # Disease Details
    details = {
        "glioma": {
            "doctor": "Neurologist / Neurosurgeon",
            "precautions": "Consult a neurologist immediately."
        },

        "meningioma": {
            "doctor": "Neurosurgeon",
            "precautions": "Regular MRI scans and consult a neurosurgeon."
        },

        "pituitary": {
            "doctor": "Endocrinologist / Neurosurgeon",
            "precautions": "Consult an endocrinologist."
        },

        "notumor": {
            "doctor": "General Physician",
            "precautions": "Maintain a healthy lifestyle."
        }
    }

    doctor = details.get(disease, {}).get("doctor", "N/A")
    precautions = details.get(disease, {}).get("precautions", "N/A")

    # Create PDF
    c = canvas.Canvas(pdf_path)

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawString(120, 800, "AI Medical Diagnosis Report")

    # Patient Details
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 765, "Patient Details")

    c.setFont("Helvetica", 12)

    c.drawString(50, 740, f"Patient Name : {patient_name}")
    c.drawString(50, 720, f"Patient ID : {patient_id}")
    c.drawString(50, 700, f"Age : {patient_age}")
    c.drawString(50, 680, f"Gender : {patient_gender}")
    c.drawString(50, 660, f"Contact : {patient_contact}")

    # MRI Image
    if image_name:

        image_path = os.path.join(
            "static",
            "uploads",
            image_name
        )

        if os.path.exists(image_path):

            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, 625, "MRI Scan")

            img = ImageReader(image_path)

            c.drawImage(
                img,
                50,
                390,
                width=250,
                height=210,
                preserveAspectRatio=True,
                mask="auto"
            )

    # Prediction Result
    c.setFont("Helvetica-Bold", 14)
    c.drawString(350, 625, "Prediction Result")

    c.setFont("Helvetica", 12)

    c.drawString(350, 595, f"Disease : {disease}")
    c.drawString(350, 570, f"Confidence : {confidence}")
    c.drawString(350, 545, f"Doctor : {doctor}")
    c.drawString(350, 520, f"Precautions : {precautions}")

    # Footer
    c.setFont("Helvetica-Oblique", 10)

    c.drawString(
        50,
        80,
        "AI Medical Assistant - AI based prediction report"
    )

    c.drawString(
        50,
        60,
        "This report is for assistance only. Consult a qualified medical professional."
    )

    c.save()

    return send_file(
        pdf_path,
        as_attachment=True
    )


@app.route('/analytics')
def analytics():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT disease, COUNT(*)
        FROM predictions
        GROUP BY disease
    """)

    data = cursor.fetchall()

    conn.close()

    diseases = [row[0] for row in data]
    counts = [row[1] for row in data]

    plt.figure(figsize=(6, 6))

    plt.pie(
        counts,
        labels=diseases,
        autopct="%1.1f%%",
        startangle=90
    )

    plt.title("Disease Prediction Analytics")

    os.makedirs("static/charts", exist_ok=True)

    chart_path = "static/charts/pie_chart.png"

    plt.savefig(chart_path)
    plt.close()

    return render_template(
        "analytics.html",
        chart="charts/pie_chart.png"
    )


@app.route('/chatbot')
def chatbot():
    return render_template("chatbot.html")


@app.route('/chat', methods=['POST'])
def chat():

    question = request.form['question'].lower()

    answers = {
        "brain tumor": "A brain tumor is an abnormal growth of cells in the brain.",
        "glioma": "Glioma is a tumor that starts in the brain's glial cells.",
        "meningioma": "Meningioma develops in the membranes surrounding the brain.",
        "pituitary": "Pituitary tumors affect hormone production.",
        "symptoms": "Common symptoms include headache, blurred vision and seizures.",
        "foods": "Eat healthy foods like fruits, vegetables and whole grains.",
        "precautions": "Follow your doctor's advice and attend regular checkups.",
        "doctor": "Consult a Neurologist or Neurosurgeon."
    }

    answer = "Sorry! I don't know the answer."

    for key in answers:
        if key in question:
            answer = answers[key]
            break

    return render_template(
        "chatbot.html",
        question=question,
        answer=answer
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
