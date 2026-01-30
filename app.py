import streamlit as st
import pdfplumber
from docx import Document
from openai import OpenAI
import json
from datetime import datetime

# PDF generation
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# -------------------------------
# App Configuration
# -------------------------------
st.set_page_config(page_title="SMEGuard", layout="centered")

st.title("🛡️ SMEGuard")
st.subheader("GenAI Contract Risk Analyzer for Indian SMEs")

# -------------------------------
# File Upload Section
# -------------------------------
st.markdown("### 📄 Upload your contract")

uploaded_file = st.file_uploader(
    "Supported formats: PDF, DOCX, TXT",
    type=["pdf", "docx", "txt"]
)

# -------------------------------
# Text Extraction
# -------------------------------
def extract_text(file):
    text = ""

    if file.name.endswith(".pdf"):
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

    elif file.name.endswith(".docx"):
        doc = Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"

    elif file.name.endswith(".txt"):
        text = file.read().decode("utf-8")

    return text

# -------------------------------
# Clause Splitting
# -------------------------------
def split_into_clauses(text):
    raw_clauses = text.split("\n\n")
    clauses = []

    for clause in raw_clauses:
        cleaned = clause.strip()
        if len(cleaned) > 40:
            clauses.append(cleaned)

    return clauses

# -------------------------------
# OpenAI Client
# -------------------------------
client = OpenAI()

def analyze_clause(clause_text):
    prompt = f"""
You are a legal assistant for Indian small and medium businesses.

Return ONLY valid JSON in this format:

{{
  "explanation": "Simple explanation",
  "risk_level": "Low | Medium | High",
  "business_impact": "Real-world SME impact"
}}

Clause:
\"\"\"{clause_text}\"\"\"
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a careful legal assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    raw = response.choices[0].message.content

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "explanation": "Could not parse AI output.",
            "risk_level": "Medium",
            "business_impact": "Manual review recommended."
        }

def suggest_safer_clause(clause_text):
    prompt = f"""
You are a legal drafting assistant for Indian SMEs.

Rewrite the clause below into a safer, balanced, SME-friendly version.

Clause:
\"\"\"{clause_text}\"\"\"
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You rewrite legal clauses safely."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content

# -------------------------------
# Risk Helpers
# -------------------------------
def risk_badge(level):
    if level == "High":
        return "🔴 High Risk"
    elif level == "Medium":
        return "🟡 Medium Risk"
    return "🟢 Low Risk"

def risk_score(level):
    return {"Low": 1, "Medium": 2, "High": 3}.get(level, 2)

# -------------------------------
# Audit Logging
# -------------------------------
def save_audit_log(clause_text, ai_result):
    log = {
        "timestamp": datetime.now().isoformat(),
        "clause": clause_text,
        "analysis": ai_result
    }

    with open("audit_log.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(log, ensure_ascii=False) + "\n")

# -------------------------------
# PDF Report Generator
# -------------------------------
def generate_pdf(summary_data):
    file_name = "SMEGuard_Contract_Report.pdf"
    doc = SimpleDocTemplate(file_name)
    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph("<b>SMEGuard – Contract Risk Report</b>", styles["Title"]))

    for item in summary_data:
        content.append(Paragraph(f"<b>Clause:</b> {item['clause']}", styles["Normal"]))
        content.append(Paragraph(f"<b>Risk Level:</b> {item['risk']}", styles["Normal"]))
        content.append(Paragraph(f"<b>Explanation:</b> {item['explanation']}", styles["Normal"]))
        content.append(Paragraph(f"<b>Business Impact:</b> {item['impact']}", styles["Normal"]))
        content.append(Paragraph("<br/>", styles["Normal"]))

    doc.build(content)
    return file_name

# -------------------------------
# Main Logic
# -------------------------------
if uploaded_file:
    st.success("File uploaded successfully!")

    extracted_text = extract_text(uploaded_file)

    if extracted_text.strip():
        clauses = split_into_clauses(extracted_text)
        st.success(f"Detected {len(clauses)} clauses")

        summary_data = []
        total_risk = 0
        analyzed = 0

        st.markdown("### 📑 Contract Clauses")

        for idx, clause in enumerate(clauses, start=1):
            with st.expander(f"Clause {idx}"):
                st.write(clause)

                if st.button(f"Analyze Clause {idx}", key=f"analyze_{idx}"):
                    with st.spinner("Analyzing clause..."):
                        ai_result = analyze_clause(clause)

                        st.markdown(f"**Risk Level:** {risk_badge(ai_result['risk_level'])}")
                        st.markdown("**Explanation:**")
                        st.write(ai_result["explanation"])
                        st.markdown("**Business Impact:**")
                        st.write(ai_result["business_impact"])

                        save_audit_log(clause, ai_result)

                        summary_data.append({
                            "clause": clause[:300] + "...",
                            "risk": ai_result["risk_level"],
                            "explanation": ai_result["explanation"],
                            "impact": ai_result["business_impact"]
                        })

                        total_risk += risk_score(ai_result["risk_level"])
                        analyzed += 1

                if st.button(f"Suggest Safer Clause {idx}", key=f"suggest_{idx}"):
                    with st.spinner("Generating safer clause..."):
                        safer_clause = suggest_safer_clause(clause)
                        st.markdown("### ✍️ Safer SME-Friendly Clause")
                        st.write(safer_clause)

        if analyzed > 0:
            avg_risk = round(total_risk / analyzed, 2)

            st.markdown("## 📊 Overall Contract Risk Score")
            st.progress(min(avg_risk / 3, 1.0))
            st.write(f"Average Risk Score: {avg_risk} / 3")

        if len(summary_data) > 0:
            if st.button("📄 Generate PDF Risk Report"):
                pdf_file = generate_pdf(summary_data)
                with open(pdf_file, "rb") as f:
                    st.download_button(
                        label="⬇️ Download Contract Report",
                        data=f,
                        file_name=pdf_file,
                        mime="application/pdf"
                    )

    else:
        st.warning("Could not extract text from this file.")
