import streamlit as st
from pypdf import PdfReader
import ollama
import re


# ============================================================
# CONFIGURATION
# ============================================================

MODEL = "qwen2.5:3b"

DEMO_USERNAME = "admin"
DEMO_PASSWORD = "1234"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI PDF Summarizer",
    page_icon="📄",
    layout="wide"
)


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = ""

if "page_count" not in st.session_state:
    st.session_state.page_count = 0

if "document_type" not in st.session_state:
    st.session_state.document_type = ""

if "summary" not in st.session_state:
    st.session_state.summary = ""

if "key_points" not in st.session_state:
    st.session_state.key_points = ""


# ============================================================
# LOGOUT FUNCTION
# ============================================================

def logout():
    """
    Completely clear the current document and AI results.
    """

    st.session_state.logged_in = False

    # Clear uploaded PDF information
    st.session_state.pdf_text = ""
    st.session_state.pdf_name = ""
    st.session_state.page_count = 0

    # Clear AI results
    st.session_state.document_type = ""
    st.session_state.summary = ""
    st.session_state.key_points = ""

    # Restart the page
    st.rerun()


# ============================================================
# OLLAMA FUNCTION
# ============================================================

def ask_ollama(prompt):
    try:
        response = ollama.chat(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0.1
            }
        )

        return response["message"]["content"].strip()

    except Exception as e:
        return f"ERROR: {str(e)}"


# ============================================================
# DOCUMENT TYPE DETECTION
# ============================================================

def detect_document_type(text):

    words = text.split()

    first_part = " ".join(words[:2500])
    last_part = " ".join(words[-1200:])

    sample = first_part + "\n\n" + last_part

    prompt = f"""
You are a document classification system.

Classify the following PDF into exactly ONE of these categories:

1. Lecture Notes
2. Resume / CV
3. Guidelines / Instructions
4. Research Paper
5. Report
6. Study Material
7. Article
8. Business Document
9. Other

Use the actual structure and content of the document.

Classification rules:

Lecture Notes:
- classroom notes
- lecture headings
- concepts explained for students
- professor/teacher notes
- course topics

Resume / CV:
- education
- skills
- work experience
- projects
- career profile
- contact information

Guidelines / Instructions:
- rules
- procedures
- steps
- instructions
- policies
- recommendations for performing an activity

Research Paper:
- abstract
- methodology
- literature review
- research question
- experiments
- results
- discussion
- references

Report:
- formal report structure
- findings
- analysis
- recommendations
- executive summary
- organizational or technical reporting

Study Material:
- educational material
- textbook-like explanations
- exam preparation
- definitions
- learning content
- questions and answers

Article:
- journalistic or general informational article
- topic-based discussion
- explanatory article

Business Document:
- business plans
- proposals
- meeting documents
- company documents
- business correspondence

Other:
- if none of the above fits clearly

Return ONLY the category name.

DOCUMENT:
{sample}
"""

    result = ask_ollama(prompt)

    allowed_types = [
        "Lecture Notes",
        "Resume / CV",
        "Guidelines / Instructions",
        "Research Paper",
        "Report",
        "Study Material",
        "Article",
        "Business Document",
        "Other"
    ]

    for document_type in allowed_types:
        if document_type.lower() in result.lower():
            return document_type

    return "Other"


# ============================================================
# TEXT SPLITTING
# ============================================================

def split_text(text, chunk_size=7000):

    words = text.split()

    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks


# ============================================================
# ANALYZE DOCUMENT SECTION
# ============================================================

def analyze_chunk(chunk, section_number, total_sections):

    prompt = f"""
You are analyzing section {section_number} of {total_sections}
of a PDF document.

Extract the most important information from this section.

Include only information that actually appears in the document.

Focus on:

- important concepts
- definitions
- facts
- names
- dates
- numbers
- examples
- instructions
- findings
- conclusions
- important relationships between ideas

Do NOT write a general summary.

Do NOT repeat the same point using different wording.

Use concise bullet points.

SECTION:

{chunk}
"""

    return ask_ollama(prompt)


# ============================================================
# FINAL SUMMARY + KEY POINTS
# ============================================================

def final_analysis(information_sections, document_type):

    combined_information = "\n\n".join(information_sections)

    prompt = f"""
You are creating the final analysis of a PDF document.

Document type:
{document_type}

Below are important facts and concepts extracted from all sections
of the document.

Create TWO separate outputs:

SUMMARY:
Write a clear, complete summary of the entire document.
Use connected paragraphs.
Cover the major ideas and conclusions.
Do not unnecessarily repeat individual facts.

KEY POINTS:
Create 8 to 12 important points.
Each point must contain a distinct piece of information.
Do not simply copy sentences from the summary.
Do not repeat the same idea.

Important:
- Use ONLY information supported by the extracted content.
- Do not invent information.
- Do not add outside knowledge.

Return exactly in this format:

SUMMARY:
[summary]

KEY POINTS:
1. [point]
2. [point]
3. [point]
...

EXTRACTED INFORMATION:

{combined_information}
"""

    result = ask_ollama(prompt)

    summary = ""
    key_points = ""

    if "KEY POINTS:" in result:

        parts = result.split("KEY POINTS:", 1)

        summary_part = parts[0]

        if "SUMMARY:" in summary_part:
            summary = summary_part.split("SUMMARY:", 1)[1].strip()
        else:
            summary = summary_part.strip()

        key_points = parts[1].strip()

    else:
        summary = result
        key_points = "Key points could not be separated automatically."

    return summary, key_points


# ============================================================
# LOGIN PAGE
# ============================================================

def login_page():

    st.title("🤖 AI PDF Summarizer")

    st.subheader("Login")

    st.write("Enter your credentials to continue.")

    username = st.text_input(
        "Username"
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button(
        "Login",
        type="primary",
        use_container_width=True
    ):

        if (
            username == DEMO_USERNAME
            and password == DEMO_PASSWORD
        ):

            st.session_state.logged_in = True

            # Make sure every previous document is cleared
            st.session_state.pdf_text = ""
            st.session_state.pdf_name = ""
            st.session_state.page_count = 0
            st.session_state.document_type = ""
            st.session_state.summary = ""
            st.session_state.key_points = ""

            st.success("Login successful!")

            st.rerun()

        else:

            st.error("Invalid username or password.")


# ============================================================
# MAIN APPLICATION
# ============================================================

def main_app():

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    col1, col2 = st.columns([5, 1])

    with col1:
        st.title("📄 AI PDF Summarizer")
        st.caption(
            "Summarize PDF documents using local AI with Ollama and Qwen 2.5."
        )

    with col2:

        if st.button(
            "Logout",
            use_container_width=True
        ):
            logout()

    st.divider()

    # --------------------------------------------------------
    # INFORMATION
    # --------------------------------------------------------

    st.info(
        "Upload a PDF to extract its content, detect the document type, "
        "generate a complete summary, and identify key points."
    )

    # --------------------------------------------------------
    # PDF UPLOAD
    # --------------------------------------------------------

    uploaded_file = st.file_uploader(
        "Upload your PDF",
        type=["pdf"]
    )

    # --------------------------------------------------------
    # PROCESS PDF
    # --------------------------------------------------------

    if uploaded_file is not None:

        # Only process when a new PDF is selected
        if uploaded_file.name != st.session_state.pdf_name:

            # Clear previous results before processing a new PDF
            st.session_state.pdf_text = ""
            st.session_state.pdf_name = ""
            st.session_state.page_count = 0
            st.session_state.document_type = ""
            st.session_state.summary = ""
            st.session_state.key_points = ""

            progress = st.progress(0)

            status = st.empty()

            # ----------------------------------------------
            # Extract PDF text
            # ----------------------------------------------

            status.write("📖 Reading PDF...")

            try:

                reader = PdfReader(uploaded_file)

                page_count = len(reader.pages)

                extracted_pages = []

                for i, page in enumerate(reader.pages):

                    page_text = page.extract_text()

                    if page_text:
                        extracted_pages.append(page_text)

                    progress_value = int(
                        ((i + 1) / page_count) * 30
                    )

                    progress.progress(progress_value)

                full_text = "\n\n".join(extracted_pages)

            except Exception as e:

                st.error(
                    f"Could not read the PDF: {e}"
                )

                return

            if not full_text.strip():

                st.error(
                    "No readable text was found in this PDF."
                )

                return

            # ----------------------------------------------
            # Save PDF information
            # ----------------------------------------------

            st.session_state.pdf_text = full_text
            st.session_state.pdf_name = uploaded_file.name
            st.session_state.page_count = page_count

            # ----------------------------------------------
            # Detect document type
            # ----------------------------------------------

            status.write("🔍 Detecting document type...")

            progress.progress(40)

            document_type = detect_document_type(
                full_text
            )

            st.session_state.document_type = document_type

            # ----------------------------------------------
            # Split document
            # ----------------------------------------------

            status.write("📚 Processing complete document...")

            chunks = split_text(
                full_text,
                chunk_size=7000
            )

            total_chunks = len(chunks)

            information_sections = []

            # ----------------------------------------------
            # Analyze chunks
            # ----------------------------------------------

            for index, chunk in enumerate(chunks):

                section_number = index + 1

                status.write(
                    f"🤖 Analyzing section {section_number} "
                    f"of {total_chunks}..."
                )

                section_result = analyze_chunk(
                    chunk,
                    section_number,
                    total_chunks
                )

                information_sections.append(
                    section_result
                )

                progress_value = 40 + int(
                    ((index + 1) / total_chunks) * 40
                )

                progress.progress(progress_value)

            # ----------------------------------------------
            # Final analysis
            # ----------------------------------------------

            status.write(
                "📝 Creating final summary and key points..."
            )

            progress.progress(90)

            summary, key_points = final_analysis(
                information_sections,
                document_type
            )

            st.session_state.summary = summary
            st.session_state.key_points = key_points

            progress.progress(100)

            status.success(
                "✅ PDF processing completed!"
            )

            st.rerun()

    # ========================================================
    # DISPLAY CURRENT DOCUMENT
    # ========================================================

    if st.session_state.pdf_name:

        st.divider()

        st.subheader("📄 Document Information")

        info_col1, info_col2, info_col3 = st.columns(3)

        with info_col1:
            st.write("**File**")
            st.write(st.session_state.pdf_name)

        with info_col2:
            st.write("**Pages**")
            st.write(st.session_state.page_count)

        with info_col3:
            st.write("**Document Type**")
            st.write(st.session_state.document_type)

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        st.divider()

        st.subheader("📝 Summary")

        if st.session_state.summary:

            st.write(
                st.session_state.summary
            )

            st.download_button(
                label="⬇️ Download Summary",
                data=st.session_state.summary,
                file_name="summary.txt",
                mime="text/plain",
                use_container_width=True
            )

        # ----------------------------------------------------
        # KEY POINTS
        # ----------------------------------------------------

        st.divider()

        st.subheader("🔑 Key Points")

        if st.session_state.key_points:

            st.write(
                st.session_state.key_points
            )

            st.download_button(
                label="⬇️ Download Key Points",
                data=st.session_state.key_points,
                file_name="key_points.txt",
                mime="text/plain",
                use_container_width=True
            )

    else:

        st.write("")
        st.info(
            "📄 Upload a PDF above to begin."
        )


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if st.session_state.logged_in:

    main_app()

else:

    login_page()