import streamlit as st
from groq import Groq
import PyPDF2

# Page config
st.set_page_config(page_title="Sonata DRN Generator", layout="wide")

st.title("📄 Sonata Defect Release Note Generator")

st.write("Upload a JIRA defect PDF or paste details to generate a TW-compliant Release Note.")

# Load Groq API key
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Input options
tab1, tab2 = st.tabs(["📄 Upload PDF", "✍️ Paste Text"])

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
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
    else:
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
- Ensure all 3 sections are properly populated (no blanks, no NA)
- Avoid one-line or one-word entries; provide clear explanation
- Maintain consistency across sections (Background, Change, Impact must align)

BACKGROUND:
- Describe the issue in business terms (PAST TENSE)
- Clearly explain:
  - What was the issue
  - Where it occurred
  - Scenario/conditions
  - Expected behaviour
  - Consequences/impact

CHANGE IMPLEMENTED:
- Clearly explain:
  - Cause of issue (business terms)
  - Fix implemented
  - Summary of fix (high-level)
- MUST include:
  - System behaviour AFTER fix (FUTURE TENSE)

DEPENDENCIES/IMPACT:
- Must not be empty
- Keep concise but meaningful
- Clearly state impacted functionality and scope

----------------------------------
LANGUAGE RULES:
- Avoid technical jargon
- Avoid internal references
- Use formal, client-facing language
- Avoid words like "getting", "flag", "Ideally"

----------------------------------
QUALITY:
- Must be violation-free
- Must include cause, fix, and outcome
- Must be complete and aligned

----------------------------------
INPUT:
{input_text}

----------------------------------
OUTPUT:
Provide ONLY the final Defect Release Note.
"""

        with st.spinner("Generating Release Note..."):
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            output = response.choices[0].message.content

        st.subheader("✅ Generated Release Note")
        st.text_area("Output", output, height=400)

        # Download button
        st.download_button(
            label="⬇️ Download Release Note",
            data=output,
            file_name="release_note.txt"
        )
