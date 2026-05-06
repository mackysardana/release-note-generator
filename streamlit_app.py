import streamlit as st
from groq import Groq
import PyPDF2

# Page config
st.set_page_config(page_title="Sonata Release Note Generator", layout="wide")

st.title("📄 Sonata Release Note Generator")
st.write(
    "Upload a JIRA/Design/BSD/IA PDF or paste details to generate Release Notes, Overview, and Testing Scope."
)

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
        "template": """Title
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
Act as a Senior Business Analyst, Technical Writer, and QA Lead preparing outputs for Sonata.

You must generate THREE sections in this exact order and exact markers:
===RELEASE_NOTES===
<content>
===OVERVIEW===
<content>
===TESTING_SCOPE===
<content>

STRICT OUTPUT FORMAT (use these headings exactly):
Title
Overview
Key Features
Menu Path
Implementation Considerations
Impact/Dependencies

ERN RULES:
- Use business-friendly language and avoid technical implementation detail unless needed for business clarity.
- Expand abbreviation at first use, e.g. "Enhancement Release Note (ERN)".
- Title must be a single-line title matching these styles (do not add bullets or numbering):
  - "Sonata’s Account Investor Type determination enhanced to consider only active owner relationships, ensuring correct transition from Joint to Individual for accounts with deceased owners and thus improving ownership accuracy"
  - "Australian Superannuation - Enhancements to Reconcile Unpaid Refunds and Identify Source of Refund Reports to Improve CTR Refund Reconciliation and Reporting Accuracy"
  - "Australian Superannuation - Sonata enhancement introduces Reconcile Unpaid Refunds and Identify Source of Refund reports, improving visibility of CTR refund, enabling reconciliation, monitoring timelines, analysing system vs manual refund trends"
  - "Australian Superannuation - Load Contribution Schedule (SuperStream) process enhancement enables automated handling of CTR exceptions using configurable Schedule Auto Rejection Rules to support Pay Day Super compliance"
- Overview must include:
  1) What was enhanced (clear change overview)
  2) The rationale sentence beginning exactly with: "The rationale behind this enhancement is..." (must start on a new line/paragraph)
  3) Previous behaviour sentence beginning exactly with: "Prior to this enhancement..." (must start on a new line/paragraph)
  4) Region/business impact sentence (global or region-specific)
  5) Glossary note when terms are used:
     "Note - For more information on the following terms - <terms>, please refer to Sonata Glossary."
- Overview should be written as 2-4 concise paragraphs (not a heading-only section) and must clearly separate current vs prior behavior.
- Key Features must contain the exact subheading "Demonstrable Additions" followed by concise bullet points.
- In Demonstrable Additions, include business-observable outcomes such as:
  - investor type is determined using active owner relationships only;
  - deceased/deleted owner relationships are excluded from owner counts;
  - account investor type changes to Individual when only one active owner remains;
  - account investor type remains Joint when multiple active owners remain.
- You may mention enabling mechanisms (e.g., relationship-status tagging like activeRelationship=true) only when essential for business understanding; keep implementation detail minimal.
- Menu Path must include Graphical Menu and Classic Menu when available from input. If not available, state "Not provided in source documentation.".
- Implementation Considerations must never be empty. Use "No configuration required." only if no dependencies are indicated.
- Impact/Dependencies must never be blank and should mention downstream impact, regression scope, and performance impact where relevant.
- Do not include client names, Jira IDs, or internal-only instructions.
- Keep the note concise, publication-ready, and in plain business English.

QUALITY CHECKS BEFORE FINALISING:
1) Ensure there is no contradiction between Overview and Key Features.
2) If the source says statuses like Active/Updated are considered active, reflect this in business terms.
3) If scope is global, explicitly state "This enhancement is applicable globally."
4) Do not repeat the same sentence across sections.
5) Do not invent menu paths, regions, products, or dependencies.

INPUT SOURCE (Design/BSD/IA/Jira):
{source_text[:12000]}

OUTPUT:
For ===RELEASE_NOTES=== provide ONLY the final ERN content.

For ===OVERVIEW=== provide a clear and simple summary that includes:
- issue/requirement context,
- as-is behaviour,
- to-be behaviour,
- business outcome.
Write in 1-3 concise paragraphs so any reader can understand quickly.

For ===TESTING_SCOPE=== follow these requirements exactly:
- Cover positive, negative, edge, regression, data integrity, and performance (if applicable).
- Use structured format with Scenario ID, Scenario Description, Pre-conditions, Test Steps (high level), Expected Result.
- Pay special attention to backward compatibility, downstream/report impact, DB validations, and batch/job/process impact.
- Include SQL validation queries and sample test-data conditions if applicable.
- Keep concise but complete. Avoid generic statements.
- Assume Sonata is a financial platform.
- Output only test scenarios (no theory).
"""

    return f"""
Act as a Senior Business Analyst and QA Lead preparing outputs for Sonata.

You must generate THREE sections in this exact order and exact markers:
===RELEASE_NOTES===
<content>
===OVERVIEW===
<content>
===TESTING_SCOPE===
<content>

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
For ===RELEASE_NOTES=== provide ONLY the final DRN.

For ===OVERVIEW=== provide a clear and simple summary that includes:
- issue/requirement context,
- as-is behaviour,
- to-be behaviour,
- business outcome.
Write in 1-3 concise paragraphs so any reader can understand quickly.

For ===TESTING_SCOPE=== follow these requirements exactly:
- Cover positive, negative, edge, regression, data integrity, and performance (if applicable).
- Use structured format with Scenario ID, Scenario Description, Pre-conditions, Test Steps (high level), Expected Result.
- Pay special attention to backward compatibility, downstream/report impact, DB validations, and batch/job/process impact.
- Include SQL validation queries and sample test-data conditions if applicable.
- Keep concise but complete. Avoid generic statements.
- Assume Sonata is a financial platform.
- Output only test scenarios (no theory).
"""


def parse_sections(output: str):
    sections = {"release_notes": "", "overview": "", "testing_scope": ""}
    markers = {
        "===RELEASE_NOTES===": "release_notes",
        "===OVERVIEW===": "overview",
        "===TESTING_SCOPE===": "testing_scope",
    }

    current_key = None
    for line in output.splitlines():
        marker_key = markers.get(line.strip())
        if marker_key:
            current_key = marker_key
            continue
        if current_key:
            sections[current_key] += (line + "\n")

    return {k: v.strip() for k, v in sections.items()}


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
if st.button("🚀 Generate Release Notes, Overview and Testing Scope"):

    if not input_text.strip():
        st.warning("Please upload PDF(s) or paste details.")
        st.stop()

    if len(input_text.strip()) < 20:
        st.error("Input too small or invalid PDF content.")
        st.stop()

    prompt = build_prompt(release_note_type, input_text)
    try:
        with st.spinner("Generating Release Notes, Overview and Testing Scope..."):
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
            parsed_output = parse_sections(output)

        st.subheader(f"✅ Generated {selected_metadata['label']}")
        st.text_area("Release Notes", parsed_output["release_notes"] or output, height=300)
        st.text_area("Overview", parsed_output["overview"], height=200)
        st.text_area("Testing Scope", parsed_output["testing_scope"], height=350)

        file_name = f"{release_note_type.lower()}_release_note.txt"
        st.download_button(
            label="⬇️ Download Full Output",
            data=output,
            file_name=file_name,
        )

    except Exception as e:
        st.error("❌ Error generating release note. Please try smaller input or paste text manually.")
        st.exception(e)
