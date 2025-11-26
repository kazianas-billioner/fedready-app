import pandas as pd
import streamlit as st
import json
import google.generativeai as genai
from fpdf import FPDF
from datetime import datetime

# --- 1. SETUP PAGE CONFIG & SESSION STATE ---
st.set_page_config(page_title="FedReady Auditor", page_icon="🛡️")

# Initialize Chat Memory
if "messages" not in st.session_state:
    st.session_state.messages = []
if "audit_context" not in st.session_state:
    st.session_state.audit_context = ""

st.title("🛡️ FedReady: AI Compliance Officer")
st.markdown("Automated NIST 800-171 Gap Analysis & Reporting")

# --- 2. SIDEBAR CONFIG ---
with st.sidebar:
    st.header("FedReady Pro 🛡️")
    
    # 1. PASSWORD PROTECTION
    password = st.text_input("Enter Client Password", type="password")
    if password != "fedready2025": 
        st.warning("🔒 System Locked. Please enter password.")
        st.stop() 
    
    st.success("✅ Access Granted: Enterprise License")
    
    # 2. AUTO-LOAD HIDDEN KEY
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except FileNotFoundError:
        st.error("Secrets file not found. Check setup.")
        st.stop()

# --- 3. CORE LOGIC ---
class AuditReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'FedReady - Official Compliance Report', 0, 1, 'C')
        self.ln(5)

    def add_violation(self, violation_title, ai_analysis):
        self.set_font('Arial', 'B', 12)
        self.set_text_color(200, 0, 0) 
        self.cell(0, 10, f"DETECTED: {violation_title}", 0, 1)
        self.set_text_color(0, 0, 0)
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 7, ai_analysis)
        self.ln(5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

def analyze_issue(model, issue_text):
    prompt = f"""
    You are a NIST Compliance Auditor.
    Violation: "{issue_text}"
    Output format:
    NIST CONTROL: [Number]
    RISK: [1 sentence]
    REMEDIATION: [1 technical fix]
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "AI Analysis Unavailable."

# --- 4. THE APP INTERFACE ---
uploaded_file = st.file_uploader("Upload System Logs", type=["json", "csv", "xlsx"])

if uploaded_file and api_key:
    # SMART LOADER
    if uploaded_file.name.endswith('.json'):
        logs = json.load(uploaded_file)
    elif uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
        logs = df.to_dict(orient='records') 
    elif uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
        logs = df.to_dict(orient='records')
    
    # Initialize AI
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')

    if st.button("🚀 Start Compliance Scan"):
        
        # --- NEW: DASHBOARD ANALYTICS ---
        st.divider()
        st.subheader("📊 Executive Dashboard")
        
        # 1. Calculate Metrics
        total_logs = len(logs)
        violation_counts = {}
        
        for log in logs:
            user = log.get('user_email', 'Unknown')
            # Universal Logic Helper
            details = log.get('details', {}) # For JSON
            def get_val(k): return details.get(k) or log.get(k) 
            
            is_issue = False
            # Check logic using helper (Works for CSV & JSON)
            if log.get('event_type') == "USER_LOGIN" and get_val('mfa_status') == "DISABLED":
                is_issue = True
            elif log.get('event_type') == "FILE_UPLOAD" and "Public" in str(get_val('destination_folder')):
                is_issue = True
            elif log.get('event_type') == "PERMISSION_CHANGE" and get_val('new_permission_level') == "PUBLIC_READ":
                is_issue = True
            elif log.get('event_type') == "SOFTWARE_INSTALL" and str(get_val('approved_list')).upper() == "FALSE":
                is_issue = True
            
            if is_issue:
                violation_counts[user] = violation_counts.get(user, 0) + 1

        total_issues = sum(violation_counts.values())
        score = max(0, 100 - (total_issues * 10)) 

        # 2. Display Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Compliance Score", f"{score}%", delta=f"-{total_issues*10}%" if total_issues > 0 else "0%")
        col2.metric("Total Events Scanned", total_logs)
        col3.metric("Critical Violations", total_issues, delta_color="inverse")
        
        # 3. Display Chart
        if total_issues > 0:
            st.caption("Top Risky Users")
            chart_data = pd.DataFrame(list(violation_counts.items()), columns=["User", "Violations"])
            st.bar_chart(chart_data.set_index("User"))
        
        st.divider()
        
        # --- DETAILED FINDINGS ---
        st.subheader("⚠️ Detailed Findings")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        pdf = AuditReport()
        pdf.add_page()
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 10, f"Scan Date: {datetime.now().strftime('%Y-%m-%d')}", 0, 1)

        issues = [] 

        # Scanning Loop
        for i, log in enumerate(logs):
            status_text.text(f"Scanning log entry {i+1}/{total_logs}...")
            progress_bar.progress((i + 1) / total_logs)
            
            details = log.get('details', {}) 
            def get_val(key): return details.get(key) or log.get(key)

            event = log.get('event_type')
            user = log.get('user_email', 'Unknown')
            mfa = get_val('mfa_status')
            folder = get_val('destination_folder')
            perm = get_val('new_permission_level')
            soft_name = get_val('software_name')
            approved = get_val('approved_list')
            
            msg = ""

            if event == "USER_LOGIN" and mfa == "DISABLED":
                msg = f"CRITICAL: User {user} logged in without MFA."
            elif event == "FILE_UPLOAD" and folder and "Public" in str(folder):
                msg = f"DATA LEAK: User {user} exposed file to Public Folder."
            elif event == "PERMISSION_CHANGE" and perm == "PUBLIC_READ":
                msg = f"HIGH RISK: User {user} set resource to Public Read."
            elif event == "SOFTWARE_INSTALL" and str(approved).upper() == "FALSE":
                msg = f"SHADOW IT: User {user} installed unapproved software: {soft_name}."

            if msg:
                issues.append(msg)
                with st.expander(f"🚨 {msg}", expanded=True):
                    if len(issues) <= 5: 
                        with st.spinner("Consulting AI Auditor..."):
                            analysis = analyze_issue(model, msg)
                            st.write(analysis)
                            pdf.add_violation(msg, analysis)
                    else:
                        st.write("Logged for Report.")
                        pdf.add_violation(msg, "See full logs.")
        
        # Save Context & PDF
        if issues:
            st.session_state.audit_context = "\n".join(issues)
        else:
            st.session_state.audit_context = "System is secure. No violations."

        pdf_filename = "FedReady_Report.pdf"
        pdf.output(pdf_filename)
        
        with open(pdf_filename, "rb") as f:
            st.download_button(
                label="📄 Download Official NIST Report",
                data=f,
                file_name="Audit_Report_v1.pdf",
                mime="application/pdf"
            )

    # --- 5. AI CONSULTANT CHATBOT (NOW SAFELY INDENTED) ---
    st.divider()
    st.subheader("💬 Ask the Auditor")
    st.caption("Ask questions about the findings (e.g., 'How do I fix the MFA issue for Steve?')")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Type your question here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                full_prompt = f"""
                You are a NIST Cybersecurity Expert. 
                Context of the current system audit:
                {st.session_state.audit_context}
                
                User Question: {prompt}
                
                Provide a specific, technical answer.
                """
                response = model.generate_content(full_prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})

elif not uploaded_file:
    st.info("👆 Please upload a log file to start the audit.")