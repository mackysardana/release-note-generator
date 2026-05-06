import streamlit as st
from groq import Groq
import PyPDF2

# Page config
st.set_page_config(page_title="Sonata Release Note Generator", layout="wide")

st.title("📄 Sonata Release Note Generator")
st.write("Upload a JIRA/Design/BSD/IA PDF or paste details to generate a TW-compliant Release Note.")

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
    },
    "ERN": {
        "label": "Enhancement Release Note",
        "input_label": "Enhancement",
        "title": "Enhancement",
        "guideline": "ERN Authoring Guidelines",
        "template": """Summary
Overview
Key Features
Menu Path
Implementation Considerations
Impact/Dependencies""",
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


def build_prompt(note_type: str, source_text: str) -> str:
    if note_type == "ERN":
        return f"""
Act as a Senior Business Analyst and Technical Writer preparing an Enhancement Release Note (ERN) for Sonata.

STRICT OUTPUT FORMAT (use these headings exactly):
Summary
Overview
Key Features
Menu Path
Implementation Considerations
Impact/Dependencies

ERN RULES:
- Use business-friendly language and avoid technical implementation detail unless needed for business clarity.
- Expand abbreviation at first use, e.g. "Enhancement Release Note (ERN)".
- Summary must be a single-line title in this style:
  "<Region if region-specific> - <Business Area> - <Enhancement> to <Business Advantage>"
- Overview must include:
  1) What was enhanced
  2) The rationale: "The rationale behind this enhancement is..."
  3) Previous behaviour: "Prior to this enhancement..."
  4) Region/business impact sentence (global or region-specific)
  5) Glossary note when terms are used:
     "Note - For more information on the following terms - <terms>, please refer to Sonata Glossary."
- Key Features must contain a **Demonstrable Additions** subsection with clear, client-facing points.
- Menu Path must include Graphical Menu and Classic Menu when available from input. If not available, state "Not provided in source documentation.".
- Implementation Considerations must never be empty. Use "No configuration required." only if no dependencies are indicated.
- Impact/Dependencies must never be blank and should mention downstream impact, regression scope, and performance impact where relevant.
- Do not include client names, Jira IDs, or internal-only instructions.
- Do not include markdown bullets under headings unless it improves readability; keep concise and publish-ready.

INPUT SOURCE (Design/BSD/IA/Jira):
{source_text[:12000]}

OUTPUT:
Provide ONLY the final ERN content.
"""

    return f"""
Act as a Senior Business Analyst preparing a Defect Release Note (DRN) for Sonata.

STRICT TEMPLATE (DO NOT CHANGE HEADINGS):
Background
Change Implemented
Dependencies/Impact

WRITING STYLE REQUIREMENTS:
- Background starts with "When a user..."
- Include expected behaviour with: "Ideally, the system should have..."
- Change Implemented starts with "This issue occurred because..."
- Include "To resolve this issue..." and end with "After these changes..."
- Dependencies/Impact format: "This change only impacts..."
- Use business-friendly language and clear cause/fix/outcome linkage.

INPUT DEFECT DETAILS:
{source_text[:12000]}

OUTPUT:
Provide ONLY the final DRN.
"""


input_text = ""

# Tab 1: PDF Upload
with tab1:
    uploaded_files = st.file_uploader(
        f"Upload {selected_metadata['input_label']} / Design / BSD / IA PDF(s)",
        type=["pdf"],
        accept_multiple_files=True,
    )
    if uploaded_files:
        combined_text = ""
        with st.spinner("Reading PDF(s)..."):
            for uploaded_file in uploaded_files:
                combined_text += f"\n\n--- Source File: {uploaded_file.name} ---\n"
                combined_text += extract_text_from_pdf(uploaded_file)
        input_text = combined_text
        st.success(f"Extracted content from {len(uploaded_files)} file(s).")

# Tab 2: Manual Input
with tab2:
    manual_text = st.text_area(
        f"Paste {selected_metadata['input_label']} / Design / BSD / IA Details", height=300
    )
    if manual_text:
        input_text = manual_text

# Generate button
if st.button("🚀 Generate Release Note"):

    if not input_text.strip():
        st.warning("Please upload PDF(s) or paste details.")
        st.stop()

    if len(input_text.strip()) < 20:
        st.error("Input too small or invalid PDF content.")
        st.stop()

    prompt = build_prompt(release_note_type, input_text)
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
                temperature=0.2,
            )

            output = response.choices[0].message.content

        st.subheader(f"✅ Generated {selected_metadata['label']}")
        st.text_area("Output", output, height=500)

        file_name = f"{release_note_type.lower()}_release_note.txt"
        st.download_button(
            label="⬇️ Download Release Note",
            data=output,
            file_name=file_name,
        )

    except Exception as e:
        st.error("❌ Error generating release note. Please try smaller input or paste text manually.")
        st.exception(e)
