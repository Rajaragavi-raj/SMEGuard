import streamlit as st
import pdfplumber
from docx import Document
import json
from datetime import datetime

# PDF generation
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# -------------------------------
# App Configuration
# -------------------------------
st.set_page_config(page_title="SMEGuard", layout="centered", page_icon="🛡️")

# -------------------------------
# Custom CSS for Attractive UI
# -------------------------------
st.markdown("""
<style>
    /* Main background and theme */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Main container styling */
    .main .block-container {
        background-color: white;
        padding: 2rem 3rem;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        max-width: 1000px;
        margin-top: 2rem;
        margin-bottom: 2rem;
    }
    
    /* Title styling */
    h1 {
        color: #1a1a2e !important;
        font-size: 3rem !important;
        font-weight: 800 !important;
        text-align: center;
        margin-bottom: 0.5rem !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Subtitle styling */
    h3 {
        color: #2c3e50 !important;
        text-align: center;
        font-weight: 600 !important;
        margin-bottom: 2rem !important;
    }
    
    /* File uploader styling */
    .stFileUploader {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 15px;
        border: 2px dashed #667eea;
        margin-bottom: 2rem;
    }
    
    .stFileUploader label {
        color: #1a1a2e !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }
    
    /* Success message styling */
    .stSuccess {
        background-color: #d4edda !important;
        color: #155724 !important;
        padding: 1rem !important;
        border-radius: 10px !important;
        border-left: 5px solid #28a745 !important;
        font-weight: 500 !important;
    }
    
    /* Warning message styling */
    .stWarning {
        background-color: #fff3cd !important;
        color: #856404 !important;
        padding: 1rem !important;
        border-radius: 10px !important;
        border-left: 5px solid #ffc107 !important;
        font-weight: 500 !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 1rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    
    .streamlit-expanderContent {
        background-color: #f8f9fa;
        border-radius: 0 0 10px 10px;
        padding: 1.5rem;
        border: 2px solid #e9ecef;
        border-top: none;
        color: #1a1a2e !important;
    }
    
    .streamlit-expanderContent p {
        color: #2c3e50 !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        width: 100%;
        margin-top: 0.5rem;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    .stButton > button:active {
        transform: translateY(-1px);
    }
    
    /* Download button styling */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.8rem 2.5rem;
        font-weight: 700;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(86, 171, 47, 0.3);
        width: 100%;
        margin-top: 1rem;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(86, 171, 47, 0.4);
        background: linear-gradient(135deg, #a8e063 0%, #56ab2f 100%);
    }
    
    /* Progress bar styling */
    .stProgress > div > div {
        background: linear-gradient(90deg, #56ab2f 0%, #a8e063 100%);
        border-radius: 10px;
        height: 30px;
    }
    
    .stProgress > div {
        background-color: #e9ecef;
        border-radius: 10px;
    }
    
    /* Risk badge styling */
    .risk-badge {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 1.1rem;
        display: inline-block;
        margin: 1rem 0;
    }
    
    /* Text styling */
    p {
        color: #2c3e50 !important;
        line-height: 1.6;
        font-size: 1rem;
        font-weight: 500;
    }
    
    div {
        color: #2c3e50 !important;
    }
    
    span {
        color: #2c3e50 !important;
    }
    
    strong {
        color: #1a1a2e !important;
    }
    
    /* Card-like containers */
    .info-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        color: #1a1a2e !important;
    }
    
    .info-card strong {
        color: #1a1a2e !important;
    }
    
    .info-card span {
        color: #2c3e50 !important;
    }
    
    /* Score display */
    .score-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        margin: 2rem 0;
        border: 3px solid #667eea;
    }
    
    .score-text {
        font-size: 2rem;
        font-weight: 800;
        color: #1a1a2e;
        margin: 0;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1.5rem;
        }
        
        h1 {
            font-size: 2rem !important;
        }
        
        .stButton > button {
            padding: 0.5rem 1rem;
        }
    }
    
    /* Hover effects */
    .info-card:hover {
        transform: translateY(-5px);
        transition: all 0.3s ease;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Header Section
# -------------------------------
st.markdown("""
<div style='text-align: center; padding: 1rem 0;'>
    <h1 style='color: #1a1a2e; text-shadow: 3px 3px 6px rgba(0,0,0,0.3);'>🛡️ SMEGuard</h1>
</div>
""", unsafe_allow_html=True)

st.markdown("<h3 style='color: #2c3e50; text-align: center; font-weight: 700;'>Contract Risk Analyzer for Indian SMEs</h3>", unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center; color: #2c3e50; margin-bottom: 2rem; font-weight: 600;'>
    <p style='font-size: 1.1rem;'>Upload your contract and get instant AI-powered risk analysis to protect your business</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------
# File Upload
# -------------------------------
uploaded_file = st.file_uploader(
    "📄 Upload contract (PDF, DOCX, TXT)",
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
                if page.extract_text():
                    text += page.extract_text() + "\n"
    elif file.name.endswith(".docx"):
        doc = Document(file)
        for p in doc.paragraphs:
            text += p.text + "\n"
    else:
        text = file.read().decode("utf-8")
    return text

# -------------------------------
# Clause Splitter
# -------------------------------
def split_into_clauses(text):
    return [c.strip() for c in text.split("\n\n") if len(c.strip()) > 40]

# -------------------------------
# Rule-Based Analysis (NO API)
# -------------------------------
def analyze_clause(clause):
    clause_lower = clause.lower()

    if "terminate" in clause_lower and "without notice" in clause_lower:
        risk = "High"
        explanation = "The other party can terminate the contract anytime without warning."
        impact = "You may suddenly lose the contract and revenue."
    elif "penalty" in clause_lower or "liquidated damages" in clause_lower:
        risk = "High"
        explanation = "The clause imposes financial penalties."
        impact = "You may face unexpected monetary loss."
    elif "jurisdiction" in clause_lower or "courts" in clause_lower:
        risk = "Medium"
        explanation = "Legal disputes are limited to a specific location."
        impact = "Litigation may be expensive and inconvenient."
    else:
        risk = "Low"
        explanation = "This clause appears balanced."
        impact = "Minimal risk to daily business operations."

    return {
        "risk_level": risk,
        "explanation": explanation,
        "business_impact": impact
    }

# -------------------------------
# Safer Clause Generator
# -------------------------------
def suggest_safer_clause(clause):
    return (
        "Both parties may terminate this agreement by providing at least "
        "30 days written notice. Any penalties shall be reasonable and "
        "mutually agreed upon. Disputes shall be resolved through arbitration "
        "or courts with mutual consent."
    )

# -------------------------------
# Risk Helpers
# -------------------------------
def risk_badge(level):
    return {"High": "🔴 High Risk", "Medium": "🟡 Medium Risk", "Low": "🟢 Low Risk"}[level]

def risk_score(level):
    return {"Low": 1, "Medium": 2, "High": 3}[level]

# -------------------------------
# Audit Log
# -------------------------------
def save_audit_log(clause, result):
    log = {
        "time": datetime.now().isoformat(),
        "clause": clause,
        "analysis": result
    }
    with open("audit_log.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(log) + "\n")

# -------------------------------
# PDF Generator
# -------------------------------
def generate_pdf(data):
    file = "SMEGuard_Report.pdf"
    doc = SimpleDocTemplate(file)
    styles = getSampleStyleSheet()
    content = [Paragraph("<b>SMEGuard Contract Risk Report</b>", styles["Title"])]

    for d in data:
        content.append(Paragraph(f"<b>Clause:</b> {d['clause']}", styles["Normal"]))
        content.append(Paragraph(f"<b>Risk:</b> {d['risk']}", styles["Normal"]))
        content.append(Paragraph(f"<b>Explanation:</b> {d['explanation']}", styles["Normal"]))
        content.append(Paragraph(f"<b>Impact:</b> {d['impact']}", styles["Normal"]))
        content.append(Paragraph("<br/>", styles["Normal"]))

    doc.build(content)
    return file

# -------------------------------
# Main App
# -------------------------------
if uploaded_file:
    with st.spinner('🔄 Processing your contract...'):
        text = extract_text(uploaded_file)

    if text.strip():
        clauses = split_into_clauses(text)
        st.success(f"✅ Successfully detected {len(clauses)} clauses in your contract")

        st.markdown("---")
        st.markdown("<h2 style='color: #1a1a2e; text-align: center; font-weight: 800; font-size: 2rem;'>📋 Clause Analysis</h2>", unsafe_allow_html=True)

        summary = []
        total = 0
        count = 0

        for i, clause in enumerate(clauses, 1):
            with st.expander(f"📄 Clause {i}"):
                st.markdown(f"<div class='info-card' style='color: #1a1a2e !important;'><strong style='color: #1a1a2e;'>{clause}</strong></div>", unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button(f"🔍 Analyze Clause {i}", key=f"a{i}"):
                        with st.spinner('Analyzing...'):
                            result = analyze_clause(clause)
                            st.markdown(f"<h3 style='color: #1a1a2e; font-weight: 800;'>{risk_badge(result['risk_level'])}</h3>", unsafe_allow_html=True)
                            st.markdown(f"<div class='info-card'><strong style='color: #1a1a2e;'>📊 Explanation:</strong><br><span style='color: #2c3e50;'>{result['explanation']}</span></div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='info-card'><strong style='color: #1a1a2e;'>💼 Business Impact:</strong><br><span style='color: #2c3e50;'>{result['business_impact']}</span></div>", unsafe_allow_html=True)

                            save_audit_log(clause, result)

                            summary.append({
                                "clause": clause[:200],
                                "risk": result["risk_level"],
                                "explanation": result["explanation"],
                                "impact": result["business_impact"]
                            })

                            total += risk_score(result["risk_level"])
                            count += 1

                with col2:
                    if st.button(f"✨ Suggest Safer Clause {i}", key=f"s{i}"):
                        st.markdown(f"<div class='info-card'><strong style='color: #1a1a2e;'>💡 Recommended Clause:</strong><br><span style='color: #2c3e50;'>{suggest_safer_clause(clause)}</span></div>", unsafe_allow_html=True)

        if count:
            st.markdown("---")
            avg = round(total / count, 2)
            
            st.markdown("<div class='score-container'>", unsafe_allow_html=True)
            st.markdown(f"<p class='score-text'>Overall Risk Score: {avg}/3</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.progress(avg / 3)
            
            if avg >= 2.5:
                st.error("⚠️ High overall risk detected. Consider legal review before signing.")
            elif avg >= 1.5:
                st.warning("⚡ Moderate risk level. Review carefully and negotiate terms.")
            else:
                st.success("✅ Low overall risk. Contract appears balanced.")

        if summary:
            st.markdown("---")
            st.markdown("<h2 style='color: #1a1a2e; text-align: center; font-weight: 800; font-size: 2rem;'>📥 Generate Report</h2>", unsafe_allow_html=True)
            
            if st.button("📄 Generate PDF Report"):
                with st.spinner('Generating your report...'):
                    pdf = generate_pdf(summary)
                    with open(pdf, "rb") as f:
                        st.download_button("⬇️ Download Report", f, file_name=pdf)
                    st.balloons()

    else:
        st.warning("⚠️ No text detected in the uploaded file. Please upload a valid document.")

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #2c3e50; padding: 2rem 0;'>
    <p style='font-weight: 700; font-size: 1.1rem;'><strong>SMEGuard</strong> - Empowering SMEs with smart contract analysis</p>
    <p style='font-size: 0.95rem; font-weight: 600;'>© 2024 All rights reserved</p>
</div>
""", unsafe_allow_html=True)
