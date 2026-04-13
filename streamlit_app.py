import streamlit as st
from groq import Groq
import PyPDF2

# Page config
st.set_page_config(page_title="Sonata Release Note Generator", layout="wide")

st.title("📄 Sonata Release Note Generator")
st.write("Upload a JIRA PDF or paste details to generate a TW-compliant Release Note.")

# Load Groq API key
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

release_note_type = st.selectbox(
    "Release Note Type",
    options=["DRN", "ERN"],
    help="DRN = Defect Release Note, ERN = Enhancement Release Note",
)

release_note_metadata = {
    "DRN": {
        "label": "Defect Release Note",
        "input_label": "Defect",
        "title": "Defect",
        "guideline": "DRN Authoring Guidelines",
        "template": """Background
Change Implemented
Dependencies/Impact""",
        "rules": """
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
""",
    },
    "ERN": {
        "label": "Enhancement Release Note",
        "input_label": "Enhancement",
        "title": "Enhancement",
        "guideline": "ERN Authoring Guidelines",
        "template": """Background
Enhancement Implemented
Dependencies/Impact""",
        "rules": """
GENERAL:
- Use business-friendly language (NOT technical)
- Ensure clarity, accuracy, and completeness
- Avoid copying raw text directly; rephrase meaningfully
- Ensure all 3 sections are properly populated
- Maintain consistency across sections

BACKGROUND:
- Describe current process/limitation and business context
- Explain why the enhancement was needed and expected business value

ENHANCEMENT IMPLEMENTED:
- Clearly explain what was enhanced
- Describe the new behaviour/capability after implementation
- Highlight user or business benefit delivered by the enhancement

DEPENDENCIES/IMPACT:
- Keep concise but meaningful
- Clearly state impacted modules, users, or downstream processes
""",
    },
}

selected_metadata = release_note_metadata[release_note_type]

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
    uploaded_file = st.file_uploader(f"Upload JIRA {selected_metadata['input_label']} PDF", type=["pdf"])
    if uploaded_file:
        with st.spinner("Reading PDF..."):
            input_text = extract_text_from_pdf(uploaded_file)
        st.success("PDF content extracted")

# Tab 2: Manual Input
with tab2:
    manual_text = st.text_area(f"Paste {selected_metadata['input_label']} Details", height=300)
    if manual_text:
        input_text = manual_text

# Generate button
if st.button("🚀 Generate Release Note"):

    if not input_text.strip():
        st.warning("Please upload a PDF or paste details.")
        st.stop()

    if len(input_text.strip()) < 20:
        st.error("Input too small or invalid PDF content.")
        st.stop()

    prompt = f"""
Act as a Business Analyst preparing a {selected_metadata['label']} ({release_note_type}) for Sonata, strictly following company {selected_metadata['guideline']}.

Your task is to convert the provided {selected_metadata['input_label'].lower()} details into a high-quality, client-facing {selected_metadata['label']}.

----------------------------------
STRICT TEMPLATE (DO NOT CHANGE HEADINGS):

{selected_metadata['template']}

----------------------------------
WRITING RULES (MANDATORY):
{selected_metadata['rules']}

----------------------------------
INPUT:
{input_text[:6000]}

----------------------------------
OUTPUT:
Provide ONLY the final {selected_metadata['label']}.
"""

    try:
        with st.spinner("Generating Release Note..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional business analyst generating client-ready release notes.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )

            output = response.choices[0].message.content

        st.subheader(f"✅ Generated {selected_metadata['label']}")
        st.text_area("Output", output, height=400)

        file_name = f"{release_note_type.lower()}_release_note.txt"
        st.download_button(
            label="⬇️ Download Release Note",
            data=output,
            file_name=file_name,
        )

    except Exception as e:
        st.error("❌ Error generating release note. Please try smaller input or paste text manually.")
        st.exception(e)
