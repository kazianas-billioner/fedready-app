# 🛡️ FedReady: AI Compliance Officer

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://fedready-app.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![AI](https://img.shields.io/badge/AI-Gemini%202.0%20Flash-orange)
![License](https://img.shields.io/badge/License-MIT-green)

**FedReady** is a Vertical AI Agent designed to automate **NIST 800-171 Gap Analysis** for government contractors and MSPs. 

Traditional compliance audits take **3-5 days** of manual effort. FedReady ingests raw system logs (Excel/CSV/JSON), detects security violations using Large Language Models, and generates a formal **Deficiency Report PDF** in **45 seconds**.

---

## 🚀 Live Demo
**Try the App here:** [https://fedready-app.streamlit.app/](https://fedready-app.streamlit.app/)
*(Password: `fedready2025`)*

---

## ⚡ Key Features

* **Universal Data Loader:** Drag-and-drop support for **Excel (.xlsx), CSV, and JSON** logs. No data cleaning required.
* **AI Logic Engine:** Powered by **Google Gemini 2.0 Flash**. It doesn't just match keywords; it understands context (e.g., distinguishing between a legitimate admin action and a brute force attack).
* **NIST Mapping:** Automatically maps every violation to specific NIST 800-171 Control Numbers (e.g., *Control 3.5.3 - Multi-Factor Authentication*).
* **Executive Dashboard:** Visualizes compliance scores and "Risky Users" via interactive charts.
* **Ask the Auditor (Chat):** An interactive RAG-based chat interface where users can ask technical remediation questions (e.g., *"How do I fix the Shadow IT issue?"*).
* **Enterprise Security:** Password-protected interface and hidden API key management.

---

## 🛠️ Tech Stack

* **Frontend:** [Streamlit](https://streamlit.io/) (Python)
* **AI Model:** Google Gemini 1.5/2.0 Flash (via `google-generativeai`)
* **Data Processing:** Pandas, OpenPyXL
* **Reporting:** FPDF (PDF Generation)
* **Deployment:** Streamlit Cloud

---

## 📸 Screenshots

### 1. The Executive Dashboard
*Real-time analysis of system health and critical violations.*

### 2. The "Ask the Auditor" Chat
*Context-aware AI assistant providing technical fixes for specific log entries.*

---

## 📦 Installation (Run Locally)

If you want to run this on your own machine:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/fedready-app.git](https://github.com/YOUR_USERNAME/fedready-app.git)
    cd fedready-app
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Secrets:**
    Create a `.streamlit/secrets.toml` file and add your Google Gemini API Key:
    ```toml
    GEMINI_API_KEY = "YOUR_API_KEY_HERE"
    ```

4.  **Run the App:**
    ```bash
    streamlit run app.py
    ```

---

## 📂 Project Structure
