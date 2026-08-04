import streamlit as st
from groq import Groq
import PyPDF2

# Page config
st.set_page_config(page_title="Sonata Change Communication Studio", layout="wide")

st.title("📘 Sonata Change Communication Studio")
st.write(
    "Upload a JIRA/Design/BSD/IA PDF or paste details to generate Release Notes with supporting Overview and Testing Scope."
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
- Generate the ERN only from the supplied source documentation. Do not invent functionality, menu paths, regions, configuration, products, or dependencies.
- Use concise, professional Bravura Sonata Product Release Notes style. Avoid generic AI wording such as "This enhancement aims to...", "The expected business outcome...", repetitive filler, or unsupported benefit statements.
- Use business-friendly language and avoid Java, SQL, APIs, database tables, code names, and internal implementation details unless they are required for business understanding.
- Preserve business-visible Sonata terminology exactly as written in the source. Do not replace business names with generic English. Examples include Transaction Creation process, Contribution Transaction, No Effect deduction transaction, Include in MATS on Closure, MATS Submit, MATS Cancel, Expense Calculation Basis, Regular Fees/Rebates Parameters, From Employer Reserve, Insurance Premium Externally Funded Adhoc Increase, Insurance Premium Externally Funded Adhoc Decrease, and Lumpsum Payment/Transfer wizard.
- Expand abbreviation at first use, e.g. "Enhancement Release Note (ERN)".
- Title must be a single-line title matching these styles (do not add bullets or numbering):
  - "Sonata’s Account Investor Type determination enhanced to consider only active owner relationships, ensuring correct transition from Joint to Individual for accounts with deceased owners and thus improving ownership accuracy"
  - "Australian Superannuation - Enhancements to Reconcile Unpaid Refunds and Identify Source of Refund Reports to Improve CTR Refund Reconciliation and Reporting Accuracy"
  - "Australian Superannuation - Sonata enhancement introduces Reconcile Unpaid Refunds and Identify Source of Refund reports, improving visibility of CTR refund, enabling reconciliation, monitoring timelines, analysing system vs manual refund trends"
  - "Australian Superannuation - Load Contribution Schedule (SuperStream) process enhancement enables automated handling of CTR exceptions using configurable Schedule Auto Rejection Rules to support Pay Day Super compliance"
- Overview must include the organisation's mandatory paragraphs in this order:
  1) Begin with a concise description of the enhancement and the relevant business context.
  2) Include a dedicated rationale paragraph beginning exactly with: "The rationale behind this enhancement is...". After this mandatory phrase, provide specific business reasons from the source; avoid repeating the title or using vague benefit statements.
  3) Include a dedicated previous-behaviour paragraph beginning exactly with: "Prior to this enhancement...". After this mandatory phrase, describe only useful source-based previous behaviour, gaps, manual effort, reporting limitation, or operational constraint.
  4) Describe the new behaviour, including each business-visible process, transaction, report, field, configuration, validation, checkbox, or extraction logic without merging separate enhancements.
  5) Describe operational or business benefit using source-supported outcomes.
- Overview must mention a region only when the source explicitly states one. If no region is stated, do not add a global or region-specific sentence.
- Overview should be narrative, publication-ready, non-repetitive, and detailed enough to preserve all business-visible solution details without collapsing multiple enhancements into one sentence.
- Overview should be written as 3-6 concise paragraphs. Avoid one-line paragraphs unless the source is very limited.
- Include a glossary note only when glossary terms are clearly identified in the source. Use: "Note - For more information on the following terms - <terms>, please refer to Sonata Glossary."
- Key Features must contain the exact subheading "Demonstrable Additions" followed by bullet points (no numbering).
- Generate one bullet for every business enhancement. Do not combine multiple enhancements into one bullet.
- Every new process, wizard, report, transaction, configuration, parameter, checkbox, attribute, menu, screen, validation, batch, extraction rule, field, or mapping must appear as its own Key Features bullet when present in the source.
- Key Features bullets should describe the business-visible capability or change, the relevant trigger/context, and the business outcome where the source supports it. Avoid generic benefit-only bullets.
- Preserve Graphical Menu and Classic Menu paths exactly when they are present in the source. Never invent menu paths. If no menu path is available, state "Not provided in source documentation.".
- Implementation Considerations must preserve all configuration details stated in the source, including configuration paths, parameter names, check boxes, mappings, expense setup, product setup, static data, and reporting configuration.
- Output "No configuration required." only when the source contains absolutely no configuration, setup, mapping, or operational adoption requirements.
- Impact/Dependencies must list impacted Sonata components and business processes rather than generic statements. Examples include Pricing, Insurance, Account Closure, Contribution Transaction Creation, Contribution History, MATS Reporting, ATO Reporting, Adhoc Fee Processing, and Lumpsum Payment/Transfer.
- Detail preservation is mandatory: every new transaction, process, report, field, configuration, parameter, validation, extraction logic, checkbox, menu, screen, batch, and mapping from the source must appear in the ERN.
- Do not include client names, Jira IDs, or internal-only instructions.
- Keep the note concise, publication-ready, and in plain business English.

QUALITY CHECKS BEFORE FINALISING:
1) Confirm every business enhancement in the source is captured in the ERN.
2) Confirm configuration, setup, mappings, check boxes, parameters, paths, and reporting details are preserved.
3) Confirm business terminology is preserved exactly as written in the source.
4) Confirm Graphical Menu and Classic Menu paths are preserved exactly when present, and no menu path is invented.
5) Confirm no functionality, region, product, dependency, validation, configuration, or benefit has been invented.
6) Confirm there are no duplicated or combined Key Features bullets for separate enhancements.
7) Confirm mandatory Overview paragraphs beginning "The rationale behind this enhancement is..." and "Prior to this enhancement..." are present, rich, non-repetitive, and source-specific.
8) Confirm generic AI wording has been removed while preserving the mandatory Overview phrases.
9) Confirm the output resembles official Bravura Sonata Product Release Notes.
10) Ensure there is no contradiction between Overview and Key Features.
11) Do not repeat the same sentence across sections.

INPUT SOURCE (Design/BSD/IA/Jira):
{source_text[:12000]}

OUTPUT:
For ===RELEASE_NOTES=== provide ONLY the final ERN content using the exact ERN headings (Title, Overview, Key Features, Menu Path, Implementation Considerations, Impact/Dependencies).
Do not place any of these six ERN sections in ===OVERVIEW=== or ===TESTING_SCOPE===.

For ===OVERVIEW=== provide a detailed yet readable summary that includes:
- issue/requirement context,
- rationale for change,
- as-is behaviour,
- to-be behaviour,
- impacted users/processes and scope,
- business outcome and expected operational benefit.
Write in 4-6 well-developed paragraphs so any reader can understand quickly.

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
Act as a Senior Business Analyst preparing a Defect Release Note (DRN) for Sonata.

----------------------------------
STRICT TEMPLATE (DO NOT CHANGE HEADINGS):

Background

Change Implemented

Dependencies/Impact

----------------------------------

WRITING STYLE REQUIREMENTS (VERY IMPORTANT):

The response must strictly follow this writing style:

BACKGROUND:
- Start with: "When a user..."
- Clearly describe:
  - What process was executed
  - What failed and why
  - What limitation caused the issue
- Include expected behaviour using:
  "Ideally, the system should have..."

CHANGE IMPLEMENTED:
- Start with:
  "This issue occurred because..."
- Clearly explain:
  - Root cause in business terms
  - What has been changed
- Include resolution using:
  "To resolve this issue..."
- End with:
  "After these changes..."

DEPENDENCIES/IMPACT:
- Keep concise
- Format strictly like:
  "This change only impacts..."

----------------------------------

QUALITY RULES:

- Use business-friendly language
- Avoid unnecessary technical jargon
- Ensure cause, fix, and outcome are clearly linked
- Maintain clear paragraph structure (not bullet points)

----------------------------------

INPUT DEFECT DETAILS:
{source_text[:5000]}

----------------------------------

OUTPUT:
You must generate THREE sections in this exact order and exact markers:
===RELEASE_NOTES===
<content>
===OVERVIEW===
<content>
===TESTING_SCOPE===
<content>

For ===RELEASE_NOTES=== provide ONLY the final DRN in the strict template above (Background, Change Implemented, Dependencies/Impact) with no extra headings.

For ===OVERVIEW=== provide a concise business summary (2-3 paragraphs) covering issue context, prior behavior, updated behavior, and expected outcome.

For ===TESTING_SCOPE=== provide focused validation scenarios for this defect including: positive, negative, boundary value (99B vs 100B+), regression impact, and data validation checks.
"""


def _normalise_marker(line: str) -> str:
    return line.strip().replace("*", "").replace("`", "")




def parse_sections(output: str, note_type: str):
    sections = {"release_notes": "", "overview": "", "testing_scope": ""}
    markers = {
        "===RELEASE_NOTES===": "release_notes",
        "===OVERVIEW===": "overview",
        "===TESTING_SCOPE===": "testing_scope",
    }

    current_key = None
    for line in output.splitlines():
        normalised = _normalise_marker(line)
        marker_key = markers.get(normalised)
        if marker_key:
            current_key = marker_key
            continue
        if current_key:
            sections[current_key] += (line + "\n")

    parsed = {k: v.strip() for k, v in sections.items()}

    return parsed


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
            st.subheader(f"✅ Generated {selected_metadata['label']}")
        if release_note_type in {"ERN", "DRN"}:
            parsed_output = parse_sections(output, release_note_type)
            ern_release_notes = parsed_output["release_notes"]
            if release_note_type == "ERN":
                ern_headings = [
                    "Title",
                    "Overview",
                    "Key Features",
                    "Menu Path",
                    "Implementation Considerations",
                    "Impact/Dependencies",
                ]
                has_required_ern_structure = all(
                    heading in ern_release_notes for heading in ern_headings
                )
                if not has_required_ern_structure and all(
                    heading in parsed_output["overview"] for heading in ern_headings
                ):
                    ern_release_notes = parsed_output["overview"]

            st.text_area("Release Notes", ern_release_notes or output, height=300)
            st.text_area("Overview", parsed_output["overview"], height=220)
            st.text_area("Testing Scope", parsed_output["testing_scope"], height=350)
        else:
            st.text_area("Output", output, height=400)

        file_name = f"{release_note_type.lower()}_release_note.txt"
        st.download_button(
            label="⬇️ Download Full Output",
            data=output,
            file_name=file_name,
        )

    except Exception as e:
        st.error("❌ Error generating release note. Please try smaller input or paste text manually.")
        st.exception(e)
