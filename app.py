
import streamlit as st
from pypdf import PdfReader
import ollama
import re


# ============================================================
# PAGE SETTINGS
# ============================================================

st.set_page_config(
    page_title="AI PDF Summarizer",
    page_icon="📄",
    layout="wide"
)


# ============================================================
# LOGIN DETAILS
# ============================================================

USERNAME = "admin"
PASSWORD = "1234"


# ============================================================
# OLLAMA MODEL
# ============================================================

MODEL = "qwen2.5:3b"


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

if "result" not in st.session_state:
    st.session_state.result = ""


# ============================================================
# OLLAMA FUNCTION
# ============================================================

def ask_ollama(prompt):

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


# ============================================================
# DOCUMENT TYPE DETECTION
# ============================================================

def detect_document_type(text):

    # --------------------------------------------------------
    # Use the beginning and end of the ORIGINAL document.
    # These areas usually contain strong structural clues.
    # --------------------------------------------------------

    words = text.split()

    first_part = " ".join(words[:2500])

    last_part = " ".join(words[-1200:])

    detection_text = f"""
BEGINNING OF DOCUMENT:

{first_part}

END OF DOCUMENT:

{last_part}
"""

    prompt = f"""
You are a professional document classification system.

Your task is to identify the type of the document.

Use ONLY the document content provided below.

Do NOT use outside knowledge.

Do NOT guess based on a single word.

Look at the overall purpose, structure, headings, writing style,
and the type of information contained in the document.

============================================================
AVAILABLE CATEGORIES
============================================================

Choose EXACTLY ONE:

1. Lecture Notes
2. Resume / CV
3. Guidelines / Instructions
4. Research Paper
5. Report
6. Study Material
7. Article
8. Business Document
9. Other

============================================================
CLASSIFICATION RULES
============================================================

LECTURE NOTES:
Use this when the document appears to be notes taken from
a lecture, classroom teaching, seminar, or lesson.

Typical clues:
- lecture topics
- classroom concepts
- teacher explanations
- topic headings
- notes written for a particular lecture
- definitions and explanations of concepts

Do NOT choose this merely because the document contains
educational information.

------------------------------------------------------------

RESUME / CV:
Use this when the document is about a person's professional
or academic background.

Typical clues:
- person's name and contact information
- career objective/profile
- education
- work experience
- skills
- projects
- certifications
- achievements

------------------------------------------------------------

GUIDELINES / INSTRUCTIONS:
Use this when the main purpose is to tell someone HOW to do
something or what rules/steps/requirements to follow.

Typical clues:
- steps
- procedures
- rules
- requirements
- do/don't instructions
- operating instructions
- policies or guidance

------------------------------------------------------------

RESEARCH PAPER:
Use this when the document presents formal academic research.

Strong clues include:
- abstract
- introduction
- research question/problem
- methodology/methods
- experiments or data collection
- results
- discussion
- conclusion
- references/citations

A document should NOT be classified as a research paper
simply because it discusses an academic topic.

------------------------------------------------------------

REPORT:
Use this when the main purpose is to formally present
findings, observations, progress, events, activities,
results, status, or an investigation.

Typical clues:
- executive summary
- findings
- observations
- analysis
- recommendations
- project status
- incident/event information
- formal reporting structure

------------------------------------------------------------

STUDY MATERIAL:
Use this when the document is specifically prepared to help
students learn, revise, or prepare for an examination.

Typical clues:
- study notes
- revision material
- exam preparation
- questions and answers
- important questions
- learning material
- educational explanations arranged for study

IMPORTANT:
General educational content is NOT automatically study material.
Use the document's purpose and structure.

------------------------------------------------------------

ARTICLE:
Use this when the document is primarily a standalone article
explaining, discussing, or informing readers about a topic.

Typical clues:
- article-style headings
- continuous explanatory prose
- introduction/body/conclusion
- informational or opinion-based discussion
- written primarily for general readers

------------------------------------------------------------

BUSINESS DOCUMENT:
Use this when the main purpose is related to business,
organizations, companies, or professional operations.

Examples:
- business proposal
- business plan
- company memo
- meeting document
- corporate document
- marketing/business strategy
- commercial document

------------------------------------------------------------

OTHER:
Use this when none of the categories accurately describe
the document.

============================================================
IMPORTANT DECISION RULES
============================================================

1. Identify the PURPOSE of the document first.

2. Look at the STRUCTURE of the document.

3. Consider multiple clues rather than one keyword.

4. Do not classify a document as Research Paper just because
   it has academic terminology.

5. Do not classify a document as Lecture Notes just because
   it contains educational concepts.

6. Do not classify a document as Study Material just because
   it is related to education.

7. Do not classify a document as Report just because it has
   headings and paragraphs.

8. Choose Other when there is not enough evidence.

9. Return ONLY ONE category name.

10. Do NOT explain your answer.

============================================================
DOCUMENT
============================================================

{detection_text}

============================================================
ANSWER
============================================================

Return exactly one of these:

Lecture Notes
Resume / CV
Guidelines / Instructions
Research Paper
Report
Study Material
Article
Business Document
Other
"""

    result = ask_ollama(prompt)

    # --------------------------------------------------------
    # Clean the AI response
    # --------------------------------------------------------

    result = result.strip()

    valid_types = [
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

    # Exact match first
    for document_type in valid_types:

        if result.lower() == document_type.lower():
            return document_type

    # Search inside response if Qwen added extra text
    for document_type in valid_types:

        if document_type.lower() in result.lower():
            return document_type

    return "Other"


# ============================================================
# SPLIT COMPLETE DOCUMENT INTO CHUNKS
# ============================================================

def split_text(text, chunk_size=7000):

    words = text.split()

    chunks = []

    current_chunk = []
    current_length = 0

    for word in words:

        current_chunk.append(word)
        current_length += len(word) + 1

        if current_length >= chunk_size:

            chunks.append(
                " ".join(current_chunk)
            )

            current_chunk = []
            current_length = 0

    if current_chunk:

        chunks.append(
            " ".join(current_chunk)
        )

    return chunks


# ============================================================
# READ IMPORTANT INFORMATION FROM EACH CHUNK
# ============================================================

def analyze_chunk(chunk, chunk_number, total_chunks):

    prompt = f"""
You are analyzing section {chunk_number} of {total_chunks}
of a larger PDF document.

Read this section carefully.

Extract the IMPORTANT INFORMATION from this section.

Include:
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

Do NOT invent information.

Do NOT add outside knowledge.

Do NOT write a general summary only.

Create a compact information record that preserves
specific details from this section.

SECTION:

{chunk}

IMPORTANT INFORMATION:
"""

    return ask_ollama(prompt)


# ============================================================
# FINAL SUMMARY + KEY POINTS
# ============================================================

def final_analysis(information_sections):

    combined = "\n\n".join(
        [
            f"SECTION {i + 1} INFORMATION:\n{info}"
            for i, info in enumerate(information_sections)
        ]
    )

    prompt = f"""
You are the final analyzer of a complete PDF document.

The information below was extracted from ALL sections
of the original document.

Use ONLY this information.

Do not invent facts.
Do not use outside knowledge.

Your task is to create TWO different outputs.

==================================================
SUMMARY
==================================================

Write a concise overall summary of the COMPLETE document.

The summary should answer:

- What is this document about?
- What is its main purpose?
- What are its major topics or ideas?
- What are the important overall conclusions?

Write the summary as normal paragraphs.

The summary should describe the document as a whole.

DO NOT make the summary a numbered list.

==================================================
KEY POINTS
==================================================

Create 8 to 12 DISTINCT key points.

These must be SPECIFIC pieces of information from
the document.

A key point can contain:

- a definition
- a specific fact
- a date
- a number
- an important concept
- a particular instruction
- an example
- a finding
- a specific relationship
- an important conclusion

IMPORTANT:

The key points must NOT simply repeat the summary.

The summary gives the BIG PICTURE.

The key points give SPECIFIC DETAILS.

Every key point should add useful information.

Avoid duplicate points.

Return the key points as a numbered list.

==================================================
OUTPUT FORMAT
==================================================

SUMMARY:
[overall paragraph summary]

KEY POINTS:
1. [specific important detail]
2. [specific important detail]
3. [specific important detail]
4. [specific important detail]
5. [specific important detail]
6. [specific important detail]
7. [specific important detail]
8. [specific important detail]

==================================================
SOURCE INFORMATION
==================================================

{combined}
"""

    return ask_ollama(prompt)


# ============================================================
# LOGIN PAGE
# ============================================================

if not st.session_state.logged_in:

    st.title("🤖 AI PDF Summarizer")

    st.subheader("🔐 Login")

    st.write(
        "Enter your username and password to continue."
    )

    username = st.text_input(
        "Username"
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button(
        "🔑 Login",
        use_container_width=True
    ):

        if (
            username == USERNAME
            and password == PASSWORD
        ):

            st.session_state.logged_in = True

            st.success(
                "✅ Login successful!"
            )

            st.rerun()

        else:

            st.error(
                "❌ Incorrect username or password."
            )


# ============================================================
# MAIN APPLICATION
# ============================================================

else:

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    col1, col2 = st.columns([5, 1])

    with col1:

        st.title("🤖 AI PDF Summarizer")

        st.write(
            "Upload a PDF and analyze the complete document "
            "using local AI."
        )

    with col2:

        if st.button(
            "🚪 Logout",
            use_container_width=True
        ):

            st.session_state.logged_in = False

            st.rerun()

    st.divider()


    # --------------------------------------------------------
    # PDF UPLOAD
    # --------------------------------------------------------

    st.subheader("📄 Upload PDF")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Upload a text-based PDF."
    )

    if uploaded_file is not None:

        st.info(
            f"Selected file: **{uploaded_file.name}**"
        )

        if st.button(
            "📤 Upload PDF",
            use_container_width=True
        ):

            try:

                reader = PdfReader(
                    uploaded_file
                )

                full_text = ""

                # Read EVERY PAGE
                for page_number, page in enumerate(
                    reader.pages,
                    start=1
                ):

                    page_text = page.extract_text()

                    if page_text:

                        full_text += (
                            f"\n\n--- PAGE {page_number} ---\n\n"
                        )

                        full_text += page_text

                # --------------------------------------------
                # CHECK TEXT
                # --------------------------------------------

                if not full_text.strip():

                    st.error(
                        "❌ No readable text was found "
                        "in this PDF."
                    )

                else:

                    st.session_state.pdf_text = (
                        full_text
                    )

                    st.session_state.pdf_name = (
                        uploaded_file.name
                    )

                    st.session_state.page_count = (
                        len(reader.pages)
                    )

                    st.session_state.result = ""

                    st.success(
                        "✅ PDF uploaded successfully!"
                    )

                    st.write(
                        f"📑 **Pages:** "
                        f"{len(reader.pages)}"
                    )

                    st.write(
                        f"📝 **Characters extracted:** "
                        f"{len(full_text):,}"
                    )

            except Exception as e:

                st.error(
                    f"❌ Error reading PDF: {e}"
                )


    # --------------------------------------------------------
    # DOCUMENT INFORMATION
    # --------------------------------------------------------

    if st.session_state.pdf_text:

        st.divider()

        st.subheader("📋 Document Information")

        st.write(
            f"**File:** "
            f"{st.session_state.pdf_name}"
        )

        st.write(
            f"**Pages:** "
            f"{st.session_state.page_count}"
        )

        st.write(
            f"**Characters extracted:** "
            f"{len(st.session_state.pdf_text):,}"
        )


        # ----------------------------------------------------
        # ANALYZE COMPLETE PDF
        # ----------------------------------------------------

        st.subheader("✨ AI Analysis")

        if st.button(
            "⚡ Analyze Complete PDF",
            use_container_width=True
        ):

            text = st.session_state.pdf_text

            try:

                # ==========================================
                # STEP 1: DOCUMENT TYPE
                # ==========================================

                with st.spinner(
                    "🔎 Identifying document type..."
                ):

                    document_type = detect_document_type(
                        text
                    )


                # ==========================================
                # STEP 2: SPLIT COMPLETE DOCUMENT
                # ==========================================

                chunks = split_text(
                    text,
                    chunk_size=7000
                )

                st.write(
                    f"📚 The complete document has been "
                    f"divided into **{len(chunks)} sections**."
                )

                information_sections = []

                progress_bar = st.progress(0)


                # ==========================================
                # STEP 3: PROCESS EVERY SECTION
                # ==========================================

                for i, chunk in enumerate(chunks):

                    with st.spinner(
                        f"🤖 Reading section "
                        f"{i + 1} of {len(chunks)}..."
                    ):

                        information = analyze_chunk(
                            chunk,
                            i + 1,
                            len(chunks)
                        )

                        information_sections.append(
                            information
                        )

                    progress_bar.progress(
                        (i + 1) / len(chunks)
                    )


                # ==========================================
                # STEP 4: FINAL SUMMARY + KEY POINTS
                # ==========================================

                with st.spinner(
                    "🧠 Creating summary and key points..."
                ):

                    result = final_analysis(
                        information_sections
                    )


                # ==========================================
                # STORE EVERYTHING
                # ==========================================

                st.session_state.result = result

                st.session_state.document_type = (
                    document_type
                )

                st.success(
                    "✅ Complete PDF analysis finished!"
                )

            except Exception as e:

                st.error(
                    f"❌ AI error: {e}"
                )


    # ========================================================
    # RESULTS
    # ========================================================

    if st.session_state.result:

        st.divider()

        st.subheader(
            "📊 AI Analysis Results"
        )


        # ----------------------------------------------------
        # DOCUMENT TYPE
        # ----------------------------------------------------

        document_type = st.session_state.get(
            "document_type",
            "Other"
        )

        st.subheader(
            "📂 Document Type"
        )

        st.success(
            document_type
        )


        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        result = st.session_state.result

        summary_match = re.search(
            r"SUMMARY:\s*(.*?)(?=\n\s*KEY POINTS:)",
            result,
            re.DOTALL | re.IGNORECASE
        )

        if summary_match:

            summary = (
                summary_match.group(1).strip()
            )

            st.subheader(
                "📝 Summary"
            )

            st.write(
                summary
            )

            st.download_button(
                "⬇️ Download Summary",
                data=summary,
                file_name="AI_Summary.txt",
                mime="text/plain",
                use_container_width=True
            )


        # ----------------------------------------------------
        # KEY POINTS
        # ----------------------------------------------------

        key_match = re.search(
            r"KEY POINTS:\s*(.*)",
            result,
            re.DOTALL | re.IGNORECASE
        )

        if key_match:

            key_points = (
                key_match.group(1).strip()
            )

            st.subheader(
                "🔑 Key Points"
            )

            st.write(
                key_points
            )

            st.download_button(
                "⬇️ Download Key Points",
                data=key_points,
                file_name="AI_Key_Points.txt",
                mime="text/plain",
                use_container_width=True
            )


        # ----------------------------------------------------
        # FALLBACK
        # ----------------------------------------------------

        if (
            not summary_match
            or not key_match
        ):

            st.warning(
                "The AI returned a slightly different "
                "format, so the complete response is shown below."
            )

            st.write(result)

            st.download_button(
                "⬇️ Download Complete Analysis",
                data=result,
                file_name="AI_Document_Analysis.txt",
                mime="text/plain",
                use_container_width=True
            )
