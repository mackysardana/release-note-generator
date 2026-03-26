import streamlit as st
from groq import Groq
import PyPDF2

# Page config
st.set_page_config(page_title="Sonata DRN Generator", layout="wide")

st.title("📄 Sonata Defect Release Note Generator")
st.write("Upload a JIRA defect PDF or paste details to generate a TW-compliant Release Note.")

# Load Groq API key
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Tabs
tab1, tab2 = st.tabs(["📄 Upload PDF", "✍️ Paste Text"])

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text

input_text = ""

# Tab 1: PDF Upload
with tab1:
    uploaded_file = st.file_uploader("Upload JIRA Defect PDF", type=["pdf"])
    if uploaded_file:
        with st.spinner("Reading PDF..."):
            input_text = extract_text_from_pdf(uploaded_file)
        st.success("PDF content extracted")

# Tab 2: Manual Input
with tab2:
    manual_text = st.text_area("Paste Defect Details", height=300)
    if manual_text:
        input_text = manual_text

# Generate button
if st.button("🚀 Generate Release Note"):

    if not input_text.strip():
        st.warning("Please upload a PDF or paste defect details.")
        st.stop()

    if len(input_text.strip()) < 20:
        st.error("Input too small or invalid PDF content.")
        st.stop()

    prompt = f"""
Act as a Business Analyst preparing a Defect Release Note (DRN) for Sonata, strictly following company DRN Authoring Guidelines.

Your task is to convert the provided defect details into a high-quality, client-facing Defect Release Note.

----------------------------------
STRICT TEMPLATE (DO NOT CHANGE HEADINGS):

Background
Change Implemented
Dependencies/Impact

----------------------------------
WRITING RULES (MANDATORY):

GENERAL:
- Use business-friendly language (NOT technical)
- Ensure clarity, accuracy, and completeness
- Avoid copying raw text directly; rephrase meaningfully
- Ensure all 3 sections are properly populated
- Maintain consistency across sections

BACKGROUND:
- Describe issue in past tense
- Include issue, scenario, expected behaviour, impact

CHANGE IMPLEMENTED:
- Include cause, fix, and behaviour after fix

DEPENDENCIES/IMPACT:
- Keep concise but meaningful
- Clearly state impacted functionality

----------------------------------
INPUT:
{input_text[:6000]}

----------------------------------
OUTPUT:
Provide ONLY the final Defect Release Note.
"""

    try:
        with st.spinner("Generating Release Note..."):
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": "You are a professional business analyst generating client-ready release notes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            output = response.choices[0].message.content

        st.subheader("✅ Generated Release Note")
        st.text_area("Output", output, height=400)

        st.download_button(
            label="⬇️ Download Release Note",
            data=output,
            file_name="release_note.txt"
        )

    except Exception as e:
        st.error("❌ Error generating release note. Please try smaller input or paste text manually.")
        st.exception(e)
